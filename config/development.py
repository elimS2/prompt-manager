"""
Development configuration.
"""
import os
from .base import BaseConfig


class DevelopmentConfig(BaseConfig):
    """Development environment specific configuration."""
    
    DEBUG = True
    TESTING = False
    
    # Development database
    SQLALCHEMY_ECHO = True  # Log all SQL statements
    
    # Development server
    HOST = os.getenv("APP_HOST", "127.0.0.1")
    PORT = int(os.getenv("APP_PORT", 5001))
    
    @staticmethod
    def init_app(app):
        """Initialize application for development."""
        BaseConfig.init_app(app)