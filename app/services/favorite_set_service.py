"""Service layer for managing user-scoped favorite prompt combinations."""
from typing import List, Optional, Dict, Any
from app.repositories.favorite_set_repository import FavoriteSetRepository, FavoriteSetItemRepository
from app.repositories.prompt_repository import PromptRepository
from app.models import FavoriteSet, FavoriteSetItem


class FavoriteSetService:
    def __init__(
        self,
        favorite_repo: Optional[FavoriteSetRepository] = None,
        item_repo: Optional[FavoriteSetItemRepository] = None,
        prompt_repo: Optional[PromptRepository] = None,
    ):
        self.favorite_repo = favorite_repo or FavoriteSetRepository()
        self.item_repo = item_repo or FavoriteSetItemRepository()
        self.prompt_repo = prompt_repo or PromptRepository()

    # Queries
    def list_for_user(self, user_id: int) -> List[FavoriteSet]:
        return self.favorite_repo.get_by_user(user_id)

    def get(self, user_id: int, favorite_id: int) -> Optional[FavoriteSet]:
        return self.favorite_repo.get_with_items(favorite_id, user_id)

    # Mutations
    def create(self, user_id: int, name: str, description: str = '', prompt_ids: Optional[List[int]] = None) -> FavoriteSet:
        self._validate_name(user_id, name)
        prompt_ids = self._normalize_prompt_ids(prompt_ids)

        favorite = self.favorite_repo.create(user_id=user_id, name=name.strip(), description=(description or '').strip(), is_active=True)

        # Insert items with order
        for idx, pid in enumerate(prompt_ids):
            self.item_repo.create(favorite_set_id=favorite.id, prompt_id=pid, position=idx)

        return self.favorite_repo.get_by_id(favorite.id)

    def update(self, user_id: int, favorite_id: int, data: Dict[str, Any]) -> FavoriteSet:
        favorite = self._require_owned(user_id, favorite_id)

        updates: Dict[str, Any] = {}
        if 'name' in data and data['name'] is not None:
            new_name = data['name'].strip()
            if new_name != favorite.name:
                self._validate_name(user_id, new_name)
                updates['name'] = new_name
        if 'description' in data and data['description'] is not None:
            updates['description'] = data['description'].strip()
        if 'is_active' in data and data['is_active'] is not None:
            is_active = data['is_active']
            if isinstance(is_active, str):
                is_active = is_active.lower() in ('true', '1', 'on', 'yes')
            updates['is_active'] = bool(is_active)

        if updates:
            self.favorite_repo.update(favorite_id, **updates)

        if 'prompt_ids' in data and data['prompt_ids'] is not None:
            prompt_ids = self._normalize_prompt_ids(data['prompt_ids'])
            # Replace items: delete existing and recreate ordered items
            existing = self.item_repo.get_by_set(favorite_id)
            for item in existing:
                self.item_repo.delete(item.id)
            for idx, pid in enumerate(prompt_ids):
                self.item_repo.create(favorite_set_id=favorite_id, prompt_id=pid, position=idx)

        return self.favorite_repo.get_with_items(favorite_id, user_id)

    def delete(self, user_id: int, favorite_id: int) -> bool:
        self._require_owned(user_id, favorite_id)
        return self.favorite_repo.delete(favorite_id)

    # Helpers
    def _require_owned(self, user_id: int, favorite_id: int) -> FavoriteSet:
        favorite = self.favorite_repo.get_with_items(favorite_id, user_id)
        if not favorite:
            raise ValueError("Favorite not found or not owned by user")
        return favorite

    def _validate_name(self, user_id: int, name: str) -> None:
        if not name or not name.strip():
            raise ValueError("Name is required")
        if len(name.strip()) > 150:
            raise ValueError("Name must be 150 characters or fewer")
        if self.favorite_repo.exists_by_name(user_id, name):
            raise ValueError("Favorite with this name already exists")

    def _normalize_prompt_ids(self, prompt_ids: Optional[List[int]]) -> List[int]:
        if not prompt_ids:
            return []
        # Ensure uniqueness while preserving order
        seen = set()
        normalized: List[int] = []
        for pid in prompt_ids:
            if not isinstance(pid, int):
                try:
                    pid = int(pid)
                except Exception:
                    continue
            if pid in seen:
                continue
            # Ensure prompt exists
            if self.prompt_repo.get_by_id(pid) is None:
                continue
            seen.add(pid)
            normalized.append(pid)
        return normalized


