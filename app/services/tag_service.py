"""
Service layer for Tag business logic.
Manages tag operations and provides tag-related functionality.
"""
from typing import List, Dict, Any, Optional
from app.repositories import TagRepository, PromptRepository
from app.models import Tag


class TagService:
    """Service for managing tags with business logic."""
    
    def __init__(self, tag_repo: Optional[TagRepository] = None,
                 prompt_repo: Optional[PromptRepository] = None):
        """
        Initialize TagService with repositories.
        
        Args:
            tag_repo: TagRepository instance (optional)
            prompt_repo: PromptRepository instance (optional)
        """
        self.tag_repo = tag_repo or TagRepository()
        self.prompt_repo = prompt_repo or PromptRepository()
    
    def create_tag(self, name: str, color: Optional[str] = None) -> Tag:
        """
        Create a new tag with validation.
        
        Args:
            name: Tag name
            color: Optional hex color (e.g., '#FF5733')
            
        Returns:
            Created Tag instance
            
        Raises:
            ValueError: If validation fails
        """
        # Validate name
        if not name or not name.strip():
            raise ValueError("Tag name is required")
        
        # Normalize name
        normalized_name = Tag.normalize_name(name)
        if not normalized_name:
            raise ValueError("Invalid tag name")
        
        # Check if already exists
        existing = self.tag_repo.get_by_name(normalized_name)
        if existing:
            raise ValueError(f"Tag '{normalized_name}' already exists")
        
        # Validate color if provided
        if color:
            if not self._is_valid_hex_color(color):
                raise ValueError("Invalid color format. Use hex format: #RRGGBB")
        
        # Create tag
        return self.tag_repo.create(name=normalized_name, color=color)
    
    def update_tag(self, id: int, name: Optional[str] = None, 
                   color: Optional[str] = None) -> Tag:
        """
        Update an existing tag.
        
        Args:
            id: Tag ID
            name: New name (optional)
            color: New color (optional)
            
        Returns:
            Updated Tag instance
            
        Raises:
            ValueError: If validation fails or tag not found
        """
        # Get existing tag
        tag = self.tag_repo.get_by_id(id)
        if not tag:
            raise ValueError(f"Tag with id {id} not found")
        
        updates = {}
        
        # Validate and normalize name if provided
        if name is not None:
            normalized_name = Tag.normalize_name(name)
            if not normalized_name:
                raise ValueError("Invalid tag name")
            
            # Check for duplicates
            existing = self.tag_repo.get_by_name(normalized_name)
            if existing and existing.id != id:
                raise ValueError(f"Tag '{normalized_name}' already exists")
            
            updates['name'] = normalized_name
        
        # Validate color if provided
        if color is not None:
            if not self._is_valid_hex_color(color):
                raise ValueError("Invalid color format. Use hex format: #RRGGBB")
            updates['color'] = color
        
        # Update tag
        if updates:
            return self.tag_repo.update(id, **updates)
        
        return tag
    
    def delete_tag(self, id: int, reassign_to: Optional[int] = None) -> bool:
        """
        Delete a tag with optional reassignment.
        
        Args:
            id: Tag ID to delete
            reassign_to: Optional tag ID to reassign prompts to
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            ValueError: If reassignment tag not found
        """
        # Check if tag exists
        tag = self.tag_repo.get_by_id(id)
        if not tag:
            return False
        
        # Handle reassignment if specified
        if reassign_to:
            if reassign_to == id:
                raise ValueError("Cannot reassign to the same tag")
            
            target_tag = self.tag_repo.get_by_id(reassign_to)
            if not target_tag:
                raise ValueError(f"Reassignment tag with id {reassign_to} not found")
            
            # Get prompts with this tag
            prompts = self.prompt_repo.get_by_tags([id])
            
            # Add target tag to prompts
            for prompt in prompts:
                if target_tag not in prompt.tags:
                    prompt.tags.append(target_tag)
            
            self.prompt_repo.commit()
        
        # Delete the tag
        return self.tag_repo.delete(id)
    
    def merge_tags(self, source_id: int, target_id: int) -> Tag:
        """
        Merge one tag into another.
        
        Args:
            source_id: ID of tag to be merged
            target_id: ID of tag to merge into
            
        Returns:
            Target tag after merge
            
        Raises:
            ValueError: If validation fails
        """
        if source_id == target_id:
            raise ValueError("Cannot merge tag with itself")
        
        # Verify both tags exist
        source_tag = self.tag_repo.get_by_id(source_id)
        target_tag = self.tag_repo.get_by_id(target_id)
        
        if not source_tag:
            raise ValueError(f"Source tag with id {source_id} not found")
        if not target_tag:
            raise ValueError(f"Target tag with id {target_id} not found")
        
        # Perform merge
        success = self.tag_repo.merge_tags(source_id, target_id)
        if not success:
            raise ValueError("Failed to merge tags")
        
        return target_tag
    
    def get_popular_tags(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most popular tags with usage statistics.
        
        Args:
            limit: Maximum number of tags to return
            
        Returns:
            List of dictionaries with tag info and usage count
        """
        return self.tag_repo.get_popular_tags(limit)
    
    def get_tag_cloud(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get tags for tag cloud visualization.
        
        Args:
            limit: Maximum number of tags
            
        Returns:
            List of tags with normalized weights for visualization
        """
        popular_tags = self.tag_repo.get_popular_tags(limit)
        
        if not popular_tags:
            return []
        
        # Calculate weight range
        max_count = max(item['usage_count'] for item in popular_tags)
        min_count = min(item['usage_count'] for item in popular_tags)
        count_range = max_count - min_count if max_count > min_count else 1
        
        # Normalize weights (1-10 scale)
        tag_cloud = []
        for item in popular_tags:
            tag = item['tag']
            count = item['usage_count']
            
            # Calculate normalized weight
            if count_range > 0:
                weight = 1 + ((count - min_count) / count_range) * 9
            else:
                weight = 5  # Default weight if all counts are equal
            
            tag_cloud.append({
                'id': tag.id,
                'name': tag.name,
                'color': tag.color,
                'usage_count': count,
                'weight': round(weight, 1)
            })
        
        return tag_cloud
    
    def search_tags(self, query: str) -> List[Tag]:
        """
        Search tags by name.
        
        Args:
            query: Search query
            
        Returns:
            List of matching tags
        """
        return self.tag_repo.search_tags(query)
    
    def get_or_create_tags(self, tag_names: List[str]) -> List[Tag]:
        """
        Get existing tags or create new ones for a list of names.
        
        Args:
            tag_names: List of tag names
            
        Returns:
            List of Tag instances
        """
        if not tag_names:
            return []
        
        # Remove duplicates and empty strings
        unique_names = list(set(name.strip() for name in tag_names if name.strip()))
        
        return self.tag_repo.bulk_get_or_create(unique_names)
    
    def cleanup_unused_tags(self) -> int:
        """
        Remove tags that are not associated with any prompts.
        
        Returns:
            Number of tags deleted
        """
        unused_tags = self.tag_repo.get_unused_tags()
        deleted_count = 0
        
        for tag in unused_tags:
            if self.tag_repo.delete(tag.id):
                deleted_count += 1
        
        return deleted_count
    
    def get_tag_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive tag statistics.
        
        Returns:
            Dictionary with various statistics
        """
        stats = self.tag_repo.get_tag_statistics()
        
        # Add additional statistics
        stats['popular_tags'] = [
            {'name': item['tag'].name, 'count': item['usage_count']}
            for item in self.tag_repo.get_popular_tags(5)
        ]
        
        return stats
    
    def suggest_tags(self, content: str, limit: int = 5) -> List[Tag]:
        """
        Suggest tags based on content analysis.
        
        Simple implementation: finds existing tags mentioned in content.
        Can be enhanced with ML/NLP in the future.
        
        Args:
            content: Text content to analyze
            limit: Maximum number of suggestions
            
        Returns:
            List of suggested tags
        """
        if not content:
            return []
        
        content_lower = content.lower()
        all_tags = self.tag_repo.get_all()
        
        # Find tags mentioned in content
        suggested = []
        for tag in all_tags:
            if tag.name in content_lower or tag.name.replace('-', ' ') in content_lower:
                suggested.append(tag)
                if len(suggested) >= limit:
                    break
        
        return suggested
    
    def _is_valid_hex_color(self, color: str) -> bool:
        """
        Validate hex color format.
        
        Args:
            color: Color string
            
        Returns:
            True if valid hex color
        """
        import re
        return bool(re.match(r'^#[0-9A-Fa-f]{6}$', color))