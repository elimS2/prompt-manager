"""Data access layer following Repository pattern."""

from .base import BaseRepository
from .prompt_repository import PromptRepository
from .tag_repository import TagRepository
from .attached_prompt_repository import AttachedPromptRepository
from .user_repository import UserRepository
from .favorite_set_repository import FavoriteSetRepository, FavoriteSetItemRepository

__all__ = ['BaseRepository', 'PromptRepository', 'TagRepository', 'AttachedPromptRepository', 'UserRepository', 'FavoriteSetRepository', 'FavoriteSetItemRepository']