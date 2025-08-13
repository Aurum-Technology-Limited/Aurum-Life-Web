#!/usr/bin/env python3
"""
NOT NULL REGRESSION TESTING
Testing backend regression after NOT NULL updates.

FOCUS AREAS:
1. Auth: login and get token
2. POST /api/areas without pillar_id should 422; with pillar_id should 200
3. POST /api/projects without area_id should 422; with area_id should 200  
4. DELETE cascades still functional (quick create P->A->PR->T then delete P and verify no children)

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password123
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time
import uuid

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://hierarchy-enforcer.preview.emergentagent.com/api"

class NotNullRegressionTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Use the specified test credentials
        self.test_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.test_user_password = "password123"
        
    def log_test(self, test_name: str, success: bool, message: str = "", status_code: int = None, data: Any = None):
        """Log test results with status codes"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'status_code': status_code,
            'timestamp': datetime.now().isoformat()
        }
        if data:
            result['data'] = data
        self.test_results.append(result)
        
        status_icon = "✅" if success else "❌"
        status_msg = f" (HTTP {status_code})" if status_code else ""
        print(f"{status_icon} {test_name}{status_msg}: {message}")
        
    def authenticate(self) -> bool:
        """Authenticate and get JWT token"""
        try:
            print(f"\n🔐 Authenticating with {self.test_user_email}...")
            
            auth_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json=auth_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get('access_token')
                if self.auth_token:
                    self.session.headers.update({
                        'Authorization': f'Bearer {self.auth_token}'
                    })
                    self.log_test("Authentication", True, f"Successfully authenticated", response.status_code)
                    return True
                else:
                    self.log_test("Authentication", False, "No access token in response", response.status_code)
                    return False
            else:
                self.log_test("Authentication", False, f"Login failed: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Authentication error: {str(e)}")
            return False
    
    def test_areas_without_pillar_id(self) -> bool:
        """Test POST /api/areas without pillar_id should return 422"""
        try:
            print(f"\n📝 Testing Areas creation without pillar_id (should be 422)...")
            
            area_data = {
                "name": f"Test Area No Pillar {int(time.time())}",
                "description": "Test area without pillar_id",
                "importance": 3
            }
            
            response = self.session.post(
                f"{self.base_url}/areas",
                json=area_data,
                timeout=10
            )
            
            if response.status_code == 422:
                self.log_test("Areas without pillar_id", True, "Correctly returned 422 for missing pillar_id", response.status_code)
                return True
            else:
                self.log_test("Areas without pillar_id", False, f"Expected 422, got {response.status_code}: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("Areas without pillar_id", False, f"Error: {str(e)}")
            return False
    
    def test_areas_with_pillar_id(self) -> tuple[bool, str]:
        """Test POST /api/areas with pillar_id should return 200. Returns (success, area_id)"""
        try:
            print(f"\n📝 Testing Areas creation with pillar_id (should be 200)...")
            
            # First create a pillar to use
            pillar_data = {
                "name": f"Test Pillar {int(time.time())}",
                "description": "Test pillar for area creation",
                "importance": 3,
                "time_allocation": 25,
                "icon": "🎯",
                "color": "#3B82F6"
            }
            
            pillar_response = self.session.post(
                f"{self.base_url}/pillars",
                json=pillar_data,
                timeout=10
            )
            
            if pillar_response.status_code != 200:
                self.log_test("Areas with pillar_id (pillar creation)", False, f"Failed to create pillar: {pillar_response.text}", pillar_response.status_code)
                return False, None
            
            pillar_id = pillar_response.json().get('id')
            
            # Now create area with pillar_id
            area_data = {
                "name": f"Test Area With Pillar {int(time.time())}",
                "description": "Test area with pillar_id",
                "importance": 3,
                "pillar_id": pillar_id
            }
            
            response = self.session.post(
                f"{self.base_url}/areas",
                json=area_data,
                timeout=10
            )
            
            if response.status_code == 200:
                area_id = response.json().get('id')
                self.log_test("Areas with pillar_id", True, f"Successfully created area with pillar_id", response.status_code)
                return True, area_id
            else:
                self.log_test("Areas with pillar_id", False, f"Expected 200, got {response.status_code}: {response.text}", response.status_code)
                return False, None
                
        except Exception as e:
            self.log_test("Areas with pillar_id", False, f"Error: {str(e)}")
            return False, None
    
    def test_projects_without_area_id(self) -> bool:
        """Test POST /api/projects without area_id should return 422"""
        try:
            print(f"\n📝 Testing Projects creation without area_id (should be 422)...")
            
            project_data = {
                "name": f"Test Project No Area {int(time.time())}",
                "description": "Test project without area_id",
                "priority": "medium",
                "status": "Not Started"
            }
            
            response = self.session.post(
                f"{self.base_url}/projects",
                json=project_data,
                timeout=10
            )
            
            if response.status_code == 422:
                self.log_test("Projects without area_id", True, "Correctly returned 422 for missing area_id", response.status_code)
                return True
            else:
                self.log_test("Projects without area_id", False, f"Expected 422, got {response.status_code}: {response.text}", response.status_code)
                return False
                
        except Exception as e:
            self.log_test("Projects without area_id", False, f"Error: {str(e)}")
            return False
    
    def test_projects_with_area_id(self, area_id: str) -> tuple[bool, str]:
        """Test POST /api/projects with area_id should return 200. Returns (success, project_id)"""
        try:
            print(f"\n📝 Testing Projects creation with area_id (should be 200)...")
            
            project_data = {
                "name": f"Test Project With Area {int(time.time())}",
                "description": "Test project with area_id",
                "priority": "medium",
                "status": "Not Started",
                "area_id": area_id
            }
            
            response = self.session.post(
                f"{self.base_url}/projects",
                json=project_data,
                timeout=10
            )
            
            if response.status_code == 200:
                project_id = response.json().get('id')
                self.log_test("Projects with area_id", True, f"Successfully created project with area_id", response.status_code)
                return True, project_id
            else:
                self.log_test("Projects with area_id", False, f"Expected 200, got {response.status_code}: {response.text}", response.status_code)
                return False, None
                
        except Exception as e:
            self.log_test("Projects with area_id", False, f"Error: {str(e)}")
            return False, None
    
    def test_cascade_deletion(self) -> bool:
        """Test DELETE cascades: create P->A->PR->T then delete P and verify no children"""
        try:
            print(f"\n🗑️ Testing CASCADE deletion functionality...")
            
            # Step 1: Create Pillar
            pillar_data = {
                "name": f"Cascade Test Pillar {int(time.time())}",
                "description": "Test pillar for cascade deletion",
                "importance": 3,
                "time_allocation": 25,
                "icon": "🧪",
                "color": "#EF4444"
            }
            
            pillar_response = self.session.post(f"{self.base_url}/pillars", json=pillar_data, timeout=10)
            if pillar_response.status_code != 200:
                self.log_test("Cascade deletion (pillar creation)", False, f"Failed to create pillar: {pillar_response.text}", pillar_response.status_code)
                return False
            
            pillar_id = pillar_response.json().get('id')
            print(f"  ✅ Created Pillar: {pillar_id}")
            
            # Step 2: Create Area
            area_data = {
                "name": f"Cascade Test Area {int(time.time())}",
                "description": "Test area for cascade deletion",
                "importance": 3,
                "pillar_id": pillar_id
            }
            
            area_response = self.session.post(f"{self.base_url}/areas", json=area_data, timeout=10)
            if area_response.status_code != 200:
                self.log_test("Cascade deletion (area creation)", False, f"Failed to create area: {area_response.text}", area_response.status_code)
                return False
            
            area_id = area_response.json().get('id')
            print(f"  ✅ Created Area: {area_id}")
            
            # Step 3: Create Project
            project_data = {
                "name": f"Cascade Test Project {int(time.time())}",
                "description": "Test project for cascade deletion",
                "priority": "medium",
                "status": "Not Started",
                "area_id": area_id
            }
            
            project_response = self.session.post(f"{self.base_url}/projects", json=project_data, timeout=10)
            if project_response.status_code != 200:
                self.log_test("Cascade deletion (project creation)", False, f"Failed to create project: {project_response.text}", project_response.status_code)
                return False
            
            project_id = project_response.json().get('id')
            print(f"  ✅ Created Project: {project_id}")
            
            # Step 4: Create Task
            task_data = {
                "name": f"Cascade Test Task {int(time.time())}",
                "description": "Test task for cascade deletion",
                "priority": "medium",
                "status": "todo",
                "project_id": project_id
            }
            
            task_response = self.session.post(f"{self.base_url}/tasks", json=task_data, timeout=10)
            if task_response.status_code != 200:
                self.log_test("Cascade deletion (task creation)", False, f"Failed to create task: {task_response.text}", task_response.status_code)
                return False
            
            task_id = task_response.json().get('id')
            print(f"  ✅ Created Task: {task_id}")
            
            # Step 5: Delete Pillar (should cascade delete all children)
            delete_response = self.session.delete(f"{self.base_url}/pillars/{pillar_id}", timeout=10)
            if delete_response.status_code not in [200, 204]:
                self.log_test("Cascade deletion (pillar deletion)", False, f"Failed to delete pillar: {delete_response.text}", delete_response.status_code)
                return False
            
            print(f"  ✅ Deleted Pillar: {pillar_id}")
            
            # Step 6: Verify all children are deleted
            time.sleep(1)  # Give a moment for cascade to complete
            
            # Check area is deleted
            area_check = self.session.get(f"{self.base_url}/areas", timeout=10)
            if area_check.status_code == 200:
                areas = area_check.json()
                area_exists = any(area.get('id') == area_id for area in areas)
                if area_exists:
                    self.log_test("Cascade deletion (area verification)", False, f"Area {area_id} still exists after pillar deletion")
                    return False
            
            # Check project is deleted
            project_check = self.session.get(f"{self.base_url}/projects", timeout=10)
            if project_check.status_code == 200:
                projects = project_check.json()
                project_exists = any(project.get('id') == project_id for project in projects)
                if project_exists:
                    self.log_test("Cascade deletion (project verification)", False, f"Project {project_id} still exists after pillar deletion")
                    return False
            
            # Check task is deleted
            task_check = self.session.get(f"{self.base_url}/tasks", timeout=10)
            if task_check.status_code == 200:
                tasks = task_check.json()
                task_exists = any(task.get('id') == task_id for task in tasks)
                if task_exists:
                    self.log_test("Cascade deletion (task verification)", False, f"Task {task_id} still exists after pillar deletion")
                    return False
            
            self.log_test("Cascade deletion", True, "All children successfully deleted with pillar", delete_response.status_code)
            return True
            
        except Exception as e:
            self.log_test("Cascade deletion", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all NOT NULL regression tests"""
        print("🧪 NOT NULL REGRESSION TESTING")
        print("=" * 50)
        
        # Test 1: Authentication
        if not self.authenticate():
            print("\n❌ Authentication failed - cannot proceed with tests")
            return self.generate_summary()
        
        # Test 2: Areas without pillar_id (should be 422)
        test2_result = self.test_areas_without_pillar_id()
        
        # Test 3: Areas with pillar_id (should be 200)
        test3_result, area_id = self.test_areas_with_pillar_id()
        
        # Test 4: Projects without area_id (should be 422)
        test4_result = self.test_projects_without_area_id()
        
        # Test 5: Projects with area_id (should be 200) - only if we have area_id
        test5_result = False
        if area_id:
            test5_result, project_id = self.test_projects_with_area_id(area_id)
        
        # Test 6: Cascade deletion
        test6_result = self.test_cascade_deletion()
        
        return self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\nDETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result['success'] else "❌"
            status_code = f" (HTTP {result['status_code']})" if result.get('status_code') else ""
            print(f"{status_icon} {result['test']}{status_code}: {result['message']}")
        
        # Return summary for test_result.md update
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': (passed_tests/total_tests)*100 if total_tests > 0 else 0,
            'results': self.test_results
        }

if __name__ == "__main__":
    tester = NotNullRegressionTester()
    summary = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if summary['failed_tests'] == 0 else 1)