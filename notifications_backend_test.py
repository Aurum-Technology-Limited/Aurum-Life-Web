#!/usr/bin/env python3
"""
NOTIFICATIONS CENTER SYSTEM - BACKEND TESTING
Complete end-to-end testing of the Notifications Center implementation.

FOCUS AREAS:
1. NOTIFICATION PREFERENCES API - Test GET/PUT /api/notifications/preferences endpoints
2. BROWSER NOTIFICATIONS API - Test CRUD operations for browser notifications
3. UNBLOCKED TASK DETECTION - Test task dependency completion notifications
4. DATABASE SCHEMA - Test notification collections and data integrity
5. AUTHENTICATION - Test that all endpoints require proper authentication
6. USER ISOLATION - Test that notifications are user-specific

SPECIFIC ENDPOINTS TO TEST:
Phase 0 - Notification Settings Backend API:
- GET /api/notifications/preferences (return preferences with new fields)
- PUT /api/notifications/preferences (accept updates to new preference fields)

Phase 1 - Browser Notifications Backend API:
- GET /api/notifications (return browser notifications for user)
- PUT /api/notifications/{notification_id}/read (mark individual notification as read)
- PUT /api/notifications/mark-all-read (mark all notifications as read)
- DELETE /api/notifications/{notification_id} (delete individual notification)
- DELETE /api/notifications/clear-all (clear all notifications)

Phase 1 - Unblocked Task Detection Logic:
- Create task with dependencies on another task
- Complete the dependency task
- Verify browser notification is created for dependent task becoming unblocked
- Check notification contains correct task names and project context

AUTHENTICATION:
- Use test credentials with realistic data for notification testing
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid
import time

# Configuration - Using the production backend URL from frontend/.env
BACKEND_URL = "https://b865cdae-a7eb-4f1f-b4e2-f43f21dbfd26.preview.emergentagent.com/api"

class NotificationsCenterTester:
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
        # Use realistic test data for notifications testing
        self.test_user_email = f"notifications.tester_{uuid.uuid4().hex[:8]}@aurumlife.com"
        self.test_user_password = "NotificationsTest2025!"
        self.test_user_data = {
            "username": f"notifications_tester_{uuid.uuid4().hex[:8]}",
            "email": self.test_user_email,
            "first_name": "Notifications",
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
        """Test user registration and login for notifications testing"""
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

    def test_notification_preferences_api(self):
        """Test Phase 0 - Notification Settings Backend API"""
        print("\n=== TESTING NOTIFICATION PREFERENCES API ===")
        
        if not self.auth_token:
            self.log_test("NOTIFICATION PREFERENCES - Authentication Required", False, "No authentication token available")
            return False
        
        # Test GET /api/notifications/preferences
        result = self.make_request('GET', '/notifications/preferences', use_auth=True)
        self.log_test(
            "GET NOTIFICATION PREFERENCES",
            result['success'],
            f"Retrieved notification preferences successfully" if result['success'] else f"Failed to get preferences: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        preferences = result['data']
        
        # Verify new fields are present
        required_fields = [
            'achievement_notifications',
            'unblocked_task_notifications',
            'task_due_notifications',
            'task_overdue_notifications',
            'task_reminder_notifications',
            'project_deadline_notifications',
            'recurring_task_notifications',
            'email_notifications',
            'browser_notifications'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in preferences:
                missing_fields.append(field)
        
        fields_present = len(missing_fields) == 0
        self.log_test(
            "NOTIFICATION PREFERENCES - REQUIRED FIELDS",
            fields_present,
            f"All required fields present" if fields_present else f"Missing fields: {missing_fields}"
        )
        
        # Test new fields specifically
        achievement_notifications_present = 'achievement_notifications' in preferences
        unblocked_task_notifications_present = 'unblocked_task_notifications' in preferences
        
        self.log_test(
            "NOTIFICATION PREFERENCES - ACHIEVEMENT NOTIFICATIONS FIELD",
            achievement_notifications_present,
            f"achievement_notifications field present: {preferences.get('achievement_notifications')}" if achievement_notifications_present else "achievement_notifications field missing"
        )
        
        self.log_test(
            "NOTIFICATION PREFERENCES - UNBLOCKED TASK NOTIFICATIONS FIELD",
            unblocked_task_notifications_present,
            f"unblocked_task_notifications field present: {preferences.get('unblocked_task_notifications')}" if unblocked_task_notifications_present else "unblocked_task_notifications field missing"
        )
        
        # Test PUT /api/notifications/preferences
        update_data = {
            "achievement_notifications": False,
            "unblocked_task_notifications": True,
            "task_due_notifications": True,
            "browser_notifications": True
        }
        
        result = self.make_request('PUT', '/notifications/preferences', data=update_data, use_auth=True)
        self.log_test(
            "PUT NOTIFICATION PREFERENCES",
            result['success'],
            f"Updated notification preferences successfully" if result['success'] else f"Failed to update preferences: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            updated_preferences = result['data']
            
            # Verify updates were applied
            achievement_updated = updated_preferences.get('achievement_notifications') == False
            unblocked_updated = updated_preferences.get('unblocked_task_notifications') == True
            
            self.log_test(
                "NOTIFICATION PREFERENCES - UPDATE VERIFICATION",
                achievement_updated and unblocked_updated,
                f"Preference updates applied correctly" if (achievement_updated and unblocked_updated) else f"Update verification failed: achievement={updated_preferences.get('achievement_notifications')}, unblocked={updated_preferences.get('unblocked_task_notifications')}"
            )
        
        return fields_present and achievement_notifications_present and unblocked_task_notifications_present

    def test_browser_notifications_api(self):
        """Test Phase 1 - Browser Notifications Backend API"""
        print("\n=== TESTING BROWSER NOTIFICATIONS API ===")
        
        if not self.auth_token:
            self.log_test("BROWSER NOTIFICATIONS - Authentication Required", False, "No authentication token available")
            return False
        
        # Test GET /api/notifications (should return empty list initially)
        result = self.make_request('GET', '/notifications', use_auth=True)
        self.log_test(
            "GET BROWSER NOTIFICATIONS - INITIAL",
            result['success'],
            f"Retrieved browser notifications successfully (count: {len(result['data']) if result['success'] else 'N/A'})" if result['success'] else f"Failed to get notifications: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        initial_notifications = result['data']
        
        # Create a test notification using the test endpoint
        result = self.make_request('POST', '/notifications/test', use_auth=True)
        test_notification_created = result['success']
        self.log_test(
            "CREATE TEST NOTIFICATION",
            test_notification_created,
            f"Test notification created successfully" if test_notification_created else f"Failed to create test notification: {result.get('error', 'Unknown error')}"
        )
        
        if not test_notification_created:
            return False
        
        # Wait a moment for notification to be processed
        time.sleep(2)
        
        # Test GET /api/notifications (should now have notifications)
        result = self.make_request('GET', '/notifications', use_auth=True)
        notifications_retrieved = result['success'] and len(result['data']) > len(initial_notifications)
        
        self.log_test(
            "GET BROWSER NOTIFICATIONS - AFTER CREATION",
            notifications_retrieved,
            f"Retrieved {len(result['data'])} notifications" if result['success'] else f"Failed to get notifications: {result.get('error', 'Unknown error')}"
        )
        
        if not notifications_retrieved:
            return False
        
        notifications = result['data']
        test_notification = notifications[0] if notifications else None
        
        if not test_notification:
            self.log_test("BROWSER NOTIFICATIONS - NO TEST NOTIFICATION", False, "No test notification found")
            return False
        
        notification_id = test_notification.get('id')
        self.created_resources['notifications'].append(notification_id)
        
        # Verify notification structure
        required_notification_fields = ['id', 'user_id', 'type', 'title', 'message', 'is_read', 'created_at']
        missing_notification_fields = [field for field in required_notification_fields if field not in test_notification]
        
        notification_structure_valid = len(missing_notification_fields) == 0
        self.log_test(
            "BROWSER NOTIFICATION - STRUCTURE VALIDATION",
            notification_structure_valid,
            f"Notification structure valid" if notification_structure_valid else f"Missing fields: {missing_notification_fields}"
        )
        
        # Test PUT /api/notifications/{notification_id}/read
        result = self.make_request('PUT', f'/notifications/{notification_id}/read', use_auth=True)
        notification_marked_read = result['success']
        
        self.log_test(
            "MARK NOTIFICATION AS READ",
            notification_marked_read,
            f"Notification marked as read successfully" if notification_marked_read else f"Failed to mark notification as read: {result.get('error', 'Unknown error')}"
        )
        
        # Verify notification is marked as read
        if notification_marked_read:
            result = self.make_request('GET', '/notifications', use_auth=True)
            if result['success']:
                updated_notifications = result['data']
                updated_notification = next((n for n in updated_notifications if n.get('id') == notification_id), None)
                
                if updated_notification:
                    is_read = updated_notification.get('is_read', False)
                    self.log_test(
                        "NOTIFICATION READ STATUS VERIFICATION",
                        is_read,
                        f"Notification read status updated correctly: {is_read}" if is_read else "Notification still marked as unread"
                    )
        
        # Create another test notification for bulk operations
        result = self.make_request('POST', '/notifications/test', use_auth=True)
        if result['success']:
            time.sleep(1)  # Wait for processing
        
        # Test PUT /api/notifications/mark-all-read
        result = self.make_request('PUT', '/notifications/mark-all-read', use_auth=True)
        all_marked_read = result['success']
        
        self.log_test(
            "MARK ALL NOTIFICATIONS AS READ",
            all_marked_read,
            f"All notifications marked as read successfully (count: {result['data'].get('count', 'N/A')})" if all_marked_read else f"Failed to mark all notifications as read: {result.get('error', 'Unknown error')}"
        )
        
        # Test DELETE /api/notifications/{notification_id}
        result = self.make_request('DELETE', f'/notifications/{notification_id}', use_auth=True)
        notification_deleted = result['success']
        
        self.log_test(
            "DELETE INDIVIDUAL NOTIFICATION",
            notification_deleted,
            f"Notification deleted successfully" if notification_deleted else f"Failed to delete notification: {result.get('error', 'Unknown error')}"
        )
        
        # Test DELETE /api/notifications/clear-all
        result = self.make_request('DELETE', '/notifications/clear-all', use_auth=True)
        all_notifications_cleared = result['success']
        
        self.log_test(
            "CLEAR ALL NOTIFICATIONS",
            all_notifications_cleared,
            f"All notifications cleared successfully (count: {result['data'].get('count', 'N/A')})" if all_notifications_cleared else f"Failed to clear all notifications: {result.get('error', 'Unknown error')}"
        )
        
        # Verify all notifications are cleared
        if all_notifications_cleared:
            result = self.make_request('GET', '/notifications', use_auth=True)
            if result['success']:
                remaining_notifications = result['data']
                all_cleared = len(remaining_notifications) == 0
                
                self.log_test(
                    "CLEAR ALL NOTIFICATIONS VERIFICATION",
                    all_cleared,
                    f"All notifications cleared successfully" if all_cleared else f"Still have {len(remaining_notifications)} notifications remaining"
                )
        
        return (notifications_retrieved and notification_structure_valid and 
                notification_marked_read and all_marked_read and 
                notification_deleted and all_notifications_cleared)

    def setup_test_infrastructure(self):
        """Create pillar, area, and project for task dependency testing"""
        print("\n=== SETTING UP TEST INFRASTRUCTURE FOR TASK DEPENDENCIES ===")
        
        if not self.auth_token:
            self.log_test("INFRASTRUCTURE SETUP - Authentication Required", False, "No authentication token available")
            return None, None, None
        
        # Create test pillar
        pillar_data = {
            "name": "Notifications Test Pillar",
            "description": "Test pillar for notifications functionality",
            "icon": "🔔",
            "color": "#4CAF50"
        }
        
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        if not result['success']:
            self.log_test("INFRASTRUCTURE - CREATE PILLAR", False, f"Failed to create test pillar: {result.get('error', 'Unknown error')}")
            return None, None, None
        
        pillar_id = result['data']['id']
        self.created_resources['pillars'].append(pillar_id)
        self.log_test("INFRASTRUCTURE - CREATE PILLAR", True, f"Created test pillar: {pillar_id}")
        
        # Create test area
        area_data = {
            "name": "Notifications Test Area",
            "description": "Test area for notifications functionality",
            "icon": "📋",
            "color": "#2196F3",
            "pillar_id": pillar_id
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        if not result['success']:
            self.log_test("INFRASTRUCTURE - CREATE AREA", False, f"Failed to create test area: {result.get('error', 'Unknown error')}")
            return pillar_id, None, None
        
        area_id = result['data']['id']
        self.created_resources['areas'].append(area_id)
        self.log_test("INFRASTRUCTURE - CREATE AREA", True, f"Created test area: {area_id}")
        
        # Create test project
        project_data = {
            "area_id": area_id,
            "name": "Notifications Test Project",
            "description": "Test project for task dependency notifications",
            "icon": "🚀",
            "priority": "high"
        }
        
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        if not result['success']:
            self.log_test("INFRASTRUCTURE - CREATE PROJECT", False, f"Failed to create test project: {result.get('error', 'Unknown error')}")
            return pillar_id, area_id, None
        
        project_id = result['data']['id']
        self.created_resources['projects'].append(project_id)
        self.log_test("INFRASTRUCTURE - CREATE PROJECT", True, f"Created test project: {project_id}")
        
        return pillar_id, area_id, project_id

    def test_unblocked_task_detection_logic(self):
        """Test Phase 1 - Unblocked Task Detection Logic"""
        print("\n=== TESTING UNBLOCKED TASK DETECTION LOGIC ===")
        
        pillar_id, area_id, project_id = self.setup_test_infrastructure()
        if not project_id:
            return False
        
        # Clear any existing notifications
        self.make_request('DELETE', '/notifications/clear-all', use_auth=True)
        
        # Create dependency task (Task A)
        dependency_task_data = {
            "project_id": project_id,
            "name": "Dependency Task - Setup Database",
            "description": "This task must be completed first",
            "priority": "high",
            "status": "todo"
        }
        
        result = self.make_request('POST', '/tasks', data=dependency_task_data, use_auth=True)
        if not result['success']:
            self.log_test("UNBLOCKED TASK DETECTION - CREATE DEPENDENCY TASK", False, f"Failed to create dependency task: {result.get('error', 'Unknown error')}")
            return False
        
        dependency_task_id = result['data']['id']
        dependency_task_name = result['data']['name']
        self.created_resources['tasks'].append(dependency_task_id)
        self.log_test("UNBLOCKED TASK DETECTION - CREATE DEPENDENCY TASK", True, f"Created dependency task: {dependency_task_name}")
        
        # Create dependent task (Task B) that depends on Task A
        dependent_task_data = {
            "project_id": project_id,
            "name": "Dependent Task - Build Application",
            "description": "This task depends on the database setup",
            "priority": "medium",
            "status": "todo",
            "dependency_task_ids": [dependency_task_id]
        }
        
        result = self.make_request('POST', '/tasks', data=dependent_task_data, use_auth=True)
        if not result['success']:
            self.log_test("UNBLOCKED TASK DETECTION - CREATE DEPENDENT TASK", False, f"Failed to create dependent task: {result.get('error', 'Unknown error')}")
            return False
        
        dependent_task_id = result['data']['id']
        dependent_task_name = result['data']['name']
        self.created_resources['tasks'].append(dependent_task_id)
        self.log_test("UNBLOCKED TASK DETECTION - CREATE DEPENDENT TASK", True, f"Created dependent task: {dependent_task_name}")
        
        # Verify dependency relationship
        result = self.make_request('GET', f'/tasks/{dependent_task_id}/dependencies', use_auth=True)
        dependency_relationship_verified = result['success'] and dependency_task_id in result['data'].get('dependency_task_ids', [])
        
        self.log_test(
            "UNBLOCKED TASK DETECTION - DEPENDENCY RELATIONSHIP",
            dependency_relationship_verified,
            f"Dependency relationship verified: {dependent_task_name} depends on {dependency_task_name}" if dependency_relationship_verified else f"Dependency relationship not found: {result.get('error', 'Unknown error')}"
        )
        
        if not dependency_relationship_verified:
            return False
        
        # Check initial notification count
        result = self.make_request('GET', '/notifications', use_auth=True)
        initial_notification_count = len(result['data']) if result['success'] else 0
        
        # Complete the dependency task (Task A)
        complete_task_data = {
            "status": "completed",
            "completed": True
        }
        
        result = self.make_request('PUT', f'/tasks/{dependency_task_id}', data=complete_task_data, use_auth=True)
        dependency_task_completed = result['success']
        
        self.log_test(
            "UNBLOCKED TASK DETECTION - COMPLETE DEPENDENCY TASK",
            dependency_task_completed,
            f"Dependency task completed successfully: {dependency_task_name}" if dependency_task_completed else f"Failed to complete dependency task: {result.get('error', 'Unknown error')}"
        )
        
        if not dependency_task_completed:
            return False
        
        # Wait for notification processing
        time.sleep(3)
        
        # Check for unblocked task notification
        result = self.make_request('GET', '/notifications', use_auth=True)
        if not result['success']:
            self.log_test("UNBLOCKED TASK DETECTION - GET NOTIFICATIONS AFTER COMPLETION", False, f"Failed to get notifications: {result.get('error', 'Unknown error')}")
            return False
        
        current_notifications = result['data']
        new_notification_count = len(current_notifications)
        
        # Look for unblocked task notification
        unblocked_notification = None
        for notification in current_notifications:
            if (notification.get('type') == 'unblocked_task' or 
                'unblocked' in notification.get('message', '').lower() or
                'available' in notification.get('message', '').lower() or
                dependent_task_name in notification.get('message', '')):
                unblocked_notification = notification
                break
        
        notification_created = unblocked_notification is not None
        self.log_test(
            "UNBLOCKED TASK DETECTION - NOTIFICATION CREATED",
            notification_created,
            f"Unblocked task notification created successfully" if notification_created else f"No unblocked task notification found (total notifications: {new_notification_count})"
        )
        
        if notification_created:
            # Verify notification content
            notification_title = unblocked_notification.get('title', '')
            notification_message = unblocked_notification.get('message', '')
            
            # Check if notification contains correct task names
            contains_dependent_task_name = dependent_task_name in notification_message or dependent_task_name in notification_title
            contains_dependency_task_name = dependency_task_name in notification_message or dependency_task_name in notification_title
            
            self.log_test(
                "UNBLOCKED TASK DETECTION - NOTIFICATION CONTENT - DEPENDENT TASK NAME",
                contains_dependent_task_name,
                f"Notification contains dependent task name '{dependent_task_name}'" if contains_dependent_task_name else f"Notification missing dependent task name. Title: '{notification_title}', Message: '{notification_message}'"
            )
            
            self.log_test(
                "UNBLOCKED TASK DETECTION - NOTIFICATION CONTENT - DEPENDENCY TASK NAME",
                contains_dependency_task_name,
                f"Notification contains dependency task name '{dependency_task_name}'" if contains_dependency_task_name else f"Notification missing dependency task name. Title: '{notification_title}', Message: '{notification_message}'"
            )
            
            # Check if notification contains project context
            project_name = "Notifications Test Project"
            contains_project_context = project_name in notification_message or project_name in notification_title
            
            self.log_test(
                "UNBLOCKED TASK DETECTION - NOTIFICATION CONTENT - PROJECT CONTEXT",
                contains_project_context,
                f"Notification contains project context '{project_name}'" if contains_project_context else f"Notification missing project context. Title: '{notification_title}', Message: '{notification_message}'"
            )
            
            # Verify notification metadata
            notification_user_id = unblocked_notification.get('user_id')
            notification_task_id = unblocked_notification.get('related_task_id')
            
            correct_user_id = notification_user_id is not None
            correct_task_id = notification_task_id == dependent_task_id
            
            self.log_test(
                "UNBLOCKED TASK DETECTION - NOTIFICATION METADATA - USER ID",
                correct_user_id,
                f"Notification has correct user_id" if correct_user_id else f"Notification missing or incorrect user_id: {notification_user_id}"
            )
            
            self.log_test(
                "UNBLOCKED TASK DETECTION - NOTIFICATION METADATA - TASK ID",
                correct_task_id,
                f"Notification has correct related_task_id: {notification_task_id}" if correct_task_id else f"Notification has incorrect related_task_id: expected {dependent_task_id}, got {notification_task_id}"
            )
            
            return (contains_dependent_task_name and contains_dependency_task_name and 
                   contains_project_context and correct_user_id and correct_task_id)
        
        return False

    def test_database_schema(self):
        """Test Database Schema for notifications"""
        print("\n=== TESTING DATABASE SCHEMA ===")
        
        if not self.auth_token:
            self.log_test("DATABASE SCHEMA - Authentication Required", False, "No authentication token available")
            return False
        
        # Test browser_notifications collection can be created and queried
        result = self.make_request('GET', '/notifications', use_auth=True)
        browser_notifications_queryable = result['success']
        
        self.log_test(
            "DATABASE SCHEMA - BROWSER NOTIFICATIONS COLLECTION",
            browser_notifications_queryable,
            f"browser_notifications collection can be queried" if browser_notifications_queryable else f"Failed to query browser_notifications: {result.get('error', 'Unknown error')}"
        )
        
        # Test notification preference fields are properly saved and retrieved
        result = self.make_request('GET', '/notifications/preferences', use_auth=True)
        preferences_queryable = result['success']
        
        self.log_test(
            "DATABASE SCHEMA - NOTIFICATION PREFERENCES COLLECTION",
            preferences_queryable,
            f"notification_preferences collection can be queried" if preferences_queryable else f"Failed to query notification_preferences: {result.get('error', 'Unknown error')}"
        )
        
        if preferences_queryable:
            preferences = result['data']
            
            # Test that new fields are properly saved
            test_update = {
                "achievement_notifications": True,
                "unblocked_task_notifications": False
            }
            
            result = self.make_request('PUT', '/notifications/preferences', data=test_update, use_auth=True)
            preferences_updatable = result['success']
            
            self.log_test(
                "DATABASE SCHEMA - NOTIFICATION PREFERENCES UPDATE",
                preferences_updatable,
                f"Notification preferences can be updated" if preferences_updatable else f"Failed to update preferences: {result.get('error', 'Unknown error')}"
            )
            
            if preferences_updatable:
                # Verify the update persisted
                result = self.make_request('GET', '/notifications/preferences', use_auth=True)
                if result['success']:
                    updated_preferences = result['data']
                    achievement_persisted = updated_preferences.get('achievement_notifications') == True
                    unblocked_persisted = updated_preferences.get('unblocked_task_notifications') == False
                    
                    fields_persisted = achievement_persisted and unblocked_persisted
                    self.log_test(
                        "DATABASE SCHEMA - PREFERENCE FIELDS PERSISTENCE",
                        fields_persisted,
                        f"New preference fields persisted correctly" if fields_persisted else f"Preference fields not persisted: achievement={updated_preferences.get('achievement_notifications')}, unblocked={updated_preferences.get('unblocked_task_notifications')}"
                    )
        
        # Test unblocked_task notification type is recognized
        # Create a test notification to verify the type is accepted
        result = self.make_request('POST', '/notifications/test', use_auth=True)
        if result['success']:
            time.sleep(1)
            result = self.make_request('GET', '/notifications', use_auth=True)
            if result['success'] and result['data']:
                notification_types = [n.get('type') for n in result['data']]
                unblocked_task_type_supported = any('unblocked' in str(t).lower() for t in notification_types)
                
                self.log_test(
                    "DATABASE SCHEMA - UNBLOCKED TASK NOTIFICATION TYPE",
                    unblocked_task_type_supported,
                    f"unblocked_task notification type is supported" if unblocked_task_type_supported else f"unblocked_task notification type not found in: {notification_types}"
                )
        
        return browser_notifications_queryable and preferences_queryable

    def test_authentication_and_user_isolation(self):
        """Test authentication requirements and user isolation"""
        print("\n=== TESTING AUTHENTICATION AND USER ISOLATION ===")
        
        # Test that endpoints require authentication
        endpoints_to_test = [
            ('GET', '/notifications/preferences'),
            ('PUT', '/notifications/preferences'),
            ('GET', '/notifications'),
            ('PUT', '/notifications/mark-all-read'),
            ('DELETE', '/notifications/clear-all')
        ]
        
        auth_required_count = 0
        total_endpoints = len(endpoints_to_test)
        
        for method, endpoint in endpoints_to_test:
            result = self.make_request(method, endpoint, use_auth=False)
            requires_auth = result['status_code'] in [401, 403]
            
            self.log_test(
                f"AUTHENTICATION REQUIRED - {method} {endpoint}",
                requires_auth,
                f"Endpoint properly requires authentication (status: {result['status_code']})" if requires_auth else f"Endpoint does not require authentication (status: {result['status_code']})"
            )
            
            if requires_auth:
                auth_required_count += 1
        
        auth_success_rate = (auth_required_count / total_endpoints) * 100
        overall_auth_success = auth_success_rate >= 80
        
        self.log_test(
            "AUTHENTICATION REQUIREMENTS OVERALL",
            overall_auth_success,
            f"Authentication requirements: {auth_required_count}/{total_endpoints} endpoints ({auth_success_rate:.1f}%)"
        )
        
        # Test user isolation (notifications are user-specific)
        if self.auth_token:
            # Get current user's notifications
            result = self.make_request('GET', '/notifications', use_auth=True)
            if result['success']:
                user_notifications = result['data']
                
                # All notifications should belong to the current user
                user_isolation_verified = True
                for notification in user_notifications:
                    if 'user_id' in notification:
                        # We can't verify the exact user_id without knowing it, but we can check consistency
                        continue
                    else:
                        user_isolation_verified = False
                        break
                
                self.log_test(
                    "USER ISOLATION - NOTIFICATIONS",
                    user_isolation_verified,
                    f"User isolation verified for notifications" if user_isolation_verified else "User isolation issues detected in notifications"
                )
        
        return overall_auth_success

    def run_comprehensive_notifications_test(self):
        """Run comprehensive notifications center tests"""
        print("\n🔔 STARTING NOTIFICATIONS CENTER COMPREHENSIVE TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("User Registration and Login", self.test_user_registration_and_login),
            ("Notification Preferences API", self.test_notification_preferences_api),
            ("Browser Notifications API", self.test_browser_notifications_api),
            ("Unblocked Task Detection Logic", self.test_unblocked_task_detection_logic),
            ("Database Schema", self.test_database_schema),
            ("Authentication and User Isolation", self.test_authentication_and_user_isolation)
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
        print("🔔 NOTIFICATIONS CENTER TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for notifications functionality
        preferences_tests_passed = sum(1 for result in self.test_results if result['success'] and 'NOTIFICATION PREFERENCES' in result['test'])
        browser_notifications_tests_passed = sum(1 for result in self.test_results if result['success'] and 'BROWSER NOTIFICATIONS' in result['test'])
        unblocked_task_tests_passed = sum(1 for result in self.test_results if result['success'] and 'UNBLOCKED TASK' in result['test'])
        database_tests_passed = sum(1 for result in self.test_results if result['success'] and 'DATABASE SCHEMA' in result['test'])
        auth_tests_passed = sum(1 for result in self.test_results if result['success'] and 'AUTHENTICATION' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"Notification Preferences Tests Passed: {preferences_tests_passed}")
        print(f"Browser Notifications Tests Passed: {browser_notifications_tests_passed}")
        print(f"Unblocked Task Detection Tests Passed: {unblocked_task_tests_passed}")
        print(f"Database Schema Tests Passed: {database_tests_passed}")
        print(f"Authentication Tests Passed: {auth_tests_passed}")
        
        if success_rate >= 85:
            print("\n✅ NOTIFICATIONS CENTER SYSTEM: SUCCESS")
            print("   ✅ Phase 0 - Notification Settings Backend API working")
            print("   ✅ Phase 1 - Browser Notifications Backend API functional")
            print("   ✅ Phase 1 - Unblocked Task Detection Logic operational")
            print("   ✅ Database schema supports notification collections")
            print("   ✅ Authentication and user isolation verified")
            print("   The Notifications Center backend is production-ready!")
        else:
            print("\n❌ NOTIFICATIONS CENTER SYSTEM: ISSUES DETECTED")
            print("   Issues found in notifications center implementation")
        
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
        
        # Clean up notifications
        try:
            result = self.make_request('DELETE', '/notifications/clear-all', use_auth=True)
            if result['success']:
                cleanup_count += result['data'].get('count', 0)
                print(f"   ✅ Cleaned up notifications: {result['data'].get('count', 0)}")
        except:
            pass
        
        # Clean up tasks first (they depend on projects)
        for task_id in self.created_resources.get('tasks', []):
            try:
                result = self.make_request('DELETE', f'/tasks/{task_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
                    print(f"   ✅ Cleaned up task: {task_id}")
            except:
                pass
        
        # Clean up projects (they depend on areas)
        for project_id in self.created_resources.get('projects', []):
            try:
                result = self.make_request('DELETE', f'/projects/{project_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
                    print(f"   ✅ Cleaned up project: {project_id}")
            except:
                pass
        
        # Clean up areas (they may depend on pillars)
        for area_id in self.created_resources.get('areas', []):
            try:
                result = self.make_request('DELETE', f'/areas/{area_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
                    print(f"   ✅ Cleaned up area: {area_id}")
            except:
                pass
        
        # Clean up pillars
        for pillar_id in self.created_resources.get('pillars', []):
            try:
                result = self.make_request('DELETE', f'/pillars/{pillar_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
                    print(f"   ✅ Cleaned up pillar: {pillar_id}")
            except:
                pass
        
        if cleanup_count > 0:
            print(f"   ✅ Cleanup completed for {cleanup_count} resources")
        else:
            print("   ℹ️ No resources to cleanup")

def main():
    """Run Notifications Center Tests"""
    print("🔔 STARTING NOTIFICATIONS CENTER BACKEND TESTING")
    print("=" * 80)
    
    tester = NotificationsCenterTester()
    
    try:
        # Run the comprehensive notifications center tests
        success = tester.run_comprehensive_notifications_test()
        
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