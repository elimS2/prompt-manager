"""
Base configuration for the Prompt Manager application.
"""
import os
from pathlib import Path


class BaseConfig:
    """Base configuration class with common settings."""
    
    # Application settings
    APP_NAME = os.getenv("APP_NAME", "Prompt Manager")
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Database settings
    BASE_DIR = Path(__file__).parent.parent
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR.as_posix()}/prompt_manager.db"
    )
    
    # Security settings
    CSRF_ENABLED = os.getenv("CSRF_ENABLED", "True").lower() == "true"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "False").lower() == "true"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    
    # Pagination
    ITEMS_PER_PAGE = int(os.getenv("ITEMS_PER_PAGE", 20))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "app.log")
    
    @staticmethod
    def init_app(app):
        """Initialize application with this config."""
        pass