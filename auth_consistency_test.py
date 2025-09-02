#!/usr/bin/env python3
"""
Authentication Consistency Backend Test
Testing Focus: Intermittent API authentication issues

This test verifies:
1. Authentication consistency across different endpoints
2. Token expiration scenarios and refresh mechanisms
3. Authentication headers validation
4. Race conditions and concurrent requests
5. Different HTTP methods authentication
6. Patterns in authentication failures

Based on review request for testing intermittent 403 "Not authenticated" errors
"""

import requests
import sys
import json
import time
import threading
import concurrent.futures
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import random

class AuthConsistencyTester:
    def __init__(self, base_url="https://smart-life-os.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.auth_failures = []
        
        # Test credentials from review request
        self.test_email = "test@aurumlife.com"
        self.test_password = "password123"
        
        # Endpoints to test for authentication consistency
        self.core_endpoints = [
            ('GET', 'tasks', {}),
            ('GET', 'projects', {}),
            ('GET', 'areas', {}),
            ('GET', 'pillars', {}),
            ('GET', 'insights', {}),
            ('GET', 'journal', {}),
        ]
        
        # HRM and AI endpoints
        self.hrm_endpoints = [
            ('GET', 'ai/task-why-statements', {}),
            ('GET', 'ai/suggest-focus', {'top_n': 3}),
            ('GET', 'ai/quota', {}),
            ('GET', 'alignment/dashboard', {}),
        ]
        
        # Semantic search endpoints
        self.semantic_endpoints = [
            ('GET', 'semantic/search', {'query': 'test', 'limit': 5}),
        ]
        
        # All endpoints combined
        self.all_endpoints = self.core_endpoints + self.hrm_endpoints + self.semantic_endpoints

    def log_test(self, name: str, success: bool, details: Dict = None, response_time: float = None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            
        result = {
            'test_name': name,
            'success': success,
            'details': details or {},
            'response_time': response_time,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        time_info = f" ({response_time:.2f}s)" if response_time else ""
        print(f"{status} {name}{time_info}")
        
        if details and not success:
            print(f"   Details: {details}")

    def log_auth_failure(self, endpoint: str, method: str, status_code: int, error: str, token_used: str = None):
        """Log authentication failure for pattern analysis"""
        failure = {
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'error': error,
            'token_used': token_used[:20] + "..." if token_used else None,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.auth_failures.append(failure)

    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None, 
                    headers: Dict = None, timeout: int = 30) -> Tuple[bool, Dict, float]:
        """Make HTTP request and return (success, response_data, response_time)"""
        url = f"{self.base_url}/api/{endpoint.lstrip('/')}"
        request_headers = {'Content-Type': 'application/json'}
        
        if headers:
            request_headers.update(headers)
        elif self.token:
            request_headers['Authorization'] = f'Bearer {self.token}'

        start_time = time.time()
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=request_headers, params=params, timeout=timeout)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=request_headers, params=params, timeout=timeout)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=request_headers, params=params, timeout=timeout)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=request_headers, params=params, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response_time = time.time() - start_time
            
            # Log authentication failures
            if response.status_code in [401, 403]:
                self.log_auth_failure(endpoint, method, response.status_code, response.text, self.token)
            
            if response.status_code < 400:
                try:
                    response_data = response.json()
                    # Handle case where response is a list
                    if isinstance(response_data, list):
                        return True, {'data': response_data, 'count': len(response_data)}, response_time
                    return True, response_data, response_time
                except:
                    return True, {'raw_response': response.text}, response_time
            else:
                return False, {
                    'status_code': response.status_code,
                    'error': response.text
                }, response_time
                
        except Exception as e:
            response_time = time.time() - start_time
            return False, {'error': str(e)}, response_time

    def test_authentication(self) -> bool:
        """Test login and get authentication token"""
        print("\n🔐 Testing Authentication...")
        
        success, response, response_time = self.make_request(
            'POST', 
            'auth/login',
            data={
                'email': self.test_email,
                'password': self.test_password
            },
            headers={'Content-Type': 'application/json'}  # No auth header for login
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            
            # Get user info
            me_success, me_response, _ = self.make_request('GET', 'auth/me')
            if me_success:
                self.user_id = me_response.get('id')
                user_data = me_response
            else:
                user_data = response.get('user', {})
            
            details = {
                'user_id': self.user_id,
                'token_length': len(self.token) if self.token else 0,
                'token_prefix': self.token[:20] + "..." if self.token else None,
                'user_email': user_data.get('email'),
                'response_structure': list(response.keys())
            }
            
            self.log_test("Authentication", True, details, response_time)
            return True
        else:
            self.log_test("Authentication", False, response, response_time)
            return False

    def test_endpoint_consistency(self) -> bool:
        """Test authentication consistency across all endpoints"""
        print("\n🔄 Testing Endpoint Authentication Consistency...")
        
        if not self.token:
            self.log_test("Endpoint Consistency", False, {'error': 'No authentication token available'})
            return False
        
        endpoint_results = []
        total_time = 0
        auth_failures = 0
        
        for method, endpoint, params in self.all_endpoints:
            print(f"   Testing {method} /api/{endpoint}...")
            
            success, response, response_time = self.make_request(method, endpoint, params=params)
            total_time += response_time
            
            endpoint_result = {
                'method': method,
                'endpoint': endpoint,
                'success': success,
                'status_code': response.get('status_code') if not success else 200,
                'response_time': response_time,
                'auth_failure': response.get('status_code') in [401, 403] if not success else False
            }
            
            if endpoint_result['auth_failure']:
                auth_failures += 1
                print(f"      ❌ AUTH FAILURE: {response.get('status_code')} - {response.get('error', '')[:100]}")
            elif not success:
                print(f"      ⚠️ OTHER ERROR: {response.get('status_code')} - {response.get('error', '')[:100]}")
            else:
                print(f"      ✅ SUCCESS: {response_time:.2f}s")
            
            endpoint_results.append(endpoint_result)
            
            # Small delay between requests to avoid overwhelming the server
            time.sleep(0.1)
        
        success_rate = (len(endpoint_results) - auth_failures) / len(endpoint_results) * 100
        
        details = {
            'total_endpoints': len(endpoint_results),
            'auth_failures': auth_failures,
            'success_rate': success_rate,
            'average_response_time': total_time / len(endpoint_results),
            'endpoint_results': endpoint_results
        }
        
        # Test passes if less than 10% auth failures (allowing for some intermittent issues)
        test_passed = auth_failures < len(endpoint_results) * 0.1
        
        self.log_test("Endpoint Consistency", test_passed, details, total_time)
        return test_passed

    def test_rapid_requests(self) -> bool:
        """Test multiple rapid API calls to detect race conditions"""
        print("\n⚡ Testing Rapid Requests (Race Conditions)...")
        
        if not self.token:
            self.log_test("Rapid Requests", False, {'error': 'No authentication token available'})
            return False
        
        # Test with tasks endpoint (most commonly used)
        endpoint = 'tasks'
        num_requests = 10
        
        results = []
        auth_failures = 0
        
        print(f"   Making {num_requests} rapid requests to /api/{endpoint}...")
        
        start_time = time.time()
        
        # Make rapid sequential requests
        for i in range(num_requests):
            success, response, response_time = self.make_request('GET', endpoint)
            
            result = {
                'request_num': i + 1,
                'success': success,
                'response_time': response_time,
                'auth_failure': response.get('status_code') in [401, 403] if not success else False
            }
            
            if result['auth_failure']:
                auth_failures += 1
                print(f"      Request {i+1}: ❌ AUTH FAILURE")
            elif not success:
                print(f"      Request {i+1}: ⚠️ ERROR")
            else:
                print(f"      Request {i+1}: ✅ SUCCESS ({response_time:.3f}s)")
            
            results.append(result)
            
            # Very small delay to simulate rapid requests
            time.sleep(0.05)
        
        total_time = time.time() - start_time
        
        details = {
            'total_requests': num_requests,
            'auth_failures': auth_failures,
            'success_rate': (num_requests - auth_failures) / num_requests * 100,
            'total_time': total_time,
            'average_response_time': sum(r['response_time'] for r in results) / num_requests,
            'results': results
        }
        
        # Test passes if no auth failures in rapid requests
        test_passed = auth_failures == 0
        
        self.log_test("Rapid Requests", test_passed, details, total_time)
        return test_passed

    def test_concurrent_requests(self) -> bool:
        """Test concurrent requests from same user"""
        print("\n🔀 Testing Concurrent Requests...")
        
        if not self.token:
            self.log_test("Concurrent Requests", False, {'error': 'No authentication token available'})
            return False
        
        def make_concurrent_request(endpoint_info):
            method, endpoint, params = endpoint_info
            return self.make_request(method, endpoint, params=params)
        
        # Select a subset of endpoints for concurrent testing
        test_endpoints = self.core_endpoints[:4]  # Test first 4 core endpoints
        
        print(f"   Making {len(test_endpoints)} concurrent requests...")
        
        start_time = time.time()
        
        # Use ThreadPoolExecutor for concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(test_endpoints)) as executor:
            future_to_endpoint = {
                executor.submit(make_concurrent_request, endpoint_info): endpoint_info 
                for endpoint_info in test_endpoints
            }
            
            results = []
            auth_failures = 0
            
            for future in concurrent.futures.as_completed(future_to_endpoint):
                endpoint_info = future_to_endpoint[future]
                method, endpoint, params = endpoint_info
                
                try:
                    success, response, response_time = future.result()
                    
                    result = {
                        'method': method,
                        'endpoint': endpoint,
                        'success': success,
                        'response_time': response_time,
                        'auth_failure': response.get('status_code') in [401, 403] if not success else False
                    }
                    
                    if result['auth_failure']:
                        auth_failures += 1
                        print(f"      {method} {endpoint}: ❌ AUTH FAILURE")
                    elif not success:
                        print(f"      {method} {endpoint}: ⚠️ ERROR")
                    else:
                        print(f"      {method} {endpoint}: ✅ SUCCESS ({response_time:.3f}s)")
                    
                    results.append(result)
                    
                except Exception as e:
                    print(f"      {method} {endpoint}: ❌ EXCEPTION: {e}")
                    results.append({
                        'method': method,
                        'endpoint': endpoint,
                        'success': False,
                        'auth_failure': False,
                        'exception': str(e)
                    })
        
        total_time = time.time() - start_time
        
        details = {
            'total_requests': len(test_endpoints),
            'auth_failures': auth_failures,
            'success_rate': (len(results) - auth_failures) / len(results) * 100 if results else 0,
            'total_time': total_time,
            'results': results
        }
        
        # Test passes if no auth failures in concurrent requests
        test_passed = auth_failures == 0
        
        self.log_test("Concurrent Requests", test_passed, details, total_time)
        return test_passed

    def test_different_http_methods(self) -> bool:
        """Test authentication across different HTTP methods"""
        print("\n🔧 Testing Different HTTP Methods...")
        
        if not self.token:
            self.log_test("HTTP Methods", False, {'error': 'No authentication token available'})
            return False
        
        # Test different HTTP methods on safe endpoints
        method_tests = [
            ('GET', 'tasks', {}),
            ('GET', 'projects', {}),
            ('GET', 'areas', {}),
            ('GET', 'pillars', {}),
            ('GET', 'insights', {}),
            # Note: We avoid POST/PUT/DELETE to prevent data modification during testing
        ]
        
        results = []
        auth_failures = 0
        total_time = 0
        
        for method, endpoint, params in method_tests:
            print(f"   Testing {method} /api/{endpoint}...")
            
            success, response, response_time = self.make_request(method, endpoint, params=params)
            total_time += response_time
            
            result = {
                'method': method,
                'endpoint': endpoint,
                'success': success,
                'response_time': response_time,
                'auth_failure': response.get('status_code') in [401, 403] if not success else False
            }
            
            if result['auth_failure']:
                auth_failures += 1
                print(f"      ❌ AUTH FAILURE: {response.get('status_code')}")
            elif not success:
                print(f"      ⚠️ OTHER ERROR: {response.get('status_code')}")
            else:
                print(f"      ✅ SUCCESS ({response_time:.3f}s)")
            
            results.append(result)
            time.sleep(0.1)
        
        details = {
            'total_methods_tested': len(method_tests),
            'auth_failures': auth_failures,
            'success_rate': (len(results) - auth_failures) / len(results) * 100 if results else 0,
            'average_response_time': total_time / len(results) if results else 0,
            'results': results
        }
        
        test_passed = auth_failures == 0
        
        self.log_test("HTTP Methods", test_passed, details, total_time)
        return test_passed

    def test_malformed_headers(self) -> bool:
        """Test authentication with malformed headers"""
        print("\n🔒 Testing Malformed Authentication Headers...")
        
        # Test various malformed headers - these should all fail with 401/403
        malformed_tests = [
            ('Missing Authorization Header', {}),
            ('Empty Authorization Header', {'Authorization': ''}),
            ('Invalid Bearer Format', {'Authorization': 'InvalidFormat token123'}),
            ('Bearer without token', {'Authorization': 'Bearer'}),
            ('Bearer with invalid token', {'Authorization': 'Bearer invalid-token-123'}),
            ('Malformed Bearer', {'Authorization': 'Bearer invalid token with spaces'}),
        ]
        
        results = []
        total_time = 0
        
        for test_name, headers in malformed_tests:
            print(f"   Testing: {test_name}...")
            
            success, response, response_time = self.make_request(
                'GET', 'tasks', headers=headers
            )
            total_time += response_time
            
            # These should all fail with 401/403
            expected_failure = response.get('status_code') in [401, 403] if not success else False
            test_passed = not success and expected_failure
            
            result = {
                'test_name': test_name,
                'success': success,
                'expected_failure': expected_failure,
                'test_passed': test_passed,
                'status_code': response.get('status_code') if not success else 200,
                'response_time': response_time
            }
            
            if test_passed:
                print(f"      ✅ CORRECTLY FAILED: {response.get('status_code')}")
            else:
                print(f"      ❌ UNEXPECTED RESULT: {response.get('status_code')}")
            
            results.append(result)
            time.sleep(0.1)
        
        # All malformed header tests should fail appropriately
        all_passed = all(r['test_passed'] for r in results)
        
        details = {
            'total_tests': len(malformed_tests),
            'correctly_failed': sum(1 for r in results if r['test_passed']),
            'all_passed': all_passed,
            'results': results
        }
        
        self.log_test("Malformed Headers", all_passed, details, total_time)
        return all_passed

    def test_token_persistence(self) -> bool:
        """Test token persistence across multiple requests over time"""
        print("\n⏰ Testing Token Persistence...")
        
        if not self.token:
            self.log_test("Token Persistence", False, {'error': 'No authentication token available'})
            return False
        
        # Test token over multiple requests with delays
        persistence_tests = []
        auth_failures = 0
        total_time = 0
        
        for i in range(5):
            print(f"   Persistence test {i+1}/5...")
            
            success, response, response_time = self.make_request('GET', 'tasks')
            total_time += response_time
            
            test_result = {
                'test_number': i + 1,
                'success': success,
                'response_time': response_time,
                'auth_failure': response.get('status_code') in [401, 403] if not success else False,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if test_result['auth_failure']:
                auth_failures += 1
                print(f"      ❌ AUTH FAILURE: {response.get('status_code')}")
            elif not success:
                print(f"      ⚠️ OTHER ERROR: {response.get('status_code')}")
            else:
                print(f"      ✅ SUCCESS ({response_time:.3f}s)")
            
            persistence_tests.append(test_result)
            
            # Wait between tests to check persistence
            if i < 4:  # Don't wait after the last test
                time.sleep(2)
        
        details = {
            'total_tests': len(persistence_tests),
            'auth_failures': auth_failures,
            'success_rate': (len(persistence_tests) - auth_failures) / len(persistence_tests) * 100,
            'average_response_time': total_time / len(persistence_tests),
            'tests': persistence_tests
        }
        
        test_passed = auth_failures == 0
        
        self.log_test("Token Persistence", test_passed, details, total_time)
        return test_passed

    def analyze_failure_patterns(self):
        """Analyze patterns in authentication failures"""
        print("\n🔍 Analyzing Authentication Failure Patterns...")
        
        if not self.auth_failures:
            print("   ✅ No authentication failures detected!")
            return
        
        print(f"   Found {len(self.auth_failures)} authentication failures:")
        
        # Group by endpoint
        endpoint_failures = {}
        for failure in self.auth_failures:
            endpoint = failure['endpoint']
            if endpoint not in endpoint_failures:
                endpoint_failures[endpoint] = []
            endpoint_failures[endpoint].append(failure)
        
        print(f"\n   📊 Failures by endpoint:")
        for endpoint, failures in endpoint_failures.items():
            print(f"      {endpoint}: {len(failures)} failures")
        
        # Group by status code
        status_code_failures = {}
        for failure in self.auth_failures:
            status_code = failure['status_code']
            if status_code not in status_code_failures:
                status_code_failures[status_code] = []
            status_code_failures[status_code].append(failure)
        
        print(f"\n   📊 Failures by status code:")
        for status_code, failures in status_code_failures.items():
            print(f"      {status_code}: {len(failures)} failures")
        
        # Group by method
        method_failures = {}
        for failure in self.auth_failures:
            method = failure['method']
            if method not in method_failures:
                method_failures[method] = []
            method_failures[method].append(failure)
        
        print(f"\n   📊 Failures by HTTP method:")
        for method, failures in method_failures.items():
            print(f"      {method}: {len(failures)} failures")
        
        # Show recent failures
        print(f"\n   🕒 Recent failures (last 5):")
        recent_failures = sorted(self.auth_failures, key=lambda x: x['timestamp'])[-5:]
        for failure in recent_failures:
            print(f"      {failure['timestamp']}: {failure['method']} {failure['endpoint']} -> {failure['status_code']}")

    def run_comprehensive_test(self):
        """Run all authentication consistency tests"""
        print("🚀 Starting Authentication Consistency Backend Test")
        print("=" * 70)
        print("Focus: Intermittent API authentication issues")
        print("=" * 70)
        
        # Authentication is required for all other tests
        if not self.test_authentication():
            print("\n❌ Authentication failed. Cannot proceed with other tests.")
            return False
        
        # Run all authentication tests
        test_methods = [
            self.test_endpoint_consistency,
            self.test_rapid_requests,
            self.test_concurrent_requests,
            self.test_different_http_methods,
            self.test_malformed_headers,
            self.test_token_persistence,
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"❌ Test {test_method.__name__} failed with exception: {e}")
                self.log_test(test_method.__name__, False, {'exception': str(e)})
        
        # Analyze failure patterns
        self.analyze_failure_patterns()
        
        # Print summary
        self.print_summary()
        
        return self.tests_passed == self.tests_run

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📊 AUTHENTICATION CONSISTENCY TEST SUMMARY")
        print("=" * 70)
        
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        # Print failed tests
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  • {test['test_name']}")
                if test['details']:
                    key_details = {k: v for k, v in test['details'].items() 
                                 if k in ['auth_failures', 'success_rate', 'error']}
                    if key_details:
                        print(f"    {key_details}")
        
        # Print key findings
        print(f"\n🔍 KEY FINDINGS:")
        
        # Authentication failures summary
        total_auth_failures = len(self.auth_failures)
        print(f"  • Total Authentication Failures: {total_auth_failures}")
        
        if total_auth_failures > 0:
            print(f"  • Authentication Issues: ❌ DETECTED")
            
            # Most problematic endpoints
            endpoint_failures = {}
            for failure in self.auth_failures:
                endpoint = failure['endpoint']
                endpoint_failures[endpoint] = endpoint_failures.get(endpoint, 0) + 1
            
            if endpoint_failures:
                most_problematic = max(endpoint_failures.items(), key=lambda x: x[1])
                print(f"  • Most Problematic Endpoint: {most_problematic[0]} ({most_problematic[1]} failures)")
        else:
            print(f"  • Authentication Issues: ✅ NONE DETECTED")
        
        # Test-specific findings
        consistency_test = next((r for r in self.test_results if r['test_name'] == 'Endpoint Consistency'), None)
        if consistency_test:
            success_rate = consistency_test['details'].get('success_rate', 0)
            print(f"  • Endpoint Consistency: {success_rate:.1f}% success rate")
        
        rapid_test = next((r for r in self.test_results if r['test_name'] == 'Rapid Requests'), None)
        if rapid_test:
            rapid_success = rapid_test['success']
            print(f"  • Race Conditions: {'✅ No issues' if rapid_success else '❌ Issues detected'}")
        
        concurrent_test = next((r for r in self.test_results if r['test_name'] == 'Concurrent Requests'), None)
        if concurrent_test:
            concurrent_success = concurrent_test['success']
            print(f"  • Concurrent Requests: {'✅ Working' if concurrent_success else '❌ Issues detected'}")
        
        persistence_test = next((r for r in self.test_results if r['test_name'] == 'Token Persistence'), None)
        if persistence_test:
            persistence_success = persistence_test['success']
            print(f"  • Token Persistence: {'✅ Stable' if persistence_success else '❌ Issues detected'}")
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        if total_auth_failures == 0 and self.tests_passed == self.tests_run:
            print("  ✅ NO INTERMITTENT AUTHENTICATION ISSUES DETECTED")
            print("  ✅ All authentication mechanisms working consistently")
        elif total_auth_failures > 0:
            print("  ❌ INTERMITTENT AUTHENTICATION ISSUES CONFIRMED")
            print("  🔧 Review the failure patterns above for specific endpoints/scenarios")
        else:
            print("  ⚠️ SOME AUTHENTICATION TESTS FAILED")
            print("  🔧 Review failed tests for specific issues")

def main():
    """Main test execution"""
    tester = AuthConsistencyTester()
    
    try:
        success = tester.run_comprehensive_test()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n❌ Test execution failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())