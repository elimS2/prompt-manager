"""Allowlist model to store pre-approved emails for access control."""
from datetime import datetime
from .base import db, BaseModel


class EmailAllowlist(BaseModel):
    __tablename__ = 'email_allowlist'

    email = db.Column(db.String(255), unique=True, nullable=False)
    default_role = db.Column(db.String(50), nullable=False, default='user')
    note = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)

    def to_dict(self):
        base = super().to_dict()
        base.update({
            'email': self.email,
            'default_role': self.default_role,
            'note': self.note,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        })
        return base


