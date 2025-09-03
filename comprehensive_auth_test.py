#!/usr/bin/env python3
"""
Comprehensive Authentication Issues Test
Testing Focus: Intermittent API authentication issues as described in review request

This test specifically addresses:
1. Authentication consistency across different endpoints
2. Token expiration scenarios
3. Authentication headers validation
4. Race conditions and concurrent requests
5. Different HTTP methods authentication
6. Patterns in authentication failures

Authentication Flow:
1. Login with test@aurumlife.com/password123
2. Get JWT token
3. Make multiple API calls with same token
4. Check for any 403 "Not authenticated" responses
5. Identify which endpoints have issues
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

class ComprehensiveAuthTester:
    def __init__(self, base_url="https://journal-analytics-1.preview.emergentagent.com"):
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
        
        # Endpoints from review request
        self.core_endpoints = [
            ('GET', 'tasks', {}),
            ('GET', 'projects', {}),
            ('GET', 'areas', {}),
            ('GET', 'pillars', {}),
        ]
        
        # HRM endpoints from review request
        self.hrm_endpoints = [
            ('GET', 'hrm/analyze', {}),
            ('GET', 'hrm/insights', {}),
        ]
        
        # Semantic search from review request
        self.semantic_endpoints = [
            ('GET', 'semantic/search', {'query': 'test task', 'limit': 5}),
        ]
        
        # Additional endpoints that might have auth issues
        self.additional_endpoints = [
            ('GET', 'insights', {}),
            ('GET', 'journal', {}),
            ('GET', 'ai/task-why-statements', {}),
            ('GET', 'ai/suggest-focus', {'top_n': 3}),
            ('GET', 'alignment/dashboard', {}),
        ]
        
        # All endpoints combined
        self.all_endpoints = (self.core_endpoints + self.hrm_endpoints + 
                            self.semantic_endpoints + self.additional_endpoints)

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

    def log_auth_failure(self, endpoint: str, method: str, status_code: int, error: str, 
                        token_used: str = None, test_context: str = None):
        """Log authentication failure for pattern analysis"""
        failure = {
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code,
            'error': error,
            'token_used': token_used[:20] + "..." if token_used else None,
            'test_context': test_context,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.auth_failures.append(failure)

    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None, 
                    headers: Dict = None, timeout: int = 30, test_context: str = None) -> Tuple[bool, Dict, float]:
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
            
            # Log authentication failures (403 "Not authenticated" as mentioned in review)
            if response.status_code in [401, 403]:
                self.log_auth_failure(endpoint, method, response.status_code, response.text, 
                                    self.token, test_context)
            
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

    def test_authentication_flow(self) -> bool:
        """Test the authentication flow as specified in review request"""
        print("\n🔐 Testing Authentication Flow (Login with test@aurumlife.com/password123)...")
        
        success, response, response_time = self.make_request(
            'POST', 
            'auth/login',
            data={
                'email': self.test_email,
                'password': self.test_password
            },
            headers={'Content-Type': 'application/json'},  # No auth header for login
            test_context="authentication_flow"
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            
            # Get user info
            me_success, me_response, _ = self.make_request('GET', 'auth/me', test_context="authentication_flow")
            if me_success:
                self.user_id = me_response.get('id')
                user_data = me_response
            else:
                user_data = response.get('user', {})
            
            details = {
                'user_id': self.user_id,
                'token_length': len(self.token) if self.token else 0,
                'token_prefix': self.token[:30] + "..." if self.token else None,
                'user_email': user_data.get('email'),
                'jwt_token_obtained': True
            }
            
            self.log_test("Authentication Flow", True, details, response_time)
            return True
        else:
            self.log_test("Authentication Flow", False, response, response_time)
            return False

    def test_multiple_api_calls_same_token(self) -> bool:
        """Test multiple API calls with the same token (as specified in review)"""
        print("\n🔄 Testing Multiple API Calls with Same Token...")
        
        if not self.token:
            self.log_test("Multiple API Calls Same Token", False, {'error': 'No authentication token available'})
            return False
        
        # Test each endpoint multiple times with the same token
        endpoint_results = []
        total_time = 0
        auth_failures = 0
        total_calls = 0
        
        for method, endpoint, params in self.all_endpoints:
            print(f"   Testing {method} /api/{endpoint} (3 calls)...")
            
            endpoint_auth_failures = 0
            endpoint_calls = 0
            
            # Make 3 calls to each endpoint
            for call_num in range(1, 4):
                success, response, response_time = self.make_request(
                    method, endpoint, params=params, 
                    test_context=f"multiple_calls_same_token_call_{call_num}"
                )
                total_time += response_time
                total_calls += 1
                endpoint_calls += 1
                
                is_auth_failure = response.get('status_code') in [401, 403] if not success else False
                
                if is_auth_failure:
                    auth_failures += 1
                    endpoint_auth_failures += 1
                    print(f"      Call {call_num}: ❌ AUTH FAILURE ({response.get('status_code')})")
                elif not success:
                    print(f"      Call {call_num}: ⚠️ OTHER ERROR ({response.get('status_code')})")
                else:
                    print(f"      Call {call_num}: ✅ SUCCESS ({response_time:.3f}s)")
                
                # Small delay between calls
                time.sleep(0.1)
            
            endpoint_results.append({
                'method': method,
                'endpoint': endpoint,
                'total_calls': endpoint_calls,
                'auth_failures': endpoint_auth_failures,
                'success_rate': (endpoint_calls - endpoint_auth_failures) / endpoint_calls * 100
            })
        
        overall_success_rate = (total_calls - auth_failures) / total_calls * 100
        
        details = {
            'total_api_calls': total_calls,
            'auth_failures': auth_failures,
            'overall_success_rate': overall_success_rate,
            'average_response_time': total_time / total_calls,
            'endpoint_results': endpoint_results
        }
        
        # Test passes if less than 5% auth failures (allowing for some intermittent issues)
        test_passed = auth_failures < total_calls * 0.05
        
        self.log_test("Multiple API Calls Same Token", test_passed, details, total_time)
        return test_passed

    def test_specific_endpoints_consistency(self) -> bool:
        """Test specific endpoints mentioned in review request"""
        print("\n🎯 Testing Specific Endpoints from Review Request...")
        
        if not self.token:
            self.log_test("Specific Endpoints Consistency", False, {'error': 'No authentication token available'})
            return False
        
        # Endpoints specifically mentioned in review
        review_endpoints = [
            ('GET', 'tasks', {}, 'Core Tasks Endpoint'),
            ('GET', 'projects', {}, 'Core Projects Endpoint'),
            ('GET', 'areas', {}, 'Core Areas Endpoint'),
            ('GET', 'pillars', {}, 'Core Pillars Endpoint'),
            ('GET', 'hrm/analyze', {}, 'HRM Analyze Endpoint'),
            ('GET', 'hrm/insights', {}, 'HRM Insights Endpoint'),
            ('GET', 'semantic/search', {'query': 'test', 'limit': 5}, 'Semantic Search Endpoint'),
        ]
        
        endpoint_results = []
        total_time = 0
        auth_failures = 0
        
        for method, endpoint, params, description in review_endpoints:
            print(f"   Testing {description}: {method} /api/{endpoint}...")
            
            success, response, response_time = self.make_request(
                method, endpoint, params=params, 
                test_context="specific_endpoints_consistency"
            )
            total_time += response_time
            
            is_auth_failure = response.get('status_code') in [401, 403] if not success else False
            
            result = {
                'description': description,
                'method': method,
                'endpoint': endpoint,
                'success': success,
                'response_time': response_time,
                'auth_failure': is_auth_failure,
                'status_code': response.get('status_code') if not success else 200
            }
            
            if is_auth_failure:
                auth_failures += 1
                print(f"      ❌ AUTH FAILURE: {response.get('status_code')} - {response.get('error', '')[:100]}")
            elif not success:
                print(f"      ⚠️ OTHER ERROR: {response.get('status_code')} - {response.get('error', '')[:100]}")
            else:
                print(f"      ✅ SUCCESS: {response_time:.3f}s")
            
            endpoint_results.append(result)
            time.sleep(0.2)  # Slight delay between endpoint tests
        
        success_rate = (len(review_endpoints) - auth_failures) / len(review_endpoints) * 100
        
        details = {
            'total_endpoints': len(review_endpoints),
            'auth_failures': auth_failures,
            'success_rate': success_rate,
            'average_response_time': total_time / len(review_endpoints),
            'endpoint_results': endpoint_results
        }
        
        # Test passes if no auth failures on core endpoints
        test_passed = auth_failures == 0
        
        self.log_test("Specific Endpoints Consistency", test_passed, details, total_time)
        return test_passed

    def test_rapid_concurrent_requests(self) -> bool:
        """Test rapid API calls and concurrent requests for race conditions"""
        print("\n⚡ Testing Rapid and Concurrent Requests (Race Conditions)...")
        
        if not self.token:
            self.log_test("Rapid Concurrent Requests", False, {'error': 'No authentication token available'})
            return False
        
        # Test 1: Rapid sequential requests
        print("   Phase 1: Rapid sequential requests...")
        rapid_results = []
        rapid_auth_failures = 0
        
        for i in range(15):  # 15 rapid requests
            success, response, response_time = self.make_request(
                'GET', 'tasks', test_context=f"rapid_request_{i+1}"
            )
            
            is_auth_failure = response.get('status_code') in [401, 403] if not success else False
            if is_auth_failure:
                rapid_auth_failures += 1
                print(f"      Request {i+1}: ❌ AUTH FAILURE")
            elif not success:
                print(f"      Request {i+1}: ⚠️ ERROR")
            else:
                print(f"      Request {i+1}: ✅ SUCCESS")
            
            rapid_results.append({
                'request_num': i + 1,
                'success': success,
                'auth_failure': is_auth_failure,
                'response_time': response_time
            })
            
            time.sleep(0.02)  # Very rapid requests
        
        # Test 2: Concurrent requests
        print("   Phase 2: Concurrent requests...")
        
        def make_concurrent_request(endpoint_info):
            method, endpoint, params = endpoint_info
            return self.make_request(method, endpoint, params=params, 
                                   test_context="concurrent_request")
        
        # Use core endpoints for concurrent testing
        concurrent_endpoints = self.core_endpoints[:4]
        concurrent_results = []
        concurrent_auth_failures = 0
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(concurrent_endpoints)) as executor:
            future_to_endpoint = {
                executor.submit(make_concurrent_request, endpoint_info): endpoint_info 
                for endpoint_info in concurrent_endpoints
            }
            
            for future in concurrent.futures.as_completed(future_to_endpoint):
                endpoint_info = future_to_endpoint[future]
                method, endpoint, params = endpoint_info
                
                try:
                    success, response, response_time = future.result()
                    
                    is_auth_failure = response.get('status_code') in [401, 403] if not success else False
                    if is_auth_failure:
                        concurrent_auth_failures += 1
                        print(f"      {method} {endpoint}: ❌ AUTH FAILURE")
                    elif not success:
                        print(f"      {method} {endpoint}: ⚠️ ERROR")
                    else:
                        print(f"      {method} {endpoint}: ✅ SUCCESS")
                    
                    concurrent_results.append({
                        'method': method,
                        'endpoint': endpoint,
                        'success': success,
                        'auth_failure': is_auth_failure,
                        'response_time': response_time
                    })
                    
                except Exception as e:
                    print(f"      {method} {endpoint}: ❌ EXCEPTION: {e}")
        
        total_auth_failures = rapid_auth_failures + concurrent_auth_failures
        total_requests = len(rapid_results) + len(concurrent_results)
        
        details = {
            'rapid_requests': len(rapid_results),
            'rapid_auth_failures': rapid_auth_failures,
            'concurrent_requests': len(concurrent_results),
            'concurrent_auth_failures': concurrent_auth_failures,
            'total_auth_failures': total_auth_failures,
            'total_requests': total_requests,
            'success_rate': (total_requests - total_auth_failures) / total_requests * 100 if total_requests > 0 else 0
        }
        
        # Test passes if no auth failures in race condition scenarios
        test_passed = total_auth_failures == 0
        
        self.log_test("Rapid Concurrent Requests", test_passed, details)
        return test_passed

    def test_different_http_methods(self) -> bool:
        """Test different HTTP methods (GET vs POST vs PUT) as mentioned in review"""
        print("\n🔧 Testing Different HTTP Methods...")
        
        if not self.token:
            self.log_test("Different HTTP Methods", False, {'error': 'No authentication token available'})
            return False
        
        # Test different HTTP methods on safe endpoints
        method_tests = [
            ('GET', 'tasks', {}, 'GET Tasks'),
            ('GET', 'projects', {}, 'GET Projects'),
            ('GET', 'areas', {}, 'GET Areas'),
            ('GET', 'pillars', {}, 'GET Pillars'),
            ('GET', 'insights', {}, 'GET Insights'),
            ('GET', 'journal', {}, 'GET Journal'),
            # Note: Avoiding POST/PUT/DELETE to prevent data modification during testing
        ]
        
        results = []
        auth_failures = 0
        total_time = 0
        
        for method, endpoint, params, description in method_tests:
            print(f"   Testing {description}: {method} /api/{endpoint}...")
            
            success, response, response_time = self.make_request(
                method, endpoint, params=params, 
                test_context="different_http_methods"
            )
            total_time += response_time
            
            is_auth_failure = response.get('status_code') in [401, 403] if not success else False
            
            result = {
                'description': description,
                'method': method,
                'endpoint': endpoint,
                'success': success,
                'response_time': response_time,
                'auth_failure': is_auth_failure
            }
            
            if is_auth_failure:
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
        
        self.log_test("Different HTTP Methods", test_passed, details, total_time)
        return test_passed

    def test_authentication_headers_validation(self) -> bool:
        """Test authentication headers as specified in review request"""
        print("\n🔒 Testing Authentication Headers Validation...")
        
        # Test proper Authorization: Bearer {token} headers
        print("   Testing proper Bearer token...")
        success, response, response_time = self.make_request(
            'GET', 'tasks', 
            headers={'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'},
            test_context="proper_bearer_token"
        )
        
        proper_auth_works = success
        
        # Test missing headers (should get 401/403)
        print("   Testing missing Authorization header...")
        success, response, response_time = self.make_request(
            'GET', 'tasks',
            headers={'Content-Type': 'application/json'},  # No Authorization header
            test_context="missing_auth_header"
        )
        
        missing_auth_fails = not success and response.get('status_code') in [401, 403]
        
        # Test malformed headers
        print("   Testing malformed Authorization header...")
        success, response, response_time = self.make_request(
            'GET', 'tasks',
            headers={'Authorization': 'Bearer invalid-token-123', 'Content-Type': 'application/json'},
            test_context="malformed_auth_header"
        )
        
        malformed_auth_fails = not success and response.get('status_code') in [401, 403]
        
        details = {
            'proper_bearer_token_works': proper_auth_works,
            'missing_auth_header_fails': missing_auth_fails,
            'malformed_auth_header_fails': malformed_auth_fails,
            'all_auth_validation_correct': proper_auth_works and missing_auth_fails and malformed_auth_fails
        }
        
        test_passed = proper_auth_works and missing_auth_fails and malformed_auth_fails
        
        self.log_test("Authentication Headers Validation", test_passed, details)
        return test_passed

    def analyze_failure_patterns(self):
        """Analyze patterns in authentication failures as requested in review"""
        print("\n🔍 Analyzing Authentication Failure Patterns...")
        
        if not self.auth_failures:
            print("   ✅ No authentication failures detected!")
            return
        
        print(f"   Found {len(self.auth_failures)} authentication failures:")
        
        # Which endpoints fail most often?
        endpoint_failures = {}
        for failure in self.auth_failures:
            endpoint = failure['endpoint']
            endpoint_failures[endpoint] = endpoint_failures.get(endpoint, 0) + 1
        
        print(f"\n   📊 Failures by endpoint (Which endpoints fail most often?):")
        for endpoint, count in sorted(endpoint_failures.items(), key=lambda x: x[1], reverse=True):
            print(f"      {endpoint}: {count} failures")
        
        # Are failures related to specific routes?
        route_patterns = {}
        for failure in self.auth_failures:
            route_type = failure['endpoint'].split('/')[0] if '/' in failure['endpoint'] else failure['endpoint']
            route_patterns[route_type] = route_patterns.get(route_type, 0) + 1
        
        print(f"\n   📊 Failures by route type (Are failures related to specific routes?):")
        for route_type, count in sorted(route_patterns.items(), key=lambda x: x[1], reverse=True):
            print(f"      {route_type}: {count} failures")
        
        # Are there timing-related issues?
        timing_contexts = {}
        for failure in self.auth_failures:
            context = failure.get('test_context', 'unknown')
            timing_contexts[context] = timing_contexts.get(context, 0) + 1
        
        print(f"\n   📊 Failures by test context (Are there timing-related issues?):")
        for context, count in sorted(timing_contexts.items(), key=lambda x: x[1], reverse=True):
            print(f"      {context}: {count} failures")
        
        # Status code distribution
        status_codes = {}
        for failure in self.auth_failures:
            status_code = failure['status_code']
            status_codes[status_code] = status_codes.get(status_code, 0) + 1
        
        print(f"\n   📊 Failures by status code:")
        for status_code, count in sorted(status_codes.items()):
            print(f"      {status_code}: {count} failures")
        
        # Recent failures timeline
        print(f"\n   🕒 Recent failures timeline:")
        recent_failures = sorted(self.auth_failures, key=lambda x: x['timestamp'])[-10:]
        for failure in recent_failures:
            print(f"      {failure['timestamp']}: {failure['method']} {failure['endpoint']} -> {failure['status_code']}")

    def run_comprehensive_test(self):
        """Run all authentication tests as specified in review request"""
        print("🚀 Starting Comprehensive Authentication Issues Test")
        print("=" * 80)
        print("Focus: Intermittent API authentication issues")
        print("Authentication Flow: Login with test@aurumlife.com/password123")
        print("=" * 80)
        
        # Step 1: Authentication flow (as specified in review)
        if not self.test_authentication_flow():
            print("\n❌ Authentication failed. Cannot proceed with other tests.")
            return False
        
        # Step 2: Get JWT token (already done in authentication flow)
        print(f"\n✅ JWT Token obtained: {self.token[:30]}...")
        
        # Step 3: Make multiple API calls with same token
        # Step 4: Check for any 403 "Not authenticated" responses
        # Step 5: Identify which endpoints have issues
        test_methods = [
            self.test_multiple_api_calls_same_token,
            self.test_specific_endpoints_consistency,
            self.test_rapid_concurrent_requests,
            self.test_different_http_methods,
            self.test_authentication_headers_validation,
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"❌ Test {test_method.__name__} failed with exception: {e}")
                self.log_test(test_method.__name__, False, {'exception': str(e)})
        
        # Analyze failure patterns (as requested in review)
        self.analyze_failure_patterns()
        
        # Print summary
        self.print_summary()
        
        return self.tests_passed == self.tests_run

    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE AUTHENTICATION ISSUES TEST SUMMARY")
        print("=" * 80)
        
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
                                 if k in ['auth_failures', 'success_rate', 'error', 'total_auth_failures']}
                    if key_details:
                        print(f"    {key_details}")
        
        # Print key findings as requested in review
        print(f"\n🔍 KEY FINDINGS (Review Request Analysis):")
        
        # Total authentication failures
        total_auth_failures = len(self.auth_failures)
        print(f"  • Total 403 'Not authenticated' errors: {total_auth_failures}")
        
        if total_auth_failures > 0:
            print(f"  • ❌ INTERMITTENT AUTHENTICATION ISSUES CONFIRMED")
            
            # Which endpoints have authentication issues?
            endpoint_failures = {}
            for failure in self.auth_failures:
                endpoint = failure['endpoint']
                endpoint_failures[endpoint] = endpoint_failures.get(endpoint, 0) + 1
            
            if endpoint_failures:
                print(f"  • Endpoints with authentication issues:")
                for endpoint, count in sorted(endpoint_failures.items(), key=lambda x: x[1], reverse=True):
                    print(f"    - {endpoint}: {count} failures")
            
            # Are failures related to specific routes?
            route_patterns = {}
            for failure in self.auth_failures:
                route_type = failure['endpoint'].split('/')[0] if '/' in failure['endpoint'] else failure['endpoint']
                route_patterns[route_type] = route_patterns.get(route_type, 0) + 1
            
            print(f"  • Route-level issues:")
            for route_type, count in sorted(route_patterns.items(), key=lambda x: x[1], reverse=True):
                print(f"    - {route_type} routes: {count} failures")
            
            # Are there timing-related issues?
            timing_contexts = {}
            for failure in self.auth_failures:
                context = failure.get('test_context', 'unknown')
                timing_contexts[context] = timing_contexts.get(context, 0) + 1
            
            timing_issues = any(context in ['rapid_request', 'concurrent_request'] for context in timing_contexts.keys())
            print(f"  • Timing-related issues: {'❌ DETECTED' if timing_issues else '✅ NONE'}")
            
        else:
            print(f"  • ✅ NO INTERMITTENT AUTHENTICATION ISSUES DETECTED")
        
        # Test-specific findings
        consistency_test = next((r for r in self.test_results if r['test_name'] == 'Multiple API Calls Same Token'), None)
        if consistency_test:
            success_rate = consistency_test['details'].get('overall_success_rate', 0)
            print(f"  • Multiple API calls consistency: {success_rate:.1f}% success rate")
        
        specific_endpoints_test = next((r for r in self.test_results if r['test_name'] == 'Specific Endpoints Consistency'), None)
        if specific_endpoints_test:
            auth_failures = specific_endpoints_test['details'].get('auth_failures', 0)
            print(f"  • Review request endpoints: {auth_failures} authentication failures")
        
        rapid_test = next((r for r in self.test_results if r['test_name'] == 'Rapid Concurrent Requests'), None)
        if rapid_test:
            rapid_success = rapid_test['success']
            print(f"  • Race conditions: {'✅ No issues' if rapid_success else '❌ Issues detected'}")
        
        headers_test = next((r for r in self.test_results if r['test_name'] == 'Authentication Headers Validation'), None)
        if headers_test:
            headers_success = headers_test['success']
            print(f"  • Authentication headers: {'✅ Working correctly' if headers_success else '❌ Issues detected'}")
        
        # Overall assessment
        print(f"\n🎯 OVERALL ASSESSMENT:")
        if total_auth_failures == 0 and self.tests_passed == self.tests_run:
            print("  ✅ NO INTERMITTENT AUTHENTICATION ISSUES FOUND")
            print("  ✅ All authentication mechanisms working consistently")
            print("  ✅ JWT tokens working properly across all endpoints")
            print("  ✅ No race conditions or timing issues detected")
        elif total_auth_failures > 0:
            print("  ❌ INTERMITTENT AUTHENTICATION ISSUES CONFIRMED")
            print("  🔧 Specific endpoints and scenarios identified above")
            print("  🔧 Review authentication decorators and JWT validation")
            print("  🔧 Check for route-level authentication configuration issues")
        else:
            print("  ⚠️ SOME AUTHENTICATION TESTS FAILED")
            print("  🔧 Review failed tests for specific authentication issues")

def main():
    """Main test execution"""
    tester = ComprehensiveAuthTester()
    
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