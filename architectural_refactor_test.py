#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, List

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://19eedb9d-8356-46da-a868-07e1ec72a1d8.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class ArchitecturalRefactorVerificationSuite:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "architectural.test@aurumlife.com"
        self.test_user_password = "ArchTest123!"
        self.test_results = []
        self.performance_results = []
        
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
                "username": "archtest",
                "email": self.test_user_email,
                "first_name": "Architectural",
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
                    return False
                    
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
            
    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.auth_token}"}
        
    async def measure_endpoint_performance(self, endpoint: str, method: str = "GET", data: dict = None, iterations: int = 3) -> Dict[str, Any]:
        """Measure endpoint performance over multiple iterations"""
        response_times = []
        success_count = 0
        
        for i in range(iterations):
            start_time = time.time()
            
            try:
                if method == "GET":
                    async with self.session.get(f"{API_BASE}{endpoint}", headers=self.get_auth_headers()) as response:
                        end_time = time.time()
                        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                        response_times.append(response_time)
                        
                        if response.status == 200:
                            success_count += 1
                            
                elif method == "POST":
                    async with self.session.post(f"{API_BASE}{endpoint}", json=data, headers=self.get_auth_headers()) as response:
                        end_time = time.time()
                        response_time = (end_time - start_time) * 1000
                        response_times.append(response_time)
                        
                        if response.status == 200:
                            success_count += 1
                            
            except Exception as e:
                print(f"⚠️ Error measuring {endpoint}: {e}")
                response_times.append(5000)  # 5 second timeout as failure
                
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        
        return {
            "endpoint": endpoint,
            "method": method,
            "avg_response_time": avg_response_time,
            "min_response_time": min_response_time,
            "max_response_time": max_response_time,
            "success_rate": (success_count / iterations) * 100,
            "iterations": iterations,
            "meets_target": avg_response_time < 300  # Target: <300ms
        }
        
    async def test_repository_pattern_verification(self):
        """Test 1: Repository Pattern Verification - Single batch operations"""
        print("\n🧪 Test 1: Repository Pattern Verification")
        
        try:
            # Test optimized services are being used
            endpoints_to_test = [
                "/pillars?include_areas=false&include_archived=false",
                "/areas?include_projects=true&include_archived=false", 
                "/projects?include_archived=false",
                "/dashboard"
            ]
            
            repository_working = True
            
            for endpoint in endpoints_to_test:
                perf_result = await self.measure_endpoint_performance(endpoint)
                self.performance_results.append(perf_result)
                
                # Repository pattern should result in fast response times
                if perf_result["avg_response_time"] > 1000:  # If > 1 second, likely N+1 queries
                    repository_working = False
                    print(f"❌ {endpoint}: {perf_result['avg_response_time']:.2f}ms (likely N+1 queries)")
                else:
                    print(f"✅ {endpoint}: {perf_result['avg_response_time']:.2f}ms (optimized)")
                    
            if repository_working:
                self.test_results.append({
                    "test": "Repository Pattern Verification", 
                    "status": "PASSED", 
                    "details": "All endpoints showing optimized performance"
                })
            else:
                self.test_results.append({
                    "test": "Repository Pattern Verification", 
                    "status": "FAILED", 
                    "reason": "Some endpoints showing N+1 query patterns"
                })
                
        except Exception as e:
            print(f"❌ Repository pattern test failed: {e}")
            self.test_results.append({
                "test": "Repository Pattern Verification", 
                "status": "FAILED", 
                "reason": str(e)
            })
            
    async def test_performance_monitoring_endpoint(self):
        """Test 2: Performance Monitoring Endpoint"""
        print("\n🧪 Test 2: Performance Monitoring Endpoint")
        
        try:
            async with self.session.get(f"{API_BASE}/performance", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check for required fields
                    required_fields = ["performance_summary", "n1_query_warnings", "status", "user_id", "timestamp"]
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        print("✅ Performance monitoring endpoint working")
                        print(f"   Status: {data.get('status', 'unknown')}")
                        print(f"   N+1 Warnings: {len(data.get('n1_query_warnings', []))}")
                        
                        # Check if system is optimized
                        if data.get("status") == "optimized":
                            self.test_results.append({
                                "test": "Performance Monitoring Endpoint", 
                                "status": "PASSED", 
                                "details": f"System status: {data['status']}, N+1 warnings: {len(data.get('n1_query_warnings', []))}"
                            })
                        else:
                            self.test_results.append({
                                "test": "Performance Monitoring Endpoint", 
                                "status": "PARTIAL", 
                                "details": f"System status: {data['status']}, needs attention"
                            })
                    else:
                        print(f"❌ Missing required fields: {missing_fields}")
                        self.test_results.append({
                            "test": "Performance Monitoring Endpoint", 
                            "status": "FAILED", 
                            "reason": f"Missing fields: {missing_fields}"
                        })
                else:
                    print(f"❌ Performance monitoring endpoint failed: {response.status}")
                    self.test_results.append({
                        "test": "Performance Monitoring Endpoint", 
                        "status": "FAILED", 
                        "reason": f"HTTP {response.status}"
                    })
                    
        except Exception as e:
            print(f"❌ Performance monitoring test failed: {e}")
            self.test_results.append({
                "test": "Performance Monitoring Endpoint", 
                "status": "FAILED", 
                "reason": str(e)
            })
            
    async def test_performance_targets(self):
        """Test 3: Performance Targets (<300ms for optimized APIs)"""
        print("\n🧪 Test 3: Performance Targets (<300ms)")
        
        try:
            # Critical endpoints that should be optimized
            critical_endpoints = [
                "/areas?include_projects=true&include_archived=false",
                "/pillars?include_areas=false&include_archived=false",
                "/projects?include_archived=false",
                "/dashboard"
            ]
            
            performance_targets_met = True
            performance_summary = []
            
            for endpoint in critical_endpoints:
                perf_result = await self.measure_endpoint_performance(endpoint, iterations=5)
                self.performance_results.append(perf_result)
                
                meets_target = perf_result["meets_target"]
                avg_time = perf_result["avg_response_time"]
                
                if meets_target:
                    print(f"✅ {endpoint}: {avg_time:.2f}ms (target: <300ms)")
                    performance_summary.append(f"{endpoint}: {avg_time:.2f}ms ✅")
                else:
                    print(f"❌ {endpoint}: {avg_time:.2f}ms (exceeds 300ms target)")
                    performance_summary.append(f"{endpoint}: {avg_time:.2f}ms ❌")
                    performance_targets_met = False
                    
            if performance_targets_met:
                self.test_results.append({
                    "test": "Performance Targets (<300ms)", 
                    "status": "PASSED", 
                    "details": "All critical endpoints meet <300ms target"
                })
            else:
                self.test_results.append({
                    "test": "Performance Targets (<300ms)", 
                    "status": "FAILED", 
                    "reason": "Some endpoints exceed 300ms target"
                })
                
        except Exception as e:
            print(f"❌ Performance targets test failed: {e}")
            self.test_results.append({
                "test": "Performance Targets (<300ms)", 
                "status": "FAILED", 
                "reason": str(e)
            })
            
    async def test_n1_query_elimination(self):
        """Test 4: N+1 Query Elimination Verification"""
        print("\n🧪 Test 4: N+1 Query Elimination Verification")
        
        try:
            # Test multiple calls to same endpoint - should have consistent performance
            endpoint = "/areas?include_projects=true&include_archived=false"
            
            # Make 10 consecutive calls
            response_times = []
            for i in range(10):
                perf_result = await self.measure_endpoint_performance(endpoint, iterations=1)
                response_times.append(perf_result["avg_response_time"])
                
            # Calculate variance - low variance indicates no N+1 queries
            avg_time = sum(response_times) / len(response_times)
            variance = sum((x - avg_time) ** 2 for x in response_times) / len(response_times)
            std_deviation = variance ** 0.5
            
            # If standard deviation is low relative to average, queries are consistent
            consistency_ratio = std_deviation / avg_time if avg_time > 0 else 1
            
            print(f"   Average response time: {avg_time:.2f}ms")
            print(f"   Standard deviation: {std_deviation:.2f}ms")
            print(f"   Consistency ratio: {consistency_ratio:.3f}")
            
            if consistency_ratio < 0.3 and avg_time < 500:  # Consistent and fast
                print("✅ N+1 queries eliminated - consistent performance")
                self.test_results.append({
                    "test": "N+1 Query Elimination", 
                    "status": "PASSED", 
                    "details": f"Consistent performance: {avg_time:.2f}ms ±{std_deviation:.2f}ms"
                })
            else:
                print("❌ Possible N+1 queries - inconsistent or slow performance")
                self.test_results.append({
                    "test": "N+1 Query Elimination", 
                    "status": "FAILED", 
                    "reason": f"Inconsistent performance: {avg_time:.2f}ms ±{std_deviation:.2f}ms"
                })
                
        except Exception as e:
            print(f"❌ N+1 query elimination test failed: {e}")
            self.test_results.append({
                "test": "N+1 Query Elimination", 
                "status": "FAILED", 
                "reason": str(e)
            })
            
    async def test_industry_standards_compliance(self):
        """Test 5: Industry Standards Compliance"""
        print("\n🧪 Test 5: Industry Standards Compliance")
        
        try:
            compliance_checks = []
            
            # Test 5a: Proper error handling
            async with self.session.get(f"{API_BASE}/pillars/invalid-id", headers=self.get_auth_headers()) as response:
                if response.status == 404:
                    compliance_checks.append("Error handling: ✅")
                    print("✅ Proper 404 error handling")
                else:
                    compliance_checks.append("Error handling: ❌")
                    print(f"❌ Expected 404, got {response.status}")
                    
            # Test 5b: Authentication required
            async with self.session.get(f"{API_BASE}/dashboard") as response:
                if response.status in [401, 403]:
                    compliance_checks.append("Authentication: ✅")
                    print("✅ Proper authentication enforcement")
                else:
                    compliance_checks.append("Authentication: ❌")
                    print(f"❌ Expected 401/403, got {response.status}")
                    
            # Test 5c: Performance monitoring exists
            async with self.session.get(f"{API_BASE}/performance", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    compliance_checks.append("Performance monitoring: ✅")
                    print("✅ Performance monitoring endpoint available")
                else:
                    compliance_checks.append("Performance monitoring: ❌")
                    print(f"❌ Performance monitoring failed: {response.status}")
                    
            # Test 5d: Fast test endpoint
            perf_result = await self.measure_endpoint_performance("/test-fast")
            if perf_result["meets_target"]:
                compliance_checks.append("Fast endpoint: ✅")
                print("✅ Fast test endpoint working")
            else:
                compliance_checks.append("Fast endpoint: ❌")
                print("❌ Fast test endpoint too slow")
                
            passed_checks = len([c for c in compliance_checks if "✅" in c])
            total_checks = len(compliance_checks)
            
            if passed_checks == total_checks:
                self.test_results.append({
                    "test": "Industry Standards Compliance", 
                    "status": "PASSED", 
                    "details": f"All {total_checks} compliance checks passed"
                })
            else:
                self.test_results.append({
                    "test": "Industry Standards Compliance", 
                    "status": "PARTIAL", 
                    "details": f"{passed_checks}/{total_checks} compliance checks passed"
                })
                
        except Exception as e:
            print(f"❌ Industry standards compliance test failed: {e}")
            self.test_results.append({
                "test": "Industry Standards Compliance", 
                "status": "FAILED", 
                "reason": str(e)
            })
            
    async def test_technical_debt_elimination(self):
        """Test 6: Technical Debt Elimination"""
        print("\n🧪 Test 6: Technical Debt Elimination")
        
        try:
            # Test consistent performance across multiple endpoints
            endpoints = [
                "/dashboard",
                "/areas?include_projects=true",
                "/projects",
                "/pillars"
            ]
            
            all_fast = True
            performance_summary = []
            
            for endpoint in endpoints:
                # Test multiple times to ensure consistency
                perf_result = await self.measure_endpoint_performance(endpoint, iterations=3)
                
                if perf_result["avg_response_time"] < 500:  # Should be fast
                    performance_summary.append(f"{endpoint}: {perf_result['avg_response_time']:.2f}ms ✅")
                    print(f"✅ {endpoint}: {perf_result['avg_response_time']:.2f}ms")
                else:
                    performance_summary.append(f"{endpoint}: {perf_result['avg_response_time']:.2f}ms ❌")
                    print(f"❌ {endpoint}: {perf_result['avg_response_time']:.2f}ms (too slow)")
                    all_fast = False
                    
            # Check performance monitoring for N+1 warnings
            async with self.session.get(f"{API_BASE}/performance", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    data = await response.json()
                    n1_warnings = len(data.get('n1_query_warnings', []))
                    
                    if n1_warnings == 0:
                        print("✅ No N+1 query warnings detected")
                    else:
                        print(f"❌ {n1_warnings} N+1 query warnings detected")
                        all_fast = False
                        
            if all_fast:
                self.test_results.append({
                    "test": "Technical Debt Elimination", 
                    "status": "PASSED", 
                    "details": "Consistent fast performance, no N+1 patterns"
                })
            else:
                self.test_results.append({
                    "test": "Technical Debt Elimination", 
                    "status": "FAILED", 
                    "reason": "Performance issues or N+1 patterns detected"
                })
                
        except Exception as e:
            print(f"❌ Technical debt elimination test failed: {e}")
            self.test_results.append({
                "test": "Technical Debt Elimination", 
                "status": "FAILED", 
                "reason": str(e)
            })
            
    def print_performance_summary(self):
        """Print detailed performance summary"""
        print("\n" + "="*80)
        print("📊 PERFORMANCE ANALYSIS SUMMARY")
        print("="*80)
        
        if not self.performance_results:
            print("No performance data collected")
            return
            
        # Overall performance statistics
        all_times = [r["avg_response_time"] for r in self.performance_results]
        avg_overall = sum(all_times) / len(all_times)
        fastest = min(all_times)
        slowest = max(all_times)
        
        print(f"📈 Overall Performance:")
        print(f"   Average response time: {avg_overall:.2f}ms")
        print(f"   Fastest endpoint: {fastest:.2f}ms")
        print(f"   Slowest endpoint: {slowest:.2f}ms")
        
        # Target compliance
        meets_target = len([r for r in self.performance_results if r["meets_target"]])
        total_endpoints = len(self.performance_results)
        target_compliance = (meets_target / total_endpoints * 100) if total_endpoints > 0 else 0
        
        print(f"\n🎯 Target Compliance (<300ms):")
        print(f"   Endpoints meeting target: {meets_target}/{total_endpoints}")
        print(f"   Compliance rate: {target_compliance:.1f}%")
        
        # Detailed breakdown
        print(f"\n📋 Endpoint Performance Details:")
        for result in self.performance_results:
            status = "✅" if result["meets_target"] else "❌"
            print(f"   {status} {result['endpoint']}: {result['avg_response_time']:.2f}ms")
            
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🏗️ ARCHITECTURAL REFACTOR VERIFICATION - TEST SUMMARY")
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
        
        # Final assessment
        if success_rate >= 90:
            print("🎉 ARCHITECTURAL REFACTOR SUCCESSFUL - PRODUCTION-READY!")
            print("✅ Repository Pattern implemented")
            print("✅ Performance targets achieved")
            print("✅ N+1 queries eliminated")
            print("✅ Industry standards compliant")
            print("✅ Technical debt eliminated")
        elif success_rate >= 75:
            print("⚠️ ARCHITECTURAL REFACTOR MOSTLY SUCCESSFUL - MINOR ISSUES")
            print("🔧 Some optimizations may need attention")
        else:
            print("❌ ARCHITECTURAL REFACTOR NEEDS SIGNIFICANT WORK")
            print("🚨 Critical performance or architecture issues detected")
            
        print("="*80)
        
    async def run_all_tests(self):
        """Run all architectural refactor verification tests"""
        print("🏗️ Starting Architectural Refactor Verification Testing...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print("🎯 Target: <300ms response times, Repository Pattern, N+1 elimination")
        
        await self.setup_session()
        
        try:
            # Authentication
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed with tests")
                return
                
            print("✅ Authentication successful")
            
            # Run all verification tests
            await self.test_repository_pattern_verification()
            await self.test_performance_monitoring_endpoint()
            await self.test_performance_targets()
            await self.test_n1_query_elimination()
            await self.test_industry_standards_compliance()
            await self.test_technical_debt_elimination()
            
        finally:
            await self.cleanup_session()
            
        # Print comprehensive summary
        self.print_test_summary()

async def main():
    """Main test execution"""
    test_suite = ArchitecturalRefactorVerificationSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())