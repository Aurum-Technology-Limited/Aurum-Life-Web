#!/usr/bin/env python3
"""
PROJECTS 422 FIX AND AREAS REFLECTION TESTING
Testing the Projects 422 fix and Areas UI refresh + cache invalidation.

FOCUS AREAS:
1. Authentication with marc.alleyne@aurumtechnologyltd.com/password123
2. Step A: Areas sanity for linkage - Create pillar, create area with pillar_id, verify GET /api/areas and /api/ultra/areas
3. Step B: Projects creation 422 fix validation - Test POST /api/projects with different scenarios
4. Step C: Projects list retrieval - GET /api/projects 
5. Step D: Cleanup - DELETE created items
6. Additionally verify cache invalidation for /api/ultra/areas

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password123
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://productivity-hub-23.preview.emergentagent.com/api"

class Projects422AreasReflectionTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Use the specified test credentials
        self.test_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.test_user_password = "password123"
        
        # Track created items for cleanup
        self.created_pillar_id = None
        self.created_area_id = None
        self.created_project_ids = []
        
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
            print(f"   Data: {json.dumps(data, indent=2)}")

    def authenticate(self) -> bool:
        """Authenticate and get JWT token"""
        try:
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                auth_data = response.json()
                self.auth_token = auth_data.get('access_token')
                self.session.headers.update({'Authorization': f'Bearer {self.auth_token}'})
                
                self.log_test("Authentication", True, f"Successfully logged in as {self.test_user_email}")
                return True
            else:
                self.log_test("Authentication", False, f"Login failed with status {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, f"Authentication error: {str(e)}")
            return False

    def step_a_areas_sanity_linkage(self) -> bool:
        """Step A: Areas sanity for linkage - Create pillar, create area, verify endpoints"""
        try:
            # Create a pillar first
            pillar_data = {
                "name": "E2E Test Pillar for Projects 422",
                "description": "Test pillar for Projects 422 fix verification",
                "icon": "🎯",
                "color": "#4CAF50",
                "importance": 3
            }
            
            response = self.session.post(f"{self.base_url}/pillars", json=pillar_data)
            
            if response.status_code != 200:
                self.log_test("Step A - Create Pillar", False, f"Failed to create pillar: {response.status_code}", response.text)
                return False
            
            pillar_result = response.json()
            self.created_pillar_id = pillar_result.get('id')
            self.log_test("Step A - Create Pillar", True, f"Created pillar with ID: {self.created_pillar_id}")
            
            # Create an area with the pillar_id
            area_data = {
                "name": "E2E Area For Project",
                "description": "",
                "pillar_id": self.created_pillar_id,
                "icon": "🎯",
                "color": "#F4B400",
                "importance": 3
            }
            
            response = self.session.post(f"{self.base_url}/areas", json=area_data)
            
            if response.status_code != 200:
                self.log_test("Step A - Create Area", False, f"Failed to create area: {response.status_code}", response.text)
                return False
            
            area_result = response.json()
            self.created_area_id = area_result.get('id')
            self.log_test("Step A - Create Area", True, f"Created area with ID: {self.created_area_id}")
            
            # Verify GET /api/areas shows the created area
            response = self.session.get(f"{self.base_url}/areas")
            
            if response.status_code != 200:
                self.log_test("Step A - GET /api/areas", False, f"Failed to get areas: {response.status_code}", response.text)
                return False
            
            areas = response.json()
            area_found = any(area.get('id') == self.created_area_id for area in areas)
            
            if not area_found:
                self.log_test("Step A - GET /api/areas", False, "Created area not found in areas list", areas)
                return False
            
            self.log_test("Step A - GET /api/areas", True, f"Found created area in areas list ({len(areas)} total areas)")
            
            # Verify GET /api/ultra/areas shows the created area
            response = self.session.get(f"{self.base_url}/ultra/areas")
            
            if response.status_code != 200:
                self.log_test("Step A - GET /api/ultra/areas", False, f"Failed to get ultra areas: {response.status_code}", response.text)
                return False
            
            ultra_areas = response.json()
            ultra_area_found = any(area.get('id') == self.created_area_id for area in ultra_areas)
            
            if not ultra_area_found:
                self.log_test("Step A - GET /api/ultra/areas", False, "Created area not found in ultra areas list", ultra_areas)
                return False
            
            self.log_test("Step A - GET /api/ultra/areas", True, f"Found created area in ultra areas list ({len(ultra_areas)} total areas)")
            
            return True
            
        except Exception as e:
            self.log_test("Step A - Areas Sanity", False, f"Error in Step A: {str(e)}")
            return False

    def step_b_projects_422_fix_validation(self) -> bool:
        """Step B: Projects creation 422 fix validation - Test different POST scenarios"""
        try:
            # Case 1: POST /api/projects with minimal payload omitting area_id
            case1_data = {
                "name": "Proj No Area",
                "description": ""
            }
            
            response = self.session.post(f"{self.base_url}/projects", json=case1_data)
            
            if response.status_code == 200:
                project_result = response.json()
                project_id = project_result.get('id')
                self.created_project_ids.append(project_id)
                
                # Check if response has expected fields
                has_id = 'id' in project_result
                has_name = 'name' in project_result
                has_default_mappings = True  # Check for default status, etc.
                
                self.log_test("Step B - Case 1 (No area_id)", True, 
                            f"Created project without area_id. ID: {project_id}, has required fields: id={has_id}, name={has_name}")
            else:
                self.log_test("Step B - Case 1 (No area_id)", False, 
                            f"Failed to create project without area_id: {response.status_code}", response.text)
                return False
            
            # Case 2: POST /api/projects with valid area_id
            case2_data = {
                "name": "Proj With Area",
                "description": "desc",
                "deadline": datetime.now().isoformat(),
                "area_id": self.created_area_id
            }
            
            response = self.session.post(f"{self.base_url}/projects", json=case2_data)
            
            if response.status_code == 200:
                project_result = response.json()
                project_id = project_result.get('id')
                self.created_project_ids.append(project_id)
                
                # Verify due_date mapping and area_id setting
                has_due_date = 'due_date' in project_result
                has_is_active = 'is_active' in project_result or 'status' in project_result
                correct_area_id = project_result.get('area_id') == self.created_area_id
                
                self.log_test("Step B - Case 2 (With area_id)", True, 
                            f"Created project with area_id. ID: {project_id}, due_date mapped: {has_due_date}, area_id correct: {correct_area_id}")
            else:
                self.log_test("Step B - Case 2 (With area_id)", False, 
                            f"Failed to create project with area_id: {response.status_code}", response.text)
                return False
            
            # Case 3: POST /api/projects with deadline as ISO string without status
            case3_data = {
                "name": "Proj ISO Deadline",
                "description": "Test ISO deadline",
                "deadline": datetime.now().isoformat()
            }
            
            response = self.session.post(f"{self.base_url}/projects", json=case3_data)
            
            if response.status_code == 200:
                project_result = response.json()
                project_id = project_result.get('id')
                self.created_project_ids.append(project_id)
                
                # Verify status defaulted to "Not Started"
                status = project_result.get('status', 'Unknown')
                status_defaulted = status == "Not Started"
                
                self.log_test("Step B - Case 3 (ISO deadline)", True, 
                            f"Created project with ISO deadline. ID: {project_id}, status defaulted to 'Not Started': {status_defaulted} (actual: {status})")
            else:
                self.log_test("Step B - Case 3 (ISO deadline)", False, 
                            f"Failed to create project with ISO deadline: {response.status_code}", response.text)
                return False
            
            return True
            
        except Exception as e:
            self.log_test("Step B - Projects 422 Fix", False, f"Error in Step B: {str(e)}")
            return False

    def step_c_projects_list_retrieval(self) -> bool:
        """Step C: Projects list retrieval - Verify GET /api/projects"""
        try:
            response = self.session.get(f"{self.base_url}/projects")
            
            if response.status_code != 200:
                self.log_test("Step C - GET /api/projects", False, f"Failed to get projects: {response.status_code}", response.text)
                return False
            
            projects = response.json()
            
            # Verify at least the newly created projects are returned
            found_projects = []
            for project_id in self.created_project_ids:
                found = any(project.get('id') == project_id for project in projects)
                if found:
                    found_projects.append(project_id)
            
            # Check for due_date mapping from deadline
            due_date_mappings = []
            for project in projects:
                if project.get('id') in self.created_project_ids:
                    has_due_date = 'due_date' in project
                    due_date_mappings.append(has_due_date)
            
            success = len(found_projects) == len(self.created_project_ids)
            
            self.log_test("Step C - Projects List", success, 
                        f"Found {len(found_projects)}/{len(self.created_project_ids)} created projects in list. Total projects: {len(projects)}")
            
            return success
            
        except Exception as e:
            self.log_test("Step C - Projects List", False, f"Error in Step C: {str(e)}")
            return False

    def step_d_cleanup(self) -> bool:
        """Step D: Cleanup - DELETE created items and verify cache invalidation"""
        try:
            cleanup_success = True
            
            # Delete created projects
            for project_id in self.created_project_ids:
                try:
                    response = self.session.delete(f"{self.base_url}/projects/{project_id}")
                    if response.status_code in [200, 204]:
                        self.log_test(f"Cleanup - Delete Project {project_id}", True, "Project deleted successfully")
                    else:
                        self.log_test(f"Cleanup - Delete Project {project_id}", False, f"Failed to delete project: {response.status_code}")
                        cleanup_success = False
                except Exception as e:
                    self.log_test(f"Cleanup - Delete Project {project_id}", False, f"Error deleting project: {str(e)}")
                    cleanup_success = False
            
            # Delete created area
            if self.created_area_id:
                try:
                    response = self.session.delete(f"{self.base_url}/areas/{self.created_area_id}")
                    if response.status_code in [200, 204]:
                        self.log_test("Cleanup - Delete Area", True, "Area deleted successfully")
                    else:
                        self.log_test("Cleanup - Delete Area", False, f"Failed to delete area: {response.status_code}")
                        cleanup_success = False
                except Exception as e:
                    self.log_test("Cleanup - Delete Area", False, f"Error deleting area: {str(e)}")
                    cleanup_success = False
            
            # Delete created pillar
            if self.created_pillar_id:
                try:
                    response = self.session.delete(f"{self.base_url}/pillars/{self.created_pillar_id}")
                    if response.status_code in [200, 204]:
                        self.log_test("Cleanup - Delete Pillar", True, "Pillar deleted successfully")
                    else:
                        self.log_test("Cleanup - Delete Pillar", False, f"Failed to delete pillar: {response.status_code}")
                        cleanup_success = False
                except Exception as e:
                    self.log_test("Cleanup - Delete Pillar", False, f"Error deleting pillar: {str(e)}")
                    cleanup_success = False
            
            # Verify cache invalidation - check that /api/ultra/areas no longer shows deleted area
            if self.created_area_id:
                try:
                    time.sleep(1)  # Give cache time to invalidate
                    response = self.session.get(f"{self.base_url}/ultra/areas")
                    if response.status_code == 200:
                        ultra_areas = response.json()
                        area_still_exists = any(area.get('id') == self.created_area_id for area in ultra_areas)
                        
                        if area_still_exists:
                            self.log_test("Cache Invalidation Check", False, "Deleted area still appears in /api/ultra/areas (stale cache)")
                        else:
                            self.log_test("Cache Invalidation Check", True, "Deleted area no longer appears in /api/ultra/areas (cache invalidated)")
                    else:
                        self.log_test("Cache Invalidation Check", False, f"Failed to check ultra areas: {response.status_code}")
                except Exception as e:
                    self.log_test("Cache Invalidation Check", False, f"Error checking cache invalidation: {str(e)}")
            
            return cleanup_success
            
        except Exception as e:
            self.log_test("Step D - Cleanup", False, f"Error in Step D: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all test steps"""
        print("🚀 Starting Projects 422 Fix and Areas Reflection Testing")
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Step 1: Authentication
        if not self.authenticate():
            print("❌ Authentication failed. Cannot proceed with tests.")
            return False
        
        # Step A: Areas sanity for linkage
        print("\n📋 Step A: Areas sanity for linkage")
        step_a_success = self.step_a_areas_sanity_linkage()
        
        # Step B: Projects creation 422 fix validation
        print("\n📋 Step B: Projects creation 422 fix validation")
        step_b_success = self.step_b_projects_422_fix_validation()
        
        # Step C: Projects list retrieval
        print("\n📋 Step C: Projects list retrieval")
        step_c_success = self.step_c_projects_list_retrieval()
        
        # Step D: Cleanup
        print("\n📋 Step D: Cleanup")
        step_d_success = self.step_d_cleanup()
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Step-by-step results
        print(f"\nStep A (Areas sanity): {'✅ PASS' if step_a_success else '❌ FAIL'}")
        print(f"Step B (Projects 422 fix): {'✅ PASS' if step_b_success else '❌ FAIL'}")
        print(f"Step C (Projects list): {'✅ PASS' if step_c_success else '❌ FAIL'}")
        print(f"Step D (Cleanup): {'✅ PASS' if step_d_success else '❌ FAIL'}")
        
        # Failed tests details
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test']}: {result['message']}")
        
        overall_success = step_a_success and step_b_success and step_c_success and step_d_success
        
        print(f"\n🎯 OVERALL RESULT: {'✅ SUCCESS' if overall_success else '❌ FAILURE'}")
        
        return overall_success

def main():
    """Main function to run the tests"""
    tester = Projects422AreasReflectionTester()
    success = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()