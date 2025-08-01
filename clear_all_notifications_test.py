#!/usr/bin/env python3
"""
DELETE /api/notifications/clear-all ENDPOINT - FOCUSED TESTING
Quick targeted test to verify the fix for the DELETE /api/notifications/clear-all endpoint 
that was previously returning 404 error.

FOCUS AREAS:
1. Test DELETE /api/notifications/clear-all endpoint specifically
2. Verify it returns proper success response instead of 404
3. Test with user that has notifications to clear
4. Test with user that has no notifications 
5. Ensure proper authentication is required
6. Verify the endpoint returns correct count of cleared notifications

TESTING STEPS:
1. Register/login a test user
2. Create some browser notifications for the user (via task completion or direct creation)
3. Call DELETE /api/notifications/clear-all
4. Verify success response with count
5. Verify notifications are actually deleted from database
6. Test endpoint again with no notifications to clear
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid
import time

# Configuration - Using the production backend URL from frontend/.env
BACKEND_URL = "https://3241bdaf-485d-4483-9bf8-f3b315478945.preview.emergentagent.com/api"

class ClearAllNotificationsTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.created_resources = {
            'pillars': [],
            'areas': [],
            'projects': [],
            'tasks': [],
            'notifications': [],
            'users': []
        }
        self.auth_token = None
        # Use realistic test data
        self.test_user_email = f"clearall.tester_{uuid.uuid4().hex[:8]}@aurumlife.com"
        self.test_user_password = "ClearAllTest2025!"
        self.test_user_data = {
            "username": f"clearall_tester_{uuid.uuid4().hex[:8]}",
            "email": self.test_user_email,
            "first_name": "ClearAll",
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
        headers = {"Content-Type": "application/json"}
        
        # Add authentication header if token is available and requested
        if use_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=headers, timeout=30)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, headers=headers, timeout=30)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, headers=headers, timeout=30)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, json=data, headers=headers, timeout=30)
            else:
                return {'error': f'Unsupported method: {method}', 'status_code': 400}
            
            # Try to parse JSON response
            try:
                response_data = response.json()
            except:
                response_data = {'raw_response': response.text}
            
            return {
                'status_code': response.status_code,
                'data': response_data,
                'success': 200 <= response.status_code < 300
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'error': str(e),
                'status_code': 0,
                'success': False
            }

    def test_basic_connectivity(self):
        """Test basic API connectivity"""
        print("\n=== TESTING BASIC CONNECTIVITY ===")
        
        # Test root endpoint
        result = self.make_request('GET', '/')
        if result.get('success'):
            self.log_test("BACKEND API CONNECTIVITY", True, f"Backend API accessible at {self.base_url}")
        else:
            self.log_test("BACKEND API CONNECTIVITY", False, f"Cannot connect to backend API", result)
            return False
        
        # Test health check
        result = self.make_request('GET', '/health')
        if result.get('success') and result.get('data', {}).get('status') == 'healthy':
            self.log_test("HEALTH CHECK RESPONSE", True, f"Health check returned: {result['data']['status']}")
        else:
            self.log_test("HEALTH CHECK RESPONSE", False, "Health check failed", result)
            return False
            
        return True

    def test_user_registration_and_login(self):
        """Test user registration and login"""
        print("\n=== TESTING USER REGISTRATION AND LOGIN ===")
        
        # Register user
        result = self.make_request('POST', '/auth/register', self.test_user_data)
        if result.get('success'):
            user_data = result.get('data', {})
            self.log_test("USER REGISTRATION", True, f"User registered successfully: {user_data.get('email')}")
            self.created_resources['users'].append(user_data.get('id'))
        else:
            self.log_test("USER REGISTRATION", False, "Failed to register user", result)
            return False
        
        # Login user
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        result = self.make_request('POST', '/auth/login', login_data)
        if result.get('success'):
            token_data = result.get('data', {})
            self.auth_token = token_data.get('access_token')
            self.log_test("USER LOGIN", True, "Login successful, JWT token received")
        else:
            self.log_test("USER LOGIN", False, "Failed to login user", result)
            return False
        
        # Validate token
        result = self.make_request('GET', '/auth/me', use_auth=True)
        if result.get('success'):
            user_info = result.get('data', {})
            self.log_test("AUTHENTICATION TOKEN VALIDATION", True, f"Token validated successfully, user: {user_info.get('email')}")
        else:
            self.log_test("AUTHENTICATION TOKEN VALIDATION", False, "Token validation failed", result)
            return False
            
        return True

    def create_test_notifications(self, count: int = 3) -> bool:
        """Create test notifications by completing tasks (which triggers notifications)"""
        print(f"\n=== CREATING {count} TEST NOTIFICATIONS ===")
        
        # First create infrastructure (pillar, area, project)
        pillar_data = {
            "name": "Test Pillar for Notifications",
            "description": "Test pillar for notification testing",
            "icon": "🔔",
            "color": "#3B82F6"
        }
        result = self.make_request('POST', '/pillars', pillar_data, use_auth=True)
        if not result.get('success'):
            self.log_test("CREATE TEST PILLAR", False, "Failed to create test pillar", result)
            return False
        pillar_id = result['data']['id']
        self.created_resources['pillars'].append(pillar_id)
        
        area_data = {
            "name": "Test Area for Notifications",
            "description": "Test area for notification testing",
            "pillar_id": pillar_id
        }
        result = self.make_request('POST', '/areas', area_data, use_auth=True)
        if not result.get('success'):
            self.log_test("CREATE TEST AREA", False, "Failed to create test area", result)
            return False
        area_id = result['data']['id']
        self.created_resources['areas'].append(area_id)
        
        project_data = {
            "name": "Test Project for Notifications",
            "description": "Test project for notification testing",
            "area_id": area_id
        }
        result = self.make_request('POST', '/projects', project_data, use_auth=True)
        if not result.get('success'):
            self.log_test("CREATE TEST PROJECT", False, "Failed to create test project", result)
            return False
        project_id = result['data']['id']
        self.created_resources['projects'].append(project_id)
        
        # Create tasks and complete them to generate notifications
        notifications_created = 0
        for i in range(count):
            # Create dependency task
            dep_task_data = {
                "name": f"Dependency Task {i+1}",
                "description": f"Dependency task {i+1} for notification testing",
                "project_id": project_id,
                "status": "todo"
            }
            result = self.make_request('POST', '/tasks', dep_task_data, use_auth=True)
            if not result.get('success'):
                continue
            dep_task_id = result['data']['id']
            self.created_resources['tasks'].append(dep_task_id)
            
            # Create dependent task
            dependent_task_data = {
                "name": f"Dependent Task {i+1}",
                "description": f"Dependent task {i+1} for notification testing",
                "project_id": project_id,
                "status": "todo",
                "dependency_task_ids": [dep_task_id]
            }
            result = self.make_request('POST', '/tasks', dependent_task_data, use_auth=True)
            if not result.get('success'):
                continue
            dependent_task_id = result['data']['id']
            self.created_resources['tasks'].append(dependent_task_id)
            
            # Complete dependency task to trigger notification
            update_data = {"status": "completed"}
            result = self.make_request('PUT', f'/tasks/{dep_task_id}', update_data, use_auth=True)
            if result.get('success'):
                notifications_created += 1
                time.sleep(0.5)  # Small delay to ensure notification is created
        
        self.log_test("CREATE TEST NOTIFICATIONS", notifications_created > 0, 
                     f"Created {notifications_created} test notifications via task completion")
        return notifications_created > 0

    def test_clear_all_notifications_with_data(self):
        """Test DELETE /api/notifications/clear-all with notifications present"""
        print("\n=== TESTING CLEAR-ALL WITH NOTIFICATIONS PRESENT ===")
        
        # First, get current notification count
        result = self.make_request('GET', '/notifications', use_auth=True)
        if not result.get('success'):
            self.log_test("GET NOTIFICATIONS BEFORE CLEAR", False, "Failed to get notifications", result)
            return False
        
        initial_notifications = result.get('data', [])
        initial_count = len(initial_notifications)
        self.log_test("GET NOTIFICATIONS BEFORE CLEAR", True, f"Found {initial_count} notifications before clear")
        
        if initial_count == 0:
            self.log_test("CLEAR-ALL WITH DATA - SETUP", False, "No notifications found to clear")
            return False
        
        # Test DELETE /api/notifications/clear-all
        result = self.make_request('DELETE', '/notifications/clear-all', use_auth=True)
        if result.get('success'):
            response_data = result.get('data', {})
            cleared_count = response_data.get('count', 0)
            success_flag = response_data.get('success', False)
            message = response_data.get('message', '')
            
            self.log_test("CLEAR-ALL ENDPOINT - SUCCESS RESPONSE", True, 
                         f"Clear-all returned success: {success_flag}, message: '{message}'")
            self.log_test("CLEAR-ALL ENDPOINT - COUNT RETURNED", cleared_count > 0, 
                         f"Clear-all returned count: {cleared_count}")
            
            # Verify notifications are actually cleared
            result = self.make_request('GET', '/notifications', use_auth=True)
            if result.get('success'):
                remaining_notifications = result.get('data', [])
                remaining_count = len(remaining_notifications)
                self.log_test("CLEAR-ALL VERIFICATION - NOTIFICATIONS DELETED", remaining_count == 0,
                             f"Remaining notifications after clear: {remaining_count}")
                return remaining_count == 0
            else:
                self.log_test("CLEAR-ALL VERIFICATION - GET AFTER CLEAR", False, "Failed to get notifications after clear", result)
                return False
        else:
            # Check if it's a 404 error (the bug we're testing for)
            status_code = result.get('status_code', 0)
            if status_code == 404:
                self.log_test("CLEAR-ALL ENDPOINT - 404 BUG DETECTED", False, 
                             "DELETE /api/notifications/clear-all returned 404 - BUG NOT FIXED", result)
            else:
                self.log_test("CLEAR-ALL ENDPOINT - OTHER ERROR", False, 
                             f"DELETE /api/notifications/clear-all failed with status {status_code}", result)
            return False

    def test_clear_all_notifications_empty(self):
        """Test DELETE /api/notifications/clear-all with no notifications"""
        print("\n=== TESTING CLEAR-ALL WITH NO NOTIFICATIONS ===")
        
        # Ensure no notifications exist
        result = self.make_request('GET', '/notifications', use_auth=True)
        if result.get('success'):
            notifications = result.get('data', [])
            if len(notifications) > 0:
                # Clear them first
                self.make_request('DELETE', '/notifications/clear-all', use_auth=True)
        
        # Test clear-all with empty notifications
        result = self.make_request('DELETE', '/notifications/clear-all', use_auth=True)
        if result.get('success'):
            response_data = result.get('data', {})
            cleared_count = response_data.get('count', 0)
            success_flag = response_data.get('success', False)
            message = response_data.get('message', '')
            
            self.log_test("CLEAR-ALL EMPTY - SUCCESS RESPONSE", True, 
                         f"Clear-all with empty notifications returned success: {success_flag}")
            self.log_test("CLEAR-ALL EMPTY - ZERO COUNT", cleared_count == 0, 
                         f"Clear-all with empty notifications returned count: {cleared_count}")
            return True
        else:
            status_code = result.get('status_code', 0)
            self.log_test("CLEAR-ALL EMPTY - FAILED", False, 
                         f"Clear-all with empty notifications failed with status {status_code}", result)
            return False

    def test_authentication_required(self):
        """Test that clear-all endpoint requires authentication"""
        print("\n=== TESTING AUTHENTICATION REQUIREMENT ===")
        
        # Test without authentication
        result = self.make_request('DELETE', '/notifications/clear-all', use_auth=False)
        if result.get('status_code') in [401, 403]:
            self.log_test("CLEAR-ALL AUTHENTICATION REQUIRED", True, 
                         f"Endpoint properly requires authentication (status: {result.get('status_code')})")
            return True
        else:
            self.log_test("CLEAR-ALL AUTHENTICATION REQUIRED", False, 
                         f"Endpoint should require authentication but returned status: {result.get('status_code')}", result)
            return False

    def cleanup_resources(self):
        """Clean up created test resources"""
        print("\n🧹 CLEANING UP TEST RESOURCES")
        cleanup_count = 0
        
        # Clean up tasks
        for task_id in self.created_resources.get('tasks', []):
            result = self.make_request('DELETE', f'/tasks/{task_id}', use_auth=True)
            if result.get('success'):
                cleanup_count += 1
                print(f"   ✅ Cleaned up task: {task_id}")
        
        # Clean up projects
        for project_id in self.created_resources.get('projects', []):
            result = self.make_request('DELETE', f'/projects/{project_id}', use_auth=True)
            if result.get('success'):
                cleanup_count += 1
                print(f"   ✅ Cleaned up project: {project_id}")
        
        # Clean up areas
        for area_id in self.created_resources.get('areas', []):
            result = self.make_request('DELETE', f'/areas/{area_id}', use_auth=True)
            if result.get('success'):
                cleanup_count += 1
                print(f"   ✅ Cleaned up area: {area_id}")
        
        # Clean up pillars
        for pillar_id in self.created_resources.get('pillars', []):
            result = self.make_request('DELETE', f'/pillars/{pillar_id}', use_auth=True)
            if result.get('success'):
                cleanup_count += 1
                print(f"   ✅ Cleaned up pillar: {pillar_id}")
        
        print(f"   ✅ Cleanup completed for {cleanup_count} resources")

    def run_all_tests(self):
        """Run all clear-all notification tests"""
        print("🔔 STARTING DELETE /api/notifications/clear-all ENDPOINT TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        test_results = []
        
        # Basic connectivity
        if not self.test_basic_connectivity():
            print("❌ Basic connectivity failed, aborting tests")
            return
        test_results.append(True)
        
        # User registration and login
        if not self.test_user_registration_and_login():
            print("❌ User registration/login failed, aborting tests")
            return
        test_results.append(True)
        
        # Test authentication requirement
        auth_result = self.test_authentication_required()
        test_results.append(auth_result)
        
        # Create test notifications
        if self.create_test_notifications(3):
            # Test clear-all with notifications present
            clear_with_data_result = self.test_clear_all_notifications_with_data()
            test_results.append(clear_with_data_result)
        else:
            test_results.append(False)
        
        # Test clear-all with no notifications
        clear_empty_result = self.test_clear_all_notifications_empty()
        test_results.append(clear_empty_result)
        
        # Print summary
        print("\n" + "=" * 80)
        print("🔔 DELETE /api/notifications/clear-all TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        
        passed_tests = sum(test_results)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("✅ DELETE /api/notifications/clear-all ENDPOINT: WORKING CORRECTLY")
            print("   The 404 error bug has been FIXED!")
        else:
            print("❌ DELETE /api/notifications/clear-all ENDPOINT: ISSUES DETECTED")
            print("   The 404 error bug may still exist!")
        
        print("=" * 80)
        
        # Cleanup
        self.cleanup_resources()
        
        return success_rate >= 80

if __name__ == "__main__":
    tester = ClearAllNotificationsTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)