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
    property_accesses = db.relationship("UserPropertyAccess", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"


class UserPropertyAccess(BaseModel):
    __tablename__ = "user_property_accesses"
    __table_args__ = (db.UniqueConstraint("user_id", "property_id", name="uq_user_property_access"),)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey("properties.id"), nullable=False)

    user = db.relationship("User", back_populates="property_accesses")
    property = db.relationship("Property")


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))
