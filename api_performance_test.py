#!/usr/bin/env python3
"""
API Performance Test - Verify all endpoints are under 201ms
Testing all critical API endpoints for Aurum Life application
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

class APIPerformanceTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.results = []
        
    async def setup_session(self):
        """Initialize aiohttp session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        )
        
    async def cleanup_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            
    async def authenticate(self) -> bool:
        """Authenticate and get JWT token"""
        try:
            print("🔐 Authenticating user...")
            
            start_time = time.time()
            async with self.session.post(
                f"{BASE_URL}/auth/login",
                json=TEST_USER_CREDENTIALS,
                headers={"Content-Type": "application/json"}
            ) as response:
                duration = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    print(f"✅ Authentication successful ({duration:.1f}ms)")
                    return True
                else:
                    print(f"❌ Authentication failed: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
            
    async def test_endpoint(self, method: str, endpoint: str, description: str) -> Tuple[str, float, bool, int]:
        """Test a single endpoint and measure response time"""
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
            
        try:
            start_time = time.time()
            
            if method.upper() == "GET":
                async with self.session.get(f"{BASE_URL}{endpoint}", headers=headers) as response:
                    duration = (time.time() - start_time) * 1000
                    status = response.status
                    
            elif method.upper() == "POST":
                async with self.session.post(f"{BASE_URL}{endpoint}", headers=headers) as response:
                    duration = (time.time() - start_time) * 1000
                    status = response.status
                    
            success = status < 400
            under_target = duration < TARGET_RESPONSE_TIME
            
            status_emoji = "✅" if success else "❌"
            perf_emoji = "🚀" if under_target else "🐌"
            
            print(f"{status_emoji}{perf_emoji} {description}: {duration:.1f}ms (Status: {status})")
            
            return endpoint, duration, under_target, status
            
        except Exception as e:
            print(f"❌ {description}: ERROR - {e}")
            return endpoint, 999.9, False, 500

    async def run_performance_tests(self):
        """Run comprehensive API performance tests"""
        
        print("🎯 Starting API Performance Tests")
        print(f"📊 Target: All endpoints under {TARGET_RESPONSE_TIME}ms")
        print("=" * 60)
        
        # Test endpoints (endpoint, method, description)
        test_endpoints = [
            ("/health", "GET", "Health Check"),
            ("/", "GET", "Root Endpoint"),
            ("/auth/me", "GET", "Current User Profile"),
            ("/dashboard", "GET", "Dashboard Data"),
            ("/pillars", "GET", "Pillars List"),
            ("/areas", "GET", "Areas List"),
            ("/areas?include_projects=true", "GET", "Areas with Projects"),
            ("/projects", "GET", "Projects List"),
            ("/tasks", "GET", "Tasks List"),
            ("/today", "GET", "Today View"),
            ("/insights", "GET", "Insights Data"),
            ("/performance", "GET", "Performance Metrics"),
        ]
        
        # Run tests
        for endpoint, method, description in test_endpoints:
            result = await self.test_endpoint(method, endpoint, description)
            self.results.append({
                "endpoint": result[0],
                "duration_ms": result[1],
                "success": result[2],
                "status_code": result[3],
                "description": description
            })
            
            # Brief pause between requests
            await asyncio.sleep(0.1)
            
        print("=" * 60)
        
    def analyze_results(self):
        """Analyze and report test results"""
        
        successful_tests = [r for r in self.results if r["success"]]
        failed_tests = [r for r in self.results if not r["success"]]
        under_target = [r for r in self.results if r["duration_ms"] < TARGET_RESPONSE_TIME and r["success"]]
        
        total_tests = len(self.results)
        success_rate = (len(successful_tests) / total_tests) * 100 if total_tests > 0 else 0
        performance_rate = (len(under_target) / len(successful_tests)) * 100 if successful_tests else 0
        
        print("\n📊 PERFORMANCE TEST RESULTS")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {len(successful_tests)} ({success_rate:.1f}%)")
        print(f"Under {TARGET_RESPONSE_TIME}ms: {len(under_target)} ({performance_rate:.1f}%)")
        print(f"Failed: {len(failed_tests)}")
        
        if successful_tests:
            avg_response_time = sum(r["duration_ms"] for r in successful_tests) / len(successful_tests)
            fastest = min(successful_tests, key=lambda x: x["duration_ms"])
            slowest = max(successful_tests, key=lambda x: x["duration_ms"])
            
            print(f"\n⚡ PERFORMANCE METRICS:")
            print(f"Average Response Time: {avg_response_time:.1f}ms")
            print(f"Fastest Endpoint: {fastest['description']} ({fastest['duration_ms']:.1f}ms)")
            print(f"Slowest Endpoint: {slowest['description']} ({slowest['duration_ms']:.1f}ms)")
            
        # Show endpoints over target
        over_target = [r for r in successful_tests if r["duration_ms"] >= TARGET_RESPONSE_TIME]
        if over_target:
            print(f"\n🐌 ENDPOINTS OVER {TARGET_RESPONSE_TIME}ms TARGET:")
            for result in over_target:
                print(f"  - {result['description']}: {result['duration_ms']:.1f}ms")
        else:
            print(f"\n🚀 ALL SUCCESSFUL ENDPOINTS UNDER {TARGET_RESPONSE_TIME}ms TARGET!")
            
        # Show failed endpoints
        if failed_tests:
            print(f"\n❌ FAILED ENDPOINTS:")
            for result in failed_tests:
                print(f"  - {result['description']}: Status {result['status_code']}")
                
        return len(under_target) == len(successful_tests) and len(successful_tests) > 0

async def main():
    """Main test execution"""
    tester = APIPerformanceTester()
    
    try:
        await tester.setup_session()
        
        # Authenticate first
        if not await tester.authenticate():
            print("❌ Authentication failed - cannot proceed with protected endpoints")
            return False
            
        # Run all performance tests
        await tester.run_performance_tests()
        
        # Analyze results
        all_under_target = tester.analyze_results()
        
        if all_under_target:
            print(f"\n🎉 SUCCESS: All API endpoints are under {TARGET_RESPONSE_TIME}ms!")
            return True
        else:
            print(f"\n⚠️  ATTENTION: Some endpoints exceed {TARGET_RESPONSE_TIME}ms target")
            return False
            
    except Exception as e:
        print(f"❌ Test execution error: {e}")
        return False
        
    finally:
        await tester.cleanup_session()

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)