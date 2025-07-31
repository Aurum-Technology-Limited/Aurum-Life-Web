#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://2a9362a1-0858-4070-86b9-4648da4a94c4.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class ArchitectPerformanceTestSuite:
    """
    🚀 THE ARCHITECT'S FINAL PERFORMANCE VERIFICATION - All Systems Operational
    
    Testing the complete solution for Aurum Life API performance optimization.
    All 5 phases of the definitive solution verification:
    
    ✅ PHASE 1: Celery + Redis infrastructure deployed
    ✅ PHASE 2: Database schema denormalized with scoring fields  
    ✅ PHASE 3: Event-driven scoring engine with Celery tasks
    ✅ PHASE 4: Optimized API endpoints (today, available-tasks)
    ✅ PHASE 5: Database indexes and event triggers integrated
    """
    
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "nav.test@aurumlife.com"
        self.test_user_password = "NavTest123!"
        self.test_results = []
        self.performance_metrics = {}
        self.created_resources = []
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()
            
    async def authenticate(self):
        """Authenticate and get JWT token"""
        try:
            # Try to register user first (in case they don't exist)
            register_data = {
                "username": "navtest",
                "email": self.test_user_email,
                "first_name": "Nav",
                "last_name": "Test",
                "password": self.test_user_password
            }
            
            async with self.session.post(f"{API_BASE}/auth/register", json=register_data) as response:
                if response.status in [200, 400]:  # 400 if user already exists
                    pass
                    
            # Login to get token
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
                    print(f"❌ Authentication failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error details: {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
            
    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.auth_token}"}
        
    async def measure_endpoint_performance(self, endpoint: str, method: str = "GET", data: dict = None, target_ms: int = 1000) -> Dict[str, Any]:
        """Measure endpoint performance and return metrics"""
        try:
            start_time = time.time()
            
            if method == "GET":
                async with self.session.get(f"{API_BASE}{endpoint}", headers=self.get_auth_headers()) as response:
                    response_data = await response.json() if response.status == 200 else None
                    status_code = response.status
            elif method == "POST":
                async with self.session.post(f"{API_BASE}{endpoint}", json=data, headers=self.get_auth_headers()) as response:
                    response_data = await response.json() if response.status == 200 else None
                    status_code = response.status
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000
            
            return {
                "endpoint": endpoint,
                "method": method,
                "status_code": status_code,
                "response_time_ms": round(response_time_ms, 1),
                "target_ms": target_ms,
                "meets_target": response_time_ms <= target_ms,
                "response_data": response_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "endpoint": endpoint,
                "method": method,
                "status_code": 500,
                "response_time_ms": 0,
                "target_ms": target_ms,
                "meets_target": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def test_optimized_today_endpoint(self):
        """Test 1: Optimized /api/today endpoint - TARGET: <200ms response time"""
        print("\n🧪 Test 1: Optimized /api/today endpoint performance")
        
        # Run multiple tests to get average performance
        response_times = []
        successful_requests = 0
        
        for i in range(5):  # Test 5 times for consistency
            metrics = await self.measure_endpoint_performance("/today", target_ms=200)
            
            if metrics["status_code"] == 200:
                response_times.append(metrics["response_time_ms"])
                successful_requests += 1
                print(f"  Request {i+1}: {metrics['response_time_ms']}ms ({'✅' if metrics['meets_target'] else '❌'})")
            else:
                print(f"  Request {i+1}: FAILED (HTTP {metrics['status_code']})")
                
        if successful_requests > 0:
            avg_response_time = sum(response_times) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            
            self.performance_metrics["today_endpoint"] = {
                "average_ms": round(avg_response_time, 1),
                "min_ms": round(min_response_time, 1),
                "max_ms": round(max_response_time, 1),
                "target_ms": 200,
                "success_rate": (successful_requests / 5) * 100,
                "meets_target": avg_response_time <= 200
            }
            
            if avg_response_time <= 200:
                print(f"✅ Today endpoint performance: {avg_response_time:.1f}ms average (target: <200ms)")
                self.test_results.append({
                    "test": "Optimized Today Endpoint Performance",
                    "status": "PASSED",
                    "details": f"Average: {avg_response_time:.1f}ms, Target: <200ms"
                })
            else:
                print(f"❌ Today endpoint performance: {avg_response_time:.1f}ms average (target: <200ms)")
                self.test_results.append({
                    "test": "Optimized Today Endpoint Performance",
                    "status": "FAILED",
                    "reason": f"Average response time {avg_response_time:.1f}ms exceeds 200ms target"
                })
        else:
            print("❌ Today endpoint completely failed")
            self.test_results.append({
                "test": "Optimized Today Endpoint Performance",
                "status": "FAILED",
                "reason": "All requests failed"
            })
    
    async def test_optimized_available_tasks_endpoint(self):
        """Test 2: Optimized /api/today/available-tasks endpoint - TARGET: <100ms response time"""
        print("\n🧪 Test 2: Optimized /api/today/available-tasks endpoint performance")
        
        # Run multiple tests to get average performance
        response_times = []
        successful_requests = 0
        
        for i in range(5):  # Test 5 times for consistency
            metrics = await self.measure_endpoint_performance("/today/available-tasks", target_ms=100)
            
            if metrics["status_code"] == 200:
                response_times.append(metrics["response_time_ms"])
                successful_requests += 1
                print(f"  Request {i+1}: {metrics['response_time_ms']}ms ({'✅' if metrics['meets_target'] else '❌'})")
            else:
                print(f"  Request {i+1}: FAILED (HTTP {metrics['status_code']})")
                
        if successful_requests > 0:
            avg_response_time = sum(response_times) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            
            self.performance_metrics["available_tasks_endpoint"] = {
                "average_ms": round(avg_response_time, 1),
                "min_ms": round(min_response_time, 1),
                "max_ms": round(max_response_time, 1),
                "target_ms": 100,
                "success_rate": (successful_requests / 5) * 100,
                "meets_target": avg_response_time <= 100
            }
            
            if avg_response_time <= 100:
                print(f"✅ Available tasks endpoint performance: {avg_response_time:.1f}ms average (target: <100ms)")
                self.test_results.append({
                    "test": "Optimized Available Tasks Endpoint Performance",
                    "status": "PASSED",
                    "details": f"Average: {avg_response_time:.1f}ms, Target: <100ms"
                })
            else:
                print(f"❌ Available tasks endpoint performance: {avg_response_time:.1f}ms average (target: <100ms)")
                self.test_results.append({
                    "test": "Optimized Available Tasks Endpoint Performance",
                    "status": "FAILED",
                    "reason": f"Average response time {avg_response_time:.1f}ms exceeds 100ms target"
                })
        else:
            print("❌ Available tasks endpoint completely failed")
            self.test_results.append({
                "test": "Optimized Available Tasks Endpoint Performance",
                "status": "FAILED",
                "reason": "All requests failed"
            })
    
    async def test_response_structure_compatibility(self):
        """Test 3: Verify response structure matches frontend expectations"""
        print("\n🧪 Test 3: Response structure compatibility")
        
        try:
            # Test today endpoint response structure
            metrics = await self.measure_endpoint_performance("/today")
            
            if metrics["status_code"] == 200 and metrics["response_data"]:
                today_data = metrics["response_data"]
                
                # Check required fields for today endpoint
                required_today_fields = [
                    "prioritized_tasks", "total_tasks_today", "high_priority_count",
                    "overdue_count", "average_score", "user_level", "current_streak",
                    "total_points", "performance", "cache_timestamp"
                ]
                
                missing_fields = [field for field in required_today_fields if field not in today_data]
                
                if not missing_fields:
                    print("✅ Today endpoint response structure is complete")
                    
                    # Check if prioritized_tasks have scoring fields
                    if today_data["prioritized_tasks"]:
                        task = today_data["prioritized_tasks"][0]
                        scoring_fields = ["current_score", "area_importance", "project_importance"]
                        missing_scoring = [field for field in scoring_fields if field not in task]
                        
                        if not missing_scoring:
                            print("✅ Task scoring fields are present")
                            self.test_results.append({
                                "test": "Response Structure Compatibility",
                                "status": "PASSED",
                                "details": "All required fields present including scoring fields"
                            })
                        else:
                            print(f"⚠️ Missing task scoring fields: {missing_scoring}")
                            self.test_results.append({
                                "test": "Response Structure Compatibility",
                                "status": "PARTIAL",
                                "reason": f"Missing task scoring fields: {missing_scoring}"
                            })
                    else:
                        print("⚠️ No tasks returned to verify scoring fields")
                        self.test_results.append({
                            "test": "Response Structure Compatibility",
                            "status": "PARTIAL",
                            "reason": "No tasks returned to verify scoring fields"
                        })
                else:
                    print(f"❌ Missing required fields in today endpoint: {missing_fields}")
                    self.test_results.append({
                        "test": "Response Structure Compatibility",
                        "status": "FAILED",
                        "reason": f"Missing required fields: {missing_fields}"
                    })
            else:
                print(f"❌ Today endpoint failed: HTTP {metrics['status_code']}")
                self.test_results.append({
                    "test": "Response Structure Compatibility",
                    "status": "FAILED",
                    "reason": f"Today endpoint failed: HTTP {metrics['status_code']}"
                })
                
        except Exception as e:
            print(f"❌ Response structure test failed: {e}")
            self.test_results.append({
                "test": "Response Structure Compatibility",
                "status": "FAILED",
                "reason": str(e)
            })
    
    async def test_performance_monitoring_endpoint(self):
        """Test 4: Performance monitoring system verification"""
        print("\n🧪 Test 4: Performance monitoring system")
        
        try:
            metrics = await self.measure_endpoint_performance("/performance")
            
            if metrics["status_code"] == 200 and metrics["response_data"]:
                perf_data = metrics["response_data"]
                
                # Check required performance monitoring fields
                required_fields = [
                    "performance_summary", "n1_query_warnings", "status", 
                    "user_id", "timestamp"
                ]
                
                missing_fields = [field for field in required_fields if field not in perf_data]
                
                if not missing_fields:
                    print("✅ Performance monitoring endpoint structure is complete")
                    
                    # Check if system status indicates optimization
                    if perf_data["status"] == "optimized":
                        print("✅ System status shows 'optimized'")
                        
                        # Check N+1 query warnings
                        n1_warnings = perf_data["n1_query_warnings"]
                        if len(n1_warnings) == 0:
                            print("✅ No N+1 query warnings detected")
                            self.test_results.append({
                                "test": "Performance Monitoring System",
                                "status": "PASSED",
                                "details": "System optimized with no N+1 query warnings"
                            })
                        else:
                            print(f"⚠️ N+1 query warnings detected: {len(n1_warnings)}")
                            self.test_results.append({
                                "test": "Performance Monitoring System",
                                "status": "PARTIAL",
                                "reason": f"N+1 query warnings detected: {len(n1_warnings)}"
                            })
                    else:
                        print(f"⚠️ System status is '{perf_data['status']}' (expected 'optimized')")
                        self.test_results.append({
                            "test": "Performance Monitoring System",
                            "status": "PARTIAL",
                            "reason": f"System status is '{perf_data['status']}' instead of 'optimized'"
                        })
                else:
                    print(f"❌ Missing required fields in performance endpoint: {missing_fields}")
                    self.test_results.append({
                        "test": "Performance Monitoring System",
                        "status": "FAILED",
                        "reason": f"Missing required fields: {missing_fields}"
                    })
            else:
                print(f"❌ Performance monitoring endpoint failed: HTTP {metrics['status_code']}")
                self.test_results.append({
                    "test": "Performance Monitoring System",
                    "status": "FAILED",
                    "reason": f"Performance endpoint failed: HTTP {metrics['status_code']}"
                })
                
        except Exception as e:
            print(f"❌ Performance monitoring test failed: {e}")
            self.test_results.append({
                "test": "Performance Monitoring System",
                "status": "FAILED",
                "reason": str(e)
            })
    
    async def test_critical_endpoints_performance(self):
        """Test 5: Critical endpoints performance baseline"""
        print("\n🧪 Test 5: Critical endpoints performance baseline")
        
        critical_endpoints = [
            ("/dashboard", 1000),  # 1 second target
            ("/areas?include_projects=true&include_archived=false", 1000),
            ("/pillars?include_areas=false&include_archived=false", 1000),
            ("/projects?include_archived=false", 1000),
            ("/insights?date_range=all_time", 1000)
        ]
        
        all_passed = True
        endpoint_results = []
        
        for endpoint, target_ms in critical_endpoints:
            metrics = await self.measure_endpoint_performance(endpoint, target_ms=target_ms)
            
            if metrics["status_code"] == 200:
                if metrics["meets_target"]:
                    print(f"✅ {endpoint}: {metrics['response_time_ms']}ms (target: <{target_ms}ms)")
                    endpoint_results.append(f"{endpoint}: {metrics['response_time_ms']}ms")
                else:
                    print(f"❌ {endpoint}: {metrics['response_time_ms']}ms (target: <{target_ms}ms)")
                    all_passed = False
                    endpoint_results.append(f"{endpoint}: {metrics['response_time_ms']}ms (SLOW)")
            else:
                print(f"❌ {endpoint}: HTTP {metrics['status_code']}")
                all_passed = False
                endpoint_results.append(f"{endpoint}: HTTP {metrics['status_code']} (FAILED)")
        
        if all_passed:
            self.test_results.append({
                "test": "Critical Endpoints Performance",
                "status": "PASSED",
                "details": f"All endpoints meet performance targets: {', '.join(endpoint_results)}"
            })
        else:
            self.test_results.append({
                "test": "Critical Endpoints Performance",
                "status": "FAILED",
                "reason": f"Some endpoints failed performance targets: {', '.join(endpoint_results)}"
            })
    
    async def test_authentication_compatibility(self):
        """Test 6: Authentication works with optimized endpoints"""
        print("\n🧪 Test 6: Authentication compatibility")
        
        try:
            # Test /auth/me endpoint
            metrics = await self.measure_endpoint_performance("/auth/me")
            
            if metrics["status_code"] == 200 and metrics["response_data"]:
                user_data = metrics["response_data"]
                
                # Check if user data has required fields
                required_fields = ["id", "email", "username", "first_name", "last_name"]
                missing_fields = [field for field in required_fields if field not in user_data]
                
                if not missing_fields:
                    print("✅ Authentication endpoint working correctly")
                    
                    # Test that protected endpoints work with auth
                    protected_endpoints = ["/today", "/dashboard", "/areas"]
                    auth_working = True
                    
                    for endpoint in protected_endpoints:
                        test_metrics = await self.measure_endpoint_performance(endpoint)
                        if test_metrics["status_code"] not in [200, 404]:  # 404 is acceptable for some endpoints
                            auth_working = False
                            break
                    
                    if auth_working:
                        print("✅ Protected endpoints accessible with authentication")
                        self.test_results.append({
                            "test": "Authentication Compatibility",
                            "status": "PASSED",
                            "details": "Authentication working with all optimized endpoints"
                        })
                    else:
                        print("❌ Some protected endpoints not accessible")
                        self.test_results.append({
                            "test": "Authentication Compatibility",
                            "status": "FAILED",
                            "reason": "Protected endpoints not accessible with authentication"
                        })
                else:
                    print(f"❌ Missing user data fields: {missing_fields}")
                    self.test_results.append({
                        "test": "Authentication Compatibility",
                        "status": "FAILED",
                        "reason": f"Missing user data fields: {missing_fields}"
                    })
            else:
                print(f"❌ Authentication endpoint failed: HTTP {metrics['status_code']}")
                self.test_results.append({
                    "test": "Authentication Compatibility",
                    "status": "FAILED",
                    "reason": f"Authentication endpoint failed: HTTP {metrics['status_code']}"
                })
                
        except Exception as e:
            print(f"❌ Authentication compatibility test failed: {e}")
            self.test_results.append({
                "test": "Authentication Compatibility",
                "status": "FAILED",
                "reason": str(e)
            })
    
    async def test_error_handling_and_fallbacks(self):
        """Test 7: Error handling and fallback mechanisms"""
        print("\n🧪 Test 7: Error handling and fallback mechanisms")
        
        try:
            # Test invalid endpoints return proper errors
            invalid_endpoints = [
                "/invalid-endpoint",
                "/today/invalid-sub-endpoint",
                "/areas/invalid-area-id"
            ]
            
            error_handling_working = True
            
            for endpoint in invalid_endpoints:
                async with self.session.get(f"{API_BASE}{endpoint}", headers=self.get_auth_headers()) as response:
                    if response.status not in [400, 404, 422]:  # Expected error codes
                        error_handling_working = False
                        print(f"❌ {endpoint}: Expected error code, got {response.status}")
                    else:
                        print(f"✅ {endpoint}: Proper error handling ({response.status})")
            
            if error_handling_working:
                self.test_results.append({
                    "test": "Error Handling and Fallbacks",
                    "status": "PASSED",
                    "details": "All invalid endpoints return proper error codes"
                })
            else:
                self.test_results.append({
                    "test": "Error Handling and Fallbacks",
                    "status": "FAILED",
                    "reason": "Some endpoints don't return proper error codes"
                })
                
        except Exception as e:
            print(f"❌ Error handling test failed: {e}")
            self.test_results.append({
                "test": "Error Handling and Fallbacks",
                "status": "FAILED",
                "reason": str(e)
            })
    
    def print_performance_summary(self):
        """Print detailed performance summary"""
        print("\n" + "="*80)
        print("🚀 THE ARCHITECT'S PERFORMANCE VERIFICATION - DETAILED METRICS")
        print("="*80)
        
        if "today_endpoint" in self.performance_metrics:
            today_metrics = self.performance_metrics["today_endpoint"]
            print(f"📊 TODAY ENDPOINT PERFORMANCE:")
            print(f"   Average: {today_metrics['average_ms']}ms (Target: <{today_metrics['target_ms']}ms)")
            print(f"   Range: {today_metrics['min_ms']}ms - {today_metrics['max_ms']}ms")
            print(f"   Success Rate: {today_metrics['success_rate']}%")
            print(f"   Meets Target: {'✅ YES' if today_metrics['meets_target'] else '❌ NO'}")
        
        if "available_tasks_endpoint" in self.performance_metrics:
            tasks_metrics = self.performance_metrics["available_tasks_endpoint"]
            print(f"\n📊 AVAILABLE TASKS ENDPOINT PERFORMANCE:")
            print(f"   Average: {tasks_metrics['average_ms']}ms (Target: <{tasks_metrics['target_ms']}ms)")
            print(f"   Range: {tasks_metrics['min_ms']}ms - {tasks_metrics['max_ms']}ms")
            print(f"   Success Rate: {tasks_metrics['success_rate']}%")
            print(f"   Meets Target: {'✅ YES' if tasks_metrics['meets_target'] else '❌ NO'}")
        
        print("\n" + "="*80)
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🎯 THE ARCHITECT'S FINAL PERFORMANCE VERIFICATION - TEST SUMMARY")
        print("="*80)
        
        passed = len([t for t in self.test_results if t["status"] == "PASSED"])
        failed = len([t for t in self.test_results if t["status"] == "FAILED"])
        partial = len([t for t in self.test_results if t["status"] == "PARTIAL"])
        total = len(self.test_results)
        
        print(f"📊 OVERALL RESULTS: {passed}/{total} tests passed")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️ Partial: {partial}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status_icon = {"PASSED": "✅", "FAILED": "❌", "PARTIAL": "⚠️"}
            icon = status_icon.get(result["status"], "❓")
            print(f"{i:2d}. {icon} {result['test']}: {result['status']}")
            
            if "details" in result:
                print(f"    📝 {result['details']}")
            if "reason" in result:
                print(f"    💬 {result['reason']}")
        
        # Print performance summary
        self.print_performance_summary()
        
        print("\n" + "="*80)
        
        # Determine overall system status
        if success_rate >= 90:
            print("🎉 THE ARCHITECT'S PERFORMANCE OPTIMIZATION IS PRODUCTION-READY!")
            print("🚀 All performance targets achieved - API response times optimized!")
        elif success_rate >= 75:
            print("⚠️ THE ARCHITECT'S OPTIMIZATION IS MOSTLY FUNCTIONAL - MINOR ISSUES DETECTED")
            print("🔧 Some performance targets may need fine-tuning")
        else:
            print("❌ THE ARCHITECT'S OPTIMIZATION HAS SIGNIFICANT ISSUES - NEEDS ATTENTION")
            print("🚨 Performance targets not met - requires immediate investigation")
            
        print("="*80)
        
    async def run_all_tests(self):
        """Run all performance verification tests"""
        print("🚀 Starting The Architect's Final Performance Verification...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print("📋 Testing all 5 phases of the performance optimization solution")
        
        await self.setup_session()
        
        try:
            # Authentication
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed with tests")
                return
                
            print("✅ Authentication successful")
            
            # Run all performance tests
            await self.test_optimized_today_endpoint()
            await self.test_optimized_available_tasks_endpoint()
            await self.test_response_structure_compatibility()
            await self.test_performance_monitoring_endpoint()
            await self.test_critical_endpoints_performance()
            await self.test_authentication_compatibility()
            await self.test_error_handling_and_fallbacks()
            
        finally:
            await self.cleanup_session()
            
        # Print summary
        self.print_test_summary()

async def main():
    """Main test execution"""
    test_suite = ArchitectPerformanceTestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())