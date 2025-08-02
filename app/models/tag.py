"""
Tag model for categorizing prompts.
"""
import re
from .base import db, BaseModel


class Tag(BaseModel):
    """Tag model for categorizing prompts."""
    
    __tablename__ = 'tags'
    
    # Fields specific to Tag
    name = db.Column(db.String(100), unique=True, nullable=False)
    color = db.Column(db.String(7), default='#3B82F6')  # Default blue color
    
    def __repr__(self):
        """String representation of the tag."""
        return f'<Tag {self.id}: {self.name}>'
    
    def to_dict(self):
        """Convert tag to dictionary for JSON serialization."""
        base_dict = super().to_dict()
        base_dict.update({
            'name': self.name,
            'color': self.color,
            'prompt_count': len(self.prompts) if hasattr(self, 'prompts') else 0
        })
        return base_dict
    
    @classmethod
    def get_by_name(cls, name):
        """Get tag by name."""
        return cls.query.filter_by(name=name).first()
    
    @classmethod
    def get_or_create(cls, name, color=None):
        """Get existing tag or create new one."""
        # Normalize tag name
        name = cls.normalize_name(name)
        
        tag = cls.get_by_name(name)
        if not tag:
            tag = cls(name=name)
            if color:
                tag.color = color
            tag.save()
        
        return tag
    
    @classmethod
    def get_popular(cls, limit=10):
        """Get most popular tags by usage count."""
        return db.session.query(cls)\
            .join(cls.prompts)\
            .group_by(cls.id)\
            .order_by(db.func.count(cls.id).desc())\
            .limit(limit)\
            .all()
    
    @staticmethod
    def normalize_name(name):
        """Normalize tag name: lowercase, trim, replace spaces with hyphens."""
        if not name:
            return ""
        # Convert to lowercase and strip whitespace
        name = name.lower().strip()
        # Replace multiple spaces with single hyphen
        name = re.sub(r'\s+', '-', name)
        # Remove special characters except hyphens
        name = re.sub(r'[^a-z0-9\-]', '', name)
        # Remove multiple consecutive hyphens
        name = re.sub(r'-+', '-', name)
        # Remove leading/trailing hyphens
        name = name.strip('-')
        return name
    
    def validate(self):
        """Validate tag data before saving."""
        errors = []
        
        if not self.name or not self.name.strip():
            errors.append("Tag name is required")
        
        if len(self.name) > 100:
            errors.append("Tag name must be less than 100 characters")
        
        # Validate color format (hex color)
        if self.color:
            if not re.match(r'^#[0-9A-Fa-f]{6}$', self.color):
                errors.append("Color must be a valid hex color (e.g., #FF5733)")
        
        # Check for duplicate names (case-insensitive)
        normalized_name = self.normalize_name(self.name)
        existing = Tag.query.filter(
            db.func.lower(Tag.name) == normalized_name,
            Tag.id != self.id
        ).first()
        if existing:
            errors.append(f"Tag '{normalized_name}' already exists")
        
        return errors
    
    def save(self):
        """Override save to normalize name before saving."""
        self.name = self.normalize_name(self.name)
        return super().save()