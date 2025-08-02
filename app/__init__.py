"""
Prompt Manager Application

A Flask-based prompt management system following SOLID principles and clean architecture.
"""
import time
import uuid
from flask import Flask, g, request
from flask_migrate import Migrate
from app.models import db
from config.base import BaseConfig


migrate = Migrate()


def create_app(config_name='development'):
    """
    Application factory pattern for creating Flask app instances.
    
    Args:
        config_name: Configuration name ('development', 'testing', 'production')
        
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_name == 'development':
        from config.development import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
        DevelopmentConfig.init_app(app)
    elif config_name == 'testing':
        from config.testing import TestingConfig
        app.config.from_object(TestingConfig)
        TestingConfig.init_app(app)
    elif config_name == 'production':
        from config.production import ProductionConfig
        app.config.from_object(ProductionConfig)
        ProductionConfig.init_app(app)
    else:
        app.config.from_object(BaseConfig)
        BaseConfig.init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Configure logging
    from app.utils.logging import setup_logging, log_request
    setup_logging(app)
    
    # Register middleware
    @app.before_request
    def before_request():
        """Set up request context."""
        g.request_id = str(uuid.uuid4())
        g.request_start_time = time.time()
        
        # Log request start
        app.logger.debug(f"Request started: {request.method} {request.path}")
    
    @app.after_request
    def after_request(response):
        """Process response and add headers."""
        # Add security headers
        response.headers['X-Request-ID'] = g.get('request_id', '')
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # Add CSP header in production
        if app.config.get('CSP'):
            csp = '; '.join([f"{key} {value}" for key, value in app.config['CSP'].items()])
            response.headers['Content-Security-Policy'] = csp
        
        # Log request completion
        if hasattr(g, 'request_start_time'):
            duration = time.time() - g.request_start_time
            app.logger.debug(f"Request completed in {duration:.3f}s: {response.status_code}")
        
        # Log access
        return log_request(response)
    
    # Register blueprints
    from app.controllers.prompt_controller import prompt_bp, register_filters
    from app.controllers.api_controller import api_bp
    
    app.register_blueprint(prompt_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Register template filters
    register_filters(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register CLI commands
    register_commands(app)
    
    return app


def register_error_handlers(app):
    """Register error handlers for the application."""
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors."""
        if 'api' in request.path:
            return {'error': 'Resource not found'}, 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        db.session.rollback()
        if 'api' in request.path:
            return {'error': 'Internal server error'}, 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(ValueError)
    def value_error(error):
        """Handle ValueError exceptions."""
        if 'api' in request.path:
            return {'error': str(error)}, 400
        flash(str(error), 'error')
        return redirect(request.referrer or url_for('prompt.index'))


# Import at the end to avoid circular imports
from flask import request, render_template, redirect, url_for, flash


def register_commands(app):
    """Register custom CLI commands.
    
    Args:
        app: Flask application instance
    """
    @app.cli.command()
    def init_db():
        """Initialize the database."""
        db.create_all()
        print("Database initialized!")
    
    @app.cli.command()
    def seed_db():
        """Seed the database with sample data."""
        from scripts.seed_data import seed_database
        with app.app_context():
            seed_database()
        print("Database seeded!")
    
    @app.cli.command()
    def clean_logs():
        """Clean old log files."""
        import os
        import glob
        from datetime import datetime, timedelta
        
        log_dir = app.config.get('LOG_DIR', 'logs')
        if not os.path.isabs(log_dir):
            log_dir = os.path.join(os.path.dirname(app.root_path), log_dir)
        
        if not os.path.exists(log_dir):
            print(f"Log directory {log_dir} does not exist")
            return
        
        # Delete logs older than 30 days
        cutoff_date = datetime.now() - timedelta(days=30)
        deleted_count = 0
        
        for log_file in glob.glob(os.path.join(log_dir, '*.log.*')):
            try:
                file_time = datetime.fromtimestamp(os.path.getmtime(log_file))
                if file_time < cutoff_date:
                    os.remove(log_file)
                    print(f"Deleted old log file: {log_file}")
                    deleted_count += 1
            except Exception as e:
                print(f"Error deleting {log_file}: {e}")
        
        print(f"Cleaned up {deleted_count} old log files")