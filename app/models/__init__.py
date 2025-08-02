"""Domain models for Prompt Manager."""

from .base import db, BaseModel
from .prompt import Prompt, prompt_tags
from .tag import Tag

__all__ = ['db', 'BaseModel', 'Prompt', 'Tag', 'prompt_tags']