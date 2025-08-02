"""
Unit tests for repository classes.
"""
import pytest
from datetime import datetime, timedelta
from app.repositories import PromptRepository, TagRepository
from app.models import Prompt, Tag


class TestBaseRepository:
    """Test base repository functionality through concrete implementations."""
    
    def test_get_all_with_filters(self, db_session, sample_prompts):
        """Test get_all with filtering."""
        repo = PromptRepository()
        
        # No filters
        all_prompts = repo.get_all()
        assert len(all_prompts) == 5
        
        # With filter
        prompts = repo.get_all(title="Test Prompt 1")
        assert len(prompts) == 1
        assert prompts[0].title == "Test Prompt 1"
    
    def test_get_paginated(self, db_session, sample_prompts):
        """Test pagination functionality."""
        repo = PromptRepository()
        
        # First page
        result = repo.get_paginated(page=1, per_page=2)
        assert result['page'] == 1
        assert result['per_page'] == 2
        assert len(result['items']) == 2
        assert result['total'] == 5
        assert result['total_pages'] == 3
        assert result['has_next'] is True
        assert result['has_prev'] is False
        
        # Last page
        result = repo.get_paginated(page=3, per_page=2)
        assert len(result['items']) == 1
        assert result['has_next'] is False
        assert result['has_prev'] is True
    
    def test_create(self, db_session):
        """Test create method."""
        repo = PromptRepository()
        
        prompt = repo.create(
            title="New Prompt",
            content="New Content",
            is_active=True
        )
        
        assert prompt.id is not None
        assert prompt.title == "New Prompt"
        assert Prompt.query.get(prompt.id) is not None
    
    def test_update(self, db_session, sample_prompt):
        """Test update method."""
        repo = PromptRepository()
        original_title = sample_prompt.title
        
        updated = repo.update(
            sample_prompt.id,
            title="Updated Title",
            content="Updated Content"
        )
        
        assert updated is not None
        assert updated.title == "Updated Title"
        assert updated.content == "Updated Content"
        
        # Non-existent ID
        result = repo.update(9999, title="Test")
        assert result is None
    
    def test_delete(self, db_session, sample_prompt):
        """Test delete method."""
        repo = PromptRepository()
        prompt_id = sample_prompt.id
        
        # Delete existing
        assert repo.delete(prompt_id) is True
        assert Prompt.query.get(prompt_id) is None
        
        # Delete non-existent
        assert repo.delete(9999) is False
    
    def test_bulk_create(self, db_session):
        """Test bulk create method."""
        repo = PromptRepository()
        
        items = [
            {"title": f"Bulk {i}", "content": f"Content {i}"}
            for i in range(3)
        ]
        
        created = repo.bulk_create(items)
        assert len(created) == 3
        
        # Verify all were created
        for prompt in created:
            assert Prompt.query.get(prompt.id) is not None
    
    def test_exists(self, db_session, sample_prompt):
        """Test exists method."""
        repo = PromptRepository()
        
        assert repo.exists(title="Test Prompt") is True
        assert repo.exists(title="Non-existent") is False
        assert repo.exists(id=sample_prompt.id) is True
    
    def test_count(self, db_session, sample_prompts):
        """Test count method."""
        repo = PromptRepository()
        
        assert repo.count() == 5
        assert repo.count(is_active=True) == 5
        assert repo.count(title="Test Prompt 1") == 1
    
    def test_find_one(self, db_session, sample_prompt):
        """Test find_one method."""
        repo = PromptRepository()
        
        found = repo.find_one(title="Test Prompt")
        assert found is not None
        assert found.id == sample_prompt.id
        
        # Non-existent
        assert repo.find_one(title="Non-existent") is None


class TestPromptRepository:
    """Test PromptRepository specific methods."""
    
    def test_get_all_active(self, db_session):
        """Test getting only active prompts."""
        repo = PromptRepository()
        
        # Create mix of active and inactive
        active1 = repo.create(title="Active 1", content="C1", is_active=True)
        active2 = repo.create(title="Active 2", content="C2", is_active=True)
        inactive = repo.create(title="Inactive", content="C3", is_active=False)
        
        active_prompts = repo.get_all_active()
        assert len(active_prompts) == 2
        assert all(p.is_active for p in active_prompts)
    
    def test_get_by_ids(self, db_session, sample_prompts):
        """Test getting prompts by multiple IDs."""
        repo = PromptRepository()
        ids = [sample_prompts[0].id, sample_prompts[2].id, sample_prompts[4].id]
        
        prompts = repo.get_by_ids(ids)
        assert len(prompts) == 3
        assert all(p.id in ids for p in prompts)
        
        # Empty list
        assert repo.get_by_ids([]) == []
        
        # Non-existent IDs
        prompts = repo.get_by_ids([9999, 8888])
        assert len(prompts) == 0
    
    def test_search(self, db_session):
        """Test search functionality."""
        repo = PromptRepository()
        
        # Create searchable prompts
        p1 = repo.create(
            title="Python Guide",
            content="Learn Python",
            description="Python tutorial",
            is_active=True
        )
        p2 = repo.create(
            title="JS Tutorial",
            content="JavaScript basics",
            is_active=False
        )
        
        # Search active only (default)
        results = repo.search("Python")
        assert len(results) == 1
        
        # Include inactive
        results = repo.search("tutorial", include_inactive=True)
        assert len(results) == 2
        
        # Empty query
        assert repo.search("") == []
    
    def test_get_by_tags(self, db_session, sample_prompts, sample_tags):
        """Test getting prompts by tags."""
        repo = PromptRepository()
        
        # Assign tags to prompts
        sample_prompts[0].tags.extend([sample_tags[0], sample_tags[1]])
        sample_prompts[1].tags.append(sample_tags[0])
        sample_prompts[2].tags.append(sample_tags[1])
        db_session.commit()
        
        # Get prompts with ANY of the tags
        tag_ids = [sample_tags[0].id]
        prompts = repo.get_by_tags(tag_ids, match_all=False)
        assert len(prompts) == 2  # prompts[0] and prompts[1]
        
        # Get prompts with ALL tags
        tag_ids = [sample_tags[0].id, sample_tags[1].id]
        prompts = repo.get_by_tags(tag_ids, match_all=True)
        assert len(prompts) == 1  # only prompts[0] has both
        
        # Empty tag list
        assert repo.get_by_tags([]) == []
    
    def test_get_by_tag_names(self, db_session, sample_prompts, sample_tags):
        """Test getting prompts by tag names."""
        repo = PromptRepository()
        
        # Assign tags
        sample_prompts[0].tags.append(sample_tags[0])  # python
        sample_prompts[1].tags.append(sample_tags[1])  # javascript
        db_session.commit()
        
        # Get by tag names
        prompts = repo.get_by_tag_names(["python"])
        assert len(prompts) == 1
        

    
    def test_get_recent(self, db_session):
        """Test getting recent prompts."""
        repo = PromptRepository()
        
        # Create prompts with different timestamps
        old_prompt = Prompt(
            title="Old",
            content="Old content",
            created_at=datetime.utcnow() - timedelta(days=7)
        )
        new_prompt = Prompt(
            title="New",
            content="New content",
            created_at=datetime.utcnow()
        )
        db_session.add_all([old_prompt, new_prompt])
        db_session.commit()
        
        recent = repo.get_recent(limit=5)
        assert len(recent) >= 2
        assert recent[0].title == "New"  # Most recent first
    
    def test_soft_delete_and_restore(self, db_session, sample_prompt):
        """Test soft delete and restore functionality."""
        repo = PromptRepository()
        
        # Soft delete
        assert sample_prompt.is_active is True
        assert repo.soft_delete(sample_prompt.id) is True
        
        # Verify soft deleted
        prompt = repo.get_by_id(sample_prompt.id)
        assert prompt is not None
        assert prompt.is_active is False
        
        # Restore
        assert repo.restore(sample_prompt.id) is True
        prompt = repo.get_by_id(sample_prompt.id)
        assert prompt.is_active is True
        
        # Non-existent ID
        assert repo.soft_delete(9999) is False
        assert repo.restore(9999) is False
    
    def test_get_with_filters(self, db_session, sample_prompts, sample_tags):
        """Test complex filtering."""
        repo = PromptRepository()
        
        # Add tags to some prompts
        sample_prompts[0].tags.append(sample_tags[0])
        sample_prompts[1].tags.append(sample_tags[0])
        db_session.commit()
        
        # Multiple filters
        filters = {
            'search': 'Test',
            'tags': [sample_tags[0].id],
            'is_active': True
        }
        
        results = repo.get_with_filters(filters)
        assert len(results) == 2  # Only prompts with the tag


class TestTagRepository:
    """Test TagRepository specific methods."""
    
    def test_get_by_name(self, db_session, sample_tag):
        """Test getting tag by name."""
        repo = TagRepository()
        
        # Exact match
        found = repo.get_by_name("test-tag")
        assert found is not None
        assert found.id == sample_tag.id
        
        # Case insensitive
        found = repo.get_by_name("TEST-TAG")
        assert found is not None
        
        # Non-normalized input
        found = repo.get_by_name("Test Tag")
        assert found is not None
    
    def test_get_or_create(self, db_session):
        """Test get or create functionality."""
        repo = TagRepository()
        
        # Create new
        tag1 = repo.get_or_create("new-tag", color="#FF0000")
        assert tag1 is not None
        assert tag1.name == "new-tag"
        assert tag1.color == "#FF0000"
        
        # Get existing
        tag2 = repo.get_or_create("new-tag", color="#00FF00")
        assert tag2.id == tag1.id
        assert tag2.color == "#FF0000"  # Original color preserved
    
    def test_get_popular_tags(self, db_session):
        """Test getting popular tags."""
        repo = TagRepository()
        prompt_repo = PromptRepository()
        
        # Create tags and prompts
        tag1 = repo.create(name="popular", color="#111111")
        tag2 = repo.create(name="less-popular", color="#222222")
        tag3 = repo.create(name="unused", color="#333333")
        
        # Create prompts with tags
        for i in range(5):
            p = prompt_repo.create(title=f"P{i}", content="Content")
            p.tags.append(tag1)
            if i < 2:
                p.tags.append(tag2)
        db_session.commit()
        
        # Get popular tags
        popular = repo.get_popular_tags(limit=3)
        assert len(popular) == 3
        assert popular[0]['tag'].name == "popular"
        assert popular[0]['usage_count'] == 5
        assert popular[1]['tag'].name == "less-popular"
        assert popular[1]['usage_count'] == 2
        assert popular[2]['tag'].name == "unused"
        assert popular[2]['usage_count'] == 0
    
    def test_get_unused_tags(self, db_session, sample_tags):
        """Test getting unused tags."""
        repo = TagRepository()
        prompt_repo = PromptRepository()
        
        # Create a prompt with one tag
        prompt = prompt_repo.create(title="Test", content="Content")
        prompt.tags.append(sample_tags[0])
        db_session.commit()
        
        # Get unused tags
        unused = repo.get_unused_tags()
        assert len(unused) == 4  # 5 total - 1 used
        assert all(tag.id != sample_tags[0].id for tag in unused)
    
    def test_search_tags(self, db_session, sample_tags):
        """Test tag search."""
        repo = TagRepository()
        
        # Search by partial name
        results = repo.search_tags("py")
        assert len(results) == 1
        assert results[0].name == "python"
        
        # Case insensitive
        results = repo.search_tags("JAVA")
        assert len(results) == 1
        assert results[0].name == "javascript"
        
        # Empty query
        assert repo.search_tags("") == []
    
    def test_bulk_get_or_create(self, db_session):
        """Test bulk get or create."""
        repo = TagRepository()
        
        # Mix of new and existing
        tag_names = ["python", "new-tag-1", "new-tag-2", "javascript"]
        
        # Create one existing tag
        existing = repo.create(name="python", color="#0000FF")
        
        # Bulk operation
        tags = repo.bulk_get_or_create(tag_names)
        assert len(tags) == 4
        
        # Verify existing tag was reused
        python_tags = [t for t in tags if t.name == "python"]
        assert len(python_tags) == 1
        assert python_tags[0].id == existing.id
        
        # Empty list
        assert repo.bulk_get_or_create([]) == []
    
    def test_rename_tag(self, db_session, sample_tag):
        """Test renaming a tag."""
        repo = TagRepository()
        
        # Successful rename
        renamed = repo.rename_tag(sample_tag.id, "renamed-tag")
        assert renamed is not None
        assert renamed.name == "renamed-tag"
        
        # Try to rename to existing name
        other_tag = repo.create(name="other-tag")
        
        with pytest.raises(ValueError) as exc:
            repo.rename_tag(sample_tag.id, "other-tag")
        assert "already exists" in str(exc.value)
        
        # Non-existent tag
        assert repo.rename_tag(9999, "new-name") is None