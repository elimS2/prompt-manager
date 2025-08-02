"""
Integration tests for API endpoints.
"""
import pytest
import json
from app.models import Prompt, Tag


class TestPromptAPI:
    """Test prompt-related API endpoints."""
    
    def test_get_prompts(self, client, sample_prompts):
        """Test GET /api/prompts endpoint."""
        response = client.get('/api/prompts')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'prompts' in data
        assert 'pagination' in data
        assert len(data['prompts']) == 5
        assert data['pagination']['total'] == 5
    
    def test_get_prompts_with_pagination(self, client, sample_prompts):
        """Test pagination in prompts list."""
        response = client.get('/api/prompts?page=2&per_page=2')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['prompts']) == 2
        assert data['pagination']['page'] == 2
        assert data['pagination']['per_page'] == 2
        assert data['pagination']['has_prev'] is True
    
    def test_get_prompts_with_search(self, client, db_session):
        """Test search functionality in prompts list."""
        # Create searchable prompts
        Prompt(title="Python Guide", content="Learn Python").save()
        Prompt(title="JavaScript Tutorial", content="Learn JS").save()
        
        response = client.get('/api/prompts?search=Python')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['prompts']) == 1
        assert data['prompts'][0]['title'] == "Python Guide"
    
    def test_get_single_prompt(self, client, sample_prompt):
        """Test GET /api/prompts/{id} endpoint."""
        response = client.get(f'/api/prompts/{sample_prompt.id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['prompt']['id'] == sample_prompt.id
        assert data['prompt']['title'] == sample_prompt.title
        
        # Non-existent prompt
        response = client.get('/api/prompts/9999')
        assert response.status_code == 404
    
    def test_create_prompt(self, client, db_session):
        """Test POST /api/prompts endpoint."""
        payload = {
            'title': 'New Prompt',
            'content': 'New content',
            'description': 'New description',
            'tags': ['python', 'api']
        }
        
        response = client.post(
            '/api/prompts',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 201
        
        data = json.loads(response.data)
        assert data['prompt']['title'] == 'New Prompt'
        assert len(data['prompt']['tags']) == 2
        
        # Verify in database
        prompt = Prompt.query.get(data['prompt']['id'])
        assert prompt is not None
        assert prompt.title == 'New Prompt'
    
    def test_create_prompt_validation(self, client):
        """Test validation in prompt creation."""
        # Missing required fields
        response = client.post(
            '/api/prompts',
            data=json.dumps({'title': ''}),
            content_type='application/json'
        )
        assert response.status_code == 400
        assert 'error' in json.loads(response.data)
        
        # Invalid content type
        response = client.post(
            '/api/prompts',
            data='not json',
            content_type='text/plain'
        )
        assert response.status_code == 400
    
    def test_update_prompt(self, client, sample_prompt):
        """Test PUT /api/prompts/{id} endpoint."""
        payload = {
            'title': 'Updated Title',
            'content': 'Updated content'
        }
        
        response = client.put(
            f'/api/prompts/{sample_prompt.id}',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['prompt']['title'] == 'Updated Title'
        
        # Verify in database
        prompt = Prompt.query.get(sample_prompt.id)
        assert prompt.title == 'Updated Title'
    
    def test_delete_prompt(self, client, sample_prompt):
        """Test DELETE /api/prompts/{id} endpoint."""
        # Soft delete (default)
        response = client.delete(f'/api/prompts/{sample_prompt.id}')
        assert response.status_code == 200
        
        # Verify soft deleted
        prompt = Prompt.query.get(sample_prompt.id)
        assert prompt is not None
        assert prompt.is_active is False
        
        # Hard delete
        new_prompt = Prompt(title="To Delete", content="Content").save()
        response = client.delete(f'/api/prompts/{new_prompt.id}?hard=true')
        assert response.status_code == 200
        
        # Verify hard deleted
        assert Prompt.query.get(new_prompt.id) is None
    
    def test_restore_prompt(self, client, sample_prompt):
        """Test POST /api/prompts/{id}/restore endpoint."""
        # First soft delete
        sample_prompt.is_active = False
        sample_prompt.save()
        
        # Restore
        response = client.post(f'/api/prompts/{sample_prompt.id}/restore')
        assert response.status_code == 200
        
        # Verify restored
        prompt = Prompt.query.get(sample_prompt.id)
        assert prompt.is_active is True
    
    def test_duplicate_prompt(self, client, sample_prompt):
        """Test POST /api/prompts/{id}/duplicate endpoint."""
        payload = {'title': 'Duplicated Prompt'}
        
        response = client.post(
            f'/api/prompts/{sample_prompt.id}/duplicate',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 201
        
        data = json.loads(response.data)
        assert data['prompt']['title'] == 'Duplicated Prompt'
        assert data['prompt']['content'] == sample_prompt.content
        assert data['prompt']['id'] != sample_prompt.id
    
    def test_merge_prompts(self, client, sample_prompts):
        """Test POST /api/prompts/merge endpoint."""
        payload = {
            'prompt_ids': [sample_prompts[0].id, sample_prompts[1].id],
            'strategy': 'simple',
            'options': {'include_title': True}
        }
        
        response = client.post(
            '/api/prompts/merge',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'merged_content' in data
        assert data['metadata']['prompt_count'] == 2
        assert sample_prompts[0].title in data['merged_content']
    
    def test_search_prompts(self, client, db_session):
        """Test GET /api/prompts/search endpoint."""
        # Create searchable prompts
        Prompt(title="Python Guide", content="Learn Python").save()
        Prompt(title="JS Tutorial", content="JavaScript basics").save()
        
        response = client.get('/api/prompts/search?q=Python')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['count'] == 1
        assert data['prompts'][0]['title'] == "Python Guide"
        
        # Missing query parameter
        response = client.get('/api/prompts/search')
        assert response.status_code == 400


class TestTagAPI:
    """Test tag-related API endpoints."""
    
    def test_get_tags(self, client, sample_tags):
        """Test GET /api/tags endpoint."""
        response = client.get('/api/tags')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['tags']) == 5
    
    def test_get_popular_tags(self, client, sample_tags, sample_prompts):
        """Test GET /api/tags?popular=true endpoint."""
        # Add tags to prompts
        sample_prompts[0].tags.append(sample_tags[0])
        sample_prompts[1].tags.append(sample_tags[0])
        sample_prompts[2].tags.append(sample_tags[1])
        sample_prompts[0].save()
        
        response = client.get('/api/tags?popular=true&limit=3')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['tags']) <= 3
        assert data['tags'][0]['usage_count'] >= data['tags'][1]['usage_count']
    
    def test_get_single_tag(self, client, sample_tag):
        """Test GET /api/tags/{id} endpoint."""
        response = client.get(f'/api/tags/{sample_tag.id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['tag']['id'] == sample_tag.id
        assert data['tag']['name'] == sample_tag.name
    
    def test_create_tag(self, client):
        """Test POST /api/tags endpoint."""
        payload = {
            'name': 'New Tag',
            'color': '#FF5733'
        }
        
        response = client.post(
            '/api/tags',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 201
        
        data = json.loads(response.data)
        assert data['tag']['name'] == 'new-tag'  # Normalized
        assert data['tag']['color'] == '#FF5733'
    
    def test_update_tag(self, client, sample_tag):
        """Test PUT /api/tags/{id} endpoint."""
        payload = {
            'name': 'Updated Tag',
            'color': '#00FF00'
        }
        
        response = client.put(
            f'/api/tags/{sample_tag.id}',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['tag']['name'] == 'updated-tag'
        assert data['tag']['color'] == '#00FF00'
    
    def test_delete_tag(self, client, sample_tag):
        """Test DELETE /api/tags/{id} endpoint."""
        response = client.delete(f'/api/tags/{sample_tag.id}')
        assert response.status_code == 200
        
        # Verify deleted
        assert Tag.query.get(sample_tag.id) is None
    
    def test_merge_tags(self, client, db_session):
        """Test POST /api/tags/merge endpoint."""
        # Create tags
        source = Tag(name="source-tag").save()
        target = Tag(name="target-tag").save()
        
        payload = {
            'source_id': source.id,
            'target_id': target.id
        }
        
        response = client.post(
            '/api/tags/merge',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code == 200
        
        # Verify merge
        assert Tag.query.get(source.id) is None
        assert Tag.query.get(target.id) is not None
    
    def test_tag_statistics(self, client, sample_tags, sample_prompts):
        """Test GET /api/tags/statistics endpoint."""
        # Add tags to prompts
        sample_prompts[0].tags.extend([sample_tags[0], sample_tags[1]])
        sample_prompts[0].save()
        
        response = client.get('/api/tags/statistics')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        stats = data['statistics']
        assert stats['total_tags'] == 5
        assert stats['used_tags'] == 2
        assert stats['unused_tags'] == 3


class TestGeneralAPI:
    """Test general API endpoints."""
    
    def test_statistics_endpoint(self, client, db_session):
        """Test GET /api/statistics endpoint."""
        # Create test data
        Prompt(title="Active", content="C1", is_active=True).save()
        Prompt(title="Inactive", content="C2", is_active=False).save()
        Tag(name="tag1").save()
        Tag(name="tag2").save()
        
        response = client.get('/api/statistics')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'prompts' in data
        assert 'tags' in data
        assert data['prompts']['total_prompts'] == 2
        assert data['tags']['total_tags'] == 2
    
    def test_health_check(self, client):
        """Test GET /api/health endpoint."""
        response = client.get('/api/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'version' in data
    
    def test_error_handling(self, client):
        """Test API error handling."""
        # 404 error
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
        assert 'error' in json.loads(response.data)
        
        # Invalid JSON
        response = client.post(
            '/api/prompts',
            data='invalid json',
            content_type='application/json'
        )
        assert response.status_code == 400