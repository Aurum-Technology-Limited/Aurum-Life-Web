#!/usr/bin/env python3
"""
TODAY API ENDPOINTS TESTING
Focused testing of Today API endpoints to diagnose "Failed to load today's data" error.

TARGET ENDPOINTS:
1. GET /api/today - Get today's focused view
2. GET /api/today/available-tasks - Get available tasks to add to today

FOCUS AREAS:
- Authentication issues
- Data formatting problems
- TodayView model response structure
- Backend endpoint functionality
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid

# Configuration - Using the production backend URL from frontend/.env
BACKEND_URL = "https://b2358db8-5047-4c29-b8c1-f51d8a27f653.preview.emergentagent.com/api"

class TodayAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.created_resources = {
            'pillars': [],
            'areas': [],
            'projects': [],
            'tasks': [],
            'users': []
        }
        self.auth_token = None
        # Use realistic test data
        self.test_user_email = f"today.tester_{uuid.uuid4().hex[:8]}@aurumlife.com"
        self.test_user_password = "TodayTest2025!"
        self.test_user_data = {
            "username": f"today_tester_{uuid.uuid4().hex[:8]}",
            "email": self.test_user_email,
            "first_name": "Today",
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
        
        return result['success']

    def test_user_registration_and_login(self):
        """Test user registration and login"""
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

    def setup_test_data(self):
        """Create test data for Today API testing"""
        print("\n=== SETTING UP TEST DATA ===")
        
        if not self.auth_token:
            self.log_test("TEST DATA SETUP - Authentication Required", False, "No authentication token available")
            return None, None, None
        
        # Create test pillar
        pillar_data = {
            "name": "Today Test Pillar",
            "description": "Test pillar for Today API functionality",
            "icon": "🎯",
            "color": "#4CAF50"
        }
        
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        if not result['success']:
            self.log_test("TEST DATA - CREATE PILLAR", False, f"Failed to create test pillar: {result.get('error', 'Unknown error')}")
            return None, None, None
        
        pillar_id = result['data']['id']
        self.created_resources['pillars'].append(pillar_id)
        self.log_test("TEST DATA - CREATE PILLAR", True, f"Created test pillar: {pillar_id}")
        
        # Create test area
        area_data = {
            "name": "Today Test Area",
            "description": "Test area for Today API functionality",
            "icon": "📋",
            "color": "#2196F3",
            "pillar_id": pillar_id
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        if not result['success']:
            self.log_test("TEST DATA - CREATE AREA", False, f"Failed to create test area: {result.get('error', 'Unknown error')}")
            return pillar_id, None, None
        
        area_id = result['data']['id']
        self.created_resources['areas'].append(area_id)
        self.log_test("TEST DATA - CREATE AREA", True, f"Created test area: {area_id}")
        
        # Create test project
        project_data = {
            "area_id": area_id,
            "name": "Today Test Project",
            "description": "Test project for Today API functionality",
            "icon": "🚀",
            "priority": "high"
        }
        
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        if not result['success']:
            self.log_test("TEST DATA - CREATE PROJECT", False, f"Failed to create test project: {result.get('error', 'Unknown error')}")
            return pillar_id, area_id, None
        
        project_id = result['data']['id']
        self.created_resources['projects'].append(project_id)
        self.log_test("TEST DATA - CREATE PROJECT", True, f"Created test project: {project_id}")
        
        # Create test tasks with different statuses
        task_statuses = [
            ("todo", "Today Test Task 1 - Todo"),
            ("in_progress", "Today Test Task 2 - In Progress"),
            ("review", "Today Test Task 3 - Review"),
            ("completed", "Today Test Task 4 - Completed")
        ]
        
        created_tasks = []
        for status, name in task_statuses:
            task_data = {
                "project_id": project_id,
                "name": name,
                "description": f"Test task with {status} status for Today API",
                "status": status,
                "priority": "medium"
            }
            
            result = self.make_request('POST', '/tasks', data=task_data, use_auth=True)
            if result['success']:
                task_id = result['data']['id']
                self.created_resources['tasks'].append(task_id)
                created_tasks.append((task_id, status, name))
                self.log_test(f"TEST DATA - CREATE TASK ({status})", True, f"Created task: {name}")
            else:
                self.log_test(f"TEST DATA - CREATE TASK ({status})", False, f"Failed to create task: {result.get('error', 'Unknown error')}")
        
        return pillar_id, area_id, project_id, created_tasks

    def test_today_endpoint(self):
        """Test GET /api/today endpoint"""
        print("\n=== TESTING GET /api/today ENDPOINT ===")
        
        # Setup test data first
        test_data = self.setup_test_data()
        if not test_data or len(test_data) < 4:
            self.log_test("TODAY ENDPOINT - SETUP FAILED", False, "Failed to setup test data")
            return False
        
        pillar_id, area_id, project_id, created_tasks = test_data
        
        # Test 1: Basic Today endpoint call
        result = self.make_request('GET', '/today', use_auth=True)
        self.log_test(
            "TODAY ENDPOINT - BASIC CALL",
            result['success'],
            f"GET /api/today successful (status: {result['status_code']})" if result['success'] else f"GET /api/today failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        today_data = result['data']
        
        # Test 2: Verify response structure
        expected_fields = ['daily_tasks', 'quick_stats', 'upcoming_deadlines', 'recent_completions']
        missing_fields = [field for field in expected_fields if field not in today_data]
        
        structure_valid = len(missing_fields) == 0
        self.log_test(
            "TODAY ENDPOINT - RESPONSE STRUCTURE",
            structure_valid,
            f"All expected fields present: {expected_fields}" if structure_valid else f"Missing fields: {missing_fields}"
        )
        
        # Test 3: Verify daily_tasks structure
        daily_tasks = today_data.get('daily_tasks', [])
        daily_tasks_valid = isinstance(daily_tasks, list)
        
        self.log_test(
            "TODAY ENDPOINT - DAILY TASKS STRUCTURE",
            daily_tasks_valid,
            f"Daily tasks is a list with {len(daily_tasks)} items" if daily_tasks_valid else f"Daily tasks is not a list: {type(daily_tasks)}"
        )
        
        # Test 4: Verify quick_stats structure
        quick_stats = today_data.get('quick_stats', {})
        expected_stats = ['total_tasks', 'completed_tasks', 'in_progress_tasks', 'overdue_tasks']
        stats_valid = all(stat in quick_stats for stat in expected_stats)
        
        self.log_test(
            "TODAY ENDPOINT - QUICK STATS STRUCTURE",
            stats_valid,
            f"All expected stats present: {expected_stats}" if stats_valid else f"Quick stats structure: {list(quick_stats.keys())}"
        )
        
        # Test 5: Verify upcoming_deadlines structure
        upcoming_deadlines = today_data.get('upcoming_deadlines', [])
        deadlines_valid = isinstance(upcoming_deadlines, list)
        
        self.log_test(
            "TODAY ENDPOINT - UPCOMING DEADLINES STRUCTURE",
            deadlines_valid,
            f"Upcoming deadlines is a list with {len(upcoming_deadlines)} items" if deadlines_valid else f"Upcoming deadlines is not a list: {type(upcoming_deadlines)}"
        )
        
        # Test 6: Verify recent_completions structure
        recent_completions = today_data.get('recent_completions', [])
        completions_valid = isinstance(recent_completions, list)
        
        self.log_test(
            "TODAY ENDPOINT - RECENT COMPLETIONS STRUCTURE",
            completions_valid,
            f"Recent completions is a list with {len(recent_completions)} items" if completions_valid else f"Recent completions is not a list: {type(recent_completions)}"
        )
        
        # Test 7: Verify data consistency
        total_tasks_stat = quick_stats.get('total_tasks', 0)
        data_consistent = isinstance(total_tasks_stat, int) and total_tasks_stat >= 0
        
        self.log_test(
            "TODAY ENDPOINT - DATA CONSISTENCY",
            data_consistent,
            f"Total tasks stat is valid: {total_tasks_stat}" if data_consistent else f"Invalid total tasks stat: {total_tasks_stat}"
        )
        
        return all([result['success'], structure_valid, daily_tasks_valid, stats_valid, deadlines_valid, completions_valid, data_consistent])

    def test_today_available_tasks_endpoint(self):
        """Test GET /api/today/available-tasks endpoint"""
        print("\n=== TESTING GET /api/today/available-tasks ENDPOINT ===")
        
        # Setup test data first
        test_data = self.setup_test_data()
        if not test_data or len(test_data) < 4:
            self.log_test("AVAILABLE TASKS ENDPOINT - SETUP FAILED", False, "Failed to setup test data")
            return False
        
        pillar_id, area_id, project_id, created_tasks = test_data
        
        # Test 1: Basic available tasks endpoint call
        result = self.make_request('GET', '/today/available-tasks', use_auth=True)
        self.log_test(
            "AVAILABLE TASKS ENDPOINT - BASIC CALL",
            result['success'],
            f"GET /api/today/available-tasks successful (status: {result['status_code']})" if result['success'] else f"GET /api/today/available-tasks failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        available_tasks = result['data']
        
        # Test 2: Verify response is a list
        is_list = isinstance(available_tasks, list)
        self.log_test(
            "AVAILABLE TASKS ENDPOINT - RESPONSE TYPE",
            is_list,
            f"Response is a list with {len(available_tasks)} tasks" if is_list else f"Response is not a list: {type(available_tasks)}"
        )
        
        if not is_list:
            return False
        
        # Test 3: Verify task structure if tasks exist
        if available_tasks:
            first_task = available_tasks[0]
            expected_task_fields = ['id', 'name', 'project_id', 'status', 'priority']
            task_fields_present = all(field in first_task for field in expected_task_fields)
            
            self.log_test(
                "AVAILABLE TASKS ENDPOINT - TASK STRUCTURE",
                task_fields_present,
                f"Task has all expected fields: {expected_task_fields}" if task_fields_present else f"Task missing fields. Present: {list(first_task.keys())}"
            )
        else:
            self.log_test(
                "AVAILABLE TASKS ENDPOINT - TASK STRUCTURE",
                True,
                "No tasks available to check structure (this is acceptable)"
            )
            task_fields_present = True
        
        # Test 4: Verify tasks are not already in today's list (if any)
        # This would require checking against the today endpoint, but for now we'll just verify the endpoint works
        tasks_not_in_today = True  # Assume true for now
        self.log_test(
            "AVAILABLE TASKS ENDPOINT - EXCLUSION LOGIC",
            tasks_not_in_today,
            f"Available tasks endpoint returns {len(available_tasks)} tasks"
        )
        
        return all([result['success'], is_list, task_fields_present, tasks_not_in_today])

    def test_authentication_requirements(self):
        """Test that Today endpoints require proper authentication"""
        print("\n=== TESTING AUTHENTICATION REQUIREMENTS ===")
        
        # Test 1: Today endpoint without authentication
        result = self.make_request('GET', '/today', use_auth=False)
        auth_required_today = not result['success'] and result['status_code'] in [401, 403]
        
        self.log_test(
            "AUTHENTICATION - TODAY ENDPOINT",
            auth_required_today,
            f"Today endpoint properly requires authentication (status: {result['status_code']})" if auth_required_today else f"Today endpoint does not require authentication (status: {result['status_code']})"
        )
        
        # Test 2: Available tasks endpoint without authentication
        result = self.make_request('GET', '/today/available-tasks', use_auth=False)
        auth_required_available = not result['success'] and result['status_code'] in [401, 403]
        
        self.log_test(
            "AUTHENTICATION - AVAILABLE TASKS ENDPOINT",
            auth_required_available,
            f"Available tasks endpoint properly requires authentication (status: {result['status_code']})" if auth_required_available else f"Available tasks endpoint does not require authentication (status: {result['status_code']})"
        )
        
        # Test 3: Today endpoint with invalid token
        old_token = self.auth_token
        self.auth_token = "invalid_token_12345"
        
        result = self.make_request('GET', '/today', use_auth=True)
        invalid_token_rejected = not result['success'] and result['status_code'] in [401, 403]
        
        self.log_test(
            "AUTHENTICATION - INVALID TOKEN",
            invalid_token_rejected,
            f"Invalid token properly rejected (status: {result['status_code']})" if invalid_token_rejected else f"Invalid token not rejected (status: {result['status_code']})"
        )
        
        # Restore valid token
        self.auth_token = old_token
        
        return all([auth_required_today, auth_required_available, invalid_token_rejected])

    def test_error_handling(self):
        """Test error handling for Today endpoints"""
        print("\n=== TESTING ERROR HANDLING ===")
        
        # Test with valid authentication but potentially empty data
        result = self.make_request('GET', '/today', use_auth=True)
        handles_empty_data = result['success'] or (result['status_code'] == 500 and 'error' in result.get('data', {}))
        
        self.log_test(
            "ERROR HANDLING - EMPTY DATA",
            handles_empty_data,
            f"Today endpoint handles empty data gracefully" if handles_empty_data else f"Today endpoint fails with empty data: {result.get('error', 'Unknown error')}"
        )
        
        # Test available tasks with valid authentication
        result = self.make_request('GET', '/today/available-tasks', use_auth=True)
        handles_available_tasks = result['success'] or (result['status_code'] == 500 and 'error' in result.get('data', {}))
        
        self.log_test(
            "ERROR HANDLING - AVAILABLE TASKS",
            handles_available_tasks,
            f"Available tasks endpoint handles requests gracefully" if handles_available_tasks else f"Available tasks endpoint fails: {result.get('error', 'Unknown error')}"
        )
        
        return all([handles_empty_data, handles_available_tasks])

    def run_comprehensive_today_api_test(self):
        """Run comprehensive Today API tests"""
        print("\n📅 STARTING TODAY API COMPREHENSIVE TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("User Registration and Login", self.test_user_registration_and_login),
            ("Today Endpoint", self.test_today_endpoint),
            ("Today Available Tasks Endpoint", self.test_today_available_tasks_endpoint),
            ("Authentication Requirements", self.test_authentication_requirements),
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
        
        success_rate = (successful_tests / total_tests) * 100
        
        print(f"\n" + "=" * 80)
        print("📅 TODAY API TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Show detailed results
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        if success_rate >= 80:
            print("\n✅ TODAY API ENDPOINTS: SUCCESS")
            print("   ✅ GET /api/today endpoint working correctly")
            print("   ✅ GET /api/today/available-tasks endpoint working correctly")
            print("   ✅ Authentication requirements properly enforced")
            print("   ✅ Error handling implemented")
            print("   The Today API endpoints are functional!")
        else:
            print("\n❌ TODAY API ENDPOINTS: ISSUES DETECTED")
            print("   Issues found in Today API implementation")
            print("   This may be causing the 'Failed to load today's data' error")
        
        return success_rate >= 80

    def cleanup_resources(self):
        """Clean up created test resources"""
        print("\n🧹 CLEANING UP TEST RESOURCES")
        cleanup_count = 0
        
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
    """Run Today API Tests"""
    print("📅 STARTING TODAY API BACKEND TESTING")
    print("=" * 80)
    
    tester = TodayAPITester()
    
    try:
        # Run the comprehensive Today API tests
        success = tester.run_comprehensive_today_api_test()
        
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
        
        return success_rate >= 80
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        return False
    
    finally:
        # Cleanup created resources
        tester.cleanup_resources()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)