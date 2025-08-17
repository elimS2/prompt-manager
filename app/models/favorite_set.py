"""Models for user-scoped favorite prompt combinations."""
from sqlalchemy import UniqueConstraint
from .base import db, BaseModel


class FavoriteSet(BaseModel):
    """A user-defined set of prompts saved as a favorite combination."""

    __tablename__ = 'favorite_sets'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    items = db.relationship(
        'FavoriteSetItem',
        backref='favorite_set',
        cascade='all, delete-orphan',
        order_by='FavoriteSetItem.position',
        lazy='joined'
    )

    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_favorite_set_user_name'),
    )

    def __repr__(self):
        return f"<FavoriteSet {self.id} user={self.user_id} name='{self.name}'>"

    def to_dict(self):
        base = super().to_dict()
        base.update({
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'items': [item.to_dict() for item in (self.items or [])]
        })
        return base


class FavoriteSetItem(BaseModel):
    """An item inside a FavoriteSet that references a Prompt and preserves order."""

    __tablename__ = 'favorite_set_items'

    favorite_set_id = db.Column(
        db.Integer,
        db.ForeignKey('favorite_sets.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    prompt_id = db.Column(
        db.Integer,
        db.ForeignKey('prompts.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
    )
    position = db.Column(db.Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint('favorite_set_id', 'prompt_id', name='uq_favorite_item_unique_prompt'),
    )

    def __repr__(self):
        return f"<FavoriteSetItem set={self.favorite_set_id} prompt={self.prompt_id} pos={self.position}>"

    def to_dict(self):
        base = super().to_dict()
        base.update({
            'favorite_set_id': self.favorite_set_id,
            'prompt_id': self.prompt_id,
            'position': self.position,
        })
        return base


