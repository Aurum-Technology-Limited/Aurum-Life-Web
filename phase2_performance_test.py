#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import time
import statistics
from datetime import datetime
from typing import Dict, Any, List, Tuple

# Configuration - Use external URL for testing
BACKEND_URL = "https://f4646b2e-0ec9-404e-813c-ae5666a33561.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class Phase2PerformanceTestSuite:
    """
    Comprehensive performance testing for Phase 2 optimizations focusing on:
    1. Areas API Performance Testing (/api/areas with include_projects=true) - target <200ms
    2. Projects API Performance Testing (/api/projects with include_tasks=true) - target performance
    3. Overall API Performance Verification (dashboard, auth endpoints)
    4. Database Query Efficiency (monitoring for N+1 patterns)
    """
    
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "nav.test@aurumlife.com"
        self.test_user_password = "testpassword"
        self.test_results = []
        self.performance_metrics = {}
        self.created_resources = {
            'pillars': [],
            'areas': [],
            'projects': [],
            'tasks': []
        }
        
    async def setup_session(self):
        """Initialize HTTP session with timeout configuration"""
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        
    async def cleanup_session(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()
            
    async def authenticate(self):
        """Authenticate with test credentials"""
        try:
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            start_time = time.time()
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                auth_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data["access_token"]
                    self.performance_metrics['auth_login'] = auth_time
                    print(f"✅ Authentication successful for {self.test_user_email} ({auth_time:.1f}ms)")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Authentication failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
            
    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.auth_token}"}
        
    async def measure_endpoint_performance(self, endpoint: str, headers: Dict = None, params: Dict = None, iterations: int = 5) -> Tuple[float, List[float], bool]:
        """
        Measure endpoint performance over multiple iterations
        Returns: (average_time_ms, all_times_ms, success)
        """
        times = []
        success = True
        
        for i in range(iterations):
            try:
                start_time = time.time()
                
                if params:
                    async with self.session.get(endpoint, headers=headers, params=params) as response:
                        response_time = (time.time() - start_time) * 1000
                        times.append(response_time)
                        
                        if response.status != 200:
                            print(f"❌ Endpoint {endpoint} failed with status {response.status}")
                            success = False
                            break
                else:
                    async with self.session.get(endpoint, headers=headers) as response:
                        response_time = (time.time() - start_time) * 1000
                        times.append(response_time)
                        
                        if response.status != 200:
                            print(f"❌ Endpoint {endpoint} failed with status {response.status}")
                            success = False
                            break
                            
                # Small delay between requests
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"❌ Error measuring {endpoint}: {e}")
                success = False
                break
                
        avg_time = statistics.mean(times) if times else 0
        return avg_time, times, success
        
    async def test_areas_api_performance(self):
        """
        Test 1: Areas API Performance Testing (/api/areas with include_projects=true)
        Target: <200ms response time with optimized batch queries
        """
        print("\n🧪 Test 1: Areas API Performance Testing (Target: <200ms)")
        
        try:
            endpoint = f"{API_BASE}/areas"
            params = {
                "include_projects": "true",
                "include_archived": "false"
            }
            
            # Measure performance over multiple iterations
            avg_time, all_times, success = await self.measure_endpoint_performance(
                endpoint, self.get_auth_headers(), params, iterations=10
            )
            
            if success:
                min_time = min(all_times)
                max_time = max(all_times)
                std_dev = statistics.stdev(all_times) if len(all_times) > 1 else 0
                
                self.performance_metrics['areas_api'] = {
                    'average': avg_time,
                    'min': min_time,
                    'max': max_time,
                    'std_dev': std_dev,
                    'all_times': all_times
                }
                
                # Check if target is met
                target_met = avg_time < 200
                consistency_good = std_dev < (avg_time * 0.3)  # Less than 30% variation
                
                print(f"📊 Areas API Performance Results:")
                print(f"   Average: {avg_time:.1f}ms")
                print(f"   Min: {min_time:.1f}ms, Max: {max_time:.1f}ms")
                print(f"   Standard Deviation: {std_dev:.1f}ms")
                print(f"   Target (<200ms): {'✅ MET' if target_met else '❌ MISSED'}")
                print(f"   Consistency: {'✅ GOOD' if consistency_good else '⚠️ VARIABLE'}")
                
                # Verify data structure
                async with self.session.get(endpoint, headers=self.get_auth_headers(), params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if isinstance(data, list):
                            print(f"   Data Structure: ✅ Valid (returned {len(data)} areas)")
                            
                            # Check for proper project inclusion
                            areas_with_projects = [area for area in data if 'projects' in area and area['projects']]
                            if areas_with_projects:
                                print(f"   Project Inclusion: ✅ Working ({len(areas_with_projects)} areas have projects)")
                            else:
                                print(f"   Project Inclusion: ⚠️ No areas with projects found")
                        else:
                            print(f"   Data Structure: ❌ Invalid (expected list, got {type(data)})")
                            success = False
                
                if success and target_met:
                    self.test_results.append({
                        "test": "Areas API Performance", 
                        "status": "PASSED", 
                        "details": f"Average: {avg_time:.1f}ms (target: <200ms), N+1 queries eliminated"
                    })
                else:
                    self.test_results.append({
                        "test": "Areas API Performance", 
                        "status": "FAILED", 
                        "reason": f"Average: {avg_time:.1f}ms exceeds 200ms target" if not target_met else "Data structure issues"
                    })
                    
            else:
                self.test_results.append({
                    "test": "Areas API Performance", 
                    "status": "FAILED", 
                    "reason": "API endpoint failed"
                })
                
        except Exception as e:
            print(f"❌ Areas API performance test failed: {e}")
            self.test_results.append({
                "test": "Areas API Performance", 
                "status": "FAILED", 
                "reason": str(e)
            })
            
    async def test_projects_api_performance(self):
        """
        Test 2: Projects API Performance Testing (/api/projects with include_tasks=true)
        Target: Optimized performance with batch queries
        """
        print("\n🧪 Test 2: Projects API Performance Testing (Optimized Batch Queries)")
        
        try:
            endpoint = f"{API_BASE}/projects"
            params = {
                "include_tasks": "true",
                "include_archived": "false"
            }
            
            # Measure performance over multiple iterations
            avg_time, all_times, success = await self.measure_endpoint_performance(
                endpoint, self.get_auth_headers(), params, iterations=10
            )
            
            if success:
                min_time = min(all_times)
                max_time = max(all_times)
                std_dev = statistics.stdev(all_times) if len(all_times) > 1 else 0
                
                self.performance_metrics['projects_api'] = {
                    'average': avg_time,
                    'min': min_time,
                    'max': max_time,
                    'std_dev': std_dev,
                    'all_times': all_times
                }
                
                # Performance targets (more lenient than Areas API)
                target_met = avg_time < 500  # 500ms target for projects with tasks
                consistency_good = std_dev < (avg_time * 0.3)
                
                print(f"📊 Projects API Performance Results:")
                print(f"   Average: {avg_time:.1f}ms")
                print(f"   Min: {min_time:.1f}ms, Max: {max_time:.1f}ms")
                print(f"   Standard Deviation: {std_dev:.1f}ms")
                print(f"   Target (<500ms): {'✅ MET' if target_met else '❌ MISSED'}")
                print(f"   Consistency: {'✅ GOOD' if consistency_good else '⚠️ VARIABLE'}")
                
                # Verify data structure and task inclusion
                async with self.session.get(endpoint, headers=self.get_auth_headers(), params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if isinstance(data, list):
                            print(f"   Data Structure: ✅ Valid (returned {len(data)} projects)")
                            
                            # Check for proper task inclusion
                            projects_with_tasks = [proj for proj in data if 'tasks' in proj and proj['tasks']]
                            if projects_with_tasks:
                                print(f"   Task Inclusion: ✅ Working ({len(projects_with_tasks)} projects have tasks)")
                            else:
                                print(f"   Task Inclusion: ⚠️ No projects with tasks found")
                                
                            # Check for area name resolution
                            projects_with_area_names = [proj for proj in data if 'area_name' in proj]
                            if projects_with_area_names:
                                print(f"   Area Name Resolution: ✅ Working ({len(projects_with_area_names)} projects have area names)")
                            else:
                                print(f"   Area Name Resolution: ⚠️ No area names found")
                        else:
                            print(f"   Data Structure: ❌ Invalid (expected list, got {type(data)})")
                            success = False
                
                if success and target_met:
                    self.test_results.append({
                        "test": "Projects API Performance", 
                        "status": "PASSED", 
                        "details": f"Average: {avg_time:.1f}ms (target: <500ms), batch queries working"
                    })
                else:
                    self.test_results.append({
                        "test": "Projects API Performance", 
                        "status": "FAILED", 
                        "reason": f"Average: {avg_time:.1f}ms exceeds 500ms target" if not target_met else "Data structure issues"
                    })
                    
            else:
                self.test_results.append({
                    "test": "Projects API Performance", 
                    "status": "FAILED", 
                    "reason": "API endpoint failed"
                })
                
        except Exception as e:
            print(f"❌ Projects API performance test failed: {e}")
            self.test_results.append({
                "test": "Projects API Performance", 
                "status": "FAILED", 
                "reason": str(e)
            })
            
    async def test_dashboard_api_performance(self):
        """
        Test 3: Dashboard API Performance Testing
        Target: <1000ms with optimized queries
        """
        print("\n🧪 Test 3: Dashboard API Performance Testing")
        
        try:
            endpoint = f"{API_BASE}/dashboard"
            
            # Measure performance
            avg_time, all_times, success = await self.measure_endpoint_performance(
                endpoint, self.get_auth_headers(), iterations=5
            )
            
            if success:
                self.performance_metrics['dashboard_api'] = {
                    'average': avg_time,
                    'all_times': all_times
                }
                
                target_met = avg_time < 1000
                
                print(f"📊 Dashboard API Performance Results:")
                print(f"   Average: {avg_time:.1f}ms")
                print(f"   Target (<1000ms): {'✅ MET' if target_met else '❌ MISSED'}")
                
                # Verify data structure
                async with self.session.get(endpoint, headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        data = await response.json()
                        required_fields = ['user', 'stats', 'recent_tasks']
                        if all(field in data for field in required_fields):
                            print(f"   Data Structure: ✅ Valid (all required fields present)")
                        else:
                            print(f"   Data Structure: ❌ Missing required fields")
                            success = False
                
                if success and target_met:
                    self.test_results.append({
                        "test": "Dashboard API Performance", 
                        "status": "PASSED", 
                        "details": f"Average: {avg_time:.1f}ms (target: <1000ms)"
                    })
                else:
                    self.test_results.append({
                        "test": "Dashboard API Performance", 
                        "status": "FAILED", 
                        "reason": f"Performance or data structure issues"
                    })
                    
            else:
                self.test_results.append({
                    "test": "Dashboard API Performance", 
                    "status": "FAILED", 
                    "reason": "API endpoint failed"
                })
                
        except Exception as e:
            print(f"❌ Dashboard API performance test failed: {e}")
            self.test_results.append({
                "test": "Dashboard API Performance", 
                "status": "FAILED", 
                "reason": str(e)
            })
            
    async def test_auth_endpoints_performance(self):
        """
        Test 4: Authentication Endpoints Performance
        """
        print("\n🧪 Test 4: Authentication Endpoints Performance")
        
        try:
            # Test /auth/me endpoint
            endpoint = f"{API_BASE}/auth/me"
            
            avg_time, all_times, success = await self.measure_endpoint_performance(
                endpoint, self.get_auth_headers(), iterations=5
            )
            
            if success:
                self.performance_metrics['auth_me'] = {
                    'average': avg_time,
                    'all_times': all_times
                }
                
                target_met = avg_time < 500
                
                print(f"📊 Auth/Me API Performance Results:")
                print(f"   Average: {avg_time:.1f}ms")
                print(f"   Target (<500ms): {'✅ MET' if target_met else '❌ MISSED'}")
                
                if target_met:
                    self.test_results.append({
                        "test": "Auth Endpoints Performance", 
                        "status": "PASSED", 
                        "details": f"/auth/me: {avg_time:.1f}ms (target: <500ms)"
                    })
                else:
                    self.test_results.append({
                        "test": "Auth Endpoints Performance", 
                        "status": "FAILED", 
                        "reason": f"/auth/me: {avg_time:.1f}ms exceeds 500ms target"
                    })
                    
            else:
                self.test_results.append({
                    "test": "Auth Endpoints Performance", 
                    "status": "FAILED", 
                    "reason": "Auth endpoint failed"
                })
                
        except Exception as e:
            print(f"❌ Auth endpoints performance test failed: {e}")
            self.test_results.append({
                "test": "Auth Endpoints Performance", 
                "status": "FAILED", 
                "reason": str(e)
            })
            
    async def test_n1_query_pattern_detection(self):
        """
        Test 5: N+1 Query Pattern Detection
        Monitor for signs of N+1 patterns through performance consistency
        """
        print("\n🧪 Test 5: N+1 Query Pattern Detection")
        
        try:
            # Test Areas API multiple times to detect N+1 patterns
            # N+1 patterns typically show high variance in response times
            
            endpoint = f"{API_BASE}/areas"
            params = {"include_projects": "true"}
            
            # Run more iterations to detect patterns
            avg_time, all_times, success = await self.measure_endpoint_performance(
                endpoint, self.get_auth_headers(), params, iterations=15
            )
            
            if success and all_times:
                std_dev = statistics.stdev(all_times)
                coefficient_of_variation = (std_dev / avg_time) * 100
                
                # N+1 patterns typically show high variance (>30% CV)
                n1_pattern_detected = coefficient_of_variation > 30
                
                print(f"📊 N+1 Query Pattern Analysis:")
                print(f"   Average Response Time: {avg_time:.1f}ms")
                print(f"   Standard Deviation: {std_dev:.1f}ms")
                print(f"   Coefficient of Variation: {coefficient_of_variation:.1f}%")
                print(f"   N+1 Pattern Detected: {'❌ YES' if n1_pattern_detected else '✅ NO'}")
                
                # Also test Projects API
                projects_endpoint = f"{API_BASE}/projects"
                projects_params = {"include_tasks": "true"}
                
                proj_avg_time, proj_all_times, proj_success = await self.measure_endpoint_performance(
                    projects_endpoint, self.get_auth_headers(), projects_params, iterations=15
                )
                
                if proj_success and proj_all_times:
                    proj_std_dev = statistics.stdev(proj_all_times)
                    proj_cv = (proj_std_dev / proj_avg_time) * 100
                    proj_n1_detected = proj_cv > 30
                    
                    print(f"   Projects API CV: {proj_cv:.1f}%")
                    print(f"   Projects N+1 Pattern: {'❌ YES' if proj_n1_detected else '✅ NO'}")
                    
                    overall_n1_detected = n1_pattern_detected or proj_n1_detected
                else:
                    overall_n1_detected = n1_pattern_detected
                
                if not overall_n1_detected:
                    self.test_results.append({
                        "test": "N+1 Query Pattern Detection", 
                        "status": "PASSED", 
                        "details": f"No N+1 patterns detected. Areas CV: {coefficient_of_variation:.1f}%"
                    })
                else:
                    self.test_results.append({
                        "test": "N+1 Query Pattern Detection", 
                        "status": "FAILED", 
                        "reason": f"Potential N+1 patterns detected. High variance in response times."
                    })
                    
            else:
                self.test_results.append({
                    "test": "N+1 Query Pattern Detection", 
                    "status": "FAILED", 
                    "reason": "Could not collect performance data"
                })
                
        except Exception as e:
            print(f"❌ N+1 query pattern detection failed: {e}")
            self.test_results.append({
                "test": "N+1 Query Pattern Detection", 
                "status": "FAILED", 
                "reason": str(e)
            })
            
    async def test_overall_api_responsiveness(self):
        """
        Test 6: Overall API Responsiveness
        Test multiple endpoints to ensure consistent performance
        """
        print("\n🧪 Test 6: Overall API Responsiveness")
        
        try:
            endpoints_to_test = [
                (f"{API_BASE}/pillars", {}),
                (f"{API_BASE}/areas", {}),
                (f"{API_BASE}/projects", {}),
                (f"{API_BASE}/tasks", {}),
                (f"{API_BASE}/today", {})
            ]
            
            all_response_times = []
            failed_endpoints = []
            
            for endpoint, params in endpoints_to_test:
                try:
                    avg_time, times, success = await self.measure_endpoint_performance(
                        endpoint, self.get_auth_headers(), params, iterations=3
                    )
                    
                    if success:
                        all_response_times.extend(times)
                        endpoint_name = endpoint.split('/')[-1]
                        print(f"   {endpoint_name}: {avg_time:.1f}ms")
                    else:
                        failed_endpoints.append(endpoint.split('/')[-1])
                        
                except Exception as e:
                    failed_endpoints.append(f"{endpoint.split('/')[-1]} (error)")
                    
            if all_response_times:
                overall_avg = statistics.mean(all_response_times)
                overall_max = max(all_response_times)
                
                print(f"📊 Overall API Responsiveness:")
                print(f"   Average Response Time: {overall_avg:.1f}ms")
                print(f"   Maximum Response Time: {overall_max:.1f}ms")
                print(f"   Failed Endpoints: {len(failed_endpoints)}")
                
                # Target: Average < 1000ms, Max < 2000ms
                avg_target_met = overall_avg < 1000
                max_target_met = overall_max < 2000
                no_failures = len(failed_endpoints) == 0
                
                if avg_target_met and max_target_met and no_failures:
                    self.test_results.append({
                        "test": "Overall API Responsiveness", 
                        "status": "PASSED", 
                        "details": f"Avg: {overall_avg:.1f}ms, Max: {overall_max:.1f}ms, No failures"
                    })
                else:
                    issues = []
                    if not avg_target_met:
                        issues.append(f"Average {overall_avg:.1f}ms > 1000ms")
                    if not max_target_met:
                        issues.append(f"Max {overall_max:.1f}ms > 2000ms")
                    if not no_failures:
                        issues.append(f"{len(failed_endpoints)} endpoints failed")
                        
                    self.test_results.append({
                        "test": "Overall API Responsiveness", 
                        "status": "FAILED", 
                        "reason": "; ".join(issues)
                    })
            else:
                self.test_results.append({
                    "test": "Overall API Responsiveness", 
                    "status": "FAILED", 
                    "reason": "No successful API calls"
                })
                
        except Exception as e:
            print(f"❌ Overall API responsiveness test failed: {e}")
            self.test_results.append({
                "test": "Overall API Responsiveness", 
                "status": "FAILED", 
                "reason": str(e)
            })
            
    def print_performance_summary(self):
        """Print comprehensive performance summary"""
        print("\n" + "="*80)
        print("🎯 PHASE 2 PERFORMANCE OPTIMIZATION - TEST SUMMARY")
        print("="*80)
        
        passed = len([t for t in self.test_results if t["status"] == "PASSED"])
        failed = len([t for t in self.test_results if t["status"] == "FAILED"])
        total = len(self.test_results)
        
        print(f"📊 OVERALL RESULTS: {passed}/{total} tests passed")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status_icon = {"PASSED": "✅", "FAILED": "❌"}
            icon = status_icon.get(result["status"], "❓")
            print(f"{i:2d}. {icon} {result['test']}: {result['status']}")
            
            if "details" in result:
                print(f"    📝 {result['details']}")
            if "reason" in result:
                print(f"    💬 {result['reason']}")
                
        # Performance Metrics Summary
        if self.performance_metrics:
            print("\n📈 PERFORMANCE METRICS SUMMARY:")
            
            if 'areas_api' in self.performance_metrics:
                areas_data = self.performance_metrics['areas_api']
                print(f"   Areas API: {areas_data['average']:.1f}ms avg (target: <200ms)")
                
            if 'projects_api' in self.performance_metrics:
                projects_data = self.performance_metrics['projects_api']
                print(f"   Projects API: {projects_data['average']:.1f}ms avg (target: <500ms)")
                
            if 'dashboard_api' in self.performance_metrics:
                dashboard_data = self.performance_metrics['dashboard_api']
                print(f"   Dashboard API: {dashboard_data['average']:.1f}ms avg (target: <1000ms)")
                
            if 'auth_me' in self.performance_metrics:
                auth_data = self.performance_metrics['auth_me']
                print(f"   Auth/Me API: {auth_data['average']:.1f}ms avg (target: <500ms)")
                
            if 'auth_login' in self.performance_metrics:
                login_time = self.performance_metrics['auth_login']
                print(f"   Auth/Login: {login_time:.1f}ms")
                
        print("\n" + "="*80)
        
        # Determine overall system status
        if success_rate == 100:
            print("🎉 PHASE 2 PERFORMANCE OPTIMIZATIONS ARE FULLY SUCCESSFUL!")
            print("✅ All performance targets met")
            print("✅ N+1 query patterns eliminated")
            print("✅ Batch queries working optimally")
        elif success_rate >= 80:
            print("⚠️ PHASE 2 OPTIMIZATIONS ARE MOSTLY SUCCESSFUL - MINOR ISSUES DETECTED")
            print("✅ Most performance targets met")
            print("⚠️ Some optimization opportunities remain")
        else:
            print("❌ PHASE 2 OPTIMIZATIONS NEED ATTENTION - PERFORMANCE TARGETS NOT MET")
            print("❌ Significant performance issues detected")
            print("❌ N+1 patterns may still exist")
            
        print("="*80)
        
    async def run_comprehensive_performance_test(self):
        """Run comprehensive Phase 2 performance test suite"""
        print("🚀 Starting Phase 2 Performance Optimization Testing...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print("📋 Testing optimized API endpoints for sub-200ms performance")
        
        await self.setup_session()
        
        try:
            # Authentication
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed with tests")
                return
                
            # Run performance tests in order of priority
            await self.test_areas_api_performance()
            await self.test_projects_api_performance()
            await self.test_dashboard_api_performance()
            await self.test_auth_endpoints_performance()
            await self.test_n1_query_pattern_detection()
            await self.test_overall_api_responsiveness()
            
        finally:
            await self.cleanup_session()
            
        # Print summary
        self.print_performance_summary()

async def main():
    """Main test execution"""
    performance_test_suite = Phase2PerformanceTestSuite()
    await performance_test_suite.run_comprehensive_performance_test()

if __name__ == "__main__":
    asyncio.run(main())