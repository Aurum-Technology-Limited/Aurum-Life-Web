#!/usr/bin/env python3
"""
Onboarding Template Creation Backend Test
Testing Focus: Complete onboarding flow with template data creation

This test verifies:
1. API endpoints for creating hierarchy data (pillars, areas, projects, tasks)
2. Testing with sample onboarding template data
3. Complete-onboarding endpoint functionality
4. User profile onboarding status tracking
5. Foreign key relationships and database constraints
6. Authentication and data isolation
"""

import requests
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

class OnboardingTemplateTester:
    def __init__(self, base_url="https://smart-life-os.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Test credentials - using the test account from review request
        self.test_email = "test@aurumlife.com"
        self.test_password = "password123"
        
        # Created entity IDs for cleanup and relationship testing
        self.created_pillar_id = None
        self.created_area_id = None
        self.created_project_id = None
        self.created_task_ids = []

    def log_test(self, name: str, success: bool, details: Dict = None, response_time: float = None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            
        result = {
            'test_name': name,
            'success': success,
            'details': details or {},
            'response_time': response_time,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        time_info = f" ({response_time:.2f}s)" if response_time else ""
        print(f"{status} {name}{time_info}")
        
        if details and not success:
            print(f"   Details: {details}")

    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> tuple:
        """Make HTTP request and return (success, response_data, response_time)"""
        url = f"{self.base_url}/api/{endpoint.lstrip('/')}"
        headers = {'Content-Type': 'application/json'}
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        start_time = time.time()
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=headers, params=params, timeout=30)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, params=params, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            response_time = time.time() - start_time
            
            if response.status_code < 400:
                return True, response.json(), response_time
            else:
                return False, {
                    'status_code': response.status_code,
                    'error': response.text
                }, response_time
                
        except Exception as e:
            response_time = time.time() - start_time
            return False, {'error': str(e)}, response_time

    def test_authentication(self) -> bool:
        """Test login and get authentication token"""
        print("\n🔐 Testing Authentication...")
        
        success, response, response_time = self.make_request(
            'POST', 
            'auth/login',
            data={
                'email': self.test_email,
                'password': self.test_password
            }
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response.get('user', {}).get('id')
            user_data = response.get('user', {})
            
            details = {
                'user_id': self.user_id,
                'has_completed_onboarding': user_data.get('has_completed_onboarding', False),
                'user_level': user_data.get('level', 'unknown')
            }
            
            self.log_test("Authentication", True, details, response_time)
            return True
        else:
            self.log_test("Authentication", False, response, response_time)
            return False

    def test_create_pillar(self) -> bool:
        """Test creating a pillar via POST /api/pillars"""
        print("\n🏛️ Testing Pillar Creation...")
        
        pillar_data = {
            "name": "Test Pillar",
            "description": "A test pillar for onboarding template testing",
            "icon": "🎯",
            "color": "#3B82F6"
        }
        
        success, response, response_time = self.make_request(
            'POST',
            'pillars',
            data=pillar_data
        )
        
        if success and 'id' in response:
            self.created_pillar_id = response['id']
            
            details = {
                'pillar_id': self.created_pillar_id,
                'pillar_name': response.get('name'),
                'user_id_match': response.get('user_id') == self.user_id
            }
            
            self.log_test("Create Pillar", True, details, response_time)
            return True
        else:
            self.log_test("Create Pillar", False, response, response_time)
            return False

    def test_create_area(self) -> bool:
        """Test creating an area via POST /api/areas"""
        print("\n🎯 Testing Area Creation...")
        
        if not self.created_pillar_id:
            self.log_test("Create Area", False, {'error': 'No pillar_id available'})
            return False
        
        area_data = {
            "pillar_id": self.created_pillar_id,
            "name": "Test Area",
            "description": "A test area for onboarding template testing",
            "icon": "📊",
            "color": "#10B981"
        }
        
        success, response, response_time = self.make_request(
            'POST',
            'areas',
            data=area_data
        )
        
        if success and 'id' in response:
            self.created_area_id = response['id']
            
            details = {
                'area_id': self.created_area_id,
                'area_name': response.get('name'),
                'pillar_id_match': response.get('pillar_id') == self.created_pillar_id,
                'user_id_match': response.get('user_id') == self.user_id
            }
            
            self.log_test("Create Area", True, details, response_time)
            return True
        else:
            self.log_test("Create Area", False, response, response_time)
            return False

    def test_create_project(self) -> bool:
        """Test creating a project via POST /api/projects"""
        print("\n🚀 Testing Project Creation...")
        
        if not self.created_area_id:
            self.log_test("Create Project", False, {'error': 'No area_id available'})
            return False
        
        project_data = {
            "area_id": self.created_area_id,
            "name": "Test Project",
            "description": "A test project for onboarding template testing",
            "icon": "💼",
            "priority": "medium",
            "status": "not_started"
        }
        
        success, response, response_time = self.make_request(
            'POST',
            'projects',
            data=project_data
        )
        
        if success and 'id' in response:
            self.created_project_id = response['id']
            
            details = {
                'project_id': self.created_project_id,
                'project_name': response.get('name'),
                'area_id_match': response.get('area_id') == self.created_area_id,
                'user_id_match': response.get('user_id') == self.user_id
            }
            
            self.log_test("Create Project", True, details, response_time)
            return True
        else:
            self.log_test("Create Project", False, response, response_time)
            return False

    def test_create_tasks(self) -> bool:
        """Test creating tasks via POST /api/tasks"""
        print("\n✅ Testing Task Creation...")
        
        if not self.created_project_id:
            self.log_test("Create Tasks", False, {'error': 'No project_id available'})
            return False
        
        # Create multiple tasks to test the hierarchy
        tasks_data = [
            {
                "project_id": self.created_project_id,
                "name": "Test Task 1",
                "description": "First test task for onboarding template",
                "priority": "high",
                "status": "todo"
            },
            {
                "project_id": self.created_project_id,
                "name": "Test Task 2", 
                "description": "Second test task for onboarding template",
                "priority": "medium",
                "status": "todo"
            },
            {
                "project_id": self.created_project_id,
                "name": "Test Task 3",
                "description": "Third test task for onboarding template",
                "priority": "low",
                "status": "todo"
            }
        ]
        
        created_tasks = []
        all_success = True
        total_time = 0
        
        for i, task_data in enumerate(tasks_data):
            success, response, response_time = self.make_request(
                'POST',
                'tasks',
                data=task_data
            )
            
            total_time += response_time
            
            if success and 'id' in response:
                task_id = response['id']
                self.created_task_ids.append(task_id)
                created_tasks.append({
                    'task_id': task_id,
                    'task_name': response.get('name'),
                    'project_id_match': response.get('project_id') == self.created_project_id,
                    'user_id_match': response.get('user_id') == self.user_id
                })
            else:
                all_success = False
                print(f"   Failed to create task {i+1}: {response}")
        
        details = {
            'tasks_created': len(created_tasks),
            'tasks_requested': len(tasks_data),
            'created_tasks': created_tasks
        }
        
        self.log_test("Create Tasks", all_success, details, total_time)
        return all_success

    def test_complete_onboarding(self) -> bool:
        """Test the complete-onboarding endpoint"""
        print("\n🎉 Testing Complete Onboarding...")
        
        success, response, response_time = self.make_request(
            'POST',
            'auth/complete-onboarding'
        )
        
        if success:
            details = {
                'message': response.get('message'),
                'has_completed_onboarding': response.get('has_completed_onboarding'),
                'success': response.get('success')
            }
            
            self.log_test("Complete Onboarding", True, details, response_time)
            return True
        else:
            self.log_test("Complete Onboarding", False, response, response_time)
            return False

    def test_user_onboarding_status(self) -> bool:
        """Test that user profile shows correct onboarding status"""
        print("\n👤 Testing User Onboarding Status...")
        
        success, response, response_time = self.make_request(
            'GET',
            'auth/me'
        )
        
        if success:
            user_data = response
            has_completed_onboarding = user_data.get('has_completed_onboarding', False)
            user_level = user_data.get('level', 1)
            
            details = {
                'user_id': user_data.get('id'),
                'has_completed_onboarding': has_completed_onboarding,
                'user_level': user_level,
                'expected_onboarding_complete': True,
                'status_correct': has_completed_onboarding == True
            }
            
            # Test passes if onboarding status is correctly updated
            test_passed = has_completed_onboarding == True
            
            self.log_test("User Onboarding Status", test_passed, details, response_time)
            return test_passed
        else:
            self.log_test("User Onboarding Status", False, response, response_time)
            return False

    def test_hierarchy_relationships(self) -> bool:
        """Test that created hierarchy has proper foreign key relationships"""
        print("\n🔗 Testing Hierarchy Relationships...")
        
        all_tests_passed = True
        total_time = 0
        
        # Test 1: Verify pillar exists and has areas
        success, pillars_response, response_time = self.make_request(
            'GET',
            'pillars'
        )
        total_time += response_time
        
        pillar_found = False
        if success and isinstance(pillars_response, list):
            for pillar in pillars_response:
                if pillar.get('id') == self.created_pillar_id:
                    pillar_found = True
                    break
        
        if not pillar_found:
            all_tests_passed = False
            print(f"   ❌ Created pillar {self.created_pillar_id} not found in pillars list")
        
        # Test 2: Verify area exists and links to pillar
        success, areas_response, response_time = self.make_request(
            'GET',
            'areas'
        )
        total_time += response_time
        
        area_found = False
        area_pillar_link_correct = False
        if success and isinstance(areas_response, list):
            for area in areas_response:
                if area.get('id') == self.created_area_id:
                    area_found = True
                    area_pillar_link_correct = area.get('pillar_id') == self.created_pillar_id
                    break
        
        if not area_found:
            all_tests_passed = False
            print(f"   ❌ Created area {self.created_area_id} not found in areas list")
        elif not area_pillar_link_correct:
            all_tests_passed = False
            print(f"   ❌ Area pillar_id does not match created pillar")
        
        # Test 3: Verify project exists and links to area
        success, projects_response, response_time = self.make_request(
            'GET',
            'projects'
        )
        total_time += response_time
        
        project_found = False
        project_area_link_correct = False
        if success and isinstance(projects_response, list):
            for project in projects_response:
                if project.get('id') == self.created_project_id:
                    project_found = True
                    project_area_link_correct = project.get('area_id') == self.created_area_id
                    break
        
        if not project_found:
            all_tests_passed = False
            print(f"   ❌ Created project {self.created_project_id} not found in projects list")
        elif not project_area_link_correct:
            all_tests_passed = False
            print(f"   ❌ Project area_id does not match created area")
        
        # Test 4: Verify tasks exist and link to project
        success, tasks_response, response_time = self.make_request(
            'GET',
            'tasks'
        )
        total_time += response_time
        
        tasks_found = 0
        tasks_project_links_correct = 0
        if success and isinstance(tasks_response, list):
            for task in tasks_response:
                if task.get('id') in self.created_task_ids:
                    tasks_found += 1
                    if task.get('project_id') == self.created_project_id:
                        tasks_project_links_correct += 1
        
        if tasks_found != len(self.created_task_ids):
            all_tests_passed = False
            print(f"   ❌ Only {tasks_found}/{len(self.created_task_ids)} created tasks found")
        elif tasks_project_links_correct != len(self.created_task_ids):
            all_tests_passed = False
            print(f"   ❌ Only {tasks_project_links_correct}/{len(self.created_task_ids)} tasks have correct project_id")
        
        details = {
            'pillar_found': pillar_found,
            'area_found': area_found,
            'area_pillar_link_correct': area_pillar_link_correct,
            'project_found': project_found,
            'project_area_link_correct': project_area_link_correct,
            'tasks_found': tasks_found,
            'tasks_expected': len(self.created_task_ids),
            'tasks_project_links_correct': tasks_project_links_correct
        }
        
        self.log_test("Hierarchy Relationships", all_tests_passed, details, total_time)
        return all_tests_passed

    def test_data_isolation(self) -> bool:
        """Test that created data is properly isolated to the authenticated user"""
        print("\n🔒 Testing Data Isolation...")
        
        all_tests_passed = True
        total_time = 0
        
        # Get all user's data and verify it belongs to the correct user
        endpoints_to_test = [
            ('pillars', self.created_pillar_id),
            ('areas', self.created_area_id),
            ('projects', self.created_project_id),
            ('tasks', self.created_task_ids[0] if self.created_task_ids else None)
        ]
        
        isolation_results = {}
        
        for endpoint, entity_id in endpoints_to_test:
            if not entity_id:
                continue
                
            success, response, response_time = self.make_request('GET', endpoint)
            total_time += response_time
            
            if success and isinstance(response, list):
                user_data_correct = True
                entity_found = False
                
                for item in response:
                    if item.get('id') == entity_id:
                        entity_found = True
                        if item.get('user_id') != self.user_id:
                            user_data_correct = False
                            all_tests_passed = False
                            print(f"   ❌ {endpoint} entity {entity_id} has wrong user_id: {item.get('user_id')} != {self.user_id}")
                        break
                
                if not entity_found:
                    all_tests_passed = False
                    print(f"   ❌ {endpoint} entity {entity_id} not found in user's data")
                
                isolation_results[endpoint] = {
                    'entity_found': entity_found,
                    'user_id_correct': user_data_correct
                }
        
        details = {
            'user_id': self.user_id,
            'isolation_results': isolation_results
        }
        
        self.log_test("Data Isolation", all_tests_passed, details, total_time)
        return all_tests_passed

    def test_constraint_violations(self) -> bool:
        """Test for common constraint violations and error handling"""
        print("\n⚠️ Testing Constraint Violations...")
        
        constraint_tests = []
        total_time = 0
        
        # Test 1: Try to create area with invalid pillar_id
        success, response, response_time = self.make_request(
            'POST',
            'areas',
            data={
                "pillar_id": "invalid-pillar-id",
                "name": "Invalid Area",
                "description": "Should fail due to invalid pillar_id"
            }
        )
        total_time += response_time
        
        constraint_tests.append({
            'test': 'Invalid pillar_id for area',
            'should_fail': True,
            'actually_failed': not success,
            'response': response
        })
        
        # Test 2: Try to create project with invalid area_id
        success, response, response_time = self.make_request(
            'POST',
            'projects',
            data={
                "area_id": "invalid-area-id",
                "name": "Invalid Project",
                "description": "Should fail due to invalid area_id"
            }
        )
        total_time += response_time
        
        constraint_tests.append({
            'test': 'Invalid area_id for project',
            'should_fail': True,
            'actually_failed': not success,
            'response': response
        })
        
        # Test 3: Try to create task with invalid project_id
        success, response, response_time = self.make_request(
            'POST',
            'tasks',
            data={
                "project_id": "invalid-project-id",
                "name": "Invalid Task",
                "description": "Should fail due to invalid project_id"
            }
        )
        total_time += response_time
        
        constraint_tests.append({
            'test': 'Invalid project_id for task',
            'should_fail': True,
            'actually_failed': not success,
            'response': response
        })
        
        # Evaluate results
        all_constraints_working = True
        for test in constraint_tests:
            if test['should_fail'] and not test['actually_failed']:
                all_constraints_working = False
                print(f"   ❌ {test['test']} should have failed but succeeded")
        
        details = {
            'constraint_tests': constraint_tests,
            'all_constraints_working': all_constraints_working
        }
        
        self.log_test("Constraint Violations", all_constraints_working, details, total_time)
        return all_constraints_working

    def cleanup_test_data(self) -> bool:
        """Clean up created test data"""
        print("\n🧹 Cleaning Up Test Data...")
        
        cleanup_success = True
        total_time = 0
        
        # Note: In a real application, we might want to delete in reverse order
        # due to foreign key constraints, but for this test we'll just attempt cleanup
        
        # Clean up tasks
        for task_id in self.created_task_ids:
            success, response, response_time = self.make_request('DELETE', f'tasks/{task_id}')
            total_time += response_time
            if not success:
                cleanup_success = False
                print(f"   ⚠️ Failed to delete task {task_id}")
        
        # Clean up project
        if self.created_project_id:
            success, response, response_time = self.make_request('DELETE', f'projects/{self.created_project_id}')
            total_time += response_time
            if not success:
                cleanup_success = False
                print(f"   ⚠️ Failed to delete project {self.created_project_id}")
        
        # Clean up area
        if self.created_area_id:
            success, response, response_time = self.make_request('DELETE', f'areas/{self.created_area_id}')
            total_time += response_time
            if not success:
                cleanup_success = False
                print(f"   ⚠️ Failed to delete area {self.created_area_id}")
        
        # Clean up pillar
        if self.created_pillar_id:
            success, response, response_time = self.make_request('DELETE', f'pillars/{self.created_pillar_id}')
            total_time += response_time
            if not success:
                cleanup_success = False
                print(f"   ⚠️ Failed to delete pillar {self.created_pillar_id}")
        
        details = {
            'tasks_cleaned': len(self.created_task_ids),
            'project_cleaned': bool(self.created_project_id),
            'area_cleaned': bool(self.created_area_id),
            'pillar_cleaned': bool(self.created_pillar_id),
            'cleanup_success': cleanup_success
        }
        
        self.log_test("Cleanup Test Data", cleanup_success, details, total_time)
        return cleanup_success

    def run_comprehensive_test(self):
        """Run all onboarding template creation tests"""
        print("🚀 Starting Onboarding Template Creation Backend Test")
        print("=" * 60)
        
        # Authentication is required for all other tests
        if not self.test_authentication():
            print("\n❌ Authentication failed. Cannot proceed with other tests.")
            return False
        
        # Run all tests in sequence (order matters for hierarchy creation)
        test_methods = [
            self.test_create_pillar,
            self.test_create_area,
            self.test_create_project,
            self.test_create_tasks,
            self.test_complete_onboarding,
            self.test_user_onboarding_status,
            self.test_hierarchy_relationships,
            self.test_data_isolation,
            self.test_constraint_violations,
            self.cleanup_test_data
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"❌ Test {test_method.__name__} failed with exception: {e}")
                self.log_test(test_method.__name__, False, {'exception': str(e)})
        
        # Print summary
        self.print_summary()
        
        return self.tests_passed == self.tests_run

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 ONBOARDING TEMPLATE CREATION TEST SUMMARY")
        print("=" * 60)
        
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        # Print failed tests
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  • {test['test_name']}")
                if test['details']:
                    print(f"    {test['details']}")
        
        # Print key findings
        print(f"\n🔍 KEY FINDINGS:")
        
        # Check if hierarchy creation worked
        hierarchy_tests = [r for r in self.test_results if r['test_name'] in ['Create Pillar', 'Create Area', 'Create Project', 'Create Tasks']]
        hierarchy_success = all(t['success'] for t in hierarchy_tests)
        print(f"  • Hierarchy Creation: {'✅ Working' if hierarchy_success else '❌ Issues Found'}")
        
        # Check if onboarding completion worked
        onboarding_tests = [r for r in self.test_results if r['test_name'] in ['Complete Onboarding', 'User Onboarding Status']]
        onboarding_success = all(t['success'] for t in onboarding_tests)
        print(f"  • Onboarding Completion: {'✅ Working' if onboarding_success else '❌ Issues Found'}")
        
        # Check if relationships are working
        relationship_test = next((r for r in self.test_results if r['test_name'] == 'Hierarchy Relationships'), None)
        relationships_working = relationship_test and relationship_test['success']
        print(f"  • Foreign Key Relationships: {'✅ Working' if relationships_working else '❌ Issues Found'}")
        
        # Check if data isolation is working
        isolation_test = next((r for r in self.test_results if r['test_name'] == 'Data Isolation'), None)
        isolation_working = isolation_test and isolation_test['success']
        print(f"  • Data Isolation: {'✅ Working' if isolation_working else '❌ Issues Found'}")
        
        # Check if constraints are working
        constraint_test = next((r for r in self.test_results if r['test_name'] == 'Constraint Violations'), None)
        constraints_working = constraint_test and constraint_test['success']
        print(f"  • Database Constraints: {'✅ Working' if constraints_working else '❌ Issues Found'}")

def main():
    """Main test execution"""
    tester = OnboardingTemplateTester()
    
    try:
        success = tester.run_comprehensive_test()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n❌ Test execution failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())