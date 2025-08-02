"""
WSGI entry point for production deployment.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import create_app after loading env vars
from app import create_app

# Create application instance
app = create_app(os.getenv('FLASK_ENV', 'production'))

if __name__ == "__main__":
    # This should not be run directly in production
    # Use a WSGI server like Gunicorn instead
    print("Use 'gunicorn wsgi:app' to run this in production")
    print("For development, use 'python run.py'")