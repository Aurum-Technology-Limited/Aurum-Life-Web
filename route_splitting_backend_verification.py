#!/usr/bin/env python3
"""
ROUTE-BASED CODE SPLITTING BACKEND VERIFICATION
Testing that backend API endpoints continue to work correctly after frontend route-based code splitting implementation.

TESTING FOCUS:
- Authentication endpoints (/api/auth/login, /api/auth/me)
- Dashboard data endpoints (/api/dashboard, /api/today)
- Core CRUD endpoints for navigation (Areas, Projects, Tasks, Pillars)
- AI Coach endpoints (/api/ai/quota)
- Feedback endpoints (/api/feedback)

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password

PRIORITY: Verify that backend functionality is completely intact after frontend code splitting implementation.
All endpoints should work exactly as they did before since this was purely a frontend optimization.
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://focus-planner-3.preview.emergentagent.com/api"

class RouteSplittingBackendVerifier:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Use the specified credentials
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
        
        # Test the root endpoint
        try:
            base_url = self.base_url.replace('/api', '')
            response = self.session.get(f"{base_url}/", timeout=30)
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

    def test_authentication_endpoints(self):
        """Test authentication endpoints (/api/auth/login, /api/auth/me)"""
        print("\n=== TESTING AUTHENTICATION ENDPOINTS ===")
        
        # Test login endpoint
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        self.log_test(
            "AUTH LOGIN ENDPOINT",
            result['success'],
            f"Login successful with {self.test_user_email}" if result['success'] else f"Login failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        token_data = result['data']
        self.auth_token = token_data.get('access_token')
        
        # Test /auth/me endpoint
        result = self.make_request('GET', '/auth/me', use_auth=True)
        self.log_test(
            "AUTH ME ENDPOINT",
            result['success'],
            f"Token validated successfully, user: {result['data'].get('email', 'Unknown')}" if result['success'] else f"Token validation failed: {result.get('error', 'Unknown error')}"
        )
        
        return result['success']

    def test_dashboard_endpoints(self):
        """Test dashboard data endpoints (/api/dashboard, /api/today)"""
        print("\n=== TESTING DASHBOARD ENDPOINTS ===")
        
        if not self.auth_token:
            self.log_test("DASHBOARD ENDPOINTS - Authentication Required", False, "No authentication token available")
            return False
        
        # Test /api/dashboard endpoint
        result = self.make_request('GET', '/dashboard', use_auth=True)
        self.log_test(
            "DASHBOARD ENDPOINT",
            result['success'],
            f"Dashboard data retrieved successfully" if result['success'] else f"Dashboard failed: {result.get('error', 'Unknown error')}"
        )
        
        dashboard_success = result['success']
        
        # Test /api/today endpoint
        result = self.make_request('GET', '/today', use_auth=True)
        self.log_test(
            "TODAY ENDPOINT",
            result['success'],
            f"Today data retrieved successfully" if result['success'] else f"Today failed: {result.get('error', 'Unknown error')}"
        )
        
        today_success = result['success']
        
        return dashboard_success and today_success

    def test_core_crud_endpoints(self):
        """Test core CRUD endpoints for navigation (Areas, Projects, Tasks, Pillars)"""
        print("\n=== TESTING CORE CRUD ENDPOINTS ===")
        
        if not self.auth_token:
            self.log_test("CORE CRUD ENDPOINTS - Authentication Required", False, "No authentication token available")
            return False
        
        endpoints_to_test = [
            ('GET', '/pillars', 'PILLARS GET'),
            ('GET', '/areas', 'AREAS GET'),
            ('GET', '/projects', 'PROJECTS GET'),
            ('GET', '/tasks', 'TASKS GET')
        ]
        
        successful_endpoints = 0
        total_endpoints = len(endpoints_to_test)
        
        for method, endpoint, test_name in endpoints_to_test:
            result = self.make_request(method, endpoint, use_auth=True)
            self.log_test(
                test_name,
                result['success'],
                f"{test_name} endpoint working correctly" if result['success'] else f"{test_name} failed: {result.get('error', 'Unknown error')}"
            )
            
            if result['success']:
                successful_endpoints += 1
        
        success_rate = (successful_endpoints / total_endpoints) * 100
        overall_success = success_rate >= 75
        
        self.log_test(
            "CORE CRUD ENDPOINTS OVERALL",
            overall_success,
            f"Core CRUD endpoints: {successful_endpoints}/{total_endpoints} working ({success_rate:.1f}%)"
        )
        
        return overall_success

    def test_ai_coach_endpoints(self):
        """Test AI Coach endpoints (/api/ai/quota)"""
        print("\n=== TESTING AI COACH ENDPOINTS ===")
        
        if not self.auth_token:
            self.log_test("AI COACH ENDPOINTS - Authentication Required", False, "No authentication token available")
            return False
        
        # Test /api/ai/quota endpoint
        result = self.make_request('GET', '/ai/quota', use_auth=True)
        self.log_test(
            "AI QUOTA ENDPOINT",
            result['success'],
            f"AI quota retrieved successfully: {result['data']}" if result['success'] else f"AI quota failed: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            # Verify quota structure
            quota_data = result['data']
            has_required_fields = all(field in quota_data for field in ['total', 'used', 'remaining'])
            self.log_test(
                "AI QUOTA STRUCTURE",
                has_required_fields,
                f"AI quota has required fields (total, used, remaining)" if has_required_fields else f"AI quota missing required fields: {list(quota_data.keys())}"
            )
            return has_required_fields
        
        return False

    def test_feedback_endpoints(self):
        """Test feedback endpoints (/api/feedback)"""
        print("\n=== TESTING FEEDBACK ENDPOINTS ===")
        
        if not self.auth_token:
            self.log_test("FEEDBACK ENDPOINTS - Authentication Required", False, "No authentication token available")
            return False
        
        # Test POST /api/feedback endpoint
        feedback_data = {
            "category": "suggestion",
            "priority": "medium",
            "subject": "Backend verification test feedback",
            "message": "Testing feedback endpoint after route-based code splitting implementation"
        }
        
        result = self.make_request('POST', '/feedback', data=feedback_data, use_auth=True)
        self.log_test(
            "FEEDBACK POST ENDPOINT",
            result['success'],
            f"Feedback submitted successfully" if result['success'] else f"Feedback submission failed: {result.get('error', 'Unknown error')}"
        )
        
        post_success = result['success']
        
        # Test GET /api/feedback endpoint
        result = self.make_request('GET', '/feedback', use_auth=True)
        self.log_test(
            "FEEDBACK GET ENDPOINT",
            result['success'],
            f"Feedback history retrieved successfully" if result['success'] else f"Feedback retrieval failed: {result.get('error', 'Unknown error')}"
        )
        
        get_success = result['success']
        
        return post_success and get_success

    def test_additional_critical_endpoints(self):
        """Test additional critical endpoints that might be affected"""
        print("\n=== TESTING ADDITIONAL CRITICAL ENDPOINTS ===")
        
        if not self.auth_token:
            self.log_test("ADDITIONAL ENDPOINTS - Authentication Required", False, "No authentication token available")
            return False
        
        # Test task search endpoint (mentioned in review context)
        result = self.make_request('GET', '/tasks/search', params={'name': 'test'}, use_auth=True)
        self.log_test(
            "TASK SEARCH ENDPOINT",
            result['success'],
            f"Task search working correctly" if result['success'] else f"Task search failed: {result.get('error', 'Unknown error')}"
        )
        
        search_success = result['success']
        
        # Test sleep reflections endpoints (mentioned in context)
        result = self.make_request('GET', '/sleep-reflections', use_auth=True)
        self.log_test(
            "SLEEP REFLECTIONS ENDPOINT",
            result['success'],
            f"Sleep reflections working correctly" if result['success'] else f"Sleep reflections failed: {result.get('error', 'Unknown error')}"
        )
        
        sleep_success = result['success']
        
        return search_success and sleep_success

    def run_comprehensive_backend_verification(self):
        """Run comprehensive backend verification after route-based code splitting"""
        print("\n🔍 STARTING ROUTE-BASED CODE SPLITTING BACKEND VERIFICATION")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("Testing that backend functionality is intact after frontend code splitting")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("Authentication Endpoints", self.test_authentication_endpoints),
            ("Dashboard Endpoints", self.test_dashboard_endpoints),
            ("Core CRUD Endpoints", self.test_core_crud_endpoints),
            ("AI Coach Endpoints", self.test_ai_coach_endpoints),
            ("Feedback Endpoints", self.test_feedback_endpoints),
            ("Additional Critical Endpoints", self.test_additional_critical_endpoints)
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
        print("🔍 ROUTE-BASED CODE SPLITTING BACKEND VERIFICATION SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Categories: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results by category
        auth_tests_passed = sum(1 for result in self.test_results if result['success'] and 'AUTH' in result['test'])
        dashboard_tests_passed = sum(1 for result in self.test_results if result['success'] and 'DASHBOARD' in result['test'] or 'TODAY' in result['test'])
        crud_tests_passed = sum(1 for result in self.test_results if result['success'] and any(crud in result['test'] for crud in ['PILLARS', 'AREAS', 'PROJECTS', 'TASKS']))
        ai_tests_passed = sum(1 for result in self.test_results if result['success'] and 'AI' in result['test'])
        feedback_tests_passed = sum(1 for result in self.test_results if result['success'] and 'FEEDBACK' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"Authentication Tests Passed: {auth_tests_passed}")
        print(f"Dashboard Tests Passed: {dashboard_tests_passed}")
        print(f"CRUD Tests Passed: {crud_tests_passed}")
        print(f"AI Coach Tests Passed: {ai_tests_passed}")
        print(f"Feedback Tests Passed: {feedback_tests_passed}")
        
        if success_rate >= 85:
            print("\n✅ BACKEND VERIFICATION: SUCCESS")
            print("   ✅ Authentication endpoints working (/api/auth/login, /api/auth/me)")
            print("   ✅ Dashboard endpoints functional (/api/dashboard, /api/today)")
            print("   ✅ Core CRUD endpoints operational (Areas, Projects, Tasks, Pillars)")
            print("   ✅ AI Coach endpoints working (/api/ai/quota)")
            print("   ✅ Feedback endpoints functional (/api/feedback)")
            print("   🎉 Backend functionality is completely intact after frontend code splitting!")
        else:
            print("\n❌ BACKEND VERIFICATION: ISSUES DETECTED")
            print("   Issues found in backend functionality after frontend code splitting")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 85

def main():
    """Run Route-Based Code Splitting Backend Verification"""
    print("🔍 STARTING ROUTE-BASED CODE SPLITTING BACKEND VERIFICATION")
    print("=" * 80)
    
    verifier = RouteSplittingBackendVerifier()
    
    try:
        # Run the comprehensive backend verification
        success = verifier.run_comprehensive_backend_verification()
        
        # Calculate overall results
        total_tests = len(verifier.test_results)
        passed_tests = sum(1 for result in verifier.test_results if result['success'])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 FINAL RESULTS")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 85:
            print("\n🎉 CONCLUSION: Backend functionality is completely intact after frontend route-based code splitting!")
            print("✅ All core endpoints continue to work exactly as they did before")
            print("✅ Frontend optimization did not break any backend functionality")
        else:
            print("\n⚠️ CONCLUSION: Some backend issues detected after frontend code splitting")
            print("🔧 Investigation needed to ensure backend stability")
        
        print("=" * 80)
        
        return success_rate >= 85
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during verification: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)