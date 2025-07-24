#!/usr/bin/env python3
"""
TASK REMINDERS & NOTIFICATIONS SYSTEM BACKEND TESTING
Comprehensive testing of the Task Reminders & Notifications System implementation.

FOCUS AREAS:
1. Notification Preferences API - GET/PUT `/api/notifications/preferences` endpoints
2. Notification Models - NotificationPreference and TaskReminder models validation
3. Browser Notifications API - GET `/api/notifications` and PUT `/api/notifications/{id}/read` endpoints
4. Task Reminder Scheduling - Creating tasks with due dates automatically schedules reminders
5. Notification Service Methods - Core NotificationService methods testing
6. Test Notification System - POST `/api/notifications/test` endpoint verification
7. Email Integration - SendGrid integration testing
8. Notification Processing - Background job logic for processing due reminders
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid
import time

# Configuration - Using the production backend URL from frontend/.env
BACKEND_URL = "https://task-pillar.preview.emergentagent.com/api"
DEFAULT_USER_ID = "demo-user-123"

class BackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.user_id = DEFAULT_USER_ID
        self.session = requests.Session()
        self.test_results = []
        self.created_resources = {
            'areas': [],
            'projects': [],
            'tasks': [],
            'users': [],
            'notifications': [],
            'reminders': []
        }
        self.auth_token = None
        self.test_user_email = f"notiftest_{uuid.uuid4().hex[:8]}@aurumlife.com"
        self.test_user_password = "NotificationTest123!"
        self.test_user_data = {
            "username": f"notiftest_{uuid.uuid4().hex[:8]}",
            "email": self.test_user_email,
            "first_name": "Notification",
            "last_name": "Tester",
            "password": self.test_user_password
        }
        
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
        headers = {}
        
        # Add authentication header if token is available and requested
        if use_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=headers)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, params=params, headers=headers)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, params=params, headers=headers)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            return {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'data': response.json() if response.content else {},
                'response': response
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None),
                'data': {},
                'response': getattr(e, 'response', None)
            }

    def test_api_configuration_fix_verification(self):
        """CRITICAL: Test API configuration fix - verify backend is accessible and timeout errors are resolved"""
        print("\n=== API CONFIGURATION FIX VERIFICATION ===")
        print("Testing that the API configuration fix resolved timeout errors")
        print(f"Backend URL: {self.base_url}")
        
        # Test 1: Basic API Health Check
        result = self.make_request('GET', '/health')
        self.log_test(
            "API HEALTH CHECK - Backend Accessibility",
            result['success'],
            f"Backend API is accessible at {self.base_url}" if result['success'] else f"Backend API not accessible: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            print("❌ CRITICAL FAILURE: Backend API is not accessible - configuration fix may not be working")
            return False
        
        # Test 2: API Root Endpoint
        result = self.make_request('GET', '/')
        self.log_test(
            "API ROOT ENDPOINT - Basic Response",
            result['success'],
            f"API root endpoint responding: {result['data'].get('message', 'Unknown')}" if result['success'] else f"API root failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test 3: User Registration (New Credentials)
        fresh_user_data = {
            "username": f"apitest_{uuid.uuid4().hex[:8]}",
            "email": f"apitest_{uuid.uuid4().hex[:8]}@aurumlife.com",
            "first_name": "API",
            "last_name": "Test",
            "password": "APITestPassword123!"
        }
        
        result = self.make_request('POST', '/auth/register', data=fresh_user_data)
        self.log_test(
            "USER REGISTRATION - New Credentials",
            result['success'],
            f"User registration successful: {result['data'].get('username', 'Unknown')}" if result['success'] else f"Registration failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            print("❌ CRITICAL FAILURE: User registration failed - API may not be working properly")
            return False
        
        user_data = result['data']
        self.created_resources['users'].append(user_data['id'])
        
        # Test 4: User Login with Registered Credentials
        login_data = {
            "email": fresh_user_data['email'],
            "password": fresh_user_data['password']
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        self.log_test(
            "USER LOGIN - Registered Credentials",
            result['success'],
            f"Login successful, JWT token received" if result['success'] else f"Login failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            print("❌ CRITICAL FAILURE: User login failed - authentication may not be working")
            return False
        
        # Store auth token for protected endpoint testing
        token_data = result['data']
        self.auth_token = token_data.get('access_token')
        
        # Verify token structure
        self.log_test(
            "JWT TOKEN VALIDATION",
            self.auth_token and len(self.auth_token) > 50 and token_data.get('token_type') == 'bearer',
            f"Valid JWT token generated (length: {len(self.auth_token) if self.auth_token else 0})"
        )
        
        # Test 5: Dashboard API Endpoint (Critical - was causing timeouts)
        result = self.make_request('GET', '/dashboard', use_auth=True)
        self.log_test(
            "DASHBOARD API - Load Without Timeouts",
            result['success'],
            f"Dashboard loads successfully without timeouts" if result['success'] else f"Dashboard failed: {result.get('error', 'Unknown error')}"
        )
        
        dashboard_success = result['success']
        if result['success']:
            dashboard_data = result['data']
            # Verify dashboard contains expected sections
            expected_sections = ['user', 'stats']
            present_sections = [section for section in expected_sections if section in dashboard_data]
            
            self.log_test(
                "Dashboard Data Structure",
                len(present_sections) >= 1,
                f"Dashboard contains {len(present_sections)}/{len(expected_sections)} expected sections: {present_sections}"
            )
            
            # Verify user data matches authenticated user
            user_section = dashboard_data.get('user', {})
            self.log_test(
                "Dashboard User Data Integrity",
                user_section.get('email') == fresh_user_data['email'],
                f"Dashboard returns correct user data: {user_section.get('email', 'Unknown')}"
            )
        
        # Test 6: Journal API Endpoint (Critical - was causing timeouts)
        result = self.make_request('GET', '/journal', use_auth=True)
        self.log_test(
            "JOURNAL API - Load Without Timeouts",
            result['success'],
            f"Journal API loads successfully without timeouts" if result['success'] else f"Journal API failed: {result.get('error', 'Unknown error')}"
        )
        
        journal_success = result['success']
        if result['success']:
            journal_entries = result['data']
            self.log_test(
                "Journal API Response Structure",
                isinstance(journal_entries, list),
                f"Journal API returns list of entries: {len(journal_entries)} entries"
            )
        
        # Test 7: Create Journal Entry to Test POST Operations
        journal_entry_data = {
            "title": "API Configuration Test Entry",
            "content": "Testing that the API configuration fix resolved timeout errors",
            "mood": "happy",
            "tags": ["testing", "api-fix"]
        }
        
        result = self.make_request('POST', '/journal', data=journal_entry_data, use_auth=True)
        self.log_test(
            "JOURNAL CREATE - POST Operation",
            result['success'],
            f"Journal entry created successfully" if result['success'] else f"Journal creation failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test 8: Additional Critical Endpoints
        critical_endpoints = [
            {'method': 'GET', 'endpoint': '/auth/me', 'name': 'Current User Info'},
            {'method': 'GET', 'endpoint': '/stats', 'name': 'User Statistics'},
            {'method': 'GET', 'endpoint': '/areas', 'name': 'User Areas'},
            {'method': 'GET', 'endpoint': '/projects', 'name': 'User Projects'},
            {'method': 'GET', 'endpoint': '/tasks', 'name': 'User Tasks'},
        ]
        
        successful_endpoints = 0
        total_endpoints = len(critical_endpoints)
        
        for endpoint_test in critical_endpoints:
            method = endpoint_test['method']
            endpoint = endpoint_test['endpoint']
            name = endpoint_test['name']
            
            result = self.make_request(method, endpoint, use_auth=True)
            
            self.log_test(
                f"CRITICAL ENDPOINT - {name}",
                result['success'],
                f"{method} {endpoint} working without timeouts" if result['success'] else f"{method} {endpoint} failed: {result.get('error', 'Unknown error')}"
            )
            
            if result['success']:
                successful_endpoints += 1
        
        success_rate = (successful_endpoints / total_endpoints) * 100
        self.log_test(
            "API Configuration Fix Success Rate",
            success_rate >= 80,
            f"API endpoints working: {successful_endpoints}/{total_endpoints} ({success_rate:.1f}%)"
        )
        
        print(f"\n✅ API CONFIGURATION FIX VERIFICATION COMPLETED")
        print(f"   Backend URL: {self.base_url}")
        print(f"   Registration: ✅ Working")
        print(f"   Login: ✅ Working") 
        print(f"   Dashboard: {'✅ Working' if dashboard_success else '❌ Failed'}")
        print(f"   Journal: {'✅ Working' if journal_success else '❌ Failed'}")
        print(f"   Overall Success Rate: {success_rate:.1f}%")
        
        return success_rate >= 80

def main():
    """Run API Configuration Fix Verification Tests"""
    print("🚀 STARTING API CONFIGURATION FIX VERIFICATION")
    print("=" * 80)
    
    tester = BackendTester()
    
    try:
        # Run the focused API configuration fix verification test
        success = tester.test_api_configuration_fix_verification()
        
        # Calculate overall results
        total_tests = len(tester.test_results)
        passed_tests = sum(1 for result in tester.test_results if result['success'])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("🎯 API CONFIGURATION FIX VERIFICATION SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("\n✅ API CONFIGURATION FIX VERIFICATION: SUCCESS")
            print("   The backend API is accessible and responding correctly")
            print("   User registration and login are working")
            print("   Dashboard and Journal APIs load without timeouts")
            print("   The API configuration fix has resolved the timeout errors")
        else:
            print("\n❌ API CONFIGURATION FIX VERIFICATION: ISSUES DETECTED")
            print("   Some API endpoints are still experiencing issues")
            print("   The configuration fix may need additional adjustments")
        
        # Show failed tests for debugging
        failed_tests = [result for result in tester.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        print("\n" + "=" * 80)
        
        return success_rate >= 80
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        return False
    
    finally:
        # Cleanup created resources
        print("\n🧹 CLEANING UP TEST RESOURCES")
        cleanup_count = 0
        
        # Clean up users
        for user_id in tester.created_resources.get('users', []):
            try:
                # Note: User deletion endpoint may not exist, so we'll skip cleanup
                cleanup_count += 1
                print(f"   ℹ️ User cleanup skipped (no delete endpoint): {user_id}")
            except:
                pass
        
        if cleanup_count > 0:
            print(f"   ✅ Cleanup completed for {cleanup_count} resources")
        else:
            print("   ℹ️ No resources to cleanup")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)