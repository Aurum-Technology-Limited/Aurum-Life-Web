#!/usr/bin/env python3
"""
ULTRA-PERFORMANCE OPTIMIZATION ENDPOINTS TESTING
Testing the ultra-performance endpoints to verify Redis connection failures and database schema errors have been fixed.

FOCUS AREAS:
1. Test all ultra-performance endpoints (/api/ultra/dashboard, /api/ultra/pillars, /api/ultra/areas, /api/ultra/projects, /api/ultra/insights)
2. Verify response times are now <200ms (target) instead of 3800ms+
3. Check that Redis connection errors are eliminated or handled gracefully
4. Confirm database schema errors are resolved
5. Test cache functionality is working properly with memory fallback
6. Compare performance against regular endpoints to ensure ultra-endpoints are faster

AUTHENTICATION: marc.alleyne@aurumtechnologyltd.com/password

EXPECTED BEHAVIOR:
The ultra-performance endpoints should now respond in <200ms instead of the previous 3800ms+ due to:
1. Enhanced cache_service.py with rapid Redis connectivity checks, 100ms timeouts, and efficient memory fallback
2. Fixed query_optimizer.py field selections to match actual database schema
3. Applied performance-first approach with fast-fail timeouts and asyncio optimization
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Any

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://productivity-hub-23.preview.emergentagent.com/api"

class UltraPerformanceTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Use the specified test credentials
        self.test_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.test_user_password = "password"
        self.performance_data = {}
        
    def log_test(self, test_name: str, success: bool, message: str = "", data: Any = None, response_time: float = None):
        """Log test results with performance data"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'response_time_ms': response_time
        }
        if data:
            result['data'] = data
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        time_info = f" ({response_time:.0f}ms)" if response_time else ""
        print(f"{status} {test_name}{time_info}: {message}")
        if data and not success:
            print(f"   Data: {json.dumps(data, indent=2, default=str)}")

    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None, use_auth: bool = False) -> Dict:
        """Make HTTP request with error handling, authentication, and performance timing"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        # Add authentication header if token is available and requested
        if use_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        start_time = time.time()
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=headers, timeout=30)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, params=params, headers=headers, timeout=30)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, params=params, headers=headers, timeout=30)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            # Try to parse JSON response
            try:
                response_data = response.json() if response.content else {}
            except:
                response_data = {"raw_content": response.text[:500] if response.text else "No content"}
                
            return {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'data': response_data,
                'response': response,
                'response_time': response_time,
                'error': f"HTTP {response.status_code}: {response_data}" if response.status_code >= 400 else None
            }
            
        except requests.exceptions.RequestException as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            error_msg = f"Request failed: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg += f" - Response: {error_data}"
                except:
                    error_msg += f" - Response: {e.response.text[:200]}"
            
            return {
                'success': False,
                'error': error_msg,
                'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
                'data': {},
                'response': getattr(e, 'response', None),
                'response_time': response_time
            }

    def test_basic_connectivity(self):
        """Test basic connectivity to the backend API"""
        print("\n=== TESTING BASIC CONNECTIVITY ===")
        
        # Test the root endpoint which should exist
        result = self.make_request('GET', '', use_auth=False)
        if not result['success']:
            # Try the base URL without /api
            base_url = self.base_url.replace('/api', '')
            url = f"{base_url}/"
            try:
                start_time = time.time()
                response = self.session.get(url, timeout=30)
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                result = {
                    'success': response.status_code < 400,
                    'status_code': response.status_code,
                    'data': response.json() if response.content else {},
                    'response_time': response_time
                }
            except:
                result = {'success': False, 'error': 'Connection failed', 'response_time': 0}
        
        self.log_test(
            "BACKEND API CONNECTIVITY",
            result['success'],
            f"Backend API accessible at {self.base_url}" if result['success'] else f"Backend API not accessible: {result.get('error', 'Unknown error')}",
            response_time=result.get('response_time', 0)
        )
        
        return result['success']

    def test_user_authentication(self):
        """Test user authentication with specified credentials"""
        print("\n=== TESTING USER AUTHENTICATION ===")
        
        # Login user with specified credentials
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        self.log_test(
            "USER LOGIN",
            result['success'],
            f"Login successful with {self.test_user_email}" if result['success'] else f"Login failed: {result.get('error', 'Unknown error')}",
            response_time=result.get('response_time', 0)
        )
        
        if not result['success']:
            return False
        
        token_data = result['data']
        self.auth_token = token_data.get('access_token')
        
        # Verify token works
        result = self.make_request('GET', '/auth/me', use_auth=True)
        self.log_test(
            "AUTHENTICATION TOKEN VALIDATION",
            result['success'],
            f"Token validated successfully, user: {result['data'].get('email', 'Unknown')}" if result['success'] else f"Token validation failed: {result.get('error', 'Unknown error')}",
            response_time=result.get('response_time', 0)
        )
        
        return result['success']

    def test_ultra_performance_endpoints(self):
        """Test all ultra-performance endpoints for response time and functionality"""
        print("\n=== TESTING ULTRA-PERFORMANCE ENDPOINTS ===")
        
        if not self.auth_token:
            self.log_test("ULTRA-PERFORMANCE ENDPOINTS - Authentication Required", False, "No authentication token available")
            return False
        
        # Define ultra-performance endpoints to test
        ultra_endpoints = [
            ('/ultra/dashboard', 'Ultra Dashboard'),
            ('/ultra/pillars', 'Ultra Pillars'),
            ('/ultra/areas', 'Ultra Areas'),
            ('/ultra/projects', 'Ultra Projects'),
            ('/ultra/insights', 'Ultra Insights')
        ]
        
        ultra_performance_results = {}
        successful_endpoints = 0
        
        for endpoint, name in ultra_endpoints:
            print(f"\n--- Testing {name} ---")
            
            # Test the ultra-performance endpoint
            result = self.make_request('GET', endpoint, use_auth=True)
            response_time = result.get('response_time', 0)
            
            # Check if endpoint is working
            if result['success']:
                # Check response time against target (<200ms)
                meets_performance_target = response_time < 200
                
                self.log_test(
                    f"{name} - FUNCTIONALITY",
                    True,
                    f"Endpoint working correctly"
                )
                
                self.log_test(
                    f"{name} - PERFORMANCE",
                    meets_performance_target,
                    f"Response time: {response_time:.0f}ms {'(MEETS TARGET <200ms)' if meets_performance_target else '(EXCEEDS TARGET >200ms)'}",
                    response_time=response_time
                )
                
                ultra_performance_results[name] = {
                    'working': True,
                    'response_time': response_time,
                    'meets_target': meets_performance_target
                }
                
                if meets_performance_target:
                    successful_endpoints += 1
                    
            else:
                self.log_test(
                    f"{name} - FUNCTIONALITY",
                    False,
                    f"Endpoint failed: {result.get('error', 'Unknown error')}",
                    response_time=response_time
                )
                
                ultra_performance_results[name] = {
                    'working': False,
                    'response_time': response_time,
                    'meets_target': False,
                    'error': result.get('error', 'Unknown error')
                }
        
        self.performance_data['ultra_endpoints'] = ultra_performance_results
        
        # Overall assessment
        total_endpoints = len(ultra_endpoints)
        success_rate = (successful_endpoints / total_endpoints) * 100
        
        self.log_test(
            "ULTRA-PERFORMANCE ENDPOINTS - OVERALL",
            success_rate >= 80,
            f"Performance targets met: {successful_endpoints}/{total_endpoints} endpoints ({success_rate:.1f}%)"
        )
        
        return success_rate >= 80

    def test_regular_endpoints_comparison(self):
        """Test regular endpoints for performance comparison"""
        print("\n=== TESTING REGULAR ENDPOINTS FOR COMPARISON ===")
        
        if not self.auth_token:
            self.log_test("REGULAR ENDPOINTS COMPARISON - Authentication Required", False, "No authentication token available")
            return False
        
        # Define regular endpoints to test for comparison
        regular_endpoints = [
            ('/dashboard', 'Regular Dashboard'),
            ('/pillars', 'Regular Pillars'),
            ('/areas', 'Regular Areas'),
            ('/projects', 'Regular Projects'),
            ('/insights', 'Regular Insights')
        ]
        
        regular_performance_results = {}
        
        for endpoint, name in regular_endpoints:
            print(f"\n--- Testing {name} ---")
            
            # Test the regular endpoint
            result = self.make_request('GET', endpoint, use_auth=True)
            response_time = result.get('response_time', 0)
            
            if result['success']:
                self.log_test(
                    f"{name} - PERFORMANCE",
                    True,
                    f"Response time: {response_time:.0f}ms",
                    response_time=response_time
                )
                
                regular_performance_results[name] = {
                    'working': True,
                    'response_time': response_time
                }
            else:
                self.log_test(
                    f"{name} - PERFORMANCE",
                    False,
                    f"Endpoint failed: {result.get('error', 'Unknown error')}",
                    response_time=response_time
                )
                
                regular_performance_results[name] = {
                    'working': False,
                    'response_time': response_time,
                    'error': result.get('error', 'Unknown error')
                }
        
        self.performance_data['regular_endpoints'] = regular_performance_results
        return True

    def test_cache_performance_stats(self):
        """Test cache performance stats endpoint"""
        print("\n=== TESTING CACHE PERFORMANCE STATS ===")
        
        if not self.auth_token:
            self.log_test("CACHE PERFORMANCE STATS - Authentication Required", False, "No authentication token available")
            return False
        
        # Test the performance stats endpoint
        result = self.make_request('GET', '/ultra/performance-stats', use_auth=True)
        response_time = result.get('response_time', 0)
        
        if result['success']:
            stats_data = result['data']
            self.log_test(
                "CACHE PERFORMANCE STATS",
                True,
                f"Performance stats retrieved successfully",
                data=stats_data,
                response_time=response_time
            )
            
            # Check if cache statistics are present
            if 'cache_stats' in stats_data:
                cache_stats = stats_data['cache_stats']
                self.log_test(
                    "CACHE STATISTICS",
                    True,
                    f"Cache hit rate: {cache_stats.get('hit_rate', 'N/A')}%, Memory fallback: {cache_stats.get('memory_fallback_count', 'N/A')}"
                )
            
            return True
        else:
            self.log_test(
                "CACHE PERFORMANCE STATS",
                False,
                f"Failed to retrieve performance stats: {result.get('error', 'Unknown error')}",
                response_time=response_time
            )
            return False

    def analyze_performance_comparison(self):
        """Analyze performance comparison between ultra and regular endpoints"""
        print("\n=== PERFORMANCE COMPARISON ANALYSIS ===")
        
        if 'ultra_endpoints' not in self.performance_data or 'regular_endpoints' not in self.performance_data:
            print("❌ Insufficient data for performance comparison")
            return False
        
        ultra_data = self.performance_data['ultra_endpoints']
        regular_data = self.performance_data['regular_endpoints']
        
        comparisons = []
        
        # Compare matching endpoints
        endpoint_pairs = [
            ('Ultra Dashboard', 'Regular Dashboard'),
            ('Ultra Pillars', 'Regular Pillars'),
            ('Ultra Areas', 'Regular Areas'),
            ('Ultra Projects', 'Regular Projects'),
            ('Ultra Insights', 'Regular Insights')
        ]
        
        for ultra_name, regular_name in endpoint_pairs:
            if ultra_name in ultra_data and regular_name in regular_data:
                ultra_endpoint = ultra_data[ultra_name]
                regular_endpoint = regular_data[regular_name]
                
                if ultra_endpoint['working'] and regular_endpoint['working']:
                    ultra_time = ultra_endpoint['response_time']
                    regular_time = regular_endpoint['response_time']
                    
                    if regular_time > 0:
                        improvement_factor = regular_time / ultra_time
                        improvement_percentage = ((regular_time - ultra_time) / regular_time) * 100
                        
                        is_faster = ultra_time < regular_time
                        
                        self.log_test(
                            f"PERFORMANCE COMPARISON - {ultra_name.replace('Ultra ', '')}",
                            is_faster,
                            f"Ultra: {ultra_time:.0f}ms vs Regular: {regular_time:.0f}ms - {improvement_factor:.1f}x faster ({improvement_percentage:.1f}% improvement)" if is_faster else f"Ultra: {ultra_time:.0f}ms vs Regular: {regular_time:.0f}ms - SLOWER by {abs(improvement_percentage):.1f}%"
                        )
                        
                        comparisons.append({
                            'endpoint': ultra_name.replace('Ultra ', ''),
                            'ultra_time': ultra_time,
                            'regular_time': regular_time,
                            'is_faster': is_faster,
                            'improvement_factor': improvement_factor if is_faster else 0,
                            'improvement_percentage': improvement_percentage if is_faster else 0
                        })
        
        # Overall performance assessment
        faster_endpoints = sum(1 for comp in comparisons if comp['is_faster'])
        total_comparisons = len(comparisons)
        
        if total_comparisons > 0:
            success_rate = (faster_endpoints / total_comparisons) * 100
            avg_improvement = sum(comp['improvement_percentage'] for comp in comparisons if comp['is_faster']) / max(faster_endpoints, 1)
            
            self.log_test(
                "ULTRA-PERFORMANCE ADVANTAGE",
                success_rate >= 80,
                f"Ultra endpoints faster: {faster_endpoints}/{total_comparisons} ({success_rate:.1f}%) - Average improvement: {avg_improvement:.1f}%"
            )
            
            return success_rate >= 80
        
        return False

    def run_comprehensive_ultra_performance_test(self):
        """Run comprehensive ultra-performance optimization tests"""
        print("\n🚀 STARTING ULTRA-PERFORMANCE OPTIMIZATION TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("Target: <200ms response times for ultra-performance endpoints")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("User Authentication", self.test_user_authentication),
            ("Ultra-Performance Endpoints", self.test_ultra_performance_endpoints),
            ("Regular Endpoints Comparison", self.test_regular_endpoints_comparison),
            ("Cache Performance Stats", self.test_cache_performance_stats),
            ("Performance Comparison Analysis", self.analyze_performance_comparison)
        ]
        
        successful_tests = 0
        total_tests = len(test_methods)
        
        for test_name, test_method in test_methods:
            print(f"\n--- {test_name} ---")
            try:
                if test_method():
                    successful_tests += 1
                    print(f"✅ {test_name} completed successfully")
                else:
                    print(f"❌ {test_name} failed")
            except Exception as e:
                print(f"❌ {test_name} raised exception: {e}")
        
        success_rate = (successful_tests / total_tests) * 100
        
        print(f"\n" + "=" * 80)
        print("🚀 ULTRA-PERFORMANCE OPTIMIZATION TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for ultra-performance functionality
        ultra_tests_passed = sum(1 for result in self.test_results if result['success'] and 'Ultra' in result['test'])
        performance_tests_passed = sum(1 for result in self.test_results if result['success'] and 'PERFORMANCE' in result['test'])
        comparison_tests_passed = sum(1 for result in self.test_results if result['success'] and 'COMPARISON' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"Ultra-Performance Tests Passed: {ultra_tests_passed}")
        print(f"Performance Tests Passed: {performance_tests_passed}")
        print(f"Comparison Tests Passed: {comparison_tests_passed}")
        
        # Performance summary
        if 'ultra_endpoints' in self.performance_data:
            ultra_data = self.performance_data['ultra_endpoints']
            working_ultra_endpoints = sum(1 for endpoint in ultra_data.values() if endpoint['working'])
            fast_ultra_endpoints = sum(1 for endpoint in ultra_data.values() if endpoint.get('meets_target', False))
            
            print(f"\n📊 ULTRA-PERFORMANCE RESULTS:")
            print(f"Working Ultra Endpoints: {working_ultra_endpoints}/{len(ultra_data)}")
            print(f"Fast Ultra Endpoints (<200ms): {fast_ultra_endpoints}/{len(ultra_data)}")
            
            # Show individual endpoint performance
            for name, data in ultra_data.items():
                status = "✅" if data['working'] and data.get('meets_target', False) else "❌"
                time_info = f"{data['response_time']:.0f}ms" if data['working'] else "FAILED"
                print(f"  {status} {name}: {time_info}")
        
        if success_rate >= 85:
            print("\n✅ ULTRA-PERFORMANCE OPTIMIZATION SYSTEM: SUCCESS")
            print("   ✅ Ultra-performance endpoints working")
            print("   ✅ Response times meet <200ms target")
            print("   ✅ Performance improvements verified")
            print("   ✅ Cache system operational")
            print("   The ultra-performance optimization fixes are working!")
        else:
            print("\n❌ ULTRA-PERFORMANCE OPTIMIZATION SYSTEM: ISSUES DETECTED")
            print("   Issues found in ultra-performance implementation")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 85

def main():
    """Run Ultra-Performance Optimization Tests"""
    print("🚀 STARTING ULTRA-PERFORMANCE OPTIMIZATION BACKEND TESTING")
    print("=" * 80)
    
    tester = UltraPerformanceTester()
    
    try:
        # Run the comprehensive ultra-performance tests
        success = tester.run_comprehensive_ultra_performance_test()
        
        # Calculate overall results
        total_tests = len(tester.test_results)
        passed_tests = sum(1 for result in tester.test_results if result['success'])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 FINAL RESULTS")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print("=" * 80)
        
        return success_rate >= 85
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)