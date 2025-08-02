#!/usr/bin/env python3
"""
Initialize database and run the application.
"""
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.models import db

def init_and_run():
    """Initialize database and run the application."""
    # Create app
    app = create_app('development')
    
    with app.app_context():
        # Print database info
        print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("Database tables created!")
        
        # Check if data exists
        from app.models import Prompt
        count = Prompt.query.count()
        print(f"Current prompts in database: {count}")
        
        if count == 0:
            print("No data found. Running seed script...")
            from scripts.seed_data import seed_database
            seed_database()
    
    # Run the application
    print("\nStarting application...")
    app.run(
        host=os.getenv("APP_HOST", "127.0.0.1"),
        port=int(os.getenv("APP_PORT", 5001)),
        debug=os.getenv("FLASK_DEBUG", "True").lower() == "true"
    )

if __name__ == "__main__":
    init_and_run()