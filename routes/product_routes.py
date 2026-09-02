from flask import Blueprint, jsonify, request
from extensions import db
from models import Product

products_bp = Blueprint("products", __name__, url_prefix="/api/products")


@products_bp.route("", methods=["GET"])
def get_products():
    products = db.session.execute(db.select(Product)).scalars().all()
    return jsonify([p.to_dict() for p in products])


@products_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id: int):
    product = db.session.get(Product, product_id)
    if product is None:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product.to_dict())


@products_bp.route("", methods=["POST"])
def create_product():
    data = request.get_json()

    if not data or "name" not in data or "price" not in data or "barcode" not in data:
        return jsonify({"error": "name, price, and barcode are required"}), 400

    new_product = Product(
        name=data["name"], # type: ignore
        price=data["price"], # type: ignore
        barcode=data["barcode"], # type: ignore
        description=data.get("description"), # type: ignore
        stock_quantity=data.get("stock_quantity", 0), # type: ignore
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify(new_product.to_dict()), 201



@products_bp.route("/<int:product_id>", methods=["PUT"])
def update_product(product_id: int):
    product = db.session.get(Product, product_id)
    if product is None:
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if "name" in data:
        product.name = data["name"]
    if "price" in data:
        product.price = data["price"]
    if "barcode" in data:
        product.barcode = data["barcode"]
    if "description" in data:
        product.description = data["description"]
    if "stock_quantity" in data:
        product.stock_quantity = data["stock_quantity"]

    db.session.commit()
    return jsonify(product.to_dict())


@products_bp.route("/<int:product_id>", methods=["DELETE"])
def delete_product(product_id: int):
    product = db.session.get(Product, product_id)

    if product is None:
        return jsonify({"error": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": f"Product {product_id} deleted"}), 200

