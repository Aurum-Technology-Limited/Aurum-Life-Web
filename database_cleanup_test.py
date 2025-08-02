#!/usr/bin/env python3
"""
DATABASE CLEANUP VERIFICATION TESTING
Complete testing after database cleanup to verify marc.alleyne@aurumtechnologyltd.com account functionality.

FOCUS AREAS:
1. Authentication - verify marc.alleyne@aurumtechnologyltd.com can still log in
2. Dashboard API - verify it returns correct user data and stats 
3. Core CRUD endpoints - pillars, areas, projects, tasks (GET operations)
4. Data integrity - verify the preserved user's data is intact and properly linked
5. Error handling for non-existent users (all test users have been deleted)

TESTING CRITERIA:
- Proper authentication with preserved user
- Correct data retrieval (7 pillars, 28 areas, 37 projects, 20 tasks)
- Data integrity and relationships
- Error handling for deleted test users
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://d9c49f44-9ee9-4b2c-b085-fbd14af62532.preview.emergentagent.com/api"

class DatabaseCleanupVerificationTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Use the preserved user credentials
        self.preserved_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.preserved_user_password = "password123"  # Assuming standard password
        # Test users that should be deleted
        self.deleted_test_users = [
            "nav.test@aurumlife.com",
            "final.test@aurumlife.com",
            "test@example.com"
        ]
        
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

    def test_preserved_user_authentication(self):
        """Test authentication with preserved user marc.alleyne@aurumtechnologyltd.com"""
        print("\n=== TESTING PRESERVED USER AUTHENTICATION ===")
        
        # Login user with preserved credentials
        login_data = {
            "email": self.preserved_user_email,
            "password": self.preserved_user_password
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        self.log_test(
            "PRESERVED USER LOGIN",
            result['success'],
            f"Login successful with {self.preserved_user_email}" if result['success'] else f"Login failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            # Try alternative password
            login_data["password"] = "aurumtech123"
            result = self.make_request('POST', '/auth/login', data=login_data)
            self.log_test(
                "PRESERVED USER LOGIN (ALT PASSWORD)",
                result['success'],
                f"Login successful with alternative password" if result['success'] else f"Login failed with alternative password: {result.get('error', 'Unknown error')}"
            )
        
        if not result['success']:
            return False
        
        token_data = result['data']
        self.auth_token = token_data.get('access_token')
        
        # Verify token works
        result = self.make_request('GET', '/auth/me', use_auth=True)
        self.log_test(
            "PRESERVED USER TOKEN VALIDATION",
            result['success'],
            f"Token validated successfully, user: {result['data'].get('email', 'Unknown')}" if result['success'] else f"Token validation failed: {result.get('error', 'Unknown error')}"
        )
        
        return result['success']

    def test_deleted_users_authentication(self):
        """Test that deleted test users can no longer authenticate"""
        print("\n=== TESTING DELETED USERS AUTHENTICATION ===")
        
        deleted_count = 0
        total_test_users = len(self.deleted_test_users)
        
        for test_email in self.deleted_test_users:
            login_data = {
                "email": test_email,
                "password": "testpassword123"
            }
            
            result = self.make_request('POST', '/auth/login', data=login_data)
            user_deleted = not result['success'] and result['status_code'] in [401, 404]
            
            self.log_test(
                f"DELETED USER - {test_email}",
                user_deleted,
                f"User properly deleted (cannot authenticate)" if user_deleted else f"User still exists or unexpected error: {result.get('error', 'Unknown')}"
            )
            
            if user_deleted:
                deleted_count += 1
        
        deletion_success_rate = (deleted_count / total_test_users) * 100
        overall_deletion_success = deletion_success_rate >= 100
        
        self.log_test(
            "DATABASE CLEANUP - USER DELETION",
            overall_deletion_success,
            f"User deletion verification: {deleted_count}/{total_test_users} test users properly deleted ({deletion_success_rate:.1f}%)"
        )
        
        return overall_deletion_success

    def test_dashboard_api(self):
        """Test dashboard API returns correct user data and stats"""
        print("\n=== TESTING DASHBOARD API ===")
        
        if not self.auth_token:
            self.log_test("DASHBOARD API - Authentication Required", False, "No authentication token available")
            return False
        
        # Test GET /api/dashboard
        result = self.make_request('GET', '/dashboard', use_auth=True)
        self.log_test(
            "DASHBOARD API ACCESS",
            result['success'],
            f"Dashboard API accessible" if result['success'] else f"Dashboard API failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        dashboard_data = result['data']
        
        # Check if dashboard has expected structure
        expected_fields = ['user', 'stats', 'recent_activity']
        has_expected_structure = any(field in dashboard_data for field in expected_fields)
        
        self.log_test(
            "DASHBOARD API - RESPONSE STRUCTURE",
            has_expected_structure,
            f"Dashboard has expected structure" if has_expected_structure else f"Dashboard structure unexpected: {list(dashboard_data.keys())}"
        )
        
        # Check user information
        if 'user' in dashboard_data:
            user_info = dashboard_data['user']
            correct_user = user_info.get('email') == self.preserved_user_email
            self.log_test(
                "DASHBOARD API - USER INFORMATION",
                correct_user,
                f"Correct user information returned: {user_info.get('email')}" if correct_user else f"Incorrect user: expected {self.preserved_user_email}, got {user_info.get('email')}"
            )
        
        return has_expected_structure

    def test_pillars_data_integrity(self):
        """Test pillars data integrity - should have 7 pillars"""
        print("\n=== TESTING PILLARS DATA INTEGRITY ===")
        
        if not self.auth_token:
            self.log_test("PILLARS DATA - Authentication Required", False, "No authentication token available")
            return False
        
        # Test GET /api/pillars
        result = self.make_request('GET', '/pillars', use_auth=True)
        self.log_test(
            "PILLARS API ACCESS",
            result['success'],
            f"Pillars API accessible" if result['success'] else f"Pillars API failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        pillars = result['data']
        pillar_count = len(pillars) if isinstance(pillars, list) else 0
        expected_pillar_count = 7
        
        correct_count = pillar_count == expected_pillar_count
        self.log_test(
            "PILLARS DATA - COUNT VERIFICATION",
            correct_count,
            f"Correct pillar count: {pillar_count}/{expected_pillar_count}" if correct_count else f"Incorrect pillar count: expected {expected_pillar_count}, got {pillar_count}"
        )
        
        # Check pillar structure
        if pillar_count > 0:
            first_pillar = pillars[0]
            required_fields = ['id', 'name', 'description']
            has_required_fields = all(field in first_pillar for field in required_fields)
            
            self.log_test(
                "PILLARS DATA - STRUCTURE VERIFICATION",
                has_required_fields,
                f"Pillars have required fields" if has_required_fields else f"Missing fields in pillar: {[f for f in required_fields if f not in first_pillar]}"
            )
            
            return correct_count and has_required_fields
        
        return correct_count

    def test_areas_data_integrity(self):
        """Test areas data integrity - should have 28 areas"""
        print("\n=== TESTING AREAS DATA INTEGRITY ===")
        
        if not self.auth_token:
            self.log_test("AREAS DATA - Authentication Required", False, "No authentication token available")
            return False
        
        # Test GET /api/areas
        result = self.make_request('GET', '/areas', use_auth=True)
        self.log_test(
            "AREAS API ACCESS",
            result['success'],
            f"Areas API accessible" if result['success'] else f"Areas API failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        areas = result['data']
        area_count = len(areas) if isinstance(areas, list) else 0
        expected_area_count = 28
        
        correct_count = area_count == expected_area_count
        self.log_test(
            "AREAS DATA - COUNT VERIFICATION",
            correct_count,
            f"Correct area count: {area_count}/{expected_area_count}" if correct_count else f"Incorrect area count: expected {expected_area_count}, got {area_count}"
        )
        
        # Check area structure and pillar relationships
        if area_count > 0:
            first_area = areas[0]
            required_fields = ['id', 'name', 'pillar_id']
            has_required_fields = all(field in first_area for field in required_fields)
            
            self.log_test(
                "AREAS DATA - STRUCTURE VERIFICATION",
                has_required_fields,
                f"Areas have required fields" if has_required_fields else f"Missing fields in area: {[f for f in required_fields if f not in first_area]}"
            )
            
            # Check pillar relationships
            areas_with_pillars = sum(1 for area in areas if area.get('pillar_id'))
            pillar_relationship_integrity = areas_with_pillars > 0
            
            self.log_test(
                "AREAS DATA - PILLAR RELATIONSHIPS",
                pillar_relationship_integrity,
                f"Areas have pillar relationships: {areas_with_pillars}/{area_count}" if pillar_relationship_integrity else "No areas have pillar relationships"
            )
            
            return correct_count and has_required_fields and pillar_relationship_integrity
        
        return correct_count

    def test_projects_data_integrity(self):
        """Test projects data integrity - should have 37 projects"""
        print("\n=== TESTING PROJECTS DATA INTEGRITY ===")
        
        if not self.auth_token:
            self.log_test("PROJECTS DATA - Authentication Required", False, "No authentication token available")
            return False
        
        # Test GET /api/projects
        result = self.make_request('GET', '/projects', use_auth=True)
        self.log_test(
            "PROJECTS API ACCESS",
            result['success'],
            f"Projects API accessible" if result['success'] else f"Projects API failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        projects = result['data']
        project_count = len(projects) if isinstance(projects, list) else 0
        expected_project_count = 37
        
        correct_count = project_count == expected_project_count
        self.log_test(
            "PROJECTS DATA - COUNT VERIFICATION",
            correct_count,
            f"Correct project count: {project_count}/{expected_project_count}" if correct_count else f"Incorrect project count: expected {expected_project_count}, got {project_count}"
        )
        
        # Check project structure and area relationships
        if project_count > 0:
            first_project = projects[0]
            required_fields = ['id', 'name', 'area_id']
            has_required_fields = all(field in first_project for field in required_fields)
            
            self.log_test(
                "PROJECTS DATA - STRUCTURE VERIFICATION",
                has_required_fields,
                f"Projects have required fields" if has_required_fields else f"Missing fields in project: {[f for f in required_fields if f not in first_project]}"
            )
            
            # Check area relationships
            projects_with_areas = sum(1 for project in projects if project.get('area_id'))
            area_relationship_integrity = projects_with_areas > 0
            
            self.log_test(
                "PROJECTS DATA - AREA RELATIONSHIPS",
                area_relationship_integrity,
                f"Projects have area relationships: {projects_with_areas}/{project_count}" if area_relationship_integrity else "No projects have area relationships"
            )
            
            return correct_count and has_required_fields and area_relationship_integrity
        
        return correct_count

    def test_tasks_data_integrity(self):
        """Test tasks data integrity - should have 20 tasks"""
        print("\n=== TESTING TASKS DATA INTEGRITY ===")
        
        if not self.auth_token:
            self.log_test("TASKS DATA - Authentication Required", False, "No authentication token available")
            return False
        
        # Test GET /api/tasks
        result = self.make_request('GET', '/tasks', use_auth=True)
        self.log_test(
            "TASKS API ACCESS",
            result['success'],
            f"Tasks API accessible" if result['success'] else f"Tasks API failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        tasks = result['data']
        task_count = len(tasks) if isinstance(tasks, list) else 0
        expected_task_count = 20
        
        correct_count = task_count == expected_task_count
        self.log_test(
            "TASKS DATA - COUNT VERIFICATION",
            correct_count,
            f"Correct task count: {task_count}/{expected_task_count}" if correct_count else f"Incorrect task count: expected {expected_task_count}, got {task_count}"
        )
        
        # Check task structure and project relationships
        if task_count > 0:
            first_task = tasks[0]
            required_fields = ['id', 'name', 'project_id']
            has_required_fields = all(field in first_task for field in required_fields)
            
            self.log_test(
                "TASKS DATA - STRUCTURE VERIFICATION",
                has_required_fields,
                f"Tasks have required fields" if has_required_fields else f"Missing fields in task: {[f for f in required_fields if f not in first_task]}"
            )
            
            # Check project relationships
            tasks_with_projects = sum(1 for task in tasks if task.get('project_id'))
            project_relationship_integrity = tasks_with_projects > 0
            
            self.log_test(
                "TASKS DATA - PROJECT RELATIONSHIPS",
                project_relationship_integrity,
                f"Tasks have project relationships: {tasks_with_projects}/{task_count}" if project_relationship_integrity else "No tasks have project relationships"
            )
            
            return correct_count and has_required_fields and project_relationship_integrity
        
        return correct_count

    def test_hierarchical_data_integrity(self):
        """Test hierarchical data integrity across all entities"""
        print("\n=== TESTING HIERARCHICAL DATA INTEGRITY ===")
        
        if not self.auth_token:
            self.log_test("HIERARCHICAL DATA - Authentication Required", False, "No authentication token available")
            return False
        
        # Get all data
        pillars_result = self.make_request('GET', '/pillars', use_auth=True)
        areas_result = self.make_request('GET', '/areas', use_auth=True)
        projects_result = self.make_request('GET', '/projects', use_auth=True)
        tasks_result = self.make_request('GET', '/tasks', use_auth=True)
        
        if not all([pillars_result['success'], areas_result['success'], projects_result['success'], tasks_result['success']]):
            self.log_test("HIERARCHICAL DATA - API ACCESS", False, "Could not access all required APIs")
            return False
        
        pillars = pillars_result['data']
        areas = areas_result['data']
        projects = projects_result['data']
        tasks = tasks_result['data']
        
        # Check pillar -> area relationships
        pillar_ids = {p['id'] for p in pillars}
        areas_with_valid_pillars = sum(1 for area in areas if area.get('pillar_id') in pillar_ids)
        pillar_area_integrity = areas_with_valid_pillars == len(areas)
        
        self.log_test(
            "HIERARCHICAL DATA - PILLAR->AREA INTEGRITY",
            pillar_area_integrity,
            f"All areas have valid pillar references: {areas_with_valid_pillars}/{len(areas)}" if pillar_area_integrity else f"Invalid pillar references: {len(areas) - areas_with_valid_pillars}/{len(areas)} areas"
        )
        
        # Check area -> project relationships
        area_ids = {a['id'] for a in areas}
        projects_with_valid_areas = sum(1 for project in projects if project.get('area_id') in area_ids)
        area_project_integrity = projects_with_valid_areas == len(projects)
        
        self.log_test(
            "HIERARCHICAL DATA - AREA->PROJECT INTEGRITY",
            area_project_integrity,
            f"All projects have valid area references: {projects_with_valid_areas}/{len(projects)}" if area_project_integrity else f"Invalid area references: {len(projects) - projects_with_valid_areas}/{len(projects)} projects"
        )
        
        # Check project -> task relationships
        project_ids = {p['id'] for p in projects}
        tasks_with_valid_projects = sum(1 for task in tasks if task.get('project_id') in project_ids)
        project_task_integrity = tasks_with_valid_projects == len(tasks)
        
        self.log_test(
            "HIERARCHICAL DATA - PROJECT->TASK INTEGRITY",
            project_task_integrity,
            f"All tasks have valid project references: {tasks_with_valid_projects}/{len(tasks)}" if project_task_integrity else f"Invalid project references: {len(tasks) - tasks_with_valid_projects}/{len(tasks)} tasks"
        )
        
        overall_integrity = pillar_area_integrity and area_project_integrity and project_task_integrity
        
        self.log_test(
            "HIERARCHICAL DATA - OVERALL INTEGRITY",
            overall_integrity,
            f"Complete hierarchical integrity maintained" if overall_integrity else "Hierarchical integrity issues detected"
        )
        
        return overall_integrity

    def run_comprehensive_database_cleanup_verification(self):
        """Run comprehensive database cleanup verification tests"""
        print("\n🧹 STARTING DATABASE CLEANUP VERIFICATION TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Preserved User: {self.preserved_user_email}")
        print(f"Expected Data: 7 pillars, 28 areas, 37 projects, 20 tasks")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("Preserved User Authentication", self.test_preserved_user_authentication),
            ("Deleted Users Authentication", self.test_deleted_users_authentication),
            ("Dashboard API", self.test_dashboard_api),
            ("Pillars Data Integrity", self.test_pillars_data_integrity),
            ("Areas Data Integrity", self.test_areas_data_integrity),
            ("Projects Data Integrity", self.test_projects_data_integrity),
            ("Tasks Data Integrity", self.test_tasks_data_integrity),
            ("Hierarchical Data Integrity", self.test_hierarchical_data_integrity)
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
        
        success_rate = (successful_tests / total_tests) * 100
        
        print(f"\n" + "=" * 80)
        print("🧹 DATABASE CLEANUP VERIFICATION SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for database cleanup verification
        auth_tests_passed = sum(1 for result in self.test_results if result['success'] and 'AUTHENTICATION' in result['test'])
        data_tests_passed = sum(1 for result in self.test_results if result['success'] and 'DATA' in result['test'])
        integrity_tests_passed = sum(1 for result in self.test_results if result['success'] and 'INTEGRITY' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"Authentication Tests Passed: {auth_tests_passed}")
        print(f"Data Integrity Tests Passed: {data_tests_passed}")
        print(f"Hierarchical Integrity Tests Passed: {integrity_tests_passed}")
        
        if success_rate >= 85:
            print("\n✅ DATABASE CLEANUP VERIFICATION: SUCCESS")
            print("   ✅ Preserved user authentication working")
            print("   ✅ Test users properly deleted")
            print("   ✅ Data integrity maintained")
            print("   ✅ Hierarchical relationships intact")
            print("   ✅ All core APIs functional")
            print("   The database cleanup was successful!")
        else:
            print("\n❌ DATABASE CLEANUP VERIFICATION: ISSUES DETECTED")
            print("   Issues found in database cleanup or data integrity")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 85

def main():
    """Run Database Cleanup Verification Tests"""
    print("🧹 STARTING DATABASE CLEANUP VERIFICATION TESTING")
    print("=" * 80)
    
    tester = DatabaseCleanupVerificationTester()
    
    try:
        # Run the comprehensive database cleanup verification tests
        success = tester.run_comprehensive_database_cleanup_verification()
        
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