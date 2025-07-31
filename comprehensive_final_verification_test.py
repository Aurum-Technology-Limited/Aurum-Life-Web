#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, List

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://776a09a2-f446-49dd-9112-c1d61e461e4c.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class ComprehensiveFinalVerificationSuite:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "nav.test@aurumlife.com"
        self.test_user_password = "NavTest123!"
        self.test_results = []
        self.performance_results = []
        self.created_resources = []
        
    async def setup_session(self):
        """Initialize HTTP session"""
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        
    async def cleanup_session(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()
            
    async def authenticate(self):
        """Authenticate with test credentials"""
        try:
            print(f"🔐 Authenticating with {self.test_user_email}...")
            
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
            
            start_time = time.time()
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data["access_token"]
                    self.performance_results.append({
                        "endpoint": "/auth/login",
                        "response_time_ms": response_time,
                        "status": "SUCCESS"
                    })
                    print(f"✅ Authentication successful ({response_time:.1f}ms)")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Authentication failed: {response.status} - {error_text}")
                    self.test_results.append({
                        "test": "Authentication System",
                        "status": "FAILED",
                        "reason": f"Login failed: {response.status}"
                    })
                    return False
                    
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            self.test_results.append({
                "test": "Authentication System",
                "status": "FAILED",
                "reason": str(e)
            })
            return False
            
    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.auth_token}"}
        
    async def test_authentication_system(self):
        """Test 1: Authentication System Verification"""
        print("\n🧪 Test 1: Authentication System Verification")
        
        try:
            # Test /auth/me endpoint
            start_time = time.time()
            async with self.session.get(f"{API_BASE}/auth/me", headers=self.get_auth_headers()) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    user_data = await response.json()
                    self.performance_results.append({
                        "endpoint": "/auth/me",
                        "response_time_ms": response_time,
                        "status": "SUCCESS"
                    })
                    
                    # Verify user data structure
                    required_fields = ["id", "email", "username", "first_name", "is_active"]
                    missing_fields = [field for field in required_fields if field not in user_data]
                    
                    if not missing_fields:
                        print(f"✅ /auth/me endpoint working ({response_time:.1f}ms)")
                        print(f"   User: {user_data.get('first_name', 'Unknown')} ({user_data.get('email', 'No email')})")
                        
                        # Test token validation with protected endpoint
                        start_time = time.time()
                        async with self.session.get(f"{API_BASE}/dashboard", headers=self.get_auth_headers()) as dash_response:
                            dash_response_time = (time.time() - start_time) * 1000
                            
                            if dash_response.status == 200:
                                print(f"✅ Token-based authentication working for protected endpoints ({dash_response_time:.1f}ms)")
                                self.test_results.append({
                                    "test": "Authentication System",
                                    "status": "PASSED",
                                    "details": "Login, token validation, and protected endpoint access working"
                                })
                            else:
                                print(f"❌ Protected endpoint access failed: {dash_response.status}")
                                self.test_results.append({
                                    "test": "Authentication System",
                                    "status": "FAILED",
                                    "reason": f"Protected endpoint failed: {dash_response.status}"
                                })
                    else:
                        print(f"❌ User data missing fields: {missing_fields}")
                        self.test_results.append({
                            "test": "Authentication System",
                            "status": "FAILED",
                            "reason": f"Missing user fields: {missing_fields}"
                        })
                else:
                    print(f"❌ /auth/me endpoint failed: {response.status}")
                    self.test_results.append({
                        "test": "Authentication System",
                        "status": "FAILED",
                        "reason": f"/auth/me failed: {response.status}"
                    })
                    
        except Exception as e:
            print(f"❌ Authentication system test failed: {e}")
            self.test_results.append({
                "test": "Authentication System",
                "status": "FAILED",
                "reason": str(e)
            })
            
    async def test_dashboard_endpoints(self):
        """Test 2: Dashboard Endpoints (PRIMARY FOCUS)"""
        print("\n🧪 Test 2: Dashboard Endpoints (PRIMARY FOCUS)")
        
        try:
            # Test /api/dashboard endpoint
            print("   Testing /api/dashboard...")
            start_time = time.time()
            async with self.session.get(f"{API_BASE}/dashboard", headers=self.get_auth_headers()) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    dashboard_data = await response.json()
                    self.performance_results.append({
                        "endpoint": "/dashboard",
                        "response_time_ms": response_time,
                        "status": "SUCCESS"
                    })
                    
                    # Verify UserDashboard structure
                    required_fields = ["user", "stats", "recent_tasks", "areas"]
                    missing_fields = [field for field in required_fields if field not in dashboard_data]
                    
                    if not missing_fields:
                        print(f"✅ /api/dashboard endpoint working ({response_time:.1f}ms)")
                        print(f"   User: {dashboard_data['user'].get('first_name', 'Unknown')}")
                        print(f"   Stats: {dashboard_data['stats'].get('tasks_completed', 0)} completed / {dashboard_data['stats'].get('total_tasks', 0)} total tasks")
                        print(f"   Recent tasks: {len(dashboard_data.get('recent_tasks', []))}")
                        print(f"   Areas: {len(dashboard_data.get('areas', []))}")
                        
                        dashboard_success = True
                    else:
                        print(f"❌ Dashboard data missing fields: {missing_fields}")
                        dashboard_success = False
                else:
                    print(f"❌ /api/dashboard endpoint failed: {response.status}")
                    error_text = await response.text()
                    print(f"   Error: {error_text}")
                    dashboard_success = False
                    
            # Test /api/today endpoint
            print("   Testing /api/today...")
            start_time = time.time()
            async with self.session.get(f"{API_BASE}/today", headers=self.get_auth_headers()) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    today_data = await response.json()
                    self.performance_results.append({
                        "endpoint": "/today",
                        "response_time_ms": response_time,
                        "status": "SUCCESS"
                    })
                    
                    # Verify today view structure
                    required_fields = ["prioritized_tasks", "total_tasks_today", "user_level"]
                    missing_fields = [field for field in required_fields if field not in today_data]
                    
                    if not missing_fields:
                        print(f"✅ /api/today endpoint working ({response_time:.1f}ms)")
                        print(f"   Prioritized tasks: {len(today_data.get('prioritized_tasks', []))}")
                        print(f"   Total tasks today: {today_data.get('total_tasks_today', 0)}")
                        print(f"   High priority: {today_data.get('high_priority_count', 0)}")
                        
                        today_success = True
                    else:
                        print(f"❌ Today data missing fields: {missing_fields}")
                        today_success = False
                else:
                    print(f"❌ /api/today endpoint failed: {response.status}")
                    today_success = False
                    
            # Test /api/today/available-tasks endpoint
            print("   Testing /api/today/available-tasks...")
            start_time = time.time()
            async with self.session.get(f"{API_BASE}/today/available-tasks", headers=self.get_auth_headers()) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    available_tasks = await response.json()
                    self.performance_results.append({
                        "endpoint": "/today/available-tasks",
                        "response_time_ms": response_time,
                        "status": "SUCCESS"
                    })
                    
                    print(f"✅ /api/today/available-tasks endpoint working ({response_time:.1f}ms)")
                    print(f"   Available tasks: {len(available_tasks)}")
                    
                    available_tasks_success = True
                else:
                    print(f"❌ /api/today/available-tasks endpoint failed: {response.status}")
                    available_tasks_success = False
                    
            # Overall dashboard endpoints result
            if dashboard_success and today_success and available_tasks_success:
                self.test_results.append({
                    "test": "Dashboard Endpoints",
                    "status": "PASSED",
                    "details": "All dashboard endpoints working with proper data structure"
                })
            else:
                failed_endpoints = []
                if not dashboard_success:
                    failed_endpoints.append("/dashboard")
                if not today_success:
                    failed_endpoints.append("/today")
                if not available_tasks_success:
                    failed_endpoints.append("/today/available-tasks")
                    
                self.test_results.append({
                    "test": "Dashboard Endpoints",
                    "status": "FAILED",
                    "reason": f"Failed endpoints: {', '.join(failed_endpoints)}"
                })
                
        except Exception as e:
            print(f"❌ Dashboard endpoints test failed: {e}")
            self.test_results.append({
                "test": "Dashboard Endpoints",
                "status": "FAILED",
                "reason": str(e)
            })
            
    async def test_navigation_endpoints(self):
        """Test 3: Navigation Endpoints"""
        print("\n🧪 Test 3: Navigation Endpoints")
        
        navigation_results = {}
        
        try:
            # Test /api/areas endpoint
            print("   Testing /api/areas...")
            start_time = time.time()
            async with self.session.get(f"{API_BASE}/areas?include_projects=true&include_archived=false", headers=self.get_auth_headers()) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    areas_data = await response.json()
                    self.performance_results.append({
                        "endpoint": "/areas",
                        "response_time_ms": response_time,
                        "status": "SUCCESS"
                    })
                    print(f"✅ /api/areas endpoint working ({response_time:.1f}ms)")
                    print(f"   Areas found: {len(areas_data)}")
                    navigation_results["areas"] = True
                else:
                    print(f"❌ /api/areas endpoint failed: {response.status}")
                    navigation_results["areas"] = False
                    
            # Test /api/pillars endpoint
            print("   Testing /api/pillars...")
            start_time = time.time()
            async with self.session.get(f"{API_BASE}/pillars?include_areas=false&include_archived=false", headers=self.get_auth_headers()) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    pillars_data = await response.json()
                    self.performance_results.append({
                        "endpoint": "/pillars",
                        "response_time_ms": response_time,
                        "status": "SUCCESS"
                    })
                    print(f"✅ /api/pillars endpoint working ({response_time:.1f}ms)")
                    print(f"   Pillars found: {len(pillars_data)}")
                    navigation_results["pillars"] = True
                else:
                    print(f"❌ /api/pillars endpoint failed: {response.status}")
                    navigation_results["pillars"] = False
                    
            # Test /api/projects endpoint
            print("   Testing /api/projects...")
            start_time = time.time()
            async with self.session.get(f"{API_BASE}/projects?include_archived=false", headers=self.get_auth_headers()) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    projects_data = await response.json()
                    self.performance_results.append({
                        "endpoint": "/projects",
                        "response_time_ms": response_time,
                        "status": "SUCCESS"
                    })
                    print(f"✅ /api/projects endpoint working ({response_time:.1f}ms)")
                    print(f"   Projects found: {len(projects_data)}")
                    navigation_results["projects"] = True
                else:
                    print(f"❌ /api/projects endpoint failed: {response.status}")
                    navigation_results["projects"] = False
                    
            # Test /api/insights endpoint
            print("   Testing /api/insights...")
            start_time = time.time()
            async with self.session.get(f"{API_BASE}/insights?date_range=all_time", headers=self.get_auth_headers()) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    insights_data = await response.json()
                    self.performance_results.append({
                        "endpoint": "/insights",
                        "response_time_ms": response_time,
                        "status": "SUCCESS"
                    })
                    print(f"✅ /api/insights endpoint working ({response_time:.1f}ms)")
                    navigation_results["insights"] = True
                else:
                    print(f"❌ /api/insights endpoint failed: {response.status}")
                    navigation_results["insights"] = False
                    
            # Overall navigation result
            successful_endpoints = sum(navigation_results.values())
            total_endpoints = len(navigation_results)
            
            if successful_endpoints == total_endpoints:
                self.test_results.append({
                    "test": "Navigation Endpoints",
                    "status": "PASSED",
                    "details": f"All {total_endpoints} navigation endpoints working"
                })
            else:
                failed_endpoints = [endpoint for endpoint, success in navigation_results.items() if not success]
                self.test_results.append({
                    "test": "Navigation Endpoints",
                    "status": "FAILED",
                    "reason": f"Failed endpoints: {', '.join(failed_endpoints)} ({successful_endpoints}/{total_endpoints} working)"
                })
                
        except Exception as e:
            print(f"❌ Navigation endpoints test failed: {e}")
            self.test_results.append({
                "test": "Navigation Endpoints",
                "status": "FAILED",
                "reason": str(e)
            })
            
    async def test_performance_verification(self):
        """Test 4: Performance Verification"""
        print("\n🧪 Test 4: Performance Verification")
        
        try:
            # Analyze performance results
            if not self.performance_results:
                self.test_results.append({
                    "test": "Performance Verification",
                    "status": "FAILED",
                    "reason": "No performance data collected"
                })
                return
                
            # Check response times
            slow_endpoints = []
            timeout_endpoints = []
            
            for result in self.performance_results:
                endpoint = result["endpoint"]
                response_time = result["response_time_ms"]
                
                if response_time > 2000:  # >2 seconds
                    slow_endpoints.append(f"{endpoint} ({response_time:.1f}ms)")
                    
                if result["status"] != "SUCCESS":
                    timeout_endpoints.append(endpoint)
                    
            # Calculate average response time
            successful_results = [r for r in self.performance_results if r["status"] == "SUCCESS"]
            if successful_results:
                avg_response_time = sum(r["response_time_ms"] for r in successful_results) / len(successful_results)
                print(f"📊 Average response time: {avg_response_time:.1f}ms")
                
                # Print individual endpoint performance
                print("📈 Endpoint Performance:")
                for result in successful_results:
                    print(f"   {result['endpoint']}: {result['response_time_ms']:.1f}ms")
                    
            # Performance assessment
            if not slow_endpoints and not timeout_endpoints:
                self.test_results.append({
                    "test": "Performance Verification",
                    "status": "PASSED",
                    "details": f"All endpoints <2s (avg: {avg_response_time:.1f}ms)"
                })
            else:
                issues = []
                if slow_endpoints:
                    issues.append(f"Slow endpoints: {', '.join(slow_endpoints)}")
                if timeout_endpoints:
                    issues.append(f"Timeout endpoints: {', '.join(timeout_endpoints)}")
                    
                self.test_results.append({
                    "test": "Performance Verification",
                    "status": "FAILED",
                    "reason": "; ".join(issues)
                })
                
        except Exception as e:
            print(f"❌ Performance verification test failed: {e}")
            self.test_results.append({
                "test": "Performance Verification",
                "status": "FAILED",
                "reason": str(e)
            })
            
    async def test_data_structure_integrity(self):
        """Test 5: Data Structure Integrity"""
        print("\n🧪 Test 5: Data Structure Integrity")
        
        try:
            # Test dashboard data structure in detail
            async with self.session.get(f"{API_BASE}/dashboard", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    dashboard_data = await response.json()
                    
                    # Verify user structure
                    user = dashboard_data.get("user", {})
                    user_required = ["id", "username", "email", "first_name", "is_active"]
                    user_missing = [field for field in user_required if field not in user]
                    
                    # Verify stats structure
                    stats = dashboard_data.get("stats", {})
                    stats_required = ["user_id", "tasks_completed", "total_tasks", "total_areas", "total_projects"]
                    stats_missing = [field for field in stats_required if field not in stats]
                    
                    # Verify tasks structure
                    recent_tasks = dashboard_data.get("recent_tasks", [])
                    task_structure_valid = True
                    if recent_tasks:
                        task = recent_tasks[0]
                        task_required = ["id", "name", "completed", "priority"]
                        task_missing = [field for field in task_required if field not in task]
                        if task_missing:
                            task_structure_valid = False
                            
                    # Overall structure assessment
                    structure_issues = []
                    if user_missing:
                        structure_issues.append(f"User missing: {user_missing}")
                    if stats_missing:
                        structure_issues.append(f"Stats missing: {stats_missing}")
                    if not task_structure_valid:
                        structure_issues.append("Task structure invalid")
                        
                    if not structure_issues:
                        print("✅ Dashboard data structure integrity verified")
                        
                        # Test JSON serialization
                        try:
                            json.dumps(dashboard_data)
                            print("✅ JSON serialization working")
                            
                            self.test_results.append({
                                "test": "Data Structure Integrity",
                                "status": "PASSED",
                                "details": "All data structures valid and JSON serializable"
                            })
                        except Exception as json_error:
                            print(f"❌ JSON serialization failed: {json_error}")
                            self.test_results.append({
                                "test": "Data Structure Integrity",
                                "status": "FAILED",
                                "reason": f"JSON serialization error: {json_error}"
                            })
                    else:
                        print(f"❌ Data structure issues: {'; '.join(structure_issues)}")
                        self.test_results.append({
                            "test": "Data Structure Integrity",
                            "status": "FAILED",
                            "reason": "; ".join(structure_issues)
                        })
                else:
                    print(f"❌ Could not retrieve dashboard data for structure test: {response.status}")
                    self.test_results.append({
                        "test": "Data Structure Integrity",
                        "status": "FAILED",
                        "reason": f"Dashboard endpoint failed: {response.status}"
                    })
                    
        except Exception as e:
            print(f"❌ Data structure integrity test failed: {e}")
            self.test_results.append({
                "test": "Data Structure Integrity",
                "status": "FAILED",
                "reason": str(e)
            })
            
    async def test_error_scenarios(self):
        """Test 6: Error Handling and Edge Cases"""
        print("\n🧪 Test 6: Error Handling and Edge Cases")
        
        try:
            error_tests_passed = 0
            total_error_tests = 0
            
            # Test 1: Invalid authentication
            total_error_tests += 1
            async with self.session.get(f"{API_BASE}/dashboard", headers={"Authorization": "Bearer invalid-token"}) as response:
                if response.status == 401:
                    print("✅ Invalid token correctly rejected (401)")
                    error_tests_passed += 1
                else:
                    print(f"❌ Invalid token should return 401, got {response.status}")
                    
            # Test 2: Missing authentication
            total_error_tests += 1
            async with self.session.get(f"{API_BASE}/dashboard") as response:
                if response.status in [401, 403]:
                    print("✅ Missing authentication correctly rejected")
                    error_tests_passed += 1
                else:
                    print(f"❌ Missing auth should return 401/403, got {response.status}")
                    
            # Test 3: Non-existent endpoint
            total_error_tests += 1
            async with self.session.get(f"{API_BASE}/nonexistent-endpoint", headers=self.get_auth_headers()) as response:
                if response.status == 404:
                    print("✅ Non-existent endpoint correctly returns 404")
                    error_tests_passed += 1
                else:
                    print(f"❌ Non-existent endpoint should return 404, got {response.status}")
                    
            # Overall error handling assessment
            if error_tests_passed == total_error_tests:
                self.test_results.append({
                    "test": "Error Handling",
                    "status": "PASSED",
                    "details": f"All {total_error_tests} error scenarios handled correctly"
                })
            else:
                self.test_results.append({
                    "test": "Error Handling",
                    "status": "FAILED",
                    "reason": f"Only {error_tests_passed}/{total_error_tests} error scenarios handled correctly"
                })
                
        except Exception as e:
            print(f"❌ Error scenarios test failed: {e}")
            self.test_results.append({
                "test": "Error Handling",
                "status": "FAILED",
                "reason": str(e)
            })
            
    def print_comprehensive_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*100)
        print("🎯 COMPREHENSIVE FINAL VERIFICATION - ALL SYSTEMS MUST WORK PERFECTLY")
        print("="*100)
        
        passed = len([t for t in self.test_results if t["status"] == "PASSED"])
        failed = len([t for t in self.test_results if t["status"] == "FAILED"])
        total = len(self.test_results)
        
        print(f"📊 OVERALL RESULTS: {passed}/{total} critical systems verified")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        # Performance summary
        if self.performance_results:
            successful_perf = [r for r in self.performance_results if r["status"] == "SUCCESS"]
            if successful_perf:
                avg_response_time = sum(r["response_time_ms"] for r in successful_perf) / len(successful_perf)
                print(f"⚡ Average Response Time: {avg_response_time:.1f}ms")
                
                fastest = min(successful_perf, key=lambda x: x["response_time_ms"])
                slowest = max(successful_perf, key=lambda x: x["response_time_ms"])
                print(f"🚀 Fastest: {fastest['endpoint']} ({fastest['response_time_ms']:.1f}ms)")
                print(f"🐌 Slowest: {slowest['endpoint']} ({slowest['response_time_ms']:.1f}ms)")
        
        print("\n📋 DETAILED VERIFICATION RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status_icon = "✅" if result["status"] == "PASSED" else "❌"
            print(f"{i:2d}. {status_icon} {result['test']}: {result['status']}")
            
            if "details" in result:
                print(f"    📝 {result['details']}")
            if "reason" in result:
                print(f"    💬 {result['reason']}")
                
        print("\n📈 PERFORMANCE BREAKDOWN:")
        if self.performance_results:
            for result in self.performance_results:
                status_icon = "✅" if result["status"] == "SUCCESS" else "❌"
                print(f"   {status_icon} {result['endpoint']}: {result['response_time_ms']:.1f}ms")
        
        print("\n" + "="*100)
        
        # Final system status
        if success_rate == 100:
            print("🎉 ALL SYSTEMS VERIFIED - PRODUCTION READY!")
            print("✅ Authentication System: WORKING")
            print("✅ Dashboard Endpoints: WORKING") 
            print("✅ Navigation Endpoints: WORKING")
            print("✅ Performance: OPTIMAL")
            print("✅ Data Integrity: VERIFIED")
            print("✅ Error Handling: ROBUST")
        elif success_rate >= 90:
            print("⚠️ MOSTLY OPERATIONAL - MINOR ISSUES DETECTED")
            failed_systems = [t["test"] for t in self.test_results if t["status"] == "FAILED"]
            print(f"❌ Issues in: {', '.join(failed_systems)}")
        else:
            print("❌ CRITICAL ISSUES DETECTED - SYSTEM NOT READY")
            failed_systems = [t["test"] for t in self.test_results if t["status"] == "FAILED"]
            print(f"❌ Failed systems: {', '.join(failed_systems)}")
            
        print("="*100)
        
        return success_rate
        
    async def run_comprehensive_verification(self):
        """Run all comprehensive verification tests"""
        print("🚀 Starting COMPREHENSIVE FINAL VERIFICATION...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print(f"👤 Test User: {self.test_user_email}")
        
        await self.setup_session()
        
        try:
            # Authentication (prerequisite for all other tests)
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed with verification")
                return 0
                
            # Run all verification tests
            await self.test_authentication_system()
            await self.test_dashboard_endpoints()
            await self.test_navigation_endpoints()
            await self.test_performance_verification()
            await self.test_data_structure_integrity()
            await self.test_error_scenarios()
            
        finally:
            await self.cleanup_session()
            
        # Print comprehensive summary and return success rate
        return self.print_comprehensive_summary()

async def main():
    """Main test execution"""
    test_suite = ComprehensiveFinalVerificationSuite()
    success_rate = await test_suite.run_comprehensive_verification()
    
    # Exit with appropriate code
    if success_rate == 100:
        exit(0)  # Perfect success
    elif success_rate >= 90:
        exit(1)  # Minor issues
    else:
        exit(2)  # Critical issues

if __name__ == "__main__":
    asyncio.run(main())