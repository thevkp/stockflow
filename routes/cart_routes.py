from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Cart, CartItem, Product

cart_bp = Blueprint("cart", __name__, url_prefix="/api/cart")


def get_or_create_cart(user_id):
    cart = db.session.execute(
        db.select(Cart).where(Cart.user_id == user_id)
    ).scalar_one_or_none()

    if cart is None:
        cart = Cart(user_id=user_id) # type: ignore
        db.session.add(cart)
        db.session.commit()

    return cart


@cart_bp.route("", methods=["GET"])
@jwt_required()
def view_cart():
    user_id = int(get_jwt_identity())
    cart = get_or_create_cart(user_id)
    return jsonify({
        "items": [item.to_dict() for item in cart.items], 
        "total": sum(item.product.price * item.quantity for item in cart.items),
    })


@cart_bp.route("/items", methods=["POST"])
@jwt_required()
def add_item():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or "product_id" not in data:
        return jsonify({"error": "product_id is required"}), 400

    quantity = data.get("quantity", 1)
    product = db.session.get(Product, data["product_id"])
    if product is None:
        return jsonify({"error": "Product not found"}), 404

    cart = get_or_create_cart(user_id)

    existing_item = db.session.execute(
        db.select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product.id
        )
    ).scalar_one_or_none()

    if existing_item:
        existing_item.quantity += quantity
    else:
        new_item = CartItem(cart_id=cart.id, product_id=product.id, quantity=quantity)
        db.session.add(new_item)

    db.session.commit()
    return jsonify({"message": "Item added to cart"}), 201


@cart_bp.route("/items/<int:item_id>", methods=["DELETE"])
@jwt_required()
def remove_item(item_id):
    user_id = int(get_jwt_identity())
    cart = get_or_create_cart(user_id)

    item = db.session.execute(
        db.select(CartItem).where(
            CartItem.id == item_id,
            CartItem.cart_id == cart.id
        )
    ).scalar_one_or_none()

    if item is None:
        return jsonify({"error": "Item not found in your cart"}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item removed"}), 200