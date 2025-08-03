#!/usr/bin/env python3
"""
Script to create test data for User Acceptance Testing of Contextual Tag Filtering.

This script creates a comprehensive set of test data including:
- Various tags with different colors
- Prompts with different statuses (active/inactive)
- Tags used in both active and inactive prompts
- Tags used only in active prompts
- Tags used only in inactive prompts
- Edge cases for testing

Usage:
    python scripts/create_uat_test_data.py
"""

import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.tag import Tag
from app.models.prompt import Prompt
from app.models.base import db


def create_uat_test_data():
    """Create comprehensive test data for UAT."""
    app = create_app('development')
    
    with app.app_context():
        print("🔄 Creating UAT test data for Contextual Tag Filtering...")
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        # db.session.query(Prompt).delete()
        # db.session.query(Tag).delete()
        # db.session.commit()
        
        # Create tags with different colors
        tags = [
            Tag(name="python", color="#3776ab"),
            Tag(name="javascript", color="#f7df1e"),
            Tag(name="sql", color="#e48e00"),
            Tag(name="html", color="#e34f26"),
            Tag(name="css", color="#1572b6"),
            Tag(name="react", color="#61dafb"),
            Tag(name="vue", color="#4fc08d"),
            Tag(name="angular", color="#dd0031"),
            Tag(name="nodejs", color="#339933"),
            Tag(name="docker", color="#2496ed"),
            Tag(name="kubernetes", color="#326ce5"),
            Tag(name="aws", color="#ff9900"),
            Tag(name="azure", color="#0089d6"),
            Tag(name="gcp", color="#4285f4"),
            Tag(name="git", color="#f05032"),
            Tag(name="linux", color="#fcc624"),
            Tag(name="windows", color="#0078d4"),
            Tag(name="macos", color="#000000"),
            Tag(name="api", color="#ff6b6b"),
            Tag(name="database", color="#4ecdc4")
        ]
        
        print(f"📝 Creating {len(tags)} tags...")
        for tag in tags:
            db.session.add(tag)
        db.session.commit()
        print("✅ Tags created successfully!")
        
        # Create prompts with different statuses
        prompts = [
            # Active prompts
            Prompt(title="Python Web Development", content="Complete guide to Python web development", is_active=True),
            Prompt(title="JavaScript ES6+ Features", content="Modern JavaScript features and syntax", is_active=True),
            Prompt(title="React Hooks Tutorial", content="Understanding React hooks and state management", is_active=True),
            Prompt(title="Vue.js 3 Composition API", content="Vue 3 composition API guide", is_active=True),
            Prompt(title="Angular Services", content="Angular dependency injection and services", is_active=True),
            Prompt(title="Node.js REST API", content="Building REST APIs with Node.js and Express", is_active=True),
            Prompt(title="Docker Containerization", content="Containerizing applications with Docker", is_active=True),
            Prompt(title="Kubernetes Deployment", content="Deploying applications to Kubernetes", is_active=True),
            Prompt(title="AWS Lambda Functions", content="Serverless functions with AWS Lambda", is_active=True),
            Prompt(title="Azure DevOps Pipeline", content="CI/CD with Azure DevOps", is_active=True),
            Prompt(title="Google Cloud Functions", content="Serverless functions with GCP", is_active=True),
            Prompt(title="Git Workflow Best Practices", content="Git branching and collaboration strategies", is_active=True),
            Prompt(title="Linux System Administration", content="Linux server management and administration", is_active=True),
            Prompt(title="API Design Principles", content="RESTful API design and best practices", is_active=True),
            Prompt(title="Database Optimization", content="SQL query optimization and indexing", is_active=True),
            
            # Inactive prompts
            Prompt(title="Legacy JavaScript ES5", content="Old JavaScript syntax and patterns", is_active=False),
            Prompt(title="AngularJS 1.x Guide", content="Legacy AngularJS framework", is_active=False),
            Prompt(title="Windows Server 2012", content="Legacy Windows server administration", is_active=False),
            Prompt(title="Old Docker Compose", content="Legacy Docker Compose syntax", is_active=False),
            Prompt(title="Deprecated AWS Services", content="AWS services that are no longer recommended", is_active=False),
            Prompt(title="Legacy Git Commands", content="Old Git commands and workflows", is_active=False),
            Prompt(title="Traditional API Patterns", content="SOAP and XML-based APIs", is_active=False),
            Prompt(title="Legacy Database Systems", content="Old database systems and practices", is_active=False),
            Prompt(title="Windows 7 Development", content="Development for Windows 7 platform", is_active=False),
            Prompt(title="Old React Patterns", content="Legacy React class components", is_active=False)
        ]
        
        print(f"📝 Creating {len(prompts)} prompts...")
        for prompt in prompts:
            db.session.add(prompt)
        db.session.commit()
        print("✅ Prompts created successfully!")
        
        # Associate tags with prompts to create various scenarios
        print("🔗 Associating tags with prompts...")
        
        # Scenario 1: Tags used in both active and inactive prompts
        prompts[0].tags = [tags[0], tags[1]]  # python, javascript (active)
        prompts[15].tags = [tags[1]]          # javascript (inactive)
        
        prompts[1].tags = [tags[1], tags[3]]  # javascript, html (active)
        prompts[16].tags = [tags[3]]          # html (inactive)
        
        prompts[2].tags = [tags[5], tags[1]]  # react, javascript (active)
        prompts[24].tags = [tags[5]]          # react (inactive)
        
        # Scenario 2: Tags used only in active prompts
        prompts[3].tags = [tags[6]]           # vue (active only)
        prompts[4].tags = [tags[7]]           # angular (active only)
        prompts[5].tags = [tags[8]]           # nodejs (active only)
        prompts[6].tags = [tags[9]]           # docker (active only)
        prompts[7].tags = [tags[10]]          # kubernetes (active only)
        
        # Scenario 3: Tags used only in inactive prompts
        prompts[17].tags = [tags[16]]         # windows (inactive only)
        prompts[18].tags = [tags[9]]          # docker (inactive only)
        prompts[19].tags = [tags[11]]         # aws (inactive only)
        prompts[20].tags = [tags[15]]         # git (inactive only)
        prompts[21].tags = [tags[18]]         # api (inactive only)
        prompts[22].tags = [tags[19]]         # database (inactive only)
        
        # Scenario 4: Multiple tags per prompt
        prompts[8].tags = [tags[11], tags[8]]     # aws, nodejs (active)
        prompts[9].tags = [tags[12], tags[9]]     # azure, docker (active)
        prompts[10].tags = [tags[13], tags[8]]    # gcp, nodejs (active)
        prompts[11].tags = [tags[14], tags[15]]   # git, linux (active)
        prompts[12].tags = [tags[15], tags[0]]    # linux, python (active)
        prompts[13].tags = [tags[18], tags[8]]    # api, nodejs (active)
        prompts[14].tags = [tags[19], tags[2]]    # database, sql (active)
        
        # Scenario 5: Complex inactive scenarios
        prompts[23].tags = [tags[16], tags[18]]   # windows, api (inactive)
        prompts[24].tags = [tags[5], tags[1]]     # react, javascript (inactive)
        
        db.session.commit()
        print("✅ Tag associations created successfully!")
        
        # Print summary
        print("\n📊 Test Data Summary:")
        print(f"   • Tags created: {len(tags)}")
        print(f"   • Prompts created: {len(prompts)}")
        print(f"   • Active prompts: {len([p for p in prompts if p.is_active])}")
        print(f"   • Inactive prompts: {len([p for p in prompts if not p.is_active])}")
        
        # Print tag usage scenarios
        print("\n🎯 Tag Usage Scenarios:")
        
        # Tags used in both active and inactive
        both_tags = ["javascript", "html", "react"]
        print(f"   • Tags used in both active and inactive: {', '.join(both_tags)}")
        
        # Tags used only in active
        active_only = ["vue", "angular", "nodejs", "docker", "kubernetes"]
        print(f"   • Tags used only in active: {', '.join(active_only)}")
        
        # Tags used only in inactive
        inactive_only = ["windows", "aws", "git", "api", "database"]
        print(f"   • Tags used only in inactive: {', '.join(inactive_only)}")
        
        print("\n✅ UAT test data creation completed!")
        print("\n🚀 Ready for User Acceptance Testing!")
        print("   Navigate to http://localhost:5001/prompts to test the feature.")
        
        return {
            'tags': tags,
            'prompts': prompts,
            'active_count': len([p for p in prompts if p.is_active]),
            'inactive_count': len([p for p in prompts if not p.is_active])
        }


def verify_test_data():
    """Verify that test data was created correctly."""
    app = create_app('development')
    
    with app.app_context():
        print("\n🔍 Verifying test data...")
        
        # Count tags and prompts
        tag_count = Tag.query.count()
        prompt_count = Prompt.query.count()
        active_prompts = Prompt.query.filter_by(is_active=True).count()
        inactive_prompts = Prompt.query.filter_by(is_active=False).count()
        
        print(f"   • Total tags: {tag_count}")
        print(f"   • Total prompts: {prompt_count}")
        print(f"   • Active prompts: {active_prompts}")
        print(f"   • Inactive prompts: {inactive_prompts}")
        
        # Check tag associations
        tags_with_prompts = db.session.query(Tag).join(Tag.prompts).distinct().count()
        print(f"   • Tags with associated prompts: {tags_with_prompts}")
        
        # Verify specific scenarios
        javascript_tag = Tag.query.filter_by(name="javascript").first()
        if javascript_tag:
            active_js_prompts = sum(1 for p in javascript_tag.prompts if p.is_active)
            inactive_js_prompts = sum(1 for p in javascript_tag.prompts if not p.is_active)
            print(f"   • JavaScript tag - Active prompts: {active_js_prompts}, Inactive: {inactive_js_prompts}")
        
        vue_tag = Tag.query.filter_by(name="vue").first()
        if vue_tag:
            active_vue_prompts = sum(1 for p in vue_tag.prompts if p.is_active)
            inactive_vue_prompts = sum(1 for p in vue_tag.prompts if not p.is_active)
            print(f"   • Vue tag - Active prompts: {active_vue_prompts}, Inactive: {inactive_vue_prompts}")
        
        print("✅ Test data verification completed!")


def cleanup_test_data():
    """Clean up test data (use with caution)."""
    app = create_app('development')
    
    with app.app_context():
        print("🗑️  Cleaning up test data...")
        
        # Delete all prompts and tags
        db.session.query(Prompt).delete()
        db.session.query(Tag).delete()
        db.session.commit()
        
        print("✅ Test data cleaned up!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Create test data for UAT")
    parser.add_argument("--cleanup", action="store_true", help="Clean up existing test data")
    parser.add_argument("--verify", action="store_true", help="Verify test data after creation")
    
    args = parser.parse_args()
    
    if args.cleanup:
        cleanup_test_data()
    
    create_uat_test_data()
    
    if args.verify:
        verify_test_data() 