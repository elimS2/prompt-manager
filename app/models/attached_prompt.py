"""
AttachedPrompt model for storing relationships between prompts.
"""
from datetime import datetime
from sqlalchemy import UniqueConstraint
from .base import db, BaseModel


class AttachedPrompt(BaseModel):
    """Model for storing attached prompt relationships."""
    
    __tablename__ = 'attached_prompts'
    
    # Fields
    main_prompt_id = db.Column(db.Integer, db.ForeignKey('prompts.id', ondelete='CASCADE'), nullable=False)
    attached_prompt_id = db.Column(db.Integer, db.ForeignKey('prompts.id', ondelete='CASCADE'), nullable=False)
    order = db.Column(db.Integer, nullable=False, default=0)
    usage_count = db.Column(db.Integer, nullable=False, default=0, index=True)
    
    # Relationships
    main_prompt = db.relationship('Prompt', foreign_keys=[main_prompt_id], backref='attached_prompts')
    attached_prompt = db.relationship('Prompt', foreign_keys=[attached_prompt_id], backref='attached_to_prompts')
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('main_prompt_id', 'attached_prompt_id', name='unique_attached_prompt'),
    )
    
    def __repr__(self):
        """String representation of the attached prompt."""
        return f'<AttachedPrompt {self.main_prompt_id} -> {self.attached_prompt_id}>'
    
    def to_dict(self):
        """Convert attached prompt to dictionary for JSON serialization."""
        base_dict = super().to_dict()
        base_dict.update({
            'main_prompt_id': self.main_prompt_id,
            'attached_prompt_id': self.attached_prompt_id,
            'order': self.order,
            'usage_count': self.usage_count,
            'main_prompt': self.main_prompt.to_dict() if self.main_prompt else None,
            'attached_prompt': self.attached_prompt.to_dict() if self.attached_prompt else None
        })
        return base_dict
    
    def validate(self):
        """Validate attached prompt data before saving."""
        errors = []
        
        if not self.main_prompt_id:
            errors.append("Main prompt ID is required")
        
        if not self.attached_prompt_id:
            errors.append("Attached prompt ID is required")
        
        if self.main_prompt_id == self.attached_prompt_id:
            errors.append("Cannot attach prompt to itself")
        
        if self.order < 0:
            errors.append("Order must be non-negative")
        
        return errors
    
    @classmethod
    def get_attached_prompts(cls, main_prompt_id: int):
        """Get all prompts attached to a main prompt, ordered by order field."""
        return cls.query.filter_by(main_prompt_id=main_prompt_id)\
                       .order_by(cls.order)\
                       .all()
    
    @classmethod
    def get_prompts_attached_to(cls, prompt_id: int):
        """Get all prompts that have the specified prompt attached to them."""
        return cls.query.filter_by(attached_prompt_id=prompt_id)\
                       .order_by(cls.order)\
                       .all()
    
    @classmethod
    def exists(cls, main_prompt_id: int, attached_prompt_id: int) -> bool:
        """Check if an attachment relationship already exists."""
        return cls.query.filter_by(
            main_prompt_id=main_prompt_id,
            attached_prompt_id=attached_prompt_id
        ).first() is not None
    
    def increment_usage(self):
        """Increment the usage count for this attachment."""
        self.usage_count += 1
        db.session.commit()
    
    @classmethod
    def get_popular_combinations(cls, limit: int = 10):
        """Get the most frequently used prompt combinations."""
        return cls.query.order_by(cls.usage_count.desc()).limit(limit).all() 