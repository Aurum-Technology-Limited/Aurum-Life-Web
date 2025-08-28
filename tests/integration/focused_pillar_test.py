#!/usr/bin/env python3
"""
Focused Pillar Creation Test
Test the exact pillar creation flow that's failing
"""

import asyncio
import aiohttp
import json

class PillarCreationTest:
    def __init__(self):
        self.base_url = "http://localhost:8001/api"
        self.session = None
        self.auth_token = None
        
    async def setup(self):
        """Setup HTTP session and authenticate"""
        self.session = aiohttp.ClientSession()
        
        # Authenticate
        login_data = {
            "email": "nav.test@aurumlife.com",
            "password": "testpassword123"
        }
        
        async with self.session.post(f"{self.base_url}/auth/login", json=login_data) as response:
            if response.status == 200:
                data = await response.json()
                self.auth_token = data["access_token"]
                print(f"✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status}")
                return False
                
    async def test_pillar_creation(self):
        """Test pillar creation with detailed logging"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        pillar_data = {
            "name": "Test Pillar Debug",
            "description": "Testing pillar creation with debug info",
            "icon": "🎯",
            "color": "#FF5722",
            "time_allocation_percentage": 25.0
        }
        
        print(f"\n🧪 Creating pillar with data: {json.dumps(pillar_data, indent=2)}")
        
        try:
            async with self.session.post(f"{self.base_url}/pillars", json=pillar_data, headers=headers) as response:
                response_text = await response.text()
                
                print(f"📊 Response status: {response.status}")
                print(f"📊 Response headers: {dict(response.headers)}")
                print(f"📊 Response body: {response_text}")
                
                if response.status == 200:
                    pillar = json.loads(response_text)
                    print(f"✅ Pillar created successfully!")
                    print(f"   ID: {pillar.get('id', 'NO_ID')}")
                    print(f"   Name: {pillar.get('name', 'NO_NAME')}")
                    print(f"   User ID: {pillar.get('user_id', 'NO_USER_ID')}")
                    return pillar
                else:
                    print(f"❌ Pillar creation failed: {response.status}")
                    try:
                        error_data = json.loads(response_text)
                        print(f"   Error details: {error_data}")
                    except:
                        print(f"   Raw error: {response_text}")
                    return None
                    
        except Exception as e:
            print(f"❌ Exception during pillar creation: {e}")
            return None
            
    async def test_pillar_retrieval(self):
        """Test pillar retrieval"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            async with self.session.get(f"{self.base_url}/pillars", headers=headers) as response:
                if response.status == 200:
                    pillars = await response.json()
                    print(f"✅ Retrieved {len(pillars)} pillars")
                    for pillar in pillars:
                        print(f"   - {pillar.get('name', 'NO_NAME')} (ID: {pillar.get('id', 'NO_ID')})")
                    return pillars
                else:
                    response_text = await response.text()
                    print(f"❌ Pillar retrieval failed: {response.status} - {response_text}")
                    return []
                    
        except Exception as e:
            print(f"❌ Exception during pillar retrieval: {e}")
            return []
            
    async def test_user_info(self):
        """Check current user info"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            async with self.session.get(f"{self.base_url}/auth/me", headers=headers) as response:
                if response.status == 200:
                    user = await response.json()
                    print(f"✅ Current user: {user.get('email', 'NO_EMAIL')} (ID: {user.get('id', 'NO_ID')})")
                    return user
                else:
                    print(f"❌ User info failed: {response.status}")
                    return None
        except Exception as e:
            print(f"❌ Exception getting user info: {e}")
            return None
    
    async def cleanup(self):
        """Cleanup session"""
        if self.session:
            await self.session.close()

async def main():
    """Run focused pillar creation test"""
    test = PillarCreationTest()
    
    try:
        print("🚀 Starting Focused Pillar Creation Test")
        
        # Setup and authenticate
        if not await test.setup():
            return
            
        # Check user info
        user = await test.test_user_info()
        if not user:
            return
            
        # Test pillar retrieval first
        print("\n📋 Testing pillar retrieval...")
        existing_pillars = await test.test_pillar_retrieval()
        
        # Test pillar creation
        print("\n🏗️ Testing pillar creation...")
        new_pillar = await test.test_pillar_creation()
        
        # Test pillar retrieval again to see if it was created
        if new_pillar:
            print("\n📋 Testing pillar retrieval after creation...")
            updated_pillars = await test.test_pillar_retrieval()
            
            if len(updated_pillars) > len(existing_pillars):
                print("✅ Pillar creation confirmed - new pillar appears in list!")
            else:
                print("⚠️ Pillar may not have been saved properly")
        
        print("\n🎯 Test completed!")
        
    finally:
        await test.cleanup()

if __name__ == "__main__":
    asyncio.run(main())