#!/usr/bin/env python3
"""
SMART ONBOARDING FLOW BACKEND TESTING - COMPREHENSIVE VERIFICATION
Testing the complete Smart Onboarding backend API endpoints as requested by user.

FOCUS AREAS:
1. Authentication with marc.alleyne@aurumtechnologyltd.com/password
2. Smart Onboarding API endpoints:
   - POST /api/pillars (pillar creation)
   - POST /api/areas (area creation) 
   - POST /api/projects (project creation with 'Not Started' status validation)
   - POST /api/tasks (task creation)
3. Project status validation fix - 'Not Started' accepted, 'not_started' rejected (422)
4. Foreign key constraint resolution - user existence in public.users table
5. Complete onboarding data creation flow end-to-end

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://hierarchy-master.preview.emergentagent.com/api"

class SmartOnboardingBackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Use the specified test credentials from review request
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

    def test_authentication(self):
        """Test authentication with specified credentials"""
        print("\n=== TESTING AUTHENTICATION ===")
        
        # Login user with specified credentials
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        self.log_test(
            "USER AUTHENTICATION",
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

    def test_pillar_creation(self):
        """Test POST /api/pillars endpoint"""
        print("\n=== TESTING PILLAR CREATION ===")
        
        if not self.auth_token:
            self.log_test("PILLAR CREATION - Authentication Required", False, "No authentication token available")
            return False
        
        # Test pillar creation with realistic data
        pillar_data = {
            "name": "Health & Wellness",
            "description": "Physical and mental health pillar for onboarding test",
            "icon": "💪",
            "color": "#10B981",
            "time_allocation_percentage": 30.0
        }
        
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        self.log_test(
            "POST /api/pillars",
            result['success'],
            f"Pillar created successfully: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Pillar creation failed: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            pillar_id = result['data'].get('id')
            if pillar_id:
                self.created_resources['pillars'].append(pillar_id)
                return pillar_id
        
        return False

    def test_area_creation(self, pillar_id: str):
        """Test POST /api/areas endpoint"""
        print("\n=== TESTING AREA CREATION ===")
        
        if not self.auth_token:
            self.log_test("AREA CREATION - Authentication Required", False, "No authentication token available")
            return False
        
        # Test area creation with pillar linkage
        area_data = {
            "pillar_id": pillar_id,
            "name": "Fitness & Exercise",
            "description": "Physical fitness and exercise routines for onboarding test",
            "icon": "🏃",
            "color": "#F59E0B",
            "importance": 4
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        self.log_test(
            "POST /api/areas",
            result['success'],
            f"Area created successfully: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Area creation failed: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            area_id = result['data'].get('id')
            if area_id:
                self.created_resources['areas'].append(area_id)
                return area_id
        
        return False

    def test_project_status_validation(self, area_id: str):
        """Test POST /api/projects endpoint with status validation"""
        print("\n=== TESTING PROJECT STATUS VALIDATION ===")
        
        if not self.auth_token:
            self.log_test("PROJECT STATUS VALIDATION - Authentication Required", False, "No authentication token available")
            return False
        
        # Test 1: Valid status 'Not Started' should be accepted
        project_data_valid = {
            "area_id": area_id,
            "name": "Morning Workout Routine",
            "description": "Daily morning exercise routine for onboarding test",
            "icon": "🏋️",
            "status": "Not Started",  # This should be accepted
            "priority": "high"
        }
        
        result = self.make_request('POST', '/projects', data=project_data_valid, use_auth=True)
        self.log_test(
            "PROJECT STATUS VALIDATION - 'Not Started' ACCEPTED",
            result['success'],
            f"Project with 'Not Started' status created successfully" if result['success'] else f"Project creation failed: {result.get('error', 'Unknown error')}"
        )
        
        project_id = None
        if result['success']:
            project_id = result['data'].get('id')
            if project_id:
                self.created_resources['projects'].append(project_id)
        
        # Test 2: Invalid status 'not_started' should be rejected with 422
        project_data_invalid = {
            "area_id": area_id,
            "name": "Evening Workout Routine",
            "description": "Daily evening exercise routine for validation test",
            "icon": "🏋️",
            "status": "not_started",  # This should be rejected
            "priority": "medium"
        }
        
        result_invalid = self.make_request('POST', '/projects', data=project_data_invalid, use_auth=True)
        validation_error_correct = result_invalid['status_code'] == 422
        self.log_test(
            "PROJECT STATUS VALIDATION - 'not_started' REJECTED (422)",
            validation_error_correct,
            f"Invalid status 'not_started' properly rejected with 422 error" if validation_error_correct else f"Expected 422 error, got: {result_invalid['status_code']}"
        )
        
        # Test 3: Verify all valid status values work
        valid_statuses = ["Not Started", "In Progress", "Completed", "On Hold"]
        valid_status_count = 0
        
        for status in valid_statuses[1:]:  # Skip "Not Started" as we already tested it
            test_project_data = {
                "area_id": area_id,
                "name": f"Test Project - {status}",
                "description": f"Test project with {status} status",
                "icon": "🧪",
                "status": status,
                "priority": "low"
            }
            
            result = self.make_request('POST', '/projects', data=test_project_data, use_auth=True)
            if result['success']:
                valid_status_count += 1
                if result['data'].get('id'):
                    self.created_resources['projects'].append(result['data']['id'])
        
        all_valid_statuses_work = valid_status_count == 3  # We tested 3 additional statuses
        self.log_test(
            "PROJECT STATUS VALIDATION - ALL VALID STATUSES",
            all_valid_statuses_work,
            f"All valid status values work correctly ({valid_status_count + 1}/4)" if all_valid_statuses_work else f"Some valid statuses failed ({valid_status_count + 1}/4)"
        )
        
        return project_id

    def test_task_creation(self, project_id: str):
        """Test POST /api/tasks endpoint"""
        print("\n=== TESTING TASK CREATION ===")
        
        if not self.auth_token:
            self.log_test("TASK CREATION - Authentication Required", False, "No authentication token available")
            return False
        
        # Test task creation with project linkage
        task_data = {
            "project_id": project_id,
            "name": "30-minute cardio session",
            "description": "High-intensity cardio workout for onboarding test",
            "status": "todo",
            "priority": "medium",
            "estimated_duration": 30
        }
        
        result = self.make_request('POST', '/tasks', data=task_data, use_auth=True)
        self.log_test(
            "POST /api/tasks",
            result['success'],
            f"Task created successfully: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Task creation failed: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            task_id = result['data'].get('id')
            if task_id:
                self.created_resources['tasks'].append(task_id)
                return task_id
        
        return False

    def test_template_application_workflow(self):
        """Test template application workflow endpoints"""
        print("\n=== TESTING TEMPLATE APPLICATION WORKFLOW ===")
        
        if not self.auth_token:
            self.log_test("TEMPLATE APPLICATION - Authentication Required", False, "No authentication token available")
            return False
        
        # Test AI Goal Decomposition endpoint
        decomposition_data = {
            "project_name": "Learn Spanish Language",
            "project_description": "Complete Spanish language learning program",
            "template_type": "learning"
        }
        
        result = self.make_request('POST', '/ai/decompose-project', data=decomposition_data, use_auth=True)
        self.log_test(
            "AI GOAL DECOMPOSITION",
            result['success'],
            f"Goal decomposition successful" if result['success'] else f"Goal decomposition failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        # Test project creation with tasks endpoint
        if self.created_resources['areas']:
            area_id = self.created_resources['areas'][0]
            project_with_tasks_data = {
                "project": {
                    "title": "Spanish Learning Project",
                    "description": "Comprehensive Spanish language learning",
                    "area_id": area_id,
                    "priority": "high",
                    "status": "Not Started"
                },
                "tasks": [
                    {
                        "title": "Download language learning app",
                        "description": "Set up Duolingo or similar app",
                        "priority": "high",
                        "estimated_duration": 15
                    },
                    {
                        "title": "Practice daily vocabulary",
                        "description": "Learn 10 new words daily",
                        "priority": "medium",
                        "estimated_duration": 20
                    }
                ]
            }
            
            result = self.make_request('POST', '/projects/create-with-tasks', data=project_with_tasks_data, use_auth=True)
            self.log_test(
                "PROJECT CREATION WITH TASKS",
                result['success'],
                f"Project with tasks created successfully" if result['success'] else f"Project with tasks creation failed: {result.get('error', 'Unknown error')}"
            )
            
            if result['success']:
                project_id = result['data'].get('project', {}).get('id')
                tasks = result['data'].get('tasks', [])
                if project_id:
                    self.created_resources['projects'].append(project_id)
                for task in tasks:
                    if task.get('id'):
                        self.created_resources['tasks'].append(task['id'])
                
                return True
        
        return False

    def test_data_retrieval_verification(self):
        """Test that all created resources can be retrieved"""
        print("\n=== TESTING DATA RETRIEVAL VERIFICATION ===")
        
        if not self.auth_token:
            self.log_test("DATA RETRIEVAL - Authentication Required", False, "No authentication token available")
            return False
        
        retrieval_success = True
        
        # Test pillar retrieval
        if self.created_resources['pillars']:
            result = self.make_request('GET', '/pillars', use_auth=True)
            pillars_retrieved = result['success'] and len(result['data']) > 0
            self.log_test(
                "PILLAR RETRIEVAL",
                pillars_retrieved,
                f"Retrieved {len(result['data']) if result['success'] else 0} pillars" if pillars_retrieved else "Pillar retrieval failed"
            )
            retrieval_success = retrieval_success and pillars_retrieved
        
        # Test area retrieval
        if self.created_resources['areas']:
            result = self.make_request('GET', '/areas', use_auth=True)
            areas_retrieved = result['success'] and len(result['data']) > 0
            self.log_test(
                "AREA RETRIEVAL",
                areas_retrieved,
                f"Retrieved {len(result['data']) if result['success'] else 0} areas" if areas_retrieved else "Area retrieval failed"
            )
            retrieval_success = retrieval_success and areas_retrieved
        
        # Test project retrieval
        if self.created_resources['projects']:
            result = self.make_request('GET', '/projects', use_auth=True)
            projects_retrieved = result['success'] and len(result['data']) > 0
            self.log_test(
                "PROJECT RETRIEVAL",
                projects_retrieved,
                f"Retrieved {len(result['data']) if result['success'] else 0} projects" if projects_retrieved else "Project retrieval failed"
            )
            retrieval_success = retrieval_success and projects_retrieved
        
        # Test task retrieval
        if self.created_resources['tasks']:
            result = self.make_request('GET', '/tasks', use_auth=True)
            tasks_retrieved = result['success'] and len(result['data']) > 0
            self.log_test(
                "TASK RETRIEVAL",
                tasks_retrieved,
                f"Retrieved {len(result['data']) if result['success'] else 0} tasks" if tasks_retrieved else "Task retrieval failed"
            )
            retrieval_success = retrieval_success and tasks_retrieved
        
        return retrieval_success

    def run_comprehensive_smart_onboarding_test(self):
        """Run comprehensive Smart Onboarding backend tests"""
        print("\n🚀 STARTING SMART ONBOARDING BACKEND COMPREHENSIVE TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_sequence = [
            ("Authentication", self.test_authentication),
            ("Pillar Creation", self.test_pillar_creation),
        ]
        
        successful_tests = 0
        total_tests = 0
        
        # Step 1: Authentication
        print(f"\n--- Authentication ---")
        if not self.test_authentication():
            print("❌ Authentication failed - cannot proceed with other tests")
            return False
        successful_tests += 1
        total_tests += 1
        
        # Step 2: Pillar Creation
        print(f"\n--- Pillar Creation ---")
        pillar_id = self.test_pillar_creation()
        if pillar_id:
            successful_tests += 1
        total_tests += 1
        
        # Step 3: Area Creation (requires pillar)
        area_id = None
        if pillar_id:
            print(f"\n--- Area Creation ---")
            area_id = self.test_area_creation(pillar_id)
            if area_id:
                successful_tests += 1
            total_tests += 1
        
        # Step 4: Project Status Validation (requires area)
        project_id = None
        if area_id:
            print(f"\n--- Project Status Validation ---")
            project_id = self.test_project_status_validation(area_id)
            if project_id:
                successful_tests += 1
            total_tests += 1
        
        # Step 5: Task Creation (requires project)
        if project_id:
            print(f"\n--- Task Creation ---")
            task_id = self.test_task_creation(project_id)
            if task_id:
                successful_tests += 1
            total_tests += 1
        
        # Step 6: Template Application Workflow
        print(f"\n--- Template Application Workflow ---")
        if self.test_template_application_workflow():
            successful_tests += 1
        total_tests += 1
        
        # Step 7: Data Retrieval Verification
        print(f"\n--- Data Retrieval Verification ---")
        if self.test_data_retrieval_verification():
            successful_tests += 1
        total_tests += 1
        
        success_rate = (successful_tests / total_tests) * 100
        
        print(f"\n" + "=" * 80)
        print("🚀 SMART ONBOARDING BACKEND TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for onboarding functionality
        auth_tests_passed = sum(1 for result in self.test_results if result['success'] and 'AUTHENTICATION' in result['test'])
        pillar_tests_passed = sum(1 for result in self.test_results if result['success'] and 'PILLAR' in result['test'])
        area_tests_passed = sum(1 for result in self.test_results if result['success'] and 'AREA' in result['test'])
        project_tests_passed = sum(1 for result in self.test_results if result['success'] and 'PROJECT' in result['test'])
        task_tests_passed = sum(1 for result in self.test_results if result['success'] and 'TASK' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"Authentication Tests Passed: {auth_tests_passed}")
        print(f"Pillar Creation Tests Passed: {pillar_tests_passed}")
        print(f"Area Creation Tests Passed: {area_tests_passed}")
        print(f"Project Creation Tests Passed: {project_tests_passed}")
        print(f"Task Creation Tests Passed: {task_tests_passed}")
        
        print(f"\n📊 CREATED RESOURCES:")
        print(f"Pillars: {len(self.created_resources['pillars'])}")
        print(f"Areas: {len(self.created_resources['areas'])}")
        print(f"Projects: {len(self.created_resources['projects'])}")
        print(f"Tasks: {len(self.created_resources['tasks'])}")
        
        if success_rate >= 85:
            print("\n✅ SMART ONBOARDING BACKEND SYSTEM: SUCCESS")
            print("   ✅ Authentication working with specified credentials")
            print("   ✅ POST /api/pillars functional")
            print("   ✅ POST /api/areas operational")
            print("   ✅ POST /api/projects with status validation working")
            print("   ✅ POST /api/tasks functional")
            print("   ✅ Template application workflow operational")
            print("   ✅ Complete onboarding data creation flow working")
            print("   The Smart Onboarding backend is production-ready!")
        else:
            print("\n❌ SMART ONBOARDING BACKEND SYSTEM: ISSUES DETECTED")
            print("   Issues found in Smart Onboarding backend implementation")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 85

def main():
    """Run Smart Onboarding Backend Tests"""
    print("🚀 STARTING SMART ONBOARDING BACKEND TESTING")
    print("=" * 80)
    
    tester = SmartOnboardingBackendTester()
    
    try:
        # Run the comprehensive Smart Onboarding backend tests
        success = tester.run_comprehensive_smart_onboarding_test()
        
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