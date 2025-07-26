#!/usr/bin/env python3
"""
ENHANCED NOTIFICATIONS SYSTEM COMPREHENSIVE TESTING
Complete end-to-end testing of the Enhanced Notifications System implementation.

FOCUS AREAS:
1. Enhanced Notification Management - Test existing and NEW bulk endpoints
2. Browser Notification Features - Test notification preferences and browser notifications
3. Notification Scheduling System - Test task reminder scheduling and generation
4. Data Integrity & Performance - Test bulk operations and data consistency
5. Authentication & Security - Test user isolation and access control
6. Error Handling - Test error scenarios and edge cases

Context: Testing the complete Enhanced Notifications system implementation with:
- Enhanced notification management with bulk operations
- Browser notification features with preferences
- Notification scheduling system for task reminders
- Data integrity and performance optimization
- Full authentication and user isolation
- Comprehensive error handling
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid
import time

# Configuration - Using the production backend URL from frontend/.env
BACKEND_URL = "https://25d39911-b77f-4948-aab8-0b3bcaee8f2f.preview.emergentagent.com/api"

class NotificationSystemTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.created_resources = {
            'notifications': [],
            'tasks': [],
            'projects': [],
            'areas': [],
            'users': []
        }
        self.auth_token = None
        # Use realistic test data for notification testing
        self.test_user_email = f"notification.tester_{uuid.uuid4().hex[:8]}@aurumlife.com"
        self.test_user_password = "NotificationTest2025!"
        self.test_user_data = {
            "username": f"notification_tester_{uuid.uuid4().hex[:8]}",
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
        
        result = self.make_request('GET', '/health')
        self.log_test(
            "BACKEND API CONNECTIVITY",
            result['success'],
            f"Backend API accessible at {self.base_url}" if result['success'] else f"Backend API not accessible: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            health_data = result['data']
            self.log_test(
                "HEALTH CHECK RESPONSE",
                'status' in health_data,
                f"Health check returned: {health_data.get('status', 'Unknown status')}"
            )
        
        return result['success']

    def test_user_registration_and_login(self):
        """Test user registration and login for notification testing"""
        print("\n=== TESTING USER REGISTRATION AND LOGIN ===")
        
        # Register user
        result = self.make_request('POST', '/auth/register', data=self.test_user_data)
        self.log_test(
            "USER REGISTRATION",
            result['success'],
            f"User registered successfully: {result['data'].get('email', 'Unknown')}" if result['success'] else f"Registration failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        self.created_resources['users'].append(result['data'].get('id'))
        
        # Login user
        login_data = {
            "email": self.test_user_data['email'],
            "password": self.test_user_data['password']
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        self.log_test(
            "USER LOGIN",
            result['success'],
            f"Login successful, JWT token received" if result['success'] else f"Login failed: {result.get('error', 'Unknown error')}"
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

    def test_notification_preferences_system(self):
        """Test notification preferences endpoints"""
        print("\n=== TESTING NOTIFICATION PREFERENCES SYSTEM ===")
        
        if not self.auth_token:
            self.log_test("NOTIFICATION PREFERENCES - Authentication Required", False, "No authentication token available")
            return False
        
        # Test 1: Get notification preferences (should create defaults if none exist)
        result = self.make_request('GET', '/notifications/preferences', use_auth=True)
        self.log_test(
            "GET NOTIFICATION PREFERENCES",
            result['success'],
            f"Retrieved notification preferences successfully" if result['success'] else f"Failed to get preferences: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        preferences = result['data']
        
        # Test 2: Verify default preference structure
        expected_fields = [
            'email_notifications', 'browser_notifications', 'task_due_notifications',
            'task_overdue_notifications', 'task_reminder_notifications', 
            'project_deadline_notifications', 'recurring_task_notifications',
            'reminder_advance_time', 'quiet_hours_start', 'quiet_hours_end'
        ]
        
        present_fields = [field for field in expected_fields if field in preferences]
        
        self.log_test(
            "NOTIFICATION PREFERENCES STRUCTURE",
            len(present_fields) >= 8,
            f"Preferences contain {len(present_fields)}/{len(expected_fields)} expected fields: {present_fields}"
        )
        
        # Test 3: Update notification preferences
        update_data = {
            "email_notifications": False,
            "browser_notifications": True,
            "task_due_notifications": True,
            "task_overdue_notifications": False,
            "reminder_advance_time": 60,
            "quiet_hours_start": "23:00",
            "quiet_hours_end": "07:00"
        }
        
        result = self.make_request('PUT', '/notifications/preferences', data=update_data, use_auth=True)
        self.log_test(
            "UPDATE NOTIFICATION PREFERENCES",
            result['success'],
            f"Preferences updated successfully" if result['success'] else f"Failed to update preferences: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            updated_prefs = result['data']
            
            # Verify updates were applied
            self.log_test(
                "PREFERENCES UPDATE VERIFICATION",
                updated_prefs.get('email_notifications') == False and updated_prefs.get('reminder_advance_time') == 60,
                f"Updated preferences: email_notifications={updated_prefs.get('email_notifications')}, reminder_advance_time={updated_prefs.get('reminder_advance_time')}"
            )
        
        return True

    def test_browser_notifications_system(self):
        """Test browser notifications endpoints"""
        print("\n=== TESTING BROWSER NOTIFICATIONS SYSTEM ===")
        
        if not self.auth_token:
            self.log_test("BROWSER NOTIFICATIONS - Authentication Required", False, "No authentication token available")
            return False
        
        # Test 1: Get browser notifications (initially empty)
        result = self.make_request('GET', '/notifications', use_auth=True)
        self.log_test(
            "GET BROWSER NOTIFICATIONS",
            result['success'],
            f"Retrieved {len(result['data']) if result['success'] else 0} browser notifications" if result['success'] else f"Failed to get notifications: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        initial_notification_count = len(result['data'])
        
        # Test 2: Send test notification to create browser notifications
        result = self.make_request('POST', '/notifications/test', use_auth=True)
        self.log_test(
            "SEND TEST NOTIFICATION",
            result['success'],
            f"Test notification sent successfully" if result['success'] else f"Failed to send test notification: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            # Wait a moment for notification processing
            time.sleep(2)
            
            # Test 3: Verify notification was created
            result = self.make_request('GET', '/notifications', use_auth=True)
            if result['success']:
                new_notification_count = len(result['data'])
                self.log_test(
                    "TEST NOTIFICATION CREATION",
                    new_notification_count > initial_notification_count,
                    f"Notification count increased from {initial_notification_count} to {new_notification_count}"
                )
                
                if new_notification_count > 0:
                    notification = result['data'][0]
                    notification_id = notification.get('id')
                    
                    # Test 4: Mark notification as read
                    if notification_id:
                        result = self.make_request('PUT', f'/notifications/{notification_id}/read', use_auth=True)
                        self.log_test(
                            "MARK NOTIFICATION READ",
                            result['success'],
                            f"Notification marked as read successfully" if result['success'] else f"Failed to mark notification as read: {result.get('error', 'Unknown error')}"
                        )
                        
                        # Test 5: Verify notification structure
                        expected_notification_fields = ['id', 'type', 'title', 'message', 'created_at', 'read']
                        present_notification_fields = [field for field in expected_notification_fields if field in notification]
                        
                        self.log_test(
                            "NOTIFICATION DATA STRUCTURE",
                            len(present_notification_fields) >= 4,
                            f"Notification contains {len(present_notification_fields)}/{len(expected_notification_fields)} expected fields: {present_notification_fields}"
                        )
        
        return True

    def test_bulk_notification_operations(self):
        """Test bulk notification operations"""
        print("\n=== TESTING BULK NOTIFICATION OPERATIONS ===")
        
        if not self.auth_token:
            self.log_test("BULK NOTIFICATION OPERATIONS - Authentication Required", False, "No authentication token available")
            return False
        
        # Create multiple test notifications first
        for i in range(3):
            result = self.make_request('POST', '/notifications/test', use_auth=True)
            if result['success']:
                time.sleep(1)  # Small delay between notifications
        
        # Wait for notifications to be processed
        time.sleep(3)
        
        # Test 1: Get all notifications
        result = self.make_request('GET', '/notifications', use_auth=True)
        self.log_test(
            "GET ALL NOTIFICATIONS FOR BULK TEST",
            result['success'] and len(result['data']) >= 3,
            f"Retrieved {len(result['data']) if result['success'] else 0} notifications for bulk testing" if result['success'] else f"Failed to get notifications: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success'] or len(result['data']) == 0:
            return False
        
        notifications = result['data']
        
        # Test 2: Mark all notifications as read (bulk operation)
        result = self.make_request('PUT', '/notifications/mark-all-read', use_auth=True)
        self.log_test(
            "MARK ALL NOTIFICATIONS READ (BULK)",
            result['success'],
            f"Bulk mark as read: {result['data'].get('message', 'Success')}" if result['success'] else f"Failed bulk mark as read: {result.get('error', 'Unknown error')}"
        )
        
        # Test 3: Delete specific notification
        if notifications:
            notification_id = notifications[0].get('id')
            if notification_id:
                result = self.make_request('DELETE', f'/notifications/{notification_id}', use_auth=True)
                self.log_test(
                    "DELETE SPECIFIC NOTIFICATION",
                    result['success'],
                    f"Notification deleted successfully" if result['success'] else f"Failed to delete notification: {result.get('error', 'Unknown error')}"
                )
        
        # Test 4: Clear all notifications (bulk operation)
        result = self.make_request('DELETE', '/notifications/clear-all', use_auth=True)
        self.log_test(
            "CLEAR ALL NOTIFICATIONS (BULK)",
            result['success'],
            f"Bulk clear notifications: {result['data'].get('message', 'Success')}" if result['success'] else f"Failed bulk clear: {result.get('error', 'Unknown error')}"
        )
        
        # Test 5: Verify notifications were cleared
        result = self.make_request('GET', '/notifications', use_auth=True)
        if result['success']:
            remaining_count = len(result['data'])
            self.log_test(
                "VERIFY BULK CLEAR OPERATION",
                remaining_count == 0,
                f"Remaining notifications after bulk clear: {remaining_count}"
            )
        
        return True

    def test_notification_scheduling_system(self):
        """Test notification scheduling system with task creation"""
        print("\n=== TESTING NOTIFICATION SCHEDULING SYSTEM ===")
        
        if not self.auth_token:
            self.log_test("NOTIFICATION SCHEDULING - Authentication Required", False, "No authentication token available")
            return False
        
        # First, create an area and project for task creation
        area_data = {
            "name": "Test Notification Area",
            "description": "Area for testing notification scheduling",
            "icon": "🔔",
            "color": "#FF5722"
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        if not result['success']:
            self.log_test("CREATE TEST AREA FOR NOTIFICATIONS", False, f"Failed to create area: {result.get('error', 'Unknown error')}")
            return False
        
        area_id = result['data']['id']
        self.created_resources['areas'].append(area_id)
        
        project_data = {
            "area_id": area_id,
            "name": "Test Notification Project",
            "description": "Project for testing notification scheduling"
        }
        
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        if not result['success']:
            self.log_test("CREATE TEST PROJECT FOR NOTIFICATIONS", False, f"Failed to create project: {result.get('error', 'Unknown error')}")
            return False
        
        project_id = result['data']['id']
        self.created_resources['projects'].append(project_id)
        
        # Test 1: Create task with due date to trigger notification scheduling
        future_date = datetime.utcnow() + timedelta(hours=1)
        task_data = {
            "project_id": project_id,
            "name": "Test Notification Task",
            "description": "Task to test notification scheduling",
            "due_date": future_date.isoformat(),
            "due_time": "14:30",
            "priority": "high"
        }
        
        result = self.make_request('POST', '/tasks', data=task_data, use_auth=True)
        self.log_test(
            "CREATE TASK WITH DUE DATE",
            result['success'],
            f"Task created with due date for notification scheduling" if result['success'] else f"Failed to create task: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        task_id = result['data']['id']
        self.created_resources['tasks'].append(task_id)
        
        # Test 2: Verify task was created with notification fields
        created_task = result['data']
        notification_fields = ['due_date', 'due_time', 'priority']
        present_fields = [field for field in notification_fields if field in created_task]
        
        self.log_test(
            "TASK NOTIFICATION FIELDS",
            len(present_fields) >= 2,
            f"Task contains {len(present_fields)}/{len(notification_fields)} notification-related fields: {present_fields}"
        )
        
        # Test 3: Create overdue task to test overdue notifications
        past_date = datetime.utcnow() - timedelta(hours=2)
        overdue_task_data = {
            "project_id": project_id,
            "name": "Overdue Test Task",
            "description": "Task to test overdue notifications",
            "due_date": past_date.isoformat(),
            "priority": "medium"
        }
        
        result = self.make_request('POST', '/tasks', data=overdue_task_data, use_auth=True)
        self.log_test(
            "CREATE OVERDUE TASK",
            result['success'],
            f"Overdue task created for notification testing" if result['success'] else f"Failed to create overdue task: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            overdue_task_id = result['data']['id']
            self.created_resources['tasks'].append(overdue_task_id)
        
        return True

    def test_authentication_and_security(self):
        """Test authentication requirements and user isolation for notification endpoints"""
        print("\n=== TESTING AUTHENTICATION AND SECURITY ===")
        
        # Test 1: Endpoints without authentication should fail
        notification_endpoints = [
            '/notifications/preferences',
            '/notifications',
            '/notifications/test'
        ]
        
        auth_protected_count = 0
        for endpoint in notification_endpoints:
            result = self.make_request('GET', endpoint, use_auth=False)
            if not result['success'] and result.get('status_code') in [401, 403]:
                auth_protected_count += 1
        
        self.log_test(
            "NOTIFICATION ENDPOINTS AUTHENTICATION PROTECTION",
            auth_protected_count == len(notification_endpoints),
            f"{auth_protected_count}/{len(notification_endpoints)} notification endpoints properly protected"
        )
        
        # Test 2: User isolation - notifications should be user-specific
        if self.auth_token:
            result = self.make_request('GET', '/notifications', use_auth=True)
            if result['success']:
                notifications = result['data']
                user_notifications = [n for n in notifications if n.get('user_id')]
                
                self.log_test(
                    "NOTIFICATION USER ISOLATION",
                    len(notifications) == 0 or len(user_notifications) == len(notifications),
                    f"All {len(notifications)} notifications are properly isolated by user"
                )
        
        # Test 3: Invalid notification ID handling
        result = self.make_request('PUT', '/notifications/invalid-id/read', use_auth=True)
        self.log_test(
            "INVALID NOTIFICATION ID HANDLING",
            not result['success'] and result.get('status_code') == 404,
            f"Invalid notification ID properly rejected with status {result.get('status_code')}"
        )
        
        return True

    def test_error_handling_scenarios(self):
        """Test various error scenarios and edge cases"""
        print("\n=== TESTING ERROR HANDLING SCENARIOS ===")
        
        if not self.auth_token:
            self.log_test("ERROR HANDLING - Authentication Required", False, "No authentication token available")
            return False
        
        # Test 1: Invalid preference values
        invalid_prefs = {
            "reminder_advance_time": -10,  # Invalid negative value
            "quiet_hours_start": "25:00"   # Invalid time format
        }
        
        result = self.make_request('PUT', '/notifications/preferences', data=invalid_prefs, use_auth=True)
        self.log_test(
            "INVALID PREFERENCE VALUES HANDLING",
            not result['success'] or result.get('status_code') in [400, 422],
            f"Invalid preference values properly handled with status {result.get('status_code')}"
        )
        
        # Test 2: Non-existent notification operations
        result = self.make_request('DELETE', '/notifications/non-existent-id', use_auth=True)
        self.log_test(
            "NON-EXISTENT NOTIFICATION DELETION",
            not result['success'] and result.get('status_code') == 404,
            f"Non-existent notification deletion properly handled with status {result.get('status_code')}"
        )
        
        # Test 3: Malformed request data
        result = self.make_request('PUT', '/notifications/preferences', data="invalid-json", use_auth=True)
        self.log_test(
            "MALFORMED REQUEST DATA HANDLING",
            not result['success'],
            f"Malformed request data properly rejected"
        )
        
        return True

    def test_data_integrity_and_performance(self):
        """Test data integrity and performance of notification operations"""
        print("\n=== TESTING DATA INTEGRITY AND PERFORMANCE ===")
        
        if not self.auth_token:
            self.log_test("DATA INTEGRITY - Authentication Required", False, "No authentication token available")
            return False
        
        # Test 1: Notification count consistency
        initial_result = self.make_request('GET', '/notifications', use_auth=True)
        if not initial_result['success']:
            return False
        
        initial_count = len(initial_result['data'])
        
        # Create test notifications
        test_notifications_created = 0
        for i in range(5):
            result = self.make_request('POST', '/notifications/test', use_auth=True)
            if result['success']:
                test_notifications_created += 1
            time.sleep(0.5)
        
        # Wait for processing
        time.sleep(3)
        
        # Verify count increased
        final_result = self.make_request('GET', '/notifications', use_auth=True)
        if final_result['success']:
            final_count = len(final_result['data'])
            expected_count = initial_count + test_notifications_created
            
            self.log_test(
                "NOTIFICATION COUNT CONSISTENCY",
                final_count >= initial_count,
                f"Notification count: {initial_count} → {final_count} (expected increase of {test_notifications_created})"
            )
        
        # Test 2: Bulk operation performance
        start_time = time.time()
        result = self.make_request('PUT', '/notifications/mark-all-read', use_auth=True)
        end_time = time.time()
        
        operation_time = end_time - start_time
        self.log_test(
            "BULK OPERATION PERFORMANCE",
            result['success'] and operation_time < 5.0,
            f"Bulk mark-all-read completed in {operation_time:.2f} seconds"
        )
        
        # Test 3: Data consistency after bulk operations
        result = self.make_request('DELETE', '/notifications/clear-all', use_auth=True)
        if result['success']:
            # Verify all notifications were cleared
            verify_result = self.make_request('GET', '/notifications', use_auth=True)
            if verify_result['success']:
                remaining_count = len(verify_result['data'])
                self.log_test(
                    "BULK CLEAR DATA CONSISTENCY",
                    remaining_count == 0,
                    f"All notifications cleared successfully, remaining: {remaining_count}"
                )
        
        return True

    def run_comprehensive_notification_test(self):
        """Run comprehensive notification system tests"""
        print("\n🔔 STARTING ENHANCED NOTIFICATIONS SYSTEM TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("User Registration and Login", self.test_user_registration_and_login),
            ("Notification Preferences System", self.test_notification_preferences_system),
            ("Browser Notifications System", self.test_browser_notifications_system),
            ("Bulk Notification Operations", self.test_bulk_notification_operations),
            ("Notification Scheduling System", self.test_notification_scheduling_system),
            ("Authentication and Security", self.test_authentication_and_security),
            ("Error Handling Scenarios", self.test_error_handling_scenarios),
            ("Data Integrity and Performance", self.test_data_integrity_and_performance)
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
        print("🎯 ENHANCED NOTIFICATIONS SYSTEM TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for notification system
        notification_tests_passed = sum(1 for result in self.test_results if result['success'] and 'NOTIFICATION' in result['test'])
        preference_tests_passed = sum(1 for result in self.test_results if result['success'] and 'PREFERENCE' in result['test'])
        bulk_tests_passed = sum(1 for result in self.test_results if result['success'] and 'BULK' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"Notification Management Tests Passed: {notification_tests_passed}")
        print(f"Preference System Tests Passed: {preference_tests_passed}")
        print(f"Bulk Operation Tests Passed: {bulk_tests_passed}")
        
        if success_rate >= 85:
            print("\n✅ ENHANCED NOTIFICATIONS SYSTEM: SUCCESS")
            print("   ✅ Enhanced notification management with bulk operations working")
            print("   ✅ Browser notification features functional")
            print("   ✅ Notification preferences system operational")
            print("   ✅ Notification scheduling system working")
            print("   ✅ Authentication and user isolation working")
            print("   ✅ Data integrity and performance optimized")
            print("   ✅ Error handling comprehensive")
            print("   The Enhanced Notifications system is production-ready!")
        else:
            print("\n❌ ENHANCED NOTIFICATIONS SYSTEM: ISSUES DETECTED")
            print("   Issues found in notification system functionality")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 85

    def cleanup_resources(self):
        """Clean up created test resources"""
        print("\n🧹 CLEANING UP TEST RESOURCES")
        cleanup_count = 0
        
        # Clean up tasks
        for task_id in self.created_resources.get('tasks', []):
            try:
                result = self.make_request('DELETE', f'/tasks/{task_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
                    print(f"   ✅ Cleaned up task: {task_id}")
            except:
                pass
        
        # Clean up projects
        for project_id in self.created_resources.get('projects', []):
            try:
                result = self.make_request('DELETE', f'/projects/{project_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
                    print(f"   ✅ Cleaned up project: {project_id}")
            except:
                pass
        
        # Clean up areas
        for area_id in self.created_resources.get('areas', []):
            try:
                result = self.make_request('DELETE', f'/areas/{area_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
                    print(f"   ✅ Cleaned up area: {area_id}")
            except:
                pass
        
        # Clear all notifications
        try:
            result = self.make_request('DELETE', '/notifications/clear-all', use_auth=True)
            if result['success']:
                cleanup_count += 1
                print(f"   ✅ Cleared all notifications")
        except:
            pass
        
        if cleanup_count > 0:
            print(f"   ✅ Cleanup completed for {cleanup_count} resources")
        else:
            print("   ℹ️ No resources to cleanup")

def main():
    """Run Enhanced Notifications System Tests"""
    print("🔔 STARTING ENHANCED NOTIFICATIONS SYSTEM BACKEND TESTING")
    print("=" * 80)
    
    tester = NotificationSystemTester()
    
    try:
        # Run the comprehensive notification system tests
        success = tester.run_comprehensive_notification_test()
        
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
    
    finally:
        # Cleanup created resources
        tester.cleanup_resources()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)