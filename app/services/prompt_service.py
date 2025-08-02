"""
Service layer for Prompt business logic.
Implements business rules and orchestrates data access through repositories.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.repositories import PromptRepository, TagRepository
from app.models import Prompt, Tag


class PromptService:
    """Service for managing prompts with business logic."""
    
    def __init__(self, prompt_repo: Optional[PromptRepository] = None, 
                 tag_repo: Optional[TagRepository] = None):
        """
        Initialize PromptService with repositories.
        
        Args:
            prompt_repo: PromptRepository instance (optional)
            tag_repo: TagRepository instance (optional)
        """
        self.prompt_repo = prompt_repo or PromptRepository()
        self.tag_repo = tag_repo or TagRepository()
    
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
                - sort_by: str - 'created', 'updated', 'title'
                - sort_order: str - 'asc' or 'desc'
                - page: int - Page number for pagination
                - per_page: int - Items per page
                
        Returns:
            List of Prompt instances or paginated result dict
        """
        # Extract sorting parameters (not model fields)
        sort_by = filters.pop('sort_by', 'created')
        sort_order = filters.pop('sort_order', 'desc')
        
        # Handle tag filtering by names
        if 'tags' in filters and filters['tags']:
            tag_names = filters.pop('tags')
            match_all = filters.pop('tag_match_all', False)
            prompts = self.prompt_repo.get_by_tag_names(tag_names, match_all)
            
            # Apply additional filters to tag-filtered results
            if filters:
                prompt_ids = [p.id for p in prompts]
                filters['ids'] = prompt_ids
        
        # Handle tag filtering by IDs
        elif 'tag_ids' in filters and filters['tag_ids']:
            tag_ids = filters.pop('tag_ids')
            match_all = filters.pop('tag_match_all', False)
            prompts = self.prompt_repo.get_by_tags(tag_ids, match_all)
            
            # Apply additional filters
            if filters:
                prompt_ids = [p.id for p in prompts]
                filters['ids'] = prompt_ids
        
        # Handle pagination
        if 'page' in filters:
            page = filters.pop('page', 1)
            per_page = filters.pop('per_page', 20)
            return self.prompt_repo.get_paginated_with_sorting(
                page=page, 
                per_page=per_page, 
                sort_by=sort_by, 
                sort_order=sort_order, 
                **filters
            )
        
        # Get filtered results with sorting
        return self.prompt_repo.get_with_filters_and_sorting(filters, sort_by, sort_order)
    
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
        if not tag_names:
            return
        
        # Get or create tags
        tags = self.tag_repo.bulk_get_or_create(tag_names)
        
        # Add tags to prompt
        for tag in tags:
            if tag not in prompt.tags:
                prompt.tags.append(tag)
        
        self.prompt_repo.commit()
    
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