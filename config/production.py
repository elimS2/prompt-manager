"""
Production configuration.
"""
import os
import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
from .base import BaseConfig


class ProductionConfig(BaseConfig):
    """Production environment specific configuration."""
    
    DEBUG = False
    TESTING = False
    
    # Production database should be set via DATABASE_URL env var
    # Example: postgresql://user:password@localhost/dbname
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://prompt_user:prompt_pass@localhost/prompt_manager'
    )
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Strict"
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # Performance
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_RECORD_QUERIES = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 20
    }
    
    # URL building behind reverse proxy
    PREFERRED_URL_SCHEME = 'https'
    
    # Content Security Policy
    CSP = {
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline' 'unsafe-eval' cdn.jsdelivr.net",
        'style-src': "'self' 'unsafe-inline' cdn.jsdelivr.net",
        'font-src': "'self' cdn.jsdelivr.net",
        'img-src': "'self' data: https:",
    }
    
    # Rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"
    
    # Caching
    CACHE_TYPE = "redis"
    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Email error notifications (optional)
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    # Use ADMINS from environment (inherits parsing from BaseConfig by default),
    # do not hardcode here to avoid overriding .env
    _ADMINS_ENV = os.getenv('ADMINS', '')
    ADMINS = [email.strip().lower() for email in _ADMINS_ENV.split(',') if email.strip()]
    
    @staticmethod
    def init_app(app):
        """Initialize application for production."""
        BaseConfig.init_app(app)
        
        # Configure logging
        if not app.debug:
            # Create logs directory if it doesn't exist
            log_dir = os.path.join(os.path.dirname(app.root_path), 'logs')
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Rotating file handler
            file_handler = RotatingFileHandler(
                os.path.join(log_dir, 'prompt_manager.log'),
                maxBytes=10485760,  # 10MB
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            
            # Email handler for errors (if mail server configured)
            if app.config.get('MAIL_SERVER'):
                auth = None
                if app.config.get('MAIL_USERNAME') or app.config.get('MAIL_PASSWORD'):
                    auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
                secure = None
                if app.config.get('MAIL_USE_TLS'):
                    secure = ()
                mail_handler = SMTPHandler(
                    mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                    fromaddr=f"no-reply@{app.config['MAIL_SERVER']}",
                    toaddrs=app.config['ADMINS'],
                    subject='Prompt Manager Application Error',
                    credentials=auth,
                    secure=secure
                )
                mail_handler.setLevel(logging.ERROR)
                app.logger.addHandler(mail_handler)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('Prompt Manager startup in production mode')