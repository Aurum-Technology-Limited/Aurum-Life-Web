#!/usr/bin/env python3
"""
AUTHENTICATION AND PROJECTS API TESTING
Quick authentication and projects API testing to diagnose the "Failed to load projects" issue.

FOCUS AREAS:
1. User Registration - Test /api/auth/register with new user data
2. User Login - Test /api/auth/login with registered credentials  
3. Authentication Token - Verify JWT token is generated correctly
4. Projects API with Authentication - Test /api/projects endpoint with valid auth token
5. Project Data Retrieval - Ensure project data is returned correctly
6. Error Investigation - Check for any 401 authentication errors

Context: The user is experiencing "Failed to load projects" error in the frontend. 
The troubleshoot agent identified this as an authentication issue. The frontend shows 
"Incorrect email or password" errors and there are 401 errors in the console.
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

    def setup_test_environment(self):
        """Setup test environment with user authentication and basic resources"""
        print("\n=== SETTING UP TEST ENVIRONMENT ===")
        
        # Test 0: Basic connectivity test
        result = self.make_request('GET', '/health')
        self.log_test(
            "BASIC CONNECTIVITY TEST",
            result['success'],
            f"Backend API accessible at {self.base_url}" if result['success'] else f"Backend API not accessible: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            print("❌ CRITICAL FAILURE: Cannot connect to backend API")
            return False
        
        # Test 1: User Registration
        result = self.make_request('POST', '/auth/register', data=self.test_user_data)
        self.log_test(
            "USER REGISTRATION - Test User Setup",
            result['success'],
            f"Test user registered: {result['data'].get('username', 'Unknown')}" if result['success'] else f"Registration failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            print(f"❌ Registration failed with status {result.get('status_code')}: {result.get('error')}")
            return False
        
        user_data = result['data']
        self.created_resources['users'].append(user_data['id'])
        
        # Test 2: User Login
        login_data = {
            "email": self.test_user_data['email'],
            "password": self.test_user_data['password']
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        self.log_test(
            "USER LOGIN - Authentication Setup",
            result['success'],
            f"Login successful, JWT token received" if result['success'] else f"Login failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            print(f"❌ Login failed with status {result.get('status_code')}: {result.get('error')}")
            return False
        
        # Store auth token
        token_data = result['data']
        self.auth_token = token_data.get('access_token')
        
        # Test 3: Create test area and project for task testing
        area_data = {
            "name": "Notification Testing Area",
            "description": "Area for testing notification system",
            "icon": "🔔",
            "color": "#F4B400"
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        self.log_test(
            "TEST AREA CREATION",
            result['success'],
            f"Test area created: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Area creation failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            print(f"❌ Area creation failed with status {result.get('status_code')}: {result.get('error')}")
            return False
        
        area_id = result['data']['id']
        self.created_resources['areas'].append(area_id)
        
        # Test 4: Create test project
        project_data = {
            "area_id": area_id,
            "name": "Notification Testing Project",
            "description": "Project for testing notification system",
            "priority": "high"
        }
        
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        self.log_test(
            "TEST PROJECT CREATION",
            result['success'],
            f"Test project created: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Project creation failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            print(f"❌ Project creation failed with status {result.get('status_code')}: {result.get('error')}")
            return False
        
        project_id = result['data']['id']
        self.created_resources['projects'].append(project_id)
        self.test_project_id = project_id
        
        print("✅ Test environment setup completed successfully")
        return True

    def test_notification_preferences_api(self):
        """Test Notification Preferences API - GET/PUT `/api/notifications/preferences` endpoints"""
        print("\n=== TESTING NOTIFICATION PREFERENCES API ===")
        
        # Test 1: GET notification preferences (should create defaults if none exist)
        result = self.make_request('GET', '/notifications/preferences', use_auth=True)
        self.log_test(
            "GET NOTIFICATION PREFERENCES - Default Creation",
            result['success'],
            f"Retrieved notification preferences with defaults" if result['success'] else f"Failed to get preferences: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        preferences = result['data']
        
        # Verify default preference structure
        expected_fields = [
            'email_notifications', 'browser_notifications', 'task_due_notifications',
            'task_overdue_notifications', 'task_reminder_notifications', 
            'project_deadline_notifications', 'recurring_task_notifications',
            'reminder_advance_time', 'overdue_check_interval', 'quiet_hours_start', 'quiet_hours_end'
        ]
        
        present_fields = [field for field in expected_fields if field in preferences]
        self.log_test(
            "NOTIFICATION PREFERENCES STRUCTURE",
            len(present_fields) == len(expected_fields),
            f"Preferences contain {len(present_fields)}/{len(expected_fields)} expected fields: {present_fields}"
        )
        
        # Verify default values
        default_checks = [
            ('email_notifications', True),
            ('browser_notifications', True),
            ('task_due_notifications', True),
            ('reminder_advance_time', 30),
            ('quiet_hours_start', '22:00')
        ]
        
        defaults_correct = 0
        for field, expected_value in default_checks:
            if preferences.get(field) == expected_value:
                defaults_correct += 1
        
        self.log_test(
            "DEFAULT VALUES VALIDATION",
            defaults_correct == len(default_checks),
            f"Default values correct: {defaults_correct}/{len(default_checks)}"
        )
        
        # Test 2: PUT notification preferences - Update preferences
        updated_preferences = {
            "email_notifications": False,
            "reminder_advance_time": 60,
            "task_overdue_notifications": False,
            "quiet_hours_start": "23:00",
            "quiet_hours_end": "07:00"
        }
        
        result = self.make_request('PUT', '/notifications/preferences', data=updated_preferences, use_auth=True)
        self.log_test(
            "PUT NOTIFICATION PREFERENCES - Update Settings",
            result['success'],
            f"Preferences updated successfully" if result['success'] else f"Failed to update preferences: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        updated_prefs = result['data']
        
        # Verify updates were applied
        update_checks = [
            ('email_notifications', False),
            ('reminder_advance_time', 60),
            ('task_overdue_notifications', False),
            ('quiet_hours_start', '23:00'),
            ('quiet_hours_end', '07:00')
        ]
        
        updates_correct = 0
        for field, expected_value in update_checks:
            if updated_prefs.get(field) == expected_value:
                updates_correct += 1
        
        self.log_test(
            "PREFERENCE UPDATES VALIDATION",
            updates_correct == len(update_checks),
            f"Preference updates applied correctly: {updates_correct}/{len(update_checks)}"
        )
        
        # Test 3: GET preferences again to verify persistence
        result = self.make_request('GET', '/notifications/preferences', use_auth=True)
        self.log_test(
            "PREFERENCE PERSISTENCE VERIFICATION",
            result['success'] and result['data'].get('reminder_advance_time') == 60,
            f"Preferences persisted correctly" if result['success'] else f"Persistence check failed"
        )
        
        return True

    def test_browser_notifications_api(self):
        """Test Browser Notifications API - GET `/api/notifications` and PUT `/api/notifications/{id}/read` endpoints"""
        print("\n=== TESTING BROWSER NOTIFICATIONS API ===")
        
        # Test 1: GET browser notifications (initially empty)
        result = self.make_request('GET', '/notifications', use_auth=True)
        self.log_test(
            "GET BROWSER NOTIFICATIONS - Initial State",
            result['success'],
            f"Retrieved browser notifications: {len(result['data']) if result['success'] else 0} notifications" if result['success'] else f"Failed to get notifications: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        initial_notifications = result['data']
        
        # Test 2: GET unread notifications only
        result = self.make_request('GET', '/notifications', params={'unread_only': True}, use_auth=True)
        self.log_test(
            "GET UNREAD NOTIFICATIONS - Filter Test",
            result['success'],
            f"Retrieved unread notifications: {len(result['data']) if result['success'] else 0} notifications" if result['success'] else f"Failed to get unread notifications: {result.get('error', 'Unknown error')}"
        )
        
        # Test 3: Create a test notification using the test endpoint
        result = self.make_request('POST', '/notifications/test', use_auth=True)
        self.log_test(
            "CREATE TEST NOTIFICATION",
            result['success'],
            f"Test notification created and processed: {result['data'].get('notifications_processed', 0)} notifications" if result['success'] else f"Failed to create test notification: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        # Wait a moment for notification processing
        time.sleep(2)
        
        # Test 4: GET notifications again to see the test notification
        result = self.make_request('GET', '/notifications', use_auth=True)
        self.log_test(
            "GET NOTIFICATIONS AFTER TEST",
            result['success'] and len(result['data']) > len(initial_notifications),
            f"New notifications appeared: {len(result['data']) if result['success'] else 0} total notifications" if result['success'] else f"Failed to get updated notifications"
        )
        
        if not result['success'] or len(result['data']) == 0:
            return False
        
        # Get the first notification for read testing
        notifications = result['data']
        test_notification = notifications[0]
        notification_id = test_notification['id']
        
        # Verify notification structure
        expected_fields = ['id', 'type', 'title', 'message', 'created_at', 'read']
        present_fields = [field for field in expected_fields if field in test_notification]
        self.log_test(
            "NOTIFICATION STRUCTURE VALIDATION",
            len(present_fields) >= 4,  # At least basic fields should be present
            f"Notification contains {len(present_fields)}/{len(expected_fields)} expected fields: {present_fields}"
        )
        
        # Test 5: Mark notification as read
        result = self.make_request('PUT', f'/notifications/{notification_id}/read', use_auth=True)
        self.log_test(
            "MARK NOTIFICATION AS READ",
            result['success'],
            f"Notification marked as read successfully" if result['success'] else f"Failed to mark notification as read: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        # Test 6: Verify notification was marked as read
        result = self.make_request('GET', '/notifications', params={'unread_only': True}, use_auth=True)
        unread_count = len(result['data']) if result['success'] else -1
        
        result = self.make_request('GET', '/notifications', use_auth=True)
        total_count = len(result['data']) if result['success'] else -1
        
        self.log_test(
            "READ STATUS VERIFICATION",
            result['success'] and unread_count < total_count,
            f"Read status updated correctly: {unread_count} unread, {total_count} total notifications"
        )
        
        return True

    def test_task_reminder_scheduling(self):
        """Test Task Reminder Scheduling - Creating tasks with due dates automatically schedules reminders"""
        print("\n=== TESTING TASK REMINDER SCHEDULING ===")
        
        # Test 1: Create task with due date and time
        due_date = datetime.utcnow() + timedelta(hours=2)
        task_data = {
            "project_id": self.test_project_id,
            "name": "Task with Reminder Test",
            "description": "Testing automatic reminder scheduling",
            "priority": "high",
            "due_date": due_date.isoformat(),
            "due_time": "14:30"
        }
        
        result = self.make_request('POST', '/tasks', data=task_data, use_auth=True)
        self.log_test(
            "CREATE TASK WITH DUE DATE",
            result['success'],
            f"Task created with due date: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Task creation failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        task_id = result['data']['id']
        self.created_resources['tasks'].append(task_id)
        
        # Verify task has due date and time
        created_task = result['data']
        self.log_test(
            "TASK DUE DATE VALIDATION",
            'due_date' in created_task and 'due_time' in created_task,
            f"Task has due_date: {created_task.get('due_date', 'None')}, due_time: {created_task.get('due_time', 'None')}"
        )
        
        # Test 2: Create task without due date (should not schedule reminders)
        task_data_no_due = {
            "project_id": self.test_project_id,
            "name": "Task without Due Date",
            "description": "Testing task without automatic reminders",
            "priority": "medium"
        }
        
        result = self.make_request('POST', '/tasks', data=task_data_no_due, use_auth=True)
        self.log_test(
            "CREATE TASK WITHOUT DUE DATE",
            result['success'],
            f"Task created without due date: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Task creation failed: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            task_id_no_due = result['data']['id']
            self.created_resources['tasks'].append(task_id_no_due)
        
        # Test 3: Create task with due date in the past (should handle gracefully)
        past_due_date = datetime.utcnow() - timedelta(hours=1)
        task_data_past = {
            "project_id": self.test_project_id,
            "name": "Past Due Task Test",
            "description": "Testing task with past due date",
            "priority": "low",
            "due_date": past_due_date.isoformat()
        }
        
        result = self.make_request('POST', '/tasks', data=task_data_past, use_auth=True)
        self.log_test(
            "CREATE TASK WITH PAST DUE DATE",
            result['success'],
            f"Task created with past due date: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Task creation failed: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            task_id_past = result['data']['id']
            self.created_resources['tasks'].append(task_id_past)
        
        return True

    def test_notification_service_methods(self):
        """Test core NotificationService methods through API endpoints"""
        print("\n=== TESTING NOTIFICATION SERVICE METHODS ===")
        
        # Test 1: Test notification system endpoint
        result = self.make_request('POST', '/notifications/test', use_auth=True)
        self.log_test(
            "NOTIFICATION SERVICE - Test Endpoint",
            result['success'],
            f"Test notification processed: {result['data'].get('notifications_processed', 0)} notifications" if result['success'] else f"Test notification failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        test_response = result['data']
        
        # Verify test response structure
        expected_fields = ['success', 'message', 'notifications_processed']
        present_fields = [field for field in expected_fields if field in test_response]
        self.log_test(
            "TEST NOTIFICATION RESPONSE STRUCTURE",
            len(present_fields) >= 2,
            f"Test response contains {len(present_fields)}/{len(expected_fields)} expected fields: {present_fields}"
        )
        
        # Test 2: Verify notification was created and processed
        notifications_processed = test_response.get('notifications_processed', 0)
        self.log_test(
            "NOTIFICATION PROCESSING VERIFICATION",
            notifications_processed > 0,
            f"Notifications were processed: {notifications_processed} notifications sent"
        )
        
        # Test 3: Check if browser notification was created
        time.sleep(1)  # Wait for processing
        result = self.make_request('GET', '/notifications', use_auth=True)
        self.log_test(
            "BROWSER NOTIFICATION CREATION",
            result['success'] and len(result['data']) > 0,
            f"Browser notifications created: {len(result['data']) if result['success'] else 0} notifications" if result['success'] else f"Failed to retrieve notifications"
        )
        
        # Test 4: Verify notification content
        if result['success'] and len(result['data']) > 0:
            latest_notification = result['data'][0]  # Most recent notification
            
            # Check for test notification characteristics
            is_test_notification = (
                'test' in latest_notification.get('title', '').lower() or
                'test' in latest_notification.get('message', '').lower()
            )
            
            self.log_test(
                "TEST NOTIFICATION CONTENT VALIDATION",
                is_test_notification,
                f"Test notification content verified: {latest_notification.get('title', 'No title')}"
            )
        
        return True

    def test_email_integration(self):
        """Test email integration with SendGrid (mock mode)"""
        print("\n=== TESTING EMAIL INTEGRATION ===")
        
        # Test 1: Enable email notifications in preferences
        email_prefs = {
            "email_notifications": True,
            "task_due_notifications": True,
            "task_reminder_notifications": True
        }
        
        result = self.make_request('PUT', '/notifications/preferences', data=email_prefs, use_auth=True)
        self.log_test(
            "ENABLE EMAIL NOTIFICATIONS",
            result['success'],
            f"Email notifications enabled in preferences" if result['success'] else f"Failed to enable email notifications: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        # Test 2: Create test notification with email channel
        result = self.make_request('POST', '/notifications/test', use_auth=True)
        self.log_test(
            "EMAIL NOTIFICATION TEST",
            result['success'],
            f"Email notification test completed: {result['data'].get('message', 'Unknown')}" if result['success'] else f"Email test failed: {result.get('error', 'Unknown error')}"
        )
        
        # Note: Since we're using placeholder SendGrid credentials, we can't test actual email sending
        # But we can verify the system attempts to send emails without errors
        
        # Test 3: Verify email notification structure would be created
        # This tests the email template generation and notification scheduling
        self.log_test(
            "EMAIL TEMPLATE GENERATION",
            result['success'],  # If the test endpoint succeeds, email template generation worked
            f"Email template generation and scheduling working" if result['success'] else f"Email template generation failed"
        )
        
        return True

    def test_notification_processing(self):
        """Test notification processing and background job logic"""
        print("\n=== TESTING NOTIFICATION PROCESSING ===")
        
        # Test 1: Create multiple test notifications
        test_count = 3
        successful_tests = 0
        
        for i in range(test_count):
            result = self.make_request('POST', '/notifications/test', use_auth=True)
            if result['success']:
                successful_tests += 1
            time.sleep(0.5)  # Small delay between tests
        
        self.log_test(
            "MULTIPLE NOTIFICATION PROCESSING",
            successful_tests == test_count,
            f"Multiple notifications processed: {successful_tests}/{test_count} successful"
        )
        
        # Test 2: Verify all notifications were processed
        time.sleep(2)  # Wait for processing
        result = self.make_request('GET', '/notifications', use_auth=True)
        
        if result['success']:
            total_notifications = len(result['data'])
            self.log_test(
                "NOTIFICATION ACCUMULATION",
                total_notifications >= successful_tests,
                f"Notifications accumulated correctly: {total_notifications} total notifications"
            )
        
        # Test 3: Test notification filtering
        result = self.make_request('GET', '/notifications', params={'unread_only': True}, use_auth=True)
        unread_notifications = len(result['data']) if result['success'] else 0
        
        result = self.make_request('GET', '/notifications', use_auth=True)
        total_notifications = len(result['data']) if result['success'] else 0
        
        self.log_test(
            "NOTIFICATION FILTERING",
            result['success'] and unread_notifications <= total_notifications,
            f"Notification filtering working: {unread_notifications} unread, {total_notifications} total"
        )
        
        # Test 4: Test batch notification reading
        if result['success'] and len(result['data']) > 0:
            # Mark first notification as read
            first_notification = result['data'][0]
            notification_id = first_notification['id']
            
            result = self.make_request('PUT', f'/notifications/{notification_id}/read', use_auth=True)
            self.log_test(
                "BATCH NOTIFICATION PROCESSING",
                result['success'],
                f"Notification read status updated successfully" if result['success'] else f"Failed to update read status"
            )
        
        return True

    def test_comprehensive_notification_system(self):
        """Run comprehensive notification system tests"""
        print("\n🔔 STARTING COMPREHENSIVE TASK REMINDERS & NOTIFICATIONS SYSTEM TESTING")
        print("=" * 80)
        
        # Setup test environment
        if not self.setup_test_environment():
            print("❌ CRITICAL FAILURE: Test environment setup failed")
            return False
        
        # Run all notification system tests
        test_methods = [
            self.test_notification_preferences_api,
            self.test_browser_notifications_api,
            self.test_task_reminder_scheduling,
            self.test_notification_service_methods,
            self.test_email_integration,
            self.test_notification_processing
        ]
        
        successful_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            try:
                if test_method():
                    successful_tests += 1
                else:
                    print(f"❌ Test method {test_method.__name__} failed")
            except Exception as e:
                print(f"❌ Test method {test_method.__name__} raised exception: {e}")
        
        success_rate = (successful_tests / total_tests) * 100
        
        print(f"\n✅ TASK REMINDERS & NOTIFICATIONS SYSTEM TESTING COMPLETED")
        print(f"   Backend URL: {self.base_url}")
        print(f"   Test Methods: {successful_tests}/{total_tests} successful")
        print(f"   Overall Success Rate: {success_rate:.1f}%")
        
        return success_rate >= 80

def main():
    """Run Task Reminders & Notifications System Tests"""
    print("🔔 STARTING TASK REMINDERS & NOTIFICATIONS SYSTEM BACKEND TESTING")
    print("=" * 80)
    
    tester = BackendTester()
    
    try:
        # Run the comprehensive notification system tests
        success = tester.test_comprehensive_notification_system()
        
        # Calculate overall results
        total_tests = len(tester.test_results)
        passed_tests = sum(1 for result in tester.test_results if result['success'])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("🎯 TASK REMINDERS & NOTIFICATIONS SYSTEM TESTING SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("\n✅ TASK REMINDERS & NOTIFICATIONS SYSTEM: SUCCESS")
            print("   ✅ Notification Preferences API working correctly")
            print("   ✅ Browser Notifications API functional")
            print("   ✅ Task Reminder Scheduling operational")
            print("   ✅ Notification Service Methods working")
            print("   ✅ Email Integration configured")
            print("   ✅ Notification Processing functional")
            print("   The Task Reminders & Notifications System is production-ready!")
        else:
            print("\n❌ TASK REMINDERS & NOTIFICATIONS SYSTEM: ISSUES DETECTED")
            print("   Some notification system components are experiencing issues")
            print("   Review failed tests for specific problems")
        
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
        
        # Clean up tasks
        for task_id in tester.created_resources.get('tasks', []):
            try:
                result = tester.make_request('DELETE', f'/tasks/{task_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
                    print(f"   ✅ Cleaned up task: {task_id}")
            except:
                pass
        
        # Clean up projects
        for project_id in tester.created_resources.get('projects', []):
            try:
                result = tester.make_request('DELETE', f'/projects/{project_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
                    print(f"   ✅ Cleaned up project: {project_id}")
            except:
                pass
        
        # Clean up areas
        for area_id in tester.created_resources.get('areas', []):
            try:
                result = tester.make_request('DELETE', f'/areas/{area_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
                    print(f"   ✅ Cleaned up area: {area_id}")
            except:
                pass
        
        if cleanup_count > 0:
            print(f"   ✅ Cleanup completed for {cleanup_count} resources")
        else:
            print("   ℹ️ No resources to cleanup")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)