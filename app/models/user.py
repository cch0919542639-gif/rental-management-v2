from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.core.db import db, login_manager
from app.models.base import BaseModel


class User(UserMixin, BaseModel):
    __tablename__ = "user"

    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="viewer")
    landlord_id = db.Column(db.Integer, db.ForeignKey("landlords.id"), nullable=True)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"


@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))
