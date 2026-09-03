# routes/order_routes.py
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.order_service import place_order, InsufficientStockError

orders_bp = Blueprint("orders", __name__, url_prefix="/api/orders")

@orders_bp.route("/checkout", methods=["POST"])
@jwt_required()
def checkout():
    user_id = int(get_jwt_identity())
    try:
        order = place_order(user_id)
        return jsonify(order.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except InsufficientStockError as e:
        return jsonify({"error": str(e)}), 409