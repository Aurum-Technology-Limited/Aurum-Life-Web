#!/usr/bin/env python3
"""
Test File Attachment Endpoints
"""

import asyncio
import aiohttp

async def test_file_endpoints():
    """Test file attachment endpoints"""
    
    session = aiohttp.ClientSession()
    
    try:
        # Login first
        login_data = {
            "email": "nav.test@aurumlife.com",
            "password": "testpassword123"
        }
        
        async with session.post("http://localhost:8001/api/auth/login", json=login_data) as response:
            if response.status == 200:
                data = await response.json()
                auth_token = data["access_token"]
                print("✅ Authentication successful")
            else:
                print(f"❌ Authentication failed: {response.status}")
                return
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Get a project ID from projects list
        async with session.get("http://localhost:8001/api/projects", headers=headers) as response:
            if response.status == 200:
                projects = await response.json()
                if projects:
                    project_id = projects[0]['id']
                    print(f"✅ Found project for testing: {project_id}")
                    
                    # Test the file attachment endpoint that was causing 500 errors
                    print(f"\n📂 Testing file attachment endpoint...")
                    async with session.get(f"http://localhost:8001/api/resources/parent/project/{project_id}", headers=headers) as file_response:
                        if file_response.status == 200:
                            files = await file_response.json()
                            print(f"✅ File endpoint working: {len(files)} files returned")
                        else:
                            error_text = await file_response.text()
                            print(f"❌ File endpoint failed: {file_response.status} - {error_text}")
                else:
                    print("⚠️ No projects found to test with")
            else:
                print(f"❌ Failed to get projects: {response.status}")
        
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(test_file_endpoints())