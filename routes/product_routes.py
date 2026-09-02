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
        name=data["name"],
        price=data["price"],
        barcode=data["barcode"],
        description=data.get("description"),
        stock_quantity=data.get("stock_quantity", 0),
    )
    db.session.add(new_product)
    db.session.commit()
    return jsonify(new_product.to_dict()), 201