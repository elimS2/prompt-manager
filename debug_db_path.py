#!/usr/bin/env python3
"""
Debug database path configuration.
"""
from app import create_app
from pathlib import Path

app = create_app('development')

with app.app_context():
    print("Database configuration:")
    print(f"SQLALCHEMY_DATABASE_URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    # Extract path from URI
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    if db_uri.startswith('sqlite:///'):
        db_path = db_uri.replace('sqlite:///', '')
        print(f"Database path: {db_path}")
        
        # Check if file exists
        if Path(db_path).exists():
            print(f"✅ Database file exists at: {db_path}")
        else:
            print(f"❌ Database file NOT found at: {db_path}")
            
        # Check current directory
        print(f"\nCurrent working directory: {Path.cwd()}")
        print(f"Expected database location: {Path.cwd() / 'prompt_manager.db'}")