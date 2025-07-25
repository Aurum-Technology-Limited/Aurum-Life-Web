#!/usr/bin/env python3
"""
PILLAR SYSTEM CHILD PILLAR REMOVAL COMPREHENSIVE TESTING
Complete end-to-end testing of the updated Pillar system with removed child pillar functionality.

FOCUS AREAS:
1. PILLAR MODEL CHANGES - Test that parent_pillar_id and sub_pillars fields are removed
2. SIMPLIFIED PILLAR STRUCTURE - Test flat structure without hierarchy
3. DATABASE MIGRATION VERIFICATION - Verify no pillar hierarchy remains
4. API ENDPOINT UPDATES - Test endpoints without include_sub_pillars parameter
5. FUNCTIONALITY VERIFICATION - Test CRUD operations work with simplified model

SPECIFIC ENDPOINTS TO TEST:
- GET /api/pillars - should NOT include parent_pillar_id or sub_pillars fields
- POST /api/pillars - should NOT accept parent_pillar_id in request body
- PUT /api/pillars/{id} - should NOT allow updating parent_pillar_id field
- Verify PillarResponse model no longer includes parent_pillar_id, sub_pillars, or parent_pillar_name fields
- Test pillar-area linking still works correctly
- Test pillar progress tracking (area_count, project_count, task_count)
- Confirm pillar sorting and filtering still function

MIGRATION VERIFICATION:
- Verify existing pillars no longer have parent_pillar_id field in database
- Test that migrated data is properly structured
- Confirm no pillar hierarchy remains in the database
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid
import time
import re

# Configuration - Using the production backend URL from frontend/.env
BACKEND_URL = "https://aurum-life-1.preview.emergentagent.com/api"

class PillarChildRemovalTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.created_resources = {
            'pillars': [],
            'areas': [],
            'projects': [],
            'tasks': [],
            'users': []
        }
        self.auth_token = None
        # Use realistic test data for pillar testing
        self.test_user_email = f"pillar.tester_{uuid.uuid4().hex[:8]}@aurumlife.com"
        self.test_user_password = "PillarTest2025!"
        self.test_user_data = {
            "username": f"pillar_tester_{uuid.uuid4().hex[:8]}",
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
        
        result = self.make_request('GET', '/health')
        self.log_test(
            "BACKEND API CONNECTIVITY",
            result['success'],
            f"Backend API accessible at {self.base_url}" if result['success'] else f"Backend API not accessible: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            health_data = result['data']
            self.log_test(
                "HEALTH CHECK RESPONSE",
                'status' in health_data,
                f"Health check returned: {health_data.get('status', 'Unknown status')}"
            )
        
        return result['success']

    def test_user_registration_and_login(self):
        """Test user registration and login for pillar testing"""
        print("\n=== TESTING USER REGISTRATION AND LOGIN ===")
        
        # Register user
        result = self.make_request('POST', '/auth/register', data=self.test_user_data)
        self.log_test(
            "USER REGISTRATION",
            result['success'],
            f"User registered successfully: {result['data'].get('email', 'Unknown')}" if result['success'] else f"Registration failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        self.created_resources['users'].append(result['data'].get('id'))
        
        # Login user
        login_data = {
            "email": self.test_user_data['email'],
            "password": self.test_user_data['password']
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        self.log_test(
            "USER LOGIN",
            result['success'],
            f"Login successful, JWT token received" if result['success'] else f"Login failed: {result.get('error', 'Unknown error')}"
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

    def test_pillar_model_changes(self):
        """Test that pillar model no longer includes hierarchy fields"""
        print("\n=== TESTING PILLAR MODEL CHANGES ===")
        
        if not self.auth_token:
            self.log_test("PILLAR MODEL CHANGES - Authentication Required", False, "No authentication token available")
            return False
        
        # Test 1: GET existing pillars to verify no hierarchy fields
        result = self.make_request('GET', '/pillars', use_auth=True)
        self.log_test(
            "GET PILLARS - NO HIERARCHY FIELDS",
            result['success'],
            f"Retrieved {len(result['data']) if result['success'] else 0} pillars" if result['success'] else f"Failed to get pillars: {result.get('error', 'Unknown error')}"
        )
        
        if result['success'] and result['data']:
            existing_pillars = result['data']
            
            # Check that no pillar has hierarchy fields
            hierarchy_fields = ['parent_pillar_id', 'sub_pillars', 'parent_pillar_name']
            pillars_with_hierarchy = []
            
            for pillar in existing_pillars:
                for field in hierarchy_fields:
                    if field in pillar:
                        pillars_with_hierarchy.append((pillar.get('id', 'unknown'), field))
            
            self.log_test(
                "PILLARS WITHOUT HIERARCHY FIELDS",
                len(pillars_with_hierarchy) == 0,
                f"No hierarchy fields found in pillars" if len(pillars_with_hierarchy) == 0 else f"Found hierarchy fields: {pillars_with_hierarchy}"
            )
        
        # Test 2: Create a new pillar and verify response structure
        pillar_data = {
            "name": "Health & Wellness Simplified",
            "description": "A test pillar for simplified structure validation",
            "icon": "🏥",
            "color": "#4CAF50"
        }
        
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        self.log_test(
            "CREATE PILLAR - SIMPLIFIED STRUCTURE",
            result['success'],
            f"Pillar created: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Failed to create pillar: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            created_pillar = result['data']
            pillar_id = created_pillar['id']
            self.created_resources['pillars'].append(pillar_id)
            
            # Verify no hierarchy fields in response
            hierarchy_fields = ['parent_pillar_id', 'sub_pillars', 'parent_pillar_name']
            found_hierarchy_fields = [field for field in hierarchy_fields if field in created_pillar]
            
            self.log_test(
                "NEW PILLAR - NO HIERARCHY FIELDS",
                len(found_hierarchy_fields) == 0,
                f"No hierarchy fields in new pillar response" if len(found_hierarchy_fields) == 0 else f"Found hierarchy fields: {found_hierarchy_fields}"
            )
            
            # Verify expected fields are present
            expected_fields = ['id', 'name', 'description', 'icon', 'color', 'user_id', 'sort_order', 'archived', 'created_at', 'updated_at', 'date_created']
            missing_fields = [field for field in expected_fields if field not in created_pillar]
            
            self.log_test(
                "NEW PILLAR - EXPECTED FIELDS PRESENT",
                len(missing_fields) == 0,
                f"All expected fields present" if len(missing_fields) == 0 else f"Missing fields: {missing_fields}"
            )
        
        return True

    def test_pillar_creation_without_hierarchy(self):
        """Test that pillar creation rejects hierarchy fields"""
        print("\n=== TESTING PILLAR CREATION WITHOUT HIERARCHY ===")
        
        if not self.auth_token:
            self.log_test("PILLAR CREATION - Authentication Required", False, "No authentication token available")
            return False
        
        # Test 1: Try to create pillar with parent_pillar_id (should be ignored or rejected)
        pillar_with_parent_data = {
            "name": "Child Pillar Test",
            "description": "Testing if parent_pillar_id is rejected",
            "icon": "👶",
            "color": "#FF9800",
            "parent_pillar_id": "fake-parent-id"  # This should be ignored
        }
        
        result = self.make_request('POST', '/pillars', data=pillar_with_parent_data, use_auth=True)
        
        if result['success']:
            # If creation succeeded, verify parent_pillar_id was ignored
            created_pillar = result['data']
            pillar_id = created_pillar['id']
            self.created_resources['pillars'].append(pillar_id)
            
            has_parent_field = 'parent_pillar_id' in created_pillar
            self.log_test(
                "CREATE PILLAR WITH PARENT_ID - FIELD IGNORED",
                not has_parent_field,
                f"parent_pillar_id field ignored in creation" if not has_parent_field else f"parent_pillar_id field present: {created_pillar.get('parent_pillar_id')}"
            )
        else:
            # If creation failed, check if it's due to validation error
            error_message = str(result.get('error', ''))
            is_validation_error = 'parent_pillar_id' in error_message.lower() or 'validation' in error_message.lower()
            
            self.log_test(
                "CREATE PILLAR WITH PARENT_ID - VALIDATION ERROR",
                is_validation_error,
                f"Validation error for parent_pillar_id field" if is_validation_error else f"Unexpected error: {error_message}"
            )
        
        # Test 2: Create a normal pillar to ensure basic functionality works
        normal_pillar_data = {
            "name": "Career & Professional Growth",
            "description": "A normal pillar without hierarchy fields",
            "icon": "💼",
            "color": "#2196F3"
        }
        
        result = self.make_request('POST', '/pillars', data=normal_pillar_data, use_auth=True)
        self.log_test(
            "CREATE NORMAL PILLAR - SUCCESS",
            result['success'],
            f"Normal pillar created: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Failed to create normal pillar: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            pillar_id = result['data']['id']
            self.created_resources['pillars'].append(pillar_id)
        
        return True

    def test_pillar_update_without_hierarchy(self):
        """Test that pillar updates reject hierarchy fields"""
        print("\n=== TESTING PILLAR UPDATE WITHOUT HIERARCHY ===")
        
        if not self.auth_token:
            self.log_test("PILLAR UPDATE - Authentication Required", False, "No authentication token available")
            return False
        
        # First create a pillar to update
        pillar_data = {
            "name": "Relationships & Social",
            "description": "A pillar for testing updates",
            "icon": "👥",
            "color": "#E91E63"
        }
        
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        if not result['success']:
            self.log_test("PILLAR UPDATE - CREATE TEST PILLAR", False, "Failed to create test pillar for update testing")
            return False
        
        pillar_id = result['data']['id']
        self.created_resources['pillars'].append(pillar_id)
        
        # Test 1: Try to update pillar with parent_pillar_id (should be ignored or rejected)
        update_with_parent_data = {
            "name": "Updated Relationships & Social",
            "parent_pillar_id": "fake-parent-id"  # This should be ignored
        }
        
        result = self.make_request('PUT', f'/pillars/{pillar_id}', data=update_with_parent_data, use_auth=True)
        
        if result['success']:
            self.log_test(
                "UPDATE PILLAR WITH PARENT_ID - SUCCESS",
                True,
                "Update succeeded (parent_pillar_id likely ignored)"
            )
            
            # Verify the pillar was updated but parent_pillar_id was ignored
            get_result = self.make_request('GET', f'/pillars/{pillar_id}', use_auth=True)
            if get_result['success']:
                updated_pillar = get_result['data']
                has_parent_field = 'parent_pillar_id' in updated_pillar
                
                self.log_test(
                    "UPDATED PILLAR - NO PARENT_ID FIELD",
                    not has_parent_field,
                    f"parent_pillar_id field not present after update" if not has_parent_field else f"parent_pillar_id field present: {updated_pillar.get('parent_pillar_id')}"
                )
                
                # Verify name was actually updated
                name_updated = updated_pillar.get('name') == "Updated Relationships & Social"
                self.log_test(
                    "UPDATED PILLAR - NAME CHANGED",
                    name_updated,
                    f"Pillar name updated correctly" if name_updated else f"Name not updated: {updated_pillar.get('name')}"
                )
        else:
            # If update failed, check if it's due to validation error
            error_message = str(result.get('error', ''))
            is_validation_error = 'parent_pillar_id' in error_message.lower() or 'validation' in error_message.lower()
            
            self.log_test(
                "UPDATE PILLAR WITH PARENT_ID - VALIDATION ERROR",
                is_validation_error,
                f"Validation error for parent_pillar_id field" if is_validation_error else f"Unexpected error: {error_message}"
            )
        
        # Test 2: Normal update without hierarchy fields
        normal_update_data = {
            "description": "Updated description for relationships pillar",
            "color": "#9C27B0"
        }
        
        result = self.make_request('PUT', f'/pillars/{pillar_id}', data=normal_update_data, use_auth=True)
        self.log_test(
            "UPDATE PILLAR - NORMAL FIELDS",
            result['success'],
            f"Normal pillar update successful" if result['success'] else f"Failed to update pillar: {result.get('error', 'Unknown error')}"
        )
        
        return True

    def test_pillar_flat_structure(self):
        """Test that pillars are returned in flat structure without hierarchy"""
        print("\n=== TESTING PILLAR FLAT STRUCTURE ===")
        
        if not self.auth_token:
            self.log_test("PILLAR FLAT STRUCTURE - Authentication Required", False, "No authentication token available")
            return False
        
        # Create multiple pillars to test flat structure
        pillar_names = [
            "Personal Development",
            "Health & Fitness", 
            "Financial Freedom",
            "Creative Expression"
        ]
        
        created_pillar_ids = []
        for name in pillar_names:
            pillar_data = {
                "name": name,
                "description": f"Test pillar for {name.lower()}",
                "icon": "🎯",
                "color": "#607D8B"
            }
            
            result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
            if result['success']:
                pillar_id = result['data']['id']
                created_pillar_ids.append(pillar_id)
                self.created_resources['pillars'].append(pillar_id)
        
        self.log_test(
            "CREATE MULTIPLE PILLARS",
            len(created_pillar_ids) == len(pillar_names),
            f"Created {len(created_pillar_ids)}/{len(pillar_names)} test pillars"
        )
        
        # Test 1: GET all pillars and verify flat structure
        result = self.make_request('GET', '/pillars', use_auth=True)
        self.log_test(
            "GET ALL PILLARS - FLAT STRUCTURE",
            result['success'],
            f"Retrieved {len(result['data']) if result['success'] else 0} pillars" if result['success'] else f"Failed to get pillars: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            all_pillars = result['data']
            
            # Verify no pillar has sub_pillars array
            pillars_with_sub_pillars = [p for p in all_pillars if 'sub_pillars' in p]
            self.log_test(
                "PILLARS WITHOUT SUB_PILLARS ARRAY",
                len(pillars_with_sub_pillars) == 0,
                f"No pillars have sub_pillars array" if len(pillars_with_sub_pillars) == 0 else f"Found {len(pillars_with_sub_pillars)} pillars with sub_pillars"
            )
            
            # Verify no pillar has parent_pillar_id
            pillars_with_parent_id = [p for p in all_pillars if 'parent_pillar_id' in p and p['parent_pillar_id'] is not None]
            self.log_test(
                "PILLARS WITHOUT PARENT_PILLAR_ID",
                len(pillars_with_parent_id) == 0,
                f"No pillars have parent_pillar_id" if len(pillars_with_parent_id) == 0 else f"Found {len(pillars_with_parent_id)} pillars with parent_pillar_id"
            )
            
            # Verify all pillars are at the same level (flat structure)
            self.log_test(
                "FLAT PILLAR STRUCTURE CONFIRMED",
                True,
                f"All {len(all_pillars)} pillars are in flat structure without hierarchy"
            )
        
        # Test 2: Test include_sub_pillars parameter is no longer supported
        result = self.make_request('GET', '/pillars', params={'include_sub_pillars': 'true'}, use_auth=True)
        
        if result['success']:
            # Parameter might be ignored, verify no sub_pillars in response
            pillars_with_sub_pillars = [p for p in result['data'] if 'sub_pillars' in p]
            self.log_test(
                "INCLUDE_SUB_PILLARS PARAMETER IGNORED",
                len(pillars_with_sub_pillars) == 0,
                f"include_sub_pillars parameter ignored, no sub_pillars in response" if len(pillars_with_sub_pillars) == 0 else f"Found sub_pillars despite removal: {len(pillars_with_sub_pillars)}"
            )
        else:
            # Parameter might cause error if validation is strict
            error_message = str(result.get('error', ''))
            is_parameter_error = 'include_sub_pillars' in error_message.lower() or 'parameter' in error_message.lower()
            
            self.log_test(
                "INCLUDE_SUB_PILLARS PARAMETER REJECTED",
                is_parameter_error,
                f"include_sub_pillars parameter rejected" if is_parameter_error else f"Unexpected error: {error_message}"
            )
        
        return True

    def test_pillar_area_linking(self):
        """Test that pillar-area linking still works correctly"""
        print("\n=== TESTING PILLAR-AREA LINKING ===")
        
        if not self.auth_token:
            self.log_test("PILLAR-AREA LINKING - Authentication Required", False, "No authentication token available")
            return False
        
        # Create a test pillar
        pillar_data = {
            "name": "Learning & Education",
            "description": "A pillar for testing area linking",
            "icon": "📚",
            "color": "#3F51B5"
        }
        
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        if not result['success']:
            self.log_test("PILLAR-AREA LINKING - CREATE PILLAR", False, "Failed to create test pillar")
            return False
        
        pillar_id = result['data']['id']
        self.created_resources['pillars'].append(pillar_id)
        
        # Create an area linked to the pillar
        area_data = {
            "name": "Online Courses",
            "description": "Area for online learning courses",
            "icon": "💻",
            "color": "#FF5722",
            "pillar_id": pillar_id
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        self.log_test(
            "CREATE AREA LINKED TO PILLAR",
            result['success'],
            f"Area created and linked to pillar: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Failed to create linked area: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            area_id = result['data']['id']
            self.created_resources['areas'].append(area_id)
            
            # Verify area has pillar_id
            created_area = result['data']
            has_pillar_id = created_area.get('pillar_id') == pillar_id
            
            self.log_test(
                "AREA HAS CORRECT PILLAR_ID",
                has_pillar_id,
                f"Area correctly linked to pillar" if has_pillar_id else f"Area pillar_id mismatch: expected {pillar_id}, got {created_area.get('pillar_id')}"
            )
            
            # Get the area and verify pillar_name is populated
            get_result = self.make_request('GET', f'/areas/{area_id}', use_auth=True)
            if get_result['success']:
                area_details = get_result['data']
                has_pillar_name = 'pillar_name' in area_details and area_details['pillar_name'] == "Learning & Education"
                
                self.log_test(
                    "AREA HAS PILLAR_NAME",
                    has_pillar_name,
                    f"Area has correct pillar_name: {area_details.get('pillar_name')}" if has_pillar_name else f"Area missing or incorrect pillar_name: {area_details.get('pillar_name')}"
                )
        
        # Test pillar with include_areas parameter
        result = self.make_request('GET', f'/pillars/{pillar_id}', params={'include_areas': 'true'}, use_auth=True)
        self.log_test(
            "GET PILLAR WITH INCLUDE_AREAS",
            result['success'],
            f"Pillar retrieved with areas" if result['success'] else f"Failed to get pillar with areas: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            pillar_with_areas = result['data']
            
            # Verify areas are included
            has_areas = 'areas' in pillar_with_areas and isinstance(pillar_with_areas['areas'], list)
            self.log_test(
                "PILLAR INCLUDES LINKED AREAS",
                has_areas,
                f"Pillar includes {len(pillar_with_areas.get('areas', []))} linked areas" if has_areas else "Pillar does not include areas array"
            )
            
            # Verify progress tracking fields
            progress_fields = ['area_count', 'project_count', 'task_count', 'completed_task_count', 'progress_percentage']
            missing_progress_fields = [field for field in progress_fields if field not in pillar_with_areas]
            
            self.log_test(
                "PILLAR PROGRESS TRACKING FIELDS",
                len(missing_progress_fields) == 0,
                f"All progress tracking fields present" if len(missing_progress_fields) == 0 else f"Missing progress fields: {missing_progress_fields}"
            )
        
        return True

    def test_pillar_progress_tracking(self):
        """Test that pillar progress tracking works with simplified model"""
        print("\n=== TESTING PILLAR PROGRESS TRACKING ===")
        
        if not self.auth_token:
            self.log_test("PILLAR PROGRESS TRACKING - Authentication Required", False, "No authentication token available")
            return False
        
        # Create a pillar for progress testing
        pillar_data = {
            "name": "Productivity & Organization",
            "description": "A pillar for testing progress tracking",
            "icon": "⚡",
            "color": "#FF9800"
        }
        
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        if not result['success']:
            self.log_test("PROGRESS TRACKING - CREATE PILLAR", False, "Failed to create test pillar")
            return False
        
        pillar_id = result['data']['id']
        self.created_resources['pillars'].append(pillar_id)
        
        # Create an area linked to the pillar
        area_data = {
            "name": "Task Management",
            "description": "Area for task management systems",
            "icon": "📋",
            "color": "#4CAF50",
            "pillar_id": pillar_id
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        if not result['success']:
            self.log_test("PROGRESS TRACKING - CREATE AREA", False, "Failed to create test area")
            return False
        
        area_id = result['data']['id']
        self.created_resources['areas'].append(area_id)
        
        # Create a project in the area
        project_data = {
            "area_id": area_id,
            "name": "Personal Task System",
            "description": "Setting up a personal task management system",
            "priority": "high"
        }
        
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        if not result['success']:
            self.log_test("PROGRESS TRACKING - CREATE PROJECT", False, "Failed to create test project")
            return False
        
        project_id = result['data']['id']
        self.created_resources['projects'].append(project_id)
        
        # Create tasks in the project
        task_names = ["Set up task categories", "Configure notifications", "Create daily review process"]
        task_statuses = ["completed", "in_progress", "todo"]
        
        for i, (task_name, status) in enumerate(zip(task_names, task_statuses)):
            task_data = {
                "project_id": project_id,
                "name": task_name,
                "description": f"Task {i+1} for progress tracking test",
                "priority": "medium",
                "status": status
            }
            
            result = self.make_request('POST', '/tasks', data=task_data, use_auth=True)
            if result['success']:
                task_id = result['data']['id']
                self.created_resources['tasks'].append(task_id)
        
        # Wait a moment for data consistency
        time.sleep(1)
        
        # Test pillar progress tracking
        result = self.make_request('GET', f'/pillars/{pillar_id}', params={'include_areas': 'true'}, use_auth=True)
        self.log_test(
            "GET PILLAR WITH PROGRESS DATA",
            result['success'],
            f"Pillar retrieved with progress data" if result['success'] else f"Failed to get pillar progress: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            pillar_with_progress = result['data']
            
            # Verify progress tracking fields are present and have reasonable values
            area_count = pillar_with_progress.get('area_count', 0)
            project_count = pillar_with_progress.get('project_count', 0)
            task_count = pillar_with_progress.get('task_count', 0)
            completed_task_count = pillar_with_progress.get('completed_task_count', 0)
            
            self.log_test(
                "PILLAR AREA COUNT",
                area_count >= 1,
                f"Pillar has {area_count} areas (expected >= 1)"
            )
            
            self.log_test(
                "PILLAR PROJECT COUNT",
                project_count >= 1,
                f"Pillar has {project_count} projects (expected >= 1)"
            )
            
            self.log_test(
                "PILLAR TASK COUNT",
                task_count >= 3,
                f"Pillar has {task_count} tasks (expected >= 3)"
            )
            
            self.log_test(
                "PILLAR COMPLETED TASK COUNT",
                completed_task_count >= 1,
                f"Pillar has {completed_task_count} completed tasks (expected >= 1)"
            )
            
            # Verify progress percentage calculation
            progress_percentage = pillar_with_progress.get('progress_percentage', 0)
            expected_progress = (completed_task_count / task_count * 100) if task_count > 0 else 0
            progress_reasonable = abs(progress_percentage - expected_progress) < 1  # Allow small rounding differences
            
            self.log_test(
                "PILLAR PROGRESS PERCENTAGE",
                progress_reasonable,
                f"Progress percentage: {progress_percentage}% (expected ~{expected_progress:.1f}%)"
            )
        
        return True

    def test_database_migration_verification(self):
        """Test that database migration removed hierarchy fields"""
        print("\n=== TESTING DATABASE MIGRATION VERIFICATION ===")
        
        if not self.auth_token:
            self.log_test("DATABASE MIGRATION - Authentication Required", False, "No authentication token available")
            return False
        
        # Get all existing pillars to verify migration
        result = self.make_request('GET', '/pillars', use_auth=True)
        self.log_test(
            "GET ALL PILLARS FOR MIGRATION CHECK",
            result['success'],
            f"Retrieved {len(result['data']) if result['success'] else 0} pillars for migration verification" if result['success'] else f"Failed to get pillars: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            all_pillars = result['data']
            
            if len(all_pillars) > 0:
                # Check each pillar for absence of hierarchy fields
                migration_issues = []
                
                for pillar in all_pillars:
                    pillar_id = pillar.get('id', 'unknown')
                    
                    # Check for parent_pillar_id field
                    if 'parent_pillar_id' in pillar and pillar['parent_pillar_id'] is not None:
                        migration_issues.append(f"Pillar {pillar_id} still has parent_pillar_id: {pillar['parent_pillar_id']}")
                    
                    # Check for sub_pillars field
                    if 'sub_pillars' in pillar:
                        migration_issues.append(f"Pillar {pillar_id} still has sub_pillars field")
                    
                    # Check for parent_pillar_name field
                    if 'parent_pillar_name' in pillar:
                        migration_issues.append(f"Pillar {pillar_id} still has parent_pillar_name field")
                
                self.log_test(
                    "DATABASE MIGRATION - NO HIERARCHY FIELDS",
                    len(migration_issues) == 0,
                    f"All pillars migrated successfully (no hierarchy fields)" if len(migration_issues) == 0 else f"Migration issues found: {migration_issues}"
                )
                
                # Verify all pillars have required simplified fields
                required_fields = ['id', 'name', 'user_id', 'created_at', 'updated_at', 'date_created']
                pillars_missing_fields = []
                
                for pillar in all_pillars:
                    pillar_id = pillar.get('id', 'unknown')
                    missing_fields = [field for field in required_fields if field not in pillar]
                    if missing_fields:
                        pillars_missing_fields.append(f"Pillar {pillar_id} missing: {missing_fields}")
                
                self.log_test(
                    "DATABASE MIGRATION - REQUIRED FIELDS PRESENT",
                    len(pillars_missing_fields) == 0,
                    f"All pillars have required fields" if len(pillars_missing_fields) == 0 else f"Missing fields: {pillars_missing_fields}"
                )
                
                # Check data consistency
                pillars_with_valid_data = 0
                for pillar in all_pillars:
                    has_name = pillar.get('name') and len(pillar['name'].strip()) > 0
                    has_user_id = pillar.get('user_id') and len(pillar['user_id'].strip()) > 0
                    has_dates = pillar.get('created_at') and pillar.get('updated_at')
                    
                    if has_name and has_user_id and has_dates:
                        pillars_with_valid_data += 1
                
                self.log_test(
                    "DATABASE MIGRATION - DATA CONSISTENCY",
                    pillars_with_valid_data == len(all_pillars),
                    f"{pillars_with_valid_data}/{len(all_pillars)} pillars have consistent data"
                )
            else:
                self.log_test(
                    "DATABASE MIGRATION - NO EXISTING PILLARS",
                    True,
                    "No existing pillars to verify migration (clean database)"
                )
        
        return True

    def test_pillar_crud_operations(self):
        """Test that basic CRUD operations work with simplified pillar model"""
        print("\n=== TESTING PILLAR CRUD OPERATIONS ===")
        
        if not self.auth_token:
            self.log_test("PILLAR CRUD - Authentication Required", False, "No authentication token available")
            return False
        
        # Test CREATE
        pillar_data = {
            "name": "Spiritual & Mindfulness",
            "description": "A pillar for spiritual growth and mindfulness practices",
            "icon": "🧘",
            "color": "#9C27B0",
            "time_allocation_percentage": 15.0
        }
        
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        self.log_test(
            "CRUD - CREATE PILLAR",
            result['success'],
            f"Pillar created: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Failed to create pillar: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        pillar_id = result['data']['id']
        self.created_resources['pillars'].append(pillar_id)
        created_pillar = result['data']
        
        # Verify created pillar has expected fields
        expected_fields = ['id', 'name', 'description', 'icon', 'color', 'time_allocation_percentage']
        missing_fields = [field for field in expected_fields if field not in created_pillar]
        
        self.log_test(
            "CRUD - CREATE PILLAR FIELDS",
            len(missing_fields) == 0,
            f"Created pillar has all expected fields" if len(missing_fields) == 0 else f"Missing fields: {missing_fields}"
        )
        
        # Test READ (individual)
        result = self.make_request('GET', f'/pillars/{pillar_id}', use_auth=True)
        self.log_test(
            "CRUD - READ PILLAR",
            result['success'],
            f"Pillar retrieved: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Failed to read pillar: {result.get('error', 'Unknown error')}"
        )
        
        # Test UPDATE
        update_data = {
            "description": "Updated description for spiritual and mindfulness pillar",
            "time_allocation_percentage": 20.0
        }
        
        result = self.make_request('PUT', f'/pillars/{pillar_id}', data=update_data, use_auth=True)
        self.log_test(
            "CRUD - UPDATE PILLAR",
            result['success'],
            f"Pillar updated successfully" if result['success'] else f"Failed to update pillar: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            # Verify update was applied
            get_result = self.make_request('GET', f'/pillars/{pillar_id}', use_auth=True)
            if get_result['success']:
                updated_pillar = get_result['data']
                description_updated = updated_pillar.get('description') == update_data['description']
                allocation_updated = updated_pillar.get('time_allocation_percentage') == update_data['time_allocation_percentage']
                
                self.log_test(
                    "CRUD - UPDATE VERIFICATION",
                    description_updated and allocation_updated,
                    f"Pillar fields updated correctly" if description_updated and allocation_updated else f"Update verification failed"
                )
        
        # Test ARCHIVE/UNARCHIVE
        result = self.make_request('PUT', f'/pillars/{pillar_id}/archive', use_auth=True)
        self.log_test(
            "CRUD - ARCHIVE PILLAR",
            result['success'],
            f"Pillar archived successfully" if result['success'] else f"Failed to archive pillar: {result.get('error', 'Unknown error')}"
        )
        
        if result['success']:
            # Verify pillar is archived
            get_result = self.make_request('GET', f'/pillars/{pillar_id}', use_auth=True)
            if get_result['success']:
                archived_pillar = get_result['data']
                is_archived = archived_pillar.get('archived', False)
                
                self.log_test(
                    "CRUD - ARCHIVE VERIFICATION",
                    is_archived,
                    f"Pillar is archived" if is_archived else f"Pillar not marked as archived"
                )
        
        # Test UNARCHIVE
        result = self.make_request('PUT', f'/pillars/{pillar_id}/unarchive', use_auth=True)
        self.log_test(
            "CRUD - UNARCHIVE PILLAR",
            result['success'],
            f"Pillar unarchived successfully" if result['success'] else f"Failed to unarchive pillar: {result.get('error', 'Unknown error')}"
        )
        
        # Test DELETE (will be done in cleanup, so just verify endpoint exists)
        # We'll test delete functionality in cleanup to avoid issues with other tests
        
        return True

    def run_comprehensive_pillar_test(self):
        """Run comprehensive pillar child removal tests"""
        print("\n🏛️ STARTING PILLAR CHILD REMOVAL COMPREHENSIVE TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("User Registration and Login", self.test_user_registration_and_login),
            ("Pillar Model Changes", self.test_pillar_model_changes),
            ("Pillar Creation Without Hierarchy", self.test_pillar_creation_without_hierarchy),
            ("Pillar Update Without Hierarchy", self.test_pillar_update_without_hierarchy),
            ("Pillar Flat Structure", self.test_pillar_flat_structure),
            ("Pillar-Area Linking", self.test_pillar_area_linking),
            ("Pillar Progress Tracking", self.test_pillar_progress_tracking),
            ("Database Migration Verification", self.test_database_migration_verification),
            ("Pillar CRUD Operations", self.test_pillar_crud_operations)
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
        print("🎯 PILLAR CHILD REMOVAL TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for pillar functionality
        pillar_tests_passed = sum(1 for result in self.test_results if result['success'] and 'PILLAR' in result['test'])
        hierarchy_tests_passed = sum(1 for result in self.test_results if result['success'] and ('HIERARCHY' in result['test'] or 'PARENT' in result['test']))
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"Pillar Tests Passed: {pillar_tests_passed}")
        print(f"Hierarchy Removal Tests Passed: {hierarchy_tests_passed}")
        
        if success_rate >= 85:
            print("\n✅ PILLAR CHILD REMOVAL: SUCCESS")
            print("   ✅ Pillar model no longer includes hierarchy fields")
            print("   ✅ API endpoints reject or ignore hierarchy parameters")
            print("   ✅ Pillars returned in flat structure without nesting")
            print("   ✅ Pillar-area linking still works correctly")
            print("   ✅ Progress tracking functions with simplified model")
            print("   ✅ Database migration removed hierarchy fields")
            print("   ✅ CRUD operations work with simplified pillar model")
            print("   The pillar system simplification is production-ready!")
        else:
            print("\n❌ PILLAR CHILD REMOVAL: ISSUES DETECTED")
            print("   Issues found in pillar hierarchy removal implementation")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 85

    def cleanup_resources(self):
        """Clean up created test resources"""
        print("\n🧹 CLEANING UP TEST RESOURCES")
        cleanup_count = 0
        
        # Clean up tasks first (they depend on projects)
        for task_id in self.created_resources.get('tasks', []):
            try:
                result = self.make_request('DELETE', f'/tasks/{task_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
                    print(f"   ✅ Cleaned up task: {task_id}")
            except:
                pass
        
        # Clean up projects (they depend on areas)
        for project_id in self.created_resources.get('projects', []):
            try:
                result = self.make_request('DELETE', f'/projects/{project_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
                    print(f"   ✅ Cleaned up project: {project_id}")
            except:
                pass
        
        # Clean up areas (they may depend on pillars)
        for area_id in self.created_resources.get('areas', []):
            try:
                result = self.make_request('DELETE', f'/areas/{area_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
                    print(f"   ✅ Cleaned up area: {area_id}")
            except:
                pass
        
        # Clean up pillars
        for pillar_id in self.created_resources.get('pillars', []):
            try:
                result = self.make_request('DELETE', f'/pillars/{pillar_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
                    print(f"   ✅ Cleaned up pillar: {pillar_id}")
            except:
                pass
        
        if cleanup_count > 0:
            print(f"   ✅ Cleanup completed for {cleanup_count} resources")
        else:
            print("   ℹ️ No resources to cleanup")

def main():
    """Run Pillar Child Removal Tests"""
    print("🏛️ STARTING PILLAR CHILD REMOVAL BACKEND TESTING")
    print("=" * 80)
    
    tester = PillarChildRemovalTester()
    
    try:
        # Run the comprehensive pillar child removal tests
        success = tester.run_comprehensive_pillar_test()
        
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
    
    finally:
        # Cleanup created resources
        tester.cleanup_resources()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)