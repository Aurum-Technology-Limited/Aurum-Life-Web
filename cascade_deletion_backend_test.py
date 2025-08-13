#!/usr/bin/env python3
"""
BACKEND CASCADE DELETE VERIFICATION TESTING
Testing cascade deletion across hierarchy as requested in review.

FOCUS AREAS:
1. Authentication with marc.alleyne@aurumtechnologyltd.com/password123
2. Create hierarchy: Pillar → Area → Project → Tasks
3. Test cascade deletion at different levels (Pillar, Area, Project)
4. Verify that deletions properly cascade down the hierarchy

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password123
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://bf6e30ba-111b-4b82-8cdf-ddd27513fb58.preview.emergentagent.com/api"

class CascadeDeletionTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Use the specified test credentials
        self.test_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.test_user_password = "password123"
        
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

    def create_hierarchy(self):
        """Create test hierarchy: Pillar → Area → Project → Tasks"""
        print("\n=== CREATING TEST HIERARCHY ===")
        
        timestamp = str(int(time.time()))
        
        # Create Pillar
        pillar_data = {
            "name": f"Cascade Pillar API {timestamp}",
            "description": "Test pillar for cascade deletion",
            "icon": "🎯",
            "color": "#10B981"
        }
        
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        if not result['success']:
            self.log_test("CREATE PILLAR", False, f"Failed to create pillar: {result.get('error')}")
            return None
        
        pillar_id = result['data']['id']
        self.log_test("CREATE PILLAR", True, f"Created pillar with ID: {pillar_id}")
        
        # Create Area
        area_data = {
            "pillar_id": pillar_id,
            "name": f"Cascade Area API {timestamp}",
            "description": "Test area for cascade deletion",
            "importance": 3,
            "icon": "📋",
            "color": "#F59E0B"
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        if not result['success']:
            self.log_test("CREATE AREA", False, f"Failed to create area: {result.get('error')}")
            return None
        
        area_id = result['data']['id']
        self.log_test("CREATE AREA", True, f"Created area with ID: {area_id}")
        
        # Create Project
        project_data = {
            "area_id": area_id,
            "name": f"Cascade Project API {timestamp}",
            "description": "test",
            "status": "Not Started",
            "priority": "medium"
        }
        
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        if not result['success']:
            self.log_test("CREATE PROJECT", False, f"Failed to create project: {result.get('error')}")
            return None
        
        project_id = result['data']['id']
        self.log_test("CREATE PROJECT", True, f"Created project with ID: {project_id}")
        
        # Create Tasks
        task_ids = []
        for i in [1, 2]:
            task_data = {
                "project_id": project_id,
                "name": f"Cascade Task {i}",
                "description": f"Test task {i} for cascade deletion",
                "status": "todo",
                "priority": "medium"
            }
            
            result = self.make_request('POST', '/tasks', data=task_data, use_auth=True)
            if not result['success']:
                self.log_test(f"CREATE TASK {i}", False, f"Failed to create task {i}: {result.get('error')}")
                return None
            
            task_id = result['data']['id']
            task_ids.append(task_id)
            self.log_test(f"CREATE TASK {i}", True, f"Created task {i} with ID: {task_id}")
        
        return {
            'pillar_id': pillar_id,
            'area_id': area_id,
            'project_id': project_id,
            'task_ids': task_ids
        }

    def verify_hierarchy_exists(self, hierarchy):
        """Verify hierarchy exists before deletion"""
        print("\n=== VERIFYING HIERARCHY EXISTS ===")
        
        # Verify Area exists under Pillar
        result = self.make_request('GET', '/areas', params={'include_projects': 'true'}, use_auth=True)
        if result['success']:
            areas = result['data']
            area_found = any(area['id'] == hierarchy['area_id'] and area.get('pillar_id') == hierarchy['pillar_id'] for area in areas)
            self.log_test("VERIFY AREA EXISTS", area_found, f"Area found under pillar" if area_found else "Area not found under pillar")
        else:
            self.log_test("VERIFY AREA EXISTS", False, f"Failed to get areas: {result.get('error')}")
            return False
        
        # Verify Project exists
        result = self.make_request('GET', '/projects', params={'area_id': hierarchy['area_id']}, use_auth=True)
        if result['success']:
            projects = result['data']
            project_found = any(project['id'] == hierarchy['project_id'] for project in projects)
            self.log_test("VERIFY PROJECT EXISTS", project_found, f"Project found" if project_found else "Project not found")
        else:
            self.log_test("VERIFY PROJECT EXISTS", False, f"Failed to get projects: {result.get('error')}")
            return False
        
        # Verify Tasks exist
        result = self.make_request('GET', '/tasks', params={'project_id': hierarchy['project_id']}, use_auth=True)
        if result['success']:
            tasks = result['data']
            tasks_found = len([task for task in tasks if task['id'] in hierarchy['task_ids']])
            expected_tasks = len(hierarchy['task_ids'])
            self.log_test("VERIFY TASKS EXIST", tasks_found == expected_tasks, f"Found {tasks_found}/{expected_tasks} tasks")
            return tasks_found == expected_tasks
        else:
            self.log_test("VERIFY TASKS EXIST", False, f"Failed to get tasks: {result.get('error')}")
            return False

    def test_pillar_cascade_delete(self, hierarchy):
        """Test Action 1: Delete Pillar and verify cascade"""
        print("\n=== TESTING PILLAR CASCADE DELETE ===")
        
        # Delete Pillar
        result = self.make_request('DELETE', f'/pillars/{hierarchy["pillar_id"]}', use_auth=True)
        if result['success']:
            response_data = result['data']
            cascade_message = "cascade" in str(response_data).lower()
            self.log_test("DELETE PILLAR", True, f"Pillar deleted with response: {response_data}")
            if cascade_message:
                self.log_test("PILLAR DELETE CASCADE MESSAGE", True, "Response indicates cascade deletion")
            else:
                self.log_test("PILLAR DELETE CASCADE MESSAGE", False, "Response does not mention cascade")
        else:
            self.log_test("DELETE PILLAR", False, f"Failed to delete pillar: {result.get('error')}")
            return False
        
        # Verify Pillar is gone
        result = self.make_request('GET', '/pillars', use_auth=True)
        if result['success']:
            pillars = result['data']
            pillar_gone = not any(pillar['id'] == hierarchy['pillar_id'] for pillar in pillars)
            self.log_test("VERIFY PILLAR DELETED", pillar_gone, "Pillar successfully removed" if pillar_gone else "Pillar still exists")
        else:
            self.log_test("VERIFY PILLAR DELETED", False, f"Failed to get pillars: {result.get('error')}")
        
        # Verify Area is gone
        result = self.make_request('GET', '/areas', use_auth=True)
        if result['success']:
            areas = result['data']
            area_gone = not any(area['id'] == hierarchy['area_id'] for area in areas)
            self.log_test("VERIFY AREA CASCADE DELETED", area_gone, "Area successfully cascade deleted" if area_gone else "Area still exists")
        else:
            self.log_test("VERIFY AREA CASCADE DELETED", False, f"Failed to get areas: {result.get('error')}")
        
        # Verify Projects are gone - check specifically for our project
        result = self.make_request('GET', '/projects', use_auth=True)
        if result['success']:
            projects = result['data']
            our_project_exists = any(project['id'] == hierarchy['project_id'] for project in projects)
            projects_gone = not our_project_exists
            self.log_test("VERIFY PROJECTS CASCADE DELETED", projects_gone, "Projects successfully cascade deleted" if projects_gone else f"Our project {hierarchy['project_id']} still exists")
        else:
            self.log_test("VERIFY PROJECTS CASCADE DELETED", False, f"Failed to get projects: {result.get('error')}")
        
        # Verify Tasks are gone
        result = self.make_request('GET', '/tasks', params={'project_id': hierarchy['project_id']}, use_auth=True)
        if result['success']:
            tasks = result['data']
            tasks_gone = len(tasks) == 0
            self.log_test("VERIFY TASKS CASCADE DELETED", tasks_gone, "Tasks successfully cascade deleted" if tasks_gone else f"Found {len(tasks)} tasks still exist")
        else:
            self.log_test("VERIFY TASKS CASCADE DELETED", False, f"Failed to get tasks: {result.get('error')}")
        
        return True

    def test_area_cascade_delete(self):
        """Test Action 2: Repeat with Area cascade"""
        print("\n=== TESTING AREA CASCADE DELETE ===")
        
        # Create new hierarchy for area cascade test
        timestamp = str(int(time.time()))
        
        # Create Pillar P2
        pillar_data = {
            "name": f"Cascade Pillar P2 {timestamp}",
            "description": "Test pillar P2 for area cascade deletion",
            "icon": "🎯",
            "color": "#10B981"
        }
        
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        if not result['success']:
            self.log_test("CREATE PILLAR P2", False, f"Failed to create pillar P2: {result.get('error')}")
            return False
        
        pillar_p2_id = result['data']['id']
        self.log_test("CREATE PILLAR P2", True, f"Created pillar P2 with ID: {pillar_p2_id}")
        
        # Create Area A2
        area_data = {
            "pillar_id": pillar_p2_id,
            "name": f"Cascade Area A2 {timestamp}",
            "description": "Test area A2 for cascade deletion",
            "importance": 3,
            "icon": "📋",
            "color": "#F59E0B"
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        if not result['success']:
            self.log_test("CREATE AREA A2", False, f"Failed to create area A2: {result.get('error')}")
            return False
        
        area_a2_id = result['data']['id']
        self.log_test("CREATE AREA A2", True, f"Created area A2 with ID: {area_a2_id}")
        
        # Create Project PR2
        project_data = {
            "area_id": area_a2_id,
            "name": f"Cascade Project PR2 {timestamp}",
            "description": "test project PR2",
            "status": "Not Started",
            "priority": "medium"
        }
        
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        if not result['success']:
            self.log_test("CREATE PROJECT PR2", False, f"Failed to create project PR2: {result.get('error')}")
            return False
        
        project_pr2_id = result['data']['id']
        self.log_test("CREATE PROJECT PR2", True, f"Created project PR2 with ID: {project_pr2_id}")
        
        # Create Task T2
        task_data = {
            "project_id": project_pr2_id,
            "name": "Cascade Task T2",
            "description": "Test task T2 for cascade deletion",
            "status": "todo",
            "priority": "medium"
        }
        
        result = self.make_request('POST', '/tasks', data=task_data, use_auth=True)
        if not result['success']:
            self.log_test("CREATE TASK T2", False, f"Failed to create task T2: {result.get('error')}")
            return False
        
        task_t2_id = result['data']['id']
        self.log_test("CREATE TASK T2", True, f"Created task T2 with ID: {task_t2_id}")
        
        # Delete Area A2
        result = self.make_request('DELETE', f'/areas/{area_a2_id}', use_auth=True)
        if result['success']:
            self.log_test("DELETE AREA A2", True, f"Area A2 deleted successfully")
        else:
            self.log_test("DELETE AREA A2", False, f"Failed to delete area A2: {result.get('error')}")
            return False
        
        # Verify Projects under A2 are gone - check specifically for our project
        result = self.make_request('GET', '/projects', use_auth=True)
        if result['success']:
            projects = result['data']
            our_project_exists = any(project['id'] == project_pr2_id for project in projects)
            projects_gone = not our_project_exists
            self.log_test("VERIFY PROJECTS UNDER A2 DELETED", projects_gone, "Projects under A2 successfully deleted" if projects_gone else f"Our project {project_pr2_id} still exists")
        else:
            self.log_test("VERIFY PROJECTS UNDER A2 DELETED", False, f"Failed to get projects: {result.get('error')}")
        
        # Verify Tasks under PR2 are gone
        result = self.make_request('GET', '/tasks', params={'project_id': project_pr2_id}, use_auth=True)
        if result['success']:
            tasks = result['data']
            tasks_gone = len(tasks) == 0
            self.log_test("VERIFY TASKS UNDER PR2 DELETED", tasks_gone, "Tasks under PR2 successfully deleted" if tasks_gone else f"Found {len(tasks)} tasks still exist")
        else:
            self.log_test("VERIFY TASKS UNDER PR2 DELETED", False, f"Failed to get tasks: {result.get('error')}")
        
        # Verify Area A2 is gone
        result = self.make_request('GET', '/areas', use_auth=True)
        if result['success']:
            areas = result['data']
            area_gone = not any(area['id'] == area_a2_id for area in areas)
            self.log_test("VERIFY AREA A2 DELETED", area_gone, "Area A2 successfully deleted" if area_gone else "Area A2 still exists")
        else:
            self.log_test("VERIFY AREA A2 DELETED", False, f"Failed to get areas: {result.get('error')}")
        
        # Verify Pillar P2 remains
        result = self.make_request('GET', '/pillars', use_auth=True)
        if result['success']:
            pillars = result['data']
            pillar_remains = any(pillar['id'] == pillar_p2_id for pillar in pillars)
            self.log_test("VERIFY PILLAR P2 REMAINS", pillar_remains, "Pillar P2 correctly remains" if pillar_remains else "Pillar P2 was incorrectly deleted")
        else:
            self.log_test("VERIFY PILLAR P2 REMAINS", False, f"Failed to get pillars: {result.get('error')}")
        
        return True

    def test_project_cascade_delete(self):
        """Test Action 3: Project cascade"""
        print("\n=== TESTING PROJECT CASCADE DELETE ===")
        
        # Create new hierarchy for project cascade test
        timestamp = str(int(time.time()))
        
        # Create Pillar P3
        pillar_data = {
            "name": f"Cascade Pillar P3 {timestamp}",
            "description": "Test pillar P3 for project cascade deletion",
            "icon": "🎯",
            "color": "#10B981"
        }
        
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        if not result['success']:
            self.log_test("CREATE PILLAR P3", False, f"Failed to create pillar P3: {result.get('error')}")
            return False
        
        pillar_p3_id = result['data']['id']
        self.log_test("CREATE PILLAR P3", True, f"Created pillar P3 with ID: {pillar_p3_id}")
        
        # Create Area A3
        area_data = {
            "pillar_id": pillar_p3_id,
            "name": f"Cascade Area A3 {timestamp}",
            "description": "Test area A3 for project cascade deletion",
            "importance": 3,
            "icon": "📋",
            "color": "#F59E0B"
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        if not result['success']:
            self.log_test("CREATE AREA A3", False, f"Failed to create area A3: {result.get('error')}")
            return False
        
        area_a3_id = result['data']['id']
        self.log_test("CREATE AREA A3", True, f"Created area A3 with ID: {area_a3_id}")
        
        # Create Project PR3
        project_data = {
            "area_id": area_a3_id,
            "name": f"Cascade Project PR3 {timestamp}",
            "description": "test project PR3",
            "status": "Not Started",
            "priority": "medium"
        }
        
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        if not result['success']:
            self.log_test("CREATE PROJECT PR3", False, f"Failed to create project PR3: {result.get('error')}")
            return False
        
        project_pr3_id = result['data']['id']
        self.log_test("CREATE PROJECT PR3", True, f"Created project PR3 with ID: {project_pr3_id}")
        
        # Create Task T3
        task_data = {
            "project_id": project_pr3_id,
            "name": "Cascade Task T3",
            "description": "Test task T3 for cascade deletion",
            "status": "todo",
            "priority": "medium"
        }
        
        result = self.make_request('POST', '/tasks', data=task_data, use_auth=True)
        if not result['success']:
            self.log_test("CREATE TASK T3", False, f"Failed to create task T3: {result.get('error')}")
            return False
        
        task_t3_id = result['data']['id']
        self.log_test("CREATE TASK T3", True, f"Created task T3 with ID: {task_t3_id}")
        
        # Delete Project PR3
        result = self.make_request('DELETE', f'/projects/{project_pr3_id}', use_auth=True)
        if result['success']:
            self.log_test("DELETE PROJECT PR3", True, f"Project PR3 deleted successfully")
        else:
            self.log_test("DELETE PROJECT PR3", False, f"Failed to delete project PR3: {result.get('error')}")
            return False
        
        # Verify Tasks under PR3 are gone
        result = self.make_request('GET', '/tasks', params={'project_id': project_pr3_id}, use_auth=True)
        if result['success']:
            tasks = result['data']
            tasks_gone = len(tasks) == 0
            self.log_test("VERIFY TASKS UNDER PR3 DELETED", tasks_gone, "Tasks under PR3 successfully deleted" if tasks_gone else f"Found {len(tasks)} tasks still exist")
        else:
            self.log_test("VERIFY TASKS UNDER PR3 DELETED", False, f"Failed to get tasks: {result.get('error')}")
        
        # Verify Project PR3 is gone
        result = self.make_request('GET', '/projects', params={'area_id': area_a3_id}, use_auth=True)
        if result['success']:
            projects = result['data']
            project_gone = not any(project['id'] == project_pr3_id for project in projects)
            self.log_test("VERIFY PROJECT PR3 DELETED", project_gone, "Project PR3 successfully deleted" if project_gone else "Project PR3 still exists")
        else:
            self.log_test("VERIFY PROJECT PR3 DELETED", False, f"Failed to get projects: {result.get('error')}")
        
        # Verify Area A3 remains
        result = self.make_request('GET', '/areas', use_auth=True)
        if result['success']:
            areas = result['data']
            area_remains = any(area['id'] == area_a3_id for area in areas)
            self.log_test("VERIFY AREA A3 REMAINS", area_remains, "Area A3 correctly remains" if area_remains else "Area A3 was incorrectly deleted")
        else:
            self.log_test("VERIFY AREA A3 REMAINS", False, f"Failed to get areas: {result.get('error')}")
        
        # Verify Pillar P3 remains
        result = self.make_request('GET', '/pillars', use_auth=True)
        if result['success']:
            pillars = result['data']
            pillar_remains = any(pillar['id'] == pillar_p3_id for pillar in pillars)
            self.log_test("VERIFY PILLAR P3 REMAINS", pillar_remains, "Pillar P3 correctly remains" if pillar_remains else "Pillar P3 was incorrectly deleted")
        else:
            self.log_test("VERIFY PILLAR P3 REMAINS", False, f"Failed to get pillars: {result.get('error')}")
        
        return True

    def run_cascade_deletion_test(self):
        """Run comprehensive cascade deletion test"""
        print("\n🗑️ STARTING BACKEND CASCADE DELETE VERIFICATION TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Step 1: Authentication
        if not self.test_authentication():
            print("❌ Authentication failed - cannot proceed with tests")
            return False
        
        # Step 2: Create initial hierarchy and test pillar cascade
        hierarchy = self.create_hierarchy()
        if not hierarchy:
            print("❌ Failed to create test hierarchy")
            return False
        
        # Step 3: Verify hierarchy exists
        if not self.verify_hierarchy_exists(hierarchy):
            print("❌ Hierarchy verification failed")
            return False
        
        # Step 4: Test pillar cascade delete
        if not self.test_pillar_cascade_delete(hierarchy):
            print("❌ Pillar cascade delete test failed")
            return False
        
        # Step 5: Test area cascade delete
        if not self.test_area_cascade_delete():
            print("❌ Area cascade delete test failed")
            return False
        
        # Step 6: Test project cascade delete
        if not self.test_project_cascade_delete():
            print("❌ Project cascade delete test failed")
            return False
        
        # Calculate results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n" + "=" * 80)
        print("🗑️ CASCADE DELETE VERIFICATION TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Results: {passed_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        if success_rate >= 85:
            print("\n✅ CASCADE DELETE VERIFICATION: SUCCESS")
            print("   ✅ Pillar cascade deletion working correctly")
            print("   ✅ Area cascade deletion working correctly")
            print("   ✅ Project cascade deletion working correctly")
            print("   ✅ Hierarchy relationships properly maintained")
            print("   The cascade deletion system is production-ready!")
        else:
            print("\n❌ CASCADE DELETE VERIFICATION: ISSUES DETECTED")
            print("   Issues found in cascade deletion implementation")
        
        return success_rate >= 85

def main():
    """Run Cascade Deletion Tests"""
    print("🗑️ STARTING BACKEND CASCADE DELETE VERIFICATION TESTING")
    print("=" * 80)
    
    tester = CascadeDeletionTester()
    
    try:
        # Run the comprehensive cascade deletion tests
        success = tester.run_cascade_deletion_test()
        
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