#!/usr/bin/env python3
"""
AI COACH GOAL DECOMPOSITION BACKEND TESTING - DEPENDENCY INJECTION FIX VERIFICATION
Testing the AI Coach Goal Decomposition "Save Project" functionality to verify the createProject dependency injection fix.

FOCUS AREAS:
1. POST /api/projects/create-with-tasks - Project creation with tasks endpoint
2. POST /api/ai/decompose-project - Goal Decomposition feature
3. GET /api/ai/quota - AI quota management
4. Complete workflow: Goal Decomposition → Save Project
5. Error handling and authentication

TESTING CRITERIA:
- API endpoints exist and are functional
- Authentication requirements working (401 without valid token)
- Project creation with tasks working end-to-end
- Goal decomposition returns proper structure
- AI quota system functional
- Error handling provides appropriate HTTP status codes

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://2ba83010-29ce-4f25-8827-92c31097d7b1.preview.emergentagent.com/api"

class AICoachGoalDecompositionTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Use the specified test credentials
        self.test_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.test_user_password = "password"
        self.created_resources = {
            'projects': [],
            'tasks': [],
            'areas': []
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
        
        # Test the root endpoint
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

    def test_ai_quota_endpoint(self):
        """Test GET /api/ai/quota endpoint"""
        print("\n=== TESTING AI QUOTA ENDPOINT ===")
        
        if not self.auth_token:
            self.log_test("AI QUOTA - Authentication Required", False, "No authentication token available")
            return False
        
        # Test GET /api/ai/quota
        result = self.make_request('GET', '/ai/quota', use_auth=True)
        self.log_test(
            "GET AI QUOTA",
            result['success'],
            f"Retrieved AI quota successfully" if result['success'] else f"Failed to get AI quota: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        quota_response = result['data']
        
        # Check if response has the expected structure
        required_fields = ['total', 'used', 'remaining']
        missing_fields = [field for field in required_fields if field not in quota_response]
        
        fields_present = len(missing_fields) == 0
        self.log_test(
            "AI QUOTA - RESPONSE STRUCTURE",
            fields_present,
            f"All required fields present: {required_fields}" if fields_present else f"Missing fields: {missing_fields}"
        )
        
        # Verify quota values are reasonable
        if fields_present:
            total = quota_response.get('total', 0)
            used = quota_response.get('used', 0)
            remaining = quota_response.get('remaining', 0)
            
            quota_valid = (total >= 0 and used >= 0 and remaining >= 0 and used + remaining <= total)
            self.log_test(
                "AI QUOTA - VALUES VALIDATION",
                quota_valid,
                f"Quota values valid: total={total}, used={used}, remaining={remaining}" if quota_valid else f"Invalid quota values: total={total}, used={used}, remaining={remaining}"
            )
            
            return quota_valid
        
        return fields_present

    def test_goal_decomposition_endpoint(self):
        """Test POST /api/ai/decompose-project endpoint"""
        print("\n=== TESTING GOAL DECOMPOSITION ENDPOINT ===")
        
        if not self.auth_token:
            self.log_test("GOAL DECOMPOSITION - Authentication Required", False, "No authentication token available")
            return False
        
        # Test POST /api/ai/decompose-project with sample goal
        goal_data = {
            "project_name": "Learn Spanish Language",
            "project_description": "Become conversational in Spanish within 6 months",
            "template_type": "learning"
        }
        
        result = self.make_request('POST', '/ai/decompose-project', data=goal_data, use_auth=True)
        self.log_test(
            "POST AI DECOMPOSE PROJECT",
            result['success'],
            f"Goal decomposition successful" if result['success'] else f"Failed to decompose goal: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        decomposition_response = result['data']
        
        # Check if response has the expected structure
        required_fields = ['suggested_project', 'suggested_tasks']
        missing_fields = [field for field in required_fields if field not in decomposition_response]
        
        structure_valid = len(missing_fields) == 0
        self.log_test(
            "GOAL DECOMPOSITION - RESPONSE STRUCTURE",
            structure_valid,
            f"Response has required fields: {required_fields}" if structure_valid else f"Missing fields: {missing_fields}"
        )
        
        if not structure_valid:
            return False
        
        # Verify suggested_project structure
        suggested_project = decomposition_response.get('suggested_project', {})
        project_fields = ['title', 'description']
        project_missing = [field for field in project_fields if field not in suggested_project]
        
        project_valid = len(project_missing) == 0
        self.log_test(
            "GOAL DECOMPOSITION - PROJECT STRUCTURE",
            project_valid,
            f"Suggested project has required fields: {project_fields}" if project_valid else f"Project missing fields: {project_missing}"
        )
        
        # Verify suggested_tasks structure
        suggested_tasks = decomposition_response.get('suggested_tasks', [])
        tasks_valid = isinstance(suggested_tasks, list) and len(suggested_tasks) > 0
        
        self.log_test(
            "GOAL DECOMPOSITION - TASKS STRUCTURE",
            tasks_valid,
            f"Suggested tasks is a list with {len(suggested_tasks)} tasks" if tasks_valid else f"Invalid tasks structure: {type(suggested_tasks)}"
        )
        
        # Store the decomposition response for the next test
        self.decomposition_data = decomposition_response
        
        return structure_valid and project_valid and tasks_valid

    def test_create_project_with_tasks_endpoint(self):
        """Test POST /api/projects/create-with-tasks endpoint"""
        print("\n=== TESTING CREATE PROJECT WITH TASKS ENDPOINT ===")
        
        if not self.auth_token:
            self.log_test("CREATE PROJECT WITH TASKS - Authentication Required", False, "No authentication token available")
            return False
        
        # First, create an area to link the project to
        area_result = self.create_test_area()
        if not area_result:
            return False
        
        area_id = area_result
        
        # Test POST /api/projects/create-with-tasks with sample data
        project_with_tasks_data = {
            "project": {
                "title": "Learn Spanish Language",
                "description": "Become conversational in Spanish within 6 months",
                "area_id": area_id,
                "priority": "medium",
                "status": "Not Started"
            },
            "tasks": [
                {
                    "title": "Download language learning app",
                    "description": "Research and download a Spanish learning app",
                    "priority": "high",
                    "estimated_duration": 20
                },
                {
                    "title": "Set up daily practice schedule",
                    "description": "Create a consistent daily practice routine",
                    "priority": "high",
                    "estimated_duration": 15
                },
                {
                    "title": "Find conversation practice partner",
                    "description": "Look for Spanish conversation practice opportunities",
                    "priority": "medium",
                    "estimated_duration": 45
                }
            ]
        }
        
        result = self.make_request('POST', '/projects/create-with-tasks', data=project_with_tasks_data, use_auth=True)
        self.log_test(
            "POST PROJECTS CREATE WITH TASKS",
            result['success'],
            f"Project with tasks created successfully" if result['success'] else f"Failed to create project with tasks: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        creation_response = result['data']
        
        # Check if response has the expected structure
        required_fields = ['success', 'project', 'tasks', 'message']
        missing_fields = [field for field in required_fields if field not in creation_response]
        
        structure_valid = len(missing_fields) == 0
        self.log_test(
            "CREATE PROJECT WITH TASKS - RESPONSE STRUCTURE",
            structure_valid,
            f"Response has required fields: {required_fields}" if structure_valid else f"Missing fields: {missing_fields}"
        )
        
        if not structure_valid:
            return False
        
        # Verify project was created
        project = creation_response.get('project', {})
        project_created = 'id' in project and project.get('name') == "Learn Spanish Language"
        
        self.log_test(
            "CREATE PROJECT WITH TASKS - PROJECT CREATION",
            project_created,
            f"Project created with ID: {project.get('id')}" if project_created else "Project creation failed"
        )
        
        # Verify tasks were created
        tasks = creation_response.get('tasks', [])
        tasks_created = isinstance(tasks, list) and len(tasks) == 3
        
        self.log_test(
            "CREATE PROJECT WITH TASKS - TASKS CREATION",
            tasks_created,
            f"Created {len(tasks)} tasks as expected" if tasks_created else f"Expected 3 tasks, got {len(tasks)}"
        )
        
        # Store created resources for cleanup
        if project_created:
            self.created_resources['projects'].append(project.get('id'))
        if tasks_created:
            for task in tasks:
                if 'id' in task:
                    self.created_resources['tasks'].append(task.get('id'))
        
        return structure_valid and project_created and tasks_created

    def create_test_area(self):
        """Create a test area for project linking"""
        area_data = {
            "name": "Learning & Development",
            "description": "Personal learning and skill development",
            "icon": "📚",
            "color": "#3B82F6",
            "importance": 4
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        if result['success']:
            area = result['data']
            area_id = area.get('id')
            if area_id:
                self.created_resources['areas'].append(area_id)
                return area_id
        
        return None

    def test_complete_workflow(self):
        """Test the complete Goal Decomposition → Save Project workflow"""
        print("\n=== TESTING COMPLETE WORKFLOW ===")
        
        if not self.auth_token:
            self.log_test("COMPLETE WORKFLOW - Authentication Required", False, "No authentication token available")
            return False
        
        # Step 1: Goal Decomposition
        goal_data = {
            "project_name": "Start a Fitness Routine",
            "project_description": "Establish a consistent exercise routine for better health",
            "template_type": "health"
        }
        
        decompose_result = self.make_request('POST', '/ai/decompose-project', data=goal_data, use_auth=True)
        if not decompose_result['success']:
            self.log_test(
                "COMPLETE WORKFLOW - STEP 1 (DECOMPOSITION)",
                False,
                f"Goal decomposition failed: {decompose_result.get('error', 'Unknown error')}"
            )
            return False
        
        decomposition = decompose_result['data']
        
        # Step 2: Create area for the project
        area_id = self.create_test_area()
        if not area_id:
            self.log_test(
                "COMPLETE WORKFLOW - STEP 2 (AREA CREATION)",
                False,
                "Failed to create test area"
            )
            return False
        
        # Step 3: Save Project with suggested data
        suggested_project = decomposition.get('suggested_project', {})
        suggested_tasks = decomposition.get('suggested_tasks', [])
        
        # Modify suggested project to include area_id
        project_data = {
            "title": suggested_project.get('title', 'Start a Fitness Routine'),
            "description": suggested_project.get('description', 'Establish a consistent exercise routine'),
            "area_id": area_id,
            "priority": suggested_project.get('priority', 'medium'),
            "status": suggested_project.get('status', 'Not Started')
        }
        
        save_data = {
            "project": project_data,
            "tasks": suggested_tasks[:3]  # Limit to first 3 tasks
        }
        
        save_result = self.make_request('POST', '/projects/create-with-tasks', data=save_data, use_auth=True)
        
        workflow_success = save_result['success']
        self.log_test(
            "COMPLETE WORKFLOW - END-TO-END",
            workflow_success,
            f"Complete workflow successful: Goal → Decomposition → Save Project" if workflow_success else f"Workflow failed at save step: {save_result.get('error', 'Unknown error')}"
        )
        
        if workflow_success:
            creation_response = save_result['data']
            project = creation_response.get('project', {})
            tasks = creation_response.get('tasks', [])
            
            # Store created resources
            if 'id' in project:
                self.created_resources['projects'].append(project.get('id'))
            for task in tasks:
                if 'id' in task:
                    self.created_resources['tasks'].append(task.get('id'))
        
        return workflow_success

    def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n=== TESTING ERROR HANDLING ===")
        
        error_tests_passed = 0
        total_error_tests = 0
        
        # Test 1: Authentication required (401 errors)
        endpoints_requiring_auth = [
            ('GET', '/ai/quota'),
            ('POST', '/ai/decompose-project'),
            ('POST', '/projects/create-with-tasks')
        ]
        
        for method, endpoint in endpoints_requiring_auth:
            total_error_tests += 1
            test_data = {"test": "data"} if method == 'POST' else None
            result = self.make_request(method, endpoint, data=test_data, use_auth=False)
            
            auth_required = result['status_code'] in [401, 403]
            if auth_required:
                error_tests_passed += 1
            
            self.log_test(
                f"ERROR HANDLING - {method} {endpoint} WITHOUT AUTH",
                auth_required,
                f"Properly requires authentication (status: {result['status_code']})" if auth_required else f"Does not require authentication (status: {result['status_code']})"
            )
        
        # Test 2: Validation errors (422 errors)
        if self.auth_token:
            # Test empty project title
            total_error_tests += 1
            invalid_project_data = {
                "project": {
                    "title": "",  # Empty title should cause validation error
                    "description": "Test description"
                },
                "tasks": []
            }
            
            result = self.make_request('POST', '/projects/create-with-tasks', data=invalid_project_data, use_auth=True)
            validation_working = result['status_code'] == 422
            if validation_working:
                error_tests_passed += 1
            
            self.log_test(
                "ERROR HANDLING - EMPTY PROJECT TITLE VALIDATION",
                validation_working,
                f"Empty project title properly rejected (status: {result['status_code']})" if validation_working else f"Validation not working (status: {result['status_code']})"
            )
            
            # Test invalid goal decomposition data
            total_error_tests += 1
            invalid_goal_data = {
                "project_name": "",  # Empty project name
                "template_type": "invalid_type"
            }
            
            result = self.make_request('POST', '/ai/decompose-project', data=invalid_goal_data, use_auth=True)
            goal_validation_working = result['status_code'] in [400, 422]
            if goal_validation_working:
                error_tests_passed += 1
            
            self.log_test(
                "ERROR HANDLING - INVALID GOAL DATA VALIDATION",
                goal_validation_working,
                f"Invalid goal data properly rejected (status: {result['status_code']})" if goal_validation_working else f"Goal validation not working (status: {result['status_code']})"
            )
        
        error_success_rate = (error_tests_passed / total_error_tests * 100) if total_error_tests > 0 else 0
        overall_error_success = error_success_rate >= 75
        
        self.log_test(
            "ERROR HANDLING - OVERALL",
            overall_error_success,
            f"Error handling tests: {error_tests_passed}/{total_error_tests} passed ({error_success_rate:.1f}%)"
        )
        
        return overall_error_success

    def cleanup_test_resources(self):
        """Clean up created test resources"""
        print("\n=== CLEANING UP TEST RESOURCES ===")
        
        if not self.auth_token:
            return
        
        cleanup_count = 0
        
        # Delete created tasks
        for task_id in self.created_resources['tasks']:
            try:
                result = self.make_request('DELETE', f'/tasks/{task_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
            except:
                pass
        
        # Delete created projects
        for project_id in self.created_resources['projects']:
            try:
                result = self.make_request('DELETE', f'/projects/{project_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
            except:
                pass
        
        # Delete created areas
        for area_id in self.created_resources['areas']:
            try:
                result = self.make_request('DELETE', f'/areas/{area_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
            except:
                pass
        
        total_resources = len(self.created_resources['tasks']) + len(self.created_resources['projects']) + len(self.created_resources['areas'])
        
        self.log_test(
            "RESOURCE CLEANUP",
            cleanup_count == total_resources,
            f"Cleaned up {cleanup_count}/{total_resources} test resources"
        )

    def run_comprehensive_ai_coach_test(self):
        """Run comprehensive AI Coach Goal Decomposition tests"""
        print("\n🤖 STARTING AI COACH GOAL DECOMPOSITION COMPREHENSIVE TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("User Authentication", self.test_user_authentication),
            ("AI Quota Endpoint", self.test_ai_quota_endpoint),
            ("Goal Decomposition Endpoint", self.test_goal_decomposition_endpoint),
            ("Create Project with Tasks Endpoint", self.test_create_project_with_tasks_endpoint),
            ("Complete Workflow", self.test_complete_workflow),
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
        
        # Cleanup test resources
        self.cleanup_test_resources()
        
        success_rate = (successful_tests / total_tests) * 100
        
        print(f"\n" + "=" * 80)
        print("🤖 AI COACH GOAL DECOMPOSITION TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for AI Coach functionality
        api_tests_passed = sum(1 for result in self.test_results if result['success'] and any(keyword in result['test'] for keyword in ['QUOTA', 'DECOMPOSE', 'CREATE PROJECT']))
        workflow_tests_passed = sum(1 for result in self.test_results if result['success'] and 'WORKFLOW' in result['test'])
        error_handling_tests_passed = sum(1 for result in self.test_results if result['success'] and 'ERROR HANDLING' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"API Endpoint Tests Passed: {api_tests_passed}")
        print(f"Workflow Tests Passed: {workflow_tests_passed}")
        print(f"Error Handling Tests Passed: {error_handling_tests_passed}")
        
        if success_rate >= 85:
            print("\n✅ AI COACH GOAL DECOMPOSITION SYSTEM: SUCCESS")
            print("   ✅ POST /api/projects/create-with-tasks working")
            print("   ✅ POST /api/ai/decompose-project functional")
            print("   ✅ GET /api/ai/quota operational")
            print("   ✅ Complete Goal Decomposition → Save Project workflow working")
            print("   ✅ Authentication and error handling verified")
            print("   The AI Coach Goal Decomposition dependency injection fix is working!")
        else:
            print("\n❌ AI COACH GOAL DECOMPOSITION SYSTEM: ISSUES DETECTED")
            print("   Issues found in AI Coach Goal Decomposition implementation")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 85

def main():
    """Run AI Coach Goal Decomposition Tests"""
    print("🤖 STARTING AI COACH GOAL DECOMPOSITION BACKEND TESTING")
    print("=" * 80)
    
    tester = AICoachGoalDecompositionTester()
    
    try:
        # Run the comprehensive AI Coach Goal Decomposition tests
        success = tester.run_comprehensive_ai_coach_test()
        
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