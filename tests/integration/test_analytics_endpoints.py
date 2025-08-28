#!/usr/bin/env python3
"""
Test Analytics Endpoints - Verify MVP v1.2 functionality
"""

import asyncio
import aiohttp
import json

class AnalyticsEndpointTest:
    def __init__(self):
        self.base_url = "http://localhost:8001/api"
        self.session = None
        self.auth_token = None
        
    async def setup(self):
        """Setup and authenticate"""
        self.session = aiohttp.ClientSession()
        
        # Login to get token
        login_data = {
            "email": "nav.test@aurumlife.com",
            "password": "testpassword123"
        }
        
        async with self.session.post(f"{self.base_url}/auth/login", json=login_data) as response:
            if response.status == 200:
                data = await response.json()
                self.auth_token = data["access_token"]
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status}")
                return False
                
    async def test_analytics_endpoints(self):
        """Test all analytics endpoints"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        print("\n📊 TESTING ANALYTICS ENDPOINTS")
        print("="*50)
        
        # Test 1: Lifetime Stats
        print("\n1️⃣ Testing /api/analytics/lifetime-stats")
        async with self.session.get(f"{self.base_url}/analytics/lifetime-stats", headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Lifetime Stats Response:")
                print(f"   Tasks Completed: {data.get('total_tasks_completed', 'N/A')}")
                print(f"   Projects Completed: {data.get('total_projects_completed', 'N/A')}")
            else:
                error_text = await response.text()
                print(f"❌ Lifetime Stats Failed: {response.status} - {error_text}")
        
        # Test 2: Pillar Alignment
        print("\n2️⃣ Testing /api/analytics/pillar-alignment")
        async with self.session.get(f"{self.base_url}/analytics/pillar-alignment", headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Pillar Alignment Response:")
                print(f"   Number of pillars: {len(data)}")
                for pillar in data:
                    print(f"   - {pillar.get('pillar_name', 'Unknown')}: {pillar.get('task_count', 0)} tasks ({pillar.get('percentage', 0)}%)")
            else:
                error_text = await response.text()
                print(f"❌ Pillar Alignment Failed: {response.status} - {error_text}")
        
        # Test 3: Complete Alignment Snapshot
        print("\n3️⃣ Testing /api/analytics/alignment-snapshot")
        async with self.session.get(f"{self.base_url}/analytics/alignment-snapshot", headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Alignment Snapshot Response:")
                print(f"   Generated at: {data.get('generated_at', 'N/A')}")
                
                lifetime_stats = data.get('lifetime_stats', {})
                print(f"   Lifetime Stats:")
                print(f"     - Tasks: {lifetime_stats.get('total_tasks_completed', 0)}")
                print(f"     - Projects: {lifetime_stats.get('total_projects_completed', 0)}")
                
                pillar_alignment = data.get('pillar_alignment', [])
                print(f"   Pillar Alignment ({len(pillar_alignment)} pillars):")
                for pillar in pillar_alignment:
                    print(f"     - {pillar.get('pillar_name', 'Unknown')}: {pillar.get('percentage', 0)}%")
                    
            else:
                error_text = await response.text()
                print(f"❌ Alignment Snapshot Failed: {response.status} - {error_text}")
        
        print("\n📈 ANALYTICS TESTING COMPLETE")
        
    async def cleanup(self):
        """Cleanup session"""
        if self.session:
            await self.session.close()

async def main():
    """Run analytics endpoint testing"""
    test = AnalyticsEndpointTest()
    
    try:
        if await test.setup():
            await test.test_analytics_endpoints()
        else:
            print("❌ Setup failed, cannot proceed with testing")
    finally:
        await test.cleanup()

if __name__ == "__main__":
    asyncio.run(main())