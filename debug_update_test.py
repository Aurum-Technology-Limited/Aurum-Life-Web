#!/usr/bin/env python3

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

async def debug_update_operations():
    """Debug update operations to see specific errors"""
    
    session = aiohttp.ClientSession()
    
    try:
        # Authenticate
        login_data = {
            "email": "nav.test@aurumlife.com",
            "password": "testpassword"
        }
        
        async with session.post(f"{BACKEND_URL}/auth/login", json=login_data) as response:
            if response.status == 200:
                data = await response.json()
                auth_token = data["access_token"]
                headers = {"Authorization": f"Bearer {auth_token}"}
                print("✅ Authentication successful")
            else:
                print(f"❌ Authentication failed: {response.status}")
                return
        
        # Create test data first
        pillar_data = {
            "name": "Debug Test Pillar",
            "description": "Test pillar for debugging",
            "icon": "🔧",
            "color": "#FF0000",
            "time_allocation_percentage": 25.0
        }
        
        async with session.post(f"{API_BASE}/pillars", json=pillar_data, headers=headers) as response:
            if response.status == 200:
                pillar = await response.json()
                pillar_id = pillar['id']
                print(f"✅ Created pillar: {pillar_id}")
            else:
                print(f"❌ Pillar creation failed: {response.status}")
                return
        
        # Create area
        area_data = {
            "pillar_id": pillar_id,
            "name": "Debug Test Area",
            "description": "Test area for debugging",
            "icon": "🔧",
            "color": "#FF0000",
            "importance": 3
        }
        
        async with session.post(f"{API_BASE}/areas", json=area_data, headers=headers) as response:
            if response.status == 200:
                area = await response.json()
                area_id = area['id']
                print(f"✅ Created area: {area_id}")
            else:
                print(f"❌ Area creation failed: {response.status}")
                return
        
        # Create project
        project_data = {
            "area_id": area_id,
            "name": "Debug Test Project",
            "description": "Test project for debugging",
            "icon": "🔧",
            "status": "Not Started",
            "priority": "high",
            "deadline": "2025-02-15T10:00:00Z"
        }
        
        async with session.post(f"{API_BASE}/projects", json=project_data, headers=headers) as response:
            if response.status == 200:
                project = await response.json()
                project_id = project['id']
                print(f"✅ Created project: {project_id}")
            else:
                print(f"❌ Project creation failed: {response.status}")
                return
        
        # Create task
        task_data = {
            "project_id": project_id,
            "name": "Debug Test Task",
            "description": "Test task for debugging",
            "status": "todo",
            "priority": "medium",
            "due_date": "2025-01-30T07:00:00Z"
        }
        
        async with session.post(f"{API_BASE}/tasks", json=task_data, headers=headers) as response:
            if response.status == 200:
                task = await response.json()
                task_id = task['id']
                print(f"✅ Created task: {task_id}")
            else:
                print(f"❌ Task creation failed: {response.status}")
                return
        
        print("\n🔍 Testing Update Operations...")
        
        # Test Project Update
        print("\n--- Project Update Test ---")
        project_update_data = {"name": "Updated Project Name", "status": "In Progress"}
        
        async with session.put(f"{API_BASE}/projects/{project_id}", json=project_update_data, headers=headers) as response:
            print(f"Project update status: {response.status}")
            response_text = await response.text()
            print(f"Project update response: {response_text}")
            
            if response.status != 200:
                try:
                    error_data = json.loads(response_text)
                    print(f"Project update error details: {error_data}")
                except:
                    print(f"Project update raw error: {response_text}")
        
        # Test Task Update
        print("\n--- Task Update Test ---")
        task_update_data = {"name": "Updated Task Name", "status": "in_progress"}
        
        async with session.put(f"{API_BASE}/tasks/{task_id}", json=task_update_data, headers=headers) as response:
            print(f"Task update status: {response.status}")
            response_text = await response.text()
            print(f"Task update response: {response_text}")
            
            if response.status != 200:
                try:
                    error_data = json.loads(response_text)
                    print(f"Task update error details: {error_data}")
                except:
                    print(f"Task update raw error: {response_text}")
        
        # Cleanup
        print("\n🧹 Cleaning up...")
        await session.delete(f"{API_BASE}/tasks/{task_id}", headers=headers)
        await session.delete(f"{API_BASE}/projects/{project_id}", headers=headers)
        await session.delete(f"{API_BASE}/areas/{area_id}", headers=headers)
        await session.delete(f"{API_BASE}/pillars/{pillar_id}", headers=headers)
        
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(debug_update_operations())