#!/usr/bin/env python3

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration - Use external URL from frontend/.env
BACKEND_URL = "https://55e67447-e9b1-4184-8259-f18223824d38.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class AreasUpdateDebugTest:
    """Debug test to understand the exact issue with areas update"""
    
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "nav.test@aurumlife.com"
        self.test_user_password = "navtest123"
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()
            
    async def authenticate(self):
        """Authenticate with test credentials"""
        try:
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            async with self.session.post(f"{BACKEND_URL}/api/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data["access_token"]
                    print(f"✅ Authentication successful for {self.test_user_email}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Authentication failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
            
    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.auth_token}"}
        
    async def debug_area_update(self):
        """Debug the area update issue step by step"""
        print("\n🔍 DEBUGGING AREA UPDATE ISSUE")
        
        # Step 1: Create a test area first
        print("\n1. Creating test area...")
        area_data = {
            "name": "Debug Test Area",
            "description": "Area for debugging update issue",
            "icon": "🔧",
            "color": "#FF5722",
            "importance": 3
        }
        
        async with self.session.post(f"{API_BASE}/areas", json=area_data, headers=self.get_auth_headers()) as response:
            if response.status == 200:
                area = await response.json()
                area_id = area['id']
                print(f"✅ Created area: {area_id}")
                print(f"   Original data: {json.dumps(area, indent=2)}")
            else:
                error_text = await response.text()
                print(f"❌ Area creation failed: {response.status} - {error_text}")
                return
        
        # Step 2: Try different update scenarios
        print(f"\n2. Testing different update scenarios for area {area_id}...")
        
        # Test 2a: Update with integer importance
        print("\n2a. Testing integer importance (5)...")
        update_data = {"importance": 5}
        
        async with self.session.put(f"{API_BASE}/areas/{area_id}", json=update_data, headers=self.get_auth_headers()) as response:
            response_text = await response.text()
            print(f"   Status: {response.status}")
            print(f"   Response: {response_text}")
            
            if response.status == 200:
                updated_area = await response.json() if response.content_type == 'application/json' else None
                if updated_area:
                    print(f"   Updated area data: {json.dumps(updated_area, indent=2)}")
                    print(f"   Importance field: {updated_area.get('importance')} (type: {type(updated_area.get('importance'))})")
        
        # Test 2b: Update with string importance
        print("\n2b. Testing string importance ('high')...")
        update_data = {"importance": "high"}
        
        async with self.session.put(f"{API_BASE}/areas/{area_id}", json=update_data, headers=self.get_auth_headers()) as response:
            response_text = await response.text()
            print(f"   Status: {response.status}")
            print(f"   Response: {response_text}")
            
            if response.status == 200:
                try:
                    updated_area = await response.json()
                    print(f"   Updated area data: {json.dumps(updated_area, indent=2)}")
                    print(f"   Importance field: {updated_area.get('importance')} (type: {type(updated_area.get('importance'))})")
                except:
                    print("   Could not parse JSON response")
        
        # Test 2c: Update name only (should work)
        print("\n2c. Testing name update only...")
        update_data = {"name": "Debug Test Area - Updated Name"}
        
        async with self.session.put(f"{API_BASE}/areas/{area_id}", json=update_data, headers=self.get_auth_headers()) as response:
            response_text = await response.text()
            print(f"   Status: {response.status}")
            print(f"   Response: {response_text}")
            
            if response.status == 200:
                try:
                    updated_area = await response.json()
                    print(f"   Updated area data: {json.dumps(updated_area, indent=2)}")
                    print(f"   Name field: {updated_area.get('name')}")
                except:
                    print("   Could not parse JSON response")
        
        # Step 3: Check current area state
        print(f"\n3. Checking current area state...")
        async with self.session.get(f"{API_BASE}/areas", headers=self.get_auth_headers()) as response:
            if response.status == 200:
                areas = await response.json()
                debug_area = next((area for area in areas if area['id'] == area_id), None)
                if debug_area:
                    print(f"   Current area state: {json.dumps(debug_area, indent=2)}")
                else:
                    print("   Area not found in areas list")
            else:
                print(f"   Failed to retrieve areas: {response.status}")
        
        # Step 4: Clean up
        print(f"\n4. Cleaning up test area...")
        async with self.session.delete(f"{API_BASE}/areas/{area_id}", headers=self.get_auth_headers()) as response:
            if response.status == 200:
                print("✅ Test area deleted successfully")
            else:
                print(f"⚠️ Failed to delete test area: {response.status}")
        
    async def run_debug_test(self):
        """Run the debug test"""
        print("🔍 Starting Areas Update Debug Test...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print(f"👤 Test User: {self.test_user_email}")
        
        await self.setup_session()
        
        try:
            # Authentication
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed with debug test")
                return
                
            # Run debug test
            await self.debug_area_update()
            
        finally:
            await self.cleanup_session()

async def main():
    """Main function to run the debug test"""
    test_suite = AreasUpdateDebugTest()
    await test_suite.run_debug_test()

if __name__ == "__main__":
    asyncio.run(main())