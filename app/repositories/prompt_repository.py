"""
Repository for Prompt model with specific query methods.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import or_, and_, func
from app.models import Prompt, Tag, prompt_tags, AttachedPrompt
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
        
        # Normalize query for better matching
        query = query.strip().lower()
        
        # Create multiple search patterns for better matching
        search_patterns = [
            f'%{query}%',  # Contains query anywhere
            f'{query}%',   # Starts with query
            f'% {query}%', # Word boundary match
            f'%{query} %'  # Word boundary match
        ]
        
        # Build search conditions
        search_conditions = []
        for pattern in search_patterns:
            search_conditions.extend([
                self.model.title.ilike(pattern),
                self.model.content.ilike(pattern),
                self.model.description.ilike(pattern)
            ])
        
        # Also search in tags
        from app.models import Tag, prompt_tags
        tag_search = (
            self.model.query
            .join(prompt_tags)
            .join(Tag)
            .filter(Tag.name.ilike(f'%{query}%'))
        )
        
        # Main search query
        base_query = self.model.query.filter(or_(*search_conditions))
        
        # Combine with tag search
        combined_query = base_query.union(tag_search)
        
        # Apply active filter if needed
        if not include_inactive:
            combined_query = combined_query.filter(self.model.is_active == True)
        
        # Return distinct results ordered by relevance
        return combined_query.distinct().order_by(self.model.title).all()
    
    def get_by_tags(self, tag_ids: List[int], match_all: bool = False, is_active: Optional[bool] = None) -> List[Prompt]:
        """
        Get prompts by tag IDs.
        
        Args:
            tag_ids: List of tag IDs
            match_all: If True, return prompts that have ALL tags; 
                      If False, return prompts that have ANY of the tags
            is_active: Filter by active status (None = no filter, True = active only, False = inactive only)
            
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
            
            query = self.model.query.filter(self.model.id.in_(subquery))
            
            # Apply active status filter if specified
            if is_active is not None:
                query = query.filter(self.model.is_active == is_active)
            
            return query.all()
        else:
            # Find prompts that have ANY of the specified tags
            query = (
                self.model.query
                .join(prompt_tags)
                .filter(prompt_tags.c.tag_id.in_(tag_ids))
            )
            
            # Apply active status filter if specified
            if is_active is not None:
                query = query.filter(self.model.is_active == is_active)
            
            return query.distinct().all()
    
    def get_by_tag_names(self, tag_names: List[str], match_all: bool = False, is_active: Optional[bool] = None) -> List[Prompt]:
        """
        Get prompts by tag names.
        
        Args:
            tag_names: List of tag names
            match_all: If True, return prompts that have ALL tags
            is_active: Filter by active status (None = no filter, True = active only, False = inactive only)
            
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
        
        return self.get_by_tags(tag_ids, match_all, is_active)
    
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
        
        # Search filter with enhanced algorithm
        if 'search' in filters and filters['search']:
            search_query = filters['search'].strip().lower()
            
            # Create multiple search patterns for better matching
            search_patterns = [
                f'%{search_query}%',  # Contains query anywhere
                f'{search_query}%',   # Starts with query
                f'% {search_query}%', # Word boundary match
                f'%{search_query} %'  # Word boundary match
            ]
            
            # Build search conditions
            search_conditions = []
            for pattern in search_patterns:
                search_conditions.extend([
                    self.model.title.ilike(pattern),
                    self.model.content.ilike(pattern),
                    self.model.description.ilike(pattern)
                ])
            
            # Also search in tags
            from app.models import Tag
            tag_search = (
                self.model.query
                .join(prompt_tags)
                .join(Tag)
                .filter(Tag.name.ilike(f'%{search_query}%'))
            )
            
            # Main search query
            base_query = self.model.query.filter(or_(*search_conditions))
            
            # Combine with tag search
            combined_query = base_query.union(tag_search)
            
            # Apply other filters to combined query (e.g., ownership/public)
            combined_query = self._apply_filters(combined_query, filters)
            if 'is_active' in filters and filters['is_active'] is not None:
                combined_query = combined_query.filter(self.model.is_active == filters['is_active'])
            
            if 'created_after' in filters:
                combined_query = combined_query.filter(self.model.created_at >= filters['created_after'])
            
            if 'created_before' in filters:
                combined_query = combined_query.filter(self.model.created_at <= filters['created_before'])
            
            return combined_query.distinct().all()
        
        # If no search, apply other filters normally
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
        
        # Search filter with enhanced algorithm
        if 'search' in filters and filters['search']:
            search_query = filters['search'].strip().lower()
            
            # Create multiple search patterns for better matching
            search_patterns = [
                f'%{search_query}%',  # Contains query anywhere
                f'{search_query}%',   # Starts with query
                f'% {search_query}%', # Word boundary match
                f'%{search_query} %'  # Word boundary match
            ]
            
            # Build search conditions
            search_conditions = []
            for pattern in search_patterns:
                search_conditions.extend([
                    self.model.title.ilike(pattern),
                    self.model.content.ilike(pattern),
                    self.model.description.ilike(pattern)
                ])
            
            # Also search in tags
            from app.models import Tag
            tag_search = (
                self.model.query
                .join(prompt_tags)
                .join(Tag)
                .filter(Tag.name.ilike(f'%{search_query}%'))
            )
            
            # Main search query
            base_query = self.model.query.filter(or_(*search_conditions))
            
            # Combine with tag search
            combined_query = base_query.union(tag_search)
            
            # Apply other filters to combined query
            if 'is_active' in filters and filters['is_active'] is not None:
                combined_query = combined_query.filter(self.model.is_active == filters['is_active'])
            
            if 'created_after' in filters:
                combined_query = combined_query.filter(self.model.created_at >= filters['created_after'])
            
            if 'created_before' in filters:
                combined_query = combined_query.filter(self.model.created_at <= filters['created_before'])
            
            # Apply sorting and return
            combined_query = self._apply_sorting(combined_query, sort_by, sort_order)
            return combined_query.distinct().all()
        
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
        
        # Apply remaining filters (e.g., ownership/public)
        query = self._apply_filters(query, filters)
        
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
        # Default sorting by order field for consistent drag & drop experience
        if sort_by == 'order':
            sort_field = self.model.order
        elif sort_by == 'created':
            sort_field = self.model.created_at
        elif sort_by == 'updated':
            sort_field = self.model.updated_at
        elif sort_by == 'title':
            sort_field = self.model.title
        else:
            # Default to order for drag & drop support
            sort_field = self.model.order
        
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
    
    def _apply_filters(self, query, filters: Dict[str, Any]):
        """
        Apply filters to query, handling search and other special filters.
        
        Args:
            query: SQLAlchemy query
            filters: Dictionary of filters
            
        Returns:
            Query with filters applied
        """
        from sqlalchemy import or_
        from app.models import prompt_tags, Tag
        
        # Handle search filter
        if 'search' in filters and filters['search']:
            search_query = filters['search'].strip().lower()
            
            # Create multiple search patterns for better matching
            search_patterns = [
                f'%{search_query}%',  # Contains query anywhere
                f'{search_query}%',   # Starts with query
                f'% {search_query}%', # Word boundary match
                f'{search_query} %'   # Word boundary match
            ]
            
            # Build search conditions
            search_conditions = []
            for pattern in search_patterns:
                search_conditions.extend([
                    self.model.title.ilike(pattern),
                    self.model.content.ilike(pattern),
                    self.model.description.ilike(pattern)
                ])
            
            # Also search in tags
            tag_search = (
                self.model.query
                .join(prompt_tags)
                .join(Tag)
                .filter(Tag.name.ilike(f'%{search_query}%'))
            )
            
            # Main search query
            base_query = self.model.query.filter(or_(*search_conditions))
            
            # Combine with tag search
            query = base_query.union(tag_search)
        
        # Handle other filters manually (don't use parent method for search)
        # Handle special filters that are not model fields
        model_filters = {}
        for key, value in filters.items():
            if key == 'search':
                # Already handled above
                continue
            elif key == 'ids':
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
    
    def update_order(self, prompt_id: int, new_order: int) -> bool:
        """
        Update the order of a specific prompt.
        
        Args:
            prompt_id: ID of the prompt to update
            new_order: New order value
            
        Returns:
            True if successful, False if prompt not found
        """
        prompt = self.get_by_id(prompt_id)
        if prompt:
            prompt.order = new_order
            self.commit()
            return True
        return False
    
    def bulk_update_order(self, order_mapping: Dict[int, int]) -> bool:
        """
        Update order for multiple prompts at once.
        
        Args:
            order_mapping: Dictionary mapping prompt_id to new order value
            
        Returns:
            True if all updates successful
        """
        try:
            for prompt_id, new_order in order_mapping.items():
                prompt = self.get_by_id(prompt_id)
                if prompt:
                    prompt.order = new_order
            self.commit()
            return True
        except Exception:
            self.rollback()
            return False
    
    def get_with_attached_prompts(self, prompt_id: int) -> Optional[Prompt]:
        """
        Get a prompt with its attached prompts loaded.
        
        Args:
            prompt_id: ID of the prompt to retrieve
            
        Returns:
            Prompt instance with attached_prompts relationship loaded, or None if not found
        """
        return self.model.query.options(
            self.db.joinedload(Prompt.attached_prompts).joinedload(AttachedPrompt.attached_prompt)
        ).filter_by(id=prompt_id).first()
    
    def get_prompts_with_attachments(self, include_inactive: bool = False) -> List[Prompt]:
        """
        Get all prompts that have attached prompts.
        
        Args:
            include_inactive: Whether to include inactive prompts
            
        Returns:
            List of prompts that have attached prompts
        """
        query = self.model.query.join(AttachedPrompt, Prompt.id == AttachedPrompt.main_prompt_id)
        
        if not include_inactive:
            query = query.filter(self.model.is_active == True)
        
        return query.distinct().all()
    
    def get_prompts_with_attachments_loaded(self, include_inactive: bool = False) -> List[Prompt]:
        """
        Get all prompts with their attached prompts pre-loaded.
        
        Args:
            include_inactive: Whether to include inactive prompts
            
        Returns:
            List of prompts with attached_prompts relationship loaded
        """
        query = self.model.query.options(
            self.db.joinedload(Prompt.attached_prompts).joinedload(AttachedPrompt.attached_prompt)
        )
        
        if not include_inactive:
            query = query.filter(self.model.is_active == True)
        
        return query.all()
    
    def get_available_for_attachment(self, main_prompt_id: int, exclude_ids: Optional[List[int]] = None) -> List[Prompt]:
        """
        Get prompts that can be attached to a specific prompt.
        
        Args:
            main_prompt_id: ID of the main prompt
            exclude_ids: List of prompt IDs to exclude (e.g., already attached)
            
        Returns:
            List of prompts available for attachment
        """
        # Get IDs of prompts already attached to this main prompt
        attached_ids = [
            ap.attached_prompt_id 
            for ap in AttachedPrompt.query.filter_by(main_prompt_id=main_prompt_id).all()
        ]
        
        # Add the main prompt itself to exclude list
        exclude_ids = exclude_ids or []
        exclude_ids.append(main_prompt_id)
        exclude_ids.extend(attached_ids)
        
        # Get available prompts
        return self.model.query.filter(
            self.model.is_active == True,
            ~self.model.id.in_(exclude_ids)
        ).order_by(self.model.title).all()