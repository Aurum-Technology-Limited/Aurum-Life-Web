#!/usr/bin/env python3
"""
ADMIN SEED DEMO ENDPOINT TESTING
Testing the /api/admin/seed-demo endpoint with authentication and verification.

FOCUS AREAS:
1. Authentication with marc.alleyne@aurumtechnologyltd.com / password123
2. POST /api/admin/seed-demo with size=medium and include_streak=true
3. Verify response HTTP 200 and JSON structure
4. Verify created counts with pillars>0, areas>0, projects>0, tasks>0
5. Fetch GET /api/ultra/pillars, /api/ultra/areas, /api/ultra/projects and confirm non-empty arrays

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password123
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://hierarchy-master.preview.emergentagent.com/api"

class AdminSeedDemoTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Use the specified test credentials
        self.test_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.test_user_password = "password123"
        
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
            start_time = time.time()
            
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
            
            response_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
            
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
                'response_time': 0
            }

    def test_user_authentication(self):
        """Test user authentication with specified credentials"""
        print("\n=== STEP 1: USER AUTHENTICATION ===")
        
        # Login user with specified credentials
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        self.log_test(
            "USER LOGIN",
            result['success'],
            f"Login successful with {self.test_user_email} ({result.get('response_time', 0)}ms)" if result['success'] else f"Login failed: {result.get('error', 'Unknown error')}"
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
            f"Token validated successfully, user: {result['data'].get('email', 'Unknown')} ({result.get('response_time', 0)}ms)" if result['success'] else f"Token validation failed: {result.get('error', 'Unknown error')}"
        )
        
        return result['success']

    def test_admin_seed_demo(self):
        """Test POST /api/admin/seed-demo with size=medium and include_streak=true"""
        print("\n=== STEP 2: ADMIN SEED DEMO ENDPOINT ===")
        
        if not self.auth_token:
            self.log_test("ADMIN SEED DEMO - Authentication Required", False, "No authentication token available")
            return False
        
        # Test POST /api/admin/seed-demo with required parameters
        params = {
            "size": "medium",
            "include_streak": "true"
        }
        
        result = self.make_request('POST', '/admin/seed-demo', params=params, use_auth=True)
        self.log_test(
            "POST ADMIN SEED DEMO",
            result['success'],
            f"Seed demo successful ({result.get('response_time', 0)}ms)" if result['success'] else f"Seed demo failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        seed_response = result['data']
        
        # Verify response structure - must contain specific keys
        required_keys = ['message', 'size', 'include_streak']
        missing_keys = [key for key in required_keys if key not in seed_response]
        
        if missing_keys:
            self.log_test(
                "SEED DEMO RESPONSE STRUCTURE",
                False,
                f"Missing required keys: {missing_keys}"
            )
            return False
        
        # Verify specific values
        message_correct = seed_response.get('message') == 'Demo data seeded'
        size_correct = seed_response.get('size') == 'medium'
        include_streak_correct = seed_response.get('include_streak') == True
        
        structure_valid = message_correct and size_correct and include_streak_correct
        self.log_test(
            "SEED DEMO RESPONSE VALUES",
            structure_valid,
            f"Response values correct: message='{seed_response.get('message')}', size='{seed_response.get('size')}', include_streak={seed_response.get('include_streak')}" if structure_valid else f"Response values incorrect: message='{seed_response.get('message')}', size='{seed_response.get('size')}', include_streak={seed_response.get('include_streak')}"
        )
        
        if not structure_valid:
            return False
        
        # Verify created counts - must have pillars>0, areas>0, projects>0, tasks>0
        created_counts = seed_response.get('created_counts', {})
        if not created_counts:
            self.log_test(
                "SEED DEMO CREATED COUNTS",
                False,
                "No 'created_counts' field in response"
            )
            return False
        
        pillars_count = created_counts.get('pillars', 0)
        areas_count = created_counts.get('areas', 0)
        projects_count = created_counts.get('projects', 0)
        tasks_count = created_counts.get('tasks', 0)
        
        counts_valid = (pillars_count > 0 and areas_count > 0 and 
                       projects_count > 0 and tasks_count > 0)
        
        self.log_test(
            "SEED DEMO CREATED COUNTS VALIDATION",
            counts_valid,
            f"Created counts valid: pillars={pillars_count}, areas={areas_count}, projects={projects_count}, tasks={tasks_count}" if counts_valid else f"Created counts invalid: pillars={pillars_count}, areas={areas_count}, projects={projects_count}, tasks={tasks_count}"
        )
        
        return counts_valid

    def test_ultra_endpoints_verification(self):
        """Test GET /api/ultra/pillars, /api/ultra/areas, /api/ultra/projects to confirm non-empty arrays"""
        print("\n=== STEP 3: ULTRA ENDPOINTS VERIFICATION ===")
        
        if not self.auth_token:
            self.log_test("ULTRA ENDPOINTS - Authentication Required", False, "No authentication token available")
            return False
        
        ultra_endpoints = [
            ('/ultra/pillars', 'pillars'),
            ('/ultra/areas', 'areas'),
            ('/ultra/projects', 'projects')
        ]
        
        all_endpoints_valid = True
        
        for endpoint, entity_name in ultra_endpoints:
            result = self.make_request('GET', endpoint, use_auth=True)
            
            if not result['success']:
                self.log_test(
                    f"GET {endpoint}",
                    False,
                    f"Failed to fetch {entity_name}: {result.get('error', 'Unknown error')}"
                )
                all_endpoints_valid = False
                continue
            
            data = result['data']
            
            # Check if response is an array and non-empty
            if isinstance(data, list):
                is_non_empty = len(data) > 0
                self.log_test(
                    f"GET {endpoint}",
                    is_non_empty,
                    f"Retrieved {len(data)} {entity_name} ({result.get('response_time', 0)}ms)" if is_non_empty else f"Empty {entity_name} array returned"
                )
                if not is_non_empty:
                    all_endpoints_valid = False
            else:
                self.log_test(
                    f"GET {endpoint}",
                    False,
                    f"Response is not an array: {type(data)}"
                )
                all_endpoints_valid = False
        
        return all_endpoints_valid

    def run_comprehensive_admin_seed_demo_test(self):
        """Run comprehensive admin seed demo test"""
        print("\n🌱 STARTING ADMIN SEED DEMO COMPREHENSIVE TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("Test Parameters: size=medium, include_streak=true")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("User Authentication", self.test_user_authentication),
            ("Admin Seed Demo", self.test_admin_seed_demo),
            ("Ultra Endpoints Verification", self.test_ultra_endpoints_verification)
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
                    # Continue with remaining tests even if one fails
            except Exception as e:
                print(f"❌ {test_name} raised exception: {e}")
        
        success_rate = (successful_tests / total_tests) * 100
        
        print(f"\n" + "=" * 80)
        print("🌱 ADMIN SEED DEMO TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for admin seed demo functionality
        auth_tests_passed = sum(1 for result in self.test_results if result['success'] and 'LOGIN' in result['test'] or 'AUTHENTICATION' in result['test'])
        seed_tests_passed = sum(1 for result in self.test_results if result['success'] and 'SEED DEMO' in result['test'])
        ultra_tests_passed = sum(1 for result in self.test_results if result['success'] and 'ultra' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"Authentication Tests Passed: {auth_tests_passed}")
        print(f"Seed Demo Tests Passed: {seed_tests_passed}")
        print(f"Ultra Endpoints Tests Passed: {ultra_tests_passed}")
        
        if success_rate >= 85:
            print("\n✅ ADMIN SEED DEMO SYSTEM: SUCCESS")
            print("   ✅ Authentication with specified credentials working")
            print("   ✅ POST /api/admin/seed-demo functional with size=medium and include_streak=true")
            print("   ✅ Response contains required JSON keys and values")
            print("   ✅ Created counts show pillars>0, areas>0, projects>0, tasks>0")
            print("   ✅ Ultra endpoints return non-empty arrays")
            print("   The Admin Seed Demo endpoint is production-ready!")
        else:
            print("\n❌ ADMIN SEED DEMO SYSTEM: ISSUES DETECTED")
            print("   Issues found in admin seed demo implementation")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 85

def main():
    """Run Admin Seed Demo Tests"""
    print("🌱 STARTING ADMIN SEED DEMO BACKEND TESTING")
    print("=" * 80)
    
    tester = AdminSeedDemoTester()
    
    try:
        # Run the comprehensive admin seed demo tests
        success = tester.run_comprehensive_admin_seed_demo_test()
        
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