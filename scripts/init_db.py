"""
Script to initialize the database with tables.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models import db
from config.development import DevelopmentConfig


def init_database():
    """Initialize database with all tables."""
    # Import models to ensure they are registered with SQLAlchemy
    from app.models import Prompt, Tag
    
    # Create a minimal Flask app context
    from flask import Flask
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    
    # Initialize database with app
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("Database tables created successfully!")
        
        # Show created tables
        print("\nCreated tables:")
        for table in db.metadata.tables:
            print(f"  - {table}")


if __name__ == "__main__":
    init_database()