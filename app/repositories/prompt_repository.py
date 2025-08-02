"""
Repository for Prompt model with specific query methods.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import or_, and_, func
from app.models import Prompt, Tag, prompt_tags
from .base import BaseRepository


class PromptRepository(BaseRepository[Prompt]):
    """Repository for managing Prompt data access."""
    
    def __init__(self):
        """Initialize PromptRepository."""
        super().__init__(Prompt)
    
    def get_all_active(self) -> List[Prompt]:
        """Get all active prompts."""
        return self.model.query.filter_by(is_active=True).all()
    
    def get_by_ids(self, ids: List[int]) -> List[Prompt]:
        """
        Get multiple prompts by their IDs.
        
        Args:
            ids: List of prompt IDs
            
        Returns:
            List of Prompt instances
        """
        if not ids:
            return []
        return self.model.query.filter(self.model.id.in_(ids)).all()
    
    def search(self, query: str, include_inactive: bool = False) -> List[Prompt]:
        """
        Search prompts by title, content, or description.
        
        Args:
            query: Search query string
            include_inactive: Whether to include inactive prompts
            
        Returns:
            List of matching prompts
        """
        if not query:
            return []
        
        search_term = f'%{query}%'
        base_query = self.model.query.filter(
            or_(
                self.model.title.ilike(search_term),
                self.model.content.ilike(search_term),
                self.model.description.ilike(search_term)
            )
        )
        
        if not include_inactive:
            base_query = base_query.filter_by(is_active=True)
        
        return base_query.all()
    
    def get_by_tags(self, tag_ids: List[int], match_all: bool = False) -> List[Prompt]:
        """
        Get prompts by tag IDs.
        
        Args:
            tag_ids: List of tag IDs
            match_all: If True, return prompts that have ALL tags; 
                      If False, return prompts that have ANY of the tags
            
        Returns:
            List of prompts
        """
        if not tag_ids:
            return []
        
        if match_all:
            # Find prompts that have ALL specified tags
            # Using subquery to count matching tags
            subquery = (
                self.session.query(prompt_tags.c.prompt_id)
                .filter(prompt_tags.c.tag_id.in_(tag_ids))
                .group_by(prompt_tags.c.prompt_id)
                .having(func.count(prompt_tags.c.tag_id) == len(tag_ids))
                .subquery()
            )
            
            return (
                self.model.query
                .filter(self.model.id.in_(subquery))
                .filter_by(is_active=True)
                .all()
            )
        else:
            # Find prompts that have ANY of the specified tags
            return (
                self.model.query
                .join(prompt_tags)
                .filter(prompt_tags.c.tag_id.in_(tag_ids))
                .filter(self.model.is_active == True)
                .distinct()
                .all()
            )
    
    def get_by_tag_names(self, tag_names: List[str], match_all: bool = False) -> List[Prompt]:
        """
        Get prompts by tag names.
        
        Args:
            tag_names: List of tag names
            match_all: If True, return prompts that have ALL tags
            
        Returns:
            List of prompts
        """
        if not tag_names:
            return []
        
        # Normalize tag names
        from app.models import Tag
        normalized_names = [Tag.normalize_name(name) for name in tag_names]
        
        # Get tag IDs
        tags = Tag.query.filter(Tag.name.in_(normalized_names)).all()
        tag_ids = [tag.id for tag in tags]
        
        if not tag_ids:
            return []
        
        return self.get_by_tags(tag_ids, match_all)
    
    def get_recent(self, limit: int = 10, include_inactive: bool = False) -> List[Prompt]:
        """
        Get most recently created prompts.
        
        Args:
            limit: Maximum number of prompts to return
            include_inactive: Whether to include inactive prompts
            
        Returns:
            List of recent prompts
        """
        query = self.model.query
        
        if not include_inactive:
            query = query.filter_by(is_active=True)
        
        return query.order_by(self.model.created_at.desc()).limit(limit).all()
    
    def get_recently_updated(self, limit: int = 10, include_inactive: bool = False) -> List[Prompt]:
        """
        Get most recently updated prompts.
        
        Args:
            limit: Maximum number of prompts to return
            include_inactive: Whether to include inactive prompts
            
        Returns:
            List of recently updated prompts
        """
        query = self.model.query
        
        if not include_inactive:
            query = query.filter_by(is_active=True)
        
        return query.order_by(self.model.updated_at.desc()).limit(limit).all()
    
    def get_with_filters(self, filters: Dict[str, Any]) -> List[Prompt]:
        """
        Get prompts with complex filtering.
        
        Args:
            filters: Dictionary of filter criteria
                - search: Search in title/content/description
                - tags: List of tag IDs
                - is_active: Boolean
                - created_after: DateTime
                - created_before: DateTime
                
        Returns:
            List of filtered prompts
        """
        query = self.model.query
        
        # Search filter
        if 'search' in filters and filters['search']:
            search_term = f"%{filters['search']}%"
            query = query.filter(
                or_(
                    self.model.title.ilike(search_term),
                    self.model.content.ilike(search_term),
                    self.model.description.ilike(search_term)
                )
            )
        
        # Tag filter
        if 'tags' in filters and filters['tags']:
            query = query.join(prompt_tags).filter(prompt_tags.c.tag_id.in_(filters['tags']))
        
        # Active filter
        if 'is_active' in filters and filters['is_active'] is not None:
            query = query.filter(self.model.is_active == filters['is_active'])
        
        # Date filters
        if 'created_after' in filters:
            query = query.filter(self.model.created_at >= filters['created_after'])
        
        if 'created_before' in filters:
            query = query.filter(self.model.created_at <= filters['created_before'])
        
        return query.distinct().all()
    
    def get_with_filters_and_sorting(self, filters: Dict[str, Any], 
                                   sort_by: str = 'created', 
                                   sort_order: str = 'desc') -> List[Prompt]:
        """
        Get prompts with complex filtering and sorting.
        
        Args:
            filters: Dictionary of filter criteria
                - search: Search in title/content/description
                - tags: List of tag IDs
                - is_active: Boolean
                - created_after: DateTime
                - created_before: DateTime
            sort_by: Field to sort by ('created', 'updated', 'title')
            sort_order: Sort order ('asc' or 'desc')
                
        Returns:
            List of filtered and sorted prompts
        """
        query = self.model.query
        
        # Search filter
        if 'search' in filters and filters['search']:
            search_term = f"%{filters['search']}%"
            query = query.filter(
                or_(
                    self.model.title.ilike(search_term),
                    self.model.content.ilike(search_term),
                    self.model.description.ilike(search_term)
                )
            )
        
        # Tag filter
        if 'tags' in filters and filters['tags']:
            query = query.join(prompt_tags).filter(prompt_tags.c.tag_id.in_(filters['tags']))
        
        # Active filter
        if 'is_active' in filters and filters['is_active'] is not None:
            query = query.filter(self.model.is_active == filters['is_active'])
        
        # Date filters
        if 'created_after' in filters:
            query = query.filter(self.model.created_at >= filters['created_after'])
        
        if 'created_before' in filters:
            query = query.filter(self.model.created_at <= filters['created_before'])
        
        # Apply sorting
        query = self._apply_sorting(query, sort_by, sort_order)
        
        return query.distinct().all()
    
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
    
    def soft_delete(self, id: int) -> bool:
        """
        Soft delete a prompt (set is_active to False).
        
        Args:
            id: Prompt ID
            
        Returns:
            True if successful, False if not found
        """
        prompt = self.get_by_id(id)
        if prompt:
            prompt.is_active = False
            self.commit()
            return True
        return False
    
    def restore(self, id: int) -> bool:
        """
        Restore a soft-deleted prompt.
        
        Args:
            id: Prompt ID
            
        Returns:
            True if successful, False if not found
        """
        prompt = self.get_by_id(id)
        if prompt:
            prompt.is_active = True
            self.commit()
            return True
        return False