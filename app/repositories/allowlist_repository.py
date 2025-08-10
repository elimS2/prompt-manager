from typing import Optional, List

from app.models import EmailAllowlist
from .base import BaseRepository


class AllowlistRepository(BaseRepository[EmailAllowlist]):
    def __init__(self) -> None:
        super().__init__(EmailAllowlist)

    def get_by_email(self, email: str) -> Optional[EmailAllowlist]:
        if not email:
            return None
        return self.model.query.filter_by(email=email.lower()).first()

    def list_all(self) -> List[EmailAllowlist]:
        return self.model.query.order_by(self.model.email.asc()).all()

    def add(self, email: str, default_role: str = 'user', note: Optional[str] = None) -> EmailAllowlist:
        email = (email or '').strip().lower()
        if not email:
            raise ValueError("Email is required")
        existing = self.get_by_email(email)
        if existing:
            return existing
        entry = self.model(email=email, default_role=default_role, note=note)
        self.session.add(entry)
        self.session.commit()
        return entry

    def remove_by_id(self, entry_id: int) -> bool:
        entry = self.get_by_id(entry_id)
        if not entry:
            return False
        self.session.delete(entry)
        self.session.commit()
        return True

    def remove_by_email(self, email: str) -> bool:
        entry = self.get_by_email(email)
        if not entry:
            return False
        self.session.delete(entry)
        self.session.commit()
        return True


