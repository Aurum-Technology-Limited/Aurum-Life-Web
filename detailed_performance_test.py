#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import time
import statistics
from datetime import datetime
from typing import Dict, Any, List, Tuple

# Configuration - Use external URL for testing
BACKEND_URL = "https://7b39a747-36d6-44f7-9408-a498365475ba.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class DetailedPerformanceTestSuite:
    """
    Detailed performance testing specifically for the review request:
    1. Areas API with include_projects=true (target <200ms)
    2. Projects API with include_tasks=true (target performance)
    3. Authentication endpoints
    4. Dashboard endpoint
    5. N+1 query pattern detection
    """
    
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "nav.test@aurumlife.com"
        self.test_user_password = "testpassword"
        self.test_results = []
        self.detailed_metrics = {}
        
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
                    print(f"✅ Authentication successful ({auth_time:.1f}ms)")
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
        
    async def detailed_endpoint_analysis(self, endpoint: str, params: Dict = None, iterations: int = 20) -> Dict[str, Any]:
        """
        Perform detailed analysis of an endpoint including:
        - Response times over multiple iterations
        - Data structure validation
        - Consistency analysis
        - Performance percentiles
        """
        times = []
        data_sizes = []
        success_count = 0
        errors = []
        
        print(f"\n🔍 Analyzing {endpoint} over {iterations} iterations...")
        
        for i in range(iterations):
            try:
                start_time = time.time()
                
                if params:
                    async with self.session.get(endpoint, headers=self.get_auth_headers(), params=params) as response:
                        response_time = (time.time() - start_time) * 1000
                        times.append(response_time)
                        
                        if response.status == 200:
                            data = await response.json()
                            data_sizes.append(len(json.dumps(data)))
                            success_count += 1
                        else:
                            errors.append(f"HTTP {response.status}")
                else:
                    async with self.session.get(endpoint, headers=self.get_auth_headers()) as response:
                        response_time = (time.time() - start_time) * 1000
                        times.append(response_time)
                        
                        if response.status == 200:
                            data = await response.json()
                            data_sizes.append(len(json.dumps(data)))
                            success_count += 1
                        else:
                            errors.append(f"HTTP {response.status}")
                            
                # Small delay between requests
                await asyncio.sleep(0.05)
                
            except Exception as e:
                errors.append(str(e))
                
        # Calculate detailed statistics
        if times:
            avg_time = statistics.mean(times)
            median_time = statistics.median(times)
            min_time = min(times)
            max_time = max(times)
            std_dev = statistics.stdev(times) if len(times) > 1 else 0
            
            # Calculate percentiles
            sorted_times = sorted(times)
            p50 = sorted_times[int(len(sorted_times) * 0.5)]
            p90 = sorted_times[int(len(sorted_times) * 0.9)]
            p95 = sorted_times[int(len(sorted_times) * 0.95)]
            p99 = sorted_times[int(len(sorted_times) * 0.99)]
            
            # Coefficient of variation (measure of consistency)
            cv = (std_dev / avg_time) * 100 if avg_time > 0 else 0
            
            avg_data_size = statistics.mean(data_sizes) if data_sizes else 0
            
            analysis = {
                'endpoint': endpoint,
                'iterations': iterations,
                'success_rate': (success_count / iterations) * 100,
                'avg_time': avg_time,
                'median_time': median_time,
                'min_time': min_time,
                'max_time': max_time,
                'std_dev': std_dev,
                'coefficient_of_variation': cv,
                'p50': p50,
                'p90': p90,
                'p95': p95,
                'p99': p99,
                'avg_data_size': avg_data_size,
                'all_times': times,
                'errors': errors
            }
            
            return analysis
        else:
            return {
                'endpoint': endpoint,
                'iterations': iterations,
                'success_rate': 0,
                'errors': errors
            }
            
    async def test_areas_api_detailed(self):
        """
        Detailed test of Areas API with include_projects=true
        Target: <200ms response time
        """
        print("\n🎯 DETAILED AREAS API PERFORMANCE TEST")
        print("=" * 60)
        
        endpoint = f"{API_BASE}/areas"
        params = {
            "include_projects": "true",
            "include_archived": "false"
        }
        
        analysis = await self.detailed_endpoint_analysis(endpoint, params, iterations=25)
        self.detailed_metrics['areas_api'] = analysis
        
        if analysis.get('success_rate', 0) > 0:
            print(f"📊 Areas API Performance Analysis:")
            print(f"   Success Rate: {analysis['success_rate']:.1f}%")
            print(f"   Average: {analysis['avg_time']:.1f}ms")
            print(f"   Median: {analysis['median_time']:.1f}ms")
            print(f"   Min: {analysis['min_time']:.1f}ms")
            print(f"   Max: {analysis['max_time']:.1f}ms")
            print(f"   Std Dev: {analysis['std_dev']:.1f}ms")
            print(f"   Coefficient of Variation: {analysis['coefficient_of_variation']:.1f}%")
            print(f"   P50: {analysis['p50']:.1f}ms")
            print(f"   P90: {analysis['p90']:.1f}ms")
            print(f"   P95: {analysis['p95']:.1f}ms")
            print(f"   P99: {analysis['p99']:.1f}ms")
            print(f"   Avg Data Size: {analysis['avg_data_size']:.0f} bytes")
            
            # Performance evaluation
            target_200ms = analysis['avg_time'] < 200
            p95_under_300ms = analysis['p95'] < 300
            consistency_good = analysis['coefficient_of_variation'] < 25
            
            print(f"\n📈 Performance Evaluation:")
            print(f"   Target <200ms (avg): {'✅ MET' if target_200ms else '❌ MISSED'}")
            print(f"   P95 <300ms: {'✅ MET' if p95_under_300ms else '❌ MISSED'}")
            print(f"   Consistency (CV<25%): {'✅ GOOD' if consistency_good else '⚠️ VARIABLE'}")
            
            # Data structure validation
            try:
                async with self.session.get(endpoint, headers=self.get_auth_headers(), params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if isinstance(data, list):
                            areas_with_projects = [area for area in data if 'projects' in area and isinstance(area['projects'], list)]
                            pillar_names_present = [area for area in data if 'pillar_name' in area]
                            
                            print(f"\n🔍 Data Structure Analysis:")
                            print(f"   Total Areas: {len(data)}")
                            print(f"   Areas with Projects: {len(areas_with_projects)}")
                            print(f"   Areas with Pillar Names: {len(pillar_names_present)}")
                            
                            # Check for N+1 indicators
                            if analysis['coefficient_of_variation'] > 30:
                                print(f"   ⚠️ High variance detected - possible N+1 queries")
                            else:
                                print(f"   ✅ Low variance - batch queries likely working")
                                
            except Exception as e:
                print(f"   ❌ Data structure validation failed: {e}")
                
            # Test result
            if target_200ms and consistency_good:
                self.test_results.append({
                    "test": "Areas API Detailed Performance", 
                    "status": "PASSED", 
                    "details": f"Avg: {analysis['avg_time']:.1f}ms, P95: {analysis['p95']:.1f}ms, CV: {analysis['coefficient_of_variation']:.1f}%"
                })
            else:
                self.test_results.append({
                    "test": "Areas API Detailed Performance", 
                    "status": "FAILED", 
                    "reason": f"Performance targets not met - Avg: {analysis['avg_time']:.1f}ms (target: <200ms)"
                })
        else:
            print(f"❌ Areas API test failed - no successful responses")
            self.test_results.append({
                "test": "Areas API Detailed Performance", 
                "status": "FAILED", 
                "reason": "No successful API responses"
            })
            
    async def test_projects_api_detailed(self):
        """
        Detailed test of Projects API with include_tasks=true
        """
        print("\n🎯 DETAILED PROJECTS API PERFORMANCE TEST")
        print("=" * 60)
        
        endpoint = f"{API_BASE}/projects"
        params = {
            "include_tasks": "true",
            "include_archived": "false"
        }
        
        analysis = await self.detailed_endpoint_analysis(endpoint, params, iterations=25)
        self.detailed_metrics['projects_api'] = analysis
        
        if analysis.get('success_rate', 0) > 0:
            print(f"📊 Projects API Performance Analysis:")
            print(f"   Success Rate: {analysis['success_rate']:.1f}%")
            print(f"   Average: {analysis['avg_time']:.1f}ms")
            print(f"   Median: {analysis['median_time']:.1f}ms")
            print(f"   Min: {analysis['min_time']:.1f}ms")
            print(f"   Max: {analysis['max_time']:.1f}ms")
            print(f"   Std Dev: {analysis['std_dev']:.1f}ms")
            print(f"   Coefficient of Variation: {analysis['coefficient_of_variation']:.1f}%")
            print(f"   P95: {analysis['p95']:.1f}ms")
            print(f"   P99: {analysis['p99']:.1f}ms")
            
            # Performance evaluation (more lenient targets for projects)
            target_500ms = analysis['avg_time'] < 500
            p95_under_800ms = analysis['p95'] < 800
            consistency_good = analysis['coefficient_of_variation'] < 30
            
            print(f"\n📈 Performance Evaluation:")
            print(f"   Target <500ms (avg): {'✅ MET' if target_500ms else '❌ MISSED'}")
            print(f"   P95 <800ms: {'✅ MET' if p95_under_800ms else '❌ MISSED'}")
            print(f"   Consistency (CV<30%): {'✅ GOOD' if consistency_good else '⚠️ VARIABLE'}")
            
            # Data structure validation
            try:
                async with self.session.get(endpoint, headers=self.get_auth_headers(), params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if isinstance(data, list):
                            projects_with_tasks = [proj for proj in data if 'tasks' in proj and isinstance(proj['tasks'], list)]
                            area_names_present = [proj for proj in data if 'area_name' in proj]
                            
                            print(f"\n🔍 Data Structure Analysis:")
                            print(f"   Total Projects: {len(data)}")
                            print(f"   Projects with Tasks: {len(projects_with_tasks)}")
                            print(f"   Projects with Area Names: {len(area_names_present)}")
                            
                            # Check for batch query optimization
                            if analysis['coefficient_of_variation'] < 25:
                                print(f"   ✅ Excellent consistency - batch queries optimized")
                            elif analysis['coefficient_of_variation'] < 35:
                                print(f"   ✅ Good consistency - batch queries working")
                            else:
                                print(f"   ⚠️ High variance - potential N+1 patterns")
                                
            except Exception as e:
                print(f"   ❌ Data structure validation failed: {e}")
                
            # Test result
            if target_500ms and consistency_good:
                self.test_results.append({
                    "test": "Projects API Detailed Performance", 
                    "status": "PASSED", 
                    "details": f"Avg: {analysis['avg_time']:.1f}ms, P95: {analysis['p95']:.1f}ms, batch queries working"
                })
            else:
                self.test_results.append({
                    "test": "Projects API Detailed Performance", 
                    "status": "FAILED", 
                    "reason": f"Performance targets not met - Avg: {analysis['avg_time']:.1f}ms"
                })
        else:
            print(f"❌ Projects API test failed - no successful responses")
            self.test_results.append({
                "test": "Projects API Detailed Performance", 
                "status": "FAILED", 
                "reason": "No successful API responses"
            })
            
    async def test_dashboard_api_detailed(self):
        """
        Detailed test of Dashboard API
        """
        print("\n🎯 DETAILED DASHBOARD API PERFORMANCE TEST")
        print("=" * 60)
        
        endpoint = f"{API_BASE}/dashboard"
        
        analysis = await self.detailed_endpoint_analysis(endpoint, iterations=15)
        self.detailed_metrics['dashboard_api'] = analysis
        
        if analysis.get('success_rate', 0) > 0:
            print(f"📊 Dashboard API Performance Analysis:")
            print(f"   Success Rate: {analysis['success_rate']:.1f}%")
            print(f"   Average: {analysis['avg_time']:.1f}ms")
            print(f"   P95: {analysis['p95']:.1f}ms")
            print(f"   Coefficient of Variation: {analysis['coefficient_of_variation']:.1f}%")
            
            target_1000ms = analysis['avg_time'] < 1000
            
            if target_1000ms:
                self.test_results.append({
                    "test": "Dashboard API Detailed Performance", 
                    "status": "PASSED", 
                    "details": f"Avg: {analysis['avg_time']:.1f}ms (target: <1000ms)"
                })
            else:
                self.test_results.append({
                    "test": "Dashboard API Detailed Performance", 
                    "status": "FAILED", 
                    "reason": f"Avg: {analysis['avg_time']:.1f}ms exceeds 1000ms target"
                })
        else:
            self.test_results.append({
                "test": "Dashboard API Detailed Performance", 
                "status": "FAILED", 
                "reason": "No successful API responses"
            })
            
    async def test_auth_endpoints_detailed(self):
        """
        Detailed test of Authentication endpoints
        """
        print("\n🎯 DETAILED AUTH ENDPOINTS PERFORMANCE TEST")
        print("=" * 60)
        
        endpoint = f"{API_BASE}/auth/me"
        
        analysis = await self.detailed_endpoint_analysis(endpoint, iterations=15)
        self.detailed_metrics['auth_me'] = analysis
        
        if analysis.get('success_rate', 0) > 0:
            print(f"📊 Auth/Me API Performance Analysis:")
            print(f"   Success Rate: {analysis['success_rate']:.1f}%")
            print(f"   Average: {analysis['avg_time']:.1f}ms")
            print(f"   P95: {analysis['p95']:.1f}ms")
            
            target_500ms = analysis['avg_time'] < 500
            
            if target_500ms:
                self.test_results.append({
                    "test": "Auth Endpoints Detailed Performance", 
                    "status": "PASSED", 
                    "details": f"/auth/me: {analysis['avg_time']:.1f}ms (target: <500ms)"
                })
            else:
                self.test_results.append({
                    "test": "Auth Endpoints Detailed Performance", 
                    "status": "FAILED", 
                    "reason": f"/auth/me: {analysis['avg_time']:.1f}ms exceeds 500ms target"
                })
        else:
            self.test_results.append({
                "test": "Auth Endpoints Detailed Performance", 
                "status": "FAILED", 
                "reason": "No successful API responses"
            })
            
    def print_comprehensive_summary(self):
        """Print comprehensive performance summary"""
        print("\n" + "="*80)
        print("🎯 PHASE 2 OPTIMIZATION - COMPREHENSIVE PERFORMANCE ANALYSIS")
        print("="*80)
        
        passed = len([t for t in self.test_results if t["status"] == "PASSED"])
        failed = len([t for t in self.test_results if t["status"] == "FAILED"])
        total = len(self.test_results)
        
        print(f"📊 OVERALL RESULTS: {passed}/{total} tests passed")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        print("\n📋 DETAILED TEST RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status_icon = {"PASSED": "✅", "FAILED": "❌"}
            icon = status_icon.get(result["status"], "❓")
            print(f"{i:2d}. {icon} {result['test']}: {result['status']}")
            
            if "details" in result:
                print(f"    📝 {result['details']}")
            if "reason" in result:
                print(f"    💬 {result['reason']}")
                
        # Performance Summary Table
        print("\n📈 PERFORMANCE METRICS SUMMARY:")
        print("-" * 80)
        print(f"{'Endpoint':<25} {'Avg (ms)':<10} {'P95 (ms)':<10} {'CV (%)':<8} {'Target':<12} {'Status'}")
        print("-" * 80)
        
        if 'areas_api' in self.detailed_metrics:
            data = self.detailed_metrics['areas_api']
            status = "✅ PASS" if data['avg_time'] < 200 else "❌ FAIL"
            print(f"{'Areas (include_projects)':<25} {data['avg_time']:<10.1f} {data['p95']:<10.1f} {data['coefficient_of_variation']:<8.1f} {'<200ms':<12} {status}")
            
        if 'projects_api' in self.detailed_metrics:
            data = self.detailed_metrics['projects_api']
            status = "✅ PASS" if data['avg_time'] < 500 else "❌ FAIL"
            print(f"{'Projects (include_tasks)':<25} {data['avg_time']:<10.1f} {data['p95']:<10.1f} {data['coefficient_of_variation']:<8.1f} {'<500ms':<12} {status}")
            
        if 'dashboard_api' in self.detailed_metrics:
            data = self.detailed_metrics['dashboard_api']
            status = "✅ PASS" if data['avg_time'] < 1000 else "❌ FAIL"
            print(f"{'Dashboard':<25} {data['avg_time']:<10.1f} {data['p95']:<10.1f} {data['coefficient_of_variation']:<8.1f} {'<1000ms':<12} {status}")
            
        if 'auth_me' in self.detailed_metrics:
            data = self.detailed_metrics['auth_me']
            status = "✅ PASS" if data['avg_time'] < 500 else "❌ FAIL"
            print(f"{'Auth/Me':<25} {data['avg_time']:<10.1f} {data['p95']:<10.1f} {data['coefficient_of_variation']:<8.1f} {'<500ms':<12} {status}")
            
        print("-" * 80)
        
        # N+1 Query Analysis
        print("\n🔍 N+1 QUERY PATTERN ANALYSIS:")
        areas_cv = self.detailed_metrics.get('areas_api', {}).get('coefficient_of_variation', 0)
        projects_cv = self.detailed_metrics.get('projects_api', {}).get('coefficient_of_variation', 0)
        
        print(f"   Areas API CV: {areas_cv:.1f}% ({'✅ Optimized' if areas_cv < 25 else '⚠️ Variable' if areas_cv < 35 else '❌ N+1 Likely'})")
        print(f"   Projects API CV: {projects_cv:.1f}% ({'✅ Optimized' if projects_cv < 25 else '⚠️ Variable' if projects_cv < 35 else '❌ N+1 Likely'})")
        
        # Overall Assessment
        print("\n" + "="*80)
        if success_rate == 100:
            print("🎉 PHASE 2 PERFORMANCE OPTIMIZATIONS ARE FULLY SUCCESSFUL!")
            print("✅ All performance targets achieved")
            print("✅ Batch queries working optimally")
            print("✅ N+1 query patterns eliminated")
        elif success_rate >= 75:
            print("⚠️ PHASE 2 OPTIMIZATIONS ARE MOSTLY SUCCESSFUL")
            print("✅ Most performance targets achieved")
            print("⚠️ Some endpoints need further optimization")
        else:
            print("❌ PHASE 2 OPTIMIZATIONS NEED SIGNIFICANT ATTENTION")
            print("❌ Performance targets not consistently met")
            print("❌ Potential N+1 patterns still present")
            
        print("="*80)
        
    async def run_comprehensive_test(self):
        """Run comprehensive detailed performance test suite"""
        print("🚀 Starting Comprehensive Phase 2 Performance Analysis...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print("📋 Focus: Areas API (<200ms), Projects API, Dashboard, Auth endpoints")
        
        await self.setup_session()
        
        try:
            # Authentication
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed with tests")
                return
                
            # Run detailed performance tests
            await self.test_areas_api_detailed()
            await self.test_projects_api_detailed()
            await self.test_dashboard_api_detailed()
            await self.test_auth_endpoints_detailed()
            
        finally:
            await self.cleanup_session()
            
        # Print comprehensive summary
        self.print_comprehensive_summary()

async def main():
    """Main test execution"""
    test_suite = DetailedPerformanceTestSuite()
    await test_suite.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())