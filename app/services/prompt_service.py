"""
Service layer for Prompt business logic.
Implements business rules and orchestrates data access through repositories.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.repositories import PromptRepository, TagRepository, AttachedPromptRepository
from app.models import Prompt, Tag
from app.utils.tag_utils import parse_tag_string, validate_tag_name


class PromptService:
    """Service for managing prompts with business logic."""
    
    def __init__(self, prompt_repo: Optional[PromptRepository] = None, 
                 tag_repo: Optional[TagRepository] = None,
                 attached_prompt_repo: Optional[AttachedPromptRepository] = None):
        """
        Initialize PromptService with repositories.
        
        Args:
            prompt_repo: PromptRepository instance (optional)
            tag_repo: TagRepository instance (optional)
            attached_prompt_repo: AttachedPromptRepository instance (optional)
        """
        self.prompt_repo = prompt_repo or PromptRepository()
        self.tag_repo = tag_repo or TagRepository()
        self.attached_prompt_repo = attached_prompt_repo or AttachedPromptRepository()
    
    def create_prompt(self, data: Dict[str, Any]) -> Prompt:
        """
        Create a new prompt with validation and tag processing.
        
        Args:
            data: Dictionary containing:
                - title: str (required)
                - content: str (required)
                - description: str (optional)
                - tags: List[str] (optional) - tag names
                - is_active: bool (optional, default True)
                
        Returns:
            Created Prompt instance
            
        Raises:
            ValueError: If validation fails
        """
        try:
            # Extract and validate required fields
            title = data.get('title', '').strip()
            content = data.get('content', '').strip()
            
            if not title:
                raise ValueError("Title is required")
            if not content:
                raise ValueError("Content is required")
            if len(title) > 255:
                raise ValueError("Title must be less than 255 characters")
            
            # Extract optional fields
            description = data.get('description', '').strip()
            is_active = data.get('is_active', True)
            tag_names = data.get('tags', [])
            
            # Handle checkbox value for is_active
            if isinstance(is_active, str):
                is_active = is_active.lower() in ('true', '1', 'on', 'yes')
            
            # Create prompt
            prompt = self.prompt_repo.create(
                title=title,
                content=content,
                description=description,
                is_active=is_active
            )
            
            # Process tags if provided
            if tag_names:
                self._add_tags_to_prompt(prompt, tag_names)
            
            return prompt
            
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in create_prompt: {str(e)}", exc_info=True)
            raise
    
    def update_prompt(self, id: int, data: Dict[str, Any]) -> Prompt:
        """
        Update an existing prompt with validation.
        
        Args:
            id: Prompt ID
            data: Dictionary with fields to update:
                - title: str (optional)
                - content: str (optional)
                - description: str (optional)
                - tags: List[str] (optional) - replaces all tags
                - is_active: bool (optional)
                
        Returns:
            Updated Prompt instance
            
        Raises:
            ValueError: If validation fails or prompt not found
        """
        # Get existing prompt
        prompt = self.prompt_repo.get_by_id(id)
        if not prompt:
            raise ValueError(f"Prompt with id {id} not found")
        
        # Validate fields if provided
        if 'title' in data:
            title = data['title'].strip()
            if not title:
                raise ValueError("Title cannot be empty")
            if len(title) > 255:
                raise ValueError("Title must be less than 255 characters")
            data['title'] = title
        
        if 'content' in data:
            content = data['content'].strip()
            if not content:
                raise ValueError("Content cannot be empty")
            data['content'] = content
        
        if 'description' in data:
            data['description'] = data['description'].strip()
        
        # Handle boolean conversion for is_active
        if 'is_active' in data:
            is_active = data['is_active']
            if isinstance(is_active, str):
                data['is_active'] = is_active.lower() in ('true', '1', 'on', 'yes')
        
        # Handle tags separately
        tag_names = data.pop('tags', None)
        
        # Update prompt fields
        updated_fields = {k: v for k, v in data.items() 
                         if k in ['title', 'content', 'description', 'is_active']}
        
        if updated_fields:
            prompt = self.prompt_repo.update(id, **updated_fields)
        
        # Update tags if provided
        if tag_names is not None:
            self._update_prompt_tags(prompt, tag_names)
        
        return prompt
    
    def delete_prompt(self, id: int, soft: bool = True) -> bool:
        """
        Delete a prompt (soft delete by default).
        
        Args:
            id: Prompt ID
            soft: If True, perform soft delete; if False, hard delete
            
        Returns:
            True if deleted, False if not found
        """
        if soft:
            return self.prompt_repo.soft_delete(id)
        else:
            return self.prompt_repo.delete(id)
    
    def restore_prompt(self, id: int) -> bool:
        """
        Restore a soft-deleted prompt.
        
        Args:
            id: Prompt ID
            
        Returns:
            True if restored, False if not found
        """
        return self.prompt_repo.restore(id)
    
    def archive_prompt(self, id: int) -> bool:
        """
        Archive a prompt (set is_active to False).
        
        Args:
            id: Prompt ID
            
        Returns:
            True if archived, False if not found
        """
        return self.prompt_repo.soft_delete(id)
    
    def get_prompt(self, id: int) -> Optional[Prompt]:
        """
        Get a single prompt by ID.
        
        Args:
            id: Prompt ID
            
        Returns:
            Prompt instance or None
        """
        return self.prompt_repo.get_by_id(id)
    
    def get_prompts_by_filters(self, filters: Dict[str, Any]) -> List[Prompt]:
        """
        Get prompts with complex filtering.
        
        Args:
            filters: Dictionary of filter criteria:
                - search: str - Search in title/content/description
                - tags: List[str] - Tag names to filter by
                - tag_ids: List[int] - Tag IDs to filter by
                - tag_match_all: bool - If True, match ALL tags; else match ANY
                - is_active: bool - Filter by active status
                - created_after: datetime - Filter by creation date
                - created_before: datetime - Filter by creation date
                - sort_by: str - 'created', 'updated', 'title', 'order'
                - sort_order: str - 'asc' or 'desc'
                - page: int - Page number for pagination
                - per_page: int - Items per page
                - include_attachments: bool - Whether to include attached prompts
                
        Returns:
            List of Prompt instances or paginated result dict
        """
        # Extract sorting parameters (not model fields)
        sort_by = filters.pop('sort_by', 'order')  # Default to order for drag & drop
        sort_order = filters.pop('sort_order', 'asc')  # Default to ascending order
        
        # Handle tag filtering by names
        if 'tags' in filters and filters['tags']:
            tag_names = filters.pop('tags')
            match_all = filters.pop('tag_match_all', False)
            is_active = filters.get('is_active')  # Get is_active before popping tags
            prompts = self.prompt_repo.get_by_tag_names(tag_names, match_all, is_active)
            
            # Apply additional filters to tag-filtered results
            if filters:
                prompt_ids = [p.id for p in prompts]
                filters['ids'] = prompt_ids
        
        # Handle tag filtering by IDs
        elif 'tag_ids' in filters and filters['tag_ids']:
            tag_ids = filters.pop('tag_ids')
            match_all = filters.pop('tag_match_all', False)
            is_active = filters.get('is_active')  # Get is_active before popping tags
            prompts = self.prompt_repo.get_by_tags(tag_ids, match_all, is_active)
            
            # Apply additional filters
            if filters:
                prompt_ids = [p.id for p in prompts]
                filters['ids'] = prompt_ids
        
        # Check if we should include attachments
        include_attachments = filters.pop('include_attachments', False)
        
        # Handle pagination
        if 'page' in filters:
            page = filters.pop('page', 1)
            per_page = filters.pop('per_page', 20)
            result = self.prompt_repo.get_paginated_with_sorting(
                page=page, 
                per_page=per_page, 
                sort_by=sort_by, 
                sort_order=sort_order, 
                **filters
            )
            
            # Load attachments if requested
            if include_attachments and isinstance(result, dict) and 'items' in result:
                for prompt in result['items']:
                    self._load_attached_prompts(prompt)
            
            return result
        
        # Get filtered results with sorting
        prompts = self.prompt_repo.get_with_filters_and_sorting(filters, sort_by, sort_order)
        
        # Load attachments if requested
        if include_attachments:
            for prompt in prompts:
                self._load_attached_prompts(prompt)
        
        return prompts
    
    def _load_attached_prompts(self, prompt: Prompt) -> None:
        """
        Load attached prompts for a given prompt.
        
        Args:
            prompt: Prompt instance to load attachments for
        """
        if not hasattr(prompt, '_attached_prompts_loaded') or not prompt._attached_prompts_loaded:
            # Get actual AttachedPrompt objects, not dictionaries
            attached_prompts = self.attached_prompt_repo.get_attached_prompts(prompt.id)
            # Store the data in a custom attribute to avoid SQLAlchemy relationship issues
            prompt._attached_prompts_data = attached_prompts
            prompt._attached_prompts_loaded = True
    
    def search_prompts(self, query: str, include_inactive: bool = False) -> List[Prompt]:
        """
        Search prompts by text query.
        
        Args:
            query: Search query
            include_inactive: Whether to include inactive prompts
            
        Returns:
            List of matching prompts
        """
        return self.prompt_repo.search(query, include_inactive)
    
    def get_recent_prompts(self, limit: int = 10) -> List[Prompt]:
        """
        Get most recently created prompts.
        
        Args:
            limit: Maximum number of prompts
            
        Returns:
            List of recent prompts
        """
        return self.prompt_repo.get_recent(limit)
    
    def duplicate_prompt(self, id: int, new_title: Optional[str] = None) -> Prompt:
        """
        Create a copy of an existing prompt.
        
        Args:
            id: ID of prompt to duplicate
            new_title: Optional new title (defaults to "Copy of [original]")
            
        Returns:
            New Prompt instance
            
        Raises:
            ValueError: If prompt not found
        """
        original = self.get_prompt(id)
        if not original:
            raise ValueError(f"Prompt with id {id} not found")
        
        # Create duplicate data
        duplicate_data = {
            'title': new_title or f"Copy of {original.title}",
            'content': original.content,
            'description': original.description,
            'tags': [tag.name for tag in original.tags],
            'is_active': True
        }
        
        return self.create_prompt(duplicate_data)
    
    def _add_tags_to_prompt(self, prompt: Prompt, tag_names: List[str]) -> None:
        """
        Add tags to a prompt (internal method).
        
        Args:
            prompt: Prompt instance
            tag_names: List of tag names
        """
        try:
            if not tag_names:
                return
            
            # Validate and filter tag names
            valid_tag_names = []
            for tag_name in tag_names:
                if validate_tag_name(tag_name):
                    valid_tag_names.append(tag_name)
                else:
                    # Log invalid tag names for debugging
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Invalid tag name skipped: {tag_name}")
            
            if not valid_tag_names:
                return
            
            # Get or create tags
            tags = self.tag_repo.bulk_get_or_create(valid_tag_names)
            
            # Add tags to prompt
            for tag in tags:
                if tag not in prompt.tags:
                    prompt.tags.append(tag)
            
            self.prompt_repo.commit()
            
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error adding tags to prompt: {str(e)}", exc_info=True)
            # Don't fail the entire prompt creation if tag addition fails
            pass
    
    def _update_prompt_tags(self, prompt: Prompt, tag_names: List[str]) -> None:
        """
        Update prompt tags (replaces all existing tags).
        
        Args:
            prompt: Prompt instance
            tag_names: List of tag names
        """
        # Clear existing tags
        prompt.tags.clear()
        
        # Add new tags
        if tag_names:
            self._add_tags_to_prompt(prompt, tag_names)
        else:
            self.prompt_repo.commit()
    
    def get_prompt_statistics(self) -> Dict[str, Any]:
        """
        Get overall prompt statistics.
        
        Returns:
            Dictionary with statistics
        """
        total = self.prompt_repo.count()
        active = self.prompt_repo.count(is_active=True)
        inactive = total - active
        
        return {
            'total_prompts': total,
            'active_prompts': active,
            'inactive_prompts': inactive,
            'active_percentage': (active / total * 100) if total > 0 else 0
        }
    
    def update_prompt_order(self, prompt_id: int, new_order: int) -> bool:
        """
        Update the order of a single prompt.
        
        Args:
            prompt_id: ID of the prompt to update
            new_order: New order value
            
        Returns:
            True if successful, False otherwise
        """
        return self.prompt_repo.update_order(prompt_id, new_order)
    
    def reorder_prompts(self, ordered_ids: List[int]) -> bool:
        """
        Reorder multiple prompts based on a list of IDs in the desired order.
        
        Args:
            ordered_ids: List of prompt IDs in the desired order
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create order mapping: ID -> new order (position in list)
            order_mapping = {prompt_id: index for index, prompt_id in enumerate(ordered_ids)}
            return self.prompt_repo.bulk_update_order(order_mapping)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error reordering prompts: {str(e)}")
            return False
    
    def get_prompt_with_attachments(self, prompt_id: int) -> Optional[Prompt]:
        """
        Get a prompt with its attached prompts loaded.
        
        Args:
            prompt_id: ID of the prompt to retrieve
            
        Returns:
            Prompt instance with attached prompts loaded, or None if not found
        """
        return self.prompt_repo.get_with_attached_prompts(prompt_id)
    
    def get_prompts_with_attachments(self, include_inactive: bool = False) -> List[Prompt]:
        """
        Get all prompts that have attached prompts.
        
        Args:
            include_inactive: Whether to include inactive prompts
            
        Returns:
            List of prompts that have attached prompts
        """
        return self.prompt_repo.get_prompts_with_attachments(include_inactive)
    
    def get_prompts_with_attachments_loaded(self, include_inactive: bool = False) -> List[Prompt]:
        """
        Get all prompts with their attached prompts pre-loaded.
        
        Args:
            include_inactive: Whether to include inactive prompts
            
        Returns:
            List of prompts with attached_prompts relationship loaded
        """
        return self.prompt_repo.get_prompts_with_attachments_loaded(include_inactive)
    
    def get_available_for_attachment(self, main_prompt_id: int, exclude_ids: Optional[List[int]] = None) -> List[Prompt]:
        """
        Get prompts that can be attached to a specific prompt.
        
        Args:
            main_prompt_id: ID of the main prompt
            exclude_ids: List of prompt IDs to exclude
            
        Returns:
            List of prompts available for attachment
        """
        return self.prompt_repo.get_available_for_attachment(main_prompt_id, exclude_ids)
    
    def get_attached_prompts_for_prompt(self, prompt_id: int) -> List[Dict[str, Any]]:
        """
        Get attached prompts with full details for a specific prompt.
        
        Args:
            prompt_id: ID of the prompt
            
        Returns:
            List of dictionaries with attached prompt details
        """
        return self.attached_prompt_repo.get_attached_prompts_with_details(prompt_id)
    
    def get_attachment_count(self, prompt_id: int) -> int:
        """
        Get the number of prompts attached to a specific prompt.
        
        Args:
            prompt_id: ID of the prompt
            
        Returns:
            Number of attached prompts
        """
        return self.attached_prompt_repo.get_attachment_count(prompt_id)
    
    def get_prompt_attachment_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about prompt attachments.
        
        Returns:
            Dictionary with attachment statistics
        """
        total_attachments = self.attached_prompt_repo.count()
        prompts_with_attachments = len(self.get_prompts_with_attachments())
        total_prompts = self.prompt_repo.count(is_active=True)
        
        return {
            'total_attachments': total_attachments,
            'prompts_with_attachments': prompts_with_attachments,
            'total_active_prompts': total_prompts,
            'attachment_coverage': (prompts_with_attachments / total_prompts * 100) if total_prompts > 0 else 0
        }