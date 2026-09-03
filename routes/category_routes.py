from flask import Blueprint, jsonify, request

from extensions import db
from models import Category
from utils.decorators import role_required


category_bp = Blueprint("category", __name__, url_prefix="/api/categories")

@category_bp.route("", methods=["GET"])
def get_categories():
    categories = db.session.execute(db.select(Category)).scalars().all()

    return jsonify([c.to_dict() for c in categories])

@category_bp.route("/<int:category_id>", methods=["GET"])
def get_category(category_id: int):
    category = db.session.get(Category, category_id)

    if category is None:
        return jsonify({"error": "Category not found"}), 404
    return jsonify(category.to_dict())

@category_bp.route("", methods=["POST"])
@role_required("admint")
def create_category():
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "name is required"}), 400

    new_category = Category(name=data["name"]) # type: ignore

    db.session.add(new_category)
    db.session.commit()
    return jsonify(new_category.to_dict()), 201

@category_bp.route("/<int:category_id>", methods=["PUT"])
def update_category(category_id: int):
    category = db.session.get(Category, category_id)
    if category is None:
        return jsonify({"error": "Category not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if "name" in data:
        category.name = data["name"]

    db.session.commit()
    return jsonify(category.to_dict())


@category_bp.route("/<int:category_id>", methods=["DELETE"])
def delete_category(category_id: int):
    category = db.session.get(Category, category_id)
    if category is None:
        return jsonify({"error": "Category not found"}), 404

    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": f"Category {category_id} deleted"}), 200