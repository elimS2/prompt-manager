"""
Service layer for managing attached prompt business logic.
"""
import logging
from typing import List, Dict, Any, Optional
from app.repositories import AttachedPromptRepository, PromptRepository
from app.models import AttachedPrompt, Prompt


logger = logging.getLogger(__name__)


class AttachedPromptService:
    """Service for managing attached prompt business logic."""
    
    def __init__(self, attached_prompt_repo: AttachedPromptRepository, prompt_repo: PromptRepository):
        """
        Initialize AttachedPromptService.
        
        Args:
            attached_prompt_repo: Repository for attached prompt data access
            prompt_repo: Repository for prompt data access
        """
        self.attached_prompt_repo = attached_prompt_repo
        self.prompt_repo = prompt_repo
    
    def attach_prompt(self, main_id: int, attached_id: int) -> AttachedPrompt:
        """
        Attach a prompt to another prompt with full validation.
        
        Args:
            main_id: ID of the main prompt
            attached_id: ID of the prompt to attach
            
        Returns:
            Created AttachedPrompt instance
            
        Raises:
            ValueError: If attachment is invalid (self-attachment, circular, etc.)
            RuntimeError: If prompts don't exist or are inactive
        """
        logger.info(f"Attempting to attach prompt {attached_id} to prompt {main_id}")
        
        # Validate that both prompts exist and are active
        main_prompt = self.prompt_repo.get_by_id(main_id)
        attached_prompt = self.prompt_repo.get_by_id(attached_id)
        
        if not main_prompt:
            raise ValueError(f"Main prompt with ID {main_id} does not exist")
        
        if not attached_prompt:
            raise ValueError(f"Attached prompt with ID {attached_id} does not exist")
        
        if not main_prompt.is_active:
            raise ValueError(f"Main prompt with ID {main_id} is not active")
        
        if not attached_prompt.is_active:
            raise ValueError(f"Attached prompt with ID {attached_id} is not active")
        
        # Prevent self-attachment
        if main_id == attached_id:
            raise ValueError("Cannot attach prompt to itself")
        
        # Check for circular attachments
        if self._would_create_circle(main_id, attached_id):
            raise ValueError("Circular attachment detected - this would create an infinite loop")
        
        # Check if attachment already exists
        if self.attached_prompt_repo.exists(main_id, attached_id):
            raise ValueError(f"Prompt {attached_id} is already attached to prompt {main_id}")
        
        # Check attachment limit (optional - can be configured)
        current_count = self.attached_prompt_repo.get_attachment_count(main_id)
        max_attachments = 10  # Configurable limit
        if current_count >= max_attachments:
            raise ValueError(f"Maximum number of attached prompts ({max_attachments}) reached for prompt {main_id}")
        
        # Get next order value
        next_order = self.attached_prompt_repo.get_max_order(main_id) + 1
        
        try:
            # Create attachment
            attached_prompt = self.attached_prompt_repo.attach_prompt(main_id, attached_id, next_order)
            logger.info(f"Successfully attached prompt {attached_id} to prompt {main_id}")
            return attached_prompt
        except Exception as e:
            logger.error(f"Failed to attach prompt {attached_id} to prompt {main_id}: {str(e)}")
            raise
    
    def detach_prompt(self, main_id: int, attached_id: int) -> bool:
        """
        Detach a prompt from another prompt.
        
        Args:
            main_id: ID of the main prompt
            attached_id: ID of the prompt to detach
            
        Returns:
            True if detachment was successful, False if attachment didn't exist
        """
        logger.info(f"Attempting to detach prompt {attached_id} from prompt {main_id}")
        
        try:
            success = self.attached_prompt_repo.detach_prompt(main_id, attached_id)
            if success:
                logger.info(f"Successfully detached prompt {attached_id} from prompt {main_id}")
            else:
                logger.warning(f"Attachment between prompt {main_id} and {attached_id} not found")
            return success
        except Exception as e:
            logger.error(f"Failed to detach prompt {attached_id} from prompt {main_id}: {str(e)}")
            raise
    
    def reorder_attachments(self, main_id: int, order_data: List[Dict[str, Any]]) -> bool:
        """
        Reorder attached prompts for a main prompt.
        
        Args:
            main_id: ID of the main prompt
            order_data: List of dictionaries with 'attached_prompt_id' and 'order' keys
            
        Returns:
            True if reordering was successful
        """
        logger.info(f"Attempting to reorder attachments for prompt {main_id}")
        
        # Validate that the main prompt exists
        main_prompt = self.prompt_repo.get_by_id(main_id)
        if not main_prompt:
            raise ValueError(f"Main prompt with ID {main_id} does not exist")
        
        # Create order map
        order_map = {}
        for item in order_data:
            attached_id = item.get('attached_prompt_id')
            order = item.get('order')
            
            if attached_id is None or order is None:
                raise ValueError("Each order item must contain 'attached_prompt_id' and 'order'")
            
            order_map[attached_id] = order
        
        try:
            success = self.attached_prompt_repo.reorder_attached_prompts(main_id, order_map)
            if success:
                logger.info(f"Successfully reordered attachments for prompt {main_id}")
            return success
        except Exception as e:
            logger.error(f"Failed to reorder attachments for prompt {main_id}: {str(e)}")
            raise
    
    def get_attached_prompts(self, main_id: int) -> List[Prompt]:
        """
        Get all prompts attached to a main prompt.
        
        Args:
            main_id: ID of the main prompt
            
        Returns:
            List of Prompt instances that are attached to the main prompt
        """
        attached_relationships = self.attached_prompt_repo.get_attached_prompts(main_id)
        attached_prompts = []
        
        for relationship in attached_relationships:
            prompt = self.prompt_repo.get_by_id(relationship.attached_prompt_id)
            if prompt:
                attached_prompts.append(prompt)
        
        return attached_prompts
    
    def get_attached_prompts_with_details(self, main_id: int) -> List[Dict[str, Any]]:
        """
        Get attached prompts with full details including order information.
        
        Args:
            main_id: ID of the main prompt
            
        Returns:
            List of dictionaries with attached prompt details
        """
        return self.attached_prompt_repo.get_attached_prompts_with_details(main_id)
    
    def get_popular_combinations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most frequently used prompt combinations.
        
        Args:
            limit: Maximum number of combinations to return
            
        Returns:
            List of dictionaries with combination statistics
        """
        return self.attached_prompt_repo.get_popular_combinations(limit)
    
    def increment_usage(self, main_id: int, attached_id: int) -> bool:
        """
        Increment usage count for a specific attachment.
        
        Args:
            main_id: ID of the main prompt
            attached_id: ID of the attached prompt
            
        Returns:
            True if successful, False if attachment not found
        """
        try:
            attachment = self.attached_prompt_repo.find_attachment(main_id, attached_id)
            if attachment:
                attachment.increment_usage()
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to increment usage for attachment {main_id} -> {attached_id}: {str(e)}")
            return False
    
    def get_available_for_attachment(self, main_id: int, exclude_ids: Optional[List[int]] = None) -> List[Prompt]:
        """
        Get prompts that can be attached to a specific prompt.
        
        Args:
            main_id: ID of the main prompt
            exclude_ids: List of prompt IDs to exclude
            
        Returns:
            List of prompts available for attachment
        """
        return self.prompt_repo.get_available_for_attachment(main_id, exclude_ids)
    
    def _would_create_circle(self, main_id: int, attached_id: int) -> bool:
        """
        Check if attaching a prompt would create a circular reference.
        
        Args:
            main_id: ID of the main prompt
            attached_id: ID of the prompt to attach
            
        Returns:
            True if circular reference would be created
        """
        # Check if the attached prompt is already attached to the main prompt
        # or if any of its attached prompts would create a circle
        visited = set()
        return self._has_path_to(attached_id, main_id, visited)
    
    def _has_path_to(self, start_id: int, target_id: int, visited: set) -> bool:
        """
        Recursively check if there's a path from start_id to target_id.
        
        Args:
            start_id: Starting prompt ID
            target_id: Target prompt ID
            visited: Set of visited prompt IDs to prevent infinite recursion
            
        Returns:
            True if path exists
        """
        if start_id == target_id:
            return True
        
        if start_id in visited:
            return False
        
        visited.add(start_id)
        
        # Get all prompts that have start_id attached to them
        attached_relationships = self.attached_prompt_repo.get_prompts_attached_to(start_id)
        
        for relationship in attached_relationships:
            if self._has_path_to(relationship.main_prompt_id, target_id, visited):
                return True
        
        return False
    
    def validate_attachment(self, main_id: int, attached_id: int) -> List[str]:
        """
        Validate if an attachment would be valid without creating it.
        
        Args:
            main_id: ID of the main prompt
            attached_id: ID of the prompt to attach
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Check if prompts exist
        main_prompt = self.prompt_repo.get_by_id(main_id)
        if not main_prompt:
            errors.append(f"Main prompt with ID {main_id} does not exist")
        
        attached_prompt = self.prompt_repo.get_by_id(attached_id)
        if not attached_prompt:
            errors.append(f"Attached prompt with ID {attached_id} does not exist")
        
        if errors:
            return errors
        
        # Check if prompts are active
        if not main_prompt.is_active:
            errors.append(f"Main prompt with ID {main_id} is not active")
        
        if not attached_prompt.is_active:
            errors.append(f"Attached prompt with ID {attached_id} is not active")
        
        # Check for self-attachment
        if main_id == attached_id:
            errors.append("Cannot attach prompt to itself")
        
        # Check for existing attachment
        if self.attached_prompt_repo.exists(main_id, attached_id):
            errors.append(f"Prompt {attached_id} is already attached to prompt {main_id}")
        
        # Check for circular attachment
        if self._would_create_circle(main_id, attached_id):
            errors.append("Circular attachment detected - this would create an infinite loop")
        
        # Check attachment limit
        current_count = self.attached_prompt_repo.get_attachment_count(main_id)
        max_attachments = 10
        if current_count >= max_attachments:
            errors.append(f"Maximum number of attached prompts ({max_attachments}) reached for prompt {main_id}")
        
        return errors 