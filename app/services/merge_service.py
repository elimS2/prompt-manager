"""
Service for merging multiple prompts with different strategies.
Implements various merge patterns and maintains merge history.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models import Prompt
from app.repositories import PromptRepository


class MergeService:
    """Service for merging prompts with various strategies."""
    
    # Default separators for different merge strategies
    DEFAULT_SEPARATOR = "\n\n---\n\n"
    DEFAULT_BULLET = "• "
    DEFAULT_NUMBER_FORMAT = "{}. "
    
    def __init__(self, prompt_repo: Optional[PromptRepository] = None):
        """
        Initialize MergeService with repository.
        
        Args:
            prompt_repo: PromptRepository instance (optional)
        """
        self.prompt_repo = prompt_repo or PromptRepository()
        self._merge_history: List[Dict[str, Any]] = []
    
    def merge_prompts(self, prompt_ids: List[int], strategy: str = 'simple',
                     options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Merge multiple prompts using specified strategy.
        
        Args:
            prompt_ids: List of prompt IDs to merge
            strategy: Merge strategy - 'simple', 'separator', 'numbered', 'bulleted', 'template'
            options: Strategy-specific options:
                - separator: str (for 'separator' strategy)
                - template: str (for 'template' strategy)
                - include_title: bool (default True)
                - include_description: bool (default False)
                
        Returns:
            Dictionary with:
                - merged_content: str - The merged result
                - metadata: Dict - Information about the merge
                
        Raises:
            ValueError: If validation fails
        """
        # Validate inputs
        if not prompt_ids:
            raise ValueError("No prompt IDs provided")
        
        if len(prompt_ids) < 2:
            raise ValueError("At least 2 prompts required for merging")
        
        # Get prompts
        prompts = self.prompt_repo.get_by_ids(prompt_ids)
        
        if len(prompts) != len(prompt_ids):
            found_ids = {p.id for p in prompts}
            missing_ids = set(prompt_ids) - found_ids
            raise ValueError(f"Prompts not found: {missing_ids}")
        
        # Sort prompts by the order of IDs provided
        id_order = {id: i for i, id in enumerate(prompt_ids)}
        prompts.sort(key=lambda p: id_order[p.id])
        
        # Set default options
        options = options or {}
        
        # Apply merge strategy
        if strategy == 'simple':
            merged_content = self.simple_concatenation(prompts, options)
        elif strategy == 'separator':
            separator = options.get('separator', self.DEFAULT_SEPARATOR)
            merged_content = self.with_separators(prompts, separator, options)
        elif strategy == 'numbered':
            merged_content = self.numbered_merge(prompts, options)
        elif strategy == 'bulleted':
            merged_content = self.bulleted_merge(prompts, options)
        elif strategy == 'template':
            template = options.get('template')
            if not template:
                raise ValueError("Template is required for template strategy")
            merged_content = self.structured_merge(prompts, template, options)
        else:
            raise ValueError(f"Unknown merge strategy: {strategy}")
        
        # Create metadata
        metadata = {
            'strategy': strategy,
            'prompt_count': len(prompts),
            'prompt_ids': prompt_ids,
            'prompt_titles': [p.title for p in prompts],
            'merged_at': datetime.utcnow().isoformat(),
            'options': options
        }
        
        # Record in history
        self._record_merge(prompts, merged_content, metadata)
        
        return {
            'merged_content': merged_content,
            'metadata': metadata
        }
    
    def simple_concatenation(self, prompts: List[Prompt], 
                           options: Optional[Dict[str, Any]] = None) -> str:
        """
        Simple concatenation of prompt contents.
        
        Args:
            prompts: List of prompts to merge
            options: Merge options
            
        Returns:
            Concatenated content
        """
        options = options or {}
        include_title = options.get('include_title', True)
        
        parts = []
        for prompt in prompts:
            if include_title:
                parts.append(f"## {prompt.title}\n\n{prompt.content}")
            else:
                parts.append(prompt.content)
        
        return "\n\n".join(parts)
    
    def with_separators(self, prompts: List[Prompt], separator: str,
                       options: Optional[Dict[str, Any]] = None) -> str:
        """
        Merge prompts with custom separators.
        
        Args:
            prompts: List of prompts to merge
            separator: Separator string
            options: Merge options
            
        Returns:
            Content merged with separators
        """
        options = options or {}
        include_title = options.get('include_title', True)
        include_description = options.get('include_description', False)
        
        parts = []
        for prompt in prompts:
            prompt_parts = []
            
            if include_title:
                prompt_parts.append(f"## {prompt.title}")
            
            if include_description and prompt.description:
                prompt_parts.append(f"*{prompt.description}*")
            
            prompt_parts.append(prompt.content)
            
            parts.append("\n\n".join(prompt_parts))
        
        return separator.join(parts)
    
    def numbered_merge(self, prompts: List[Prompt],
                      options: Optional[Dict[str, Any]] = None) -> str:
        """
        Merge prompts with numbered format.
        
        Args:
            prompts: List of prompts to merge
            options: Merge options
            
        Returns:
            Numbered merged content
        """
        options = options or {}
        include_title = options.get('include_title', True)
        number_format = options.get('number_format', self.DEFAULT_NUMBER_FORMAT)
        
        parts = []
        for i, prompt in enumerate(prompts, 1):
            if include_title:
                parts.append(f"{number_format.format(i)} **{prompt.title}**\n\n{prompt.content}")
            else:
                parts.append(f"{number_format.format(i)} {prompt.content}")
        
        return "\n\n".join(parts)
    
    def bulleted_merge(self, prompts: List[Prompt],
                      options: Optional[Dict[str, Any]] = None) -> str:
        """
        Merge prompts with bullet points.
        
        Args:
            prompts: List of prompts to merge
            options: Merge options
            
        Returns:
            Bulleted merged content
        """
        options = options or {}
        include_title = options.get('include_title', True)
        bullet = options.get('bullet', self.DEFAULT_BULLET)
        
        parts = []
        for prompt in prompts:
            if include_title:
                parts.append(f"{bullet}**{prompt.title}**\n  {prompt.content.replace(chr(10), chr(10) + '  ')}")
            else:
                parts.append(f"{bullet}{prompt.content.replace(chr(10), chr(10) + '  ')}")
        
        return "\n\n".join(parts)
    
    def structured_merge(self, prompts: List[Prompt], template: str,
                        options: Optional[Dict[str, Any]] = None) -> str:
        """
        Merge prompts using a custom template.
        
        Template variables:
            - {prompts} - All prompt contents
            - {prompt_1}, {prompt_2}, etc. - Individual prompts
            - {title_1}, {title_2}, etc. - Individual titles
            - {content_1}, {content_2}, etc. - Individual contents
            - {description_1}, {description_2}, etc. - Individual descriptions
            - {count} - Number of prompts
            - {titles} - All titles as comma-separated list
            
        Args:
            prompts: List of prompts to merge
            template: Template string with placeholders
            options: Merge options
            
        Returns:
            Merged content based on template
        """
        # Validate template
        if not template:
            raise ValueError("Template cannot be empty")
        
        # Prepare template variables
        variables = {
            'count': str(len(prompts)),
            'titles': ', '.join(p.title for p in prompts),
            'prompts': '\n\n'.join(p.content for p in prompts)
        }
        
        # Add individual prompt variables
        for i, prompt in enumerate(prompts, 1):
            variables[f'prompt_{i}'] = f"{prompt.title}\n\n{prompt.content}"
            variables[f'title_{i}'] = prompt.title
            variables[f'content_{i}'] = prompt.content
            variables[f'description_{i}'] = prompt.description or ""
        
        # Replace variables in template
        result = template
        for key, value in variables.items():
            result = result.replace(f"{{{key}}}", value)
        
        return result
    
    def validate_merge(self, prompt_ids: List[int]) -> Dict[str, Any]:
        """
        Validate if prompts can be merged.
        
        Args:
            prompt_ids: List of prompt IDs
            
        Returns:
            Dictionary with validation results:
                - valid: bool
                - errors: List[str]
                - warnings: List[str]
        """
        errors = []
        warnings = []
        
        # Check minimum count
        if len(prompt_ids) < 2:
            errors.append("At least 2 prompts required for merging")
        
        # Check for duplicates
        if len(set(prompt_ids)) != len(prompt_ids):
            errors.append("Duplicate prompt IDs found")
        
        # Check if prompts exist
        prompts = self.prompt_repo.get_by_ids(prompt_ids)
        if len(prompts) != len(prompt_ids):
            found_ids = {p.id for p in prompts}
            missing_ids = set(prompt_ids) - found_ids
            errors.append(f"Prompts not found: {missing_ids}")
        
        # Check for inactive prompts
        inactive_prompts = [p for p in prompts if not p.is_active]
        if inactive_prompts:
            warnings.append(f"{len(inactive_prompts)} inactive prompt(s) included")
        
        # Check content size
        total_size = sum(len(p.content) for p in prompts)
        if total_size > 50000:  # 50KB warning threshold
            warnings.append(f"Large merged content size: {total_size} characters")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def _record_merge(self, prompts: List[Prompt], merged_content: str,
                     metadata: Dict[str, Any]) -> None:
        """
        Record merge operation in history.
        
        Args:
            prompts: List of merged prompts
            merged_content: Result of merge
            metadata: Merge metadata
        """
        history_entry = {
            'timestamp': datetime.utcnow(),
            'prompt_ids': [p.id for p in prompts],
            'prompt_titles': [p.title for p in prompts],
            'content_length': len(merged_content),
            'metadata': metadata
        }
        
        self._merge_history.append(history_entry)
        
        # Keep only last 100 entries
        if len(self._merge_history) > 100:
            self._merge_history = self._merge_history[-100:]
    
    def get_merge_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent merge history.
        
        Args:
            limit: Maximum number of entries
            
        Returns:
            List of merge history entries
        """
        return self._merge_history[-limit:][::-1]  # Return in reverse chronological order