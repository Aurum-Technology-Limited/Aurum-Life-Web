#!/usr/bin/env python3
"""
ONBOARDING PILLAR CREATION FIX TESTING - POST DATABASE FIXES
Testing the onboarding pillar creation after manual database fixes.

MANUAL DATABASE FIXES COMPLETED:
1. Fixed foreign key constraints to reference public.users instead of auth.users
2. Created the missing user record (272edb74-8be3-4504-818c-b1dd42c63ebe) in the public.users table

TEST FOCUS:
1. Authentication with marc.alleyne@aurumtechnologyltd.com / password
2. Create a pillar to verify the foreign key constraint issue is resolved
3. Test the complete onboarding flow if possible (create pillar → area → project → task)
4. Verify that template selection now works without errors

EXPECTED BEHAVIOR:
Pillar/area/project/task creation should work without foreign key constraint violations,
and the complete onboarding template application should succeed.

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://8f296db8-41e4-45d4-b9b1-dbc5e21b4a2a.preview.emergentagent.com/api"

class OnboardingPillarCreationTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Use the specified test credentials from the review request
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

    def test_pillar_creation(self):
        """Test pillar creation to verify foreign key constraint fix"""
        print("\n=== TESTING PILLAR CREATION (FOREIGN KEY CONSTRAINT FIX) ===")
        
        if not self.auth_token:
            self.log_test("PILLAR CREATION - Authentication Required", False, "No authentication token available")
            return False
        
        # Create a pillar with realistic onboarding data
        pillar_data = {
            "name": "Health & Wellness",
            "description": "Physical and mental health, fitness, and overall well-being",
            "icon": "💪",
            "color": "#10B981",
            "time_allocation_percentage": 25.0
        }
        
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        
        if result['success']:
            pillar = result['data']
            self.created_resources['pillars'].append(pillar.get('id'))
            self.log_test(
                "PILLAR CREATION",
                True,
                f"Pillar '{pillar_data['name']}' created successfully with ID: {pillar.get('id')}"
            )
            return pillar.get('id')
        else:
            # Check if it's a foreign key constraint error
            error_msg = str(result.get('error', ''))
            if 'foreign key constraint' in error_msg.lower() or 'violates foreign key' in error_msg.lower():
                self.log_test(
                    "PILLAR CREATION - FOREIGN KEY CONSTRAINT ERROR",
                    False,
                    f"Foreign key constraint violation still occurring: {error_msg}"
                )
            else:
                self.log_test(
                    "PILLAR CREATION",
                    False,
                    f"Pillar creation failed: {result.get('error', 'Unknown error')}"
                )
            return False

    def test_area_creation(self, pillar_id: str):
        """Test area creation linked to the pillar"""
        print("\n=== TESTING AREA CREATION ===")
        
        if not pillar_id:
            self.log_test("AREA CREATION - Pillar Required", False, "No pillar ID available")
            return False
        
        # Create an area linked to the pillar
        area_data = {
            "pillar_id": pillar_id,
            "name": "Fitness & Exercise",
            "description": "Physical fitness, workouts, and exercise routines",
            "icon": "🏃",
            "color": "#F59E0B",
            "importance": 4
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        
        if result['success']:
            area = result['data']
            self.created_resources['areas'].append(area.get('id'))
            self.log_test(
                "AREA CREATION",
                True,
                f"Area '{area_data['name']}' created successfully with ID: {area.get('id')}"
            )
            return area.get('id')
        else:
            # Check if it's a foreign key constraint error
            error_msg = str(result.get('error', ''))
            if 'foreign key constraint' in error_msg.lower() or 'violates foreign key' in error_msg.lower():
                self.log_test(
                    "AREA CREATION - FOREIGN KEY CONSTRAINT ERROR",
                    False,
                    f"Foreign key constraint violation: {error_msg}"
                )
            else:
                self.log_test(
                    "AREA CREATION",
                    False,
                    f"Area creation failed: {result.get('error', 'Unknown error')}"
                )
            return False

    def test_project_creation(self, area_id: str):
        """Test project creation linked to the area"""
        print("\n=== TESTING PROJECT CREATION ===")
        
        if not area_id:
            self.log_test("PROJECT CREATION - Area Required", False, "No area ID available")
            return False
        
        # Create a project linked to the area
        project_data = {
            "area_id": area_id,
            "name": "Morning Workout Routine",
            "description": "Establish a consistent morning exercise routine",
            "icon": "🏋️",
            "status": "Not Started",
            "priority": "high",
            "deadline": "2025-02-15T10:00:00Z"
        }
        
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        
        if result['success']:
            project = result['data']
            self.created_resources['projects'].append(project.get('id'))
            self.log_test(
                "PROJECT CREATION",
                True,
                f"Project '{project_data['name']}' created successfully with ID: {project.get('id')}"
            )
            return project.get('id')
        else:
            # Check if it's a foreign key constraint error
            error_msg = str(result.get('error', ''))
            if 'foreign key constraint' in error_msg.lower() or 'violates foreign key' in error_msg.lower():
                self.log_test(
                    "PROJECT CREATION - FOREIGN KEY CONSTRAINT ERROR",
                    False,
                    f"Foreign key constraint violation: {error_msg}"
                )
            else:
                self.log_test(
                    "PROJECT CREATION",
                    False,
                    f"Project creation failed: {result.get('error', 'Unknown error')}"
                )
            return False

    def test_task_creation(self, project_id: str):
        """Test task creation linked to the project"""
        print("\n=== TESTING TASK CREATION ===")
        
        if not project_id:
            self.log_test("TASK CREATION - Project Required", False, "No project ID available")
            return False
        
        # Create a task linked to the project
        task_data = {
            "project_id": project_id,
            "name": "30-minute cardio session",
            "description": "High-intensity cardio workout to start the day",
            "status": "todo",
            "priority": "medium",
            "due_date": "2025-01-30T07:00:00Z",
            "estimated_duration": 30
        }
        
        result = self.make_request('POST', '/tasks', data=task_data, use_auth=True)
        
        if result['success']:
            task = result['data']
            self.created_resources['tasks'].append(task.get('id'))
            self.log_test(
                "TASK CREATION",
                True,
                f"Task '{task_data['name']}' created successfully with ID: {task.get('id')}"
            )
            return task.get('id')
        else:
            # Check if it's a foreign key constraint error
            error_msg = str(result.get('error', ''))
            if 'foreign key constraint' in error_msg.lower() or 'violates foreign key' in error_msg.lower():
                self.log_test(
                    "TASK CREATION - FOREIGN KEY CONSTRAINT ERROR",
                    False,
                    f"Foreign key constraint violation: {error_msg}"
                )
            else:
                self.log_test(
                    "TASK CREATION",
                    False,
                    f"Task creation failed: {result.get('error', 'Unknown error')}"
                )
            return False

    def test_template_application(self):
        """Test template application using AI Coach Goal Decomposition"""
        print("\n=== TESTING TEMPLATE APPLICATION (AI COACH GOAL DECOMPOSITION) ===")
        
        if not self.auth_token:
            self.log_test("TEMPLATE APPLICATION - Authentication Required", False, "No authentication token available")
            return False
        
        # Test AI Coach Goal Decomposition endpoint
        goal_data = {
            "project_name": "Learn Spanish Language",
            "project_description": "Become conversational in Spanish within 6 months",
            "template_type": "learning"
        }
        
        result = self.make_request('POST', '/ai/decompose-project', data=goal_data, use_auth=True)
        
        if result['success']:
            decomposition = result['data']
            self.log_test(
                "AI GOAL DECOMPOSITION",
                True,
                f"Goal decomposition successful, suggested {len(decomposition.get('suggested_tasks', []))} tasks"
            )
            
            # Test creating project with tasks from decomposition
            if 'suggested_project' in decomposition and 'suggested_tasks' in decomposition:
                create_data = {
                    "project": decomposition['suggested_project'],
                    "tasks": decomposition['suggested_tasks']
                }
                
                result = self.make_request('POST', '/projects/create-with-tasks', data=create_data, use_auth=True)
                
                if result['success']:
                    created_project = result['data']
                    self.created_resources['projects'].append(created_project.get('project', {}).get('id'))
                    self.log_test(
                        "TEMPLATE APPLICATION - PROJECT WITH TASKS CREATION",
                        True,
                        f"Template applied successfully: created project with {len(created_project.get('tasks', []))} tasks"
                    )
                    return True
                else:
                    error_msg = str(result.get('error', ''))
                    if 'foreign key constraint' in error_msg.lower() or 'violates foreign key' in error_msg.lower():
                        self.log_test(
                            "TEMPLATE APPLICATION - FOREIGN KEY CONSTRAINT ERROR",
                            False,
                            f"Foreign key constraint violation during template application: {error_msg}"
                        )
                    else:
                        self.log_test(
                            "TEMPLATE APPLICATION - PROJECT WITH TASKS CREATION",
                            False,
                            f"Template application failed: {result.get('error', 'Unknown error')}"
                        )
                    return False
            else:
                self.log_test(
                    "TEMPLATE APPLICATION - INVALID DECOMPOSITION RESPONSE",
                    False,
                    "Goal decomposition response missing required fields"
                )
                return False
        else:
            self.log_test(
                "AI GOAL DECOMPOSITION",
                False,
                f"Goal decomposition failed: {result.get('error', 'Unknown error')}"
            )
            return False

    def test_data_retrieval(self):
        """Test data retrieval to verify all created resources are accessible"""
        print("\n=== TESTING DATA RETRIEVAL ===")
        
        if not self.auth_token:
            self.log_test("DATA RETRIEVAL - Authentication Required", False, "No authentication token available")
            return False
        
        success_count = 0
        total_tests = 4
        
        # Test pillars retrieval
        result = self.make_request('GET', '/pillars', use_auth=True)
        if result['success']:
            pillars = result['data']
            created_pillar_found = any(p.get('id') in self.created_resources['pillars'] for p in pillars)
            if created_pillar_found:
                self.log_test("PILLARS RETRIEVAL", True, f"Retrieved {len(pillars)} pillars, created pillar found")
                success_count += 1
            else:
                self.log_test("PILLARS RETRIEVAL", False, "Created pillar not found in retrieval")
        else:
            self.log_test("PILLARS RETRIEVAL", False, f"Failed to retrieve pillars: {result.get('error')}")
        
        # Test areas retrieval
        result = self.make_request('GET', '/areas', use_auth=True)
        if result['success']:
            areas = result['data']
            created_area_found = any(a.get('id') in self.created_resources['areas'] for a in areas)
            if created_area_found:
                self.log_test("AREAS RETRIEVAL", True, f"Retrieved {len(areas)} areas, created area found")
                success_count += 1
            else:
                self.log_test("AREAS RETRIEVAL", False, "Created area not found in retrieval")
        else:
            self.log_test("AREAS RETRIEVAL", False, f"Failed to retrieve areas: {result.get('error')}")
        
        # Test projects retrieval
        result = self.make_request('GET', '/projects', use_auth=True)
        if result['success']:
            projects = result['data']
            created_project_found = any(p.get('id') in self.created_resources['projects'] for p in projects)
            if created_project_found:
                self.log_test("PROJECTS RETRIEVAL", True, f"Retrieved {len(projects)} projects, created project found")
                success_count += 1
            else:
                self.log_test("PROJECTS RETRIEVAL", False, "Created project not found in retrieval")
        else:
            self.log_test("PROJECTS RETRIEVAL", False, f"Failed to retrieve projects: {result.get('error')}")
        
        # Test tasks retrieval
        result = self.make_request('GET', '/tasks', use_auth=True)
        if result['success']:
            tasks = result['data']
            created_task_found = any(t.get('id') in self.created_resources['tasks'] for t in tasks)
            if created_task_found:
                self.log_test("TASKS RETRIEVAL", True, f"Retrieved {len(tasks)} tasks, created task found")
                success_count += 1
            else:
                self.log_test("TASKS RETRIEVAL", False, "Created task not found in retrieval")
        else:
            self.log_test("TASKS RETRIEVAL", False, f"Failed to retrieve tasks: {result.get('error')}")
        
        return success_count == total_tests

    def run_comprehensive_onboarding_test(self):
        """Run comprehensive onboarding pillar creation test"""
        print("\n🚀 STARTING ONBOARDING PILLAR CREATION TESTING - POST DATABASE FIXES")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("Database Fixes Applied:")
        print("  1. Fixed foreign key constraints to reference public.users instead of auth.users")
        print("  2. Created missing user record (272edb74-8be3-4504-818c-b1dd42c63ebe) in public.users table")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("User Authentication", self.test_user_authentication),
        ]
        
        successful_tests = 0
        total_tests = len(test_methods)
        
        # Run basic tests first
        for test_name, test_method in test_methods:
            print(f"\n--- {test_name} ---")
            try:
                if test_method():
                    successful_tests += 1
                    print(f"✅ {test_name} completed successfully")
                else:
                    print(f"❌ {test_name} failed")
                    # If authentication fails, we can't continue
                    if test_name == "User Authentication":
                        print("❌ Cannot continue without authentication")
                        break
            except Exception as e:
                print(f"❌ {test_name} raised exception: {e}")
                if test_name == "User Authentication":
                    break
        
        # If authentication succeeded, run the onboarding flow tests
        if self.auth_token:
            print(f"\n--- Complete Onboarding Flow Test ---")
            
            # Test pillar creation (the main fix)
            pillar_id = self.test_pillar_creation()
            if pillar_id:
                successful_tests += 1
                total_tests += 1
                
                # Test area creation
                area_id = self.test_area_creation(pillar_id)
                if area_id:
                    successful_tests += 1
                    total_tests += 1
                    
                    # Test project creation
                    project_id = self.test_project_creation(area_id)
                    if project_id:
                        successful_tests += 1
                        total_tests += 1
                        
                        # Test task creation
                        task_id = self.test_task_creation(project_id)
                        if task_id:
                            successful_tests += 1
                            total_tests += 1
                        else:
                            total_tests += 1
                    else:
                        total_tests += 1
                else:
                    total_tests += 1
            else:
                total_tests += 1
            
            # Test template application
            print(f"\n--- Template Application Test ---")
            if self.test_template_application():
                successful_tests += 1
            total_tests += 1
            
            # Test data retrieval
            print(f"\n--- Data Retrieval Test ---")
            if self.test_data_retrieval():
                successful_tests += 1
            total_tests += 1
        
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n" + "=" * 80)
        print("🚀 ONBOARDING PILLAR CREATION TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for foreign key constraint fixes
        foreign_key_errors = sum(1 for result in self.test_results if 'FOREIGN KEY CONSTRAINT ERROR' in result['test'])
        pillar_creation_success = sum(1 for result in self.test_results if result['success'] and 'PILLAR CREATION' in result['test'])
        template_application_success = sum(1 for result in self.test_results if result['success'] and 'TEMPLATE APPLICATION' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"Foreign Key Constraint Errors: {foreign_key_errors}")
        print(f"Pillar Creation Success: {pillar_creation_success > 0}")
        print(f"Template Application Success: {template_application_success > 0}")
        print(f"Created Resources: Pillars: {len(self.created_resources['pillars'])}, Areas: {len(self.created_resources['areas'])}, Projects: {len(self.created_resources['projects'])}, Tasks: {len(self.created_resources['tasks'])}")
        
        if success_rate >= 85 and foreign_key_errors == 0:
            print("\n✅ ONBOARDING PILLAR CREATION FIX: SUCCESS")
            print("   ✅ Authentication working with specified credentials")
            print("   ✅ Pillar creation working without foreign key constraint violations")
            print("   ✅ Complete onboarding flow (pillar → area → project → task) functional")
            print("   ✅ Template selection and application working")
            print("   ✅ Data retrieval and persistence verified")
            print("   The database fixes have successfully resolved the onboarding issues!")
        elif foreign_key_errors > 0:
            print("\n❌ ONBOARDING PILLAR CREATION FIX: FOREIGN KEY CONSTRAINTS STILL FAILING")
            print("   ❌ Foreign key constraint violations still occurring")
            print("   🔧 Additional database fixes may be required")
        else:
            print("\n⚠️ ONBOARDING PILLAR CREATION FIX: PARTIAL SUCCESS")
            print("   ⚠️ Some issues detected in onboarding flow implementation")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 85 and foreign_key_errors == 0

def main():
    """Run Onboarding Pillar Creation Tests"""
    print("🚀 STARTING ONBOARDING PILLAR CREATION BACKEND TESTING - POST DATABASE FIXES")
    print("=" * 80)
    
    tester = OnboardingPillarCreationTester()
    
    try:
        # Run the comprehensive onboarding pillar creation tests
        success = tester.run_comprehensive_onboarding_test()
        
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