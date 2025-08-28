#!/usr/bin/env python3
"""
Test API performance after cleanup
"""

import asyncio
import aiohttp
import time

async def test_api_performance():
    """Test API performance"""
    
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
        
        # Test various endpoints for performance
        endpoints = [
            ("/", "Root"),
            ("/api/health", "Health Check"),
            ("/api/pillars", "Pillars"),
            ("/api/areas", "Areas"),
            ("/api/projects", "Projects"),
            ("/api/analytics/alignment-snapshot", "Analytics Snapshot")
        ]
        
        print(f"\n⚡ PERFORMANCE TESTING")
        print("="*50)
        
        for endpoint, name in endpoints:
            # Test multiple times to get average
            times = []
            for i in range(3):
                start_time = time.time()
                
                url = f"http://localhost:8001{endpoint}"
                request_headers = headers if endpoint.startswith("/api") and endpoint != "/api/health" else {}
                
                async with session.get(url, headers=request_headers) as response:
                    duration = (time.time() - start_time) * 1000
                    times.append(duration)
                    
                    if response.status == 200:
                        status = "✅"
                    else:
                        status = "❌"
                        
                await asyncio.sleep(0.1)  # Brief pause between requests
            
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            print(f"{status} {name}: {avg_time:.1f}ms avg (range: {min_time:.1f}-{max_time:.1f}ms)")
        
        print(f"\n🎯 All endpoint performance tests completed!")
        
    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(test_api_performance())