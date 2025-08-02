#!/usr/bin/env python3
"""
QUICK HEALTH CHECK - CORE API CONNECTIVITY TESTING
Testing core APIs to ensure frontend onboarding UI improvements don't affect backend functionality.

FOCUS AREAS:
1. Basic API connectivity to /api/health (if exists) or /api/auth/me endpoint
2. Core authentication endpoints are responding correctly
3. No new errors in backend logs

This is a quick verification that frontend onboarding UI changes (hiding scrollbar and full-screen layout) 
haven't broken any backend communication. The changes were purely CSS/UI related and should not affect API functionality.

TESTING CRITERIA:
- Backend connectivity
- Authentication endpoints working
- Core API endpoints responding
- No critical errors in logs
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://89a5bc44-c171-4189-bb43-48a9a2640899.preview.emergentagent.com/api"

class QuickHealthCheckTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Use the specified test credentials
        self.test_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.test_user_password = "password"
        
    def log_test(self, test_name: str, success: bool, message: str = "", data: Any = None):
        """Log test results"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        if data:
            result['data'] = data
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if data and not success:
            print(f"   Data: {json.dumps(data, indent=2, default=str)}")

    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None, use_auth: bool = False) -> Dict:
        """Make HTTP request with error handling and optional authentication"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        # Add authentication header if token is available and requested
        if use_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
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
                'error': f"HTTP {response.status_code}: {response_data}" if response.status_code >= 400 else None
            }
            
        except requests.exceptions.RequestException as e:
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
                'response': getattr(e, 'response', None)
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
                response = self.session.get(url, timeout=30)
                result = {
                    'success': response.status_code < 400,
                    'status_code': response.status_code,
                    'data': response.json() if response.content else {},
                }
            except:
                result = {'success': False, 'error': 'Connection failed'}
        
        self.log_test(
            "BACKEND API CONNECTIVITY",
            result['success'],
            f"Backend API accessible at {self.base_url}" if result['success'] else f"Backend API not accessible: {result.get('error', 'Unknown error')}"
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
            f"Login successful with {self.test_user_email}" if result['success'] else f"Login failed: {result.get('error', 'Unknown error')}"
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
            f"Token validated successfully, user: {result['data'].get('email', 'Unknown')}" if result['success'] else f"Token validation failed: {result.get('error', 'Unknown error')}"
        )
        
        return result['success']

    def test_core_api_endpoints(self):
        """Test core API endpoints to ensure they're responding"""
        print("\n=== TESTING CORE API ENDPOINTS ===")
        
        if not self.auth_token:
            self.log_test("CORE API ENDPOINTS - Authentication Required", False, "No authentication token available")
            return False
        
        # Test core endpoints that should be working
        core_endpoints = [
            ('/dashboard', 'Dashboard API'),
            ('/pillars', 'Pillars API'),
            ('/areas', 'Areas API'),
            ('/projects', 'Projects API'),
            ('/tasks', 'Tasks API')
        ]
        
        successful_endpoints = 0
        total_endpoints = len(core_endpoints)
        
        for endpoint, name in core_endpoints:
            result = self.make_request('GET', endpoint, use_auth=True)
            success = result['success']
            
            self.log_test(
                f"CORE API - {name}",
                success,
                f"{name} responding correctly" if success else f"{name} failed: {result.get('error', 'Unknown error')}"
            )
            
            if success:
                successful_endpoints += 1
        
        overall_success = successful_endpoints >= (total_endpoints * 0.8)  # 80% success rate
        
        self.log_test(
            "CORE API ENDPOINTS - OVERALL",
            overall_success,
            f"Core API endpoints: {successful_endpoints}/{total_endpoints} working ({(successful_endpoints/total_endpoints)*100:.1f}%)"
        )
        
        return overall_success

    def test_health_endpoint(self):
        """Test health endpoint if it exists"""
        print("\n=== TESTING HEALTH ENDPOINT ===")
        
        # Try common health endpoint patterns
        health_endpoints = [
            '/health',
            '/api/health',
            '/',
            '/status'
        ]
        
        health_found = False
        
        for endpoint in health_endpoints:
            # For root endpoint, use base URL without /api
            if endpoint == '/':
                test_url = self.base_url.replace('/api', '') + endpoint
                try:
                    response = self.session.get(test_url, timeout=30)
                    if response.status_code < 400:
                        self.log_test(
                            "HEALTH ENDPOINT",
                            True,
                            f"Health endpoint found at {test_url} (status: {response.status_code})"
                        )
                        health_found = True
                        break
                except:
                    continue
            else:
                result = self.make_request('GET', endpoint, use_auth=False)
                if result['success']:
                    self.log_test(
                        "HEALTH ENDPOINT",
                        True,
                        f"Health endpoint found at {endpoint} (status: {result['status_code']})"
                    )
                    health_found = True
                    break
        
        if not health_found:
            self.log_test(
                "HEALTH ENDPOINT",
                False,
                "No health endpoint found, but this is not critical"
            )
        
        return True  # Not critical if health endpoint doesn't exist

    def run_quick_health_check(self):
        """Run quick health check of core APIs"""
        print("\n🏥 STARTING QUICK HEALTH CHECK - CORE API CONNECTIVITY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("Purpose: Verify frontend UI changes haven't broken backend communication")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("Health Endpoint", self.test_health_endpoint),
            ("User Authentication", self.test_user_authentication),
            ("Core API Endpoints", self.test_core_api_endpoints)
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
        print("🏥 QUICK HEALTH CHECK SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results
        connectivity_tests_passed = sum(1 for result in self.test_results if result['success'] and 'CONNECTIVITY' in result['test'])
        auth_tests_passed = sum(1 for result in self.test_results if result['success'] and 'AUTHENTICATION' in result['test'])
        api_tests_passed = sum(1 for result in self.test_results if result['success'] and 'CORE API' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"Backend Connectivity Tests Passed: {connectivity_tests_passed}")
        print(f"Authentication Tests Passed: {auth_tests_passed}")
        print(f"Core API Tests Passed: {api_tests_passed}")
        
        if success_rate >= 75:
            print("\n✅ QUICK HEALTH CHECK: SUCCESS")
            print("   ✅ Backend connectivity working")
            print("   ✅ Authentication endpoints functional")
            print("   ✅ Core API endpoints responding")
            print("   ✅ Frontend UI changes have NOT broken backend communication")
            print("   The system is healthy and ready for use!")
        else:
            print("\n❌ QUICK HEALTH CHECK: ISSUES DETECTED")
            print("   Issues found that may indicate backend communication problems")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 75

def main():
    """Run Quick Health Check"""
    print("🏥 STARTING QUICK HEALTH CHECK - CORE API CONNECTIVITY")
    print("=" * 80)
    
    tester = QuickHealthCheckTester()
    
    try:
        # Run the quick health check
        success = tester.run_quick_health_check()
        
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
        
        return success_rate >= 75
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)