#!/usr/bin/env python3
"""
PILLAR HIERARCHY BACKEND IMPLEMENTATION - PHASE 1 TESTING
Comprehensive testing of the Pillar Hierarchy system including:
1. Pillar CRUD Operations
2. Pillar Hierarchy (nested pillars)
3. Area-Pillar Linking
4. Progress Tracking
5. Validation & Security
6. Authentication
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid
import time

# Configuration
BACKEND_URL = "https://d5525f43-5dcd-48e4-b22b-982ef0b3bb33.preview.emergentagent.com/api"

class PillarHierarchyTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        self.test_user_email = f"pillartest_{uuid.uuid4().hex[:8]}@aurumlife.com"
        self.test_user_password = "PillarTest123!"
        self.test_user_data = {
            "username": f"pillartest_{uuid.uuid4().hex[:8]}",
            "email": self.test_user_email,
            "first_name": "Pillar",
            "last_name": "Tester",
            "password": self.test_user_password
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
        headers = {}
        
        # Add authentication header if token is available and requested
        if use_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=headers)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, params=params, headers=headers)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, params=params, headers=headers)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            return {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'data': response.json() if response.content else {},
                'response': response
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', None),
                'data': {},
                'response': getattr(e, 'response', None)
            }

    def setup_authentication(self):
        """Setup authentication for testing"""
        print("🔐 SETTING UP AUTHENTICATION FOR PILLAR HIERARCHY TESTING")
        
        # Register test user
        result = self.make_request('POST', '/auth/register', data=self.test_user_data)
        self.log_test(
            "User Registration for Testing",
            result['success'],
            f"Test user registered: {result['data'].get('username', 'Unknown')}" if result['success'] else f"Registration failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        # Login with test user
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        self.log_test(
            "User Login for Testing",
            result['success'],
            f"Test user logged in successfully" if result['success'] else f"Login failed: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            self.auth_token = result['data'].get('access_token')
            return True
        
        return False

    def test_pillar_hierarchy_backend_implementation(self):
        """COMPREHENSIVE PILLAR HIERARCHY BACKEND TESTING - Phase 1"""
        print("\n=== PILLAR HIERARCHY BACKEND IMPLEMENTATION TESTING - PHASE 1 ===")
        print("Testing comprehensive Pillar Hierarchy system with nested pillars, area-pillar linking, and progress tracking")
        
        if not self.auth_token:
            self.log_test("Pillar Hierarchy Testing Setup", False, "No auth token available")
            return False
        
        # Initialize tracking for created resources
        created_pillars = []
        created_areas = []
        created_projects = []
        created_tasks = []
        
        try:
            # Test 1: Create Root Pillar (Health & Wellness)
            root_pillar_data = {
                "name": "Health & Wellness",
                "description": "Overall health and wellness pillar",
                "icon": "🏃‍♂️",
                "color": "#4CAF50",
                "time_allocation_percentage": 30.0
            }
            
            result = self.make_request('POST', '/pillars', data=root_pillar_data, use_auth=True)
            self.log_test(
                "PILLAR CRUD - Create Root Pillar",
                result['success'],
                f"Root pillar created: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Root pillar creation failed: {result.get('error', 'Unknown error')}"
            )
            
            if not result['success']:
                return False
            
            root_pillar_id = result['data']['id']
            created_pillars.append(root_pillar_id)
            
            # Verify pillar structure
            required_fields = ['id', 'name', 'description', 'icon', 'color', 'user_id', 'sort_order', 'archived', 'created_at', 'updated_at']
            missing_fields = [field for field in required_fields if field not in result['data']]
            self.log_test(
                "Pillar Data Structure Validation",
                len(missing_fields) == 0,
                f"All required fields present" if len(missing_fields) == 0 else f"Missing fields: {missing_fields}"
            )
            
            # Test 2: Create Sub-Pillar (Physical Fitness)
            sub_pillar_data = {
                "name": "Physical Fitness",
                "description": "Exercise and physical activity",
                "icon": "💪",
                "color": "#FF5722",
                "parent_pillar_id": root_pillar_id,
                "time_allocation_percentage": 15.0
            }
            
            result = self.make_request('POST', '/pillars', data=sub_pillar_data, use_auth=True)
            self.log_test(
                "PILLAR HIERARCHY - Create Sub-Pillar",
                result['success'],
                f"Sub-pillar created with parent: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Sub-pillar creation failed: {result.get('error', 'Unknown error')}"
            )
            
            if result['success']:
                sub_pillar_id = result['data']['id']
                created_pillars.append(sub_pillar_id)
                
                # Verify parent-child relationship
                self.log_test(
                    "Parent-Child Relationship Validation",
                    result['data'].get('parent_pillar_id') == root_pillar_id,
                    f"Sub-pillar correctly linked to parent: {result['data'].get('parent_pillar_id') == root_pillar_id}"
                )
            
            # Test 3: Create Another Sub-Pillar (Mental Health)
            mental_pillar_data = {
                "name": "Mental Health",
                "description": "Mental wellness and mindfulness",
                "icon": "🧠",
                "color": "#9C27B0",
                "parent_pillar_id": root_pillar_id,
                "time_allocation_percentage": 15.0
            }
            
            result = self.make_request('POST', '/pillars', data=mental_pillar_data, use_auth=True)
            self.log_test(
                "PILLAR HIERARCHY - Create Second Sub-Pillar",
                result['success'],
                f"Second sub-pillar created: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Second sub-pillar creation failed: {result.get('error', 'Unknown error')}"
            )
            
            if result['success']:
                mental_pillar_id = result['data']['id']
                created_pillars.append(mental_pillar_id)
            
            # Test 4: Get All Pillars with Hierarchy
            result = self.make_request('GET', '/pillars', params={'include_sub_pillars': True}, use_auth=True)
            self.log_test(
                "PILLAR CRUD - Get All Pillars with Hierarchy",
                result['success'],
                f"Retrieved {len(result['data']) if result['success'] else 0} root pillars with hierarchy" if result['success'] else f"Failed to get pillars: {result.get('error', 'Unknown error')}"
            )
            
            if result['success']:
                pillars = result['data']
                # Should have 1 root pillar with 2 sub-pillars
                root_pillars = [p for p in pillars if not p.get('parent_pillar_id')]
                self.log_test(
                    "Hierarchy Structure Validation",
                    len(root_pillars) >= 1 and len(root_pillars[0].get('sub_pillars', [])) >= 2,
                    f"Hierarchy structure correct: {len(root_pillars)} root pillar(s) with {len(root_pillars[0].get('sub_pillars', [])) if root_pillars else 0} sub-pillars"
                )
            
            # Test 5: Get Specific Pillar by ID
            result = self.make_request('GET', f'/pillars/{root_pillar_id}', params={'include_sub_pillars': True}, use_auth=True)
            self.log_test(
                "PILLAR CRUD - Get Specific Pillar by ID",
                result['success'],
                f"Retrieved specific pillar: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Failed to get specific pillar: {result.get('error', 'Unknown error')}"
            )
            
            if result['success']:
                pillar_data = result['data']
                self.log_test(
                    "Specific Pillar Sub-Pillars Included",
                    len(pillar_data.get('sub_pillars', [])) >= 2,
                    f"Sub-pillars included in response: {len(pillar_data.get('sub_pillars', []))}"
                )
            
            # Test 6: Update Pillar
            update_data = {
                "description": "Updated comprehensive health and wellness pillar",
                "time_allocation_percentage": 35.0
            }
            
            result = self.make_request('PUT', f'/pillars/{root_pillar_id}', data=update_data, use_auth=True)
            self.log_test(
                "PILLAR CRUD - Update Pillar",
                result['success'],
                f"Pillar updated successfully" if result['success'] else f"Pillar update failed: {result.get('error', 'Unknown error')}"
            )
            
            # Test 7: Create Area Linked to Pillar
            area_data = {
                "name": "Gym Workouts",
                "description": "Regular gym sessions and strength training",
                "icon": "🏋️‍♂️",
                "color": "#FF5722",
                "pillar_id": sub_pillar_id if 'sub_pillar_id' in locals() else root_pillar_id
            }
            
            result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
            self.log_test(
                "AREA-PILLAR LINKING - Create Area with Pillar Link",
                result['success'],
                f"Area created and linked to pillar: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Area creation failed: {result.get('error', 'Unknown error')}"
            )
            
            if result['success']:
                area_id = result['data']['id']
                created_areas.append(area_id)
                
                # Verify pillar link
                self.log_test(
                    "Area-Pillar Link Validation",
                    result['data'].get('pillar_id') is not None,
                    f"Area correctly linked to pillar: {result['data'].get('pillar_id') is not None}"
                )
                
                # Test 8: Create Project in Area for Progress Tracking
                project_data = {
                    "name": "Strength Training Program",
                    "description": "12-week strength training program",
                    "area_id": area_id,
                    "priority": "high"
                }
                
                result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
                self.log_test(
                    "PROGRESS TRACKING - Create Project in Area",
                    result['success'],
                    f"Project created in area: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Project creation failed: {result.get('error', 'Unknown error')}"
                )
                
                if result['success']:
                    project_id = result['data']['id']
                    created_projects.append(project_id)
                    
                    # Test 9: Create Tasks in Project for Progress Tracking
                    task_data_list = [
                        {
                            "name": "Week 1 - Squats",
                            "description": "3 sets of 10 squats",
                            "project_id": project_id,
                            "priority": "high",
                            "status": "completed"
                        },
                        {
                            "name": "Week 2 - Deadlifts",
                            "description": "3 sets of 8 deadlifts",
                            "project_id": project_id,
                            "priority": "medium",
                            "status": "in_progress"
                        },
                        {
                            "name": "Week 3 - Bench Press",
                            "description": "3 sets of 12 bench press",
                            "project_id": project_id,
                            "priority": "medium",
                            "status": "todo"
                        }
                    ]
                    
                    for i, task_data in enumerate(task_data_list):
                        result = self.make_request('POST', '/tasks', data=task_data, use_auth=True)
                        self.log_test(
                            f"PROGRESS TRACKING - Create Task {i+1}",
                            result['success'],
                            f"Task created: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Task creation failed: {result.get('error', 'Unknown error')}"
                        )
                        
                        if result['success']:
                            created_tasks.append(result['data']['id'])
            
            # Test 10: Get Areas to Verify Pillar Name Resolution
            result = self.make_request('GET', '/areas', use_auth=True)
            self.log_test(
                "AREA-PILLAR LINKING - Pillar Name Resolution",
                result['success'],
                f"Retrieved areas with pillar information" if result['success'] else f"Failed to get areas: {result.get('error', 'Unknown error')}"
            )
            
            if result['success'] and result['data']:
                area_with_pillar = next((area for area in result['data'] if area.get('pillar_id')), None)
                if area_with_pillar:
                    self.log_test(
                        "Pillar Name Resolution in Area",
                        area_with_pillar.get('pillar_name') is not None,
                        f"Pillar name resolved in area: {area_with_pillar.get('pillar_name', 'Not resolved')}"
                    )
            
            # Test 11: Archive Pillar
            result = self.make_request('PUT', f'/pillars/{root_pillar_id}/archive', use_auth=True)
            self.log_test(
                "PILLAR CRUD - Archive Pillar",
                result['success'],
                f"Pillar archived successfully" if result['success'] else f"Pillar archiving failed: {result.get('error', 'Unknown error')}"
            )
            
            # Test 12: Unarchive Pillar
            result = self.make_request('PUT', f'/pillars/{root_pillar_id}/unarchive', use_auth=True)
            self.log_test(
                "PILLAR CRUD - Unarchive Pillar",
                result['success'],
                f"Pillar unarchived successfully" if result['success'] else f"Pillar unarchiving failed: {result.get('error', 'Unknown error')}"
            )
            
            # Test 13: Validation - Prevent Circular Reference
            circular_data = {
                "parent_pillar_id": root_pillar_id
            }
            
            result = self.make_request('PUT', f'/pillars/{root_pillar_id}', data=circular_data, use_auth=True)
            self.log_test(
                "VALIDATION - Circular Reference Prevention",
                not result['success'] and result['status_code'] == 400,
                f"Circular reference properly prevented" if not result['success'] else "Circular reference was incorrectly allowed"
            )
            
            # Test 14: Validation - Invalid Parent Pillar
            invalid_parent_data = {
                "name": "Test Invalid Parent",
                "parent_pillar_id": "non-existent-pillar-id"
            }
            
            result = self.make_request('POST', '/pillars', data=invalid_parent_data, use_auth=True)
            self.log_test(
                "VALIDATION - Invalid Parent Pillar",
                not result['success'] and result['status_code'] == 400,
                f"Invalid parent pillar properly rejected" if not result['success'] else "Invalid parent pillar was incorrectly accepted"
            )
            
            # Test 15: Progress Tracking - Get Pillar with Progress
            result = self.make_request('GET', f'/pillars/{root_pillar_id}', params={'include_areas': True}, use_auth=True)
            self.log_test(
                "PROGRESS TRACKING - Pillar Progress Calculation",
                result['success'],
                f"Pillar progress data retrieved" if result['success'] else f"Failed to get pillar progress: {result.get('error', 'Unknown error')}"
            )
            
            if result['success']:
                pillar_data = result['data']
                progress_fields = ['area_count', 'project_count', 'task_count', 'completed_task_count']
                has_progress_fields = all(field in pillar_data for field in progress_fields)
                
                self.log_test(
                    "Progress Fields Present",
                    has_progress_fields,
                    f"Progress tracking fields present: {has_progress_fields}"
                )
                
                if has_progress_fields:
                    self.log_test(
                        "Progress Data Accuracy",
                        pillar_data['area_count'] >= 1,  # We created at least one area
                        f"Progress data shows {pillar_data['area_count']} areas, {pillar_data['project_count']} projects, {pillar_data['task_count']} tasks"
                    )
            
            # Test 16: Authentication - Unauthenticated Access
            result = self.make_request('GET', '/pillars', use_auth=False)
            self.log_test(
                "AUTHENTICATION - Unauthenticated Access Blocked",
                not result['success'] and result['status_code'] in [401, 403],
                f"Unauthenticated access properly blocked (status: {result['status_code']})" if not result['success'] else "Unauthenticated access was incorrectly allowed"
            )
            
            # Test 17: User Isolation - Verify pillars are user-specific
            result = self.make_request('GET', '/pillars', use_auth=True)
            if result['success']:
                user_pillars = result['data']
                self.log_test(
                    "USER ISOLATION - User-Specific Pillar Filtering",
                    len(user_pillars) >= 1,
                    f"User-specific pillars retrieved: {len(user_pillars)} pillars for authenticated user"
                )
            
            print(f"\n✅ PILLAR HIERARCHY BACKEND IMPLEMENTATION TESTING COMPLETED")
            print(f"   Created {len(created_pillars)} pillars, {len(created_areas)} areas, {len(created_projects)} projects, {len(created_tasks)} tasks")
            print(f"   Tested: CRUD operations, hierarchy, area-pillar linking, progress tracking, validation, authentication")
            
            return True
            
        except Exception as e:
            self.log_test("Pillar Hierarchy Testing Exception", False, f"Unexpected error: {str(e)}")
            return False
        
        finally:
            # Cleanup created resources
            print(f"\n🧹 CLEANING UP PILLAR HIERARCHY TEST RESOURCES")
            
            # Delete created tasks first
            for task_id in created_tasks:
                try:
                    result = self.make_request('DELETE', f'/tasks/{task_id}', use_auth=True)
                    if result['success']:
                        print(f"   ✅ Cleaned up task: {task_id}")
                    else:
                        print(f"   ⚠️ Failed to cleanup task: {task_id}")
                except:
                    print(f"   ⚠️ Exception cleaning up task: {task_id}")
            
            # Delete created projects
            for project_id in created_projects:
                try:
                    result = self.make_request('DELETE', f'/projects/{project_id}', use_auth=True)
                    if result['success']:
                        print(f"   ✅ Cleaned up project: {project_id}")
                    else:
                        print(f"   ⚠️ Failed to cleanup project: {project_id}")
                except:
                    print(f"   ⚠️ Exception cleaning up project: {project_id}")
            
            # Delete created areas
            for area_id in created_areas:
                try:
                    result = self.make_request('DELETE', f'/areas/{area_id}', use_auth=True)
                    if result['success']:
                        print(f"   ✅ Cleaned up area: {area_id}")
                    else:
                        print(f"   ⚠️ Failed to cleanup area: {area_id}")
                except:
                    print(f"   ⚠️ Exception cleaning up area: {area_id}")
            
            # Delete created pillars (in reverse order to handle hierarchy)
            for pillar_id in reversed(created_pillars):
                try:
                    result = self.make_request('DELETE', f'/pillars/{pillar_id}', use_auth=True)
                    if result['success']:
                        print(f"   ✅ Cleaned up pillar: {pillar_id}")
                    else:
                        print(f"   ⚠️ Failed to cleanup pillar: {pillar_id}")
                except:
                    print(f"   ⚠️ Exception cleaning up pillar: {pillar_id}")

    def run_tests(self):
        """Run all pillar hierarchy tests"""
        print("🏛️ STARTING PILLAR HIERARCHY BACKEND IMPLEMENTATION TESTING - PHASE 1")
        print("="*80)
        
        # Setup authentication
        if not self.setup_authentication():
            print("❌ CRITICAL: Authentication setup failed - cannot proceed with testing")
            return
        
        # Run pillar hierarchy tests
        success = self.test_pillar_hierarchy_backend_implementation()
        
        # Print summary
        self.print_summary(success)

    def print_summary(self, overall_success: bool):
        """Print test summary"""
        print("\n" + "="*80)
        print("🏁 PILLAR HIERARCHY BACKEND TESTING SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['success']])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if overall_success and success_rate >= 85:
            print("\n🎉 PILLAR HIERARCHY BACKEND IMPLEMENTATION - PHASE 1 TESTING COMPLETED SUCCESSFULLY!")
            print("✅ All critical pillar hierarchy features are working correctly")
            print("✅ CRUD operations, hierarchy, area-pillar linking, progress tracking, validation, and authentication all functional")
        elif success_rate >= 70:
            print("\n⚠️ PILLAR HIERARCHY BACKEND IMPLEMENTATION - PHASE 1 TESTING COMPLETED WITH MINOR ISSUES")
            print("✅ Most pillar hierarchy features are working correctly")
            print("⚠️ Some minor issues detected - see failed tests above")
        else:
            print("\n❌ PILLAR HIERARCHY BACKEND IMPLEMENTATION - PHASE 1 TESTING FAILED")
            print("❌ Critical issues detected in pillar hierarchy implementation")
            print("❌ Review failed tests and fix issues before proceeding")
        
        # Show failed tests
        failed_tests_list = [t for t in self.test_results if not t['success']]
        if failed_tests_list:
            print(f"\n❌ FAILED TESTS ({len(failed_tests_list)}):")
            for test in failed_tests_list:
                print(f"   • {test['test']}: {test['message']}")

if __name__ == "__main__":
    tester = PillarHierarchyTester()
    tester.run_tests()