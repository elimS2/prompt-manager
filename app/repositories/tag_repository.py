"""
Repository for Tag model with specific query methods.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import func
from app.models import Tag, Prompt, prompt_tags
from .base import BaseRepository


class TagRepository(BaseRepository[Tag]):
    """Repository for managing Tag data access."""
    
    def __init__(self):
        """Initialize TagRepository."""
        super().__init__(Tag)
    
    def get_by_name(self, name: str) -> Optional[Tag]:
        """
        Get tag by name (case-insensitive).
        
        Args:
            name: Tag name
            
        Returns:
            Tag instance or None
        """
        normalized_name = Tag.normalize_name(name)
        return self.model.query.filter_by(name=normalized_name).first()
    
    def get_or_create(self, name: str, color: Optional[str] = None) -> Tag:
        """
        Get existing tag or create new one.
        
        Args:
            name: Tag name
            color: Optional hex color for new tag
            
        Returns:
            Tag instance
        """
        tag = self.get_by_name(name)
        if not tag:
            normalized_name = Tag.normalize_name(name)
            tag = self.create(name=normalized_name, color=color or '#3B82F6')
        return tag
    
    def get_popular_tags(self, limit: int = 10, is_active: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        Get most popular tags by usage count, optionally filtered by prompt status.
        
        Args:
            limit: Maximum number of tags to return
            is_active: Filter by prompt status (True=Active, False=Inactive, None=All)
            
        Returns:
            List of dictionaries with tag info and usage count
        """
        # Base query to get tags with their usage count
        query = (
            self.session.query(
                Tag,
                func.count(prompt_tags.c.prompt_id).label('usage_count')
            )
            .outerjoin(prompt_tags, Tag.id == prompt_tags.c.tag_id)
        )
        
        # Apply status filter if specified
        if is_active is not None:
            from app.models import Prompt
            query = (
                query
                .join(Prompt, prompt_tags.c.prompt_id == Prompt.id)
                .filter(Prompt.is_active == is_active)
            )
        
        # Complete the query with grouping, ordering, and limit
        results = (
            query
            .group_by(Tag.id)
            .order_by(func.count(prompt_tags.c.prompt_id).desc())
            .limit(limit)
            .all()
        )
        
        return [
            {
                'tag': tag,
                'usage_count': count
            }
            for tag, count in results
        ]
    
    def get_unused_tags(self) -> List[Tag]:
        """
        Get tags that are not associated with any prompts.
        
        Returns:
            List of unused tags
        """
        # Subquery to find tags with no associations
        used_tag_ids = (
            self.session.query(prompt_tags.c.tag_id)
            .distinct()
            .subquery()
        )
        
        return (
            self.model.query
            .filter(~self.model.id.in_(used_tag_ids))
            .all()
        )
    
    def get_tags_for_prompt(self, prompt_id: int) -> List[Tag]:
        """
        Get all tags for a specific prompt.
        
        Args:
            prompt_id: Prompt ID
            
        Returns:
            List of tags
        """
        return (
            self.model.query
            .join(prompt_tags)
            .filter(prompt_tags.c.prompt_id == prompt_id)
            .all()
        )
    
    def search_tags(self, query: str) -> List[Tag]:
        """
        Search tags by name.
        
        Args:
            query: Search query
            
        Returns:
            List of matching tags
        """
        if not query:
            return []
        
        search_term = f'%{query}%'
        return self.model.query.filter(self.model.name.ilike(search_term)).all()
    
    def get_tag_statistics(self) -> Dict[str, Any]:
        """
        Get overall tag statistics.
        
        Returns:
            Dictionary with statistics
        """
        total_tags = self.count()
        
        # Get usage statistics
        usage_stats = (
            self.session.query(
                func.count(prompt_tags.c.tag_id).label('prompt_count')
            )
            .select_from(prompt_tags)
            .group_by(prompt_tags.c.tag_id)
            .all()
        )
        
        usage_counts = [count for (count,) in usage_stats]
        
        return {
            'total_tags': total_tags,
            'used_tags': len(usage_counts),
            'unused_tags': total_tags - len(usage_counts),
            'avg_prompts_per_tag': sum(usage_counts) / len(usage_counts) if usage_counts else 0,
            'max_prompts_per_tag': max(usage_counts) if usage_counts else 0,
            'min_prompts_per_tag': min(usage_counts) if usage_counts else 0
        }
    
    def bulk_get_or_create(self, tag_names: List[str], default_color: str = '#3B82F6') -> List[Tag]:
        """
        Get or create multiple tags efficiently.
        
        Args:
            tag_names: List of tag names
            default_color: Default color for new tags
            
        Returns:
            List of Tag instances
        """
        if not tag_names:
            return []
        
        # Normalize all names
        normalized_names = [Tag.normalize_name(name) for name in tag_names]
        
        # Get existing tags
        existing_tags = self.model.query.filter(self.model.name.in_(normalized_names)).all()
        existing_names = {tag.name for tag in existing_tags}
        
        # Create new tags for names that don't exist
        new_tags = []
        for name in normalized_names:
            if name not in existing_names and name:  # Skip empty names
                new_tags.append({'name': name, 'color': default_color})
        
        if new_tags:
            created_tags = self.bulk_create(new_tags)
            existing_tags.extend(created_tags)
        
        return existing_tags
    
    def merge_tags(self, source_tag_id: int, target_tag_id: int) -> bool:
        """
        Merge source tag into target tag.
        All prompts associated with source tag will be associated with target tag.
        
        Args:
            source_tag_id: ID of tag to be merged
            target_tag_id: ID of tag to merge into
            
        Returns:
            True if successful
        """
        if source_tag_id == target_tag_id:
            return False
        
        source_tag = self.get_by_id(source_tag_id)
        target_tag = self.get_by_id(target_tag_id)
        
        if not source_tag or not target_tag:
            return False
        
        # Update all prompt associations
        self.session.execute(
            prompt_tags.update()
            .where(prompt_tags.c.tag_id == source_tag_id)
            .values(tag_id=target_tag_id)
        )
        
        # Delete the source tag
        self.delete(source_tag_id)
        
        return True
    
    def rename_tag(self, tag_id: int, new_name: str) -> Optional[Tag]:
        """
        Rename a tag with normalization.
        
        Args:
            tag_id: Tag ID
            new_name: New tag name
            
        Returns:
            Updated tag or None
        """
        tag = self.get_by_id(tag_id)
        if not tag:
            return None
        
        normalized_name = Tag.normalize_name(new_name)
        
        # Check if normalized name already exists
        existing = self.get_by_name(normalized_name)
        if existing and existing.id != tag_id:
            raise ValueError(f"Tag '{normalized_name}' already exists")
        
        tag.name = normalized_name
        self.commit()
        return tag