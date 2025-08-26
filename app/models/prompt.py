"""
Prompt model representing a text prompt in the system.
"""
from datetime import datetime
from .base import db, BaseModel
from sqlalchemy.orm import relationship


# Association table for many-to-many relationship
prompt_tags = db.Table('prompt_tags',
    db.Column('prompt_id', db.Integer, db.ForeignKey('prompts.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
)


class Prompt(BaseModel):
    """Prompt model for storing text prompts."""
    
    __tablename__ = 'prompts'
    
    # Fields specific to Prompt
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_public = db.Column(db.Boolean, default=False, nullable=False, index=True)
    order = db.Column(db.Integer, nullable=False, default=0, index=True)
    
    # Ownership
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True, nullable=True)
    owner = relationship('User', backref=db.backref('prompts', lazy=True))
    
    # Relationships
    tags = db.relationship('Tag', secondary=prompt_tags, lazy='subquery',
                          backref=db.backref('prompts', lazy=True))
    
    # Attached prompts relationships (defined in AttachedPrompt model with backref)
    
    def __repr__(self):
        """String representation of the prompt."""
        return f'<Prompt {self.id}: {self.title[:30]}...>'
    
    def to_dict(self, include_attached_prompts=False):
        """Convert prompt to dictionary for JSON serialization."""
        base_dict = super().to_dict()
        base_dict.update({
            'title': self.title,
            'content': self.content,
            'description': self.description,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'order': self.order,
            'tags': [tag.to_dict() for tag in self.tags]
        })
        
        if include_attached_prompts:
            attached_prompts = self.get_attached_prompts()
            base_dict['attached_prompts'] = [
                {
                    'id': ap.attached_prompt.id,
                    'title': ap.attached_prompt.title,
                    'content': ap.attached_prompt.content,
                    'order': ap.order
                } for ap in attached_prompts
            ]
        
        return base_dict
    
    @classmethod
    def get_active(cls):
        """Get all active prompts."""
        return cls.query.filter_by(is_active=True).all()
    
    @classmethod
    def search(cls, query):
        """Search prompts by title or content."""
        search_term = f'%{query}%'
        return cls.query.filter(
            db.or_(
                cls.title.ilike(search_term),
                cls.content.ilike(search_term),
                cls.description.ilike(search_term)
            )
        ).all()
    
    def add_tag(self, tag):
        """Add a tag to this prompt."""
        if tag not in self.tags:
            self.tags.append(tag)
            db.session.commit()
    
    def remove_tag(self, tag):
        """Remove a tag from this prompt."""
        if tag in self.tags:
            self.tags.remove(tag)
            db.session.commit()
    
    def validate(self):
        """Validate prompt data before saving."""
        errors = []
        
        if not self.title or not self.title.strip():
            errors.append("Title is required")
        
        if not self.content or not self.content.strip():
            errors.append("Content is required")
        
        if len(self.title) > 255:
            errors.append("Title must be less than 255 characters")
        
        return errors
    
    def get_attached_prompts(self):
        """Get all prompts attached to this prompt."""
        # Use cached data if available
        if hasattr(self, '_attached_prompts_data'):
            return self._attached_prompts_data
        
        # Fallback to direct query
        from .attached_prompt import AttachedPrompt
        return AttachedPrompt.get_attached_prompts(self.id)
    
    def get_prompts_this_is_attached_to(self):
        """Get all prompts that this prompt is attached to."""
        from .attached_prompt import AttachedPrompt
        return AttachedPrompt.get_prompts_attached_to(self.id)
    
    def has_attached_prompts(self):
        """Check if this prompt has any attached prompts."""
        return len(self.get_attached_prompts()) > 0
    
    def is_attached_to_any_prompt(self):
        """Check if this prompt is attached to any other prompt."""
        return len(self.get_prompts_this_is_attached_to()) > 0