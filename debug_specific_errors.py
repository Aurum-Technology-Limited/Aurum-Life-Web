#!/usr/bin/env python3

import asyncio
import aiohttp
import json

# Configuration
BACKEND_URL = "https://fastapi-react-fix.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

async def debug_specific_errors():
    """Debug the specific 500 errors for Areas and Tasks"""
    
    session = aiohttp.ClientSession()
    
    try:
        # Authenticate first
        login_data = {
            "email": "nav.test@aurumlife.com",
            "password": "testpassword"
        }
        
        async with session.post(f"{BACKEND_URL}/api/auth/login", json=login_data) as response:
            if response.status == 200:
                data = await response.json()
                auth_token = data["access_token"]
                headers = {"Authorization": f"Bearer {auth_token}"}
                print("✅ Authentication successful")
            else:
                print("❌ Authentication failed")
                return
        
        # Create an area first (this should work)
        print("\n🔍 Creating area for task testing...")
        area_data = {
            "name": "Debug Area for Task Test",
            "description": "Debug area for task testing",
            "icon": "🔍",
            "color": "#F59E0B",
            "importance": 4
        }
        
        area_id = None
        async with session.post(f"{API_BASE}/areas", json=area_data, headers=headers) as response:
            if response.status == 200:
                area = await response.json()
                area_id = area['id']
                print(f"✅ Area created successfully: {area_id}")
            else:
                error_text = await response.text()
                print(f"❌ Area creation failed: {response.status} - {error_text}")
                return
        
        # Create a project (this should work)
        print("\n🔍 Creating project for task testing...")
        project_data = {
            "area_id": area_id,
            "name": "Debug Project for Task Test",
            "description": "Debug project for task testing",
            "icon": "🚀",
            "status": "Not Started",
            "priority": "high"
        }
        
        project_id = None
        async with session.post(f"{API_BASE}/projects", json=project_data, headers=headers) as response:
            if response.status == 200:
                project = await response.json()
                project_id = project['id']
                print(f"✅ Project created successfully: {project_id}")
            else:
                error_text = await response.text()
                print(f"❌ Project creation failed: {response.status} - {error_text}")
                return
        
        # Now test task creation with detailed error
        print("\n🔍 Testing Task creation with detailed error...")
        task_data = {
            "project_id": project_id,
            "name": "Debug Test Task",
            "description": "Debug test task for error investigation",
            "status": "todo",
            "priority": "medium"
        }
        
        async with session.post(f"{API_BASE}/tasks", json=task_data, headers=headers) as response:
            print(f"Task creation status: {response.status}")
            error_text = await response.text()
            print(f"Task creation response: {error_text}")
            
            if response.status == 200:
                task = await response.json()
                print(f"✅ Task created successfully: {task['id']}")
                
                # Clean up - delete the task
                await session.delete(f"{API_BASE}/tasks/{task['id']}", headers=headers)
            
        # Clean up - delete project and area
        if project_id:
            await session.delete(f"{API_BASE}/projects/{project_id}", headers=headers)
        if area_id:
            await session.delete(f"{API_BASE}/areas/{area_id}", headers=headers)
            
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(debug_specific_errors())