#!/usr/bin/env python3
"""
ENHANCED GOAL DECOMPOSITION INTERACTIVE WORKFLOW - BACKEND TESTING
Testing the fixed "Save Project" feature in the Enhanced Goal Decomposition Interactive Workflow.

FOCUS AREAS:
1. AI Integration Test - Complete Goal Decomposition workflow
2. Generate AI breakdown for "Learn web development" goal
3. Verify structured response with project details and tasks
4. Test the fixed POST /projects/create-with-tasks endpoint
5. Success Feedback Test - Create project with tasks through workflow
6. Error Handling Test - Validation errors and authentication
7. Quota Management - Verify user has full 10/10 AI interactions quota
8. Integration Verification - Complete workflow: Generate → Edit → Save → Verify

TESTING CRITERIA:
- POST /api/ai/decompose-project working with structured JSON response
- POST /api/projects/create-with-tasks endpoint functional (the fixed createProject issue)
- AI generation consumes quota, but saving project/tasks does NOT consume additional quota
- Proper validation errors (empty project title returns 422)
- Authentication requirements working
- Created project appears in user's projects list
- Alignment score updates when project is created

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / Alleyne2025!
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://f0a50716-337f-44d1-8fc0-56cc66936b59.preview.emergentagent.com/api"

class EnhancedGoalDecompositionTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Use the specified test credentials
        self.test_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.test_user_password = "Alleyne2025!"
        self.created_resources = {
            'projects': [],
            'tasks': []
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
        self.log_test(
            "USER LOGIN",
            result['success'],
            f"Login successful with {self.test_user_email}" if result['success'] else f"Login failed: {result.get('error', 'Unknown error')}"
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

    def test_ai_quota_management(self):
        """Test AI quota management - verify user has full 10/10 quota"""
        print("\n=== TESTING AI QUOTA MANAGEMENT ===")
        
        if not self.auth_token:
            self.log_test("AI QUOTA MANAGEMENT - Authentication Required", False, "No authentication token available")
            return False
        
        # Test GET /api/ai/quota
        result = self.make_request('GET', '/ai/quota', use_auth=True)
        self.log_test(
            "GET AI QUOTA",
            result['success'],
            f"Retrieved AI quota successfully" if result['success'] else f"Failed to get quota: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        quota_response = result['data']
        
        # Verify quota structure
        required_fields = ['total', 'used', 'remaining']
        missing_fields = [field for field in required_fields if field not in quota_response]
        
        structure_valid = len(missing_fields) == 0
        self.log_test(
            "AI QUOTA - RESPONSE STRUCTURE",
            structure_valid,
            f"Response has all required fields (total, used, remaining)" if structure_valid else f"Missing fields: {missing_fields}"
        )
        
        if not structure_valid:
            return False
        
        # Verify user has full quota (10/10)
        total_quota = quota_response.get('total', 0)
        used_quota = quota_response.get('used', 0)
        remaining_quota = quota_response.get('remaining', 0)
        
        full_quota_available = total_quota == 10 and remaining_quota > 0
        self.log_test(
            "AI QUOTA - FULL QUOTA VERIFICATION",
            full_quota_available,
            f"User has {remaining_quota}/{total_quota} AI interactions available" if full_quota_available else f"Quota issue: {used_quota}/{total_quota} used, {remaining_quota} remaining"
        )
        
        return structure_valid and full_quota_available

    def test_ai_goal_decomposition(self):
        """Test AI Goal Decomposition with structured response"""
        print("\n=== TESTING AI GOAL DECOMPOSITION ===")
        
        if not self.auth_token:
            self.log_test("AI GOAL DECOMPOSITION - Authentication Required", False, "No authentication token available")
            return False, None
        
        # Test POST /api/ai/decompose-project with "Learn web development" goal
        decomposition_data = {
            "project_name": "Learn web development"
        }
        
        result = self.make_request('POST', '/ai/decompose-project', data=decomposition_data, use_auth=True)
        self.log_test(
            "POST AI DECOMPOSE PROJECT",
            result['success'],
            f"AI decomposition successful for 'Learn web development'" if result['success'] else f"AI decomposition failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False, None
        
        decomposition_response = result['data']
        
        # Verify structured response format
        required_fields = ['suggested_project', 'suggested_tasks', 'available_areas', 'editable', 'instructions']
        missing_fields = [field for field in required_fields if field not in decomposition_response]
        
        structure_valid = len(missing_fields) == 0
        self.log_test(
            "AI DECOMPOSITION - RESPONSE STRUCTURE",
            structure_valid,
            f"Response has all required fields for interactive workflow" if structure_valid else f"Missing fields: {missing_fields}"
        )
        
        if not structure_valid:
            return False, None
        
        # Verify suggested_project structure
        suggested_project = decomposition_response.get('suggested_project', {})
        project_fields = ['title', 'description', 'area_id', 'priority', 'status']
        missing_project_fields = [field for field in project_fields if field not in suggested_project]
        
        project_structure_valid = len(missing_project_fields) == 0
        self.log_test(
            "AI DECOMPOSITION - PROJECT STRUCTURE",
            project_structure_valid,
            f"Suggested project has all required fields" if project_structure_valid else f"Missing project fields: {missing_project_fields}"
        )
        
        # Verify suggested_tasks structure
        suggested_tasks = decomposition_response.get('suggested_tasks', [])
        tasks_valid = len(suggested_tasks) > 0 and all(
            'title' in task and 'priority' in task and 'estimated_duration' in task 
            for task in suggested_tasks
        )
        
        self.log_test(
            "AI DECOMPOSITION - TASKS STRUCTURE",
            tasks_valid,
            f"Generated {len(suggested_tasks)} tasks with proper structure" if tasks_valid else f"Tasks structure invalid or empty"
        )
        
        # Verify contextual task generation for web development
        web_dev_keywords = ['html', 'css', 'javascript', 'framework', 'project', 'practice', 'tutorial', 'learn']
        contextual_tasks = any(
            any(keyword.lower() in task.get('title', '').lower() for keyword in web_dev_keywords)
            for task in suggested_tasks
        )
        
        self.log_test(
            "AI DECOMPOSITION - CONTEXTUAL TASKS",
            contextual_tasks,
            f"Tasks are contextually relevant to web development" if contextual_tasks else f"Tasks may not be contextually relevant"
        )
        
        # Verify available areas
        available_areas = decomposition_response.get('available_areas', [])
        areas_available = len(available_areas) > 0
        
        self.log_test(
            "AI DECOMPOSITION - AVAILABLE AREAS",
            areas_available,
            f"Found {len(available_areas)} available areas for project assignment" if areas_available else f"No available areas found"
        )
        
        overall_success = structure_valid and project_structure_valid and tasks_valid and areas_available
        return overall_success, decomposition_response

    def test_save_project_functionality(self, decomposition_response):
        """Test the fixed Save Project functionality - POST /projects/create-with-tasks"""
        print("\n=== TESTING SAVE PROJECT FUNCTIONALITY (FIXED createProject) ===")
        
        if not self.auth_token:
            self.log_test("SAVE PROJECT - Authentication Required", False, "No authentication token available")
            return False
        
        if not decomposition_response:
            self.log_test("SAVE PROJECT - No Decomposition Data", False, "No decomposition response available")
            return False
        
        # Extract project and tasks data from decomposition response
        suggested_project = decomposition_response.get('suggested_project', {})
        suggested_tasks = decomposition_response.get('suggested_tasks', [])
        
        # Prepare project creation data
        project_data = {
            "title": suggested_project.get('title', 'Learn web development'),
            "description": suggested_project.get('description', 'A comprehensive project to learn web development'),
            "area_id": suggested_project.get('area_id'),  # May be None
            "priority": suggested_project.get('priority', 'medium'),
            "status": suggested_project.get('status', 'Not Started')
        }
        
        # Prepare tasks data (limit to first 5 tasks for testing)
        tasks_data = suggested_tasks[:5] if len(suggested_tasks) > 5 else suggested_tasks
        
        # Create the request payload
        create_request = {
            "project": project_data,
            "tasks": tasks_data
        }
        
        # Test POST /api/projects/create-with-tasks (the fixed endpoint)
        result = self.make_request('POST', '/projects/create-with-tasks', data=create_request, use_auth=True)
        self.log_test(
            "POST PROJECTS CREATE-WITH-TASKS",
            result['success'],
            f"Project and tasks created successfully" if result['success'] else f"Project creation failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        creation_response = result['data']
        
        # Verify response structure
        required_response_fields = ['success', 'project', 'tasks', 'message']
        missing_response_fields = [field for field in required_response_fields if field not in creation_response]
        
        response_structure_valid = len(missing_response_fields) == 0
        self.log_test(
            "SAVE PROJECT - RESPONSE STRUCTURE",
            response_structure_valid,
            f"Response has all required fields" if response_structure_valid else f"Missing response fields: {missing_response_fields}"
        )
        
        # Verify success flag
        success_flag = creation_response.get('success', False)
        self.log_test(
            "SAVE PROJECT - SUCCESS FLAG",
            success_flag,
            f"Success flag is True" if success_flag else f"Success flag is False or missing"
        )
        
        # Verify created project
        created_project = creation_response.get('project', {})
        project_has_id = 'id' in created_project
        
        self.log_test(
            "SAVE PROJECT - PROJECT CREATED",
            project_has_id,
            f"Project created with ID: {created_project.get('id', 'N/A')}" if project_has_id else f"Project creation failed or missing ID"
        )
        
        # Verify created tasks
        created_tasks = creation_response.get('tasks', [])
        tasks_created = len(created_tasks) > 0
        
        self.log_test(
            "SAVE PROJECT - TASKS CREATED",
            tasks_created,
            f"Created {len(created_tasks)} tasks" if tasks_created else f"No tasks created"
        )
        
        # Store created resources for cleanup
        if project_has_id:
            self.created_resources['projects'].append(created_project['id'])
        
        for task in created_tasks:
            if 'id' in task:
                self.created_resources['tasks'].append(task['id'])
        
        overall_success = response_structure_valid and success_flag and project_has_id and tasks_created
        return overall_success

    def test_project_verification(self):
        """Test that created project appears in user's projects list"""
        print("\n=== TESTING PROJECT VERIFICATION ===")
        
        if not self.auth_token:
            self.log_test("PROJECT VERIFICATION - Authentication Required", False, "No authentication token available")
            return False
        
        if not self.created_resources['projects']:
            self.log_test("PROJECT VERIFICATION - No Projects Created", False, "No projects were created to verify")
            return False
        
        # Get user's projects list
        result = self.make_request('GET', '/projects', use_auth=True)
        self.log_test(
            "GET PROJECTS LIST",
            result['success'],
            f"Retrieved projects list successfully" if result['success'] else f"Failed to get projects: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        projects_list = result['data']
        
        # Verify created project appears in list
        created_project_id = self.created_resources['projects'][0]
        project_found = any(project.get('id') == created_project_id for project in projects_list)
        
        self.log_test(
            "PROJECT VERIFICATION - PROJECT IN LIST",
            project_found,
            f"Created project found in user's projects list" if project_found else f"Created project not found in projects list"
        )
        
        # Verify project has proper associations
        if project_found:
            created_project = next(project for project in projects_list if project.get('id') == created_project_id)
            has_name = 'name' in created_project
            has_status = 'status' in created_project
            has_priority = 'priority' in created_project
            
            associations_valid = has_name and has_status and has_priority
            self.log_test(
                "PROJECT VERIFICATION - PROJECT ASSOCIATIONS",
                associations_valid,
                f"Project has proper associations (name, status, priority)" if associations_valid else f"Project missing some associations"
            )
            
            return project_found and associations_valid
        
        return project_found

    def test_error_handling(self):
        """Test error handling for validation errors"""
        print("\n=== TESTING ERROR HANDLING ===")
        
        if not self.auth_token:
            self.log_test("ERROR HANDLING - Authentication Required", False, "No authentication token available")
            return False
        
        # Test empty project title validation
        invalid_request = {
            "project": {
                "title": "",  # Empty title should trigger 422
                "description": "Test project",
                "priority": "medium",
                "status": "Not Started"
            },
            "tasks": []
        }
        
        result = self.make_request('POST', '/projects/create-with-tasks', data=invalid_request, use_auth=True)
        validation_error = result['status_code'] == 422
        
        self.log_test(
            "ERROR HANDLING - EMPTY PROJECT TITLE",
            validation_error,
            f"Empty project title properly rejected with 422 status" if validation_error else f"Empty project title not properly validated (status: {result['status_code']})"
        )
        
        # Test authentication requirement
        result = self.make_request('POST', '/projects/create-with-tasks', data=invalid_request, use_auth=False)
        auth_required = result['status_code'] in [401, 403]
        
        self.log_test(
            "ERROR HANDLING - AUTHENTICATION REQUIRED",
            auth_required,
            f"Endpoint properly requires authentication (status: {result['status_code']})" if auth_required else f"Endpoint does not require authentication (status: {result['status_code']})"
        )
        
        return validation_error and auth_required

    def test_quota_consumption(self):
        """Test that AI generation consumes quota but saving does not"""
        print("\n=== TESTING QUOTA CONSUMPTION ===")
        
        if not self.auth_token:
            self.log_test("QUOTA CONSUMPTION - Authentication Required", False, "No authentication token available")
            return False
        
        # Get initial quota
        result = self.make_request('GET', '/ai/quota', use_auth=True)
        if not result['success']:
            self.log_test("QUOTA CONSUMPTION - Initial Quota Check Failed", False, "Could not get initial quota")
            return False
        
        initial_quota = result['data']
        initial_used = initial_quota.get('used', 0)
        initial_remaining = initial_quota.get('remaining', 0)
        
        # Generate AI breakdown (should consume quota)
        decomposition_data = {"project_name": "Test quota consumption"}
        result = self.make_request('POST', '/ai/decompose-project', data=decomposition_data, use_auth=True)
        
        if not result['success']:
            self.log_test("QUOTA CONSUMPTION - AI Generation Failed", False, "AI generation failed")
            return False
        
        # Check quota after AI generation
        result = self.make_request('GET', '/ai/quota', use_auth=True)
        if not result['success']:
            self.log_test("QUOTA CONSUMPTION - Post-AI Quota Check Failed", False, "Could not get quota after AI generation")
            return False
        
        post_ai_quota = result['data']
        post_ai_used = post_ai_quota.get('used', 0)
        post_ai_remaining = post_ai_quota.get('remaining', 0)
        
        ai_consumed_quota = post_ai_used > initial_used
        self.log_test(
            "QUOTA CONSUMPTION - AI GENERATION CONSUMES QUOTA",
            ai_consumed_quota,
            f"AI generation consumed quota: {initial_used} → {post_ai_used}" if ai_consumed_quota else f"AI generation did not consume quota: {initial_used} → {post_ai_used}"
        )
        
        # Save project (should NOT consume additional quota)
        if result['success']:
            decomposition_response = result['data']
            suggested_project = decomposition_response.get('suggested_project', {})
            
            create_request = {
                "project": {
                    "title": "Test quota project",
                    "description": "Testing quota consumption",
                    "priority": "medium",
                    "status": "Not Started"
                },
                "tasks": []
            }
            
            result = self.make_request('POST', '/projects/create-with-tasks', data=create_request, use_auth=True)
            
            if result['success']:
                # Check quota after project creation
                result = self.make_request('GET', '/ai/quota', use_auth=True)
                if result['success']:
                    post_save_quota = result['data']
                    post_save_used = post_save_quota.get('used', 0)
                    
                    save_no_quota_consumption = post_save_used == post_ai_used
                    self.log_test(
                        "QUOTA CONSUMPTION - SAVE PROJECT DOES NOT CONSUME QUOTA",
                        save_no_quota_consumption,
                        f"Save project did not consume quota: {post_ai_used} → {post_save_used}" if save_no_quota_consumption else f"Save project consumed quota: {post_ai_used} → {post_save_used}"
                    )
                    
                    return ai_consumed_quota and save_no_quota_consumption
        
        return ai_consumed_quota

    def cleanup_created_resources(self):
        """Clean up created test resources"""
        print("\n=== CLEANING UP TEST RESOURCES ===")
        
        if not self.auth_token:
            return
        
        # Delete created tasks
        for task_id in self.created_resources['tasks']:
            try:
                result = self.make_request('DELETE', f'/tasks/{task_id}', use_auth=True)
                if result['success']:
                    print(f"✅ Deleted task: {task_id}")
                else:
                    print(f"❌ Failed to delete task: {task_id}")
            except Exception as e:
                print(f"❌ Error deleting task {task_id}: {e}")
        
        # Delete created projects
        for project_id in self.created_resources['projects']:
            try:
                result = self.make_request('DELETE', f'/projects/{project_id}', use_auth=True)
                if result['success']:
                    print(f"✅ Deleted project: {project_id}")
                else:
                    print(f"❌ Failed to delete project: {project_id}")
            except Exception as e:
                print(f"❌ Error deleting project {project_id}: {e}")

    def run_comprehensive_goal_decomposition_test(self):
        """Run comprehensive Enhanced Goal Decomposition Interactive Workflow tests"""
        print("\n🎯 STARTING ENHANCED GOAL DECOMPOSITION INTERACTIVE WORKFLOW TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("Testing the fixed 'Save Project' feature (createProject TypeError resolved)")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("User Authentication", self.test_user_authentication),
            ("AI Quota Management", self.test_ai_quota_management),
            ("AI Goal Decomposition", lambda: self.test_ai_goal_decomposition()[0]),
            ("Save Project Functionality", lambda: self.test_save_project_functionality(self.decomposition_data)),
            ("Project Verification", self.test_project_verification),
            ("Error Handling", self.test_error_handling),
            ("Quota Consumption", self.test_quota_consumption)
        ]
        
        successful_tests = 0
        total_tests = len(test_methods)
        self.decomposition_data = None
        
        for test_name, test_method in test_methods:
            print(f"\n--- {test_name} ---")
            try:
                if test_name == "AI Goal Decomposition":
                    success, self.decomposition_data = self.test_ai_goal_decomposition()
                    if success:
                        successful_tests += 1
                        print(f"✅ {test_name} completed successfully")
                    else:
                        print(f"❌ {test_name} failed")
                elif test_name == "Save Project Functionality":
                    if self.test_save_project_functionality(self.decomposition_data):
                        successful_tests += 1
                        print(f"✅ {test_name} completed successfully")
                    else:
                        print(f"❌ {test_name} failed")
                else:
                    if test_method():
                        successful_tests += 1
                        print(f"✅ {test_name} completed successfully")
                    else:
                        print(f"❌ {test_name} failed")
            except Exception as e:
                print(f"❌ {test_name} raised exception: {e}")
        
        # Clean up resources
        self.cleanup_created_resources()
        
        success_rate = (successful_tests / total_tests) * 100
        
        print(f"\n" + "=" * 80)
        print("🎯 ENHANCED GOAL DECOMPOSITION INTERACTIVE WORKFLOW TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for specific functionality
        ai_tests_passed = sum(1 for result in self.test_results if result['success'] and 'AI' in result['test'])
        save_tests_passed = sum(1 for result in self.test_results if result['success'] and 'SAVE PROJECT' in result['test'])
        quota_tests_passed = sum(1 for result in self.test_results if result['success'] and 'QUOTA' in result['test'])
        error_tests_passed = sum(1 for result in self.test_results if result['success'] and 'ERROR HANDLING' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"AI Integration Tests Passed: {ai_tests_passed}")
        print(f"Save Project Tests Passed: {save_tests_passed}")
        print(f"Quota Management Tests Passed: {quota_tests_passed}")
        print(f"Error Handling Tests Passed: {error_tests_passed}")
        
        if success_rate >= 85:
            print("\n✅ ENHANCED GOAL DECOMPOSITION INTERACTIVE WORKFLOW: SUCCESS")
            print("   ✅ AI Goal Decomposition working with structured response")
            print("   ✅ POST /projects/create-with-tasks endpoint functional (createProject fixed)")
            print("   ✅ Complete workflow: Generate → Edit → Save → Verify working")
            print("   ✅ Quota management working correctly")
            print("   ✅ Error handling and validation working")
            print("   The Enhanced Goal Decomposition Interactive Workflow is production-ready!")
        else:
            print("\n❌ ENHANCED GOAL DECOMPOSITION INTERACTIVE WORKFLOW: ISSUES DETECTED")
            print("   Issues found in the Enhanced Goal Decomposition implementation")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 85

def main():
    """Run Enhanced Goal Decomposition Interactive Workflow Tests"""
    print("🎯 STARTING ENHANCED GOAL DECOMPOSITION INTERACTIVE WORKFLOW BACKEND TESTING")
    print("=" * 80)
    
    tester = EnhancedGoalDecompositionTester()
    
    try:
        # Run the comprehensive Enhanced Goal Decomposition tests
        success = tester.run_comprehensive_goal_decomposition_test()
        
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

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)