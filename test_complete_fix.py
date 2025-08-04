#!/usr/bin/env python3
"""
Comprehensive test of the complete foreign key constraint fix
including new user registration and data creation flow
"""

import asyncio
import sys
import os
from dotenv import load_dotenv
import uuid
import aiohttp
import json

# Load environment variables
load_dotenv('/app/backend/.env')
sys.path.append('/app/backend')

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://8f296db8-41e4-45d4-b9b1-dbc5e21b4a2a.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

async def test_complete_fix():
    """Test the complete foreign key constraint fix including new user registration"""
    
    async with aiohttp.ClientSession() as session:
        print("🔍 Testing Complete Foreign Key Constraint Fix...")
        
        # Generate unique test user
        unique_id = str(uuid.uuid4())[:8]
        test_email = f"complete.test.{unique_id}@aurumlife.com"
        test_username = f"completetest_{unique_id}"
        test_password = "CompleteTest123!"
        
        print(f"📧 Test user: {test_email}")
        
        # Step 1: Register new user
        print("\n1️⃣ Testing new user registration...")
        
        register_data = {
            "username": test_username,
            "email": test_email,
            "first_name": "Complete",
            "last_name": "Test",
            "password": test_password
        }
        
        auth_token = None
        user_id = None
        
        try:
            async with session.post(f"{API_BASE}/auth/register", json=register_data) as response:
                if response.status == 200:
                    user_data = await response.json()
                    user_id = user_data.get('id')
                    print(f"✅ User registered successfully: {user_id}")
                else:
                    error_text = await response.text()
                    print(f"❌ Registration failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
        
        # Step 2: Login with new user
        print("\n2️⃣ Testing login with new user...")
        
        login_data = {
            "email": test_email,
            "password": test_password
        }
        
        try:
            async with session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                if response.status == 200:
                    login_result = await response.json()
                    auth_token = login_result.get("access_token")
                    print("✅ Login successful")
                else:
                    error_text = await response.text()
                    print(f"❌ Login failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
        
        if not auth_token:
            print("❌ No auth token received")
            return False
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Step 3: Test /auth/me endpoint
        print("\n3️⃣ Testing /auth/me endpoint...")
        
        try:
            async with session.get(f"{API_BASE}/auth/me", headers=headers) as response:
                if response.status == 200:
                    user_data = await response.json()
                    user_id = user_data.get('id')
                    print(f"✅ /auth/me working - User ID: {user_id}")
                else:
                    error_text = await response.text()
                    print(f"❌ /auth/me failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ /auth/me error: {e}")
            return False
        
        # Step 4: Test data creation - Pillar
        print("\n4️⃣ Testing pillar creation (critical foreign key test)...")
        
        pillar_data = {
            "name": f"Complete Test Pillar {unique_id}",
            "description": "Testing complete foreign key fix",
            "icon": "🔧",
            "color": "#4CAF50"
        }
        
        pillar_id = None
        
        try:
            async with session.post(f"{API_BASE}/pillars", json=pillar_data, headers=headers) as response:
                if response.status == 200:
                    pillar = await response.json()
                    pillar_id = pillar.get('id')
                    print(f"🎉 SUCCESS: Pillar created - ID: {pillar_id}")
                else:
                    error_text = await response.text()
                    print(f"❌ Pillar creation failed: {response.status} - {error_text}")
                    if "foreign key constraint" in error_text.lower():
                        print("🚨 FOREIGN KEY CONSTRAINT VIOLATION DETECTED!")
                    return False
        except Exception as e:
            print(f"❌ Pillar creation error: {e}")
            return False
        
        # Step 5: Test data creation - Area
        print("\n5️⃣ Testing area creation...")
        
        area_data = {
            "name": f"Complete Test Area {unique_id}",
            "description": "Testing area creation with complete fix",
            "icon": "🎯",
            "color": "#2196F3",
            "pillar_id": pillar_id,
            "importance": 4
        }
        
        area_id = None
        
        try:
            async with session.post(f"{API_BASE}/areas", json=area_data, headers=headers) as response:
                if response.status == 200:
                    area = await response.json()
                    area_id = area.get('id')
                    print(f"✅ Area created - ID: {area_id}")
                else:
                    error_text = await response.text()
                    print(f"❌ Area creation failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Area creation error: {e}")
            return False
        
        # Step 6: Test data creation - Project
        print("\n6️⃣ Testing project creation...")
        
        project_data = {
            "name": f"Complete Test Project {unique_id}",
            "description": "Testing project creation with complete fix",
            "icon": "🚀",
            "area_id": area_id,
            "status": "Not Started",
            "priority": "medium",
            "importance": 3
        }
        
        project_id = None
        
        try:
            async with session.post(f"{API_BASE}/projects", json=project_data, headers=headers) as response:
                if response.status == 200:
                    project = await response.json()
                    project_id = project.get('id')
                    print(f"✅ Project created - ID: {project_id}")
                else:
                    error_text = await response.text()
                    print(f"❌ Project creation failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Project creation error: {e}")
            return False
        
        # Step 7: Test data creation - Task
        print("\n7️⃣ Testing task creation...")
        
        task_data = {
            "name": f"Complete Test Task {unique_id}",
            "description": "Testing task creation with complete fix",
            "project_id": project_id,
            "status": "todo",
            "priority": "medium"
        }
        
        task_id = None
        
        try:
            async with session.post(f"{API_BASE}/tasks", json=task_data, headers=headers) as response:
                if response.status == 200:
                    task = await response.json()
                    task_id = task.get('id')
                    print(f"✅ Task created - ID: {task_id}")
                else:
                    error_text = await response.text()
                    print(f"❌ Task creation failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            print(f"❌ Task creation error: {e}")
            return False
        
        # Step 8: Clean up test data
        print("\n8️⃣ Cleaning up test data...")
        
        cleanup_endpoints = [
            (f"{API_BASE}/tasks/{task_id}", "Task"),
            (f"{API_BASE}/projects/{project_id}", "Project"),
            (f"{API_BASE}/areas/{area_id}", "Area"),
            (f"{API_BASE}/pillars/{pillar_id}", "Pillar")
        ]
        
        for endpoint, resource_type in cleanup_endpoints:
            try:
                async with session.delete(endpoint, headers=headers) as response:
                    if response.status in [200, 204]:
                        print(f"🧹 {resource_type} cleaned up")
                    else:
                        print(f"⚠️ Could not clean up {resource_type}")
            except Exception as e:
                print(f"⚠️ Cleanup error for {resource_type}: {e}")
        
        print("\n🎉 COMPLETE SUCCESS!")
        print("=" * 60)
        print("✅ User registration: WORKING")
        print("✅ User authentication: WORKING")
        print("✅ Pillar creation: WORKING")
        print("✅ Area creation: WORKING")
        print("✅ Project creation: WORKING")
        print("✅ Task creation: WORKING")
        print("=" * 60)
        print("🔧 Foreign key constraint issue has been COMPLETELY RESOLVED!")
        print("📈 New users can register and immediately create data!")
        print("🚀 Application is ready for production use!")
        
        return True

if __name__ == "__main__":
    asyncio.run(test_complete_fix())