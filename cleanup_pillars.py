#!/usr/bin/env python3
"""
Clean up duplicate test pillars to improve performance
"""

import asyncio
import aiohttp

async def cleanup_duplicate_pillars():
    """Remove duplicate test pillars"""
    
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
        
        # Get all pillars
        print("\n🔍 Getting all pillars...")
        async with session.get("http://localhost:8001/api/pillars", headers=headers) as response:
            if response.status == 200:
                pillars = await response.json()
                print(f"✅ Found {len(pillars)} pillars")
                
                # Group pillars by name to find duplicates
                pillar_groups = {}
                for pillar in pillars:
                    name = pillar['name']
                    if name not in pillar_groups:
                        pillar_groups[name] = []
                    pillar_groups[name].append(pillar)
                
                # Keep only one of each duplicate group, delete the rest
                deleted_count = 0
                for name, group in pillar_groups.items():
                    if len(group) > 1:
                        print(f"\n🔍 Found {len(group)} duplicates of '{name}'")
                        # Keep the first one, delete the rest
                        for pillar in group[1:]:
                            pillar_id = pillar['id']
                            print(f"  🗑️ Deleting duplicate: {pillar_id}")
                            
                            async with session.delete(f"http://localhost:8001/api/pillars/{pillar_id}", headers=headers) as delete_response:
                                if delete_response.status == 200:
                                    print(f"    ✅ Deleted successfully")
                                    deleted_count += 1
                                else:
                                    error_text = await delete_response.text()
                                    print(f"    ❌ Failed to delete: {delete_response.status} - {error_text}")
                
                print(f"\n🎉 Cleanup complete! Deleted {deleted_count} duplicate pillars")
                
                # Get updated count
                async with session.get("http://localhost:8001/api/pillars", headers=headers) as response:
                    if response.status == 200:
                        updated_pillars = await response.json()
                        print(f"📊 Pillars remaining: {len(updated_pillars)}")
                        
                        # Show remaining pillars
                        print("\n📋 Remaining pillars:")
                        for pillar in updated_pillars:
                            print(f"  - {pillar['name']}")
                            
            else:
                error_text = await response.text()
                print(f"❌ Failed to get pillars: {response.status} - {error_text}")
        
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(cleanup_duplicate_pillars())