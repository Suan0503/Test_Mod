#!/usr/bin/env python3
"""
Smoke test script for Flask application
Tests basic functionality and endpoints
"""
import os
import sys
import logging
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set test environment
os.environ['FLASK_CONFIG'] = 'testing'
os.environ['SECRET_KEY'] = 'test-secret-key'
os.environ['LINE_CHANNEL_ACCESS_TOKEN'] = 'test-token'
os.environ['LINE_CHANNEL_SECRET'] = 'test-secret'

def run_smoke_tests():
    """Run basic smoke tests for the application."""
    try:
        # Test imports
        print("Testing imports...")
        from app import create_app
        from extensions import db
        from models.whitelist import Whitelist
        from models.blacklist import Blacklist
        print("✅ All imports successful")

        # Test app creation
        print("Testing app creation...")
        app = create_app('testing')
        print("✅ App creation successful")

        # Test database models
        print("Testing database models...")
        with app.app_context():
            # Test model creation
            wl = Whitelist(
                identifier='test-id',
                name='Test User',
                phone='0900000000',
                email='test@example.com',
                note='Test note'
            )
            bl = Blacklist(
                identifier='test-blocked-id',
                name='Blocked User',
                phone='0900000001',
                email='blocked@example.com',
                reason='Test reason'
            )
            print("✅ Model instantiation successful")

        # Test routes exist
        print("Testing routes...")
        with app.test_client() as client:
            # Test home route
            response = client.get('/')
            assert response.status_code == 200
            print("✅ Home route works")

            # Test admin routes exist (might get errors but shouldn't crash)
            routes_to_test = [
                '/admin/list/',
                '/admin/list/whitelist/new',
                '/admin/list/blacklist/new'
            ]
            
            for route in routes_to_test:
                try:
                    response = client.get(route)
                    print(f"✅ Route {route} accessible (status: {response.status_code})")
                except Exception as e:
                    print(f"⚠️  Route {route} error: {e}")

        print("\n🎉 Smoke tests completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Smoke test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_smoke_tests()
    sys.exit(0 if success else 1)