#!/usr/bin/env python3
"""
Test Pillar Deletion Endpoint
"""

import asyncio
import aiohttp

async def test_pillar_deletion():
    """Test pillar deletion endpoint"""
    
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
        
        # Get existing pillars
        print("\n🔍 Getting existing pillars...")
        async with session.get("http://localhost:8001/api/pillars", headers=headers) as response:
            if response.status == 200:
                pillars = await response.json()
                print(f"✅ Found {len(pillars)} pillars")
                
                if pillars:
                    # Test deleting the first pillar
                    pillar_to_delete = pillars[0]
                    pillar_id = pillar_to_delete['id']
                    pillar_name = pillar_to_delete['name']
                    
                    print(f"\n🗑️ Testing deletion of pillar: {pillar_name} ({pillar_id})")
                    
                    async with session.delete(f"http://localhost:8001/api/pillars/{pillar_id}", headers=headers) as delete_response:
                        if delete_response.status == 200:
                            result = await delete_response.json()
                            print(f"✅ Pillar deletion successful: {result}")
                        else:
                            error_text = await delete_response.text()
                            print(f"❌ Pillar deletion failed: {delete_response.status} - {error_text}")
                else:
                    print("⚠️ No pillars found to delete")
            else:
                error_text = await response.text()
                print(f"❌ Failed to get pillars: {response.status} - {error_text}")
        
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(test_pillar_deletion())