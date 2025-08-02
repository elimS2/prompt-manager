"""
Script to seed the database with sample data.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models import db, Prompt, Tag
from config.development import DevelopmentConfig


SAMPLE_PROMPTS = [
    {
        'title': 'Python Code Review',
        'content': 'Please review the following Python code for best practices, potential bugs, and performance improvements. Suggest refactoring where appropriate.',
        'description': 'A prompt for requesting comprehensive Python code reviews',
        'tags': ['python', 'code-review', 'best-practices']
    },
    {
        'title': 'API Documentation',
        'content': 'Generate comprehensive API documentation for the following endpoints. Include request/response examples, error codes, and authentication requirements.',
        'description': 'Template for generating API documentation',
        'tags': ['documentation', 'api', 'technical-writing']
    },
    {
        'title': 'Unit Test Generator',
        'content': 'Create unit tests for the following function/class. Include edge cases, error handling, and mock external dependencies where needed.',
        'description': 'Prompt for generating comprehensive unit tests',
        'tags': ['testing', 'unit-tests', 'python']
    },
    {
        'title': 'SQL Query Optimization',
        'content': 'Analyze and optimize the following SQL query. Explain the optimization strategy and provide performance metrics if possible.',
        'description': 'Template for SQL query optimization requests',
        'tags': ['sql', 'optimization', 'database']
    },
    {
        'title': 'Error Message Explanation',
        'content': 'Explain the following error message in simple terms. Provide the most common causes and step-by-step solutions.',
        'description': 'Prompt for getting clear explanations of error messages',
        'tags': ['debugging', 'errors', 'troubleshooting']
    },
    {
        'title': 'Commit Message',
        'content': 'Write a clear and descriptive commit message for the following changes. Follow conventional commit format: type(scope): description. Include a brief summary of what was changed and why.',
        'description': 'Template for generating clear and descriptive commit messages',
        'tags': ['git', 'commit', 'version-control']
    }
]

TAG_COLORS = {
    'python': '#3776AB',
    'code-review': '#10B981',
    'documentation': '#F59E0B',
    'api': '#8B5CF6',
    'testing': '#EF4444',
    'sql': '#3B82F6',
    'debugging': '#EC4899',
    'git': '#F05032',
    'commit': '#10B981',
    'version-control': '#3B82F6'
}


def seed_database():
    """Seed database with sample data."""
    from flask import Flask
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    
    db.init_app(app)
    
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        # Clear association table first
        db.session.execute(db.text('DELETE FROM prompt_tags'))
        Prompt.query.delete()
        Tag.query.delete()
        db.session.commit()
        
        # Create tags
        print("Creating tags...")
        tags_dict = {}
        for prompt_data in SAMPLE_PROMPTS:
            for tag_name in prompt_data['tags']:
                if tag_name not in tags_dict:
                    color = TAG_COLORS.get(tag_name, '#6B7280')
                    tag = Tag.get_or_create(tag_name, color=color)
                    tags_dict[tag_name] = tag
        
        # Create prompts
        print("Creating prompts...")
        for prompt_data in SAMPLE_PROMPTS:
            prompt = Prompt(
                title=prompt_data['title'],
                content=prompt_data['content'],
                description=prompt_data['description']
            )
            
            # Add tags
            for tag_name in prompt_data['tags']:
                prompt.tags.append(tags_dict[tag_name])
            
            prompt.save()
            print(f"  Created: {prompt.title}")
        
        # Show statistics
        print(f"\nDatabase seeded successfully!")
        print(f"  - Total prompts: {Prompt.query.count()}")
        print(f"  - Total tags: {Tag.query.count()}")
        print(f"  - Active prompts: {len(Prompt.get_active())}")


if __name__ == "__main__":
    seed_database()