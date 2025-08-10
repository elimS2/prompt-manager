"""User model for authentication and authorization.

Follows existing BaseModel patterns and integrates with Flask-Login.
"""
from datetime import datetime
from flask_login import UserMixin
from .base import db, BaseModel


class User(BaseModel, UserMixin):
    __tablename__ = 'users'

    google_sub = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=True)
    picture_url = db.Column(db.String(512), nullable=True)
    role = db.Column(db.String(50), nullable=False, default='user')
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    last_login_at = db.Column(db.DateTime, nullable=True)

    def mark_logged_in(self) -> None:
        self.last_login_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        base = super().to_dict()
        base.update({
            'google_sub': self.google_sub,
            'email': self.email,
            'name': self.name,
            'picture_url': self.picture_url,
            'role': self.role,
            'is_active': self.is_active,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
        })
        return base

 