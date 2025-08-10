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
    
    # Access control / Admins
    # ACCESS_POLICY defines how access is granted to new users after Google OAuth.
    # - allowlist_then_approval (default): Non-allowlisted users become pending until approved by admin.
    # - allowlist_strict: Only allowlisted or admin emails may access; others remain pending and cannot proceed.
    ACCESS_POLICY = os.getenv("ACCESS_POLICY", "allowlist_then_approval")

    # ADMINS is a comma-separated list of admin emails; they will be granted admin role upon first login.
    _ADMINS_ENV = os.getenv("ADMINS", "")
    ADMINS = [email.strip().lower() for email in _ADMINS_ENV.split(",") if email.strip()]

    # Pagination
    ITEMS_PER_PAGE = int(os.getenv("ITEMS_PER_PAGE", 20))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "app.log")

    # OAuth (Google)
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
    OAUTH_GOOGLE_REDIRECT_URI = os.getenv("OAUTH_GOOGLE_REDIRECT_URI")
    OAUTH_GOOGLE_ALLOWED_HD = os.getenv("OAUTH_GOOGLE_ALLOWED_HD")
    
    @staticmethod
    def init_app(app):
        """Initialize application with this config."""
        pass