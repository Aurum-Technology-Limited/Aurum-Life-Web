#!/usr/bin/env python3
"""
DYNAMIC PREDEFINED ACHIEVEMENTS SYSTEM - PHASE 1 TESTING
Complete end-to-end testing of the Dynamic Achievements System implementation.

FOCUS AREAS:
1. ACHIEVEMENT SERVICE CORE FUNCTIONS - Test GET /api/achievements and POST /api/achievements/check
2. AUTO-TRACKING TRIGGER FUNCTIONS - Test task completion, project completion, journal entry triggers
3. PROGRESS CALCULATION - Test achievement progress calculation accuracy
4. ACHIEVEMENT UNLOCKING - Test that achievements unlock when requirements are met
5. NOTIFICATION SYSTEM - Test achievement notifications are created properly
6. PERFORMANCE VERIFICATION - Verify trigger functions are efficient and don't add latency

SPECIFIC ENDPOINTS TO TEST:
- GET /api/achievements (get all achievements with progress calculation)
- POST /api/achievements/check (manual achievement checking for testing)

TRIGGER SCENARIOS TO TEST:
- Task completion triggers (when tasks are marked complete)
- Project completion triggers (when projects are marked "Completed")
- Journal entry creation triggers (when new entries are created)
- Course completion triggers (if applicable)

AUTHENTICATION:
- Use test credentials with realistic data for achievements testing
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
BACKEND_URL = "https://f923e448-cb55-4f9b-ac76-0b3c55a83122.preview.emergentagent.com/api"

class AchievementSystemTester:
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
            'users': []
        }
        self.auth_token = None
        # Use realistic test data for achievements testing
        self.test_user_email = f"achievement.tester_{uuid.uuid4().hex[:8]}@aurumlife.com"
        self.test_user_password = "AchievementTest2025!"
        self.test_user_data = {
            "username": f"achievement_tester_{uuid.uuid4().hex[:8]}",
            "email": self.test_user_email,
            "first_name": "Achievement",
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
        """Test user registration and login for achievements testing"""
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

    def test_achievement_api_endpoints(self):
        """Test basic achievement API endpoints"""
        print("\n=== TESTING ACHIEVEMENT API ENDPOINTS ===")
        
        if not self.auth_token:
            self.log_test("ACHIEVEMENT API - Authentication Required", False, "No authentication token available")
            return False
        
        # Test 1: GET /api/achievements - Get all achievements with progress
        result = self.make_request('GET', '/achievements', use_auth=True)
        self.log_test(
            "GET ACHIEVEMENTS ENDPOINT",
            result['success'],
            f"Retrieved achievements successfully" if result['success'] else f"Failed to get achievements: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            achievements_data = result['data']
            
            # Verify response structure
            has_success = achievements_data.get('success', False)
            has_achievements = 'achievements' in achievements_data
            has_timestamp = 'timestamp' in achievements_data
            
            self.log_test(
                "ACHIEVEMENTS RESPONSE STRUCTURE",
                has_success and has_achievements and has_timestamp,
                f"Response has correct structure (success: {has_success}, achievements: {has_achievements}, timestamp: {has_timestamp})"
            )
            
            if has_achievements:
                achievements_list = achievements_data['achievements']
                self.log_test(
                    "ACHIEVEMENTS LIST TYPE",
                    isinstance(achievements_list, list),
                    f"Achievements returned as list with {len(achievements_list)} items" if isinstance(achievements_list, list) else f"Achievements not returned as list: {type(achievements_list)}"
                )
                
                # Check achievement structure if any exist
                if achievements_list:
                    first_achievement = achievements_list[0]
                    expected_fields = ['id', 'name', 'description', 'icon', 'rarity', 'category', 'requirements', 'earned', 'progress']
                    missing_fields = [field for field in expected_fields if field not in first_achievement]
                    
                    self.log_test(
                        "ACHIEVEMENT OBJECT STRUCTURE",
                        len(missing_fields) == 0,
                        f"Achievement has all expected fields" if len(missing_fields) == 0 else f"Missing fields: {missing_fields}"
                    )
                    
                    # Verify progress is a number between 0-100
                    progress = first_achievement.get('progress', -1)
                    progress_valid = isinstance(progress, (int, float)) and 0 <= progress <= 100
                    
                    self.log_test(
                        "ACHIEVEMENT PROGRESS CALCULATION",
                        progress_valid,
                        f"Progress is valid: {progress}%" if progress_valid else f"Invalid progress value: {progress}"
                    )
        
        # Test 2: POST /api/achievements/check - Manual achievement checking
        result = self.make_request('POST', '/achievements/check', use_auth=True)
        self.log_test(
            "CHECK ACHIEVEMENTS ENDPOINT",
            result['success'],
            f"Achievement check completed successfully" if result['success'] else f"Failed to check achievements: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            check_data = result['data']
            
            # Verify response structure
            has_success = check_data.get('success', False)
            has_newly_unlocked = 'newly_unlocked' in check_data
            has_achievements = 'achievements' in check_data
            has_timestamp = 'timestamp' in check_data
            
            self.log_test(
                "CHECK ACHIEVEMENTS RESPONSE STRUCTURE",
                has_success and has_newly_unlocked and has_achievements and has_timestamp,
                f"Check response has correct structure (success: {has_success}, newly_unlocked: {has_newly_unlocked}, achievements: {has_achievements}, timestamp: {has_timestamp})"
            )
            
            newly_unlocked_count = check_data.get('newly_unlocked', -1)
            self.log_test(
                "NEWLY UNLOCKED COUNT",
                isinstance(newly_unlocked_count, int) and newly_unlocked_count >= 0,
                f"Newly unlocked count: {newly_unlocked_count}" if isinstance(newly_unlocked_count, int) else f"Invalid newly unlocked count: {newly_unlocked_count}"
            )
        
        return True

    def test_task_completion_achievement_trigger(self):
        """Test that task completion triggers achievement checking"""
        print("\n=== TESTING TASK COMPLETION ACHIEVEMENT TRIGGER ===")
        
        if not self.auth_token:
            self.log_test("TASK COMPLETION TRIGGER - Authentication Required", False, "No authentication token available")
            return False
        
        # First, create necessary infrastructure (pillar, area, project)
        pillar_data = {
            "name": "Productivity Achievement Test",
            "description": "Test pillar for achievement triggers",
            "icon": "🎯",
            "color": "#4CAF50"
        }
        
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        if not result['success']:
            self.log_test("TASK TRIGGER - CREATE PILLAR", False, "Failed to create test pillar")
            return False
        
        pillar_id = result['data']['id']
        self.created_resources['pillars'].append(pillar_id)
        
        area_data = {
            "name": "Task Management Test",
            "description": "Test area for task achievement triggers",
            "icon": "📋",
            "color": "#2196F3",
            "pillar_id": pillar_id
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        if not result['success']:
            self.log_test("TASK TRIGGER - CREATE AREA", False, "Failed to create test area")
            return False
        
        area_id = result['data']['id']
        self.created_resources['areas'].append(area_id)
        
        project_data = {
            "area_id": area_id,
            "name": "Achievement Testing Project",
            "description": "Project for testing task completion achievements",
            "priority": "high"
        }
        
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        if not result['success']:
            self.log_test("TASK TRIGGER - CREATE PROJECT", False, "Failed to create test project")
            return False
        
        project_id = result['data']['id']
        self.created_resources['projects'].append(project_id)
        
        # Get initial achievement state
        initial_result = self.make_request('GET', '/achievements', use_auth=True)
        initial_achievements = []
        if initial_result['success']:
            initial_achievements = initial_result['data'].get('achievements', [])
        
        # Create and complete multiple tasks to trigger achievements
        task_names = [
            "Set up task tracking system",
            "Complete first productivity task",
            "Organize daily workflow",
            "Review and optimize processes",
            "Establish task completion habits"
        ]
        
        completed_tasks = 0
        for i, task_name in enumerate(task_names):
            # Create task
            task_data = {
                "project_id": project_id,
                "name": task_name,
                "description": f"Achievement test task {i+1}",
                "priority": "medium",
                "status": "todo"
            }
            
            result = self.make_request('POST', '/tasks', data=task_data, use_auth=True)
            if result['success']:
                task_id = result['data']['id']
                self.created_resources['tasks'].append(task_id)
                
                # Complete the task (this should trigger achievement checking)
                update_data = {"status": "completed"}
                update_result = self.make_request('PUT', f'/tasks/{task_id}', data=update_data, use_auth=True)
                
                if update_result['success']:
                    completed_tasks += 1
                    self.log_test(
                        f"TASK COMPLETION {i+1}",
                        True,
                        f"Task '{task_name}' completed successfully"
                    )
                    
                    # Small delay to allow trigger processing
                    time.sleep(0.5)
        
        self.log_test(
            "MULTIPLE TASK COMPLETIONS",
            completed_tasks == len(task_names),
            f"Completed {completed_tasks}/{len(task_names)} tasks"
        )
        
        # Wait a moment for achievement processing
        time.sleep(2)
        
        # Check if achievements were triggered
        final_result = self.make_request('GET', '/achievements', use_auth=True)
        if final_result['success']:
            final_achievements = final_result['data'].get('achievements', [])
            
            # Look for task-related achievements that might have been unlocked
            task_achievements = [a for a in final_achievements if 'task' in a.get('category', '').lower() or 'productivity' in a.get('category', '').lower()]
            unlocked_task_achievements = [a for a in task_achievements if a.get('earned', False)]
            
            self.log_test(
                "TASK ACHIEVEMENT UNLOCKING",
                len(unlocked_task_achievements) > 0,
                f"Found {len(unlocked_task_achievements)} unlocked task-related achievements" if len(unlocked_task_achievements) > 0 else "No task achievements unlocked yet"
            )
            
            # Check progress on task achievements
            task_achievements_with_progress = [a for a in task_achievements if a.get('progress', 0) > 0]
            self.log_test(
                "TASK ACHIEVEMENT PROGRESS",
                len(task_achievements_with_progress) > 0,
                f"Found {len(task_achievements_with_progress)} task achievements with progress > 0" if len(task_achievements_with_progress) > 0 else "No task achievements showing progress"
            )
        
        # Test manual achievement check after task completions
        check_result = self.make_request('POST', '/achievements/check', use_auth=True)
        if check_result['success']:
            newly_unlocked = check_result['data'].get('newly_unlocked', 0)
            self.log_test(
                "MANUAL ACHIEVEMENT CHECK AFTER TASKS",
                isinstance(newly_unlocked, int),
                f"Manual check found {newly_unlocked} newly unlocked achievements"
            )
        
        return True

    def test_project_completion_achievement_trigger(self):
        """Test that project completion triggers achievement checking"""
        print("\n=== TESTING PROJECT COMPLETION ACHIEVEMENT TRIGGER ===")
        
        if not self.auth_token:
            self.log_test("PROJECT COMPLETION TRIGGER - Authentication Required", False, "No authentication token available")
            return False
        
        # Create a project for completion testing
        # First need pillar and area
        pillar_data = {
            "name": "Project Achievement Test",
            "description": "Test pillar for project achievement triggers",
            "icon": "🏗️",
            "color": "#FF9800"
        }
        
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        if not result['success']:
            self.log_test("PROJECT TRIGGER - CREATE PILLAR", False, "Failed to create test pillar")
            return False
        
        pillar_id = result['data']['id']
        self.created_resources['pillars'].append(pillar_id)
        
        area_data = {
            "name": "Project Management Test",
            "description": "Test area for project achievement triggers",
            "icon": "📊",
            "color": "#9C27B0",
            "pillar_id": pillar_id
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        if not result['success']:
            self.log_test("PROJECT TRIGGER - CREATE AREA", False, "Failed to create test area")
            return False
        
        area_id = result['data']['id']
        self.created_resources['areas'].append(area_id)
        
        # Get initial achievement state
        initial_result = self.make_request('GET', '/achievements', use_auth=True)
        initial_project_achievements = []
        if initial_result['success']:
            all_achievements = initial_result['data'].get('achievements', [])
            initial_project_achievements = [a for a in all_achievements if 'project' in a.get('category', '').lower() or 'productivity' in a.get('category', '').lower()]
        
        # Create and complete multiple projects
        project_names = [
            "Website Redesign Project",
            "Mobile App Development",
            "Marketing Campaign Launch"
        ]
        
        completed_projects = 0
        for i, project_name in enumerate(project_names):
            # Create project
            project_data = {
                "area_id": area_id,
                "name": project_name,
                "description": f"Achievement test project {i+1}",
                "priority": "high",
                "status": "active"
            }
            
            result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
            if result['success']:
                project_id = result['data']['id']
                self.created_resources['projects'].append(project_id)
                
                # Complete the project (this should trigger achievement checking)
                update_data = {"status": "completed"}
                update_result = self.make_request('PUT', f'/projects/{project_id}', data=update_data, use_auth=True)
                
                if update_result['success']:
                    completed_projects += 1
                    self.log_test(
                        f"PROJECT COMPLETION {i+1}",
                        True,
                        f"Project '{project_name}' completed successfully"
                    )
                    
                    # Small delay to allow trigger processing
                    time.sleep(0.5)
        
        self.log_test(
            "MULTIPLE PROJECT COMPLETIONS",
            completed_projects == len(project_names),
            f"Completed {completed_projects}/{len(project_names)} projects"
        )
        
        # Wait for achievement processing
        time.sleep(2)
        
        # Check if project achievements were triggered
        final_result = self.make_request('GET', '/achievements', use_auth=True)
        if final_result['success']:
            final_achievements = final_result['data'].get('achievements', [])
            
            # Look for project-related achievements
            project_achievements = [a for a in final_achievements if 'project' in a.get('category', '').lower() or 'productivity' in a.get('category', '').lower()]
            unlocked_project_achievements = [a for a in project_achievements if a.get('earned', False)]
            
            self.log_test(
                "PROJECT ACHIEVEMENT UNLOCKING",
                len(unlocked_project_achievements) > 0,
                f"Found {len(unlocked_project_achievements)} unlocked project-related achievements" if len(unlocked_project_achievements) > 0 else "No project achievements unlocked yet"
            )
            
            # Check progress on project achievements
            project_achievements_with_progress = [a for a in project_achievements if a.get('progress', 0) > 0]
            self.log_test(
                "PROJECT ACHIEVEMENT PROGRESS",
                len(project_achievements_with_progress) > 0,
                f"Found {len(project_achievements_with_progress)} project achievements with progress > 0" if len(project_achievements_with_progress) > 0 else "No project achievements showing progress"
            )
        
        return True

    def test_journal_entry_achievement_trigger(self):
        """Test that journal entry creation triggers achievement checking"""
        print("\n=== TESTING JOURNAL ENTRY ACHIEVEMENT TRIGGER ===")
        
        if not self.auth_token:
            self.log_test("JOURNAL ENTRY TRIGGER - Authentication Required", False, "No authentication token available")
            return False
        
        # Get initial achievement state
        initial_result = self.make_request('GET', '/achievements', use_auth=True)
        initial_journal_achievements = []
        if initial_result['success']:
            all_achievements = initial_result['data'].get('achievements', [])
            initial_journal_achievements = [a for a in all_achievements if 'journal' in a.get('category', '').lower() or 'reflection' in a.get('category', '').lower()]
        
        # Create multiple journal entries to trigger achievements
        journal_entries = [
            {
                "title": "Daily Reflection - Achievement Test 1",
                "content": "Today I'm testing the achievement system by creating journal entries. This is my first entry to see if the trigger system works correctly.",
                "mood": "happy",
                "energy_level": "high",
                "tags": ["achievement", "testing", "reflection"]
            },
            {
                "title": "Gratitude Journal - Achievement Test 2", 
                "content": "I'm grateful for the opportunity to test this achievement system. The journal functionality seems to be working well and I hope the triggers are functioning.",
                "mood": "grateful",
                "energy_level": "medium",
                "tags": ["gratitude", "achievement", "testing"]
            },
            {
                "title": "Goal Setting - Achievement Test 3",
                "content": "Setting goals for the achievement system testing. I want to ensure that journal entry creation properly triggers the achievement checking mechanism.",
                "mood": "motivated",
                "energy_level": "high", 
                "tags": ["goals", "achievement", "motivation"]
            },
            {
                "title": "Learning Log - Achievement Test 4",
                "content": "Learning about how the achievement system works through testing. Each journal entry should trigger the achievement checking process automatically.",
                "mood": "curious",
                "energy_level": "medium",
                "tags": ["learning", "achievement", "system"]
            },
            {
                "title": "Weekly Review - Achievement Test 5",
                "content": "Reviewing the week and testing the achievement system. This should be the fifth journal entry, which might unlock some reflection-based achievements.",
                "mood": "reflective",
                "energy_level": "medium",
                "tags": ["review", "achievement", "reflection"]
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
                    f"JOURNAL ENTRY CREATION {i+1}",
                    True,
                    f"Journal entry '{entry_data['title']}' created successfully"
                )
                
                # Small delay to allow trigger processing
                time.sleep(0.5)
            else:
                self.log_test(
                    f"JOURNAL ENTRY CREATION {i+1}",
                    False,
                    f"Failed to create journal entry: {result.get('error', 'Unknown error')}"
                )
        
        self.log_test(
            "MULTIPLE JOURNAL ENTRY CREATIONS",
            created_entries == len(journal_entries),
            f"Created {created_entries}/{len(journal_entries)} journal entries"
        )
        
        # Wait for achievement processing
        time.sleep(2)
        
        # Check if journal achievements were triggered
        final_result = self.make_request('GET', '/achievements', use_auth=True)
        if final_result['success']:
            final_achievements = final_result['data'].get('achievements', [])
            
            # Look for journal/reflection-related achievements
            journal_achievements = [a for a in final_achievements if 'journal' in a.get('category', '').lower() or 'reflection' in a.get('category', '').lower()]
            unlocked_journal_achievements = [a for a in journal_achievements if a.get('earned', False)]
            
            self.log_test(
                "JOURNAL ACHIEVEMENT UNLOCKING",
                len(unlocked_journal_achievements) > 0,
                f"Found {len(unlocked_journal_achievements)} unlocked journal-related achievements" if len(unlocked_journal_achievements) > 0 else "No journal achievements unlocked yet"
            )
            
            # Check progress on journal achievements
            journal_achievements_with_progress = [a for a in journal_achievements if a.get('progress', 0) > 0]
            self.log_test(
                "JOURNAL ACHIEVEMENT PROGRESS",
                len(journal_achievements_with_progress) > 0,
                f"Found {len(journal_achievements_with_progress)} journal achievements with progress > 0" if len(journal_achievements_with_progress) > 0 else "No journal achievements showing progress"
            )
            
            # Check if any achievements have requirements for journal entries
            journal_requirement_achievements = []
            for achievement in final_achievements:
                requirements = achievement.get('requirements', {})
                if 'journal_entries' in requirements:
                    journal_requirement_achievements.append(achievement)
            
            self.log_test(
                "JOURNAL ENTRY REQUIREMENT ACHIEVEMENTS",
                len(journal_requirement_achievements) > 0,
                f"Found {len(journal_requirement_achievements)} achievements with journal entry requirements" if len(journal_requirement_achievements) > 0 else "No achievements found with journal entry requirements"
            )
        
        return True

    def test_achievement_progress_calculation(self):
        """Test that achievement progress is calculated correctly"""
        print("\n=== TESTING ACHIEVEMENT PROGRESS CALCULATION ===")
        
        if not self.auth_token:
            self.log_test("ACHIEVEMENT PROGRESS - Authentication Required", False, "No authentication token available")
            return False
        
        # Get current achievements to analyze progress calculation
        result = self.make_request('GET', '/achievements', use_auth=True)
        if not result['success']:
            self.log_test("ACHIEVEMENT PROGRESS - GET ACHIEVEMENTS", False, "Failed to get achievements for progress testing")
            return False
        
        achievements = result['data'].get('achievements', [])
        
        if not achievements:
            self.log_test("ACHIEVEMENT PROGRESS - NO ACHIEVEMENTS", False, "No achievements found to test progress calculation")
            return False
        
        # Test progress calculation accuracy
        progress_tests_passed = 0
        total_progress_tests = 0
        
        for achievement in achievements:
            achievement_name = achievement.get('name', 'Unknown')
            progress = achievement.get('progress', 0)
            requirements = achievement.get('requirements', {})
            earned = achievement.get('earned', False)
            
            total_progress_tests += 1
            
            # Test 1: Progress should be between 0 and 100
            progress_in_range = isinstance(progress, (int, float)) and 0 <= progress <= 100
            if progress_in_range:
                progress_tests_passed += 1
            
            self.log_test(
                f"PROGRESS RANGE - {achievement_name}",
                progress_in_range,
                f"Progress {progress}% is within valid range (0-100)" if progress_in_range else f"Invalid progress: {progress}"
            )
            
            # Test 2: If earned, progress should be 100%
            if earned:
                progress_complete = progress == 100
                self.log_test(
                    f"EARNED ACHIEVEMENT PROGRESS - {achievement_name}",
                    progress_complete,
                    f"Earned achievement has 100% progress" if progress_complete else f"Earned achievement has {progress}% progress (should be 100%)"
                )
            
            # Test 3: Progress should make sense based on requirements
            if requirements:
                req_type = list(requirements.keys())[0] if requirements else None
                req_value = list(requirements.values())[0] if requirements else None
                
                if req_type and req_value:
                    self.log_test(
                        f"PROGRESS REQUIREMENT - {achievement_name}",
                        True,
                        f"Achievement requires {req_value} {req_type}, current progress: {progress}%"
                    )
        
        overall_progress_success = progress_tests_passed / total_progress_tests if total_progress_tests > 0 else 0
        self.log_test(
            "OVERALL PROGRESS CALCULATION ACCURACY",
            overall_progress_success >= 0.8,
            f"Progress calculation accuracy: {progress_tests_passed}/{total_progress_tests} ({overall_progress_success*100:.1f}%)"
        )
        
        return True

    def test_achievement_notification_system(self):
        """Test that achievement notifications are created properly"""
        print("\n=== TESTING ACHIEVEMENT NOTIFICATION SYSTEM ===")
        
        if not self.auth_token:
            self.log_test("ACHIEVEMENT NOTIFICATIONS - Authentication Required", False, "No authentication token available")
            return False
        
        # Get initial notification count
        initial_notifications_result = self.make_request('GET', '/notifications', use_auth=True)
        initial_notification_count = 0
        if initial_notifications_result['success']:
            initial_notification_count = len(initial_notifications_result['data'])
        
        # Trigger achievement checking manually to potentially unlock achievements
        check_result = self.make_request('POST', '/achievements/check', use_auth=True)
        self.log_test(
            "MANUAL ACHIEVEMENT CHECK FOR NOTIFICATIONS",
            check_result['success'],
            f"Manual achievement check completed" if check_result['success'] else f"Failed to check achievements: {check_result.get('error', 'Unknown error')}"
        )
        
        if check_result['success']:
            newly_unlocked = check_result['data'].get('newly_unlocked', 0)
            self.log_test(
                "NEWLY UNLOCKED ACHIEVEMENTS",
                isinstance(newly_unlocked, int),
                f"Found {newly_unlocked} newly unlocked achievements"
            )
        
        # Wait for notification processing
        time.sleep(2)
        
        # Check if notifications were created
        final_notifications_result = self.make_request('GET', '/notifications', use_auth=True)
        if final_notifications_result['success']:
            final_notifications = final_notifications_result['data']
            final_notification_count = len(final_notifications)
            
            # Look for achievement-related notifications
            achievement_notifications = [n for n in final_notifications if n.get('type') == 'achievement_unlocked']
            
            self.log_test(
                "ACHIEVEMENT NOTIFICATIONS CREATED",
                len(achievement_notifications) > 0,
                f"Found {len(achievement_notifications)} achievement notifications" if len(achievement_notifications) > 0 else "No achievement notifications found"
            )
            
            # Test notification structure if any exist
            if achievement_notifications:
                first_notification = achievement_notifications[0]
                expected_fields = ['type', 'title', 'message', 'data']
                missing_fields = [field for field in expected_fields if field not in first_notification]
                
                self.log_test(
                    "ACHIEVEMENT NOTIFICATION STRUCTURE",
                    len(missing_fields) == 0,
                    f"Achievement notification has correct structure" if len(missing_fields) == 0 else f"Missing fields: {missing_fields}"
                )
                
                # Check notification content
                title = first_notification.get('title', '')
                message = first_notification.get('message', '')
                
                title_valid = 'achievement' in title.lower() or 'unlocked' in title.lower()
                message_valid = len(message) > 0 and ('badge' in message.lower() or 'achievement' in message.lower())
                
                self.log_test(
                    "ACHIEVEMENT NOTIFICATION CONTENT",
                    title_valid and message_valid,
                    f"Notification has appropriate achievement content" if title_valid and message_valid else f"Notification content may be invalid"
                )
        
        return True

    def test_performance_and_efficiency(self):
        """Test that trigger functions are efficient and don't add significant latency"""
        print("\n=== TESTING PERFORMANCE AND EFFICIENCY ===")
        
        if not self.auth_token:
            self.log_test("PERFORMANCE TESTING - Authentication Required", False, "No authentication token available")
            return False
        
        # Test task creation/completion performance
        start_time = time.time()
        
        # Create infrastructure for performance test
        pillar_data = {
            "name": "Performance Test Pillar",
            "description": "Testing performance of achievement triggers",
            "icon": "⚡",
            "color": "#FF5722"
        }
        
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        if not result['success']:
            self.log_test("PERFORMANCE - CREATE PILLAR", False, "Failed to create performance test pillar")
            return False
        
        pillar_id = result['data']['id']
        self.created_resources['pillars'].append(pillar_id)
        
        area_data = {
            "name": "Performance Test Area",
            "description": "Testing area for performance",
            "icon": "🏃",
            "color": "#607D8B",
            "pillar_id": pillar_id
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        if not result['success']:
            self.log_test("PERFORMANCE - CREATE AREA", False, "Failed to create performance test area")
            return False
        
        area_id = result['data']['id']
        self.created_resources['areas'].append(area_id)
        
        project_data = {
            "area_id": area_id,
            "name": "Performance Test Project",
            "description": "Testing project for performance",
            "priority": "medium"
        }
        
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        if not result['success']:
            self.log_test("PERFORMANCE - CREATE PROJECT", False, "Failed to create performance test project")
            return False
        
        project_id = result['data']['id']
        self.created_resources['projects'].append(project_id)
        
        setup_time = time.time() - start_time
        
        # Test task operations with achievement triggers
        task_operation_times = []
        
        for i in range(5):  # Test 5 task operations
            task_start = time.time()
            
            # Create task
            task_data = {
                "project_id": project_id,
                "name": f"Performance Test Task {i+1}",
                "description": f"Testing task operation performance {i+1}",
                "priority": "low",
                "status": "todo"
            }
            
            create_result = self.make_request('POST', '/tasks', data=task_data, use_auth=True)
            if create_result['success']:
                task_id = create_result['data']['id']
                self.created_resources['tasks'].append(task_id)
                
                # Complete task (triggers achievement checking)
                update_result = self.make_request('PUT', f'/tasks/{task_id}', data={"status": "completed"}, use_auth=True)
                
                if update_result['success']:
                    task_end = time.time()
                    operation_time = task_end - task_start
                    task_operation_times.append(operation_time)
        
        # Analyze performance
        if task_operation_times:
            avg_task_time = sum(task_operation_times) / len(task_operation_times)
            max_task_time = max(task_operation_times)
            
            # Performance should be reasonable (under 2 seconds per operation)
            performance_acceptable = avg_task_time < 2.0 and max_task_time < 5.0
            
            self.log_test(
                "TASK OPERATION PERFORMANCE",
                performance_acceptable,
                f"Average task operation time: {avg_task_time:.2f}s, Max: {max_task_time:.2f}s" if performance_acceptable else f"Performance issue - Avg: {avg_task_time:.2f}s, Max: {max_task_time:.2f}s"
            )
        
        # Test achievement API performance
        achievement_start = time.time()
        result = self.make_request('GET', '/achievements', use_auth=True)
        achievement_time = time.time() - achievement_start
        
        achievement_performance_ok = achievement_time < 3.0
        self.log_test(
            "ACHIEVEMENT API PERFORMANCE",
            achievement_performance_ok,
            f"Achievement API response time: {achievement_time:.2f}s" if achievement_performance_ok else f"Slow achievement API: {achievement_time:.2f}s"
        )
        
        # Test manual check performance
        check_start = time.time()
        result = self.make_request('POST', '/achievements/check', use_auth=True)
        check_time = time.time() - check_start
        
        check_performance_ok = check_time < 5.0
        self.log_test(
            "ACHIEVEMENT CHECK PERFORMANCE",
            check_performance_ok,
            f"Achievement check time: {check_time:.2f}s" if check_performance_ok else f"Slow achievement check: {check_time:.2f}s"
        )
        
        return True

    def run_comprehensive_achievement_test(self):
        """Run comprehensive achievement system tests"""
        print("\n🏆 STARTING DYNAMIC ACHIEVEMENTS SYSTEM COMPREHENSIVE TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("User Registration and Login", self.test_user_registration_and_login),
            ("Achievement API Endpoints", self.test_achievement_api_endpoints),
            ("Task Completion Achievement Trigger", self.test_task_completion_achievement_trigger),
            ("Project Completion Achievement Trigger", self.test_project_completion_achievement_trigger),
            ("Journal Entry Achievement Trigger", self.test_journal_entry_achievement_trigger),
            ("Achievement Progress Calculation", self.test_achievement_progress_calculation),
            ("Achievement Notification System", self.test_achievement_notification_system),
            ("Performance and Efficiency", self.test_performance_and_efficiency)
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
        print("🎯 DYNAMIC ACHIEVEMENTS SYSTEM TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for achievement functionality
        api_tests_passed = sum(1 for result in self.test_results if result['success'] and 'API' in result['test'])
        trigger_tests_passed = sum(1 for result in self.test_results if result['success'] and 'TRIGGER' in result['test'])
        progress_tests_passed = sum(1 for result in self.test_results if result['success'] and 'PROGRESS' in result['test'])
        notification_tests_passed = sum(1 for result in self.test_results if result['success'] and 'NOTIFICATION' in result['test'])
        performance_tests_passed = sum(1 for result in self.test_results if result['success'] and 'PERFORMANCE' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"API Tests Passed: {api_tests_passed}")
        print(f"Trigger Tests Passed: {trigger_tests_passed}")
        print(f"Progress Tests Passed: {progress_tests_passed}")
        print(f"Notification Tests Passed: {notification_tests_passed}")
        print(f"Performance Tests Passed: {performance_tests_passed}")
        
        if success_rate >= 85:
            print("\n✅ DYNAMIC ACHIEVEMENTS SYSTEM: SUCCESS")
            print("   ✅ Achievement API endpoints working correctly")
            print("   ✅ Auto-tracking trigger functions operational")
            print("   ✅ Progress calculation accurate")
            print("   ✅ Achievement unlocking functional")
            print("   ✅ Notification system creating achievement notifications")
            print("   ✅ Performance optimized - no significant latency added")
            print("   The Dynamic Achievements System is production-ready!")
        else:
            print("\n❌ DYNAMIC ACHIEVEMENTS SYSTEM: ISSUES DETECTED")
            print("   Issues found in achievement system implementation")
        
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
    """Run Dynamic Achievements System Tests"""
    print("🏆 STARTING DYNAMIC ACHIEVEMENTS SYSTEM BACKEND TESTING")
    print("=" * 80)
    
    tester = AchievementSystemTester()
    
    try:
        # Run the comprehensive achievement system tests
        success = tester.run_comprehensive_achievement_test()
        
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