"""
Logging configuration and utilities.
"""
import os
import logging
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from flask import Flask, request, g, has_request_context
import time


class RequestFormatter(logging.Formatter):
    """Custom formatter that includes request information."""
    
    def format(self, record):
        """Format log record with request context."""
        if has_request_context():
            record.request_id = getattr(g, 'request_id', '-')
            record.url = request.url
            record.remote_addr = request.remote_addr
            record.method = request.method
        else:
            record.request_id = '-'
            record.url = '-'
            record.remote_addr = '-'
            record.method = '-'
            
        return super().format(record)


def setup_logging(app: Flask) -> None:
    """Configure logging for the application.
    
    Args:
        app: Flask application instance
    """
    # Remove default Flask handler
    app.logger.handlers = []
    
    # Set log level from environment or config
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper())
    app.logger.setLevel(log_level)
    
    # Create formatters
    detailed_formatter = RequestFormatter(
        '[%(asctime)s] %(levelname)s [%(request_id)s] %(remote_addr)s - %(method)s %(url)s\n'
        '%(message)s\n'
        'File: %(pathname)s:%(lineno)d\n'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler (always active)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(simple_formatter)
    app.logger.addHandler(console_handler)
    
    # File handlers (only in production/staging)
    if not app.debug and not app.testing:
        # Create logs directory
        log_dir = app.config.get('LOG_DIR', 'logs')
        if not os.path.isabs(log_dir):
            log_dir = os.path.join(os.path.dirname(app.root_path), log_dir)
        
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # General application log (rotating by size)
        app_log_file = os.path.join(log_dir, 'app.log')
        app_file_handler = RotatingFileHandler(
            app_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10
        )
        app_file_handler.setFormatter(detailed_formatter)
        app_file_handler.setLevel(logging.INFO)
        app.logger.addHandler(app_file_handler)
        
        # Error log (rotating daily)
        error_log_file = os.path.join(log_dir, 'error.log')
        error_file_handler = TimedRotatingFileHandler(
            error_log_file,
            when='midnight',
            interval=1,
            backupCount=30
        )
        error_file_handler.setFormatter(detailed_formatter)
        error_file_handler.setLevel(logging.ERROR)
        app.logger.addHandler(error_file_handler)
        
        # Access log (rotating daily)
        access_log_file = os.path.join(log_dir, 'access.log')
        access_logger = logging.getLogger('access')
        access_handler = TimedRotatingFileHandler(
            access_log_file,
            when='midnight',
            interval=1,
            backupCount=30
        )
        access_handler.setFormatter(logging.Formatter(
            '%(remote_addr)s - [%(asctime)s] "%(method)s %(url)s" %(status_code)s %(response_size)s'
        ))
        access_logger.addHandler(access_handler)
        access_logger.setLevel(logging.INFO)
    
    app.logger.info(f'Logging configured for {app.config.get("ENV", "development")} environment')


def log_request(response):
    """Log request details for access logging.
    
    Args:
        response: Flask response object
        
    Returns:
        response: Unmodified response object
    """
    if request.path.startswith('/static'):
        return response
        
    access_logger = logging.getLogger('access')
    
    # Create log record
    log_data = {
        'remote_addr': request.remote_addr,
        'method': request.method,
        'url': request.url,
        'status_code': response.status_code,
        'response_size': response.content_length or 0,
        'asctime': time.strftime('%d/%b/%Y:%H:%M:%S %z')
    }
    
    # Log based on status code
    if response.status_code >= 500:
        access_logger.error('%(remote_addr)s - [%(asctime)s] "%(method)s %(url)s" %(status_code)s %(response_size)s', log_data)
    elif response.status_code >= 400:
        access_logger.warning('%(remote_addr)s - [%(asctime)s] "%(method)s %(url)s" %(status_code)s %(response_size)s', log_data)
    else:
        access_logger.info('%(remote_addr)s - [%(asctime)s] "%(method)s %(url)s" %(status_code)s %(response_size)s', log_data)
    
    return response


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name.
    
    Args:
        name: Logger name, typically __name__
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)