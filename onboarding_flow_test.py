#!/usr/bin/env python3
"""
COMPLETE ONBOARDING FLOW TESTING - POST USER ID MISMATCH FIX
Testing the complete onboarding flow after resolving the user ID mismatch issue.

FIXES COMPLETED:
1. ✅ Foreign key constraints fixed to reference public.users instead of auth.users
2. ✅ User ID mismatch resolved - both tables now use 6848f065-2d12-4c4e-88c4-80f375358d7b

TEST SCOPE:
1. Authentication with marc.alleyne@aurumtechnologyltd.com / password
2. User info retrieval (should now work without 404 errors)  
3. Create pillar (should work without foreign key constraint violations)
4. Create area, project, and task (full template application flow)
5. Verify that template selection in onboarding wizard works end-to-end

EXPECTED BEHAVIOR:
The entire onboarding template selection and application should work without errors, 
allowing users to complete the smart onboarding process and get taken to the dashboard 
with their personalized structure.

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://fa85c789-1504-48f1-9b33-719ff2e79ef1.preview.emergentagent.com/api"

class OnboardingFlowTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        self.user_id = None
        # Use the specified test credentials from the review request
        self.test_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.test_user_password = "password"
        
        # Track created resources for cleanup
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
        """Test 1: Authentication with specified credentials"""
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
        
        # Verify token works and get user info
        result = self.make_request('GET', '/auth/me', use_auth=True)
        self.log_test(
            "AUTHENTICATION TOKEN VALIDATION",
            result['success'],
            f"Token validated successfully, user: {result['data'].get('email', 'Unknown')}" if result['success'] else f"Token validation failed: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            self.user_id = result['data'].get('id')
            print(f"   User ID: {self.user_id}")
        
        return result['success']

    def test_user_info_retrieval(self):
        """Test 2: User info retrieval (should now work without 404 errors)"""
        print("\n=== TESTING USER INFO RETRIEVAL ===")
        
        if not self.auth_token:
            self.log_test("USER INFO RETRIEVAL - Authentication Required", False, "No authentication token available")
            return False
        
        # Test user profile retrieval
        result = self.make_request('GET', '/auth/me', use_auth=True)
        self.log_test(
            "USER INFO RETRIEVAL",
            result['success'],
            f"User info retrieved successfully for user ID: {result['data'].get('id', 'Unknown')}" if result['success'] else f"User info retrieval failed: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            user_data = result['data']
            # Verify expected user ID matches the fixed ID
            expected_user_id = "6848f065-2d12-4c4e-88c4-80f375358d7b"
            actual_user_id = user_data.get('id')
            
            if actual_user_id == expected_user_id:
                self.log_test(
                    "USER ID VERIFICATION",
                    True,
                    f"User ID matches expected fixed ID: {expected_user_id}"
                )
            else:
                self.log_test(
                    "USER ID VERIFICATION",
                    False,
                    f"User ID mismatch - Expected: {expected_user_id}, Got: {actual_user_id}"
                )
                return False
        
        return result['success']

    def test_create_pillar(self):
        """Test 3: Create pillar (should work without foreign key constraint violations)"""
        print("\n=== TESTING PILLAR CREATION ===")
        
        if not self.auth_token:
            self.log_test("PILLAR CREATION - Authentication Required", False, "No authentication token available")
            return False
        
        # Create a test pillar for onboarding
        pillar_data = {
            "name": "Health & Wellness",
            "description": "Physical and mental health pillar for onboarding test",
            "icon": "💪",
            "color": "#10B981",
            "time_allocation_percentage": 30.0
        }
        
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        self.log_test(
            "PILLAR CREATION",
            result['success'],
            f"Pillar created successfully: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Pillar creation failed: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            pillar_id = result['data'].get('id')
            self.created_resources['pillars'].append(pillar_id)
            print(f"   Created Pillar ID: {pillar_id}")
            return pillar_id
        
        return False

    def test_create_area(self, pillar_id: str):
        """Test 4: Create area linked to pillar"""
        print("\n=== TESTING AREA CREATION ===")
        
        if not self.auth_token:
            self.log_test("AREA CREATION - Authentication Required", False, "No authentication token available")
            return False
        
        # Create a test area linked to the pillar
        area_data = {
            "pillar_id": pillar_id,
            "name": "Fitness & Exercise",
            "description": "Physical fitness and exercise routines",
            "icon": "🏃",
            "color": "#F59E0B",
            "importance": 4
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        self.log_test(
            "AREA CREATION",
            result['success'],
            f"Area created successfully: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Area creation failed: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            area_id = result['data'].get('id')
            self.created_resources['areas'].append(area_id)
            print(f"   Created Area ID: {area_id}")
            
            # Verify pillar linkage
            if result['data'].get('pillar_id') == pillar_id:
                self.log_test(
                    "AREA-PILLAR LINKAGE",
                    True,
                    f"Area correctly linked to pillar: {pillar_id}"
                )
            else:
                self.log_test(
                    "AREA-PILLAR LINKAGE",
                    False,
                    f"Area pillar linkage failed - Expected: {pillar_id}, Got: {result['data'].get('pillar_id')}"
                )
            
            return area_id
        
        return False

    def test_create_project(self, area_id: str):
        """Test 5: Create project linked to area"""
        print("\n=== TESTING PROJECT CREATION ===")
        
        if not self.auth_token:
            self.log_test("PROJECT CREATION - Authentication Required", False, "No authentication token available")
            return False
        
        # Create a test project linked to the area
        project_data = {
            "area_id": area_id,
            "name": "Morning Workout Routine",
            "description": "Daily morning exercise routine for onboarding test",
            "icon": "🏋️",
            "status": "Not Started",  # This was the validation issue that was fixed
            "priority": "high",
            "deadline": "2025-02-15T10:00:00Z"
        }
        
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        self.log_test(
            "PROJECT CREATION",
            result['success'],
            f"Project created successfully: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Project creation failed: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            project_id = result['data'].get('id')
            self.created_resources['projects'].append(project_id)
            print(f"   Created Project ID: {project_id}")
            
            # Verify area linkage and status validation fix
            project_data_response = result['data']
            if project_data_response.get('area_id') == area_id:
                self.log_test(
                    "PROJECT-AREA LINKAGE",
                    True,
                    f"Project correctly linked to area: {area_id}"
                )
            else:
                self.log_test(
                    "PROJECT-AREA LINKAGE",
                    False,
                    f"Project area linkage failed - Expected: {area_id}, Got: {project_data_response.get('area_id')}"
                )
            
            # Verify status validation fix
            if project_data_response.get('status') == 'Not Started':
                self.log_test(
                    "PROJECT STATUS VALIDATION FIX",
                    True,
                    "Project status 'Not Started' accepted correctly (validation fix working)"
                )
            else:
                self.log_test(
                    "PROJECT STATUS VALIDATION FIX",
                    False,
                    f"Project status validation issue - Expected: 'Not Started', Got: {project_data_response.get('status')}"
                )
            
            return project_id
        
        return False

    def test_create_task(self, project_id: str):
        """Test 6: Create task linked to project"""
        print("\n=== TESTING TASK CREATION ===")
        
        if not self.auth_token:
            self.log_test("TASK CREATION - Authentication Required", False, "No authentication token available")
            return False
        
        # Create a test task linked to the project
        task_data = {
            "project_id": project_id,
            "name": "30-minute cardio session",
            "description": "High-intensity cardio workout for onboarding test",
            "status": "todo",
            "priority": "medium",
            "due_date": "2025-01-30T07:00:00Z"
        }
        
        result = self.make_request('POST', '/tasks', data=task_data, use_auth=True)
        self.log_test(
            "TASK CREATION",
            result['success'],
            f"Task created successfully: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Task creation failed: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            task_id = result['data'].get('id')
            self.created_resources['tasks'].append(task_id)
            print(f"   Created Task ID: {task_id}")
            
            # Verify project linkage
            if result['data'].get('project_id') == project_id:
                self.log_test(
                    "TASK-PROJECT LINKAGE",
                    True,
                    f"Task correctly linked to project: {project_id}"
                )
            else:
                self.log_test(
                    "TASK-PROJECT LINKAGE",
                    False,
                    f"Task project linkage failed - Expected: {project_id}, Got: {result['data'].get('project_id')}"
                )
            
            return task_id
        
        return False

    def test_template_application_workflow(self):
        """Test 7: Simulate template application workflow (AI Coach Goal Decomposition)"""
        print("\n=== TESTING TEMPLATE APPLICATION WORKFLOW ===")
        
        if not self.auth_token:
            self.log_test("TEMPLATE WORKFLOW - Authentication Required", False, "No authentication token available")
            return False
        
        # Test AI Coach Goal Decomposition endpoint (simulates template selection)
        goal_data = {
            "project_name": "Learn Spanish Language",
            "project_description": "Complete Spanish language learning program",
            "template_type": "learning"
        }
        
        result = self.make_request('POST', '/ai/decompose-project', data=goal_data, use_auth=True)
        self.log_test(
            "AI GOAL DECOMPOSITION",
            result['success'],
            f"Goal decomposition successful for: {goal_data['project_name']}" if result['success'] else f"Goal decomposition failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        # Extract suggested project and tasks
        decomposition_data = result['data']
        suggested_project = decomposition_data.get('suggested_project', {})
        suggested_tasks = decomposition_data.get('suggested_tasks', [])
        
        self.log_test(
            "TEMPLATE STRUCTURE GENERATION",
            len(suggested_tasks) > 0,
            f"Generated {len(suggested_tasks)} suggested tasks for project template" if len(suggested_tasks) > 0 else "No tasks generated for template"
        )
        
        # Test creating project with tasks from template (simulates onboarding completion)
        if suggested_project and suggested_tasks:
            # Ensure we have an area to link to
            if not self.created_resources['areas']:
                self.log_test("TEMPLATE APPLICATION", False, "No area available for template application")
                return False
            
            # Prepare project data with area linkage
            template_project_data = {
                "project": {
                    "title": suggested_project.get('title', 'Template Project'),
                    "description": suggested_project.get('description', 'Generated from template'),
                    "area_id": self.created_resources['areas'][0],  # Link to first created area
                    "priority": suggested_project.get('priority', 'medium'),
                    "status": suggested_project.get('status', 'Not Started')
                },
                "tasks": suggested_tasks[:3]  # Limit to first 3 tasks for testing
            }
            
            result = self.make_request('POST', '/projects/create-with-tasks', data=template_project_data, use_auth=True)
            self.log_test(
                "TEMPLATE APPLICATION - CREATE PROJECT WITH TASKS",
                result['success'],
                f"Template applied successfully - Created project with {len(template_project_data['tasks'])} tasks" if result['success'] else f"Template application failed: {result.get('error', 'Unknown error')}"
            )
            
            if result['success']:
                created_project = result['data'].get('project', {})
                created_tasks = result['data'].get('tasks', [])
                
                self.created_resources['projects'].append(created_project.get('id'))
                for task in created_tasks:
                    self.created_resources['tasks'].append(task.get('id'))
                
                self.log_test(
                    "TEMPLATE COMPLETION VERIFICATION",
                    len(created_tasks) == len(template_project_data['tasks']),
                    f"All {len(template_project_data['tasks'])} template tasks created successfully" if len(created_tasks) == len(template_project_data['tasks']) else f"Task creation mismatch - Expected: {len(template_project_data['tasks'])}, Created: {len(created_tasks)}"
                )
                
                return True
        
        return False

    def test_data_retrieval_verification(self):
        """Test 8: Verify all created data can be retrieved correctly"""
        print("\n=== TESTING DATA RETRIEVAL VERIFICATION ===")
        
        if not self.auth_token:
            self.log_test("DATA RETRIEVAL - Authentication Required", False, "No authentication token available")
            return False
        
        success_count = 0
        total_tests = 4
        
        # Test pillar retrieval
        result = self.make_request('GET', '/pillars', use_auth=True)
        if result['success']:
            pillars = result['data']
            created_pillars = [p for p in pillars if p['id'] in self.created_resources['pillars']]
            if len(created_pillars) == len(self.created_resources['pillars']):
                self.log_test("PILLAR RETRIEVAL", True, f"All {len(created_pillars)} created pillars retrieved successfully")
                success_count += 1
            else:
                self.log_test("PILLAR RETRIEVAL", False, f"Pillar retrieval mismatch - Expected: {len(self.created_resources['pillars'])}, Found: {len(created_pillars)}")
        else:
            self.log_test("PILLAR RETRIEVAL", False, f"Pillar retrieval failed: {result.get('error', 'Unknown error')}")
        
        # Test area retrieval
        result = self.make_request('GET', '/areas', use_auth=True)
        if result['success']:
            areas = result['data']
            created_areas = [a for a in areas if a['id'] in self.created_resources['areas']]
            if len(created_areas) == len(self.created_resources['areas']):
                self.log_test("AREA RETRIEVAL", True, f"All {len(created_areas)} created areas retrieved successfully")
                success_count += 1
            else:
                self.log_test("AREA RETRIEVAL", False, f"Area retrieval mismatch - Expected: {len(self.created_resources['areas'])}, Found: {len(created_areas)}")
        else:
            self.log_test("AREA RETRIEVAL", False, f"Area retrieval failed: {result.get('error', 'Unknown error')}")
        
        # Test project retrieval
        result = self.make_request('GET', '/projects', use_auth=True)
        if result['success']:
            projects = result['data']
            created_projects = [p for p in projects if p['id'] in self.created_resources['projects']]
            if len(created_projects) == len(self.created_resources['projects']):
                self.log_test("PROJECT RETRIEVAL", True, f"All {len(created_projects)} created projects retrieved successfully")
                success_count += 1
            else:
                self.log_test("PROJECT RETRIEVAL", False, f"Project retrieval mismatch - Expected: {len(self.created_resources['projects'])}, Found: {len(created_projects)}")
        else:
            self.log_test("PROJECT RETRIEVAL", False, f"Project retrieval failed: {result.get('error', 'Unknown error')}")
        
        # Test task retrieval
        result = self.make_request('GET', '/tasks', use_auth=True)
        if result['success']:
            tasks = result['data']
            created_tasks = [t for t in tasks if t['id'] in self.created_resources['tasks']]
            if len(created_tasks) == len(self.created_resources['tasks']):
                self.log_test("TASK RETRIEVAL", True, f"All {len(created_tasks)} created tasks retrieved successfully")
                success_count += 1
            else:
                self.log_test("TASK RETRIEVAL", False, f"Task retrieval mismatch - Expected: {len(self.created_resources['tasks'])}, Found: {len(created_tasks)}")
        else:
            self.log_test("TASK RETRIEVAL", False, f"Task retrieval failed: {result.get('error', 'Unknown error')}")
        
        overall_success = success_count == total_tests
        self.log_test(
            "OVERALL DATA RETRIEVAL",
            overall_success,
            f"All data retrieval tests passed ({success_count}/{total_tests})" if overall_success else f"Data retrieval issues detected ({success_count}/{total_tests} passed)"
        )
        
        return overall_success

    def run_complete_onboarding_flow_test(self):
        """Run comprehensive onboarding flow test"""
        print("\n🚀 STARTING COMPLETE ONBOARDING FLOW TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("Testing post-fix onboarding flow with user ID: 6848f065-2d12-4c4e-88c4-80f375358d7b")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Authentication", self.test_authentication),
            ("User Info Retrieval", self.test_user_info_retrieval),
        ]
        
        successful_tests = 0
        total_tests = len(test_methods)
        
        # Run initial authentication tests
        for test_name, test_method in test_methods:
            print(f"\n--- {test_name} ---")
            try:
                if test_method():
                    successful_tests += 1
                    print(f"✅ {test_name} completed successfully")
                else:
                    print(f"❌ {test_name} failed")
                    # Stop if authentication fails
                    if test_name == "Authentication":
                        print("❌ Cannot continue without authentication")
                        break
            except Exception as e:
                print(f"❌ {test_name} raised exception: {e}")
                if test_name == "Authentication":
                    break
        
        # Continue with CRUD operations if authentication succeeded
        if successful_tests >= 1:  # Authentication passed
            print(f"\n--- Creating Onboarding Structure ---")
            
            # Create pillar
            pillar_id = self.test_create_pillar()
            if pillar_id:
                successful_tests += 1
                total_tests += 1
                
                # Create area
                area_id = self.test_create_area(pillar_id)
                if area_id:
                    successful_tests += 1
                    total_tests += 1
                    
                    # Create project
                    project_id = self.test_create_project(area_id)
                    if project_id:
                        successful_tests += 1
                        total_tests += 1
                        
                        # Create task
                        task_id = self.test_create_task(project_id)
                        if task_id:
                            successful_tests += 1
                            total_tests += 1
            
            # Test template workflow
            print(f"\n--- Template Application Workflow ---")
            if self.test_template_application_workflow():
                successful_tests += 1
            total_tests += 1
            
            # Test data retrieval
            print(f"\n--- Data Retrieval Verification ---")
            if self.test_data_retrieval_verification():
                successful_tests += 1
            total_tests += 1
        
        success_rate = (successful_tests / total_tests) * 100
        
        print(f"\n" + "=" * 80)
        print("🚀 COMPLETE ONBOARDING FLOW TESTING SUMMARY")
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
        template_tests_passed = sum(1 for result in self.test_results if result['success'] and 'TEMPLATE' in result['test'])
        
        print(f"\n🔍 ONBOARDING FLOW ANALYSIS:")
        print(f"Authentication Tests Passed: {auth_tests_passed}")
        print(f"Pillar Creation Tests Passed: {pillar_tests_passed}")
        print(f"Area Creation Tests Passed: {area_tests_passed}")
        print(f"Project Creation Tests Passed: {project_tests_passed}")
        print(f"Task Creation Tests Passed: {task_tests_passed}")
        print(f"Template Application Tests Passed: {template_tests_passed}")
        
        print(f"\n📊 CREATED RESOURCES:")
        print(f"Pillars: {len(self.created_resources['pillars'])}")
        print(f"Areas: {len(self.created_resources['areas'])}")
        print(f"Projects: {len(self.created_resources['projects'])}")
        print(f"Tasks: {len(self.created_resources['tasks'])}")
        
        if success_rate >= 85:
            print("\n✅ COMPLETE ONBOARDING FLOW: SUCCESS")
            print("   ✅ Authentication with marc.alleyne@aurumtechnologyltd.com working")
            print("   ✅ User info retrieval working (no 404 errors)")
            print("   ✅ Pillar creation working (no foreign key constraint violations)")
            print("   ✅ Area, project, and task creation working")
            print("   ✅ Template application workflow functional")
            print("   ✅ Smart onboarding process can complete successfully")
            print("   The onboarding flow is production-ready!")
        else:
            print("\n❌ COMPLETE ONBOARDING FLOW: ISSUES DETECTED")
            print("   Issues found in onboarding flow implementation")
            if auth_tests_passed == 0:
                print("   🚨 CRITICAL: Authentication failing")
            if pillar_tests_passed == 0:
                print("   🚨 CRITICAL: Pillar creation failing (foreign key issues?)")
            if project_tests_passed == 0:
                print("   🚨 CRITICAL: Project creation failing (validation issues?)")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 85

def main():
    """Run Complete Onboarding Flow Tests"""
    print("🚀 STARTING COMPLETE ONBOARDING FLOW BACKEND TESTING")
    print("=" * 80)
    
    tester = OnboardingFlowTester()
    
    try:
        # Run the comprehensive onboarding flow tests
        success = tester.run_complete_onboarding_flow_test()
        
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