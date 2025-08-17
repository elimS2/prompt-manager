"""Repositories for FavoriteSet and FavoriteSetItem following BaseRepository pattern."""
from typing import List, Optional
from .base import BaseRepository
from app.models import FavoriteSet, FavoriteSetItem, db


class FavoriteSetRepository(BaseRepository[FavoriteSet]):
    def __init__(self):
        super().__init__(FavoriteSet)

    def get_by_user(self, user_id: int) -> List[FavoriteSet]:
        return self.model.query.filter_by(user_id=user_id, is_active=True).order_by(self.model.created_at.desc()).all()

    def get_with_items(self, favorite_id: int, user_id: int) -> Optional[FavoriteSet]:
        return self.model.query.filter_by(id=favorite_id, user_id=user_id).first()

    def exists_by_name(self, user_id: int, name: str) -> bool:
        return self.model.query.filter(db.func.lower(self.model.name) == name.lower(), self.model.user_id == user_id).first() is not None


class FavoriteSetItemRepository(BaseRepository[FavoriteSetItem]):
    def __init__(self):
        super().__init__(FavoriteSetItem)

    def get_by_set(self, favorite_set_id: int) -> List[FavoriteSetItem]:
        return self.model.query.filter_by(favorite_set_id=favorite_set_id).order_by(self.model.position).all()


