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


