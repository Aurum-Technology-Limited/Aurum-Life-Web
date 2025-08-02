#!/usr/bin/env python3
"""
ALIGNMENT SCORE SYSTEM BACKEND TESTING
Testing the new Alignment Score system backend implementation.

FOCUS AREAS:
1. Alignment Score API Endpoints:
   - GET /api/alignment/dashboard - comprehensive alignment data
   - GET /api/alignment/weekly-score - rolling 7-day score
   - GET /api/alignment/monthly-score - current month score
   - GET /api/alignment/monthly-goal - user's monthly goal
   - POST /api/alignment/monthly-goal - set user's monthly goal

2. Task Completion Hook:
   - PUT /api/tasks/{task_id} - automatic alignment score calculation when completing tasks
   - Verify additive scoring algorithm: Base (5) + Task Priority (10) + Project Priority (15) + Area Importance (20) = up to 50 points

TESTING SCENARIOS:
1. Get initial dashboard data (should show 0 scores, no goal set)
2. Set a monthly goal (e.g., 500 points)
3. Complete a few tasks and verify alignment scores are calculated and recorded
4. Verify rolling weekly score updates correctly
5. Test that high-priority tasks in high-priority projects in important areas earn maximum points

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "http://localhost:8001/api"

class AlignmentScoreAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Use the specified test credentials
        self.test_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.test_user_password = "password"
        self.created_resources = []  # Track created resources for cleanup
        
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
        
        if result['success'] and 'access_token' in result['data']:
            self.auth_token = result['data']['access_token']
            self.log_test(
                "USER AUTHENTICATION",
                True,
                f"Successfully authenticated user {self.test_user_email}"
            )
            return True
        else:
            self.log_test(
                "USER AUTHENTICATION",
                False,
                f"Failed to authenticate user {self.test_user_email}",
                result
            )
            return False

    def test_alignment_dashboard_endpoint(self):
        """Test GET /api/alignment/dashboard endpoint"""
        print("\n=== TESTING ALIGNMENT DASHBOARD ENDPOINT ===")
        
        result = self.make_request('GET', '/alignment/dashboard', use_auth=True)
        
        if result['success']:
            data = result['data']
            required_fields = ['rolling_weekly_score', 'monthly_score', 'monthly_goal', 'progress_percentage', 'has_goal_set']
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                self.log_test(
                    "ALIGNMENT DASHBOARD STRUCTURE",
                    False,
                    f"Missing required fields: {missing_fields}",
                    data
                )
                return False
            
            self.log_test(
                "ALIGNMENT DASHBOARD ENDPOINT",
                True,
                f"Dashboard data retrieved successfully. Weekly: {data['rolling_weekly_score']}, Monthly: {data['monthly_score']}, Goal: {data['monthly_goal']}"
            )
            return True
        else:
            self.log_test(
                "ALIGNMENT DASHBOARD ENDPOINT",
                False,
                f"Failed to retrieve dashboard data",
                result
            )
            return False

    def test_weekly_score_endpoint(self):
        """Test GET /api/alignment/weekly-score endpoint"""
        print("\n=== TESTING WEEKLY SCORE ENDPOINT ===")
        
        result = self.make_request('GET', '/alignment/weekly-score', use_auth=True)
        
        if result['success']:
            data = result['data']
            if 'weekly_score' in data and isinstance(data['weekly_score'], int):
                self.log_test(
                    "WEEKLY SCORE ENDPOINT",
                    True,
                    f"Weekly score retrieved: {data['weekly_score']} points"
                )
                return True
            else:
                self.log_test(
                    "WEEKLY SCORE ENDPOINT",
                    False,
                    "Invalid weekly score response structure",
                    data
                )
                return False
        else:
            self.log_test(
                "WEEKLY SCORE ENDPOINT",
                False,
                "Failed to retrieve weekly score",
                result
            )
            return False

    def test_monthly_score_endpoint(self):
        """Test GET /api/alignment/monthly-score endpoint"""
        print("\n=== TESTING MONTHLY SCORE ENDPOINT ===")
        
        result = self.make_request('GET', '/alignment/monthly-score', use_auth=True)
        
        if result['success']:
            data = result['data']
            if 'monthly_score' in data and isinstance(data['monthly_score'], int):
                self.log_test(
                    "MONTHLY SCORE ENDPOINT",
                    True,
                    f"Monthly score retrieved: {data['monthly_score']} points"
                )
                return True
            else:
                self.log_test(
                    "MONTHLY SCORE ENDPOINT",
                    False,
                    "Invalid monthly score response structure",
                    data
                )
                return False
        else:
            self.log_test(
                "MONTHLY SCORE ENDPOINT",
                False,
                "Failed to retrieve monthly score",
                result
            )
            return False

    def test_get_monthly_goal_endpoint(self):
        """Test GET /api/alignment/monthly-goal endpoint"""
        print("\n=== TESTING GET MONTHLY GOAL ENDPOINT ===")
        
        result = self.make_request('GET', '/alignment/monthly-goal', use_auth=True)
        
        if result['success']:
            data = result['data']
            self.log_test(
                "GET MONTHLY GOAL ENDPOINT",
                True,
                f"Monthly goal retrieved: {data.get('monthly_goal', 'No goal set')}"
            )
            return True
        else:
            self.log_test(
                "GET MONTHLY GOAL ENDPOINT",
                False,
                "Failed to retrieve monthly goal",
                result
            )
            return False

    def test_set_monthly_goal_endpoint(self):
        """Test POST /api/alignment/monthly-goal endpoint"""
        print("\n=== TESTING SET MONTHLY GOAL ENDPOINT ===")
        
        # Set a test goal of 500 points
        goal_data = {"goal": 500}
        result = self.make_request('POST', '/alignment/monthly-goal', data=goal_data, use_auth=True)
        
        if result['success']:
            self.log_test(
                "SET MONTHLY GOAL ENDPOINT",
                True,
                f"Monthly goal set successfully to 500 points"
            )
            
            # Verify the goal was set by retrieving it
            verify_result = self.make_request('GET', '/alignment/monthly-goal', use_auth=True)
            if verify_result['success'] and verify_result['data'].get('monthly_goal') == 500:
                self.log_test(
                    "MONTHLY GOAL VERIFICATION",
                    True,
                    "Monthly goal correctly set and retrieved"
                )
                return True
            else:
                self.log_test(
                    "MONTHLY GOAL VERIFICATION",
                    False,
                    "Monthly goal not properly saved",
                    verify_result
                )
                return False
        else:
            # Check if this is a database schema issue
            if result['status_code'] == 500:
                self.log_test(
                    "SET MONTHLY GOAL ENDPOINT",
                    False,
                    "DATABASE SCHEMA ISSUE: monthly_alignment_goal column missing from user_profiles table",
                    result
                )
            else:
                self.log_test(
                    "SET MONTHLY GOAL ENDPOINT",
                    False,
                    "Failed to set monthly goal",
                    result
                )
            return False

    def create_test_hierarchy(self):
        """Create test pillar, area, project, and task for alignment score testing"""
        print("\n=== CREATING TEST HIERARCHY FOR ALIGNMENT TESTING ===")
        
        # Create a test pillar
        pillar_data = {
            "name": "Alignment Test Pillar",
            "description": "Test pillar for alignment score testing",
            "icon": "target",
            "color": "#FF6B6B",
            "time_allocation_percentage": 25
        }
        
        pillar_result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        if not pillar_result['success']:
            self.log_test(
                "CREATE TEST PILLAR",
                False,
                "Failed to create test pillar",
                pillar_result
            )
            return None
        
        pillar_id = pillar_result['data']['id']
        self.created_resources.append(('pillar', pillar_id))
        
        # Create a test area with high importance (5/5)
        area_data = {
            "name": "High Importance Test Area",
            "description": "Test area with maximum importance for alignment testing",
            "pillar_id": pillar_id,
            "importance": 5,
            "icon": "star",
            "color": "#4ECDC4"
        }
        
        area_result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        if not area_result['success']:
            self.log_test(
                "CREATE TEST AREA",
                False,
                "Failed to create test area",
                area_result
            )
            return None
        
        area_id = area_result['data']['id']
        self.created_resources.append(('area', area_id))
        
        # Create a test project with high priority
        project_data = {
            "name": "High Priority Test Project",
            "description": "Test project with high priority for alignment testing",
            "area_id": area_id,
            "priority": "high",
            "status": "In Progress"
        }
        
        project_result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        if not project_result['success']:
            self.log_test(
                "CREATE TEST PROJECT",
                False,
                "Failed to create test project",
                project_result
            )
            return None
        
        project_id = project_result['data']['id']
        self.created_resources.append(('project', project_id))
        
        # Create a test task with high priority (should earn maximum 50 points)
        task_data = {
            "name": "Maximum Points Test Task",
            "description": "High priority task in high priority project in high importance area",
            "project_id": project_id,
            "priority": "high",
            "status": "todo",
            "completed": False
        }
        
        task_result = self.make_request('POST', '/tasks', data=task_data, use_auth=True)
        if not task_result['success']:
            self.log_test(
                "CREATE TEST TASK",
                False,
                "Failed to create test task",
                task_result
            )
            return None
        
        task_id = task_result['data']['id']
        self.created_resources.append(('task', task_id))
        
        self.log_test(
            "CREATE TEST HIERARCHY",
            True,
            f"Successfully created test hierarchy: Pillar -> Area (importance 5) -> Project (high priority) -> Task (high priority)"
        )
        
        return {
            'pillar_id': pillar_id,
            'area_id': area_id,
            'project_id': project_id,
            'task_id': task_id
        }

    def test_task_completion_alignment_scoring(self):
        """Test that completing a task automatically calculates and records alignment scores"""
        print("\n=== TESTING TASK COMPLETION ALIGNMENT SCORING ===")
        
        # Create test hierarchy
        hierarchy = self.create_test_hierarchy()
        if not hierarchy:
            return False
        
        task_id = hierarchy['task_id']
        
        # Get initial scores for comparison
        initial_dashboard = self.make_request('GET', '/alignment/dashboard', use_auth=True)
        initial_weekly = initial_dashboard['data']['rolling_weekly_score'] if initial_dashboard['success'] else 0
        initial_monthly = initial_dashboard['data']['monthly_score'] if initial_dashboard['success'] else 0
        
        # Complete the task (should trigger alignment score calculation)
        task_update_data = {
            "completed": True,
            "status": "Completed"
        }
        
        result = self.make_request('PUT', f'/tasks/{task_id}', data=task_update_data, use_auth=True)
        
        if result['success']:
            # Check if alignment score was included in the response
            response_data = result['data']
            if 'alignment_score' in response_data:
                alignment_score = response_data['alignment_score']
                points_earned = alignment_score.get('points_earned', 0)
                breakdown = alignment_score.get('breakdown', {})
                
                # Verify maximum points (50) were earned
                expected_points = 50  # Base(5) + Task Priority(10) + Project Priority(15) + Area Importance(20)
                if points_earned == expected_points:
                    self.log_test(
                        "MAXIMUM ALIGNMENT POINTS",
                        True,
                        f"Task earned maximum {points_earned} points as expected. Breakdown: {breakdown}"
                    )
                else:
                    self.log_test(
                        "MAXIMUM ALIGNMENT POINTS",
                        False,
                        f"Expected {expected_points} points but got {points_earned}. Breakdown: {breakdown}"
                    )
                    return False
            else:
                # Check if this is because alignment_scores table doesn't exist
                self.log_test(
                    "ALIGNMENT SCORE IN RESPONSE",
                    False,
                    "DATABASE SCHEMA ISSUE: alignment_scores table likely missing from database",
                    response_data
                )
                return False
            
            # Wait a moment for the score to be recorded
            time.sleep(2)
            
            # Verify scores were updated in dashboard
            updated_dashboard = self.make_request('GET', '/alignment/dashboard', use_auth=True)
            if updated_dashboard['success']:
                new_weekly = updated_dashboard['data']['rolling_weekly_score']
                new_monthly = updated_dashboard['data']['monthly_score']
                
                weekly_increase = new_weekly - initial_weekly
                monthly_increase = new_monthly - initial_monthly
                
                if weekly_increase >= 50 and monthly_increase >= 50:
                    self.log_test(
                        "ALIGNMENT SCORES UPDATED",
                        True,
                        f"Scores updated correctly. Weekly increased by {weekly_increase}, Monthly increased by {monthly_increase}"
                    )
                    return True
                else:
                    self.log_test(
                        "ALIGNMENT SCORES UPDATED",
                        False,
                        f"Scores not updated as expected. Weekly increased by {weekly_increase}, Monthly increased by {monthly_increase}"
                    )
                    return False
            else:
                self.log_test(
                    "VERIFY SCORE UPDATE",
                    False,
                    "Failed to retrieve updated dashboard data",
                    updated_dashboard
                )
                return False
        else:
            self.log_test(
                "TASK COMPLETION",
                False,
                "Failed to complete test task",
                result
            )
            return False

    def test_authentication_requirements(self):
        """Test that all alignment endpoints require authentication"""
        print("\n=== TESTING AUTHENTICATION REQUIREMENTS ===")
        
        endpoints = [
            '/alignment/dashboard',
            '/alignment/weekly-score',
            '/alignment/monthly-score',
            '/alignment/monthly-goal'
        ]
        
        all_protected = True
        
        for endpoint in endpoints:
            result = self.make_request('GET', endpoint, use_auth=False)
            if result['status_code'] in [401, 403]:
                self.log_test(
                    f"AUTH REQUIRED - {endpoint}",
                    True,
                    f"Endpoint properly requires authentication (status: {result['status_code']})"
                )
            else:
                self.log_test(
                    f"AUTH REQUIRED - {endpoint}",
                    False,
                    f"Endpoint does not require authentication (status: {result['status_code']})",
                    result
                )
                all_protected = False
        
        # Test POST endpoint
        goal_data = {"goal": 100}
        result = self.make_request('POST', '/alignment/monthly-goal', data=goal_data, use_auth=False)
        if result['status_code'] in [401, 403]:
            self.log_test(
                "AUTH REQUIRED - POST /alignment/monthly-goal",
                True,
                f"POST endpoint properly requires authentication (status: {result['status_code']})"
            )
        else:
            self.log_test(
                "AUTH REQUIRED - POST /alignment/monthly-goal",
                False,
                f"POST endpoint does not require authentication (status: {result['status_code']})",
                result
            )
            all_protected = False
        
        return all_protected

    def cleanup_test_resources(self):
        """Clean up created test resources"""
        print("\n=== CLEANING UP TEST RESOURCES ===")
        
        cleanup_success = True
        
        # Clean up in reverse order (task -> project -> area -> pillar)
        for resource_type, resource_id in reversed(self.created_resources):
            endpoint = f"/{resource_type}s/{resource_id}"  # pluralize the resource type
            result = self.make_request('DELETE', endpoint, use_auth=True)
            
            if result['success']:
                self.log_test(
                    f"CLEANUP {resource_type.upper()}",
                    True,
                    f"Successfully deleted {resource_type} {resource_id}"
                )
            else:
                self.log_test(
                    f"CLEANUP {resource_type.upper()}",
                    False,
                    f"Failed to delete {resource_type} {resource_id}",
                    result
                )
                cleanup_success = False
        
        return cleanup_success

    def run_all_tests(self):
        """Run all alignment score system tests"""
        print("🎯 ALIGNMENT SCORE SYSTEM BACKEND TESTING")
        print("=" * 60)
        
        # Test basic connectivity
        if not self.test_basic_connectivity():
            print("❌ Cannot proceed - Backend API not accessible")
            return False
        
        # Test authentication
        if not self.test_user_authentication():
            print("❌ Cannot proceed - Authentication failed")
            return False
        
        # Test all alignment score endpoints
        tests = [
            self.test_alignment_dashboard_endpoint,
            self.test_weekly_score_endpoint,
            self.test_monthly_score_endpoint,
            self.test_get_monthly_goal_endpoint,
            self.test_set_monthly_goal_endpoint,
            self.test_task_completion_alignment_scoring,
            self.test_authentication_requirements
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} failed with exception: {e}")
        
        # Clean up test resources
        self.cleanup_test_resources()
        
        # Calculate success rate
        success_rate = (passed_tests / total_tests) * 100
        
        print("\n" + "=" * 60)
        print("🎯 ALIGNMENT SCORE SYSTEM TESTING SUMMARY")
        print("=" * 60)
        print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT - Alignment Score system is production-ready!")
        elif success_rate >= 75:
            print("✅ GOOD - Alignment Score system is mostly functional with minor issues")
        elif success_rate >= 50:
            print("⚠️  MODERATE - Alignment Score system has significant issues that need attention")
        else:
            print("❌ POOR - Alignment Score system has critical issues that must be fixed")
        
        return success_rate >= 75

if __name__ == "__main__":
    tester = AlignmentScoreAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)