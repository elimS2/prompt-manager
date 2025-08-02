"""Data access layer following Repository pattern."""

from .base import BaseRepository
from .prompt_repository import PromptRepository
from .tag_repository import TagRepository

__all__ = ['BaseRepository', 'PromptRepository', 'TagRepository']