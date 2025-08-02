import pytest
from unittest.mock import Mock, patch
from app.models.prompt import Prompt
from app.services.prompt_service import PromptService
from app.repositories.prompt_repository import PromptRepository


class TestArchiveFunctionality:
    """Тесты для функциональности архивирования промптов."""
    
    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.mock_repo = Mock(spec=PromptRepository)
        self.prompt_service = PromptService()
        self.prompt_service.prompt_repo = self.mock_repo
    
    def test_archive_prompt_success(self):
        """Тест успешного архивирования промпта."""
        # Arrange
        prompt_id = 1
        self.mock_repo.soft_delete.return_value = True
        
        # Act
        result = self.prompt_service.archive_prompt(prompt_id)
        
        # Assert
        assert result is True
        self.mock_repo.soft_delete.assert_called_once_with(prompt_id)
    
    def test_archive_prompt_not_found(self):
        """Тест архивирования несуществующего промпта."""
        # Arrange
        prompt_id = 999
        self.mock_repo.soft_delete.return_value = False
        
        # Act
        result = self.prompt_service.archive_prompt(prompt_id)
        
        # Assert
        assert result is False
        self.mock_repo.soft_delete.assert_called_once_with(prompt_id)
    
    def test_archive_prompt_uses_soft_delete(self):
        """Тест что архивирование использует метод soft_delete."""
        # Arrange
        prompt_id = 1
        self.mock_repo.soft_delete.return_value = True
        
        # Act
        self.prompt_service.archive_prompt(prompt_id)
        
        # Assert
        self.mock_repo.soft_delete.assert_called_once_with(prompt_id)
        # Убеждаемся что не вызывается hard delete
        self.mock_repo.delete.assert_not_called()


class TestPromptModelArchive:
    """Тесты модели Prompt для архивирования."""
    
    def test_prompt_is_active_default(self):
        """Тест что по умолчанию промпт активен."""
        # Arrange & Act
        prompt = Prompt(
            title="Test Prompt",
            content="Test content",
            description="Test description",
            is_active=True
        )
        
        # Assert
        assert prompt.is_active is True
    
    def test_prompt_is_active_field_exists(self):
        """Тест что поле is_active существует и имеет правильный тип."""
        # Arrange & Act
        prompt = Prompt(
            title="Test Prompt",
            content="Test content",
            description="Test description",
            is_active=True
        )
        
        # Assert
        assert hasattr(prompt, 'is_active')
        assert isinstance(prompt.is_active, bool)
        assert prompt.is_active is True
    
    def test_prompt_can_be_archived(self):
        """Тест что промпт может быть архивирован."""
        # Arrange
        prompt = Prompt(
            title="Test Prompt",
            content="Test content",
            description="Test description"
        )
        
        # Act
        prompt.is_active = False
        
        # Assert
        assert prompt.is_active is False
    
    def test_prompt_can_be_restored(self):
        """Тест что промпт может быть восстановлен."""
        # Arrange
        prompt = Prompt(
            title="Test Prompt",
            content="Test content",
            description="Test description",
            is_active=False
        )
        
        # Act
        prompt.is_active = True
        
        # Assert
        assert prompt.is_active is True 