"""
Repository for AttachedPrompt model with specific query methods.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import func, desc
from app.models import AttachedPrompt, Prompt
from .base import BaseRepository


class AttachedPromptRepository(BaseRepository[AttachedPrompt]):
    """Repository for managing AttachedPrompt data access."""
    
    def __init__(self):
        """Initialize AttachedPromptRepository."""
        super().__init__(AttachedPrompt)
    
    def get_attached_prompts(self, main_prompt_id: int) -> List[AttachedPrompt]:
        """
        Get all prompts attached to a main prompt, ordered by order field.
        
        Args:
            main_prompt_id: ID of the main prompt
            
        Returns:
            List of AttachedPrompt instances ordered by order field
        """
        return self.model.query.filter_by(main_prompt_id=main_prompt_id)\
                              .order_by(self.model.order)\
                              .all()
    
    def get_prompts_attached_to(self, prompt_id: int) -> List[AttachedPrompt]:
        """
        Get all prompts that have the specified prompt attached to them.
        
        Args:
            prompt_id: ID of the prompt to find attachments for
            
        Returns:
            List of AttachedPrompt instances where this prompt is attached
        """
        return self.model.query.filter_by(attached_prompt_id=prompt_id)\
                              .order_by(self.model.order)\
                              .all()
    
    def attach_prompt(self, main_prompt_id: int, attached_prompt_id: int, order: int = 0) -> AttachedPrompt:
        """
        Attach a prompt to another prompt.
        
        Args:
            main_prompt_id: ID of the main prompt
            attached_prompt_id: ID of the prompt to attach
            order: Order position for the attached prompt
            
        Returns:
            Created AttachedPrompt instance
            
        Raises:
            ValueError: If attachment already exists
        """
        # Check if attachment already exists
        existing = self.model.query.filter_by(
            main_prompt_id=main_prompt_id,
            attached_prompt_id=attached_prompt_id
        ).first()
        
        if existing:
            raise ValueError(f"Prompt {attached_prompt_id} is already attached to prompt {main_prompt_id}")
        
        # Create new attachment using the base repository create method
        return self.create(
            main_prompt_id=main_prompt_id,
            attached_prompt_id=attached_prompt_id,
            order=order
        )
    
    def detach_prompt(self, main_prompt_id: int, attached_prompt_id: int) -> bool:
        """
        Detach a prompt from another prompt.
        
        Args:
            main_prompt_id: ID of the main prompt
            attached_prompt_id: ID of the prompt to detach
            
        Returns:
            True if detachment was successful, False if attachment didn't exist
        """
        attached_prompt = self.model.query.filter_by(
            main_prompt_id=main_prompt_id,
            attached_prompt_id=attached_prompt_id
        ).first()
        
        if not attached_prompt:
            return False
        
        self.delete(attached_prompt.id)
        return True
    
    def reorder_attached_prompts(self, main_prompt_id: int, order_map: Dict[int, int]) -> bool:
        """
        Reorder attached prompts for a main prompt.
        
        Args:
            main_prompt_id: ID of the main prompt
            order_map: Dictionary mapping attached_prompt_id to new order
            
        Returns:
            True if reordering was successful
        """
        try:
            for attached_prompt_id, new_order in order_map.items():
                attached_prompt = self.model.query.filter_by(
                    main_prompt_id=main_prompt_id,
                    attached_prompt_id=attached_prompt_id
                ).first()
                
                if attached_prompt:
                    attached_prompt.order = new_order
            
            self.db.session.commit()
            return True
        except Exception:
            self.db.session.rollback()
            return False
    
    def get_popular_combinations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most frequently used prompt combinations.
        
        Args:
            limit: Maximum number of combinations to return
            
        Returns:
            List of dictionaries with combination statistics
        """
        result = self.session.query(
            AttachedPrompt.main_prompt_id,
            AttachedPrompt.attached_prompt_id,
            AttachedPrompt.usage_count,
            Prompt.title.label('main_title'),
            Prompt.title.label('attached_title')
        ).join(
            Prompt, AttachedPrompt.main_prompt_id == Prompt.id
        ).filter(
            AttachedPrompt.usage_count > 0
        ).order_by(
            AttachedPrompt.usage_count.desc()
        ).limit(limit).all()
        
        return [
            {
                'main_prompt_id': row.main_prompt_id,
                'attached_prompt_id': row.attached_prompt_id,
                'usage_count': row.usage_count,
                'main_title': row.main_title,
                'attached_title': row.attached_title
            }
            for row in result
        ]
    
    def get_attached_prompts_with_details(self, main_prompt_id: int) -> List[Dict[str, Any]]:
        """
        Get attached prompts with full prompt details.
        
        Args:
            main_prompt_id: ID of the main prompt
            
        Returns:
            List of dictionaries with attached prompt details
        """
        result = self.session.query(
            AttachedPrompt,
            Prompt.title.label('attached_title'),
            Prompt.content.label('attached_content')
        ).join(
            Prompt, AttachedPrompt.attached_prompt_id == Prompt.id
        ).filter(
            AttachedPrompt.main_prompt_id == main_prompt_id
        ).order_by(
            AttachedPrompt.order
        ).all()
        
        return [
            {
                'id': row.AttachedPrompt.id,
                'main_prompt_id': row.AttachedPrompt.main_prompt_id,
                'attached_prompt_id': row.AttachedPrompt.attached_prompt_id,
                'order': row.AttachedPrompt.order,
                'attached_title': row.attached_title,
                'attached_content': row.attached_content,
                'created_at': row.AttachedPrompt.created_at
            }
            for row in result
        ]
    
    def exists(self, main_prompt_id: int, attached_prompt_id: int) -> bool:
        """
        Check if an attachment relationship already exists.
        
        Args:
            main_prompt_id: ID of the main prompt
            attached_prompt_id: ID of the attached prompt
            
        Returns:
            True if attachment exists, False otherwise
        """
        return self.model.query.filter_by(
            main_prompt_id=main_prompt_id,
            attached_prompt_id=attached_prompt_id
        ).first() is not None
    
    def get_attachment_count(self, main_prompt_id: int) -> int:
        """
        Get the number of prompts attached to a main prompt.
        
        Args:
            main_prompt_id: ID of the main prompt
            
        Returns:
            Number of attached prompts
        """
        return self.model.query.filter_by(main_prompt_id=main_prompt_id).count()
    
    def get_max_order(self, main_prompt_id: int) -> int:
        """
        Get the maximum order value for attached prompts of a main prompt.
        
        Args:
            main_prompt_id: ID of the main prompt
            
        Returns:
            Maximum order value, or -1 if no attachments exist
        """
        result = self.session.query(
            func.max(AttachedPrompt.order)
        ).filter_by(
            main_prompt_id=main_prompt_id
        ).scalar()
        
        return result if result is not None else -1
    
    def find_attachment(self, main_prompt_id: int, attached_prompt_id: int) -> Optional[AttachedPrompt]:
        """
        Find a specific attachment relationship.
        
        Args:
            main_prompt_id: ID of the main prompt
            attached_prompt_id: ID of the attached prompt
            
        Returns:
            AttachedPrompt instance if found, None otherwise
        """
        return self.model.query.filter_by(
            main_prompt_id=main_prompt_id,
            attached_prompt_id=attached_prompt_id
        ).first() 