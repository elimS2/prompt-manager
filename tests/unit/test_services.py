"""
Unit tests for service classes.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from app.services import PromptService, TagService, MergeService
from app.models import Prompt, Tag


class TestPromptService:
    """Test PromptService business logic."""
    
    def test_create_prompt_success(self, db_session):
        """Test successful prompt creation."""
        service = PromptService()
        
        data = {
            'title': 'Test Prompt',
            'content': 'Test content',
            'description': 'Test description',
            'tags': ['python', 'testing'],
            'is_active': True
        }
        
        prompt = service.create_prompt(data)
        
        assert prompt.id is not None
        assert prompt.title == 'Test Prompt'
        assert len(prompt.tags) == 2
        assert all(tag.name in ['python', 'testing'] for tag in prompt.tags)
    
    def test_create_prompt_validation(self, db_session):
        """Test prompt creation validation."""
        service = PromptService()
        
        # Empty title
        with pytest.raises(ValueError) as exc:
            service.create_prompt({'title': '', 'content': 'Content'})
        assert "Title is required" in str(exc.value)
        
        # Empty content
        with pytest.raises(ValueError) as exc:
            service.create_prompt({'title': 'Title', 'content': ''})
        assert "Content is required" in str(exc.value)
        
        # Title too long
        with pytest.raises(ValueError) as exc:
            service.create_prompt({
                'title': 'a' * 256,
                'content': 'Content'
            })
        assert "Title must be less than 255 characters" in str(exc.value)
    
    def test_update_prompt_success(self, db_session, sample_prompt):
        """Test successful prompt update."""
        service = PromptService()
        
        data = {
            'title': 'Updated Title',
            'content': 'Updated content',
            'tags': ['new-tag']
        }
        
        updated = service.update_prompt(sample_prompt.id, data)
        
        assert updated.title == 'Updated Title'
        assert updated.content == 'Updated content'
        assert len(updated.tags) == 1
        assert updated.tags[0].name == 'new-tag'
    
    def test_update_prompt_validation(self, db_session, sample_prompt):
        """Test prompt update validation."""
        service = PromptService()
        
        # Empty title
        with pytest.raises(ValueError) as exc:
            service.update_prompt(sample_prompt.id, {'title': ''})
        assert "Title cannot be empty" in str(exc.value)
        
        # Non-existent prompt
        with pytest.raises(ValueError) as exc:
            service.update_prompt(9999, {'title': 'Test'})
        assert "Prompt with id 9999 not found" in str(exc.value)
    
    def test_delete_prompt(self, db_session, sample_prompt):
        """Test prompt deletion."""
        service = PromptService()
        
        # Soft delete (default)
        assert service.delete_prompt(sample_prompt.id) is True
        prompt = Prompt.query.get(sample_prompt.id)
        assert prompt is not None
        assert prompt.is_active is False
        
        # Hard delete
        new_prompt = Prompt(title="To Delete", content="Content").save()
        assert service.delete_prompt(new_prompt.id, soft=False) is True
        assert Prompt.query.get(new_prompt.id) is None
    
    def test_get_prompts_by_filters(self, db_session):
        """Test filtered prompt retrieval."""
        service = PromptService()
        
        # Create test data
        p1 = Prompt(title="Python Guide", content="Learn Python").save()
        p2 = Prompt(title="JS Tutorial", content="Learn JavaScript").save()
        
        tag = Tag(name="python").save()
        p1.tags.append(tag)
        db_session.commit()
        
        # Filter by search
        filters = {'search': 'Python'}
        results = service.get_prompts_by_filters(filters)
        assert len(results) == 1
        assert results[0].id == p1.id
        
        # Filter by tags
        filters = {'tags': ['python']}
        results = service.get_prompts_by_filters(filters)
        assert len(results) == 1
        
        # Pagination
        filters = {'page': 1, 'per_page': 1}
        result = service.get_prompts_by_filters(filters)
        assert 'items' in result
        assert 'total' in result
        assert result['per_page'] == 1
    
    def test_duplicate_prompt(self, db_session, sample_prompt, sample_tag):
        """Test prompt duplication."""
        service = PromptService()
        sample_prompt.tags.append(sample_tag)
        db_session.commit()
        
        # Duplicate with custom title
        duplicate = service.duplicate_prompt(sample_prompt.id, "Copy Title")
        
        assert duplicate.id != sample_prompt.id
        assert duplicate.title == "Copy Title"
        assert duplicate.content == sample_prompt.content
        assert len(duplicate.tags) == 1
        assert duplicate.tags[0].name == sample_tag.name
        
        # Duplicate with default title
        duplicate2 = service.duplicate_prompt(sample_prompt.id)
        assert duplicate2.title == f"Copy of {sample_prompt.title}"
        
        # Non-existent prompt
        with pytest.raises(ValueError):
            service.duplicate_prompt(9999)
    
    def test_get_prompt_statistics(self, db_session):
        """Test statistics calculation."""
        service = PromptService()
        
        # Create test data
        Prompt(title="Active 1", content="C1", is_active=True).save()
        Prompt(title="Active 2", content="C2", is_active=True).save()
        Prompt(title="Inactive", content="C3", is_active=False).save()
        
        stats = service.get_prompt_statistics()
        
        assert stats['total_prompts'] == 3
        assert stats['active_prompts'] == 2
        assert stats['inactive_prompts'] == 1
        assert stats['active_percentage'] == pytest.approx(66.67, 0.01)


class TestTagService:
    """Test TagService business logic."""
    
    def test_create_tag_success(self, db_session):
        """Test successful tag creation."""
        service = TagService()
        
        tag = service.create_tag("Test Tag", "#FF5733")
        
        assert tag.id is not None
        assert tag.name == "test-tag"  # Normalized
        assert tag.color == "#FF5733"
    
    def test_create_tag_validation(self, db_session):
        """Test tag creation validation."""
        service = TagService()
        
        # Empty name
        with pytest.raises(ValueError) as exc:
            service.create_tag("")
        assert "Tag name is required" in str(exc.value)
        
        # Invalid color
        with pytest.raises(ValueError) as exc:
            service.create_tag("test", "invalid-color")
        assert "Invalid color format" in str(exc.value)
        
        # Duplicate tag
        service.create_tag("duplicate")
        with pytest.raises(ValueError) as exc:
            service.create_tag("Duplicate")  # Case insensitive
        assert "already exists" in str(exc.value)
    
    def test_update_tag(self, db_session, sample_tag):
        """Test tag update."""
        service = TagService()
        
        # Update name and color
        updated = service.update_tag(
            sample_tag.id,
            name="Updated Tag",
            color="#00FF00"
        )
        
        assert updated.name == "updated-tag"
        assert updated.color == "#00FF00"
        
        # Invalid updates
        with pytest.raises(ValueError):
            service.update_tag(9999, name="Test")
        
        with pytest.raises(ValueError):
            service.update_tag(sample_tag.id, color="invalid")
    
    def test_delete_tag_with_reassignment(self, db_session):
        """Test tag deletion with prompt reassignment."""
        service = TagService()
        prompt_service = PromptService()
        
        # Create tags and prompt
        tag1 = service.create_tag("tag1")
        tag2 = service.create_tag("tag2")
        
        prompt = prompt_service.create_prompt({
            'title': 'Test',
            'content': 'Content',
            'tags': ['tag1']
        })
        
        # Delete tag1 and reassign to tag2
        assert service.delete_tag(tag1.id, reassign_to=tag2.id) is True
        
        # Verify reassignment
        db_session.refresh(prompt)
        assert len(prompt.tags) == 1
        assert prompt.tags[0].id == tag2.id
        
        # Verify tag1 is deleted
        assert Tag.query.get(tag1.id) is None
    
    def test_merge_tags(self, db_session):
        """Test tag merging."""
        service = TagService()
        
        # Create tags
        source = service.create_tag("source-tag")
        target = service.create_tag("target-tag")
        
        # Merge
        result = service.merge_tags(source.id, target.id)
        assert result.id == target.id
        
        # Source should be deleted
        assert Tag.query.get(source.id) is None
        
        # Invalid merges
        with pytest.raises(ValueError):
            service.merge_tags(target.id, target.id)  # Same tag
        
        with pytest.raises(ValueError):
            service.merge_tags(9999, target.id)  # Non-existent
    
    def test_get_tag_cloud(self, db_session):
        """Test tag cloud generation."""
        service = TagService()
        
        # Mock repository method
        mock_tags = [
            {'tag': Mock(id=1, name='popular', color='#111'), 'usage_count': 10},
            {'tag': Mock(id=2, name='medium', color='#222'), 'usage_count': 5},
            {'tag': Mock(id=3, name='rare', color='#333'), 'usage_count': 1}
        ]
        
        with patch.object(service.tag_repo, 'get_popular_tags', return_value=mock_tags):
            cloud = service.get_tag_cloud(limit=3)
        
        assert len(cloud) == 3
        assert cloud[0]['name'] == 'popular'
        assert cloud[0]['weight'] == 10.0  # Highest weight
        assert cloud[2]['weight'] == 1.0   # Lowest weight
    
    def test_cleanup_unused_tags(self, db_session):
        """Test cleanup of unused tags."""
        service = TagService()
        
        # Create unused tags
        unused1 = Tag(name="unused1").save()
        unused2 = Tag(name="unused2").save()
        used = Tag(name="used").save()
        
        # Create a prompt with one tag
        prompt = Prompt(title="Test", content="Content").save()
        prompt.tags.append(used)
        db_session.commit()
        
        # Cleanup
        deleted_count = service.cleanup_unused_tags()
        assert deleted_count == 2
        
        # Verify only unused tags were deleted
        assert Tag.query.get(unused1.id) is None
        assert Tag.query.get(unused2.id) is None
        assert Tag.query.get(used.id) is not None
    
    def test_suggest_tags(self, db_session):
        """Test tag suggestions based on content."""
        service = TagService()
        
        # Create tags
        python_tag = service.create_tag("python")
        api_tag = service.create_tag("api")
        unused_tag = service.create_tag("unused")
        
        # Test content mentioning tags
        content = "This is a Python tutorial about building APIs"
        suggestions = service.suggest_tags(content, limit=5)
        
        assert len(suggestions) == 2
        tag_names = [tag.name for tag in suggestions]
        assert "python" in tag_names
        assert "api" in tag_names
        assert "unused" not in tag_names


class TestMergeService:
    """Test MergeService functionality."""
    
    def test_merge_prompts_simple(self, db_session):
        """Test simple merge strategy."""
        service = MergeService()
        
        # Create test prompts
        p1 = Prompt(title="First", content="Content 1").save()
        p2 = Prompt(title="Second", content="Content 2").save()
        
        result = service.merge_prompts(
            [p1.id, p2.id],
            strategy='simple',
            options={'include_title': True}
        )
        
        assert "## First" in result['merged_content']
        assert "Content 1" in result['merged_content']
        assert "## Second" in result['merged_content']
        assert "Content 2" in result['merged_content']
        assert result['metadata']['prompt_count'] == 2
    
    def test_merge_prompts_with_separator(self, db_session):
        """Test merge with custom separator."""
        service = MergeService()
        
        p1 = Prompt(title="First", content="Content 1").save()
        p2 = Prompt(title="Second", content="Content 2").save()
        
        result = service.merge_prompts(
            [p1.id, p2.id],
            strategy='separator',
            options={
                'separator': '\n===\n',
                'include_title': False
            }
        )
        
        merged = result['merged_content']
        assert "Content 1\n===\nContent 2" in merged
        assert "##" not in merged  # No titles
    
    def test_merge_prompts_numbered(self, db_session):
        """Test numbered merge strategy."""
        service = MergeService()
        
        p1 = Prompt(title="First", content="Content 1").save()
        p2 = Prompt(title="Second", content="Content 2").save()
        
        result = service.merge_prompts(
            [p1.id, p2.id],
            strategy='numbered'
        )
        
        merged = result['merged_content']
        assert "1. **First**" in merged
        assert "2. **Second**" in merged
    
    def test_merge_prompts_template(self, db_session):
        """Test template merge strategy."""
        service = MergeService()
        
        p1 = Prompt(title="First", content="Content 1").save()
        p2 = Prompt(title="Second", content="Content 2").save()
        
        template = "Total: {count}\nTitles: {titles}\n\n{content_1}\n---\n{content_2}"
        
        result = service.merge_prompts(
            [p1.id, p2.id],
            strategy='template',
            options={'template': template}
        )
        
        merged = result['merged_content']
        assert "Total: 2" in merged
        assert "Titles: First, Second" in merged
        assert "Content 1\n---\nContent 2" in merged
    
    def test_merge_validation(self, db_session):
        """Test merge validation."""
        service = MergeService()
        
        # No prompts
        with pytest.raises(ValueError) as exc:
            service.merge_prompts([])
        assert "No prompt IDs provided" in str(exc.value)
        
        # Single prompt
        with pytest.raises(ValueError) as exc:
            service.merge_prompts([1])
        assert "At least 2 prompts required" in str(exc.value)
        
        # Non-existent prompts
        with pytest.raises(ValueError) as exc:
            service.merge_prompts([9999, 8888])
        assert "Prompts not found" in str(exc.value)
    
    def test_validate_merge(self, db_session):
        """Test merge validation method."""
        service = MergeService()
        
        # Create test prompts
        p1 = Prompt(title="Active", content="C1", is_active=True).save()
        p2 = Prompt(title="Inactive", content="C2", is_active=False).save()
        
        # Valid merge with warning
        validation = service.validate_merge([p1.id, p2.id])
        assert validation['valid'] is True
        assert len(validation['warnings']) == 1
        assert "inactive prompt(s)" in validation['warnings'][0]
        
        # Invalid - duplicate IDs
        validation = service.validate_merge([p1.id, p1.id])
        assert validation['valid'] is False
        assert "Duplicate prompt IDs" in validation['errors'][0]
    
    def test_merge_history(self, db_session):
        """Test merge history tracking."""
        service = MergeService()
        
        p1 = Prompt(title="First", content="Content 1").save()
        p2 = Prompt(title="Second", content="Content 2").save()
        
        # Perform merge
        service.merge_prompts([p1.id, p2.id])
        
        # Check history
        history = service.get_merge_history(limit=10)
        assert len(history) == 1
        assert history[0]['prompt_ids'] == [p1.id, p2.id]
        assert history[0]['prompt_titles'] == ["First", "Second"]