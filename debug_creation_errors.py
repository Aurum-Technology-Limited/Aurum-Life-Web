#!/usr/bin/env python3

import asyncio
import aiohttp
import json

# Configuration
BACKEND_URL = "https://3241bdaf-485d-4483-9bf8-f3b315478945.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

async def debug_creation_errors():
    """Debug the specific creation errors for Areas, Projects, and Tasks"""
    
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
        
        # Test Area creation with detailed error
        print("\n🔍 Testing Area creation with detailed error...")
        area_data = {
            "name": "Debug Test Area",
            "description": "Debug test area for error investigation",
            "icon": "🔍",
            "color": "#F59E0B",
            "importance": 4
        }
        
        async with session.post(f"{API_BASE}/areas", json=area_data, headers=headers) as response:
            print(f"Area creation status: {response.status}")
            error_text = await response.text()
            print(f"Area creation error: {error_text}")
            
        # Test Project creation with detailed error
        print("\n🔍 Testing Project creation with detailed error...")
        project_data = {
            "name": "Debug Test Project",
            "description": "Debug test project for error investigation",
            "icon": "🔍",
            "status": "Not Started",
            "priority": "high"
        }
        
        async with session.post(f"{API_BASE}/projects", json=project_data, headers=headers) as response:
            print(f"Project creation status: {response.status}")
            error_text = await response.text()
            print(f"Project creation error: {error_text}")
            
        # Test Task creation with detailed error
        print("\n🔍 Testing Task creation with detailed error...")
        task_data = {
            "name": "Debug Test Task",
            "description": "Debug test task for error investigation",
            "status": "todo",
            "priority": "medium"
        }
        
        async with session.post(f"{API_BASE}/tasks", json=task_data, headers=headers) as response:
            print(f"Task creation status: {response.status}")
            error_text = await response.text()
            print(f"Task creation error: {error_text}")
            
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(debug_creation_errors())