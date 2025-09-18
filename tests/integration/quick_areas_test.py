#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import time
import statistics
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

class QuickAreasTest:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "nav.test@aurumlife.com"
        self.test_user_password = "testpassword123"
        
    async def setup_session(self):
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        if self.session:
            await self.session.close()
            
    async def authenticate(self):
        try:
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data["access_token"]
                    return True
                else:
                    print(f"❌ Auth failed: {response.status}")
                    return False
        except Exception as e:
            print(f"❌ Auth error: {e}")
            return False
            
    def get_auth_headers(self):
        return {"Authorization": f"Bearer {self.auth_token}"}
        
    async def quick_areas_test(self):
        print("🚀 Quick Areas API Test")
        
        await self.setup_session()
        
        try:
            if not await self.authenticate():
                return
                
            # Warm-up call
            print("\n🔥 Warm-up call...")
            async with self.session.get(f"{API_BASE}/areas", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    print("✅ Warm-up successful")
                else:
                    print(f"❌ Warm-up failed: {response.status}")
                    return
                    
            # Performance test calls
            print("\n📊 Performance test calls:")
            times = []
            
            for i in range(10):
                start_time = time.time()
                async with self.session.get(f"{API_BASE}/areas", headers=self.get_auth_headers()) as response:
                    end_time = time.time()
                    response_time_ms = (end_time - start_time) * 1000
                    times.append(response_time_ms)
                    
                    if response.status == 200:
                        areas = await response.json()
                        
                        # Check first area for importance field
                        if areas and 'importance' in areas[0]:
                            importance_val = areas[0]['importance']
                            importance_type = type(importance_val).__name__
                            print(f"Call {i+1:2d}: {response_time_ms:6.1f}ms | {len(areas):2d} areas | importance: {importance_val} ({importance_type})")
                        else:
                            print(f"Call {i+1:2d}: {response_time_ms:6.1f}ms | {len(areas):2d} areas | no importance field")
                    else:
                        print(f"Call {i+1:2d}: FAILED {response.status}")
                        
            # Statistics
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            median_time = statistics.median(times)
            
            print(f"\n📈 Results:")
            print(f"   Average: {avg_time:.1f}ms")
            print(f"   Median:  {median_time:.1f}ms")
            print(f"   Min:     {min_time:.1f}ms")
            print(f"   Max:     {max_time:.1f}ms")
            print(f"   Baseline: 430ms")
            
            if avg_time < 430:
                improvement = 430 - avg_time
                print(f"   🎉 IMPROVED by {improvement:.1f}ms ({improvement/430*100:.1f}%)")
            else:
                regression = avg_time - 430
                print(f"   ⚠️  SLOWER by {regression:.1f}ms ({regression/430*100:.1f}%)")
                
        finally:
            await self.cleanup_session()

async def main():
    test = QuickAreasTest()
    await test.quick_areas_test()

if __name__ == "__main__":
    asyncio.run(main())