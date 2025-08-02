"""
Base model class with common fields and methods.
Following DRY principle by extracting common functionality.
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class BaseModel(db.Model):
    """Abstract base model with common fields."""
    
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def save(self):
        """Save the model to database."""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """Delete the model from database."""
        db.session.delete(self)
        db.session.commit()
    
    @classmethod
    def get_by_id(cls, id):
        """Get model by ID."""
        return cls.query.get(id)
    
    @classmethod
    def get_all(cls):
        """Get all models."""
        return cls.query.all()
    
    def to_dict(self):
        """Convert model to dictionary. To be overridden by subclasses."""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }