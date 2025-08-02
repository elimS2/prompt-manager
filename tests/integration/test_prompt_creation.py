"""
Integration tests for prompt creation functionality.
"""
import pytest
import requests
import time
from app import create_app
from app.models import db
from app.services import PromptService


class TestPromptCreation:
    """Test prompt creation through web interface."""
    
    @pytest.fixture
    def app(self):
        """Create test application."""
        app = create_app('testing')
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    def test_create_prompt_page_accessible(self, client):
        """Test that create prompt page is accessible."""
        response = client.get('/prompts/create')
        assert response.status_code == 200
        assert b'Create New Prompt' in response.data
    
    def test_create_prompt_success(self, client):
        """Test successful prompt creation."""
        form_data = {
            'title': 'Test Integration Prompt',
            'content': 'This is a test prompt for integration testing.',
            'description': 'Integration test description',
            'tags': 'integration,test,prompt',
            'is_active': 'true'
        }
        
        response = client.post('/prompts/create', data=form_data, follow_redirects=False)
        assert response.status_code == 302  # Redirect after successful creation
        
        # Follow redirect to view page
        redirect_url = response.headers.get('Location')
        assert redirect_url is not None
        assert '/prompts/' in redirect_url
        
        # Check the created prompt
        view_response = client.get(redirect_url)
        assert view_response.status_code == 200
        assert b'Test Integration Prompt' in view_response.data
        assert b'This is a test prompt for integration testing.' in view_response.data
    
    def test_create_prompt_validation_errors(self, client):
        """Test validation errors when creating prompt."""
        # Test missing title
        form_data = {
            'title': '',
            'content': 'Some content',
            'is_active': 'true'
        }
        
        response = client.post('/prompts/create', data=form_data, follow_redirects=True)
        assert response.status_code == 200
        assert b'Title is required' in response.data
        
        # Test missing content
        form_data = {
            'title': 'Some title',
            'content': '',
            'is_active': 'true'
        }
        
        response = client.post('/prompts/create', data=form_data, follow_redirects=True)
        assert response.status_code == 200
        assert b'Content is required' in response.data
    
    def test_create_prompt_with_tags(self, client):
        """Test prompt creation with tags."""
        form_data = {
            'title': 'Tagged Prompt',
            'content': 'Prompt with tags',
            'tags': 'python,testing,integration',
            'is_active': 'true'
        }
        
        response = client.post('/prompts/create', data=form_data, follow_redirects=False)
        assert response.status_code == 302
        
        # Follow redirect and check tags
        redirect_url = response.headers.get('Location')
        view_response = client.get(redirect_url)
        assert view_response.status_code == 200
        assert b'python' in view_response.data
        assert b'testing' in view_response.data
        assert b'integration' in view_response.data
    
    def test_create_prompt_inactive(self, client):
        """Test creating inactive prompt."""
        form_data = {
            'title': 'Inactive Prompt',
            'content': 'This prompt is inactive',
            'is_active': 'false'
        }
        
        response = client.post('/prompts/create', data=form_data, follow_redirects=False)
        assert response.status_code == 302
        
        # Check that prompt was created (even if inactive)
        redirect_url = response.headers.get('Location')
        view_response = client.get(redirect_url)
        assert view_response.status_code == 200
        assert b'Inactive Prompt' in view_response.data


class TestPromptService:
    """Test prompt service directly."""
    
    @pytest.fixture
    def app(self):
        """Create test application."""
        app = create_app('testing')
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    def test_create_prompt_service(self, app):
        """Test prompt creation through service."""
        with app.app_context():
            service = PromptService()
            
            data = {
                'title': 'Service Test Prompt',
                'content': 'Test content for service',
                'description': 'Service test description',
                'tags': ['service', 'test'],
                'is_active': True
            }
            
            prompt = service.create_prompt(data)
            
            assert prompt.id is not None
            assert prompt.title == 'Service Test Prompt'
            assert prompt.content == 'Test content for service'
            assert prompt.is_active is True
            assert len(prompt.tags) == 2
            assert any(tag.name == 'service' for tag in prompt.tags)
            assert any(tag.name == 'test' for tag in prompt.tags)
    
    def test_create_prompt_validation(self, app):
        """Test prompt validation in service."""
        with app.app_context():
            service = PromptService()
            
            # Test missing title
            with pytest.raises(ValueError, match="Title is required"):
                service.create_prompt({'content': 'Some content'})
            
            # Test missing content
            with pytest.raises(ValueError, match="Content is required"):
                service.create_prompt({'title': 'Some title'})
            
            # Test title too long
            long_title = 'a' * 256
            with pytest.raises(ValueError, match="Title must be less than 255 characters"):
                service.create_prompt({'title': long_title, 'content': 'Some content'}) 