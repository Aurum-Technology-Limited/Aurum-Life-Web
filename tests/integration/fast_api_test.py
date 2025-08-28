#!/usr/bin/env python3
"""
FAST API Performance Test - Multiple runs to check consistency
"""

import asyncio
import aiohttp
import time
import json
from typing import Dict, List, Tuple

# Configuration  
BASE_URL = "http://localhost:8001/api"
TARGET_RESPONSE_TIME = 201  # milliseconds
TEST_USER_CREDENTIALS = {
    "email": "nav.test@aurumlife.com", 
    "password": "testpassword123"
}

async def quick_performance_test():
    """Run a quick performance test of critical endpoints"""
    
    session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5))
    
    try:
        # Authenticate
        async with session.post(f"{BASE_URL}/auth/login", json=TEST_USER_CREDENTIALS) as response:
            if response.status != 200:
                print("❌ Authentication failed")
                return
            
            data = await response.json()
            auth_token = data.get("access_token")
            
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Test critical endpoints
        endpoints = [
            ("/dashboard", "Dashboard"),
            ("/today", "Today View"), 
            ("/pillars", "Pillars"),
            ("/areas", "Areas"),
            ("/projects", "Projects"),
            ("/tasks", "Tasks")
        ]
        
        results = []
        for endpoint, name in endpoints:
            start_time = time.time()
            async with session.get(f"{BASE_URL}{endpoint}", headers=headers) as response:
                duration = (time.time() - start_time) * 1000
                success = response.status == 200
                
                status_emoji = "✅" if success else "❌"
                perf_emoji = "🚀" if duration < TARGET_RESPONSE_TIME else "🐌"
                
                print(f"{status_emoji}{perf_emoji} {name}: {duration:.1f}ms")
                results.append((name, duration, success))
        
        # Summary
        successful = [r for r in results if r[2]]
        under_target = [r for r in successful if r[1] < TARGET_RESPONSE_TIME]
        
        avg_time = sum(r[1] for r in successful) / len(successful) if successful else 0
        
        print(f"\n📊 SUMMARY:")
        print(f"Average: {avg_time:.1f}ms")
        print(f"Under {TARGET_RESPONSE_TIME}ms: {len(under_target)}/{len(successful)}")
        
        return len(under_target) == len(successful)
        
    finally:
        await session.close()

async def run_multiple_tests(num_runs=3):
    """Run multiple performance tests to check consistency"""
    print(f"🎯 Running {num_runs} performance tests for consistency check")
    print("=" * 60)
    
    results = []
    for i in range(num_runs):
        print(f"\n🔄 Run {i+1}/{num_runs}:")
        success = await quick_performance_test()
        results.append(success)
        
        if i < num_runs - 1:
            await asyncio.sleep(1)  # Brief pause between runs
    
    print("\n" + "=" * 60)
    success_count = sum(results)
    print(f"🎯 FINAL RESULT: {success_count}/{num_runs} runs had all endpoints under {TARGET_RESPONSE_TIME}ms")
    
    if success_count == num_runs:
        print(f"🎉 EXCELLENT: All {num_runs} runs achieved the performance target!")
    elif success_count > num_runs // 2:
        print(f"✅ GOOD: {success_count}/{num_runs} runs achieved the performance target")
    else:
        print(f"⚠️ NEEDS WORK: Only {success_count}/{num_runs} runs achieved the performance target")

if __name__ == "__main__":
    asyncio.run(run_multiple_tests(3))