#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, List

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://7767cc54-7d42-422d-ae92-93a862d5b150.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class TanStackQueryBackendTestSuite:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "tanstack.test@aurumlife.com"
        self.test_user_password = "TanStackTest123!"
        self.test_results = []
        self.performance_metrics = {}
        
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
                "username": "tanstacktest",
                "email": self.test_user_email,
                "first_name": "TanStack",
                "last_name": "Test",
                "password": self.test_user_password
            }
            
            print(f"🔄 Attempting to register test user: {self.test_user_email}")
            async with self.session.post(f"{API_BASE}/auth/register", json=register_data) as response:
                if response.status == 200:
                    print("✅ Test user registered successfully")
                elif response.status == 400:
                    print("ℹ️ Test user already exists")
                else:
                    print(f"⚠️ User registration returned: {response.status}")
                    error_text = await response.text()
                    print(f"Registration error: {error_text}")
                    
            # Login to get token
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            start_time = time.time()
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data["access_token"]
                    self.performance_metrics["auth_login"] = response_time
                    print(f"✅ Authentication successful ({response_time:.2f}ms)")
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
        
    async def test_dashboard_api_endpoint(self):
        """Test 1: Dashboard API Endpoint Testing"""
        print("\n🧪 Test 1: Dashboard API Endpoint Testing")
        
        try:
            start_time = time.time()
            async with self.session.get(f"{API_BASE}/dashboard", headers=self.get_auth_headers()) as response:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                self.performance_metrics["dashboard"] = response_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Verify response structure includes required fields
                    required_fields = ["user", "stats", "recent_tasks"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        print(f"✅ Dashboard API successful ({response_time:.2f}ms)")
                        print(f"   📊 Response includes: user, stats, recent_tasks")
                        
                        # Check performance target (<1s for caching effectiveness)
                        if response_time < 1000:
                            print(f"   🚀 Performance excellent: {response_time:.2f}ms < 1000ms target")
                            performance_status = "EXCELLENT"
                        elif response_time < 2000:
                            print(f"   ⚡ Performance good: {response_time:.2f}ms < 2000ms")
                            performance_status = "GOOD"
                        else:
                            print(f"   ⚠️ Performance slow: {response_time:.2f}ms > 2000ms")
                            performance_status = "SLOW"
                            
                        self.test_results.append({
                            "test": "Dashboard API Endpoint",
                            "status": "PASSED",
                            "response_time": f"{response_time:.2f}ms",
                            "performance": performance_status,
                            "details": f"All required fields present, {len(data.get('recent_tasks', []))} recent tasks"
                        })
                    else:
                        print(f"❌ Dashboard API missing fields: {missing_fields}")
                        self.test_results.append({
                            "test": "Dashboard API Endpoint",
                            "status": "FAILED",
                            "reason": f"Missing required fields: {missing_fields}"
                        })
                else:
                    print(f"❌ Dashboard API failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    self.test_results.append({
                        "test": "Dashboard API Endpoint",
                        "status": "FAILED",
                        "reason": f"HTTP {response.status}: {error_text}"
                    })
                    
        except Exception as e:
            print(f"❌ Dashboard API test failed: {e}")
            self.test_results.append({
                "test": "Dashboard API Endpoint",
                "status": "FAILED",
                "reason": str(e)
            })
            
    async def test_areas_api_endpoint(self):
        """Test 2: Areas API Endpoint Testing"""
        print("\n🧪 Test 2: Areas API Endpoint Testing")
        
        try:
            # Test with TanStack Query parameters
            params = "include_projects=true&include_archived=false"
            
            start_time = time.time()
            async with self.session.get(f"{API_BASE}/areas?{params}", headers=self.get_auth_headers()) as response:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                self.performance_metrics["areas"] = response_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    print(f"✅ Areas API successful ({response_time:.2f}ms)")
                    print(f"   📊 Retrieved {len(data)} areas")
                    
                    # Verify response includes area data with project relationships
                    if isinstance(data, list) and len(data) > 0:
                        sample_area = data[0]
                        has_projects = "projects" in sample_area or "project_count" in sample_area
                        has_pillar_info = "pillar_name" in sample_area or "pillar_id" in sample_area
                        
                        if has_projects:
                            print(f"   🔗 Areas include project relationship data")
                        if has_pillar_info:
                            print(f"   🏛️ Areas include pillar information")
                            
                    # Check performance for batch data loading
                    if response_time < 500:
                        print(f"   🚀 Performance excellent: {response_time:.2f}ms < 500ms")
                        performance_status = "EXCELLENT"
                    elif response_time < 1000:
                        print(f"   ⚡ Performance good: {response_time:.2f}ms < 1000ms")
                        performance_status = "GOOD"
                    else:
                        print(f"   ⚠️ Performance slow: {response_time:.2f}ms > 1000ms")
                        performance_status = "SLOW"
                        
                    self.test_results.append({
                        "test": "Areas API Endpoint",
                        "status": "PASSED",
                        "response_time": f"{response_time:.2f}ms",
                        "performance": performance_status,
                        "details": f"{len(data)} areas retrieved with project relationships"
                    })
                else:
                    print(f"❌ Areas API failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    self.test_results.append({
                        "test": "Areas API Endpoint",
                        "status": "FAILED",
                        "reason": f"HTTP {response.status}: {error_text}"
                    })
                    
            # Test with different query parameters (include_archived=true)
            params_archived = "include_projects=true&include_archived=true"
            
            start_time = time.time()
            async with self.session.get(f"{API_BASE}/areas?{params_archived}", headers=self.get_auth_headers()) as response:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                if response.status == 200:
                    data_with_archived = await response.json()
                    print(f"✅ Areas API with archived successful ({response_time:.2f}ms)")
                    print(f"   📊 Retrieved {len(data_with_archived)} areas (including archived)")
                else:
                    print(f"⚠️ Areas API with archived failed: {response.status}")
                    
        except Exception as e:
            print(f"❌ Areas API test failed: {e}")
            self.test_results.append({
                "test": "Areas API Endpoint",
                "status": "FAILED",
                "reason": str(e)
            })
            
    async def test_pillars_api_endpoint(self):
        """Test 3: Pillars API Endpoint Testing"""
        print("\n🧪 Test 3: Pillars API Endpoint Testing")
        
        try:
            # Test basic pillars endpoint
            start_time = time.time()
            async with self.session.get(f"{API_BASE}/pillars", headers=self.get_auth_headers()) as response:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                self.performance_metrics["pillars"] = response_time
                
                if response.status == 200:
                    data = await response.json()
                    
                    print(f"✅ Pillars API successful ({response_time:.2f}ms)")
                    print(f"   📊 Retrieved {len(data)} pillars")
                    
                    # Verify proper response structure for dropdown/selection components
                    if isinstance(data, list) and len(data) > 0:
                        sample_pillar = data[0]
                        required_fields = ["id", "name"]
                        has_required = all(field in sample_pillar for field in required_fields)
                        
                        if has_required:
                            print(f"   ✅ Pillars have required fields for dropdown components")
                        else:
                            print(f"   ⚠️ Pillars missing some required fields")
                            
                    # Check performance
                    if response_time < 500:
                        performance_status = "EXCELLENT"
                    elif response_time < 1000:
                        performance_status = "GOOD"
                    else:
                        performance_status = "SLOW"
                        
                    self.test_results.append({
                        "test": "Pillars API Endpoint",
                        "status": "PASSED",
                        "response_time": f"{response_time:.2f}ms",
                        "performance": performance_status,
                        "details": f"{len(data)} pillars retrieved"
                    })
                else:
                    print(f"❌ Pillars API failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    self.test_results.append({
                        "test": "Pillars API Endpoint",
                        "status": "FAILED",
                        "reason": f"HTTP {response.status}: {error_text}"
                    })
                    
            # Test with query parameters
            test_params = [
                "include_areas=true",
                "include_archived=true",
                "include_areas=true&include_archived=true"
            ]
            
            for params in test_params:
                start_time = time.time()
                async with self.session.get(f"{API_BASE}/pillars?{params}", headers=self.get_auth_headers()) as response:
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Pillars API with params '{params}' successful ({response_time:.2f}ms)")
                    else:
                        print(f"⚠️ Pillars API with params '{params}' failed: {response.status}")
                        
        except Exception as e:
            print(f"❌ Pillars API test failed: {e}")
            self.test_results.append({
                "test": "Pillars API Endpoint",
                "status": "FAILED",
                "reason": str(e)
            })
            
    async def test_authentication_integration(self):
        """Test 4: Authentication Integration"""
        print("\n🧪 Test 4: Authentication Integration")
        
        try:
            # Test /auth/me endpoint
            start_time = time.time()
            async with self.session.get(f"{API_BASE}/auth/me", headers=self.get_auth_headers()) as response:
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                if response.status == 200:
                    user_data = await response.json()
                    print(f"✅ Auth/me endpoint successful ({response_time:.2f}ms)")
                    print(f"   👤 User: {user_data.get('email', 'N/A')}")
                    
                    auth_me_success = True
                else:
                    print(f"❌ Auth/me endpoint failed: {response.status}")
                    auth_me_success = False
                    
            # Test protected endpoint without token (should return 401)
            async with self.session.get(f"{API_BASE}/dashboard") as response:
                if response.status == 401:
                    print(f"✅ Protected endpoint correctly returns 401 without token")
                    auth_protection_success = True
                else:
                    print(f"⚠️ Protected endpoint should return 401 without token, got: {response.status}")
                    auth_protection_success = False
                    
            # Test with invalid token (should return 401)
            invalid_headers = {"Authorization": "Bearer invalid-token-12345"}
            async with self.session.get(f"{API_BASE}/dashboard", headers=invalid_headers) as response:
                if response.status == 401:
                    print(f"✅ Protected endpoint correctly rejects invalid token")
                    invalid_token_success = True
                else:
                    print(f"⚠️ Protected endpoint should reject invalid token, got: {response.status}")
                    invalid_token_success = False
                    
            # Overall authentication test result
            if auth_me_success and auth_protection_success and invalid_token_success:
                self.test_results.append({
                    "test": "Authentication Integration",
                    "status": "PASSED",
                    "details": "JWT authentication working correctly for all scenarios"
                })
            else:
                failed_tests = []
                if not auth_me_success:
                    failed_tests.append("auth/me endpoint")
                if not auth_protection_success:
                    failed_tests.append("401 without token")
                if not invalid_token_success:
                    failed_tests.append("invalid token rejection")
                    
                self.test_results.append({
                    "test": "Authentication Integration",
                    "status": "FAILED",
                    "reason": f"Failed: {', '.join(failed_tests)}"
                })
                
        except Exception as e:
            print(f"❌ Authentication integration test failed: {e}")
            self.test_results.append({
                "test": "Authentication Integration",
                "status": "FAILED",
                "reason": str(e)
            })
            
    async def test_performance_validation(self):
        """Test 5: Performance Validation"""
        print("\n🧪 Test 5: Performance Validation")
        
        try:
            # Test multiple endpoints for performance consistency
            endpoints_to_test = [
                ("dashboard", f"{API_BASE}/dashboard"),
                ("areas", f"{API_BASE}/areas?include_projects=true"),
                ("pillars", f"{API_BASE}/pillars"),
                ("insights", f"{API_BASE}/insights"),
                ("today", f"{API_BASE}/today")
            ]
            
            performance_results = {}
            
            for endpoint_name, endpoint_url in endpoints_to_test:
                response_times = []
                
                # Test each endpoint 3 times for consistency
                for i in range(3):
                    try:
                        start_time = time.time()
                        async with self.session.get(endpoint_url, headers=self.get_auth_headers()) as response:
                            end_time = time.time()
                            response_time = (end_time - start_time) * 1000
                            
                            if response.status == 200:
                                response_times.append(response_time)
                            else:
                                print(f"   ⚠️ {endpoint_name} returned {response.status} on attempt {i+1}")
                                
                    except Exception as e:
                        print(f"   ❌ {endpoint_name} failed on attempt {i+1}: {e}")
                        
                if response_times:
                    avg_time = sum(response_times) / len(response_times)
                    min_time = min(response_times)
                    max_time = max(response_times)
                    
                    performance_results[endpoint_name] = {
                        "avg": avg_time,
                        "min": min_time,
                        "max": max_time,
                        "consistency": max_time - min_time
                    }
                    
                    print(f"   📊 {endpoint_name}: avg={avg_time:.2f}ms, min={min_time:.2f}ms, max={max_time:.2f}ms")
                    
            # Analyze overall performance
            if performance_results:
                avg_response_time = sum(result["avg"] for result in performance_results.values()) / len(performance_results)
                fast_endpoints = sum(1 for result in performance_results.values() if result["avg"] < 1000)
                total_endpoints = len(performance_results)
                
                print(f"\n   📈 Performance Summary:")
                print(f"   Average response time: {avg_response_time:.2f}ms")
                print(f"   Fast endpoints (<1s): {fast_endpoints}/{total_endpoints}")
                
                if avg_response_time < 1000 and fast_endpoints >= total_endpoints * 0.8:
                    performance_status = "EXCELLENT"
                    print(f"   🚀 Performance is excellent for caching optimization")
                elif avg_response_time < 2000:
                    performance_status = "GOOD"
                    print(f"   ⚡ Performance is good for caching")
                else:
                    performance_status = "NEEDS_IMPROVEMENT"
                    print(f"   ⚠️ Performance needs improvement for effective caching")
                    
                self.test_results.append({
                    "test": "Performance Validation",
                    "status": "PASSED",
                    "performance": performance_status,
                    "details": f"Avg: {avg_response_time:.2f}ms, {fast_endpoints}/{total_endpoints} endpoints <1s"
                })
            else:
                self.test_results.append({
                    "test": "Performance Validation",
                    "status": "FAILED",
                    "reason": "No successful performance measurements"
                })
                
        except Exception as e:
            print(f"❌ Performance validation test failed: {e}")
            self.test_results.append({
                "test": "Performance Validation",
                "status": "FAILED",
                "reason": str(e)
            })
            
    async def test_error_scenarios(self):
        """Test 6: Error Scenarios and Proper Error Responses"""
        print("\n🧪 Test 6: Error Scenarios and Proper Error Responses")
        
        try:
            error_tests = []
            
            # Test 404 for non-existent resources
            async with self.session.get(f"{API_BASE}/areas/non-existent-id", headers=self.get_auth_headers()) as response:
                if response.status == 404:
                    error_tests.append(("404 for non-existent area", True))
                    print(f"   ✅ 404 correctly returned for non-existent area")
                else:
                    error_tests.append(("404 for non-existent area", False))
                    print(f"   ❌ Expected 404 for non-existent area, got {response.status}")
                    
            # Test malformed requests
            async with self.session.get(f"{API_BASE}/areas?include_projects=invalid", headers=self.get_auth_headers()) as response:
                if response.status in [200, 400]:  # Either handles gracefully or rejects
                    error_tests.append(("Malformed query parameter handling", True))
                    print(f"   ✅ Malformed query parameter handled gracefully ({response.status})")
                else:
                    error_tests.append(("Malformed query parameter handling", False))
                    print(f"   ❌ Unexpected response to malformed query: {response.status}")
                    
            # Test rate limiting or server errors
            async with self.session.get(f"{API_BASE}/nonexistent-endpoint", headers=self.get_auth_headers()) as response:
                if response.status == 404:
                    error_tests.append(("Non-existent endpoint handling", True))
                    print(f"   ✅ Non-existent endpoint correctly returns 404")
                else:
                    error_tests.append(("Non-existent endpoint handling", False))
                    print(f"   ❌ Expected 404 for non-existent endpoint, got {response.status}")
                    
            # Overall error handling assessment
            successful_error_tests = sum(1 for _, success in error_tests if success)
            total_error_tests = len(error_tests)
            
            if successful_error_tests == total_error_tests:
                self.test_results.append({
                    "test": "Error Scenarios",
                    "status": "PASSED",
                    "details": f"All {total_error_tests} error scenarios handled correctly"
                })
            else:
                self.test_results.append({
                    "test": "Error Scenarios",
                    "status": "PARTIAL",
                    "details": f"{successful_error_tests}/{total_error_tests} error scenarios handled correctly"
                })
                
        except Exception as e:
            print(f"❌ Error scenarios test failed: {e}")
            self.test_results.append({
                "test": "Error Scenarios",
                "status": "FAILED",
                "reason": str(e)
            })
            
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🎯 TANSTACK QUERY BACKEND INTEGRATION - TEST SUMMARY")
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
        
        # Performance summary
        if self.performance_metrics:
            print(f"\n⚡ PERFORMANCE METRICS:")
            for endpoint, time_ms in self.performance_metrics.items():
                status = "🚀" if time_ms < 500 else "⚡" if time_ms < 1000 else "⚠️"
                print(f"   {status} {endpoint}: {time_ms:.2f}ms")
                
            avg_performance = sum(self.performance_metrics.values()) / len(self.performance_metrics)
            print(f"   📈 Average Response Time: {avg_performance:.2f}ms")
            
        print("\n📋 DETAILED RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status_icon = {"PASSED": "✅", "FAILED": "❌", "PARTIAL": "⚠️"}
            icon = status_icon.get(result["status"], "❓")
            print(f"{i:2d}. {icon} {result['test']}: {result['status']}")
            
            if "response_time" in result:
                print(f"    ⏱️ Response Time: {result['response_time']}")
            if "performance" in result:
                perf_icon = {"EXCELLENT": "🚀", "GOOD": "⚡", "SLOW": "⚠️", "NEEDS_IMPROVEMENT": "⚠️"}
                print(f"    {perf_icon.get(result['performance'], '📊')} Performance: {result['performance']}")
            if "details" in result:
                print(f"    📝 {result['details']}")
            if "reason" in result:
                print(f"    💬 {result['reason']}")
                
        print("\n" + "="*80)
        
        # Determine overall system status
        if success_rate >= 90:
            print("🎉 TANSTACK QUERY BACKEND INTEGRATION IS PRODUCTION-READY!")
            print("   All API endpoints are working correctly for TanStack Query caching")
        elif success_rate >= 75:
            print("⚠️ TANSTACK QUERY BACKEND INTEGRATION IS MOSTLY FUNCTIONAL")
            print("   Minor issues detected but core functionality working")
        else:
            print("❌ TANSTACK QUERY BACKEND INTEGRATION HAS SIGNIFICANT ISSUES")
            print("   Major problems detected that need immediate attention")
            
        # Performance assessment for caching
        if self.performance_metrics:
            avg_perf = sum(self.performance_metrics.values()) / len(self.performance_metrics)
            if avg_perf < 500:
                print("🚀 PERFORMANCE: Excellent for TanStack Query caching optimization")
            elif avg_perf < 1000:
                print("⚡ PERFORMANCE: Good for TanStack Query caching")
            else:
                print("⚠️ PERFORMANCE: May need optimization for effective caching")
                
        print("="*80)
        
    async def run_all_tests(self):
        """Run all TanStack Query backend integration tests"""
        print("🚀 Starting TanStack Query Backend Integration Testing...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print(f"👤 Test User: {self.test_user_email}")
        
        await self.setup_session()
        
        try:
            # Authentication
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed with tests")
                return
                
            # Run all tests
            await self.test_dashboard_api_endpoint()
            await self.test_areas_api_endpoint()
            await self.test_pillars_api_endpoint()
            await self.test_authentication_integration()
            await self.test_performance_validation()
            await self.test_error_scenarios()
            
        finally:
            await self.cleanup_session()
            
        # Print summary
        self.print_test_summary()

async def main():
    """Main test execution"""
    test_suite = TanStackQueryBackendTestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())