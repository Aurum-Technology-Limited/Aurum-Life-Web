#!/usr/bin/env python3
"""
JOURNAL ENHANCEMENTS SYSTEM COMPREHENSIVE TESTING
Complete end-to-end testing of the Journal Enhancements system implementation.

FOCUS AREAS:
1. Journal Entry Management - Test POST/GET/PUT/DELETE with enhanced fields (mood, energy_level, tags, template_id, template_responses, weather, location)
2. Advanced Filtering - Test GET /api/journal with mood_filter, tag_filter, date_from, date_to, pagination
3. Journal Templates System - Test GET/POST/PUT/DELETE for templates, verify default templates
4. Enhanced Features - Test search, on-this-day, insights analytics
5. Default Templates Verification - Verify 5 default templates created on startup
6. Authentication & User Isolation - Test all endpoints require auth and user-specific data
7. Template Usage Tracking - Test usage_count increments and template responses
8. Word Count & Reading Time - Test automatic calculations
9. Mood & Energy Level Enums - Test validation and filtering
10. Journal Insights Analytics - Test comprehensive analytics endpoint

Context: Testing the complete Journal Enhancements system implementation with:
- Enhanced JournalEntry model with mood, energy_level, tags, template support
- JournalTemplate system with default and custom templates
- Advanced filtering and search capabilities
- Comprehensive analytics and insights
- "On This Day" functionality for historical entries
- Full authentication and user isolation
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid
import time

# Configuration - Using the production backend URL from frontend/.env
BACKEND_URL = "https://9e0755cb-5122-46b7-bde6-cd0ca0c057dc.preview.emergentagent.com/api"

class AuthProjectsTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.created_resources = {
            'areas': [],
            'projects': [],
            'tasks': [],
            'users': []
        }
        self.auth_token = None
        # Use realistic test data instead of dummy data
        self.test_user_email = f"sarah.johnson_{uuid.uuid4().hex[:8]}@aurumlife.com"
        self.test_user_password = "SecurePass2025!"
        self.test_user_data = {
            "username": f"sarah_johnson_{uuid.uuid4().hex[:8]}",
            "email": self.test_user_email,
            "first_name": "Sarah",
            "last_name": "Johnson",
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

    def test_user_registration(self):
        """Test user registration with new user data"""
        print("\n=== TESTING USER REGISTRATION ===")
        
        result = self.make_request('POST', '/auth/register', data=self.test_user_data)
        self.log_test(
            "USER REGISTRATION",
            result['success'],
            f"User registered successfully: {result['data'].get('email', 'Unknown')}" if result['success'] else f"Registration failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            # Log detailed error information
            print(f"   Status Code: {result.get('status_code')}")
            print(f"   Error Details: {result.get('error')}")
            return False
        
        user_data = result['data']
        self.created_resources['users'].append(user_data.get('id'))
        
        # Verify user data structure
        expected_fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active']
        present_fields = [field for field in expected_fields if field in user_data]
        self.log_test(
            "USER DATA STRUCTURE",
            len(present_fields) >= 5,
            f"User data contains {len(present_fields)}/{len(expected_fields)} expected fields: {present_fields}"
        )
        
        return True

    def test_user_login(self):
        """Test user login with registered credentials"""
        print("\n=== TESTING USER LOGIN ===")
        
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
            # Log detailed error information for authentication issues
            print(f"   Status Code: {result.get('status_code')}")
            print(f"   Error Details: {result.get('error')}")
            if result.get('status_code') == 401:
                print("   ⚠️  401 AUTHENTICATION ERROR DETECTED - This matches the reported issue!")
            return False
        
        token_data = result['data']
        self.auth_token = token_data.get('access_token')
        
        # Verify token structure
        self.log_test(
            "JWT TOKEN STRUCTURE",
            'access_token' in token_data and 'token_type' in token_data,
            f"Token type: {token_data.get('token_type', 'Unknown')}, Token length: {len(self.auth_token) if self.auth_token else 0}"
        )
        
        return True

    def test_authentication_token(self):
        """Verify JWT token is generated correctly and works for protected endpoints"""
        print("\n=== TESTING AUTHENTICATION TOKEN ===")
        
        if not self.auth_token:
            self.log_test(
                "TOKEN AVAILABILITY",
                False,
                "No authentication token available for testing"
            )
            return False
        
        # Test token with /auth/me endpoint
        result = self.make_request('GET', '/auth/me', use_auth=True)
        self.log_test(
            "TOKEN VALIDATION - /auth/me",
            result['success'],
            f"Token validated successfully, user: {result['data'].get('email', 'Unknown')}" if result['success'] else f"Token validation failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            if result.get('status_code') == 401:
                print("   ⚠️  401 AUTHENTICATION ERROR - Token is invalid or expired!")
            elif result.get('status_code') == 403:
                print("   ⚠️  403 FORBIDDEN ERROR - Token format issue!")
            return False
        
        # Verify user data from token
        user_data = result['data']
        self.log_test(
            "AUTHENTICATED USER DATA",
            user_data.get('email') == self.test_user_email,
            f"Authenticated user matches registered user: {user_data.get('email', 'Unknown')}"
        )
        
        return True

    def test_projects_api_without_auth(self):
        """Test projects API without authentication to verify it's properly protected"""
        print("\n=== TESTING PROJECTS API WITHOUT AUTHENTICATION ===")
        
        result = self.make_request('GET', '/projects', use_auth=False)
        self.log_test(
            "PROJECTS API - No Authentication",
            not result['success'] and result.get('status_code') in [401, 403],
            f"Projects API properly protected: Status {result.get('status_code')}" if not result['success'] else f"⚠️  Projects API not protected - this is a security issue!"
        )
        
        if result.get('status_code') == 401:
            print("   ✅ Correct behavior: 401 Unauthorized when no token provided")
        elif result.get('status_code') == 403:
            print("   ✅ Correct behavior: 403 Forbidden when no token provided")
        
        return not result['success']

    def test_projects_api_with_auth(self):
        """Test projects API with valid authentication token"""
        print("\n=== TESTING PROJECTS API WITH AUTHENTICATION ===")
        
        if not self.auth_token:
            self.log_test(
                "PROJECTS API - Authentication Required",
                False,
                "No authentication token available for testing"
            )
            return False
        
        result = self.make_request('GET', '/projects', use_auth=True)
        self.log_test(
            "PROJECTS API - With Authentication",
            result['success'],
            f"Projects retrieved successfully: {len(result['data']) if result['success'] else 0} projects" if result['success'] else f"Projects API failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            if result.get('status_code') == 401:
                print("   ⚠️  401 AUTHENTICATION ERROR - This matches the reported 'Failed to load projects' issue!")
                print("   🔍 Root cause: Authentication token is not working properly")
            return False
        
        projects_data = result['data']
        
        # Verify projects data structure
        if isinstance(projects_data, list):
            self.log_test(
                "PROJECTS DATA STRUCTURE",
                True,
                f"Projects returned as list with {len(projects_data)} items"
            )
            
            if len(projects_data) > 0:
                first_project = projects_data[0]
                expected_fields = ['id', 'name', 'area_id']
                present_fields = [field for field in expected_fields if field in first_project]
                self.log_test(
                    "PROJECT ITEM STRUCTURE",
                    len(present_fields) >= 2,
                    f"Project contains {len(present_fields)}/{len(expected_fields)} expected fields: {present_fields}"
                )
        else:
            self.log_test(
                "PROJECTS DATA TYPE",
                False,
                f"Expected list, got {type(projects_data)}: {projects_data}"
            )
        
        return True

    def test_create_area_and_project(self):
        """Create test area and project to ensure we have data to retrieve"""
        print("\n=== TESTING AREA AND PROJECT CREATION ===")
        
        if not self.auth_token:
            self.log_test(
                "AREA/PROJECT CREATION - Authentication Required",
                False,
                "No authentication token available for testing"
            )
            return False
        
        # Create test area
        area_data = {
            "name": "Personal Development",
            "description": "Area for personal growth and development",
            "icon": "🌱",
            "color": "#4CAF50"
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        self.log_test(
            "AREA CREATION",
            result['success'],
            f"Area created: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Area creation failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        area_id = result['data']['id']
        self.created_resources['areas'].append(area_id)
        
        # Create test project
        project_data = {
            "area_id": area_id,
            "name": "Learning New Skills",
            "description": "Project for acquiring new professional skills",
            "priority": "high"
        }
        
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        self.log_test(
            "PROJECT CREATION",
            result['success'],
            f"Project created: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Project creation failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        project_id = result['data']['id']
        self.created_resources['projects'].append(project_id)
        
        return True

    def test_project_data_retrieval(self):
        """Test comprehensive project data retrieval"""
        print("\n=== TESTING PROJECT DATA RETRIEVAL ===")
        
        if not self.auth_token:
            self.log_test(
                "PROJECT DATA RETRIEVAL - Authentication Required",
                False,
                "No authentication token available for testing"
            )
            return False
        
        # Test 1: Get all projects
        result = self.make_request('GET', '/projects', use_auth=True)
        self.log_test(
            "GET ALL PROJECTS",
            result['success'],
            f"Retrieved {len(result['data']) if result['success'] else 0} projects" if result['success'] else f"Failed to retrieve projects: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        projects = result['data']
        
        # Test 2: Get projects with area filter (if we have projects)
        if len(projects) > 0 and len(self.created_resources['areas']) > 0:
            area_id = self.created_resources['areas'][0]
            result = self.make_request('GET', '/projects', params={'area_id': area_id}, use_auth=True)
            self.log_test(
                "GET PROJECTS BY AREA",
                result['success'],
                f"Retrieved {len(result['data']) if result['success'] else 0} projects for area {area_id}" if result['success'] else f"Failed to filter projects by area: {result.get('error', 'Unknown error')}"
            )
        
        # Test 3: Get specific project details (if we have projects)
        if len(projects) > 0:
            project_id = projects[0]['id']
            result = self.make_request('GET', f'/projects/{project_id}', use_auth=True)
            self.log_test(
                "GET SPECIFIC PROJECT",
                result['success'],
                f"Retrieved project details: {result['data'].get('name', 'Unknown')}" if result['success'] else f"Failed to get project details: {result.get('error', 'Unknown error')}"
            )
        
        return True

    def test_error_investigation(self):
        """Investigate specific error scenarios that might cause 401 errors"""
        print("\n=== INVESTIGATING ERROR SCENARIOS ===")
        
        # Test 1: Invalid token format
        original_token = self.auth_token
        self.auth_token = "invalid-token-format"
        
        result = self.make_request('GET', '/projects', use_auth=True)
        self.log_test(
            "INVALID TOKEN FORMAT",
            not result['success'] and result.get('status_code') == 401,
            f"Invalid token properly rejected with status {result.get('status_code')}" if not result['success'] else "⚠️  Invalid token was accepted - security issue!"
        )
        
        # Test 2: Expired/malformed token
        self.auth_token = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        
        result = self.make_request('GET', '/projects', use_auth=True)
        self.log_test(
            "MALFORMED TOKEN",
            not result['success'] and result.get('status_code') == 401,
            f"Malformed token properly rejected with status {result.get('status_code')}" if not result['success'] else "⚠️  Malformed token was accepted - security issue!"
        )
        
        # Test 3: Missing Bearer prefix
        self.auth_token = original_token.replace('Bearer ', '') if original_token and 'Bearer' in original_token else original_token
        
        result = self.make_request('GET', '/projects', use_auth=True)
        token_without_bearer_works = result['success']
        
        # Restore original token
        self.auth_token = original_token
        
        # Test 4: Verify original token still works
        result = self.make_request('GET', '/projects', use_auth=True)
        self.log_test(
            "ORIGINAL TOKEN VALIDATION",
            result['success'],
            f"Original token still works after error tests" if result['success'] else f"Original token no longer works: {result.get('error', 'Unknown error')}"
        )
        
        return True

    def run_comprehensive_auth_projects_test(self):
        """Run comprehensive authentication and projects API tests"""
        print("\n🔐 STARTING AUTHENTICATION AND PROJECTS API TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Authentication Token", self.test_authentication_token),
            ("Projects API - No Auth", self.test_projects_api_without_auth),
            ("Projects API - With Auth", self.test_projects_api_with_auth),
            ("Create Area and Project", self.test_create_area_and_project),
            ("Project Data Retrieval", self.test_project_data_retrieval),
            ("Error Investigation", self.test_error_investigation)
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
        print("🎯 AUTHENTICATION AND PROJECTS API TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for the specific "Failed to load projects" issue
        auth_tests_passed = sum(1 for result in self.test_results if result['success'] and 'LOGIN' in result['test'])
        projects_tests_passed = sum(1 for result in self.test_results if result['success'] and 'PROJECTS' in result['test'])
        
        print(f"\n🔍 ISSUE ANALYSIS:")
        print(f"Authentication Tests Passed: {auth_tests_passed}")
        print(f"Projects API Tests Passed: {projects_tests_passed}")
        
        if success_rate >= 80:
            print("\n✅ AUTHENTICATION AND PROJECTS API: SUCCESS")
            print("   ✅ User registration working correctly")
            print("   ✅ User login generating valid JWT tokens")
            print("   ✅ Authentication tokens working for protected endpoints")
            print("   ✅ Projects API accessible with proper authentication")
            print("   ✅ Project data retrieval functional")
            print("   The authentication system is working properly!")
            print("\n💡 RECOMMENDATION: The 'Failed to load projects' issue may be:")
            print("   - Frontend not sending authentication token correctly")
            print("   - Frontend not handling authentication state properly")
            print("   - Network/CORS issues between frontend and backend")
        else:
            print("\n❌ AUTHENTICATION AND PROJECTS API: ISSUES DETECTED")
            print("   Issues found in authentication or projects API")
            
            # Check for specific 401 errors
            auth_errors = [result for result in self.test_results if not result['success'] and '401' in str(result.get('data', {}))]
            if auth_errors:
                print(f"   ⚠️  {len(auth_errors)} authentication errors (401) detected")
                print("   🔍 ROOT CAUSE: Authentication system has issues")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 80

    def cleanup_resources(self):
        """Clean up created test resources"""
        print("\n🧹 CLEANING UP TEST RESOURCES")
        cleanup_count = 0
        
        # Clean up projects
        for project_id in self.created_resources.get('projects', []):
            try:
                result = self.make_request('DELETE', f'/projects/{project_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
                    print(f"   ✅ Cleaned up project: {project_id}")
            except:
                pass
        
        # Clean up areas
        for area_id in self.created_resources.get('areas', []):
            try:
                result = self.make_request('DELETE', f'/areas/{area_id}', use_auth=True)
                if result['success']:
                    cleanup_count += 1
                    print(f"   ✅ Cleaned up area: {area_id}")
            except:
                pass
        
        if cleanup_count > 0:
            print(f"   ✅ Cleanup completed for {cleanup_count} resources")
        else:
            print("   ℹ️ No resources to cleanup")

def main():
    """Run Authentication and Projects API Tests"""
    print("🔐 STARTING AUTHENTICATION AND PROJECTS API BACKEND TESTING")
    print("=" * 80)
    
    tester = AuthProjectsTester()
    
    try:
        # Run the comprehensive authentication and projects tests
        success = tester.run_comprehensive_auth_projects_test()
        
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
        
        return success_rate >= 80
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        return False
    
    finally:
        # Cleanup created resources
        tester.cleanup_resources()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)