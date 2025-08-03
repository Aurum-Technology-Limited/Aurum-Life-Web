#!/usr/bin/env python3
"""
ONBOARDING TEMPLATE APPLICATION 422 ERROR TESTING

Testing the onboarding template application endpoint that is causing 422 errors according to the user's report.

FOCUS AREAS:
1. Test the /api/auth/complete-onboarding endpoint 
2. Test the template application process by creating a new test user and attempting to apply an onboarding template
3. Specifically look for any 422 errors during the template creation process (creating pillars, areas, projects, tasks)
4. Check if there are any validation or foreign key constraint issues that could cause 422 errors
5. Test with a user who has has_completed_onboarding: false

The goal is to reproduce the 422 error that the user reported so the main agent can then fix the frontend error handling.
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time
import uuid

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://2add7c3c-bc98-404b-af7c-7c73ee7f9c41.preview.emergentagent.com/api"

class OnboardingTemplateErrorTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Create a new test user for onboarding testing
        self.test_user_email = f"onboarding.test.{int(time.time())}@aurumlife.com"
        self.test_user_password = "testpassword123"
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

    def test_create_new_user(self):
        """Test creating a new user for onboarding testing"""
        print("\n=== TESTING NEW USER CREATION ===")
        
        # Create a new user account
        register_data = {
            "email": self.test_user_email,
            "password": self.test_user_password,
            "username": f"onboarding_test_{int(time.time())}"
        }
        
        result = self.make_request('POST', '/auth/register', data=register_data)
        self.log_test(
            "NEW USER REGISTRATION",
            result['success'],
            f"User registration successful for {self.test_user_email}" if result['success'] else f"User registration failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            # If registration fails, try to login with existing credentials
            print("Registration failed, attempting to login with existing credentials...")
            return self.test_user_authentication()
        
        return result['success']

    def test_user_authentication(self):
        """Test user authentication with new user credentials"""
        print("\n=== TESTING USER AUTHENTICATION ===")
        
        # Login user with new credentials
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
        
        # Verify token works and check onboarding status
        result = self.make_request('GET', '/auth/me', use_auth=True)
        self.log_test(
            "AUTHENTICATION TOKEN VALIDATION",
            result['success'],
            f"Token validated successfully, user: {result['data'].get('email', 'Unknown')}" if result['success'] else f"Token validation failed: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            user_data = result['data']
            has_completed_onboarding = user_data.get('has_completed_onboarding', True)
            self.log_test(
                "ONBOARDING STATUS CHECK",
                not has_completed_onboarding,
                f"User has_completed_onboarding: {has_completed_onboarding} (should be False for new user)" if not has_completed_onboarding else f"WARNING: User already completed onboarding: {has_completed_onboarding}"
            )
        
        return result['success']

    def test_template_application_process(self):
        """Test the complete template application process that could cause 422 errors"""
        print("\n=== TESTING TEMPLATE APPLICATION PROCESS ===")
        
        if not self.auth_token:
            self.log_test("TEMPLATE APPLICATION - Authentication Required", False, "No authentication token available")
            return False
        
        # Step 1: Create a pillar (first step in template application)
        pillar_data = {
            "name": "Health & Wellness",
            "description": "Physical and mental health pillar from onboarding template",
            "icon": "💪",
            "color": "#10B981",
            "time_allocation_percentage": 25.0
        }
        
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        if result['status_code'] == 422:
            self.log_test(
                "PILLAR CREATION - 422 ERROR DETECTED",
                False,
                f"422 Unprocessable Entity error during pillar creation: {result.get('error', 'Unknown error')}",
                result['data']
            )
            return False
        elif not result['success']:
            self.log_test(
                "PILLAR CREATION",
                False,
                f"Pillar creation failed with status {result['status_code']}: {result.get('error', 'Unknown error')}",
                result['data']
            )
            return False
        else:
            pillar = result['data']
            self.created_resources['pillars'].append(pillar['id'])
            self.log_test(
                "PILLAR CREATION",
                True,
                f"Pillar created successfully: {pillar['name']}"
            )
        
        # Step 2: Create an area linked to the pillar
        area_data = {
            "pillar_id": pillar['id'],
            "name": "Fitness & Exercise",
            "description": "Physical fitness and exercise routines from template",
            "icon": "🏃",
            "color": "#F59E0B",
            "importance": 4
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        if result['status_code'] == 422:
            self.log_test(
                "AREA CREATION - 422 ERROR DETECTED",
                False,
                f"422 Unprocessable Entity error during area creation: {result.get('error', 'Unknown error')}",
                result['data']
            )
            return False
        elif not result['success']:
            self.log_test(
                "AREA CREATION",
                False,
                f"Area creation failed with status {result['status_code']}: {result.get('error', 'Unknown error')}",
                result['data']
            )
            return False
        else:
            area = result['data']
            self.created_resources['areas'].append(area['id'])
            self.log_test(
                "AREA CREATION",
                True,
                f"Area created successfully: {area['name']}"
            )
        
        # Step 3: Create a project linked to the area
        project_data = {
            "area_id": area['id'],
            "name": "Morning Workout Routine",
            "description": "Daily morning exercise routine from template",
            "icon": "🏋️",
            "status": "Not Started",
            "priority": "high",
            "deadline": "2025-02-15T10:00:00Z"
        }
        
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        if result['status_code'] == 422:
            self.log_test(
                "PROJECT CREATION - 422 ERROR DETECTED",
                False,
                f"422 Unprocessable Entity error during project creation: {result.get('error', 'Unknown error')}",
                result['data']
            )
            return False
        elif not result['success']:
            self.log_test(
                "PROJECT CREATION",
                False,
                f"Project creation failed with status {result['status_code']}: {result.get('error', 'Unknown error')}",
                result['data']
            )
            return False
        else:
            project = result['data']
            self.created_resources['projects'].append(project['id'])
            self.log_test(
                "PROJECT CREATION",
                True,
                f"Project created successfully: {project['name']}"
            )
        
        # Step 4: Create tasks linked to the project
        task_data_list = [
            {
                "project_id": project['id'],
                "name": "30-minute cardio session",
                "description": "High-intensity cardio workout",
                "status": "todo",
                "priority": "medium",
                "due_date": "2025-01-30T07:00:00Z"
            },
            {
                "project_id": project['id'],
                "name": "Strength training session",
                "description": "Weight lifting and resistance exercises",
                "status": "todo",
                "priority": "high",
                "due_date": "2025-01-31T07:00:00Z"
            }
        ]
        
        for i, task_data in enumerate(task_data_list):
            result = self.make_request('POST', '/tasks', data=task_data, use_auth=True)
            if result['status_code'] == 422:
                self.log_test(
                    f"TASK {i+1} CREATION - 422 ERROR DETECTED",
                    False,
                    f"422 Unprocessable Entity error during task creation: {result.get('error', 'Unknown error')}",
                    result['data']
                )
                return False
            elif not result['success']:
                self.log_test(
                    f"TASK {i+1} CREATION",
                    False,
                    f"Task creation failed with status {result['status_code']}: {result.get('error', 'Unknown error')}",
                    result['data']
                )
                return False
            else:
                task = result['data']
                self.created_resources['tasks'].append(task['id'])
                self.log_test(
                    f"TASK {i+1} CREATION",
                    True,
                    f"Task created successfully: {task['name']}"
                )
        
        return True

    def test_complete_onboarding_endpoint(self):
        """Test the /api/auth/complete-onboarding endpoint"""
        print("\n=== TESTING COMPLETE ONBOARDING ENDPOINT ===")
        
        if not self.auth_token:
            self.log_test("COMPLETE ONBOARDING - Authentication Required", False, "No authentication token available")
            return False
        
        # Test the complete onboarding endpoint
        result = self.make_request('POST', '/auth/complete-onboarding', use_auth=True)
        if result['status_code'] == 422:
            self.log_test(
                "COMPLETE ONBOARDING - 422 ERROR DETECTED",
                False,
                f"422 Unprocessable Entity error during onboarding completion: {result.get('error', 'Unknown error')}",
                result['data']
            )
            return False
        elif not result['success']:
            self.log_test(
                "COMPLETE ONBOARDING",
                False,
                f"Onboarding completion failed with status {result['status_code']}: {result.get('error', 'Unknown error')}",
                result['data']
            )
            return False
        else:
            self.log_test(
                "COMPLETE ONBOARDING",
                True,
                f"Onboarding completed successfully"
            )
        
        # Verify onboarding status was updated
        result = self.make_request('GET', '/auth/me', use_auth=True)
        if result['success']:
            user_data = result['data']
            has_completed_onboarding = user_data.get('has_completed_onboarding', False)
            self.log_test(
                "ONBOARDING STATUS UPDATE VERIFICATION",
                has_completed_onboarding,
                f"User has_completed_onboarding: {has_completed_onboarding} (should be True after completion)" if has_completed_onboarding else f"ERROR: Onboarding status not updated: {has_completed_onboarding}"
            )
            return has_completed_onboarding
        else:
            self.log_test(
                "ONBOARDING STATUS UPDATE VERIFICATION",
                False,
                f"Failed to verify onboarding status: {result.get('error', 'Unknown error')}"
            )
            return False

    def test_validation_edge_cases(self):
        """Test validation edge cases that could cause 422 errors"""
        print("\n=== TESTING VALIDATION EDGE CASES ===")
        
        if not self.auth_token:
            self.log_test("VALIDATION EDGE CASES - Authentication Required", False, "No authentication token available")
            return False
        
        edge_cases_passed = 0
        total_edge_cases = 0
        
        # Test 1: Invalid pillar_id format in area creation
        total_edge_cases += 1
        invalid_area_data = {
            "pillar_id": "invalid-uuid-format",
            "name": "Test Area",
            "description": "Test area with invalid pillar_id",
            "icon": "🧪",
            "color": "#FF0000",
            "importance": 3
        }
        
        result = self.make_request('POST', '/areas', data=invalid_area_data, use_auth=True)
        if result['status_code'] == 422 or result['status_code'] == 400:
            self.log_test(
                "VALIDATION - INVALID PILLAR_ID FORMAT",
                True,
                f"Properly rejected invalid pillar_id format with status {result['status_code']}"
            )
            edge_cases_passed += 1
        else:
            self.log_test(
                "VALIDATION - INVALID PILLAR_ID FORMAT",
                False,
                f"Did not properly reject invalid pillar_id format, got status {result['status_code']}"
            )
        
        # Test 2: Non-existent pillar_id in area creation
        total_edge_cases += 1
        nonexistent_area_data = {
            "pillar_id": str(uuid.uuid4()),  # Valid UUID format but non-existent
            "name": "Test Area",
            "description": "Test area with non-existent pillar_id",
            "icon": "🧪",
            "color": "#FF0000",
            "importance": 3
        }
        
        result = self.make_request('POST', '/areas', data=nonexistent_area_data, use_auth=True)
        if result['status_code'] == 422 or result['status_code'] == 400:
            self.log_test(
                "VALIDATION - NON-EXISTENT PILLAR_ID",
                True,
                f"Properly rejected non-existent pillar_id with status {result['status_code']}"
            )
            edge_cases_passed += 1
        else:
            self.log_test(
                "VALIDATION - NON-EXISTENT PILLAR_ID",
                False,
                f"Did not properly reject non-existent pillar_id, got status {result['status_code']}"
            )
        
        # Test 3: Invalid area_id format in project creation
        total_edge_cases += 1
        invalid_project_data = {
            "area_id": "invalid-uuid-format",
            "name": "Test Project",
            "description": "Test project with invalid area_id",
            "icon": "🧪",
            "status": "Not Started",
            "priority": "medium"
        }
        
        result = self.make_request('POST', '/projects', data=invalid_project_data, use_auth=True)
        if result['status_code'] == 422 or result['status_code'] == 400:
            self.log_test(
                "VALIDATION - INVALID AREA_ID FORMAT",
                True,
                f"Properly rejected invalid area_id format with status {result['status_code']}"
            )
            edge_cases_passed += 1
        else:
            self.log_test(
                "VALIDATION - INVALID AREA_ID FORMAT",
                False,
                f"Did not properly reject invalid area_id format, got status {result['status_code']}"
            )
        
        # Test 4: Invalid project_id format in task creation
        total_edge_cases += 1
        invalid_task_data = {
            "project_id": "invalid-uuid-format",
            "name": "Test Task",
            "description": "Test task with invalid project_id",
            "status": "todo",
            "priority": "medium"
        }
        
        result = self.make_request('POST', '/tasks', data=invalid_task_data, use_auth=True)
        if result['status_code'] == 422 or result['status_code'] == 400:
            self.log_test(
                "VALIDATION - INVALID PROJECT_ID FORMAT",
                True,
                f"Properly rejected invalid project_id format with status {result['status_code']}"
            )
            edge_cases_passed += 1
        else:
            self.log_test(
                "VALIDATION - INVALID PROJECT_ID FORMAT",
                False,
                f"Did not properly reject invalid project_id format, got status {result['status_code']}"
            )
        
        validation_success_rate = (edge_cases_passed / total_edge_cases) * 100
        self.log_test(
            "VALIDATION EDGE CASES SUMMARY",
            edge_cases_passed >= total_edge_cases * 0.75,  # 75% success rate
            f"Validation edge cases: {edge_cases_passed}/{total_edge_cases} passed ({validation_success_rate:.1f}%)"
        )
        
        return edge_cases_passed >= total_edge_cases * 0.75

    def cleanup_created_resources(self):
        """Clean up created resources"""
        print("\n=== CLEANING UP CREATED RESOURCES ===")
        
        if not self.auth_token:
            return
        
        # Delete in reverse order (tasks -> projects -> areas -> pillars)
        for task_id in self.created_resources['tasks']:
            try:
                self.make_request('DELETE', f'/tasks/{task_id}', use_auth=True)
            except:
                pass
        
        for project_id in self.created_resources['projects']:
            try:
                self.make_request('DELETE', f'/projects/{project_id}', use_auth=True)
            except:
                pass
        
        for area_id in self.created_resources['areas']:
            try:
                self.make_request('DELETE', f'/areas/{area_id}', use_auth=True)
            except:
                pass
        
        for pillar_id in self.created_resources['pillars']:
            try:
                self.make_request('DELETE', f'/pillars/{pillar_id}', use_auth=True)
            except:
                pass
        
        print("✅ Resource cleanup completed")

    def run_comprehensive_onboarding_template_test(self):
        """Run comprehensive onboarding template application tests"""
        print("\n🎯 STARTING ONBOARDING TEMPLATE APPLICATION 422 ERROR TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Create New User", self.test_create_new_user),
            ("User Authentication", self.test_user_authentication),
            ("Template Application Process", self.test_template_application_process),
            ("Complete Onboarding Endpoint", self.test_complete_onboarding_endpoint),
            ("Validation Edge Cases", self.test_validation_edge_cases)
        ]
        
        successful_tests = 0
        total_tests = len(test_methods)
        found_422_errors = []
        
        try:
            for test_name, test_method in test_methods:
                print(f"\n--- {test_name} ---")
                try:
                    if test_method():
                        successful_tests += 1
                        print(f"✅ {test_name} completed successfully")
                    else:
                        print(f"❌ {test_name} failed")
                        # Check if this test found 422 errors
                        for result in self.test_results:
                            if "422 ERROR DETECTED" in result['test'] and not result['success']:
                                found_422_errors.append(result)
                except Exception as e:
                    print(f"❌ {test_name} raised exception: {e}")
        finally:
            # Always cleanup resources
            self.cleanup_created_resources()
        
        success_rate = (successful_tests / total_tests) * 100
        
        print(f"\n" + "=" * 80)
        print("🎯 ONBOARDING TEMPLATE APPLICATION TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Report 422 errors found
        if found_422_errors:
            print(f"\n🚨 422 ERRORS DETECTED ({len(found_422_errors)}):")
            for error in found_422_errors:
                print(f"   ❌ {error['test']}: {error['message']}")
                if 'data' in error:
                    print(f"      Data: {json.dumps(error['data'], indent=6, default=str)}")
        else:
            print(f"\n✅ NO 422 ERRORS DETECTED")
            print("   The onboarding template application process completed without 422 errors")
        
        # Analyze results for onboarding functionality
        template_tests_passed = sum(1 for result in self.test_results if result['success'] and 'CREATION' in result['test'])
        onboarding_tests_passed = sum(1 for result in self.test_results if result['success'] and 'ONBOARDING' in result['test'])
        validation_tests_passed = sum(1 for result in self.test_results if result['success'] and 'VALIDATION' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"Template Creation Tests Passed: {template_tests_passed}")
        print(f"Onboarding Tests Passed: {onboarding_tests_passed}")
        print(f"Validation Tests Passed: {validation_tests_passed}")
        
        if len(found_422_errors) == 0 and success_rate >= 80:
            print("\n✅ ONBOARDING TEMPLATE APPLICATION: SUCCESS")
            print("   ✅ No 422 errors detected during template application")
            print("   ✅ Complete onboarding endpoint working")
            print("   ✅ Template hierarchy creation functional")
            print("   ✅ Validation and error handling working")
            print("   The onboarding template application process is working correctly!")
        else:
            print("\n❌ ONBOARDING TEMPLATE APPLICATION: ISSUES DETECTED")
            if found_422_errors:
                print("   🚨 422 Unprocessable Entity errors found during template application")
                print("   This matches the user's reported issue!")
            else:
                print("   Issues found in onboarding template application implementation")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return len(found_422_errors) == 0 and success_rate >= 80

def main():
    """Run Onboarding Template Application Tests"""
    print("🎯 STARTING ONBOARDING TEMPLATE APPLICATION 422 ERROR TESTING")
    print("=" * 80)
    
    tester = OnboardingTemplateErrorTester()
    
    try:
        # Run the comprehensive onboarding template application tests
        success = tester.run_comprehensive_onboarding_template_test()
        
        # Calculate overall results
        total_tests = len(tester.test_results)
        passed_tests = sum(1 for result in tester.test_results if result['success'])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Count 422 errors found
        found_422_errors = [result for result in tester.test_results if "422 ERROR DETECTED" in result['test'] and not result['success']]
        
        print("\n" + "=" * 80)
        print("📊 FINAL RESULTS")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"422 Errors Found: {len(found_422_errors)}")
        
        if found_422_errors:
            print("\n🚨 CRITICAL FINDING: 422 ERRORS DETECTED")
            print("This matches the user's reported issue with onboarding template application!")
            print("The frontend is likely trying to render the raw error object, causing React errors.")
        else:
            print("\n✅ NO 422 ERRORS FOUND")
            print("The onboarding template application process is working correctly.")
        
        print("=" * 80)
        
        return success
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)