"""
Unit tests for model classes.
"""
import pytest
from datetime import datetime
from app.models import Prompt, Tag, prompt_tags


class TestBaseModel:
    """Test base model functionality."""
    
    def test_save_method(self, db_session, sample_prompt):
        """Test the save method adds and commits the model."""
        new_prompt = Prompt(
            title="New Prompt",
            content="New content"
        )
        saved = new_prompt.save()
        
        assert saved.id is not None
        assert Prompt.query.get(saved.id) is not None
    
    def test_delete_method(self, db_session, sample_prompt):
        """Test the delete method removes the model."""
        prompt_id = sample_prompt.id
        sample_prompt.delete()
        
        assert Prompt.query.get(prompt_id) is None
    
    def test_get_by_id(self, db_session, sample_prompt):
        """Test getting model by ID."""
        found = Prompt.get_by_id(sample_prompt.id)
        assert found is not None
        assert found.id == sample_prompt.id
        
        # Test non-existent ID
        assert Prompt.get_by_id(9999) is None
    
    def test_get_all(self, db_session, sample_prompts):
        """Test getting all models."""
        all_prompts = Prompt.get_all()
        assert len(all_prompts) == 5
    
    def test_to_dict(self, db_session, sample_prompt):
        """Test model serialization to dictionary."""
        data = sample_prompt.to_dict()
        
        assert 'id' in data
        assert 'created_at' in data
        assert data['id'] == sample_prompt.id


class TestTagModel:
    """Test Tag model specific functionality."""
    
    def test_tag_creation(self, db_session):
        """Test creating a tag with normalization."""
        tag = Tag(name="Test Tag", color="#FF5733")
        tag.save()
        
        # Name should be normalized
        assert tag.name == "test-tag"
        assert tag.color == "#FF5733"
    
    def test_tag_normalization(self):
        """Test tag name normalization."""
        test_cases = [
            ("Simple Tag", "simple-tag"),
            ("UPPERCASE TAG", "uppercase-tag"),
            ("Multiple   Spaces", "multiple-spaces"),
            ("Special!@#$%Characters", "specialcharacters"),
            ("  Leading Trailing  ", "leading-trailing"),
            ("Already-Hyphenated", "already-hyphenated"),
            ("123 Numbers 456", "123-numbers-456"),
            ("", ""),
        ]
        
        for input_name, expected in test_cases:
            assert Tag.normalize_name(input_name) == expected
    
    def test_tag_validation(self, db_session):
        """Test tag validation."""
        # Valid tag
        tag = Tag(name="valid-tag", color="#3B82F6")
        errors = tag.validate()
        assert len(errors) == 0
        
        # Empty name
        tag = Tag(name="", color="#3B82F6")
        errors = tag.validate()
        assert "Tag name is required" in errors
        
        # Invalid color
        tag = Tag(name="test", color="invalid")
        errors = tag.validate()
        assert "Color must be a valid hex color" in errors
        
        # Long name
        tag = Tag(name="a" * 101, color="#3B82F6")
        errors = tag.validate()
        assert "Tag name must be less than 100 characters" in errors
    
    def test_tag_uniqueness(self, db_session, sample_tag):
        """Test tag name uniqueness validation."""
        # Try to create duplicate
        duplicate_tag = Tag(name="test-tag", color="#FF5733")
        errors = duplicate_tag.validate()
        assert "Tag 'test-tag' already exists" in errors
    
    def test_get_by_name(self, db_session, sample_tag):
        """Test getting tag by name."""
        # Exact match
        found = Tag.get_by_name("test-tag")
        assert found is not None
        assert found.id == sample_tag.id
        
        # Case insensitive
        found = Tag.get_by_name("TEST-TAG")
        assert found is not None
        
        # Non-existent
        assert Tag.get_by_name("non-existent") is None
    
    def test_to_dict(self, db_session):
        """Test tag serialization."""
        tag = Tag(name="test", color="#123456")
        tag.save()
        
        # Add some prompts to test count
        prompt1 = Prompt(title="P1", content="C1")
        prompt2 = Prompt(title="P2", content="C2")
        prompt1.tags.append(tag)
        prompt2.tags.append(tag)
        db_session.commit()
        
        data = tag.to_dict()
        assert data['name'] == "test"
        assert data['color'] == "#123456"
        assert data['prompt_count'] == 2


class TestPromptModel:
    """Test Prompt model specific functionality."""
    
    def test_prompt_creation(self, db_session):
        """Test creating a prompt."""
        prompt = Prompt(
            title="Test Title",
            content="Test Content",
            description="Test Description",
            is_active=True
        )
        prompt.save()
        
        assert prompt.id is not None
        assert prompt.created_at is not None
        assert prompt.updated_at is not None
        assert prompt.is_active is True
    
    def test_prompt_validation(self, db_session):
        """Test prompt validation."""
        # Valid prompt
        prompt = Prompt(title="Valid", content="Content")
        errors = prompt.validate()
        assert len(errors) == 0
        
        # Empty title
        prompt = Prompt(title="", content="Content")
        errors = prompt.validate()
        assert "Title is required" in errors
        
        # Empty content
        prompt = Prompt(title="Title", content="")
        errors = prompt.validate()
        assert "Content is required" in errors
        
        # Long title
        prompt = Prompt(title="a" * 256, content="Content")
        errors = prompt.validate()
        assert "Title must be less than 255 characters" in errors
    
    def test_prompt_tags_relationship(self, db_session, sample_prompt, sample_tag):
        """Test many-to-many relationship with tags."""
        # Add tag
        sample_prompt.add_tag(sample_tag)
        assert len(sample_prompt.tags) == 1
        assert sample_tag in sample_prompt.tags
        
        # Add same tag again (should not duplicate)
        sample_prompt.add_tag(sample_tag)
        assert len(sample_prompt.tags) == 1
        
        # Remove tag
        sample_prompt.remove_tag(sample_tag)
        assert len(sample_prompt.tags) == 0
    
    def test_prompt_soft_delete(self, db_session, sample_prompt):
        """Test soft delete functionality."""
        assert sample_prompt.is_active is True
        
        # Soft delete
        sample_prompt.is_active = False
        sample_prompt.save()
        
        # Should still exist in database
        found = Prompt.query.get(sample_prompt.id)
        assert found is not None
        assert found.is_active is False
    
    def test_get_active(self, db_session):
        """Test getting only active prompts."""
        # Create mix of active and inactive prompts
        active1 = Prompt(title="Active 1", content="C1", is_active=True).save()
        active2 = Prompt(title="Active 2", content="C2", is_active=True).save()
        inactive = Prompt(title="Inactive", content="C3", is_active=False).save()
        
        active_prompts = Prompt.get_active()
        assert len(active_prompts) == 2
        assert all(p.is_active for p in active_prompts)
    
    def test_search(self, db_session):
        """Test search functionality."""
        # Create prompts with searchable content
        p1 = Prompt(
            title="Python Tutorial",
            content="Learn Python programming",
            description="Basic Python guide"
        ).save()
        
        p2 = Prompt(
            title="JavaScript Guide",
            content="JavaScript for beginners",
            description="Learn JS basics"
        ).save()
        
        p3 = Prompt(
            title="API Development",
            content="Build REST APIs with Python Flask",
            description=None
        ).save()
        
        # Search by title
        results = Prompt.search("Python")
        assert len(results) == 2  # p1 and p3
        
        # Search by content
        results = Prompt.search("beginners")
        assert len(results) == 1
        assert results[0].id == p2.id
        
        # Search by description
        results = Prompt.search("guide")
        assert len(results) == 2  # p1 and p2
        
        # Case insensitive
        results = Prompt.search("PYTHON")
        assert len(results) == 2
        
        # No results
        results = Prompt.search("NonExistent")
        assert len(results) == 0
    
    def test_to_dict(self, db_session, sample_prompt, sample_tag):
        """Test prompt serialization with tags."""
        sample_prompt.add_tag(sample_tag)
        
        data = sample_prompt.to_dict()
        
        assert data['title'] == "Test Prompt"
        assert data['content'] == "This is a test prompt content"
        assert data['description'] == "Test description"
        assert data['is_active'] is True
        assert 'tags' in data
        assert len(data['tags']) == 1
        assert data['tags'][0]['name'] == "test-tag"