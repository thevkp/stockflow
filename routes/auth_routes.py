from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt # type: ignore

from extensions import db
from models import User


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "username and password are required"}), 400

    existing = db.session.execute(
        db.select(User).where(User.username == data["username"])
    ).scalar_one_or_none()

    if existing:
        return jsonify({"error": "Username already taken"}), 409

    new_user = User(username=data["username"], role=data.get("role", "customer")) # type: ignore
    new_user.set_password(data["password"])
    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user.to_dict()), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "username and password are required"}), 400

    user = db.session.execute(
        db.select(User).where(User.username == data["username"])
    ).scalar_one_or_none()

    if user is None or not user.check_password(data["password"]):
        return jsonify({"error": "invalid username or password"}), 401

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role}
    )

    return jsonify({"access_token": token}), 200