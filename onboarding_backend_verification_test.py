#!/usr/bin/env python3
"""
ONBOARDING BACKEND VERIFICATION TEST
Testing backend functionality after frontend OnboardingWizard error handling fix.

FOCUS AREAS (as specified in review request):
1. Authentication endpoints are working (/api/auth/login, /api/auth/me)
2. Core CRUD endpoints for onboarding template creation:
   - POST /api/pillars (create pillar)
   - POST /api/areas (create area with pillar_id)
   - POST /api/projects (create project with area_id) 
   - POST /api/tasks (create task with project_id)
3. POST /api/auth/complete-onboarding endpoint
4. Verify that 422 validation errors are still properly returned by the backend

The goal is to ensure that the frontend fix didn't break any backend functionality.
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://1b0a62f2-f882-476f-afb6-6747b2b238a1.preview.emergentagent.com/api"

class OnboardingBackendVerificationTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Use existing test user credentials
        self.test_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.test_user_password = "password"
        self.created_resources = {
            'pillars': [],
            'areas': [],
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

    def test_authentication_endpoints(self):
        """Test 1: Authentication endpoints (/api/auth/login, /api/auth/me)"""
        print("\n=== TESTING AUTHENTICATION ENDPOINTS ===")
        
        # Test /api/auth/login
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        self.log_test(
            "POST /api/auth/login",
            result['success'],
            f"Login successful with {self.test_user_email}" if result['success'] else f"Login failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        token_data = result['data']
        self.auth_token = token_data.get('access_token')
        
        if not self.auth_token:
            self.log_test("Authentication Token Extraction", False, "No access_token in login response")
            return False
        
        # Test /api/auth/me
        result = self.make_request('GET', '/auth/me', use_auth=True)
        self.log_test(
            "GET /api/auth/me",
            result['success'],
            f"User profile retrieved successfully, email: {result['data'].get('email', 'Unknown')}" if result['success'] else f"Profile retrieval failed: {result.get('error', 'Unknown error')}"
        )
        
        return result['success']

    def test_pillar_creation(self):
        """Test 2: POST /api/pillars (create pillar)"""
        print("\n=== TESTING PILLAR CREATION ===")
        
        if not self.auth_token:
            self.log_test("Pillar Creation - Authentication Required", False, "No authentication token available")
            return None
        
        # Test valid pillar creation
        pillar_data = {
            "name": "Health & Wellness Test",
            "description": "Test pillar for backend verification",
            "icon": "💪",
            "color": "#10B981",
            "time_allocation_percentage": 25.0
        }
        
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        self.log_test(
            "POST /api/pillars - Valid Data",
            result['success'],
            f"Pillar created successfully with ID: {result['data'].get('id', 'Unknown')}" if result['success'] else f"Pillar creation failed: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            pillar_id = result['data'].get('id')
            if pillar_id:
                self.created_resources['pillars'].append(pillar_id)
                return pillar_id
        
        return None

    def test_area_creation(self, pillar_id: str):
        """Test 3: POST /api/areas (create area with pillar_id)"""
        print("\n=== TESTING AREA CREATION ===")
        
        if not self.auth_token:
            self.log_test("Area Creation - Authentication Required", False, "No authentication token available")
            return None
        
        if not pillar_id:
            self.log_test("Area Creation - Pillar ID Required", False, "No pillar ID available for area creation")
            return None
        
        # Test valid area creation with pillar_id
        area_data = {
            "pillar_id": pillar_id,
            "name": "Fitness & Exercise Test",
            "description": "Test area for backend verification",
            "icon": "🏃",
            "color": "#F59E0B",
            "importance": 4
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        self.log_test(
            "POST /api/areas - Valid Data with pillar_id",
            result['success'],
            f"Area created successfully with ID: {result['data'].get('id', 'Unknown')}, linked to pillar: {pillar_id}" if result['success'] else f"Area creation failed: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            area_id = result['data'].get('id')
            if area_id:
                self.created_resources['areas'].append(area_id)
                return area_id
        
        return None

    def test_project_creation(self, area_id: str):
        """Test 4: POST /api/projects (create project with area_id)"""
        print("\n=== TESTING PROJECT CREATION ===")
        
        if not self.auth_token:
            self.log_test("Project Creation - Authentication Required", False, "No authentication token available")
            return None
        
        if not area_id:
            self.log_test("Project Creation - Area ID Required", False, "No area ID available for project creation")
            return None
        
        # Test valid project creation with area_id
        project_data = {
            "area_id": area_id,
            "name": "Morning Workout Routine Test",
            "description": "Test project for backend verification",
            "icon": "🏋️",
            "status": "Not Started",
            "priority": "high",
            "deadline": "2025-02-15T10:00:00Z"
        }
        
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        self.log_test(
            "POST /api/projects - Valid Data with area_id",
            result['success'],
            f"Project created successfully with ID: {result['data'].get('id', 'Unknown')}, linked to area: {area_id}" if result['success'] else f"Project creation failed: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            project_id = result['data'].get('id')
            if project_id:
                self.created_resources['projects'].append(project_id)
                return project_id
        
        return None

    def test_task_creation(self, project_id: str):
        """Test 5: POST /api/tasks (create task with project_id)"""
        print("\n=== TESTING TASK CREATION ===")
        
        if not self.auth_token:
            self.log_test("Task Creation - Authentication Required", False, "No authentication token available")
            return None
        
        if not project_id:
            self.log_test("Task Creation - Project ID Required", False, "No project ID available for task creation")
            return None
        
        # Test valid task creation with project_id
        task_data = {
            "project_id": project_id,
            "name": "30-minute cardio session test",
            "description": "Test task for backend verification",
            "status": "todo",
            "priority": "medium",
            "due_date": "2025-01-30T07:00:00Z"
        }
        
        result = self.make_request('POST', '/tasks', data=task_data, use_auth=True)
        self.log_test(
            "POST /api/tasks - Valid Data with project_id",
            result['success'],
            f"Task created successfully with ID: {result['data'].get('id', 'Unknown')}, linked to project: {project_id}" if result['success'] else f"Task creation failed: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            task_id = result['data'].get('id')
            if task_id:
                self.created_resources['tasks'].append(task_id)
                return task_id
        
        return None

    def test_complete_onboarding_endpoint(self):
        """Test 6: POST /api/auth/complete-onboarding endpoint"""
        print("\n=== TESTING COMPLETE ONBOARDING ENDPOINT ===")
        
        if not self.auth_token:
            self.log_test("Complete Onboarding - Authentication Required", False, "No authentication token available")
            return False
        
        result = self.make_request('POST', '/auth/complete-onboarding', use_auth=True)
        self.log_test(
            "POST /api/auth/complete-onboarding",
            result['success'],
            f"Onboarding completion successful: {result['data'].get('message', 'Unknown')}" if result['success'] else f"Onboarding completion failed: {result.get('error', 'Unknown error')}"
        )
        
        return result['success']

    def test_422_validation_errors(self):
        """Test 7: Verify that 422 validation errors are still properly returned by the backend"""
        print("\n=== TESTING 422 VALIDATION ERRORS ===")
        
        if not self.auth_token:
            self.log_test("422 Validation Testing - Authentication Required", False, "No authentication token available")
            return False
        
        validation_tests = []
        
        # Test 1: Missing required field in pillar creation
        invalid_pillar_data = {
            "description": "Missing name field",
            "icon": "💪",
            "color": "#10B981"
            # Missing required 'name' field
        }
        
        result = self.make_request('POST', '/pillars', data=invalid_pillar_data, use_auth=True)
        is_422 = result['status_code'] == 422
        validation_tests.append(is_422)
        self.log_test(
            "422 Validation - Missing pillar name",
            is_422,
            f"Properly returned 422 validation error for missing pillar name" if is_422 else f"Expected 422, got {result['status_code']}: {result.get('error', 'Unknown')}"
        )
        
        # Test 2: Invalid data type in pillar creation
        invalid_pillar_data2 = {
            "name": "Test Pillar",
            "description": "Invalid time allocation type",
            "icon": "💪",
            "color": "#10B981",
            "time_allocation_percentage": "not_a_number"  # Should be float
        }
        
        result = self.make_request('POST', '/pillars', data=invalid_pillar_data2, use_auth=True)
        is_422 = result['status_code'] == 422
        validation_tests.append(is_422)
        self.log_test(
            "422 Validation - Invalid pillar time_allocation_percentage type",
            is_422,
            f"Properly returned 422 validation error for invalid data type" if is_422 else f"Expected 422, got {result['status_code']}: {result.get('error', 'Unknown')}"
        )
        
        # Test 3: Invalid importance value in area creation
        invalid_area_data = {
            "pillar_id": "fake-pillar-id",
            "name": "Test Area",
            "description": "Invalid importance value",
            "icon": "🏃",
            "color": "#F59E0B",
            "importance": 15  # Should be 1-10
        }
        
        result = self.make_request('POST', '/areas', data=invalid_area_data, use_auth=True)
        is_422 = result['status_code'] == 422
        validation_tests.append(is_422)
        self.log_test(
            "422 Validation - Invalid area importance value",
            is_422,
            f"Properly returned 422 validation error for invalid importance value" if is_422 else f"Expected 422, got {result['status_code']}: {result.get('error', 'Unknown')}"
        )
        
        # Test 4: Invalid status enum in project creation
        invalid_project_data = {
            "area_id": "fake-area-id",
            "name": "Test Project",
            "description": "Invalid status enum",
            "icon": "🏋️",
            "status": "Invalid Status",  # Invalid enum value
            "priority": "high"
        }
        
        result = self.make_request('POST', '/projects', data=invalid_project_data, use_auth=True)
        is_422 = result['status_code'] == 422
        validation_tests.append(is_422)
        self.log_test(
            "422 Validation - Invalid project status enum",
            is_422,
            f"Properly returned 422 validation error for invalid status enum" if is_422 else f"Expected 422, got {result['status_code']}: {result.get('error', 'Unknown')}"
        )
        
        # Test 5: Missing required field in task creation
        invalid_task_data = {
            "project_id": "fake-project-id",
            "description": "Missing name field",
            "status": "todo",
            "priority": "medium"
            # Missing required 'name' field
        }
        
        result = self.make_request('POST', '/tasks', data=invalid_task_data, use_auth=True)
        is_422 = result['status_code'] == 422
        validation_tests.append(is_422)
        self.log_test(
            "422 Validation - Missing task name",
            is_422,
            f"Properly returned 422 validation error for missing task name" if is_422 else f"Expected 422, got {result['status_code']}: {result.get('error', 'Unknown')}"
        )
        
        # Calculate overall validation success rate
        validation_success_rate = (sum(validation_tests) / len(validation_tests)) * 100
        overall_validation_success = validation_success_rate >= 80
        
        self.log_test(
            "422 Validation Errors - Overall",
            overall_validation_success,
            f"422 validation errors working correctly: {sum(validation_tests)}/{len(validation_tests)} tests passed ({validation_success_rate:.1f}%)"
        )
        
        return overall_validation_success

    def cleanup_created_resources(self):
        """Clean up created test resources"""
        print("\n=== CLEANING UP TEST RESOURCES ===")
        
        cleanup_success = 0
        total_resources = 0
        
        # Delete tasks
        for task_id in self.created_resources['tasks']:
            total_resources += 1
            result = self.make_request('DELETE', f'/tasks/{task_id}', use_auth=True)
            if result['success']:
                cleanup_success += 1
                print(f"✅ Deleted task: {task_id}")
            else:
                print(f"❌ Failed to delete task: {task_id}")
        
        # Delete projects
        for project_id in self.created_resources['projects']:
            total_resources += 1
            result = self.make_request('DELETE', f'/projects/{project_id}', use_auth=True)
            if result['success']:
                cleanup_success += 1
                print(f"✅ Deleted project: {project_id}")
            else:
                print(f"❌ Failed to delete project: {project_id}")
        
        # Delete areas
        for area_id in self.created_resources['areas']:
            total_resources += 1
            result = self.make_request('DELETE', f'/areas/{area_id}', use_auth=True)
            if result['success']:
                cleanup_success += 1
                print(f"✅ Deleted area: {area_id}")
            else:
                print(f"❌ Failed to delete area: {area_id}")
        
        # Delete pillars
        for pillar_id in self.created_resources['pillars']:
            total_resources += 1
            result = self.make_request('DELETE', f'/pillars/{pillar_id}', use_auth=True)
            if result['success']:
                cleanup_success += 1
                print(f"✅ Deleted pillar: {pillar_id}")
            else:
                print(f"❌ Failed to delete pillar: {pillar_id}")
        
        if total_resources > 0:
            cleanup_rate = (cleanup_success / total_resources) * 100
            print(f"🧹 Cleanup completed: {cleanup_success}/{total_resources} resources deleted ({cleanup_rate:.1f}%)")

    def run_comprehensive_onboarding_backend_test(self):
        """Run comprehensive onboarding backend verification tests"""
        print("\n🔧 STARTING ONBOARDING BACKEND VERIFICATION TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("Testing backend functionality after frontend OnboardingWizard error handling fix")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Authentication Endpoints", self.test_authentication_endpoints),
            ("Complete Onboarding Endpoint", self.test_complete_onboarding_endpoint),
            ("422 Validation Errors", self.test_422_validation_errors)
        ]
        
        successful_tests = 0
        total_tests = len(test_methods)
        
        # Test authentication first
        auth_success = self.test_authentication_endpoints()
        if auth_success:
            successful_tests += 1
        
        # Test onboarding template creation workflow
        if auth_success:
            print("\n--- Testing Onboarding Template Creation Workflow ---")
            pillar_id = self.test_pillar_creation()
            if pillar_id:
                successful_tests += 1
                
                area_id = self.test_area_creation(pillar_id)
                if area_id:
                    successful_tests += 1
                    
                    project_id = self.test_project_creation(area_id)
                    if project_id:
                        successful_tests += 1
                        
                        task_id = self.test_task_creation(project_id)
                        if task_id:
                            successful_tests += 1
                        else:
                            total_tests += 1
                    else:
                        total_tests += 2
                else:
                    total_tests += 3
            else:
                total_tests += 4
        else:
            total_tests += 5
        
        # Test remaining endpoints
        for test_name, test_method in test_methods[1:]:  # Skip authentication as already tested
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
        self.cleanup_created_resources()
        
        success_rate = (successful_tests / total_tests) * 100
        
        print(f"\n" + "=" * 80)
        print("🔧 ONBOARDING BACKEND VERIFICATION TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results
        auth_tests_passed = sum(1 for result in self.test_results if result['success'] and 'auth' in result['test'].lower())
        crud_tests_passed = sum(1 for result in self.test_results if result['success'] and any(crud in result['test'].lower() for crud in ['pillar', 'area', 'project', 'task']))
        validation_tests_passed = sum(1 for result in self.test_results if result['success'] and '422' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"Authentication Tests Passed: {auth_tests_passed}")
        print(f"CRUD Operations Tests Passed: {crud_tests_passed}")
        print(f"Validation Error Tests Passed: {validation_tests_passed}")
        
        if success_rate >= 85:
            print("\n✅ ONBOARDING BACKEND VERIFICATION: SUCCESS")
            print("   ✅ Authentication endpoints working correctly")
            print("   ✅ Core CRUD endpoints for onboarding template creation functional")
            print("   ✅ Complete onboarding endpoint operational")
            print("   ✅ 422 validation errors properly returned by backend")
            print("   The backend is working correctly after frontend OnboardingWizard fix!")
        else:
            print("\n❌ ONBOARDING BACKEND VERIFICATION: ISSUES DETECTED")
            print("   Issues found in backend functionality after frontend fix")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 85

def main():
    """Run Onboarding Backend Verification Tests"""
    print("🔧 STARTING ONBOARDING BACKEND VERIFICATION TESTING")
    print("=" * 80)
    
    tester = OnboardingBackendVerificationTester()
    
    try:
        # Run the comprehensive onboarding backend verification tests
        success = tester.run_comprehensive_onboarding_backend_test()
        
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