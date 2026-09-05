from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt # type: ignore
from pydantic import ValidationError

from extensions import db
from models import User
from utils.decorators import role_required
from schemas.user import UserCreate, UserLogin, UserUpdate


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    try:
        user_data = UserCreate(**data)
    except ValidationError as e:
        return jsonify({
            "error": "Validtion failed",
            "details": e.errors()
        }), 400

    # if not data or "username" not in data or "password" not in data:
    #     return jsonify({"error": "username and password are required"}), 400

    existing = db.session.execute(
        db.select(User).where(
            db.or_(
                User.username == user_data.username,
                User.email == user_data.email
            )
        )
    ).scalar_one_or_none()

    if existing:
        return jsonify({"error": "Username already taken"}), 409

    new_user = User(username=data["username"], email=data["email"], role="customer") # type: ignore
    new_user.set_password(data["password"])
    db.session.add(new_user)
    db.session.commit()

    return jsonify(new_user.to_dict()), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    try:
        user_data = UserLogin(**data)
    except ValidationError as e:
        return jsonify({
            "error": "Validation failed",
            "details": e.errors()
        }), 400

    # if not data or "username" not in data or "password" not in data:
    #     return jsonify({"error": "username and password are required"}), 400

    user = db.session.execute(
        db.select(User).where(
            db.or_(
                User.username == user_data.identifier,
                User.email == user_data.identifier,
            )
        )
    ).scalar_one_or_none()

    if user is None or not user.check_password(data["password"]):
        return jsonify({"error": "invalid username or password"}), 401

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role}
    )

    return jsonify({"access_token": token}), 200


@auth_bp.route("/users/<int:user_id>/role", methods=["PUT"])
@role_required("admin")
def update_user_role(user_id):
    data = request.get_json()
    if not data or "role" not in data:
        return jsonify({"error": "role is required"}), 400

    if data["role"] not in ("admin", "customer"):
        return jsonify({"error": "invalid role"}), 400

    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404

    user.role = data["role"]
    db.session.commit()
    return jsonify(user.to_dict())