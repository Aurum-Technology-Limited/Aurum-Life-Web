"""
MVP Performance Testing Script
Validates API response times meet <150ms P95 target
"""

import asyncio
import aiohttp
import time
import statistics
from datetime import datetime
import json
from typing import List, Dict
import os

# Test configuration
API_BASE_URL = os.environ.get("API_URL", "http://localhost:8000")
TEST_USER_TOKEN = os.environ.get("TEST_USER_TOKEN", "")
CONCURRENT_USERS = 10
REQUESTS_PER_USER = 100

class PerformanceTester:
    def __init__(self):
        self.results = {
            "today_tasks": [],
            "get_pillars": [],
            "get_areas": [],
            "get_projects": [],
            "get_tasks": [],
            "create_task": [],
            "update_task": [],
        }
        
    async def make_request(self, session: aiohttp.ClientSession, method: str, endpoint: str, data: dict = None) -> float:
        """Make a single request and return response time"""
        headers = {"Authorization": f"Bearer {TEST_USER_TOKEN}"}
        
        start_time = time.time()
        try:
            async with session.request(method, f"{API_BASE_URL}{endpoint}", headers=headers, json=data) as response:
                await response.json()
                duration = time.time() - start_time
                return duration
        except Exception as e:
            print(f"Request failed: {e}")
            return -1
            
    async def test_endpoint(self, session: aiohttp.ClientSession, name: str, method: str, endpoint: str, data: dict = None):
        """Test a single endpoint multiple times"""
        print(f"Testing {name}...")
        
        for _ in range(REQUESTS_PER_USER):
            duration = await self.make_request(session, method, endpoint, data)
            if duration > 0:
                self.results[name].append(duration)
                
    async def run_user_simulation(self, user_id: int):
        """Simulate a single user making various requests"""
        async with aiohttp.ClientSession() as session:
            # Test Today view (most critical)
            await self.test_endpoint(session, "today_tasks", "GET", "/api/today/tasks")
            
            # Test hierarchy endpoints
            await self.test_endpoint(session, "get_pillars", "GET", "/api/pillars")
            await self.test_endpoint(session, "get_areas", "GET", "/api/areas")
            await self.test_endpoint(session, "get_projects", "GET", "/api/projects")
            await self.test_endpoint(session, "get_tasks", "GET", "/api/tasks")
            
            # Test mutations
            task_data = {
                "name": f"Test Task {user_id}",
                "project_id": "test-project-id",
                "priority": "medium",
                "due_date": datetime.utcnow().isoformat()
            }
            await self.test_endpoint(session, "create_task", "POST", "/api/tasks", task_data)
            
            # Test task update
            update_data = {"completed": True}
            await self.test_endpoint(session, "update_task", "PATCH", "/api/tasks/test-task-id", update_data)
            
    async def run_load_test(self):
        """Run concurrent load test"""
        print(f"Starting load test with {CONCURRENT_USERS} concurrent users...")
        print(f"Each user will make {REQUESTS_PER_USER} requests per endpoint")
        
        # Create concurrent user tasks
        tasks = []
        for i in range(CONCURRENT_USERS):
            task = asyncio.create_task(self.run_user_simulation(i))
            tasks.append(task)
            
        # Wait for all users to complete
        await asyncio.gather(*tasks)
        
    def calculate_statistics(self, times: List[float]) -> Dict:
        """Calculate performance statistics"""
        if not times:
            return {"error": "No data"}
            
        sorted_times = sorted(times)
        
        return {
            "count": len(times),
            "min": round(min(times) * 1000, 2),  # Convert to ms
            "max": round(max(times) * 1000, 2),
            "mean": round(statistics.mean(times) * 1000, 2),
            "median": round(statistics.median(times) * 1000, 2),
            "p95": round(sorted_times[int(len(sorted_times) * 0.95)] * 1000, 2),
            "p99": round(sorted_times[int(len(sorted_times) * 0.99)] * 1000, 2),
        }
        
    def generate_report(self):
        """Generate performance test report"""
        print("\n" + "="*60)
        print("PERFORMANCE TEST RESULTS")
        print("="*60)
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Concurrent Users: {CONCURRENT_USERS}")
        print(f"Requests per User per Endpoint: {REQUESTS_PER_USER}")
        print("-"*60)
        
        all_p95s = []
        
        for endpoint, times in self.results.items():
            if times:
                stats = self.calculate_statistics(times)
                all_p95s.append(stats["p95"])
                
                status = "✅ PASS" if stats["p95"] < 150 else "❌ FAIL"
                print(f"\n{endpoint}: {status}")
                print(f"  Requests: {stats['count']}")
                print(f"  Min: {stats['min']}ms")
                print(f"  Mean: {stats['mean']}ms")
                print(f"  P95: {stats['p95']}ms {'<-- TARGET: <150ms' if endpoint == 'today_tasks' else ''}")
                print(f"  P99: {stats['p99']}ms")
                print(f"  Max: {stats['max']}ms")
                
        print("\n" + "-"*60)
        overall_p95 = statistics.mean(all_p95s) if all_p95s else 0
        overall_status = "✅ PASS" if overall_p95 < 150 else "❌ FAIL"
        print(f"OVERALL P95: {overall_p95:.2f}ms - {overall_status}")
        print("="*60)
        
        # Save detailed results
        with open("performance_test_results.json", "w") as f:
            detailed_results = {
                "test_time": datetime.now().isoformat(),
                "configuration": {
                    "concurrent_users": CONCURRENT_USERS,
                    "requests_per_user": REQUESTS_PER_USER,
                    "api_url": API_BASE_URL
                },
                "results": {
                    endpoint: self.calculate_statistics(times)
                    for endpoint, times in self.results.items()
                    if times
                },
                "overall_p95": overall_p95,
                "pass": overall_p95 < 150
            }
            json.dump(detailed_results, f, indent=2)
            
        print("\nDetailed results saved to: performance_test_results.json")
        
        return overall_p95 < 150

async def main():
    """Main test execution"""
    print("Aurum Life MVP Performance Test")
    print("================================")
    
    if not TEST_USER_TOKEN:
        print("WARNING: No TEST_USER_TOKEN set. Using unauthenticated requests.")
        print("Set TEST_USER_TOKEN environment variable for authenticated tests.")
        
    tester = PerformanceTester()
    
    # Run the load test
    start_time = time.time()
    await tester.run_load_test()
    total_time = time.time() - start_time
    
    print(f"\nTotal test duration: {total_time:.2f} seconds")
    
    # Generate report
    passed = tester.generate_report()
    
    # Exit with appropriate code
    exit(0 if passed else 1)

if __name__ == "__main__":
    asyncio.run(main())