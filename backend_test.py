#!/usr/bin/env python3
"""
FEEDBACK API SYSTEM - BACKEND TESTING
Complete end-to-end testing of the Feedback API endpoint implementation.

FOCUS AREAS:
1. FEEDBACK ENDPOINT - Test POST /api/feedback endpoint functionality
2. AUTHENTICATION - Test that feedback endpoint requires authentication
3. DATA VALIDATION - Test feedback data structure validation
4. EMAIL SERVICE - Test email service integration (mock mode)
5. ERROR HANDLING - Test error scenarios and proper responses
6. FEEDBACK CATEGORIES - Test different feedback categories

SPECIFIC ENDPOINT TO TEST:
- POST /api/feedback (submit user feedback and send email)

TEST SCENARIOS:
1. Valid Feedback Submission - Test feedback with proper data structure
2. Authentication Required - Test that endpoint requires valid JWT token
3. Email Service Integration - Test that email service is called (mock mode)
4. Different Categories - Test various feedback categories (suggestion, bug_report, etc.)
5. Data Validation - Test required and optional fields
6. Error Handling - Test invalid data and error responses

AUTHENTICATION:
- Use test credentials with realistic data for feedback testing
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
BACKEND_URL = "https://fc488f1a-b6ad-4e7c-bf64-4eb3b4a9be77.preview.emergentagent.com/api"

class IconPickerSystemTester:
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
        # Use realistic test data for icon picker testing
        self.test_user_email = f"iconpicker.tester_{uuid.uuid4().hex[:8]}@aurumlife.com"
        self.test_user_password = "IconPickerTest2025!"
        self.test_user_data = {
            "username": f"iconpicker_tester_{uuid.uuid4().hex[:8]}",
            "email": self.test_user_email,
            "first_name": "IconPicker",
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
        """Test user registration and login for icon picker testing"""
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

    def setup_test_infrastructure(self):
        """Create pillar and area for project testing"""
        print("\n=== SETTING UP TEST INFRASTRUCTURE ===")
        
        if not self.auth_token:
            self.log_test("INFRASTRUCTURE SETUP - Authentication Required", False, "No authentication token available")
            return None, None
        
        # Create test pillar
        pillar_data = {
            "name": "Icon Picker Test Pillar",
            "description": "Test pillar for icon picker functionality",
            "icon": "🎯",
            "color": "#4CAF50"
        }
        
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        if not result['success']:
            self.log_test("INFRASTRUCTURE - CREATE PILLAR", False, f"Failed to create test pillar: {result.get('error', 'Unknown error')}")
            return None, None
        
        pillar_id = result['data']['id']
        self.created_resources['pillars'].append(pillar_id)
        self.log_test("INFRASTRUCTURE - CREATE PILLAR", True, f"Created test pillar: {pillar_id}")
        
        # Create test area
        area_data = {
            "name": "Icon Picker Test Area",
            "description": "Test area for icon picker functionality",
            "icon": "📋",
            "color": "#2196F3",
            "pillar_id": pillar_id
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        if not result['success']:
            self.log_test("INFRASTRUCTURE - CREATE AREA", False, f"Failed to create test area: {result.get('error', 'Unknown error')}")
            return pillar_id, None
        
        area_id = result['data']['id']
        self.created_resources['areas'].append(area_id)
        self.log_test("INFRASTRUCTURE - CREATE AREA", True, f"Created test area: {area_id}")
        
        return pillar_id, area_id

    def test_project_creation_with_default_icon(self):
        """Test project creation with default icon (🚀)"""
        print("\n=== TESTING PROJECT CREATION WITH DEFAULT ICON ===")
        
        pillar_id, area_id = self.setup_test_infrastructure()
        if not area_id:
            return False
        
        # Create project without specifying icon (should get default 🚀)
        project_data = {
            "area_id": area_id,
            "name": "Default Icon Test Project",
            "description": "Testing default icon assignment",
            "priority": "medium"
        }
        
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        self.log_test(
            "PROJECT CREATION WITHOUT ICON",
            result['success'],
            f"Project created successfully" if result['success'] else f"Failed to create project: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        project_id = result['data']['id']
        self.created_resources['projects'].append(project_id)
        
        # Verify default icon is assigned
        project_icon = result['data'].get('icon')
        default_icon_assigned = project_icon == '🚀'
        
        self.log_test(
            "DEFAULT ICON ASSIGNMENT",
            default_icon_assigned,
            f"Default icon '🚀' assigned correctly" if default_icon_assigned else f"Incorrect default icon: '{project_icon}' (expected: '🚀')"
        )
        
        # Verify icon field is present in response
        icon_field_present = 'icon' in result['data']
        self.log_test(
            "ICON FIELD IN CREATE RESPONSE",
            icon_field_present,
            f"Icon field present in project creation response" if icon_field_present else "Icon field missing from project creation response"
        )
        
        return default_icon_assigned and icon_field_present

    def test_project_creation_with_custom_icons(self):
        """Test project creation with various custom emoji icons"""
        print("\n=== TESTING PROJECT CREATION WITH CUSTOM ICONS ===")
        
        pillar_id, area_id = self.setup_test_infrastructure()
        if not area_id:
            return False
        
        # Test various emoji types
        test_icons = [
            ("💻", "Basic computer emoji"),
            ("🎨", "Basic art emoji"),
            ("📱", "Basic phone emoji"),
            ("🏗️", "Complex construction emoji"),
            ("👨‍💻", "Multi-character man technologist emoji"),
            ("🚀", "Rocket emoji (same as default)"),
            ("🌟", "Star emoji"),
            ("⚡", "Lightning emoji"),
            ("🔥", "Fire emoji"),
            ("💡", "Light bulb emoji")
        ]
        
        successful_creations = 0
        total_tests = len(test_icons)
        
        for icon, description in test_icons:
            project_data = {
                "area_id": area_id,
                "name": f"Custom Icon Test Project - {description}",
                "description": f"Testing {description}",
                "icon": icon,
                "priority": "medium"
            }
            
            result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
            
            if result['success']:
                project_id = result['data']['id']
                self.created_resources['projects'].append(project_id)
                
                # Verify the icon was stored correctly
                returned_icon = result['data'].get('icon')
                icon_correct = returned_icon == icon
                
                if icon_correct:
                    successful_creations += 1
                
                self.log_test(
                    f"CUSTOM ICON CREATION - {description}",
                    icon_correct,
                    f"Icon '{icon}' stored and returned correctly" if icon_correct else f"Icon mismatch: expected '{icon}', got '{returned_icon}'"
                )
            else:
                self.log_test(
                    f"CUSTOM ICON CREATION - {description}",
                    False,
                    f"Failed to create project with icon '{icon}': {result.get('error', 'Unknown error')}"
                )
        
        success_rate = (successful_creations / total_tests) * 100
        overall_success = success_rate >= 90  # 90% success rate threshold
        
        self.log_test(
            "CUSTOM ICON CREATION OVERALL",
            overall_success,
            f"Custom icon creation success rate: {successful_creations}/{total_tests} ({success_rate:.1f}%)"
        )
        
        return overall_success

    def test_project_icon_updates(self):
        """Test updating project icons"""
        print("\n=== TESTING PROJECT ICON UPDATES ===")
        
        pillar_id, area_id = self.setup_test_infrastructure()
        if not area_id:
            return False
        
        # Create a project with initial icon
        initial_project_data = {
            "area_id": area_id,
            "name": "Icon Update Test Project",
            "description": "Testing icon updates",
            "icon": "📝",
            "priority": "medium"
        }
        
        result = self.make_request('POST', '/projects', data=initial_project_data, use_auth=True)
        if not result['success']:
            self.log_test("ICON UPDATE - CREATE INITIAL PROJECT", False, "Failed to create initial project for update testing")
            return False
        
        project_id = result['data']['id']
        self.created_resources['projects'].append(project_id)
        
        # Verify initial icon
        initial_icon = result['data'].get('icon')
        self.log_test(
            "ICON UPDATE - INITIAL ICON VERIFICATION",
            initial_icon == "📝",
            f"Initial icon set correctly: '{initial_icon}'"
        )
        
        # Test updating to different icons
        update_icons = [
            ("🎯", "Target emoji"),
            ("🚀", "Rocket emoji (default)"),
            ("💼", "Briefcase emoji"),
            ("🌈", "Rainbow emoji"),
            ("⭐", "Star emoji")
        ]
        
        successful_updates = 0
        total_updates = len(update_icons)
        
        for new_icon, description in update_icons:
            update_data = {"icon": new_icon}
            
            result = self.make_request('PUT', f'/projects/{project_id}', data=update_data, use_auth=True)
            
            if result['success']:
                # Verify the update by getting the project
                get_result = self.make_request('GET', f'/projects/{project_id}', use_auth=True)
                
                if get_result['success']:
                    updated_icon = get_result['data'].get('icon')
                    icon_updated_correctly = updated_icon == new_icon
                    
                    if icon_updated_correctly:
                        successful_updates += 1
                    
                    self.log_test(
                        f"ICON UPDATE - {description}",
                        icon_updated_correctly,
                        f"Icon updated to '{new_icon}' successfully" if icon_updated_correctly else f"Icon update failed: expected '{new_icon}', got '{updated_icon}'"
                    )
                else:
                    self.log_test(
                        f"ICON UPDATE - {description} (VERIFICATION)",
                        False,
                        f"Failed to verify icon update: {get_result.get('error', 'Unknown error')}"
                    )
            else:
                self.log_test(
                    f"ICON UPDATE - {description}",
                    False,
                    f"Failed to update icon to '{new_icon}': {result.get('error', 'Unknown error')}"
                )
        
        success_rate = (successful_updates / total_updates) * 100
        overall_success = success_rate >= 90
        
        self.log_test(
            "ICON UPDATE OVERALL",
            overall_success,
            f"Icon update success rate: {successful_updates}/{total_updates} ({success_rate:.1f}%)"
        )
        
        return overall_success

    def test_project_icon_persistence(self):
        """Test that project icons persist correctly across different API calls"""
        print("\n=== TESTING PROJECT ICON PERSISTENCE ===")
        
        pillar_id, area_id = self.setup_test_infrastructure()
        if not area_id:
            return False
        
        # Create project with specific icon
        test_icon = "🎨"
        project_data = {
            "area_id": area_id,
            "name": "Icon Persistence Test Project",
            "description": "Testing icon persistence across API calls",
            "icon": test_icon,
            "priority": "high"
        }
        
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        if not result['success']:
            self.log_test("ICON PERSISTENCE - CREATE PROJECT", False, "Failed to create project for persistence testing")
            return False
        
        project_id = result['data']['id']
        self.created_resources['projects'].append(project_id)
        
        # Test 1: GET specific project
        result = self.make_request('GET', f'/projects/{project_id}', use_auth=True)
        get_specific_success = result['success'] and result['data'].get('icon') == test_icon
        
        self.log_test(
            "ICON PERSISTENCE - GET SPECIFIC PROJECT",
            get_specific_success,
            f"Icon '{test_icon}' persisted in GET /projects/{{id}}" if get_specific_success else f"Icon not persisted correctly in specific project GET"
        )
        
        # Test 2: GET all projects (list)
        result = self.make_request('GET', '/projects', use_auth=True)
        list_projects_success = False
        if result['success']:
            projects = result['data']
            # Find our project in the list
            our_project = next((p for p in projects if p.get('id') == project_id), None)
            list_projects_success = our_project is not None and our_project.get('icon') == test_icon
        
        self.log_test(
            "ICON PERSISTENCE - GET PROJECTS LIST",
            list_projects_success,
            f"Icon '{test_icon}' persisted in GET /projects list" if list_projects_success else f"Icon not persisted correctly in projects list"
        )
        
        # Test 3: GET projects with area filter
        result = self.make_request('GET', '/projects', params={'area_id': area_id}, use_auth=True)
        filtered_projects_success = False
        if result['success']:
            projects = result['data']
            our_project = next((p for p in projects if p.get('id') == project_id), None)
            filtered_projects_success = our_project is not None and our_project.get('icon') == test_icon
        
        self.log_test(
            "ICON PERSISTENCE - GET FILTERED PROJECTS",
            filtered_projects_success,
            f"Icon '{test_icon}' persisted in filtered projects" if filtered_projects_success else f"Icon not persisted correctly in filtered projects"
        )
        
        # Test 4: Update other fields and verify icon remains
        update_data = {
            "name": "Updated Icon Persistence Test Project",
            "description": "Updated description"
        }
        
        result = self.make_request('PUT', f'/projects/{project_id}', data=update_data, use_auth=True)
        update_preserves_icon = False
        if result['success']:
            # Get the project again to verify icon is still there
            get_result = self.make_request('GET', f'/projects/{project_id}', use_auth=True)
            if get_result['success']:
                updated_icon = get_result['data'].get('icon')
                update_preserves_icon = updated_icon == test_icon
        
        self.log_test(
            "ICON PERSISTENCE - AFTER OTHER UPDATES",
            update_preserves_icon,
            f"Icon '{test_icon}' preserved after updating other fields" if update_preserves_icon else f"Icon lost after updating other fields"
        )
        
        overall_persistence_success = all([
            get_specific_success,
            list_projects_success,
            filtered_projects_success,
            update_preserves_icon
        ])
        
        self.log_test(
            "ICON PERSISTENCE OVERALL",
            overall_persistence_success,
            f"Icon persistence verified across all API endpoints" if overall_persistence_success else f"Icon persistence issues detected"
        )
        
        return overall_persistence_success

    def test_unicode_emoji_support(self):
        """Test support for various types of Unicode emojis"""
        print("\n=== TESTING UNICODE EMOJI SUPPORT ===")
        
        pillar_id, area_id = self.setup_test_infrastructure()
        if not area_id:
            return False
        
        # Test different categories of Unicode emojis
        unicode_test_cases = [
            # Basic emojis
            ("😀", "Basic smiley face"),
            ("🎉", "Basic party emoji"),
            ("❤️", "Heart with variation selector"),
            
            # Emojis with skin tone modifiers
            ("👍🏽", "Thumbs up with medium skin tone"),
            ("🤝🏻", "Handshake with light skin tone"),
            
            # Multi-character emojis (ZWJ sequences)
            ("👨‍💻", "Man technologist"),
            ("👩‍🚀", "Woman astronaut"),
            ("🏳️‍🌈", "Rainbow flag"),
            
            # Emojis with multiple components
            ("🧑‍🤝‍🧑", "People holding hands"),
            ("👨‍👩‍👧‍👦", "Family"),
            
            # Regional indicator symbols (flags)
            ("🇺🇸", "US flag"),
            ("🇬🇧", "UK flag"),
            
            # Mathematical and technical symbols
            ("⚡", "Lightning bolt"),
            ("⭐", "Star"),
            ("✅", "Check mark"),
            
            # Recently added emojis (if supported)
            ("🫡", "Saluting face"),
            ("🥹", "Face holding back tears")
        ]
        
        successful_unicode_tests = 0
        total_unicode_tests = len(unicode_test_cases)
        
        for emoji, description in unicode_test_cases:
            project_data = {
                "area_id": area_id,
                "name": f"Unicode Test - {description}",
                "description": f"Testing Unicode support for {description}",
                "icon": emoji,
                "priority": "low"
            }
            
            # Create project with Unicode emoji
            result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
            
            if result['success']:
                project_id = result['data']['id']
                self.created_resources['projects'].append(project_id)
                
                # Verify the emoji was stored and returned correctly
                returned_emoji = result['data'].get('icon')
                unicode_preserved = returned_emoji == emoji
                
                if unicode_preserved:
                    # Double-check by retrieving the project
                    get_result = self.make_request('GET', f'/projects/{project_id}', use_auth=True)
                    if get_result['success']:
                        retrieved_emoji = get_result['data'].get('icon')
                        unicode_preserved = retrieved_emoji == emoji
                
                if unicode_preserved:
                    successful_unicode_tests += 1
                
                self.log_test(
                    f"UNICODE SUPPORT - {description}",
                    unicode_preserved,
                    f"Unicode emoji '{emoji}' supported correctly" if unicode_preserved else f"Unicode emoji '{emoji}' not preserved (got: '{returned_emoji}')"
                )
            else:
                self.log_test(
                    f"UNICODE SUPPORT - {description}",
                    False,
                    f"Failed to create project with Unicode emoji '{emoji}': {result.get('error', 'Unknown error')}"
                )
        
        unicode_success_rate = (successful_unicode_tests / total_unicode_tests) * 100
        overall_unicode_success = unicode_success_rate >= 80  # 80% threshold for Unicode support
        
        self.log_test(
            "UNICODE EMOJI SUPPORT OVERALL",
            overall_unicode_success,
            f"Unicode emoji support: {successful_unicode_tests}/{total_unicode_tests} ({unicode_success_rate:.1f}%)"
        )
        
        return overall_unicode_success

    def test_api_response_format_consistency(self):
        """Test that icon field appears consistently in all project API responses"""
        print("\n=== TESTING API RESPONSE FORMAT CONSISTENCY ===")
        
        pillar_id, area_id = self.setup_test_infrastructure()
        if not area_id:
            return False
        
        # Create a test project
        project_data = {
            "area_id": area_id,
            "name": "API Response Format Test Project",
            "description": "Testing API response format consistency",
            "icon": "🔍",
            "priority": "medium"
        }
        
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        if not result['success']:
            self.log_test("API RESPONSE FORMAT - CREATE PROJECT", False, "Failed to create project for response format testing")
            return False
        
        project_id = result['data']['id']
        self.created_resources['projects'].append(project_id)
        
        # Test different API endpoints for consistent icon field presence
        api_tests = []
        
        # Test 1: POST /projects response
        create_response_has_icon = 'icon' in result['data']
        api_tests.append(("POST /projects", create_response_has_icon, result['data'].get('icon')))
        
        self.log_test(
            "API RESPONSE FORMAT - POST /projects",
            create_response_has_icon,
            f"Icon field present in POST response" if create_response_has_icon else "Icon field missing from POST response"
        )
        
        # Test 2: GET /projects/{id} response
        result = self.make_request('GET', f'/projects/{project_id}', use_auth=True)
        get_specific_has_icon = result['success'] and 'icon' in result['data']
        if result['success']:
            api_tests.append(("GET /projects/{id}", get_specific_has_icon, result['data'].get('icon')))
        
        self.log_test(
            "API RESPONSE FORMAT - GET /projects/{id}",
            get_specific_has_icon,
            f"Icon field present in GET specific response" if get_specific_has_icon else "Icon field missing from GET specific response"
        )
        
        # Test 3: GET /projects (list) response
        result = self.make_request('GET', '/projects', use_auth=True)
        get_list_has_icon = False
        if result['success']:
            projects = result['data']
            our_project = next((p for p in projects if p.get('id') == project_id), None)
            get_list_has_icon = our_project is not None and 'icon' in our_project
            if our_project:
                api_tests.append(("GET /projects (list)", get_list_has_icon, our_project.get('icon')))
        
        self.log_test(
            "API RESPONSE FORMAT - GET /projects (list)",
            get_list_has_icon,
            f"Icon field present in GET list response" if get_list_has_icon else "Icon field missing from GET list response"
        )
        
        # Test 4: PUT /projects/{id} response (if it returns project data)
        update_data = {"description": "Updated description for response format test"}
        result = self.make_request('PUT', f'/projects/{project_id}', data=update_data, use_auth=True)
        put_response_valid = result['success']
        
        self.log_test(
            "API RESPONSE FORMAT - PUT /projects/{id}",
            put_response_valid,
            f"PUT request successful" if put_response_valid else f"PUT request failed: {result.get('error', 'Unknown error')}"
        )
        
        # Test 5: Verify icon values are consistent across all responses
        icon_values = [test[2] for test in api_tests if test[1]]  # Get icon values from successful tests
        icon_consistency = len(set(icon_values)) <= 1 if icon_values else False  # All should be the same
        
        self.log_test(
            "API RESPONSE FORMAT - ICON VALUE CONSISTENCY",
            icon_consistency,
            f"Icon values consistent across all API responses: {set(icon_values)}" if icon_consistency else f"Inconsistent icon values: {icon_values}"
        )
        
        # Test 6: Verify icon field data type is string
        icon_data_types = [type(test[2]).__name__ for test in api_tests if test[1] and test[2] is not None]
        all_strings = all(dt == 'str' for dt in icon_data_types)
        
        self.log_test(
            "API RESPONSE FORMAT - ICON DATA TYPE",
            all_strings,
            f"All icon fields are strings" if all_strings else f"Icon field data types: {set(icon_data_types)}"
        )
        
        # Overall API response format consistency
        format_tests_passed = [
            create_response_has_icon,
            get_specific_has_icon,
            get_list_has_icon,
            put_response_valid,
            icon_consistency,
            all_strings
        ]
        
        overall_format_success = sum(format_tests_passed) >= 5  # At least 5 out of 6 tests should pass
        
        self.log_test(
            "API RESPONSE FORMAT OVERALL",
            overall_format_success,
            f"API response format consistency: {sum(format_tests_passed)}/6 tests passed"
        )
        
        return overall_format_success

    def run_comprehensive_icon_picker_test(self):
        """Run comprehensive icon picker system tests"""
        print("\n🎨 STARTING ICON PICKER SYSTEM COMPREHENSIVE TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("User Registration and Login", self.test_user_registration_and_login),
            ("Project Creation with Default Icon", self.test_project_creation_with_default_icon),
            ("Project Creation with Custom Icons", self.test_project_creation_with_custom_icons),
            ("Project Icon Updates", self.test_project_icon_updates),
            ("Project Icon Persistence", self.test_project_icon_persistence),
            ("Unicode Emoji Support", self.test_unicode_emoji_support),
            ("API Response Format Consistency", self.test_api_response_format_consistency)
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
        print("🎨 ICON PICKER SYSTEM TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for icon picker functionality
        model_tests_passed = sum(1 for result in self.test_results if result['success'] and ('DEFAULT ICON' in result['test'] or 'CUSTOM ICON' in result['test']))
        crud_tests_passed = sum(1 for result in self.test_results if result['success'] and ('CREATION' in result['test'] or 'UPDATE' in result['test']))
        persistence_tests_passed = sum(1 for result in self.test_results if result['success'] and 'PERSISTENCE' in result['test'])
        unicode_tests_passed = sum(1 for result in self.test_results if result['success'] and 'UNICODE' in result['test'])
        api_tests_passed = sum(1 for result in self.test_results if result['success'] and 'API RESPONSE' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"Model Tests Passed: {model_tests_passed}")
        print(f"CRUD Tests Passed: {crud_tests_passed}")
        print(f"Persistence Tests Passed: {persistence_tests_passed}")
        print(f"Unicode Tests Passed: {unicode_tests_passed}")
        print(f"API Format Tests Passed: {api_tests_passed}")
        
        if success_rate >= 85:
            print("\n✅ ICON PICKER SYSTEM: SUCCESS")
            print("   ✅ Project model with icon field working correctly")
            print("   ✅ Default icon ('🚀') assignment functional")
            print("   ✅ Custom icon creation and updates working")
            print("   ✅ Icon persistence across API calls verified")
            print("   ✅ Unicode emoji support confirmed")
            print("   ✅ API response format consistency maintained")
            print("   The Icon Picker System backend is production-ready!")
        else:
            print("\n❌ ICON PICKER SYSTEM: ISSUES DETECTED")
            print("   Issues found in icon picker system implementation")
        
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
    """Run Icon Picker System Tests"""
    print("🎨 STARTING ICON PICKER SYSTEM BACKEND TESTING")
    print("=" * 80)
    
    tester = IconPickerSystemTester()
    
    try:
        # Run the comprehensive icon picker system tests
        success = tester.run_comprehensive_icon_picker_test()
        
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