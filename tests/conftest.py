"""
Pytest configuration and fixtures for the test suite.
"""
import pytest
import os
import tempfile
from app import create_app
from app.models import db, Prompt, Tag


@pytest.fixture(scope='session')
def app():
    """Create application for the tests."""
    # Create a temporary file for test database
    db_fd, db_path = tempfile.mkstemp()
    
    # Create app with testing configuration
    app = create_app('testing')
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False
    })
    
    # Create the database and tables
    with app.app_context():
        db.create_all()
    
    yield app
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope='function')
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create a test runner for the app's Click commands."""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def db_session(app):
    """Create a clean database session for a test."""
    with app.app_context():
        # Clean all tables
        db.session.query(Prompt).delete()
        db.session.query(Tag).delete()
        db.session.commit()
        
        yield db.session
        
        # Rollback any uncommitted transactions
        db.session.rollback()


@pytest.fixture
def sample_prompt(db_session):
    """Create a sample prompt for testing."""
    prompt = Prompt(
        title="Test Prompt",
        content="This is a test prompt content",
        description="Test description",
        is_active=True
    )
    db_session.add(prompt)
    db_session.commit()
    return prompt


@pytest.fixture
def sample_tag(db_session):
    """Create a sample tag for testing."""
    tag = Tag(name="test-tag", color="#3B82F6")
    db_session.add(tag)
    db_session.commit()
    return tag


@pytest.fixture
def sample_prompts(db_session):
    """Create multiple sample prompts for testing."""
    prompts = []
    for i in range(5):
        prompt = Prompt(
            title=f"Test Prompt {i+1}",
            content=f"Content for test prompt {i+1}",
            description=f"Description {i+1}",
            is_active=True
        )
        prompts.append(prompt)
        db_session.add(prompt)
    
    db_session.commit()
    return prompts


@pytest.fixture
def sample_tags(db_session):
    """Create multiple sample tags for testing."""
    tags = []
    tag_names = ["python", "javascript", "api", "testing", "documentation"]
    colors = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"]
    
    for name, color in zip(tag_names, colors):
        tag = Tag(name=name, color=color)
        tags.append(tag)
        db_session.add(tag)
    
    db_session.commit()
    return tags


@pytest.fixture
def auth_headers():
    """Return headers for API authentication (if needed in future)."""
    return {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }