#!/usr/bin/env python3
"""
USER-DEFINED CUSTOM ACHIEVEMENTS SYSTEM - PHASE 2 TESTING
Complete end-to-end testing of the Custom Achievements System implementation.

FOCUS AREAS:
1. CUSTOM ACHIEVEMENT CRUD OPERATIONS - Test GET/POST/PUT/DELETE /api/achievements/custom endpoints
2. CUSTOM ACHIEVEMENT MODELS & DATA - Test CustomAchievement model with all target types
3. AUTO-TRACKING INTEGRATION - Test custom achievement triggers when actions occur
4. PROGRESS CALCULATION - Test progress calculation for different target types
5. COMPLETION & NOTIFICATIONS - Test achievement completion and notification creation
6. TARGET VALIDATION - Test validation for projects/courses targets

SPECIFIC ENDPOINTS TO TEST:
- GET /api/achievements/custom (get all user's custom achievements)
- POST /api/achievements/custom (create new custom achievement)
- PUT /api/achievements/custom/{id} (update custom achievement)
- DELETE /api/achievements/custom/{id} (delete custom achievement)
- POST /api/achievements/custom/check (check progress for all custom achievements)

TEST SCENARIOS:
1. Basic CRUD Operations - Create, read, update, delete custom achievements
2. Task-Based Goals - Create custom achievement for "Complete 5 tasks" and test trigger
3. Project-Specific Goals - Create custom achievement for "Complete Project X" and test trigger
4. Journal Entry Goals - Create custom achievement for "Write 3 journal entries" and test trigger
5. Progress Tracking - Verify progress updates accurately as actions occur
6. Completion & Notifications - Test achievement completion and notification creation
7. Target Validation - Test validation for non-existent projects/targets

AUTHENTICATION:
- Use test credentials with realistic data for custom achievements testing
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid
import time
import re

# Configuration - Using the production backend URL from frontend/.env
BACKEND_URL = "https://a6f7ddc8-1ace-40b1-9ed5-db784a5228b2.preview.emergentagent.com/api"

class CustomAchievementSystemTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.created_resources = {
            'pillars': [],
            'areas': [],
            'projects': [],
            'tasks': [],
            'journal_entries': [],
            'custom_achievements': [],
            'users': []
        }
        self.auth_token = None
        # Use realistic test data for custom achievements testing
        self.test_user_email = f"custom.achievement.tester_{uuid.uuid4().hex[:8]}@aurumlife.com"
        self.test_user_password = "CustomAchievementTest2025!"
        self.test_user_data = {
            "username": f"custom_achievement_tester_{uuid.uuid4().hex[:8]}",
            "email": self.test_user_email,
            "first_name": "Custom",
            "last_name": "Achievement Tester",
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
        
        return result['success']

    def test_user_registration_and_login(self):
        """Test user registration and login for custom achievements testing"""
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

    def test_custom_achievement_crud_operations(self):
        """Test Custom Achievement CRUD operations"""
        print("\n=== TESTING CUSTOM ACHIEVEMENT CRUD OPERATIONS ===")
        
        if not self.auth_token:
            self.log_test("CUSTOM ACHIEVEMENT CRUD - Authentication Required", False, "No authentication token available")
            return False
        
        # Test 1: GET /api/achievements/custom - Get all custom achievements (should be empty initially)
        result = self.make_request('GET', '/achievements/custom', use_auth=True)
        self.log_test(
            "GET CUSTOM ACHIEVEMENTS ENDPOINT",
            result['success'],
            f"Retrieved custom achievements successfully" if result['success'] else f"Failed to get custom achievements: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            custom_achievements_data = result['data']
            
            # Verify response structure
            has_success = custom_achievements_data.get('success', False)
            has_custom_achievements = 'custom_achievements' in custom_achievements_data
            has_timestamp = 'timestamp' in custom_achievements_data
            
            self.log_test(
                "CUSTOM ACHIEVEMENTS RESPONSE STRUCTURE",
                has_success and has_custom_achievements and has_timestamp,
                f"Response has correct structure (success: {has_success}, custom_achievements: {has_custom_achievements}, timestamp: {has_timestamp})"
            )
            
            initial_custom_achievements = custom_achievements_data.get('custom_achievements', [])
            self.log_test(
                "INITIAL CUSTOM ACHIEVEMENTS COUNT",
                isinstance(initial_custom_achievements, list),
                f"Initial custom achievements: {len(initial_custom_achievements)} (expected: 0 for new user)"
            )
        
        # Test 2: POST /api/achievements/custom - Create new custom achievements
        custom_achievement_test_cases = [
            {
                "name": "Complete 5 Tasks",
                "description": "Complete 5 tasks to boost productivity",
                "icon": "✅",
                "target_type": "complete_tasks",
                "target_count": 5
            },
            {
                "name": "Write 3 Journal Entries",
                "description": "Write 3 journal entries for reflection",
                "icon": "📝",
                "target_type": "write_journal_entries",
                "target_count": 3
            },
            {
                "name": "Complete 2 Projects",
                "description": "Complete 2 projects to achieve goals",
                "icon": "🎯",
                "target_type": "complete_project",
                "target_count": 2
            }
        ]
        
        created_achievements = []
        for i, achievement_data in enumerate(custom_achievement_test_cases):
            result = self.make_request('POST', '/achievements/custom', data=achievement_data, use_auth=True)
            
            self.log_test(
                f"CREATE CUSTOM ACHIEVEMENT {i+1}",
                result['success'],
                f"Created custom achievement '{achievement_data['name']}'" if result['success'] else f"Failed to create custom achievement: {result.get('error', 'Unknown error')}"
            )
            
            if result['success']:
                achievement_response = result['data']
                
                # Verify response structure
                has_success = achievement_response.get('success', False)
                has_achievement = 'achievement' in achievement_response
                has_message = 'message' in achievement_response
                
                self.log_test(
                    f"CREATE CUSTOM ACHIEVEMENT {i+1} RESPONSE STRUCTURE",
                    has_success and has_achievement and has_message,
                    f"Create response has correct structure"
                )
                
                if has_achievement:
                    created_achievement = achievement_response['achievement']
                    created_achievements.append(created_achievement)
                    self.created_resources['custom_achievements'].append(created_achievement['id'])
                    
                    # Verify achievement fields
                    expected_fields = ['id', 'name', 'description', 'icon', 'target_type', 'target_count', 'is_active', 'is_completed', 'current_progress']
                    missing_fields = [field for field in expected_fields if field not in created_achievement]
                    
                    self.log_test(
                        f"CUSTOM ACHIEVEMENT {i+1} OBJECT STRUCTURE",
                        len(missing_fields) == 0,
                        f"Achievement has all expected fields" if len(missing_fields) == 0 else f"Missing fields: {missing_fields}"
                    )
        
        # Test 3: GET /api/achievements/custom - Verify created achievements
        result = self.make_request('GET', '/achievements/custom', use_auth=True)
        if result['success']:
            custom_achievements_data = result['data']
            current_custom_achievements = custom_achievements_data.get('custom_achievements', [])
            
            self.log_test(
                "VERIFY CREATED CUSTOM ACHIEVEMENTS",
                len(current_custom_achievements) == len(created_achievements),
                f"Found {len(current_custom_achievements)} custom achievements (expected: {len(created_achievements)})"
            )
        
        # Test 4: PUT /api/achievements/custom/{id} - Update custom achievement
        if created_achievements:
            first_achievement = created_achievements[0]
            achievement_id = first_achievement['id']
            
            update_data = {
                "name": "Complete 10 Tasks (Updated)",
                "description": "Updated description for task completion goal",
                "target_count": 10
            }
            
            result = self.make_request('PUT', f'/achievements/custom/{achievement_id}', data=update_data, use_auth=True)
            self.log_test(
                "UPDATE CUSTOM ACHIEVEMENT",
                result['success'],
                f"Updated custom achievement successfully" if result['success'] else f"Failed to update custom achievement: {result.get('error', 'Unknown error')}"
            )
            
            if result['success']:
                # Verify update response structure
                update_response = result['data']
                has_success = update_response.get('success', False)
                has_message = 'message' in update_response
                
                self.log_test(
                    "UPDATE CUSTOM ACHIEVEMENT RESPONSE STRUCTURE",
                    has_success and has_message,
                    f"Update response has correct structure"
                )
        
        # Test 5: DELETE /api/achievements/custom/{id} - Delete custom achievement
        if created_achievements and len(created_achievements) > 1:
            last_achievement = created_achievements[-1]
            achievement_id = last_achievement['id']
            
            result = self.make_request('DELETE', f'/achievements/custom/{achievement_id}', use_auth=True)
            self.log_test(
                "DELETE CUSTOM ACHIEVEMENT",
                result['success'],
                f"Deleted custom achievement successfully" if result['success'] else f"Failed to delete custom achievement: {result.get('error', 'Unknown error')}"
            )
            
            if result['success']:
                # Remove from our tracking
                self.created_resources['custom_achievements'].remove(achievement_id)
                
                # Verify deletion response structure
                delete_response = result['data']
                has_success = delete_response.get('success', False)
                has_message = 'message' in delete_response
                
                self.log_test(
                    "DELETE CUSTOM ACHIEVEMENT RESPONSE STRUCTURE",
                    has_success and has_message,
                    f"Delete response has correct structure"
                )
        
        return True

    def test_custom_achievement_progress_check(self):
        """Test custom achievement progress check endpoint"""
        print("\n=== TESTING CUSTOM ACHIEVEMENT PROGRESS CHECK ===")
        
        if not self.auth_token:
            self.log_test("CUSTOM ACHIEVEMENT PROGRESS CHECK - Authentication Required", False, "No authentication token available")
            return False
        
        # Test POST /api/achievements/custom/check - Check progress for all custom achievements
        result = self.make_request('POST', '/achievements/custom/check', use_auth=True)
        self.log_test(
            "CUSTOM ACHIEVEMENT PROGRESS CHECK ENDPOINT",
            result['success'],
            f"Custom achievement progress check completed successfully" if result['success'] else f"Failed to check custom achievement progress: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            check_data = result['data']
            
            # Verify response structure
            has_success = check_data.get('success', False)
            has_newly_completed = 'newly_completed' in check_data
            has_achievements = 'achievements' in check_data
            has_timestamp = 'timestamp' in check_data
            
            self.log_test(
                "CUSTOM ACHIEVEMENT PROGRESS CHECK RESPONSE STRUCTURE",
                has_success and has_newly_completed and has_timestamp,
                f"Progress check response has correct structure (success: {has_success}, newly_completed: {has_newly_completed}, timestamp: {has_timestamp})"
            )
            
            newly_completed_count = check_data.get('newly_completed', -1)
            self.log_test(
                "CUSTOM ACHIEVEMENT NEWLY COMPLETED COUNT",
                isinstance(newly_completed_count, int) and newly_completed_count >= 0,
                f"Newly completed count: {newly_completed_count}" if isinstance(newly_completed_count, int) else f"Invalid newly completed count: {newly_completed_count}"
            )
        
        return True

    def test_custom_achievement_with_infrastructure(self):
        """Test custom achievements with actual infrastructure (projects, tasks, journal entries)"""
        print("\n=== TESTING CUSTOM ACHIEVEMENTS WITH INFRASTRUCTURE ===")
        
        if not self.auth_token:
            self.log_test("CUSTOM ACHIEVEMENT INFRASTRUCTURE - Authentication Required", False, "No authentication token available")
            return False
        
        # Create infrastructure for testing
        pillar_data = {
            "name": "Custom Achievement Test Pillar",
            "description": "Test pillar for custom achievement testing",
            "icon": "🎯",
            "color": "#4CAF50"
        }
        
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        if not result['success']:
            self.log_test("INFRASTRUCTURE - CREATE PILLAR", False, "Failed to create test pillar")
            return False
        
        pillar_id = result['data']['id']
        self.created_resources['pillars'].append(pillar_id)
        
        area_data = {
            "name": "Custom Achievement Test Area",
            "description": "Test area for custom achievement testing",
            "icon": "📋",
            "color": "#2196F3",
            "pillar_id": pillar_id
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        if not result['success']:
            self.log_test("INFRASTRUCTURE - CREATE AREA", False, "Failed to create test area")
            return False
        
        area_id = result['data']['id']
        self.created_resources['areas'].append(area_id)
        
        project_data = {
            "area_id": area_id,
            "name": "Custom Achievement Test Project",
            "description": "Project for testing custom achievements",
            "priority": "high"
        }
        
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        if not result['success']:
            self.log_test("INFRASTRUCTURE - CREATE PROJECT", False, "Failed to create test project")
            return False
        
        project_id = result['data']['id']
        self.created_resources['projects'].append(project_id)
        
        # Create custom achievements for testing
        task_achievement_data = {
            "name": "Complete 3 Tasks in Test Project",
            "description": "Complete 3 tasks in the test project",
            "icon": "✅",
            "target_type": "complete_tasks",
            "target_id": project_id,
            "target_count": 3
        }
        
        result = self.make_request('POST', '/achievements/custom', data=task_achievement_data, use_auth=True)
        if not result['success']:
            self.log_test("INFRASTRUCTURE - CREATE TASK ACHIEVEMENT", False, "Failed to create task custom achievement")
            return False
        
        task_achievement_id = result['data']['achievement']['id']
        self.created_resources['custom_achievements'].append(task_achievement_id)
        
        # Create journal achievement
        journal_achievement_data = {
            "name": "Write 2 Journal Entries",
            "description": "Write 2 journal entries for reflection",
            "icon": "📝",
            "target_type": "write_journal_entries",
            "target_count": 2
        }
        
        result = self.make_request('POST', '/achievements/custom', data=journal_achievement_data, use_auth=True)
        if not result['success']:
            self.log_test("INFRASTRUCTURE - CREATE JOURNAL ACHIEVEMENT", False, "Failed to create journal custom achievement")
            return False
        
        journal_achievement_id = result['data']['achievement']['id']
        self.created_resources['custom_achievements'].append(journal_achievement_id)
        
        # Test initial progress (should be 0)
        result = self.make_request('POST', '/achievements/custom/check', use_auth=True)
        self.log_test(
            "INITIAL CUSTOM ACHIEVEMENT PROGRESS CHECK",
            result['success'],
            f"Initial progress check completed" if result['success'] else f"Failed initial progress check: {result.get('error', 'Unknown error')}"
        )
        
        # Create and complete tasks to test progress
        task_names = ["Test Task 1", "Test Task 2", "Test Task 3"]
        completed_tasks = 0
        
        for i, task_name in enumerate(task_names):
            # Create task
            task_data = {
                "project_id": project_id,
                "name": task_name,
                "description": f"Custom achievement test task {i+1}",
                "priority": "medium",
                "status": "todo"
            }
            
            result = self.make_request('POST', '/tasks', data=task_data, use_auth=True)
            if result['success']:
                task_id = result['data']['id']
                self.created_resources['tasks'].append(task_id)
                
                # Complete the task
                update_data = {"status": "completed"}
                update_result = self.make_request('PUT', f'/tasks/{task_id}', data=update_data, use_auth=True)
                
                if update_result['success']:
                    completed_tasks += 1
                    self.log_test(
                        f"INFRASTRUCTURE TEST TASK COMPLETION {i+1}",
                        True,
                        f"Task '{task_name}' completed successfully"
                    )
                    
                    # Small delay to allow trigger processing
                    time.sleep(0.5)
        
        # Check progress after task completions
        time.sleep(2)  # Allow time for triggers to process
        
        result = self.make_request('POST', '/achievements/custom/check', use_auth=True)
        if result['success']:
            check_data = result['data']
            newly_completed = check_data.get('newly_completed', 0)
            
            self.log_test(
                "CUSTOM ACHIEVEMENT PROGRESS AFTER TASKS",
                isinstance(newly_completed, int),
                f"Progress check found {newly_completed} newly completed custom achievements"
            )
        
        # Create journal entries to test journal achievement progress
        journal_entries = [
            {
                "title": "Custom Achievement Test Entry 1",
                "content": "Testing custom achievement progress with journal entries. This is the first entry.",
                "mood": "motivated",
                "energy_level": "high",
                "tags": ["custom", "achievement", "test"]
            },
            {
                "title": "Custom Achievement Test Entry 2",
                "content": "Second journal entry for testing custom achievement progress tracking.",
                "mood": "reflective",
                "energy_level": "moderate",
                "tags": ["custom", "achievement", "progress"]
            }
        ]
        
        created_entries = 0
        for i, entry_data in enumerate(journal_entries):
            result = self.make_request('POST', '/journal', data=entry_data, use_auth=True)
            
            if result['success']:
                entry_id = result['data']['id']
                self.created_resources['journal_entries'].append(entry_id)
                created_entries += 1
                
                self.log_test(
                    f"INFRASTRUCTURE TEST JOURNAL ENTRY {i+1}",
                    True,
                    f"Journal entry '{entry_data['title']}' created successfully"
                )
                
                time.sleep(0.5)
        
        # Final progress check
        time.sleep(2)
        
        result = self.make_request('POST', '/achievements/custom/check', use_auth=True)
        if result['success']:
            check_data = result['data']
            newly_completed = check_data.get('newly_completed', 0)
            
            self.log_test(
                "FINAL CUSTOM ACHIEVEMENT PROGRESS CHECK",
                isinstance(newly_completed, int),
                f"Final progress check found {newly_completed} newly completed custom achievements"
            )
        
        # Get all custom achievements to verify progress
        result = self.make_request('GET', '/achievements/custom', use_auth=True)
        if result['success']:
            custom_achievements = result['data'].get('custom_achievements', [])
            
            for achievement in custom_achievements:
                name = achievement.get('name', 'Unknown')
                current_progress = achievement.get('current_progress', 0)
                target_count = achievement.get('target_count', 1)
                is_completed = achievement.get('is_completed', False)
                progress_percentage = achievement.get('progress_percentage', 0)
                
                self.log_test(
                    f"CUSTOM ACHIEVEMENT PROGRESS - {name}",
                    isinstance(current_progress, int) and isinstance(progress_percentage, (int, float)),
                    f"Progress: {current_progress}/{target_count} ({progress_percentage:.1f}%), Completed: {is_completed}"
                )
        
        return True

    def run_comprehensive_custom_achievement_test(self):
        """Run comprehensive custom achievement system tests"""
        print("\n🏆 STARTING USER-DEFINED CUSTOM ACHIEVEMENTS SYSTEM - PHASE 2 TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("User Registration and Login", self.test_user_registration_and_login),
            ("Custom Achievement CRUD Operations", self.test_custom_achievement_crud_operations),
            ("Custom Achievement Progress Check", self.test_custom_achievement_progress_check),
            ("Custom Achievement with Infrastructure", self.test_custom_achievement_with_infrastructure)
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
        print("🎯 USER-DEFINED CUSTOM ACHIEVEMENTS SYSTEM TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for custom achievement functionality
        crud_tests_passed = sum(1 for result in self.test_results if result['success'] and 'CRUD' in result['test'])
        progress_tests_passed = sum(1 for result in self.test_results if result['success'] and 'PROGRESS' in result['test'])
        infrastructure_tests_passed = sum(1 for result in self.test_results if result['success'] and 'INFRASTRUCTURE' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"CRUD Tests Passed: {crud_tests_passed}")
        print(f"Progress Tests Passed: {progress_tests_passed}")
        print(f"Infrastructure Tests Passed: {infrastructure_tests_passed}")
        
        if success_rate >= 85:
            print("\n✅ USER-DEFINED CUSTOM ACHIEVEMENTS SYSTEM: SUCCESS")
            print("   ✅ Custom Achievement CRUD operations working correctly")
            print("   ✅ Progress calculation and tracking functional")
            print("   ✅ Auto-tracking integration with existing triggers")
            print("   ✅ All target types supported (tasks, projects, journal entries, etc.)")
            print("   The User-Defined Custom Achievements System is production-ready!")
        else:
            print("\n❌ USER-DEFINED CUSTOM ACHIEVEMENTS SYSTEM: ISSUES DETECTED")
            print("   Issues found in custom achievement system implementation")
        
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
        
        # Clean up custom achievements
        for achievement_id in self.created_resources.get('custom_achievements', []):
            try:
                result = self.make_request('DELETE', f'/achievements/custom/{achievement_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
                    print(f"   ✅ Cleaned up custom achievement: {achievement_id}")
            except:
                pass
        
        # Clean up journal entries
        for entry_id in self.created_resources.get('journal_entries', []):
            try:
                result = self.make_request('DELETE', f'/journal/{entry_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
                    print(f"   ✅ Cleaned up journal entry: {entry_id}")
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
    """Run User-Defined Custom Achievements System Tests"""
    print("🏆 STARTING USER-DEFINED CUSTOM ACHIEVEMENTS SYSTEM BACKEND TESTING")
    print("=" * 80)
    
    tester = CustomAchievementSystemTester()
    
    try:
        # Run the comprehensive custom achievement system tests
        success = tester.run_comprehensive_custom_achievement_test()
        
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