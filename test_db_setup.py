#!/usr/bin/env python
"""
Database initialization and testing script for MagniFood
Helps test connection and enable pgvector extension
"""
import os
import sys
import django
from pathlib import Path

# Add project to path
project_path = Path(__file__).parent / 'MagniFood'
sys.path.insert(0, str(project_path))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MagniFood.settings')
django.setup()

from django.db import connection
from Main.models import Recipe

def test_connection():
    """Test database connection"""
    print("Testing database connection...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✓ Connected to database: {version[:50]}...")
        return True
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

def enable_pgvector():
    """Enable pgvector extension"""
    print("\nEnabling pgvector extension...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        print("✓ pgvector extension enabled")
        return True
    except Exception as e:
        print(f"✗ Failed to enable pgvector: {e}")
        return False

def check_recipe_model():
    """Check Recipe model and count recipes"""
    print("\nChecking Recipe model...")
    try:
        count = Recipe.objects.count()
        print(f"✓ Recipe table exists with {count} recipes")
        return True
    except Exception as e:
        print(f"✗ Recipe model error: {e}")
        return False

def check_embedding_field():
    """Check if embedding field exists"""
    print("\nChecking embedding field...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'Main_recipe' AND column_name = 'embedding'
            """)
            result = cursor.fetchone()
            if result:
                print(f"✓ Embedding field found: {result[0]} ({result[1]})")
                return True
            else:
                print("✗ Embedding field not found. Run: python manage.py migrate")
                return False
    except Exception as e:
        print(f"✗ Error checking embedding field: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("MagniFood Database Setup Test")
    print("=" * 60)
    
    results = []
    results.append(("Database Connection", test_connection()))
    
    if results[-1][1]:  # Only proceed if connected
        results.append(("pgvector Extension", enable_pgvector()))
        results.append(("Recipe Model", check_recipe_model()))
        results.append(("Embedding Field", check_embedding_field()))
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print("=" * 60)
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result for _, result in results)
    print("=" * 60)
    if all_passed:
        print("✓ All tests passed! Database is ready.")
    else:
        print("✗ Some tests failed. Please check the errors above.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
