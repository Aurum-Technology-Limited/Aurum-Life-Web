#!/usr/bin/env python3
"""
ONBOARDING PILLAR CREATION FIX TESTING - COMPREHENSIVE TESTING
Testing the fix for foreign key constraint violations when creating pillars, areas, projects, and tasks.

ISSUE DESCRIPTION:
Users existed in the user_profiles table but not in the users table, causing foreign key constraint 
violations when creating pillars, areas, projects, and tasks.

FIX IMPLEMENTED:
Automatically creates the user in the users table if they don't exist when creating pillars, areas, 
projects, or tasks.

TESTING CRITERIA:
1. Authentication with existing credentials
2. Create a pillar to verify the fix works 
3. Test the complete onboarding flow (create pillar → area → project → task)
4. Verify that the foreign key constraint error is resolved

EXPECTED BEHAVIOR:
Pillar/area/project/task creation should work without foreign key constraint violations, 
and users should be automatically created in the users table when needed.

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

class OnboardingPillarFixTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Use the specified test credentials
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

    def test_pillar_creation_fix(self):
        """Test pillar creation to verify the foreign key constraint fix"""
        print("\n=== TESTING PILLAR CREATION FIX ===")
        
        if not self.auth_token:
            self.log_test("PILLAR CREATION - Authentication Required", False, "No authentication token available")
            return False
        
        # Test creating a pillar - this should trigger the user creation fix if needed
        pillar_data = {
            "name": "Health & Wellness",
            "description": "Physical and mental health pillar for onboarding test",
            "icon": "💪",
            "color": "#10B981",
            "time_allocation_percentage": 30.0
        }
        
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        
        if result['success']:
            pillar = result['data']
            self.created_resources['pillars'].append(pillar.get('id'))
            
            self.log_test(
                "PILLAR CREATION WITH FK FIX",
                True,
                f"Pillar '{pillar_data['name']}' created successfully - Foreign key constraint fix working"
            )
            
            # Verify the pillar was actually created and can be retrieved
            get_result = self.make_request('GET', '/pillars', use_auth=True)
            if get_result['success']:
                pillars = get_result['data']
                created_pillar = next((p for p in pillars if p.get('id') == pillar.get('id')), None)
                
                if created_pillar:
                    self.log_test(
                        "PILLAR RETRIEVAL VERIFICATION",
                        True,
                        f"Created pillar found in database with ID: {pillar.get('id')}"
                    )
                    return pillar.get('id')
                else:
                    self.log_test(
                        "PILLAR RETRIEVAL VERIFICATION",
                        False,
                        "Created pillar not found in database"
                    )
                    return False
            else:
                self.log_test(
                    "PILLAR RETRIEVAL VERIFICATION",
                    False,
                    f"Failed to retrieve pillars: {get_result.get('error', 'Unknown error')}"
                )
                return False
        else:
            # Check if this is a foreign key constraint error
            error_message = str(result.get('error', ''))
            if 'foreign key' in error_message.lower() or 'constraint' in error_message.lower():
                self.log_test(
                    "PILLAR CREATION WITH FK FIX",
                    False,
                    f"FOREIGN KEY CONSTRAINT ERROR STILL EXISTS: {error_message}"
                )
            else:
                self.log_test(
                    "PILLAR CREATION WITH FK FIX",
                    False,
                    f"Pillar creation failed: {result.get('error', 'Unknown error')}"
                )
            return False

    def test_area_creation_fix(self, pillar_id: str):
        """Test area creation to verify the foreign key constraint fix"""
        print("\n=== TESTING AREA CREATION FIX ===")
        
        if not self.auth_token:
            self.log_test("AREA CREATION - Authentication Required", False, "No authentication token available")
            return False
        
        # Test creating an area - this should also trigger the user creation fix if needed
        area_data = {
            "pillar_id": pillar_id,
            "name": "Fitness & Exercise",
            "description": "Physical fitness and exercise routines for onboarding test",
            "icon": "🏃",
            "color": "#F59E0B",
            "importance": 4
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        
        if result['success']:
            area = result['data']
            self.created_resources['areas'].append(area.get('id'))
            
            self.log_test(
                "AREA CREATION WITH FK FIX",
                True,
                f"Area '{area_data['name']}' created successfully - Foreign key constraint fix working"
            )
            
            # Verify the area was actually created and linked to the pillar
            get_result = self.make_request('GET', '/areas', use_auth=True)
            if get_result['success']:
                areas = get_result['data']
                created_area = next((a for a in areas if a.get('id') == area.get('id')), None)
                
                if created_area and created_area.get('pillar_id') == pillar_id:
                    self.log_test(
                        "AREA RETRIEVAL AND LINKING VERIFICATION",
                        True,
                        f"Created area found in database with correct pillar link: {area.get('id')}"
                    )
                    return area.get('id')
                else:
                    self.log_test(
                        "AREA RETRIEVAL AND LINKING VERIFICATION",
                        False,
                        "Created area not found or pillar link incorrect"
                    )
                    return False
            else:
                self.log_test(
                    "AREA RETRIEVAL VERIFICATION",
                    False,
                    f"Failed to retrieve areas: {get_result.get('error', 'Unknown error')}"
                )
                return False
        else:
            # Check if this is a foreign key constraint error
            error_message = str(result.get('error', ''))
            if 'foreign key' in error_message.lower() or 'constraint' in error_message.lower():
                self.log_test(
                    "AREA CREATION WITH FK FIX",
                    False,
                    f"FOREIGN KEY CONSTRAINT ERROR STILL EXISTS: {error_message}"
                )
            else:
                self.log_test(
                    "AREA CREATION WITH FK FIX",
                    False,
                    f"Area creation failed: {result.get('error', 'Unknown error')}"
                )
            return False

    def test_project_creation_fix(self, area_id: str):
        """Test project creation to verify the foreign key constraint fix"""
        print("\n=== TESTING PROJECT CREATION FIX ===")
        
        if not self.auth_token:
            self.log_test("PROJECT CREATION - Authentication Required", False, "No authentication token available")
            return False
        
        # Test creating a project - this should also trigger the user creation fix if needed
        project_data = {
            "area_id": area_id,
            "name": "Morning Workout Routine",
            "description": "Daily morning exercise routine for onboarding test",
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
                "PROJECT CREATION WITH FK FIX",
                True,
                f"Project '{project_data['name']}' created successfully - Foreign key constraint fix working"
            )
            
            # Verify the project was actually created and linked to the area
            get_result = self.make_request('GET', '/projects', use_auth=True)
            if get_result['success']:
                projects = get_result['data']
                created_project = next((p for p in projects if p.get('id') == project.get('id')), None)
                
                if created_project and created_project.get('area_id') == area_id:
                    self.log_test(
                        "PROJECT RETRIEVAL AND LINKING VERIFICATION",
                        True,
                        f"Created project found in database with correct area link: {project.get('id')}"
                    )
                    return project.get('id')
                else:
                    self.log_test(
                        "PROJECT RETRIEVAL AND LINKING VERIFICATION",
                        False,
                        "Created project not found or area link incorrect"
                    )
                    return False
            else:
                self.log_test(
                    "PROJECT RETRIEVAL VERIFICATION",
                    False,
                    f"Failed to retrieve projects: {get_result.get('error', 'Unknown error')}"
                )
                return False
        else:
            # Check if this is a foreign key constraint error
            error_message = str(result.get('error', ''))
            if 'foreign key' in error_message.lower() or 'constraint' in error_message.lower():
                self.log_test(
                    "PROJECT CREATION WITH FK FIX",
                    False,
                    f"FOREIGN KEY CONSTRAINT ERROR STILL EXISTS: {error_message}"
                )
            else:
                self.log_test(
                    "PROJECT CREATION WITH FK FIX",
                    False,
                    f"Project creation failed: {result.get('error', 'Unknown error')}"
                )
            return False

    def test_task_creation_fix(self, project_id: str):
        """Test task creation to verify the foreign key constraint fix"""
        print("\n=== TESTING TASK CREATION FIX ===")
        
        if not self.auth_token:
            self.log_test("TASK CREATION - Authentication Required", False, "No authentication token available")
            return False
        
        # Test creating a task - this should also trigger the user creation fix if needed
        task_data = {
            "project_id": project_id,
            "name": "30-minute cardio session",
            "description": "High-intensity cardio workout for onboarding test",
            "status": "todo",
            "priority": "medium",
            "due_date": "2025-01-30T07:00:00Z"
        }
        
        result = self.make_request('POST', '/tasks', data=task_data, use_auth=True)
        
        if result['success']:
            task = result['data']
            self.created_resources['tasks'].append(task.get('id'))
            
            self.log_test(
                "TASK CREATION WITH FK FIX",
                True,
                f"Task '{task_data['name']}' created successfully - Foreign key constraint fix working"
            )
            
            # Verify the task was actually created and linked to the project
            get_result = self.make_request('GET', f'/tasks?project_id={project_id}', use_auth=True)
            if get_result['success']:
                tasks = get_result['data']
                created_task = next((t for t in tasks if t.get('id') == task.get('id')), None)
                
                if created_task and created_task.get('project_id') == project_id:
                    self.log_test(
                        "TASK RETRIEVAL AND LINKING VERIFICATION",
                        True,
                        f"Created task found in database with correct project link: {task.get('id')}"
                    )
                    return task.get('id')
                else:
                    self.log_test(
                        "TASK RETRIEVAL AND LINKING VERIFICATION",
                        False,
                        "Created task not found or project link incorrect"
                    )
                    return False
            else:
                self.log_test(
                    "TASK RETRIEVAL VERIFICATION",
                    False,
                    f"Failed to retrieve tasks: {get_result.get('error', 'Unknown error')}"
                )
                return False
        else:
            # Check if this is a foreign key constraint error
            error_message = str(result.get('error', ''))
            if 'foreign key' in error_message.lower() or 'constraint' in error_message.lower():
                self.log_test(
                    "TASK CREATION WITH FK FIX",
                    False,
                    f"FOREIGN KEY CONSTRAINT ERROR STILL EXISTS: {error_message}"
                )
            else:
                self.log_test(
                    "TASK CREATION WITH FK FIX",
                    False,
                    f"Task creation failed: {result.get('error', 'Unknown error')}"
                )
            return False

    def test_complete_onboarding_flow(self):
        """Test the complete onboarding flow: pillar → area → project → task"""
        print("\n=== TESTING COMPLETE ONBOARDING FLOW ===")
        
        # Step 1: Create Pillar
        pillar_id = self.test_pillar_creation_fix()
        if not pillar_id:
            self.log_test(
                "COMPLETE ONBOARDING FLOW",
                False,
                "Failed at pillar creation step"
            )
            return False
        
        # Step 2: Create Area
        area_id = self.test_area_creation_fix(pillar_id)
        if not area_id:
            self.log_test(
                "COMPLETE ONBOARDING FLOW",
                False,
                "Failed at area creation step"
            )
            return False
        
        # Step 3: Create Project
        project_id = self.test_project_creation_fix(area_id)
        if not project_id:
            self.log_test(
                "COMPLETE ONBOARDING FLOW",
                False,
                "Failed at project creation step"
            )
            return False
        
        # Step 4: Create Task
        task_id = self.test_task_creation_fix(project_id)
        if not task_id:
            self.log_test(
                "COMPLETE ONBOARDING FLOW",
                False,
                "Failed at task creation step"
            )
            return False
        
        # If we get here, the complete flow worked
        self.log_test(
            "COMPLETE ONBOARDING FLOW",
            True,
            f"Complete onboarding flow successful: Pillar({pillar_id}) → Area({area_id}) → Project({project_id}) → Task({task_id})"
        )
        
        return True

    def test_foreign_key_constraint_resolution(self):
        """Test that foreign key constraints are properly resolved"""
        print("\n=== TESTING FOREIGN KEY CONSTRAINT RESOLUTION ===")
        
        # Try to create multiple resources in quick succession to test the fix
        test_resources = []
        
        for i in range(3):
            # Create pillar
            pillar_data = {
                "name": f"Test Pillar {i+1}",
                "description": f"Test pillar {i+1} for FK constraint testing",
                "icon": "🧪",
                "color": "#6366F1",
                "time_allocation_percentage": 20.0
            }
            
            result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
            
            if result['success']:
                pillar_id = result['data'].get('id')
                test_resources.append(('pillar', pillar_id))
                self.created_resources['pillars'].append(pillar_id)
                
                # Create area for this pillar
                area_data = {
                    "pillar_id": pillar_id,
                    "name": f"Test Area {i+1}",
                    "description": f"Test area {i+1} for FK constraint testing",
                    "icon": "🔬",
                    "color": "#8B5CF6",
                    "importance": 3
                }
                
                area_result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
                
                if area_result['success']:
                    area_id = area_result['data'].get('id')
                    test_resources.append(('area', area_id))
                    self.created_resources['areas'].append(area_id)
                else:
                    error_message = str(area_result.get('error', ''))
                    if 'foreign key' in error_message.lower() or 'constraint' in error_message.lower():
                        self.log_test(
                            "FK CONSTRAINT RESOLUTION - RAPID CREATION",
                            False,
                            f"Foreign key constraint error in rapid creation test: {error_message}"
                        )
                        return False
            else:
                error_message = str(result.get('error', ''))
                if 'foreign key' in error_message.lower() or 'constraint' in error_message.lower():
                    self.log_test(
                        "FK CONSTRAINT RESOLUTION - RAPID CREATION",
                        False,
                        f"Foreign key constraint error in rapid creation test: {error_message}"
                    )
                    return False
        
        success_count = len([r for r in test_resources if r[0] in ['pillar', 'area']])
        expected_count = 6  # 3 pillars + 3 areas
        
        if success_count >= expected_count * 0.8:  # 80% success rate
            self.log_test(
                "FK CONSTRAINT RESOLUTION - RAPID CREATION",
                True,
                f"Rapid resource creation successful: {success_count}/{expected_count} resources created without FK errors"
            )
            return True
        else:
            self.log_test(
                "FK CONSTRAINT RESOLUTION - RAPID CREATION",
                False,
                f"Rapid resource creation failed: only {success_count}/{expected_count} resources created"
            )
            return False

    def cleanup_test_resources(self):
        """Clean up created test resources"""
        print("\n=== CLEANING UP TEST RESOURCES ===")
        
        cleanup_count = 0
        total_resources = sum(len(resources) for resources in self.created_resources.values())
        
        # Delete in reverse order: tasks → projects → areas → pillars
        for task_id in self.created_resources['tasks']:
            try:
                result = self.make_request('DELETE', f'/tasks/{task_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
            except:
                pass
        
        for project_id in self.created_resources['projects']:
            try:
                result = self.make_request('DELETE', f'/projects/{project_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
            except:
                pass
        
        for area_id in self.created_resources['areas']:
            try:
                result = self.make_request('DELETE', f'/areas/{area_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
            except:
                pass
        
        for pillar_id in self.created_resources['pillars']:
            try:
                result = self.make_request('DELETE', f'/pillars/{pillar_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
            except:
                pass
        
        self.log_test(
            "RESOURCE CLEANUP",
            cleanup_count >= total_resources * 0.8,
            f"Cleaned up {cleanup_count}/{total_resources} test resources"
        )

    def run_comprehensive_onboarding_fix_test(self):
        """Run comprehensive onboarding pillar creation fix tests"""
        print("\n🔧 STARTING ONBOARDING PILLAR CREATION FIX TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("Issue: Foreign key constraint violations when creating pillars/areas/projects/tasks")
        print("Fix: Automatically create user in users table if they don't exist")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("User Authentication", self.test_user_authentication),
            ("Complete Onboarding Flow", self.test_complete_onboarding_flow),
            ("Foreign Key Constraint Resolution", self.test_foreign_key_constraint_resolution),
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
        try:
            self.cleanup_test_resources()
        except Exception as e:
            print(f"⚠️ Cleanup failed: {e}")
        
        success_rate = (successful_tests / total_tests) * 100
        
        print(f"\n" + "=" * 80)
        print("🔧 ONBOARDING PILLAR CREATION FIX TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for the specific fix
        pillar_tests_passed = sum(1 for result in self.test_results if result['success'] and 'PILLAR' in result['test'])
        area_tests_passed = sum(1 for result in self.test_results if result['success'] and 'AREA' in result['test'])
        project_tests_passed = sum(1 for result in self.test_results if result['success'] and 'PROJECT' in result['test'])
        task_tests_passed = sum(1 for result in self.test_results if result['success'] and 'TASK' in result['test'])
        fk_tests_passed = sum(1 for result in self.test_results if result['success'] and 'FK CONSTRAINT' in result['test'])
        
        print(f"\n🔍 FIX ANALYSIS:")
        print(f"Pillar Creation Tests Passed: {pillar_tests_passed}")
        print(f"Area Creation Tests Passed: {area_tests_passed}")
        print(f"Project Creation Tests Passed: {project_tests_passed}")
        print(f"Task Creation Tests Passed: {task_tests_passed}")
        print(f"FK Constraint Resolution Tests Passed: {fk_tests_passed}")
        
        # Check for foreign key constraint errors
        fk_errors = [result for result in self.test_results if not result['success'] and 
                    ('foreign key' in result['message'].lower() or 'constraint' in result['message'].lower())]
        
        if success_rate >= 85 and len(fk_errors) == 0:
            print("\n✅ ONBOARDING PILLAR CREATION FIX: SUCCESS")
            print("   ✅ Pillar creation working without FK constraint errors")
            print("   ✅ Area creation working without FK constraint errors")
            print("   ✅ Project creation working without FK constraint errors")
            print("   ✅ Task creation working without FK constraint errors")
            print("   ✅ Complete onboarding flow functional")
            print("   ✅ Foreign key constraint violations resolved")
            print("   The onboarding pillar creation fix is working correctly!")
        elif len(fk_errors) > 0:
            print("\n❌ ONBOARDING PILLAR CREATION FIX: FOREIGN KEY ERRORS STILL EXIST")
            print("   ❌ Foreign key constraint violations are still occurring")
            print("   🔧 The fix may not be working properly or needs adjustment")
            for error in fk_errors:
                print(f"   ❌ {error['test']}: {error['message']}")
        else:
            print("\n⚠️ ONBOARDING PILLAR CREATION FIX: PARTIAL SUCCESS")
            print("   ⚠️ Some tests failed but no FK constraint errors detected")
            print("   🔧 May need investigation of other issues")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 85 and len(fk_errors) == 0

def main():
    """Run Onboarding Pillar Creation Fix Tests"""
    print("🔧 STARTING ONBOARDING PILLAR CREATION FIX BACKEND TESTING")
    print("=" * 80)
    
    tester = OnboardingPillarFixTester()
    
    try:
        # Run the comprehensive onboarding fix tests
        success = tester.run_comprehensive_onboarding_fix_test()
        
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