"""
Base repository class implementing common data access patterns.
Following Repository pattern for data access abstraction.
"""
from typing import TypeVar, Generic, Type, List, Optional, Dict, Any
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_
from app.models.base import db, BaseModel

# Type variable for model classes
ModelType = TypeVar('ModelType', bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """
    Abstract base repository providing common CRUD operations.
    
    This class implements the Repository pattern, providing a layer of abstraction
    between the domain models and data access logic.
    """
    
    def __init__(self, model: Type[ModelType]):
        """Initialize repository with model class."""
        self.model = model
        self.session = db.session
    
    def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get a single record by ID."""
        return self.model.query.get(id)
    
    def get_all(self, **filters) -> List[ModelType]:
        """
        Get all records with optional filtering.
        
        Args:
            **filters: Keyword arguments for filtering
            
        Returns:
            List of model instances
        """
        query = self.model.query
        
        if filters:
            query = self._apply_filters(query, filters)
            
        return query.all()
    
    def get_paginated(self, page: int = 1, per_page: int = 20, **filters) -> Dict[str, Any]:
        """
        Get paginated results.
        
        Args:
            page: Page number (1-indexed)
            per_page: Items per page
            **filters: Additional filters
            
        Returns:
            Dictionary with items, total, page, per_page, has_next, has_prev
        """
        query = self.model.query
        
        if filters:
            query = self._apply_filters(query, filters)
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'items': pagination.items,
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
            'total_pages': pagination.pages
        }
    
    def get_paginated_with_sorting(self, page: int = 1, per_page: int = 20, 
                                 sort_by: str = 'created', sort_order: str = 'desc',
                                 **filters) -> Dict[str, Any]:
        """
        Get paginated results with sorting.
        
        Args:
            page: Page number (1-indexed)
            per_page: Items per page
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')
            **filters: Additional filters
            
        Returns:
            Dictionary with items, total, page, per_page, has_next, has_prev
        """
        query = self.model.query
        
        if filters:
            query = self._apply_filters(query, filters)
        
        # Apply sorting
        query = self._apply_sorting(query, sort_by, sort_order)
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'items': pagination.items,
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
            'total_pages': pagination.pages
        }
    
    def _apply_sorting(self, query, sort_by: str, sort_order: str):
        """
        Apply sorting to query.
        
        Args:
            query: SQLAlchemy query
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')
            
        Returns:
            Query with sorting applied
        """
        # Default sorting by created_at
        if sort_by == 'created':
            sort_field = self.model.created_at
        elif sort_by == 'updated':
            sort_field = self.model.updated_at
        elif sort_by == 'title':
            sort_field = self.model.title
        else:
            sort_field = self.model.created_at
        
        if sort_order == 'asc':
            return query.order_by(sort_field.asc())
        else:
            return query.order_by(sort_field.desc())
    
    def _apply_filters(self, query, filters: Dict[str, Any]):
        """
        Apply filters to query, handling special filters that are not model fields.
        
        Args:
            query: SQLAlchemy query
            filters: Dictionary of filters
            
        Returns:
            Query with filters applied
        """
        # Handle special filters that are not model fields
        model_filters = {}
        for key, value in filters.items():
            if key == 'ids':
                # Handle ID filtering
                if value:
                    query = query.filter(self.model.id.in_(value))
            elif hasattr(self.model, key):
                # Only add filters that are actual model fields and not None
                if value is not None:
                    model_filters[key] = value
        
        # Apply model field filters
        if model_filters:
            query = query.filter_by(**model_filters)
        
        return query
    
    def create(self, **data) -> ModelType:
        """
        Create a new record.
        
        Args:
            **data: Model attributes
            
        Returns:
            Created model instance
        """
        instance = self.model(**data)
        self.session.add(instance)
        self.session.commit()
        return instance
    
    def update(self, id: int, **data) -> Optional[ModelType]:
        """
        Update an existing record.
        
        Args:
            id: Record ID
            **data: Updated attributes
            
        Returns:
            Updated model instance or None if not found
        """
        instance = self.get_by_id(id)
        if instance:
            for key, value in data.items():
                if hasattr(instance, key):
                    # Handle boolean conversion for common boolean fields
                    if key in ['is_active', 'is_deleted', 'is_archived'] and isinstance(value, str):
                        value = value.lower() in ('true', '1', 'on', 'yes')
                    setattr(instance, key, value)
            self.session.commit()
        return instance
    
    def delete(self, id: int) -> bool:
        """
        Delete a record by ID.
        
        Args:
            id: Record ID
            
        Returns:
            True if deleted, False if not found
        """
        instance = self.get_by_id(id)
        if instance:
            self.session.delete(instance)
            self.session.commit()
            return True
        return False
    
    def bulk_create(self, items: List[Dict[str, Any]]) -> List[ModelType]:
        """
        Create multiple records in a single transaction.
        
        Args:
            items: List of dictionaries with model attributes
            
        Returns:
            List of created model instances
        """
        instances = [self.model(**item) for item in items]
        self.session.bulk_save_objects(instances, return_defaults=True)
        self.session.commit()
        return instances
    
    def exists(self, **filters) -> bool:
        """
        Check if a record exists with given filters.
        
        Args:
            **filters: Filter criteria
            
        Returns:
            True if exists, False otherwise
        """
        query = self.model.query
        if filters:
            query = self._apply_filters(query, filters)
        return query.first() is not None
    
    def count(self, **filters) -> int:
        """
        Count records with optional filtering.
        
        Args:
            **filters: Filter criteria
            
        Returns:
            Number of records
        """
        query = self.model.query
        if filters:
            query = self._apply_filters(query, filters)
        return query.count()
    
    def find_one(self, **filters) -> Optional[ModelType]:
        """
        Find a single record by filters.
        
        Args:
            **filters: Filter criteria
            
        Returns:
            Model instance or None
        """
        query = self.model.query
        if filters:
            query = self._apply_filters(query, filters)
        return query.first()
    
    def commit(self):
        """Commit the current transaction."""
        self.session.commit()
    
    def rollback(self):
        """Rollback the current transaction."""
        self.session.rollback()