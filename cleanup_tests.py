"""
Test Suite Cleanup Script for Aurum Life MVP v1.2
Removes irrelevant test files and organizes the remaining tests
"""

import os
import shutil
from datetime import datetime
import re

# Test files to keep (MVP-relevant)
KEEP_TESTS = [
    "test_auth.py",
    "test_pillars.py", 
    "test_areas.py",
    "test_projects.py",
    "test_tasks.py",
    "test_today_view.py",
    "test_rls_isolation.py",
    "test_performance.py",
    "test_validation.py"
]

# Patterns for test files to remove
REMOVE_PATTERNS = [
    r".*_test\.py$",  # Old naming convention
    r"test_.*_direct\.py$",  # Direct test files
    r"test_.*_integration\.py$",  # Old integration tests
    r".*_backend_test\.py$",  # Backend test files
    r"test_ai_.*\.py$",  # AI-related tests
    r"test_achievement.*\.py$",  # Achievement tests
    r"test_journal.*\.py$",  # Journal tests
    r"test_notification.*\.py$",  # Notification tests
    r"test_file.*\.py$",  # File management tests
    r"test_template.*\.py$",  # Template tests
]

def should_remove_file(filename):
    """Check if a test file should be removed"""
    # Keep if in keep list
    if filename in KEEP_TESTS:
        return False
    
    # Remove if matches any remove pattern
    for pattern in REMOVE_PATTERNS:
        if re.match(pattern, filename):
            return True
    
    # Remove all test files not explicitly kept
    if filename.startswith("test_") and filename.endswith(".py"):
        return True
    
    return False

def cleanup_root_tests():
    """Clean up test files in root directory"""
    root_files = os.listdir(".")
    test_files_removed = []
    
    # Create archive directory
    archive_dir = f"archived_tests_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(archive_dir, exist_ok=True)
    
    for filename in root_files:
        if filename.endswith(".py") and should_remove_file(filename):
            try:
                # Archive the file
                shutil.move(filename, os.path.join(archive_dir, filename))
                test_files_removed.append(filename)
                print(f"Archived: {filename}")
            except Exception as e:
                print(f"Error archiving {filename}: {e}")
    
    # Remove PNG files (screenshots)
    for filename in root_files:
        if filename.endswith(".png"):
            try:
                shutil.move(filename, os.path.join(archive_dir, filename))
                print(f"Archived screenshot: {filename}")
            except Exception as e:
                print(f"Error archiving {filename}: {e}")
    
    return test_files_removed, archive_dir

def create_organized_test_structure():
    """Create proper test directory structure"""
    
    # Create test directories
    test_dirs = [
        "tests",
        "tests/unit",
        "tests/unit/models",
        "tests/unit/services",
        "tests/unit/api",
        "tests/integration",
        "tests/e2e",
        "tests/performance",
        "tests/security"
    ]
    
    for dir_path in test_dirs:
        os.makedirs(dir_path, exist_ok=True)
        
        # Create __init__.py
        init_file = os.path.join(dir_path, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write("")

def create_test_templates():
    """Create template test files for MVP features"""
    
    # Unit test template
    unit_test_template = '''"""
Unit tests for {feature} functionality
MVP v1.2
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

class Test{Feature}:
    """Test cases for {feature}"""
    
    def test_create_{feature}_valid_input(self):
        """Test creating {feature} with valid input"""
        # TODO: Implement
        pass
    
    def test_create_{feature}_invalid_input(self):
        """Test creating {feature} with invalid input"""
        # TODO: Implement
        pass
    
    def test_update_{feature}_ownership(self):
        """Test that users can only update their own {feature}"""
        # TODO: Implement
        pass
'''

    # Integration test template
    integration_test_template = '''"""
Integration tests for {feature} with database
MVP v1.2
"""

import pytest
from httpx import AsyncClient
from datetime import datetime

@pytest.mark.asyncio
class Test{Feature}Integration:
    """Integration tests for {feature}"""
    
    async def test_{feature}_crud_flow(self, client: AsyncClient, auth_headers):
        """Test complete CRUD flow for {feature}"""
        # Create
        create_response = await client.post(
            "/api/{feature}s",
            json={{"name": "Test {Feature}"}},
            headers=auth_headers
        )
        assert create_response.status_code == 201
        
        # Read
        {feature}_id = create_response.json()["id"]
        read_response = await client.get(
            f"/api/{feature}s/{{feature_id}}",
            headers=auth_headers
        )
        assert read_response.status_code == 200
        
        # Update
        update_response = await client.patch(
            f"/api/{feature}s/{{feature_id}}",
            json={{"name": "Updated {Feature}"}},
            headers=auth_headers
        )
        assert update_response.status_code == 200
        
        # Delete
        delete_response = await client.delete(
            f"/api/{feature}s/{{feature_id}}",
            headers=auth_headers
        )
        assert delete_response.status_code == 204
'''

    # Security test template
    security_test_template = '''"""
Security tests for RLS and data isolation
MVP v1.2
"""

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
class TestRLSIsolation:
    """Test Row Level Security isolation"""
    
    async def test_user_cannot_access_other_user_data(
        self, 
        client: AsyncClient, 
        user_a_headers, 
        user_b_headers
    ):
        """Verify User A cannot access User B's data"""
        # User A creates a pillar
        response_a = await client.post(
            "/api/pillars",
            json={{"name": "User A Pillar"}},
            headers=user_a_headers
        )
        assert response_a.status_code == 201
        pillar_id = response_a.json()["id"]
        
        # User B tries to access User A's pillar
        response_b = await client.get(
            f"/api/pillars/{{pillar_id}}",
            headers=user_b_headers
        )
        assert response_b.status_code == 404
        
        # User B tries to update User A's pillar
        response_b_update = await client.patch(
            f"/api/pillars/{{pillar_id}}",
            json={{"name": "Hacked!"}},
            headers=user_b_headers
        )
        assert response_b_update.status_code == 404
'''

    # Create template files
    templates = {
        "tests/unit/test_pillars.py": unit_test_template.format(feature="pillar", Feature="Pillar"),
        "tests/unit/test_areas.py": unit_test_template.format(feature="area", Feature="Area"),
        "tests/unit/test_projects.py": unit_test_template.format(feature="project", Feature="Project"),
        "tests/unit/test_tasks.py": unit_test_template.format(feature="task", Feature="Task"),
        "tests/integration/test_hierarchy_flow.py": integration_test_template.format(feature="pillar", Feature="Pillar"),
        "tests/security/test_rls_isolation.py": security_test_template
    }
    
    for filepath, content in templates.items():
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Created: {filepath}")

def create_pytest_config():
    """Create pytest configuration"""
    
    pytest_ini = """[pytest]
minversion = 6.0
addopts = -ra -q --strict-markers
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Unit tests
    integration: Integration tests requiring database
    e2e: End-to-end tests
    security: Security and RLS tests
    performance: Performance tests
    asyncio: Async tests
"""
    
    with open("pytest.ini", 'w') as f:
        f.write(pytest_ini)
    print("Created: pytest.ini")
    
    # Create conftest.py
    conftest = '''"""
Pytest configuration and fixtures
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from supabase import create_client
import os

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def client():
    """Create async test client"""
    from backend.server_secure import app
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def auth_headers(client: AsyncClient):
    """Get auth headers for test user"""
    # Create test user
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "Test123!@#",
            "first_name": "Test",
            "last_name": "User"
        }
    )
    
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
async def supabase_client():
    """Create Supabase client for tests"""
    return create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_ANON_KEY")
    )
'''
    
    with open("tests/conftest.py", 'w') as f:
        f.write(conftest)
    print("Created: tests/conftest.py")

def create_test_requirements():
    """Create test requirements file"""
    
    requirements = """# Test dependencies for Aurum Life MVP v1.2
pytest==7.4.0
pytest-asyncio==0.21.0
pytest-cov==4.1.0
httpx==0.24.1
faker==18.11.2
freezegun==1.2.2
pytest-mock==3.11.1
pytest-env==0.8.2
pytest-timeout==2.1.0
"""
    
    with open("tests/requirements-test.txt", 'w') as f:
        f.write(requirements)
    print("Created: tests/requirements-test.txt")

def main():
    """Main cleanup function"""
    print("Starting test suite cleanup...")
    
    # 1. Archive old tests
    removed_files, archive_dir = cleanup_root_tests()
    print(f"\nArchived {len(removed_files)} test files to {archive_dir}")
    
    # 2. Create organized structure
    create_organized_test_structure()
    print("\nCreated organized test structure")
    
    # 3. Create test templates
    create_test_templates()
    print("\nCreated test templates")
    
    # 4. Create configuration
    create_pytest_config()
    create_test_requirements()
    print("\nCreated test configuration")
    
    print("\n✅ Test suite cleanup complete!")
    print(f"Old tests archived in: {archive_dir}")
    print("New test structure created in: tests/")
    print("\nNext steps:")
    print("1. Review archived tests for any valuable code")
    print("2. Implement the test templates")
    print("3. Run: pip install -r tests/requirements-test.txt")
    print("4. Run: pytest tests/ --cov=backend")

if __name__ == "__main__":
    main()