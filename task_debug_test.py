#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import os

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://3241bdaf-485d-4483-9bf8-f3b315478945.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

async def test_task_creation_debug():
    """Debug task creation issue"""
    
    session = aiohttp.ClientSession()
    
    try:
        # Authenticate
        login_data = {
            "email": "nav.test@aurumlife.com",
            "password": "testpassword123"
        }
        
        async with session.post(f"{API_BASE}/auth/login", json=login_data) as response:
            if response.status != 200:
                print(f"❌ Authentication failed: {response.status}")
                return
                
            data = await response.json()
            auth_token = data["access_token"]
            headers = {"Authorization": f"Bearer {auth_token}"}
            print("✅ Authentication successful")
        
        # Get existing projects
        async with session.get(f"{API_BASE}/projects", headers=headers) as response:
            if response.status != 200:
                print(f"❌ Failed to get projects: {response.status}")
                return
                
            projects = await response.json()
            if not projects:
                print("❌ No projects found")
                return
                
            project_id = projects[0]["id"]
            print(f"✅ Using project ID: {project_id}")
        
        # Try different task creation payloads
        test_payloads = [
            {
                "name": "Simple Task",
                "description": "A simple test task",
                "project_id": project_id,
                "priority": "medium",
                "status": "todo"
            },
            {
                "name": "Task with explicit None parent",
                "description": "Task with parent_task_id explicitly set to None",
                "project_id": project_id,
                "parent_task_id": None,
                "priority": "medium",
                "status": "todo"
            },
            {
                "name": "Task without parent field",
                "description": "Task without parent_task_id field at all",
                "project_id": project_id,
                "priority": "medium",
                "status": "todo"
            }
        ]
        
        for i, payload in enumerate(test_payloads, 1):
            print(f"\n🧪 Test {i}: {payload['name']}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            
            async with session.post(f"{API_BASE}/tasks", json=payload, headers=headers) as response:
                if response.status == 200:
                    task = await response.json()
                    print(f"✅ Task created successfully: {task['id']}")
                    
                    # Clean up
                    async with session.delete(f"{API_BASE}/tasks/{task['id']}", headers=headers) as del_response:
                        if del_response.status == 200:
                            print(f"✅ Task deleted: {task['id']}")
                        else:
                            print(f"⚠️ Failed to delete task: {del_response.status}")
                else:
                    error_text = await response.text()
                    print(f"❌ Task creation failed: {response.status}")
                    print(f"Error: {error_text}")
                    
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(test_task_creation_debug())