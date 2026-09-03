from typing import Dict, Any

from extensions import db
import bcrypt


class User(db.Model):
    __tablename__ = "users"

    id: int = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash: str = db.Column(db.String(200), nullable=False)
    role: str = db.Column(db.String(20), nullable=False, default="customer")

    def set_password(self, plain_password: str):
        self.password_hash = bcrypt.hashpw(
            plain_password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, plain_password: str):
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), self.password_hash.encode("utf-8")
        )

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "username": self.username, "role": self.role}