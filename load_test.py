#!/usr/bin/env python3
"""
Load Testing Script for Aurum Life Backend
Tests API performance under various load conditions
"""

import asyncio
import aiohttp
import time
import statistics
import json
from datetime import datetime
from typing import List, Dict, Any
import random

class LoadTester:
    def __init__(self, base_url="http://localhost:8000/api"):
        self.base_url = base_url
        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "scenarios": {},
            "summary": {},
            "bottlenecks": [],
            "recommendations": []
        }
        
        # Test endpoints with expected response times
        self.endpoints = [
            {"path": "/health", "method": "GET", "expected_ms": 50},
            {"path": "/pillars", "method": "GET", "expected_ms": 200},
            {"path": "/areas", "method": "GET", "expected_ms": 200},
            {"path": "/projects", "method": "GET", "expected_ms": 300},
            {"path": "/tasks", "method": "GET", "expected_ms": 300},
            {"path": "/stats/overview", "method": "GET", "expected_ms": 500},
            {"path": "/journal/entries", "method": "GET", "expected_ms": 400},
        ]
    
    async def run_load_tests(self):
        """Execute comprehensive load testing scenarios"""
        print("🚀 Starting Load Testing for Aurum Life Backend...\n")
        
        # Test 1: Baseline Performance (Single User)
        print("📊 Test 1: Baseline Performance (Single User)")
        await self.test_baseline_performance()
        
        # Test 2: Concurrent Users (Moderate Load)
        print("\n📊 Test 2: Concurrent Users Test (10 users)")
        await self.test_concurrent_users(num_users=10)
        
        # Test 3: Stress Test (High Load)
        print("\n📊 Test 3: Stress Test (50 concurrent users)")
        await self.test_stress_load(num_users=50)
        
        # Test 4: Spike Test
        print("\n📊 Test 4: Spike Test (Sudden load increase)")
        await self.test_spike_load()
        
        # Test 5: Sustained Load Test
        print("\n📊 Test 5: Sustained Load Test (30 seconds)")
        await self.test_sustained_load(duration=30)
        
        # Generate analysis and recommendations
        self.analyze_results()
        self.save_results()
        
        return self.results
    
    async def make_request(self, session: aiohttp.ClientSession, endpoint: Dict) -> Dict:
        """Make a single HTTP request and measure performance"""
        start_time = time.time()
        
        try:
            async with session.request(
                method=endpoint["method"],
                url=f"{self.base_url}{endpoint['path']}",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                await response.read()
                end_time = time.time()
                
                return {
                    "endpoint": endpoint["path"],
                    "status": response.status,
                    "response_time_ms": (end_time - start_time) * 1000,
                    "success": 200 <= response.status < 300,
                    "size_bytes": len(await response.read()) if response.status == 200 else 0
                }
        except asyncio.TimeoutError:
            return {
                "endpoint": endpoint["path"],
                "status": "timeout",
                "response_time_ms": 10000,
                "success": False,
                "error": "Request timeout"
            }
        except Exception as e:
            return {
                "endpoint": endpoint["path"],
                "status": "error",
                "response_time_ms": (time.time() - start_time) * 1000,
                "success": False,
                "error": str(e)
            }
    
    async def test_baseline_performance(self):
        """Test single-user performance for each endpoint"""
        results = []
        
        async with aiohttp.ClientSession() as session:
            for endpoint in self.endpoints:
                result = await self.make_request(session, endpoint)
                results.append(result)
                
                # Check against expected performance
                if result["success"] and result["response_time_ms"] > endpoint["expected_ms"]:
                    self.results["bottlenecks"].append({
                        "endpoint": endpoint["path"],
                        "actual_ms": result["response_time_ms"],
                        "expected_ms": endpoint["expected_ms"],
                        "severity": "medium" if result["response_time_ms"] < endpoint["expected_ms"] * 2 else "high"
                    })
        
        self.results["scenarios"]["baseline"] = {
            "description": "Single user performance test",
            "results": results,
            "avg_response_time_ms": statistics.mean([r["response_time_ms"] for r in results if r["success"]])
        }
        
        # Print results
        print(f"Average response time: {self.results['scenarios']['baseline']['avg_response_time_ms']:.2f} ms")
        for result in results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['endpoint']}: {result['response_time_ms']:.2f} ms")
    
    async def test_concurrent_users(self, num_users: int):
        """Test performance with multiple concurrent users"""
        all_results = []
        
        async with aiohttp.ClientSession() as session:
            # Simulate concurrent users
            tasks = []
            for _ in range(num_users):
                for endpoint in self.endpoints:
                    tasks.append(self.make_request(session, endpoint))
            
            start_time = time.time()
            results = await asyncio.gather(*tasks)
            total_time = time.time() - start_time
            
            all_results.extend(results)
        
        # Calculate metrics
        successful_requests = [r for r in all_results if r["success"]]
        failed_requests = [r for r in all_results if not r["success"]]
        
        self.results["scenarios"]["concurrent_users"] = {
            "description": f"{num_users} concurrent users",
            "total_requests": len(all_results),
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "total_time_seconds": total_time,
            "requests_per_second": len(all_results) / total_time,
            "avg_response_time_ms": statistics.mean([r["response_time_ms"] for r in successful_requests]) if successful_requests else 0,
            "p95_response_time_ms": self.calculate_percentile([r["response_time_ms"] for r in successful_requests], 95) if successful_requests else 0,
            "p99_response_time_ms": self.calculate_percentile([r["response_time_ms"] for r in successful_requests], 99) if successful_requests else 0,
        }
        
        print(f"Total requests: {len(all_results)}")
        print(f"Successful: {len(successful_requests)} ({len(successful_requests)/len(all_results)*100:.1f}%)")
        print(f"Failed: {len(failed_requests)}")
        print(f"Requests/second: {len(all_results) / total_time:.2f}")
        print(f"Avg response time: {self.results['scenarios']['concurrent_users']['avg_response_time_ms']:.2f} ms")
        print(f"P95 response time: {self.results['scenarios']['concurrent_users']['p95_response_time_ms']:.2f} ms")
    
    async def test_stress_load(self, num_users: int):
        """Stress test with high concurrent load"""
        all_results = []
        
        async with aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=100)
        ) as session:
            # Create high load
            tasks = []
            for _ in range(num_users):
                # Each user makes multiple requests
                for _ in range(3):
                    endpoint = random.choice(self.endpoints)
                    tasks.append(self.make_request(session, endpoint))
            
            start_time = time.time()
            results = await asyncio.gather(*tasks)
            total_time = time.time() - start_time
            
            all_results.extend(results)
        
        # Analyze stress test results
        successful_requests = [r for r in all_results if r["success"]]
        failed_requests = [r for r in all_results if not r["success"]]
        timeout_requests = [r for r in all_results if r.get("status") == "timeout"]
        
        self.results["scenarios"]["stress_test"] = {
            "description": f"Stress test with {num_users} concurrent users",
            "total_requests": len(all_results),
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "timeout_requests": len(timeout_requests),
            "error_rate": len(failed_requests) / len(all_results) * 100,
            "avg_response_time_ms": statistics.mean([r["response_time_ms"] for r in successful_requests]) if successful_requests else 0,
        }
        
        # Check for performance degradation
        if len(failed_requests) / len(all_results) > 0.1:  # More than 10% failure
            self.results["bottlenecks"].append({
                "test": "stress_test",
                "issue": "High failure rate under load",
                "error_rate": f"{len(failed_requests) / len(all_results) * 100:.1f}%",
                "severity": "critical"
            })
        
        print(f"Total requests: {len(all_results)}")
        print(f"Error rate: {self.results['scenarios']['stress_test']['error_rate']:.1f}%")
        print(f"Timeouts: {len(timeout_requests)}")
    
    async def test_spike_load(self):
        """Test system behavior under sudden load spike"""
        results_before = []
        results_during = []
        results_after = []
        
        async with aiohttp.ClientSession() as session:
            # Normal load
            print("  Phase 1: Normal load (5 users)...")
            for _ in range(5):
                for endpoint in self.endpoints[:3]:  # Test subset
                    result = await self.make_request(session, endpoint)
                    results_before.append(result)
            
            # Spike load
            print("  Phase 2: Spike load (30 users)...")
            spike_tasks = []
            for _ in range(30):
                for endpoint in self.endpoints[:3]:
                    spike_tasks.append(self.make_request(session, endpoint))
            
            spike_results = await asyncio.gather(*spike_tasks)
            results_during.extend(spike_results)
            
            # Recovery phase
            print("  Phase 3: Recovery (5 users)...")
            await asyncio.sleep(2)  # Allow system to recover
            for _ in range(5):
                for endpoint in self.endpoints[:3]:
                    result = await self.make_request(session, endpoint)
                    results_after.append(result)
        
        # Analyze spike impact
        avg_before = statistics.mean([r["response_time_ms"] for r in results_before if r["success"]])
        avg_during = statistics.mean([r["response_time_ms"] for r in results_during if r["success"]])
        avg_after = statistics.mean([r["response_time_ms"] for r in results_after if r["success"]])
        
        self.results["scenarios"]["spike_test"] = {
            "description": "Sudden load spike test",
            "avg_response_before_spike_ms": avg_before,
            "avg_response_during_spike_ms": avg_during,
            "avg_response_after_spike_ms": avg_after,
            "performance_degradation": (avg_during - avg_before) / avg_before * 100,
            "recovery_time_assessment": "Good" if avg_after < avg_before * 1.2 else "Poor"
        }
        
        print(f"Response time before spike: {avg_before:.2f} ms")
        print(f"Response time during spike: {avg_during:.2f} ms")
        print(f"Response time after spike: {avg_after:.2f} ms")
        print(f"Performance degradation: {self.results['scenarios']['spike_test']['performance_degradation']:.1f}%")
    
    async def test_sustained_load(self, duration: int):
        """Test performance under sustained load"""
        print(f"  Running sustained load for {duration} seconds...")
        
        results_over_time = []
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            while time.time() - start_time < duration:
                # Maintain 10 concurrent users
                tasks = []
                for _ in range(10):
                    endpoint = random.choice(self.endpoints)
                    tasks.append(self.make_request(session, endpoint))
                
                batch_results = await asyncio.gather(*tasks)
                results_over_time.append({
                    "timestamp": time.time() - start_time,
                    "results": batch_results
                })
                
                await asyncio.sleep(1)  # 1 second between batches
        
        # Analyze performance over time
        response_times_by_second = []
        for batch in results_over_time:
            successful = [r["response_time_ms"] for r in batch["results"] if r["success"]]
            if successful:
                response_times_by_second.append(statistics.mean(successful))
        
        # Check for performance degradation
        first_half = response_times_by_second[:len(response_times_by_second)//2]
        second_half = response_times_by_second[len(response_times_by_second)//2:]
        
        degradation = 0
        if first_half and second_half:
            avg_first = statistics.mean(first_half)
            avg_second = statistics.mean(second_half)
            degradation = (avg_second - avg_first) / avg_first * 100
        
        self.results["scenarios"]["sustained_load"] = {
            "description": f"Sustained load test ({duration}s)",
            "duration_seconds": duration,
            "avg_response_time_ms": statistics.mean(response_times_by_second) if response_times_by_second else 0,
            "performance_degradation_percent": degradation,
            "stability": "Stable" if abs(degradation) < 10 else "Unstable"
        }
        
        print(f"Average response time: {self.results['scenarios']['sustained_load']['avg_response_time_ms']:.2f} ms")
        print(f"Performance degradation: {degradation:.1f}%")
        print(f"Stability: {self.results['scenarios']['sustained_load']['stability']}")
    
    def calculate_percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def analyze_results(self):
        """Analyze test results and generate recommendations"""
        recommendations = []
        
        # Check baseline performance
        if "baseline" in self.results["scenarios"]:
            avg_baseline = self.results["scenarios"]["baseline"]["avg_response_time_ms"]
            if avg_baseline > 300:
                recommendations.append({
                    "priority": "HIGH",
                    "category": "Performance",
                    "issue": "Slow baseline performance",
                    "details": f"Average response time {avg_baseline:.0f}ms exceeds 300ms target",
                    "recommendation": "Implement caching layer and optimize database queries"
                })
        
        # Check concurrent user performance
        if "concurrent_users" in self.results["scenarios"]:
            scenario = self.results["scenarios"]["concurrent_users"]
            if scenario["p95_response_time_ms"] > 1000:
                recommendations.append({
                    "priority": "HIGH",
                    "category": "Scalability",
                    "issue": "Poor performance under concurrent load",
                    "details": f"P95 response time {scenario['p95_response_time_ms']:.0f}ms exceeds 1000ms",
                    "recommendation": "Add connection pooling and implement request queuing"
                })
        
        # Check stress test results
        if "stress_test" in self.results["scenarios"]:
            scenario = self.results["scenarios"]["stress_test"]
            if scenario["error_rate"] > 5:
                recommendations.append({
                    "priority": "CRITICAL",
                    "category": "Reliability",
                    "issue": "High error rate under stress",
                    "details": f"Error rate {scenario['error_rate']:.1f}% exceeds 5% threshold",
                    "recommendation": "Implement rate limiting, circuit breakers, and auto-scaling"
                })
        
        # Check for bottlenecks
        critical_bottlenecks = [b for b in self.results["bottlenecks"] if b.get("severity") == "critical"]
        if critical_bottlenecks:
            recommendations.append({
                "priority": "CRITICAL",
                "category": "Bottlenecks",
                "issue": "Critical performance bottlenecks detected",
                "endpoints": [b["endpoint"] for b in critical_bottlenecks[:5]],
                "recommendation": "Focus optimization efforts on these endpoints"
            })
        
        self.results["recommendations"] = sorted(
            recommendations,
            key=lambda x: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}[x["priority"]]
        )
    
    def save_results(self):
        """Save test results to file"""
        output_file = f"/workspace/load_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n✅ Load testing complete! Results saved to: {output_file}")
        
        # Print summary
        print("\n📊 LOAD TEST SUMMARY")
        print("=" * 60)
        
        # Performance summary
        for scenario_name, scenario_data in self.results["scenarios"].items():
            print(f"\n{scenario_name.upper().replace('_', ' ')}:")
            if "avg_response_time_ms" in scenario_data:
                print(f"  Average Response Time: {scenario_data['avg_response_time_ms']:.2f} ms")
            if "error_rate" in scenario_data:
                print(f"  Error Rate: {scenario_data['error_rate']:.1f}%")
            if "requests_per_second" in scenario_data:
                print(f"  Throughput: {scenario_data['requests_per_second']:.2f} req/s")
        
        # Recommendations
        if self.results["recommendations"]:
            print(f"\n🚨 CRITICAL ISSUES: {len([r for r in self.results['recommendations'] if r['priority'] == 'CRITICAL'])}")
            print(f"⚠️  HIGH PRIORITY: {len([r for r in self.results['recommendations'] if r['priority'] == 'HIGH'])}")
            
            print("\nTOP RECOMMENDATIONS:")
            for rec in self.results["recommendations"][:3]:
                print(f"\n[{rec['priority']}] {rec['issue']}")
                print(f"  → {rec['recommendation']}")

async def main():
    # Check if backend is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/api/health", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                if resp.status != 200:
                    print("❌ Backend server is not responding. Please start it first.")
                    return
    except:
        print("❌ Cannot connect to backend server at http://localhost:8000")
        print("Please start the backend server first with: cd backend && python server.py")
        return
    
    tester = LoadTester()
    await tester.run_load_tests()

if __name__ == "__main__":
    asyncio.run(main())