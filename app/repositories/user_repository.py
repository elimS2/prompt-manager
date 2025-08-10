"""User repository implementing data access for User model."""
from typing import Optional

from app.models import User
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self) -> None:
        super().__init__(User)

    def get_by_email(self, email: str) -> Optional[User]:
        if not email:
            return None
        return self.model.query.filter_by(email=email).first()

    def get_by_google_sub(self, google_sub: str) -> Optional[User]:
        if not google_sub:
            return None
        return self.model.query.filter_by(google_sub=google_sub).first()

    def list_by_status(self, status: str):
        return self.model.query.filter_by(status=status).order_by(self.model.created_at.asc()).all()

    def mark_approved(self, user: User, approver_user_id: int | None = None, role: str | None = None):
        if role:
            user.role = role
        user.status = 'active'
        user.approved_by_user_id = approver_user_id
        user.approved_at = __import__('datetime').datetime.utcnow()
        self.session.commit()
        return user

    def mark_disabled(self, user: User):
        user.status = 'disabled'
        self.session.commit()
        return user


