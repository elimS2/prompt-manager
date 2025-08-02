"""
Testing configuration.
"""
import os
from .base import BaseConfig


class TestingConfig(BaseConfig):
    """Testing environment specific configuration."""
    
    DEBUG = False
    TESTING = True
    
    # Use in-memory SQLite for tests
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Faster password hashing for tests
    BCRYPT_LOG_ROUNDS = 4
    
    @staticmethod
    def init_app(app):
        """Initialize application for testing."""
        BaseConfig.init_app(app)