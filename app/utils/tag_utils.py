"""
Utility functions for tag processing and normalization.
"""
from typing import List, Set
import re


def normalize_tag_name(tag_name: str) -> str:
    """
    Normalize a tag name by removing extra spaces and converting to lowercase.
    
    Args:
        tag_name: Raw tag name
        
    Returns:
        Normalized tag name
    """
    if not tag_name:
        return ""
    
    # Remove extra spaces and convert to lowercase
    normalized = re.sub(r'\s+', ' ', tag_name.strip().lower())
    
    # Remove special characters except hyphens and underscores
    normalized = re.sub(r'[^\w\s-]', '', normalized)
    
    # Replace spaces with hyphens
    normalized = re.sub(r'\s+', '-', normalized)
    
    return normalized


def parse_tag_string(tag_string: str) -> List[str]:
    """
    Parse a comma-separated tag string into a list of normalized tag names.
    
    Args:
        tag_string: Comma-separated tag string
        
    Returns:
        List of normalized tag names
    """
    if not tag_string:
        return []
    
    # Split by comma and clean up
    raw_tags = [tag.strip() for tag in tag_string.split(',') if tag.strip()]
    
    # Normalize and remove duplicates
    normalized_tags = []
    seen_tags: Set[str] = set()
    
    for tag in raw_tags:
        normalized = normalize_tag_name(tag)
        if normalized and normalized not in seen_tags:
            normalized_tags.append(normalized)
            seen_tags.add(normalized)
    
    return normalized_tags


def format_tags_for_display(tags: List[str]) -> str:
    """
    Format a list of tag names for display in forms.
    
    Args:
        tags: List of tag names
        
    Returns:
        Comma-separated string of tag names
    """
    return ', '.join(tags) if tags else ""


def validate_tag_name(tag_name: str) -> bool:
    """
    Validate if a tag name is acceptable.
    
    Args:
        tag_name: Tag name to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not tag_name:
        return False
    
    normalized = normalize_tag_name(tag_name)
    
    # Check length (1-50 characters)
    if len(normalized) < 1 or len(normalized) > 50:
        return False
    
    # Check if it contains only valid characters
    if not re.match(r'^[a-z0-9-]+$', normalized):
        return False
    
    return True


def suggest_similar_tags(tag_name: str, existing_tags: List[str], max_suggestions: int = 5) -> List[str]:
    """
    Suggest similar tags based on existing tags.
    
    Args:
        tag_name: Tag name to find suggestions for
        existing_tags: List of existing tag names
        max_suggestions: Maximum number of suggestions to return
        
    Returns:
        List of suggested tag names
    """
    if not tag_name or not existing_tags:
        return []
    
    normalized_input = normalize_tag_name(tag_name)
    suggestions = []
    
    for existing_tag in existing_tags:
        normalized_existing = normalize_tag_name(existing_tag)
        
        # Check if input is contained in existing tag or vice versa
        if (normalized_input in normalized_existing or 
            normalized_existing in normalized_input):
            suggestions.append(existing_tag)
        
        # Check for similar prefixes
        elif (normalized_input.startswith(normalized_existing[:3]) or 
              normalized_existing.startswith(normalized_input[:3])):
            suggestions.append(existing_tag)
    
    # Remove duplicates and limit results
    unique_suggestions = list(dict.fromkeys(suggestions))
    return unique_suggestions[:max_suggestions] 