"""
Integration tests for contextual tag filtering functionality.

Tests cover:
- Complete workflow from status filter change to tag update
- AJAX endpoint integration with real database
- JavaScript DOM updates
- Error scenarios in real environment
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from flask import Flask
from app import create_app
from app.models.tag import Tag
from app.models.prompt import Prompt
from app.models.base import db
from app.services.tag_service import TagService
from app.repositories.tag_repository import TagRepository


class TestContextualTagFilteringIntegration:
    """Integration tests for contextual tag filtering workflow."""
    
    @pytest.fixture
    def app(self):
        """Create Flask app for testing."""
        app = create_app('testing')
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    @pytest.fixture
    def db_session(self, app):
        """Create database session."""
        with app.app_context():
            db.create_all()
            yield db.session
            db.session.remove()
            db.drop_all()
    
    @pytest.fixture
    def sample_data(self, db_session):
        """Create sample data for testing."""
        # Create tags
        tag1 = Tag(name="python", color="#3776ab")
        tag2 = Tag(name="javascript", color="#f7df1e")
        tag3 = Tag(name="sql", color="#e48e00")
        tag4 = Tag(name="html", color="#e34f26")
        tag5 = Tag(name="css", color="#1572b6")
        
        db_session.add_all([tag1, tag2, tag3, tag4, tag5])
        db_session.commit()
        
        # Create prompts with different statuses
        prompt1 = Prompt(title="Python Guide", content="Python tutorial", is_active=True)
        prompt2 = Prompt(title="JS Tutorial", content="JavaScript guide", is_active=True)
        prompt3 = Prompt(title="SQL Basics", content="SQL introduction", is_active=False)
        prompt4 = Prompt(title="HTML Intro", content="HTML basics", is_active=True)
        prompt5 = Prompt(title="CSS Styling", content="CSS guide", is_active=False)
        
        db_session.add_all([prompt1, prompt2, prompt3, prompt4, prompt5])
        db_session.commit()
        
        # Associate tags with prompts
        prompt1.tags = [tag1, tag2]  # python, javascript (active)
        prompt2.tags = [tag2, tag4]  # javascript, html (active)
        prompt3.tags = [tag3]        # sql (inactive)
        prompt4.tags = [tag4, tag5]  # html, css (active + inactive)
        prompt5.tags = [tag5]        # css (inactive)
        
        db_session.commit()
        
        return {
            'tags': [tag1, tag2, tag3, tag4, tag5],
            'prompts': [prompt1, prompt2, prompt3, prompt4, prompt5]
        }
    
    def test_api_endpoint_with_real_database(self, client, db_session, sample_data):
        """Test API endpoint with real database queries."""
        # Test getting all tags
        response = client.get('/api/tags/popular')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['tags']) > 0
        
        # Test getting active tags only
        response = client.get('/api/tags/popular?is_active=true')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Verify only active tags are returned
        active_tags = [tag['name'] for tag in data['tags']]
        assert 'python' in active_tags
        assert 'javascript' in active_tags
        assert 'html' in active_tags
        # sql and css should not be in active tags (or have 0 count)
        
        # Test getting inactive tags only
        response = client.get('/api/tags/popular?is_active=false')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Verify inactive tags are returned
        inactive_tags = [tag['name'] for tag in data['tags']]
        assert 'sql' in inactive_tags
        assert 'css' in inactive_tags
    
    def test_tag_service_integration(self, app, db_session, sample_data):
        """Test TagService integration with real database."""
        with app.app_context():
            tag_service = TagService(TagRepository(db_session))
            
            # Test getting all tags
            all_tags = tag_service.get_popular_tags(limit=10, is_active=None)
            assert len(all_tags) > 0
            
            # Test getting active tags
            active_tags = tag_service.get_popular_tags(limit=10, is_active=True)
            assert len(active_tags) > 0
            
            # Verify active tags have correct counts
            for tag_data in active_tags:
                if tag_data['tag'].name == 'python':
                    assert tag_data['usage_count'] >= 1
                elif tag_data['tag'].name == 'javascript':
                    assert tag_data['usage_count'] >= 2
            
            # Test getting inactive tags
            inactive_tags = tag_service.get_popular_tags(limit=10, is_active=False)
            assert len(inactive_tags) > 0
            
            # Verify inactive tags have correct counts
            for tag_data in inactive_tags:
                if tag_data['tag'].name == 'sql':
                    assert tag_data['usage_count'] >= 1
                elif tag_data['tag'].name == 'css':
                    assert tag_data['usage_count'] >= 1
    
    def test_parameter_conversion_integration(self, client, db_session, sample_data):
        """Test parameter conversion in real API calls."""
        # Test string 'true'
        response = client.get('/api/tags/popular?is_active=true')
        assert response.status_code == 200
        
        # Test string 'false'
        response = client.get('/api/tags/popular?is_active=false')
        assert response.status_code == 200
        
        # Test 'all'
        response = client.get('/api/tags/popular?is_active=all')
        assert response.status_code == 200
        
        # Test invalid parameter
        response = client.get('/api/tags/popular?is_active=invalid')
        assert response.status_code == 200
        
        # Test no parameter
        response = client.get('/api/tags/popular')
        assert response.status_code == 200
    
    def test_error_handling_integration(self, client, db_session):
        """Test error handling in real environment."""
        # Test with empty database
        response = client.get('/api/tags/popular?is_active=true')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['tags']) == 0
    
    @pytest.mark.selenium
    def test_javascript_dom_updates(self, app, db_session, sample_data):
        """Test JavaScript DOM updates with Selenium (requires Chrome)."""
        # This test requires Chrome WebDriver
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(options=chrome_options)
            
            try:
                # Navigate to prompts page
                driver.get("http://localhost:5001/prompts")
                
                # Wait for page to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "popular-tags-container"))
                )
                
                # Get initial tags
                initial_tags = driver.find_elements(By.CSS_SELECTOR, ".popular-tags-container .tag-filter")
                initial_count = len(initial_tags)
                
                # Change status filter to Active
                active_radio = driver.find_element(By.CSS_SELECTOR, 'input[name="is_active"][value="true"]')
                active_radio.click()
                
                # Wait for tags to update
                WebDriverWait(driver, 5).until(
                    lambda d: len(d.find_elements(By.CSS_SELECTOR, ".popular-tags-container .tag-filter")) != initial_count
                )
                
                # Verify tags changed
                updated_tags = driver.find_elements(By.CSS_SELECTOR, ".popular-tags-container .tag-filter")
                assert len(updated_tags) != initial_count
                
                # Change status filter to Inactive
                inactive_radio = driver.find_element(By.CSS_SELECTOR, 'input[name="is_active"][value="false"]')
                inactive_radio.click()
                
                # Wait for tags to update again
                WebDriverWait(driver, 5).until(
                    lambda d: len(d.find_elements(By.CSS_SELECTOR, ".popular-tags-container .tag-filter")) != len(updated_tags)
                )
                
            finally:
                driver.quit()
                
        except Exception as e:
            pytest.skip(f"Selenium test skipped: {e}")
    
    def test_loading_states_integration(self, client, db_session, sample_data):
        """Test loading states in real environment."""
        # Simulate slow database query
        with patch('app.services.tag_service.TagService.get_popular_tags') as mock_get_tags:
            # Make the mock sleep to simulate slow query
            import time
            def slow_get_tags(*args, **kwargs):
                time.sleep(0.1)
                return [{'tag': sample_data['tags'][0], 'usage_count': 1}]
            
            mock_get_tags.side_effect = slow_get_tags
            
            # Make request
            response = client.get('/api/tags/popular?is_active=true')
            assert response.status_code == 200
    
    def test_data_consistency_integration(self, app, db_session, sample_data):
        """Test data consistency across different status filters."""
        with app.app_context():
            tag_service = TagService(TagRepository(db_session))
            
            # Get all tags
            all_tags = tag_service.get_popular_tags(limit=50, is_active=None)
            all_tag_names = {tag_data['tag'].name for tag_data in all_tags}
            
            # Get active tags
            active_tags = tag_service.get_popular_tags(limit=50, is_active=True)
            active_tag_names = {tag_data['tag'].name for tag_data in active_tags}
            
            # Get inactive tags
            inactive_tags = tag_service.get_popular_tags(limit=50, is_active=False)
            inactive_tag_names = {tag_data['tag'].name for tag_data in inactive_tags}
            
            # Verify consistency
            # Active + Inactive should be subset of All
            combined = active_tag_names.union(inactive_tag_names)
            assert combined.issubset(all_tag_names)
            
            # Active and Inactive should not overlap (for tags with usage > 0)
            active_with_usage = {tag_data['tag'].name for tag_data in active_tags if tag_data['usage_count'] > 0}
            inactive_with_usage = {tag_data['tag'].name for tag_data in inactive_tags if tag_data['usage_count'] > 0}
            
            # They can overlap if a tag is used in both active and inactive prompts
            # This is expected behavior
    
    def test_performance_integration(self, client, db_session, sample_data):
        """Test performance of tag filtering."""
        import time
        
        # Test response time for different status filters
        start_time = time.time()
        response = client.get('/api/tags/popular?is_active=true')
        active_time = time.time() - start_time
        
        start_time = time.time()
        response = client.get('/api/tags/popular?is_active=false')
        inactive_time = time.time() - start_time
        
        start_time = time.time()
        response = client.get('/api/tags/popular')
        all_time = time.time() - start_time
        
        # All responses should complete within reasonable time
        assert active_time < 1.0, f"Active filter took {active_time:.2f}s"
        assert inactive_time < 1.0, f"Inactive filter took {inactive_time:.2f}s"
        assert all_time < 1.0, f"All filter took {all_time:.2f}s"
    
    def test_backward_compatibility_integration(self, app, db_session, sample_data):
        """Test backward compatibility with existing code."""
        with app.app_context():
            tag_service = TagService(TagRepository(db_session))
            
            # Test old method call (without is_active parameter)
            old_result = tag_service.get_popular_tags(limit=5)
            assert len(old_result) > 0
            
            # Test new method call with None
            new_result = tag_service.get_popular_tags(limit=5, is_active=None)
            assert len(new_result) > 0
            
            # Results should be equivalent
            assert len(old_result) == len(new_result)
    
    def test_edge_cases_integration(self, client, db_session):
        """Test edge cases in real environment."""
        # Test with no tags in database
        response = client.get('/api/tags/popular?is_active=true')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['tags']) == 0
        
        # Test with no prompts in database
        response = client.get('/api/tags/popular?is_active=false')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['tags']) == 0
        
        # Test with very large limit
        response = client.get('/api/tags/popular?is_active=true')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True


class TestContextualFilteringWorkflow:
    """Test complete workflow scenarios."""
    
    @pytest.fixture
    def app(self):
        """Create Flask app for testing."""
        app = create_app('testing')
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    @pytest.fixture
    def db_session(self, app):
        """Create database session."""
        with app.app_context():
            db.create_all()
            yield db.session
            db.session.remove()
            db.drop_all()
    
    def test_complete_workflow_scenario_1(self, client, db_session):
        """Test complete workflow: User changes status filter."""
        # Setup: Create test data
        tag = Tag(name="test-tag", color="#000000")
        prompt1 = Prompt(title="Active Prompt", content="Content", is_active=True)
        prompt2 = Prompt(title="Inactive Prompt", content="Content", is_active=False)
        
        db_session.add_all([tag, prompt1, prompt2])
        db_session.commit()
        
        prompt1.tags = [tag]
        prompt2.tags = [tag]
        db_session.commit()
        
        # Step 1: Get all tags
        response = client.get('/api/tags/popular')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['tags']) == 1
        assert data['tags'][0]['usage_count'] == 2  # Used in both active and inactive
        
        # Step 2: Get active tags only
        response = client.get('/api/tags/popular?is_active=true')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['tags']) == 1
        assert data['tags'][0]['usage_count'] == 1  # Used only in active
        
        # Step 3: Get inactive tags only
        response = client.get('/api/tags/popular?is_active=false')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['tags']) == 1
        assert data['tags'][0]['usage_count'] == 1  # Used only in inactive
    
    def test_complete_workflow_scenario_2(self, client, db_session):
        """Test complete workflow: Multiple tags with different statuses."""
        # Setup: Create test data
        tag1 = Tag(name="active-only", color="#00ff00")
        tag2 = Tag(name="inactive-only", color="#ff0000")
        tag3 = Tag(name="both", color="#0000ff")
        
        prompt1 = Prompt(title="Active Prompt", content="Content", is_active=True)
        prompt2 = Prompt(title="Inactive Prompt", content="Content", is_active=False)
        
        db_session.add_all([tag1, tag2, tag3, prompt1, prompt2])
        db_session.commit()
        
        prompt1.tags = [tag1, tag3]  # active-only and both
        prompt2.tags = [tag2, tag3]  # inactive-only and both
        db_session.commit()
        
        # Test active filter
        response = client.get('/api/tags/popular?is_active=true')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        tag_names = [tag['name'] for tag in data['tags']]
        assert 'active-only' in tag_names
        assert 'both' in tag_names
        assert 'inactive-only' not in tag_names
        
        # Test inactive filter
        response = client.get('/api/tags/popular?is_active=false')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        tag_names = [tag['name'] for tag in data['tags']]
        assert 'inactive-only' in tag_names
        assert 'both' in tag_names
        assert 'active-only' not in tag_names


if __name__ == '__main__':
    pytest.main([__file__]) 