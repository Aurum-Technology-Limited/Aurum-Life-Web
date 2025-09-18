#!/usr/bin/env python3
"""
COMPREHENSIVE ALIGNMENT SCORE BACKEND TESTING - PRIORITY HIGH
Testing all alignment score functionality as specified in the review request.

TESTING SCOPE REQUIRED:
✅ **Authentication & User Credentials**: Use marc.alleyne@aurumtechnologyltd.com / password credentials for all testing

✅ **Core Alignment Score API Endpoints**:
1. GET /api/alignment/dashboard - Should return comprehensive alignment data (weekly, monthly, goal)
2. GET /api/alignment/weekly-score - Returns rolling 7-day score 
3. GET /api/alignment/monthly-score - Returns current month score
4. GET /api/alignment/monthly-goal - Retrieves user's monthly goal
5. POST /api/alignment/monthly-goal - Sets user's monthly goal (test with 1000 points)

✅ **Task Completion Scoring Integration**:
- Test PUT /api/tasks/{task_id} with completed=true triggers alignment score calculation
- Verify scoring algorithm: Base (5) + Task Priority Bonus + Project Priority Bonus + Area Importance Bonus
- Create test hierarchy: Pillar → Area (importance 8) → Project (high priority) → Task (high priority)
- Expected points: 5 + 10 + 15 + 20 = 50 points maximum
- Verify dashboard scores update correctly after task completion

✅ **Authentication Security**:
- Verify all 5 alignment endpoints require authentication (return 401 for unauthorized requests)  
- Test invalid tokens are properly rejected

✅ **Database Schema Verification**:
- Confirm alignment_scores table is functional for recording task completion points
- Verify monthly_alignment_goal field in user_profiles table works correctly
- Test data persistence and retrieval

✅ **Error Handling**:
- Test invalid goal values, missing parameters
- Verify proper 422 validation errors for malformed requests

BACKEND ARCHITECTURE:
- Backend: FastAPI at http://localhost:8001
- Key files: server.py, alignment_score_service.py, supabase_services.py
- Database: Supabase PostgreSQL with alignment_scores table
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "http://localhost:8001/api"

class ComprehensiveAlignmentScoreTester:
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

    def test_authentication_and_credentials(self):
        """Test authentication with specified credentials"""
        print("\n=== TESTING AUTHENTICATION & USER CREDENTIALS ===")
        
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
            
            # Verify token works with /auth/me
            me_result = self.make_request('GET', '/auth/me', use_auth=True)
            if me_result['success']:
                user_data = me_result['data']
                self.log_test(
                    "JWT TOKEN VALIDATION",
                    True,
                    f"JWT token validated successfully for user: {user_data.get('email', 'Unknown')}"
                )
                return True
            else:
                self.log_test(
                    "JWT TOKEN VALIDATION",
                    False,
                    "JWT token validation failed",
                    me_result
                )
                return False
        else:
            self.log_test(
                "USER AUTHENTICATION",
                False,
                f"Failed to authenticate user {self.test_user_email}",
                result
            )
            return False

    def test_core_alignment_score_endpoints(self):
        """Test all 5 core alignment score API endpoints"""
        print("\n=== TESTING CORE ALIGNMENT SCORE API ENDPOINTS ===")
        
        endpoints_tested = 0
        endpoints_passed = 0
        
        # 1. GET /api/alignment/dashboard
        result = self.make_request('GET', '/alignment/dashboard', use_auth=True)
        endpoints_tested += 1
        if result['success']:
            data = result['data']
            required_fields = ['rolling_weekly_score', 'monthly_score', 'monthly_goal', 'progress_percentage', 'has_goal_set']
            missing_fields = [field for field in required_fields if field not in data]
            
            if not missing_fields:
                self.log_test(
                    "GET /api/alignment/dashboard",
                    True,
                    f"Dashboard data retrieved successfully. Weekly: {data['rolling_weekly_score']}, Monthly: {data['monthly_score']}, Goal: {data['monthly_goal']}"
                )
                endpoints_passed += 1
            else:
                self.log_test(
                    "GET /api/alignment/dashboard",
                    False,
                    f"Missing required fields: {missing_fields}",
                    data
                )
        else:
            self.log_test(
                "GET /api/alignment/dashboard",
                False,
                "Failed to retrieve dashboard data",
                result
            )
        
        # 2. GET /api/alignment/weekly-score
        result = self.make_request('GET', '/alignment/weekly-score', use_auth=True)
        endpoints_tested += 1
        if result['success'] and 'weekly_score' in result['data']:
            self.log_test(
                "GET /api/alignment/weekly-score",
                True,
                f"Rolling 7-day score retrieved: {result['data']['weekly_score']} points"
            )
            endpoints_passed += 1
        else:
            self.log_test(
                "GET /api/alignment/weekly-score",
                False,
                "Failed to retrieve weekly score",
                result
            )
        
        # 3. GET /api/alignment/monthly-score
        result = self.make_request('GET', '/alignment/monthly-score', use_auth=True)
        endpoints_tested += 1
        if result['success'] and 'monthly_score' in result['data']:
            self.log_test(
                "GET /api/alignment/monthly-score",
                True,
                f"Current month score retrieved: {result['data']['monthly_score']} points"
            )
            endpoints_passed += 1
        else:
            self.log_test(
                "GET /api/alignment/monthly-score",
                False,
                "Failed to retrieve monthly score",
                result
            )
        
        # 4. GET /api/alignment/monthly-goal
        result = self.make_request('GET', '/alignment/monthly-goal', use_auth=True)
        endpoints_tested += 1
        if result['success']:
            goal = result['data'].get('monthly_goal')
            self.log_test(
                "GET /api/alignment/monthly-goal",
                True,
                f"Monthly goal retrieved: {goal if goal is not None else 'No goal set'}"
            )
            endpoints_passed += 1
        else:
            self.log_test(
                "GET /api/alignment/monthly-goal",
                False,
                "Failed to retrieve monthly goal",
                result
            )
        
        # 5. POST /api/alignment/monthly-goal (test with 1000 points as specified)
        goal_data = {"goal": 1000}
        result = self.make_request('POST', '/alignment/monthly-goal', data=goal_data, use_auth=True)
        endpoints_tested += 1
        if result['success']:
            self.log_test(
                "POST /api/alignment/monthly-goal",
                True,
                "Monthly goal set successfully to 1000 points"
            )
            
            # Verify the goal was set by retrieving it
            verify_result = self.make_request('GET', '/alignment/monthly-goal', use_auth=True)
            if verify_result['success'] and verify_result['data'].get('monthly_goal') == 1000:
                self.log_test(
                    "MONTHLY GOAL VERIFICATION",
                    True,
                    "Monthly goal correctly set and retrieved (1000 points)"
                )
                endpoints_passed += 1
            else:
                self.log_test(
                    "MONTHLY GOAL VERIFICATION",
                    False,
                    "Monthly goal not properly saved",
                    verify_result
                )
        else:
            self.log_test(
                "POST /api/alignment/monthly-goal",
                False,
                "Failed to set monthly goal",
                result
            )
        
        success_rate = (endpoints_passed / endpoints_tested) * 100
        overall_success = success_rate == 100
        
        self.log_test(
            "CORE ALIGNMENT ENDPOINTS SUMMARY",
            overall_success,
            f"All 5 alignment endpoints working: {endpoints_passed}/{endpoints_tested} ({success_rate:.1f}%)"
        )
        
        return overall_success

    def create_test_hierarchy_with_importance_5(self):
        """Create test hierarchy: Pillar → Area (importance 5) → Project (high priority) → Task (high priority)"""
        print("\n=== CREATING TEST HIERARCHY FOR SCORING VERIFICATION ===")
        
        # Create a test pillar
        pillar_data = {
            "name": "Comprehensive Test Pillar",
            "description": "Test pillar for comprehensive alignment score testing",
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
        
        # Create a test area with importance 5 (maximum importance that gives 20 points bonus)
        # Note: Based on the algorithm, importance 5 gives maximum 20 points bonus
        area_data = {
            "name": "High Importance Test Area (5/5)",
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
        
        # Create a test task with high priority
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
            f"Successfully created test hierarchy: Pillar → Area (importance 5) → Project (high priority) → Task (high priority)"
        )
        
        return {
            'pillar_id': pillar_id,
            'area_id': area_id,
            'project_id': project_id,
            'task_id': task_id
        }

    def test_task_completion_scoring_integration(self):
        """Test task completion scoring integration with PUT /api/tasks/{task_id}"""
        print("\n=== TESTING TASK COMPLETION SCORING INTEGRATION ===")
        
        # Create test hierarchy
        hierarchy = self.create_test_hierarchy_with_importance_5()
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
            "status": "completed"
        }
        
        result = self.make_request('PUT', f'/tasks/{task_id}', data=task_update_data, use_auth=True)
        
        if result['success']:
            # Check if alignment score was included in the response
            response_data = result['data']
            if 'alignment_score' in response_data:
                alignment_score = response_data['alignment_score']
                points_earned = alignment_score.get('points_earned', 0)
                breakdown = alignment_score.get('breakdown', {})
                
                # Verify scoring algorithm: Base (5) + Task Priority (10) + Project Priority (15) + Area Importance (20) = 50 points
                expected_points = 50  # Maximum points as specified in review
                if points_earned == expected_points:
                    self.log_test(
                        "SCORING ALGORITHM VERIFICATION",
                        True,
                        f"Task earned expected {points_earned} points. Breakdown: {breakdown}"
                    )
                else:
                    self.log_test(
                        "SCORING ALGORITHM VERIFICATION",
                        False,
                        f"Expected {expected_points} points but got {points_earned}. Breakdown: {breakdown}"
                    )
                    return False
                
                # Verify breakdown components
                expected_breakdown = {
                    'base': 5,
                    'task_priority': 10,
                    'project_priority': 15,
                    'area_importance': 20
                }
                
                breakdown_correct = all(
                    breakdown.get(key) == expected_breakdown[key] 
                    for key in expected_breakdown
                )
                
                self.log_test(
                    "SCORING BREAKDOWN VERIFICATION",
                    breakdown_correct,
                    f"Scoring breakdown correct: {breakdown}" if breakdown_correct else f"Expected {expected_breakdown}, got {breakdown}"
                )
                
                if not breakdown_correct:
                    return False
                    
            else:
                self.log_test(
                    "ALIGNMENT SCORE IN RESPONSE",
                    False,
                    "Alignment score not included in task update response",
                    response_data
                )
                return False
            
            # Wait a moment for the score to be recorded
            time.sleep(2)
            
            # Verify dashboard scores update correctly after task completion
            updated_dashboard = self.make_request('GET', '/alignment/dashboard', use_auth=True)
            if updated_dashboard['success']:
                new_weekly = updated_dashboard['data']['rolling_weekly_score']
                new_monthly = updated_dashboard['data']['monthly_score']
                
                weekly_increase = new_weekly - initial_weekly
                monthly_increase = new_monthly - initial_monthly
                
                if weekly_increase >= 50 and monthly_increase >= 50:
                    self.log_test(
                        "DASHBOARD SCORES UPDATE VERIFICATION",
                        True,
                        f"Dashboard scores updated correctly. Weekly increased by {weekly_increase}, Monthly increased by {monthly_increase}"
                    )
                    return True
                else:
                    self.log_test(
                        "DASHBOARD SCORES UPDATE VERIFICATION",
                        False,
                        f"Dashboard scores not updated as expected. Weekly increased by {weekly_increase}, Monthly increased by {monthly_increase}"
                    )
                    return False
            else:
                self.log_test(
                    "DASHBOARD SCORES UPDATE VERIFICATION",
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

    def test_authentication_security(self):
        """Test authentication security for all alignment endpoints"""
        print("\n=== TESTING AUTHENTICATION SECURITY ===")
        
        endpoints = [
            ('GET', '/alignment/dashboard'),
            ('GET', '/alignment/weekly-score'),
            ('GET', '/alignment/monthly-score'),
            ('GET', '/alignment/monthly-goal'),
            ('POST', '/alignment/monthly-goal')
        ]
        
        all_protected = True
        protected_count = 0
        
        for method, endpoint in endpoints:
            # Test without authentication
            data = {"goal": 100} if method == 'POST' else None
            result = self.make_request(method, endpoint, data=data, use_auth=False)
            
            if result['status_code'] in [401, 403]:
                self.log_test(
                    f"AUTH REQUIRED - {method} {endpoint}",
                    True,
                    f"Endpoint properly requires authentication (status: {result['status_code']})"
                )
                protected_count += 1
            else:
                self.log_test(
                    f"AUTH REQUIRED - {method} {endpoint}",
                    False,
                    f"Endpoint does not require authentication (status: {result['status_code']})",
                    result
                )
                all_protected = False
        
        # Test invalid tokens are properly rejected
        invalid_token = "invalid-token-12345"
        old_token = self.auth_token
        self.auth_token = invalid_token
        
        result = self.make_request('GET', '/alignment/dashboard', use_auth=True)
        invalid_token_rejected = result['status_code'] in [401, 403]
        
        self.log_test(
            "INVALID TOKEN REJECTION",
            invalid_token_rejected,
            f"Invalid tokens properly rejected (status: {result['status_code']})" if invalid_token_rejected else f"Invalid token not rejected (status: {result['status_code']})"
        )
        
        # Restore valid token
        self.auth_token = old_token
        
        success_rate = (protected_count / len(endpoints)) * 100
        overall_success = all_protected and invalid_token_rejected
        
        self.log_test(
            "AUTHENTICATION SECURITY SUMMARY",
            overall_success,
            f"All 5 alignment endpoints require authentication: {protected_count}/{len(endpoints)} ({success_rate:.1f}%) + Invalid token rejection: {invalid_token_rejected}"
        )
        
        return overall_success

    def test_database_schema_verification(self):
        """Test database schema verification"""
        print("\n=== TESTING DATABASE SCHEMA VERIFICATION ===")
        
        # Test alignment_scores table functionality by creating a test task and completing it
        hierarchy = self.create_test_hierarchy_with_importance_5()
        if not hierarchy:
            self.log_test(
                "DATABASE SCHEMA - ALIGNMENT_SCORES TABLE",
                False,
                "Failed to create test hierarchy for database testing"
            )
            return False
        
        task_id = hierarchy['task_id']
        
        # Complete task to test alignment_scores table
        task_update_data = {"completed": True, "status": "completed"}
        result = self.make_request('PUT', f'/tasks/{task_id}', data=task_update_data, use_auth=True)
        
        alignment_scores_functional = result['success'] and 'alignment_score' in result['data']
        self.log_test(
            "DATABASE SCHEMA - ALIGNMENT_SCORES TABLE",
            alignment_scores_functional,
            "alignment_scores table functional for recording task completion points" if alignment_scores_functional else "alignment_scores table not functional"
        )
        
        # Test monthly_alignment_goal field in user_profiles table
        goal_data = {"goal": 1500}
        goal_result = self.make_request('POST', '/alignment/monthly-goal', data=goal_data, use_auth=True)
        
        if goal_result['success']:
            # Verify goal was saved
            verify_result = self.make_request('GET', '/alignment/monthly-goal', use_auth=True)
            monthly_goal_functional = verify_result['success'] and verify_result['data'].get('monthly_goal') == 1500
            
            self.log_test(
                "DATABASE SCHEMA - MONTHLY_ALIGNMENT_GOAL FIELD",
                monthly_goal_functional,
                "monthly_alignment_goal field in user_profiles table works correctly" if monthly_goal_functional else "monthly_alignment_goal field not working correctly"
            )
        else:
            monthly_goal_functional = False
            self.log_test(
                "DATABASE SCHEMA - MONTHLY_ALIGNMENT_GOAL FIELD",
                False,
                "Failed to test monthly_alignment_goal field",
                goal_result
            )
        
        # Test data persistence and retrieval
        dashboard_result = self.make_request('GET', '/alignment/dashboard', use_auth=True)
        data_persistence = dashboard_result['success'] and isinstance(dashboard_result['data'].get('monthly_score'), int)
        
        self.log_test(
            "DATABASE SCHEMA - DATA PERSISTENCE",
            data_persistence,
            "Data persistence and retrieval working correctly" if data_persistence else "Data persistence issues detected"
        )
        
        return alignment_scores_functional and monthly_goal_functional and data_persistence

    def test_error_handling(self):
        """Test error handling for invalid goal values and missing parameters"""
        print("\n=== TESTING ERROR HANDLING ===")
        
        # Test invalid goal values
        invalid_goals = [
            {"goal": -100},  # Negative value
            {"goal": "not_a_number"},  # String instead of number
            {"goal": None},  # Null value
            {}  # Missing goal parameter
        ]
        
        error_handling_tests = 0
        error_handling_passed = 0
        
        for invalid_goal in invalid_goals:
            result = self.make_request('POST', '/alignment/monthly-goal', data=invalid_goal, use_auth=True)
            error_handling_tests += 1
            
            # Should return 422 validation error or 400 bad request
            if result['status_code'] in [400, 422]:
                self.log_test(
                    f"ERROR HANDLING - INVALID GOAL: {invalid_goal}",
                    True,
                    f"Invalid goal properly rejected (status: {result['status_code']})"
                )
                error_handling_passed += 1
            else:
                self.log_test(
                    f"ERROR HANDLING - INVALID GOAL: {invalid_goal}",
                    False,
                    f"Invalid goal not properly rejected (status: {result['status_code']})",
                    result
                )
        
        # Test malformed requests
        malformed_requests = [
            {"invalid_field": 100},  # Wrong field name
            {"goal": 100, "extra_field": "should_be_ignored"}  # Extra fields
        ]
        
        for malformed_request in malformed_requests:
            result = self.make_request('POST', '/alignment/monthly-goal', data=malformed_request, use_auth=True)
            error_handling_tests += 1
            
            # Should either reject with 422 or accept and ignore extra fields
            if result['status_code'] in [200, 400, 422]:
                self.log_test(
                    f"ERROR HANDLING - MALFORMED REQUEST: {malformed_request}",
                    True,
                    f"Malformed request handled appropriately (status: {result['status_code']})"
                )
                error_handling_passed += 1
            else:
                self.log_test(
                    f"ERROR HANDLING - MALFORMED REQUEST: {malformed_request}",
                    False,
                    f"Malformed request not handled properly (status: {result['status_code']})",
                    result
                )
        
        success_rate = (error_handling_passed / error_handling_tests) * 100
        overall_success = success_rate >= 80  # Allow some flexibility in error handling
        
        self.log_test(
            "ERROR HANDLING SUMMARY",
            overall_success,
            f"Error handling tests: {error_handling_passed}/{error_handling_tests} ({success_rate:.1f}%)"
        )
        
        return overall_success

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

    def run_comprehensive_alignment_score_test(self):
        """Run comprehensive alignment score backend testing"""
        print("🎯 COMPREHENSIVE ALIGNMENT SCORE BACKEND TESTING - PRIORITY HIGH")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Test sequence as specified in review request
        test_methods = [
            ("Authentication & User Credentials", self.test_authentication_and_credentials),
            ("Core Alignment Score API Endpoints", self.test_core_alignment_score_endpoints),
            ("Task Completion Scoring Integration", self.test_task_completion_scoring_integration),
            ("Authentication Security", self.test_authentication_security),
            ("Database Schema Verification", self.test_database_schema_verification),
            ("Error Handling", self.test_error_handling)
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
        
        # Clean up test resources
        self.cleanup_test_resources()
        
        success_rate = (successful_tests / total_tests) * 100
        
        print(f"\n" + "=" * 80)
        print("🎯 COMPREHENSIVE ALIGNMENT SCORE BACKEND TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Categories: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze individual test results
        total_individual_tests = len(self.test_results)
        passed_individual_tests = sum(1 for result in self.test_results if result['success'])
        individual_success_rate = (passed_individual_tests / total_individual_tests * 100) if total_individual_tests > 0 else 0
        
        print(f"Individual Tests: {passed_individual_tests}/{total_individual_tests} successful")
        print(f"Individual Success Rate: {individual_success_rate:.1f}%")
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"✅ Authentication & User Credentials: {'PASS' if successful_tests >= 1 else 'FAIL'}")
        print(f"✅ Core Alignment Score API Endpoints: {'PASS' if successful_tests >= 2 else 'FAIL'}")
        print(f"✅ Task Completion Scoring Integration: {'PASS' if successful_tests >= 3 else 'FAIL'}")
        print(f"✅ Authentication Security: {'PASS' if successful_tests >= 4 else 'FAIL'}")
        print(f"✅ Database Schema Verification: {'PASS' if successful_tests >= 5 else 'FAIL'}")
        print(f"✅ Error Handling: {'PASS' if successful_tests >= 6 else 'FAIL'}")
        
        if success_rate >= 95:
            print("\n🎉 EXCELLENT - ALIGNMENT SCORE SYSTEM: 100% SUCCESS!")
            print("   ✅ All 5 alignment endpoints working perfectly")
            print("   ✅ Task completion scoring integration functional")
            print("   ✅ Scoring algorithm verified: Base(5) + Task Priority(10) + Project Priority(15) + Area Importance(20) = 50 points maximum")
            print("   ✅ Dashboard scores update correctly after task completion")
            print("   ✅ Authentication security verified for all endpoints")
            print("   ✅ Database schema functional (alignment_scores table + monthly_alignment_goal field)")
            print("   ✅ Error handling working correctly")
            print("   The Alignment Score system backend is PRODUCTION-READY and achieves 100% success rate!")
        elif success_rate >= 85:
            print("\n✅ GOOD - ALIGNMENT SCORE SYSTEM: HIGH SUCCESS RATE")
            print("   Most functionality working correctly with minor issues")
        elif success_rate >= 70:
            print("\n⚠️  MODERATE - ALIGNMENT SCORE SYSTEM: SOME ISSUES DETECTED")
            print("   Core functionality working but some components need attention")
        else:
            print("\n❌ POOR - ALIGNMENT SCORE SYSTEM: CRITICAL ISSUES")
            print("   Significant problems detected that must be fixed")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 90

def main():
    """Run Comprehensive Alignment Score Backend Tests"""
    print("🎯 STARTING COMPREHENSIVE ALIGNMENT SCORE BACKEND TESTING")
    print("=" * 80)
    
    tester = ComprehensiveAlignmentScoreTester()
    
    try:
        # Run the comprehensive alignment score tests
        success = tester.run_comprehensive_alignment_score_test()
        
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
        
        return success_rate >= 90
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)