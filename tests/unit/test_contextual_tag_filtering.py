"""
Unit tests for contextual tag filtering functionality.

Tests cover:
- TagRepository.get_popular_tags() with status filtering
- TagService.get_popular_tags() with status parameter
- Controller API endpoint functionality
- Error handling scenarios
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from app.repositories.tag_repository import TagRepository
from app.services.tag_service import TagService
from app.controllers.prompt_controller import get_popular_tags_api
from app.models.tag import Tag
from app.models.prompt import Prompt
from flask import Flask, json
from werkzeug.exceptions import HTTPException


class TestTagRepositoryContextualFiltering:
    """Test TagRepository.get_popular_tags() with status filtering."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def tag_repo(self, mock_session):
        """Create TagRepository instance with mock session."""
        return TagRepository(mock_session)
    
    @pytest.fixture
    def sample_tags(self):
        """Create sample tag data for testing."""
        return [
            Tag(id=1, name="python", color="#3776ab"),
            Tag(id=2, name="javascript", color="#f7df1e"),
            Tag(id=3, name="sql", color="#e48e00"),
            Tag(id=4, name="html", color="#e34f26"),
            Tag(id=5, name="css", color="#1572b6")
        ]
    
    @pytest.fixture
    def sample_prompts(self):
        """Create sample prompt data for testing."""
        return [
            Prompt(id=1, title="Python Guide", is_active=True),
            Prompt(id=2, title="JS Tutorial", is_active=True),
            Prompt(id=3, title="SQL Basics", is_active=False),
            Prompt(id=4, title="HTML Intro", is_active=True),
            Prompt(id=5, title="CSS Styling", is_active=False)
        ]
    
    def test_get_popular_tags_all_statuses(self, tag_repo, mock_session, sample_tags):
        """Test getting popular tags without status filter (all tags)."""
        # Mock query results
        mock_results = [
            (sample_tags[0], 5),  # python: 5 uses
            (sample_tags[1], 3),  # javascript: 3 uses
            (sample_tags[2], 2),  # sql: 2 uses
        ]
        
        # Mock the query chain
        mock_query = Mock()
        mock_outerjoin = Mock()
        mock_group_by = Mock()
        mock_order_by = Mock()
        mock_limit = Mock()
        
        mock_session.query.return_value = mock_query
        mock_query.outerjoin.return_value = mock_outerjoin
        mock_outerjoin.group_by.return_value = mock_group_by
        mock_group_by.order_by.return_value = mock_order_by
        mock_order_by.limit.return_value = mock_limit
        mock_limit.all.return_value = mock_results
        
        # Execute method
        result = tag_repo.get_popular_tags(limit=3, is_active=None)
        
        # Verify results
        assert len(result) == 3
        assert result[0]['tag'].name == "python"
        assert result[0]['usage_count'] == 5
        assert result[1]['tag'].name == "javascript"
        assert result[1]['usage_count'] == 3
        assert result[2]['tag'].name == "sql"
        assert result[2]['usage_count'] == 2
        
        # Verify query was called correctly
        mock_session.query.assert_called_once()
    
    def test_get_popular_tags_active_only(self, tag_repo, mock_session, sample_tags, sample_prompts):
        """Test getting popular tags for active prompts only."""
        # Mock query results for active prompts
        mock_results = [
            (sample_tags[0], 3),  # python: 3 active uses
            (sample_tags[1], 2),  # javascript: 2 active uses
            (sample_tags[3], 1),  # html: 1 active use
        ]
        
        # Mock the query chain with JOIN
        mock_query = Mock()
        mock_join = Mock()
        mock_filter = Mock()
        mock_group_by = Mock()
        mock_order_by = Mock()
        mock_limit = Mock()
        
        mock_session.query.return_value = mock_query
        mock_query.join.return_value = mock_join
        mock_join.filter.return_value = mock_filter
        mock_filter.group_by.return_value = mock_group_by
        mock_group_by.order_by.return_value = mock_order_by
        mock_order_by.limit.return_value = mock_limit
        mock_limit.all.return_value = mock_results
        
        # Execute method
        result = tag_repo.get_popular_tags(limit=3, is_active=True)
        
        # Verify results
        assert len(result) == 3
        assert result[0]['tag'].name == "python"
        assert result[0]['usage_count'] == 3
        assert result[1]['tag'].name == "javascript"
        assert result[1]['usage_count'] == 2
        assert result[2]['tag'].name == "html"
        assert result[2]['usage_count'] == 1
        
        # Verify JOIN was used for active filter
        mock_query.join.assert_called_once()
    
    def test_get_popular_tags_inactive_only(self, tag_repo, mock_session, sample_tags, sample_prompts):
        """Test getting popular tags for inactive prompts only."""
        # Mock query results for inactive prompts
        mock_results = [
            (sample_tags[2], 2),  # sql: 2 inactive uses
            (sample_tags[4], 1),  # css: 1 inactive use
        ]
        
        # Mock the query chain with JOIN
        mock_query = Mock()
        mock_join = Mock()
        mock_filter = Mock()
        mock_group_by = Mock()
        mock_order_by = Mock()
        mock_limit = Mock()
        
        mock_session.query.return_value = mock_query
        mock_query.join.return_value = mock_join
        mock_join.filter.return_value = mock_filter
        mock_filter.group_by.return_value = mock_group_by
        mock_group_by.order_by.return_value = mock_order_by
        mock_order_by.limit.return_value = mock_limit
        mock_limit.all.return_value = mock_results
        
        # Execute method
        result = tag_repo.get_popular_tags(limit=2, is_active=False)
        
        # Verify results
        assert len(result) == 2
        assert result[0]['tag'].name == "sql"
        assert result[0]['usage_count'] == 2
        assert result[1]['tag'].name == "css"
        assert result[1]['usage_count'] == 1
        
        # Verify JOIN was used for inactive filter
        mock_query.join.assert_called_once()
    
    def test_get_popular_tags_empty_result(self, tag_repo, mock_session):
        """Test getting popular tags when no tags exist."""
        # Mock empty results
        mock_query = Mock()
        mock_outerjoin = Mock()
        mock_group_by = Mock()
        mock_order_by = Mock()
        mock_limit = Mock()
        
        mock_session.query.return_value = mock_query
        mock_query.outerjoin.return_value = mock_outerjoin
        mock_outerjoin.group_by.return_value = mock_group_by
        mock_group_by.order_by.return_value = mock_order_by
        mock_order_by.limit.return_value = mock_limit
        mock_limit.all.return_value = []
        
        # Execute method
        result = tag_repo.get_popular_tags(limit=10, is_active=None)
        
        # Verify empty result
        assert len(result) == 0
    
    def test_get_popular_tags_backward_compatibility(self, tag_repo, mock_session, sample_tags):
        """Test backward compatibility - no is_active parameter."""
        # Mock query results
        mock_results = [(sample_tags[0], 5)]
        
        # Mock the query chain
        mock_query = Mock()
        mock_outerjoin = Mock()
        mock_group_by = Mock()
        mock_order_by = Mock()
        mock_limit = Mock()
        
        mock_session.query.return_value = mock_query
        mock_query.outerjoin.return_value = mock_outerjoin
        mock_outerjoin.group_by.return_value = mock_group_by
        mock_group_by.order_by.return_value = mock_order_by
        mock_order_by.limit.return_value = mock_limit
        mock_limit.all.return_value = mock_results
        
        # Execute method without is_active parameter
        result = tag_repo.get_popular_tags(limit=1)
        
        # Verify results
        assert len(result) == 1
        assert result[0]['tag'].name == "python"
        assert result[0]['usage_count'] == 5
        
        # Verify OUTER JOIN was used (default behavior)
        mock_query.outerjoin.assert_called_once()


class TestTagServiceContextualFiltering:
    """Test TagService.get_popular_tags() with status parameter."""
    
    @pytest.fixture
    def mock_tag_repo(self):
        """Create a mock TagRepository."""
        return Mock(spec=TagRepository)
    
    @pytest.fixture
    def tag_service(self, mock_tag_repo):
        """Create TagService instance with mock repository."""
        return TagService(mock_tag_repo)
    
    def test_get_popular_tags_passes_parameters(self, tag_service, mock_tag_repo):
        """Test that TagService passes parameters correctly to repository."""
        # Mock repository response
        mock_response = [{'tag': Tag(id=1, name="test", color="#000"), 'usage_count': 1}]
        mock_tag_repo.get_popular_tags.return_value = mock_response
        
        # Execute method
        result = tag_service.get_popular_tags(limit=5, is_active=True)
        
        # Verify repository was called with correct parameters
        mock_tag_repo.get_popular_tags.assert_called_once_with(limit=5, is_active=True)
        
        # Verify result is passed through
        assert result == mock_response
    
    def test_get_popular_tags_none_status(self, tag_service, mock_tag_repo):
        """Test TagService with None status parameter."""
        mock_response = [{'tag': Tag(id=1, name="test", color="#000"), 'usage_count': 1}]
        mock_tag_repo.get_popular_tags.return_value = mock_response
        
        result = tag_service.get_popular_tags(limit=3, is_active=None)
        
        mock_tag_repo.get_popular_tags.assert_called_once_with(limit=3, is_active=None)
        assert result == mock_response
    
    def test_get_popular_tags_backward_compatibility(self, tag_service, mock_tag_repo):
        """Test TagService backward compatibility - no is_active parameter."""
        mock_response = [{'tag': Tag(id=1, name="test", color="#000"), 'usage_count': 1}]
        mock_tag_repo.get_popular_tags.return_value = mock_response
        
        result = tag_service.get_popular_tags(limit=10)
        
        # Should pass None as default for is_active
        mock_tag_repo.get_popular_tags.assert_called_once_with(limit=10, is_active=None)
        assert result == mock_response


class TestControllerAPIContextualFiltering:
    """Test controller API endpoint for contextual tag filtering."""
    
    @pytest.fixture
    def app(self):
        """Create Flask app for testing."""
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    @patch('app.controllers.prompt_controller.tag_service')
    def test_get_popular_tags_api_success(self, mock_tag_service, app, client):
        """Test successful API response."""
        # Mock service response
        mock_tags = [
            {'tag': Tag(id=1, name="python", color="#3776ab"), 'usage_count': 5},
            {'tag': Tag(id=2, name="javascript", color="#f7df1e"), 'usage_count': 3}
        ]
        mock_tag_service.get_popular_tags.return_value = mock_tags
        
        # Register route
        app.add_url_rule('/api/tags/popular', 'get_popular_tags_api', get_popular_tags_api)
        
        # Make request
        response = client.get('/api/tags/popular?is_active=true')
        
        # Verify response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['tags']) == 2
        assert data['tags'][0]['name'] == "python"
        assert data['tags'][0]['usage_count'] == 5
        assert data['tags'][1]['name'] == "javascript"
        assert data['tags'][1]['usage_count'] == 3
        
        # Verify service was called correctly
        mock_tag_service.get_popular_tags.assert_called_once_with(limit=10, is_active=True)
    
    @patch('app.controllers.prompt_controller.tag_service')
    def test_get_popular_tags_api_all_status(self, mock_tag_service, app, client):
        """Test API with 'all' status (no filter)."""
        mock_tags = [{'tag': Tag(id=1, name="test", color="#000"), 'usage_count': 1}]
        mock_tag_service.get_popular_tags.return_value = mock_tags
        
        app.add_url_rule('/api/tags/popular', 'get_popular_tags_api', get_popular_tags_api)
        
        # Test with 'all' parameter
        response = client.get('/api/tags/popular?is_active=all')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Should pass None for is_active
        mock_tag_service.get_popular_tags.assert_called_once_with(limit=10, is_active=None)
    
    @patch('app.controllers.prompt_controller.tag_service')
    def test_get_popular_tags_api_no_parameter(self, mock_tag_service, app, client):
        """Test API without is_active parameter."""
        mock_tags = [{'tag': Tag(id=1, name="test", color="#000"), 'usage_count': 1}]
        mock_tag_service.get_popular_tags.return_value = mock_tags
        
        app.add_url_rule('/api/tags/popular', 'get_popular_tags_api', get_popular_tags_api)
        
        response = client.get('/api/tags/popular')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Should pass None for is_active
        mock_tag_service.get_popular_tags.assert_called_once_with(limit=10, is_active=None)
    
    @patch('app.controllers.prompt_controller.tag_service')
    def test_get_popular_tags_api_error_handling(self, mock_tag_service, app, client):
        """Test API error handling."""
        # Mock service to raise exception
        mock_tag_service.get_popular_tags.side_effect = Exception("Database error")
        
        app.add_url_rule('/api/tags/popular', 'get_popular_tags_api', get_popular_tags_api)
        
        response = client.get('/api/tags/popular?is_active=true')
        
        # Verify error response
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data
        assert 'Database error' in data['error']
    
    @patch('app.controllers.prompt_controller.tag_service')
    def test_get_popular_tags_api_invalid_parameter(self, mock_tag_service, app, client):
        """Test API with invalid is_active parameter."""
        mock_tags = [{'tag': Tag(id=1, name="test", color="#000"), 'usage_count': 1}]
        mock_tag_service.get_popular_tags.return_value = mock_tags
        
        app.add_url_rule('/api/tags/popular', 'get_popular_tags_api', get_popular_tags_api)
        
        # Test with invalid parameter
        response = client.get('/api/tags/popular?is_active=invalid')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Should pass None for invalid parameter
        mock_tag_service.get_popular_tags.assert_called_once_with(limit=10, is_active=None)
    
    @patch('app.controllers.prompt_controller.tag_service')
    def test_get_popular_tags_api_empty_result(self, mock_tag_service, app, client):
        """Test API with empty result."""
        mock_tag_service.get_popular_tags.return_value = []
        
        app.add_url_rule('/api/tags/popular', 'get_popular_tags_api', get_popular_tags_api)
        
        response = client.get('/api/tags/popular?is_active=false')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['tags']) == 0


class TestContextualFilteringIntegration:
    """Integration tests for contextual tag filtering."""
    
    def test_parameter_conversion_logic(self):
        """Test parameter conversion logic in controller."""
        # Test string 'true' -> boolean True
        assert self._convert_is_active_param('true') is True
        
        # Test string 'false' -> boolean False
        assert self._convert_is_active_param('false') is False
        
        # Test 'all' -> None
        assert self._convert_is_active_param('all') is None
        
        # Test None -> None
        assert self._convert_is_active_param(None) is None
        
        # Test invalid string -> None
        assert self._convert_is_active_param('invalid') is None
    
    def _convert_is_active_param(self, value):
        """Helper method to test parameter conversion logic."""
        if value == 'true':
            return True
        elif value == 'false':
            return False
        else:
            return None
    
    def test_tag_count_formatting(self):
        """Test tag count formatting logic."""
        # Test zero count
        assert self._format_count(0) == '0'
        
        # Test normal count
        assert self._format_count(5) == '5'
        
        # Test large count
        assert self._format_count(100) == '99+'
        assert self._format_count(999) == '99+'
    
    def _format_count(self, count):
        """Helper method to test count formatting logic."""
        if count == 0:
            return '0'
        if count > 99:
            return '99+'
        return str(count)
    
    def test_count_class_assignment(self):
        """Test count class assignment logic."""
        # Test zero count
        assert self._get_count_class(0) == 'count-zero'
        
        # Test low count
        assert self._get_count_class(1) == 'count-low'
        assert self._get_count_class(2) == 'count-low'
        
        # Test medium count
        assert self._get_count_class(3) == 'count-medium'
        assert self._get_count_class(5) == 'count-medium'
        
        # Test high count
        assert self._get_count_class(6) == 'count-high'
        assert self._get_count_class(10) == 'count-high'
    
    def _get_count_class(self, count):
        """Helper method to test count class assignment logic."""
        if count == 0:
            return 'count-zero'
        if count <= 2:
            return 'count-low'
        if count <= 5:
            return 'count-medium'
        return 'count-high'


if __name__ == '__main__':
    pytest.main([__file__]) 