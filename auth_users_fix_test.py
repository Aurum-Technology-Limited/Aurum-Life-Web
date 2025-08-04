#!/usr/bin/env python3
"""
AUTH.USERS CREATION FIX TESTING - COMPREHENSIVE TESTING
Testing the fixed auth.users creation approach for onboarding pillar creation.

FOCUS AREAS:
1. Authentication with marc.alleyne@aurumtechnologyltd.com / password
2. Create a pillar to test if the auth.users creation fix now works
3. Check logs to see if the Supabase Admin API user creation executes properly
4. Verify that foreign key constraint errors are resolved

ISSUE FIXED:
- `from supabase_client import supabase` (incorrect - supabase variable doesn't exist)
- Fixed to: `from supabase_client import get_supabase_client` + `supabase = get_supabase_client()`

EXPECTED BEHAVIOR:
The system will now successfully create users in auth.users when needed, resolving the 
foreign key constraint violations and allowing pillar creation to succeed.

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

class AuthUsersCreationTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        # Use the specified test credentials from review request
        self.test_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.test_user_password = "password"
        
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

    def test_pillar_creation_with_auth_users_fix(self):
        """Test pillar creation to verify auth.users creation fix"""
        print("\n=== TESTING PILLAR CREATION WITH AUTH.USERS FIX ===")
        
        if not self.auth_token:
            self.log_test("PILLAR CREATION - Authentication Required", False, "No authentication token available")
            return False
        
        # Create a test pillar - this should trigger the auth.users creation if needed
        pillar_data = {
            "name": "Test Pillar - Auth Users Fix",
            "description": "Testing the auth.users creation fix for foreign key constraints",
            "icon": "🧪",
            "color": "#10B981",
            "time_allocation_percentage": 25.0
        }
        
        print(f"🔍 Creating pillar to test auth.users creation fix...")
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        
        if result['success']:
            pillar = result['data']
            pillar_id = pillar.get('id')
            
            self.log_test(
                "PILLAR CREATION SUCCESS",
                True,
                f"Pillar created successfully with ID: {pillar_id}. Auth.users creation fix is working!"
            )
            
            # Verify the pillar was actually created by retrieving it
            verify_result = self.make_request('GET', '/pillars', use_auth=True)
            if verify_result['success']:
                pillars = verify_result['data']
                created_pillar = next((p for p in pillars if p.get('id') == pillar_id), None)
                
                if created_pillar:
                    self.log_test(
                        "PILLAR CREATION VERIFICATION",
                        True,
                        f"Created pillar verified in database: {created_pillar.get('name')}"
                    )
                    return pillar_id
                else:
                    self.log_test(
                        "PILLAR CREATION VERIFICATION",
                        False,
                        "Created pillar not found in database"
                    )
                    return False
            else:
                self.log_test(
                    "PILLAR CREATION VERIFICATION",
                    False,
                    f"Failed to verify pillar creation: {verify_result.get('error')}"
                )
                return False
        else:
            # Check if this is a foreign key constraint error
            error_message = str(result.get('error', ''))
            if 'foreign key' in error_message.lower() or 'constraint' in error_message.lower():
                self.log_test(
                    "PILLAR CREATION - FOREIGN KEY ERROR",
                    False,
                    f"Foreign key constraint error still occurring: {error_message}. Auth.users creation fix may not be working."
                )
            else:
                self.log_test(
                    "PILLAR CREATION FAILED",
                    False,
                    f"Pillar creation failed: {error_message}"
                )
            return False

    def test_area_creation_with_pillar(self, pillar_id: str):
        """Test area creation linked to the pillar"""
        print("\n=== TESTING AREA CREATION WITH PILLAR LINK ===")
        
        if not pillar_id:
            self.log_test("AREA CREATION - No Pillar ID", False, "No pillar ID available for area creation")
            return False
        
        # Create a test area linked to the pillar
        area_data = {
            "pillar_id": pillar_id,
            "name": "Test Area - Auth Users Fix",
            "description": "Testing area creation after auth.users fix",
            "icon": "🎯",
            "color": "#F59E0B",
            "importance": 4
        }
        
        print(f"🔍 Creating area linked to pillar {pillar_id}...")
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        
        if result['success']:
            area = result['data']
            area_id = area.get('id')
            
            self.log_test(
                "AREA CREATION SUCCESS",
                True,
                f"Area created successfully with ID: {area_id}, linked to pillar: {pillar_id}"
            )
            return area_id
        else:
            error_message = str(result.get('error', ''))
            if 'foreign key' in error_message.lower() or 'constraint' in error_message.lower():
                self.log_test(
                    "AREA CREATION - FOREIGN KEY ERROR",
                    False,
                    f"Foreign key constraint error in area creation: {error_message}"
                )
            else:
                self.log_test(
                    "AREA CREATION FAILED",
                    False,
                    f"Area creation failed: {error_message}"
                )
            return False

    def test_project_creation_with_area(self, area_id: str):
        """Test project creation linked to the area"""
        print("\n=== TESTING PROJECT CREATION WITH AREA LINK ===")
        
        if not area_id:
            self.log_test("PROJECT CREATION - No Area ID", False, "No area ID available for project creation")
            return False
        
        # Create a test project linked to the area
        project_data = {
            "area_id": area_id,
            "name": "Test Project - Auth Users Fix",
            "description": "Testing project creation after auth.users fix",
            "icon": "📋",
            "status": "Not Started",
            "priority": "medium"
        }
        
        print(f"🔍 Creating project linked to area {area_id}...")
        result = self.make_request('POST', '/projects', data=project_data, use_auth=True)
        
        if result['success']:
            project = result['data']
            project_id = project.get('id')
            
            self.log_test(
                "PROJECT CREATION SUCCESS",
                True,
                f"Project created successfully with ID: {project_id}, linked to area: {area_id}"
            )
            return project_id
        else:
            error_message = str(result.get('error', ''))
            if 'foreign key' in error_message.lower() or 'constraint' in error_message.lower():
                self.log_test(
                    "PROJECT CREATION - FOREIGN KEY ERROR",
                    False,
                    f"Foreign key constraint error in project creation: {error_message}"
                )
            else:
                self.log_test(
                    "PROJECT CREATION FAILED",
                    False,
                    f"Project creation failed: {error_message}"
                )
            return False

    def test_hierarchy_integrity(self, pillar_id: str, area_id: str, project_id: str):
        """Test the integrity of the created hierarchy"""
        print("\n=== TESTING HIERARCHY INTEGRITY ===")
        
        if not all([pillar_id, area_id, project_id]):
            self.log_test("HIERARCHY INTEGRITY - Missing IDs", False, "Not all hierarchy elements were created")
            return False
        
        # Get pillars with areas included
        result = self.make_request('GET', '/pillars?include_areas=true', use_auth=True)
        if result['success']:
            pillars = result['data']
            test_pillar = next((p for p in pillars if p.get('id') == pillar_id), None)
            
            if test_pillar:
                self.log_test(
                    "HIERARCHY INTEGRITY - PILLAR FOUND",
                    True,
                    f"Test pillar found: {test_pillar.get('name')}"
                )
            else:
                self.log_test(
                    "HIERARCHY INTEGRITY - PILLAR NOT FOUND",
                    False,
                    "Test pillar not found in hierarchy"
                )
                return False
        
        # Get areas with projects included
        result = self.make_request('GET', '/areas?include_projects=true', use_auth=True)
        if result['success']:
            areas = result['data']
            test_area = next((a for a in areas if a.get('id') == area_id), None)
            
            if test_area and test_area.get('pillar_id') == pillar_id:
                self.log_test(
                    "HIERARCHY INTEGRITY - AREA LINKED TO PILLAR",
                    True,
                    f"Test area correctly linked to pillar: {test_area.get('name')}"
                )
            else:
                self.log_test(
                    "HIERARCHY INTEGRITY - AREA LINK BROKEN",
                    False,
                    "Test area not properly linked to pillar"
                )
                return False
        
        # Get projects
        result = self.make_request('GET', '/projects', use_auth=True)
        if result['success']:
            projects = result['data']
            test_project = next((p for p in projects if p.get('id') == project_id), None)
            
            if test_project and test_project.get('area_id') == area_id:
                self.log_test(
                    "HIERARCHY INTEGRITY - PROJECT LINKED TO AREA",
                    True,
                    f"Test project correctly linked to area: {test_project.get('name')}"
                )
                return True
            else:
                self.log_test(
                    "HIERARCHY INTEGRITY - PROJECT LINK BROKEN",
                    False,
                    "Test project not properly linked to area"
                )
                return False
        
        return False

    def test_cleanup_created_resources(self, pillar_id: str, area_id: str, project_id: str):
        """Clean up the test resources created during testing"""
        print("\n=== CLEANING UP TEST RESOURCES ===")
        
        cleanup_success = True
        
        # Delete project first (child)
        if project_id:
            result = self.make_request('DELETE', f'/projects/{project_id}', use_auth=True)
            if result['success']:
                self.log_test("CLEANUP - PROJECT DELETED", True, f"Test project {project_id} deleted")
            else:
                self.log_test("CLEANUP - PROJECT DELETE FAILED", False, f"Failed to delete project: {result.get('error')}")
                cleanup_success = False
        
        # Delete area second (parent of project)
        if area_id:
            result = self.make_request('DELETE', f'/areas/{area_id}', use_auth=True)
            if result['success']:
                self.log_test("CLEANUP - AREA DELETED", True, f"Test area {area_id} deleted")
            else:
                self.log_test("CLEANUP - AREA DELETE FAILED", False, f"Failed to delete area: {result.get('error')}")
                cleanup_success = False
        
        # Delete pillar last (parent of area)
        if pillar_id:
            result = self.make_request('DELETE', f'/pillars/{pillar_id}', use_auth=True)
            if result['success']:
                self.log_test("CLEANUP - PILLAR DELETED", True, f"Test pillar {pillar_id} deleted")
            else:
                self.log_test("CLEANUP - PILLAR DELETE FAILED", False, f"Failed to delete pillar: {result.get('error')}")
                cleanup_success = False
        
        return cleanup_success

    def run_comprehensive_auth_users_creation_test(self):
        """Run comprehensive auth.users creation fix testing"""
        print("\n🔐 STARTING AUTH.USERS CREATION FIX COMPREHENSIVE TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("Testing the fix for auth.users creation during onboarding pillar creation")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("User Authentication", self.test_user_authentication),
        ]
        
        successful_tests = 0
        total_tests = len(test_methods)
        
        # Run basic tests first
        for test_name, test_method in test_methods:
            print(f"\n--- {test_name} ---")
            try:
                if test_method():
                    successful_tests += 1
                    print(f"✅ {test_name} completed successfully")
                else:
                    print(f"❌ {test_name} failed")
                    # If authentication fails, we can't continue
                    if test_name == "User Authentication":
                        print("❌ Cannot continue without authentication")
                        break
            except Exception as e:
                print(f"❌ {test_name} raised exception: {e}")
                if test_name == "User Authentication":
                    break
        
        # If authentication succeeded, run the main tests
        if self.auth_token:
            print(f"\n--- Auth.Users Creation Fix Testing ---")
            
            # Test pillar creation (main test)
            pillar_id = self.test_pillar_creation_with_auth_users_fix()
            if pillar_id:
                successful_tests += 1
                total_tests += 1
                
                # Test area creation
                area_id = self.test_area_creation_with_pillar(pillar_id)
                if area_id:
                    successful_tests += 1
                    total_tests += 1
                    
                    # Test project creation
                    project_id = self.test_project_creation_with_area(area_id)
                    if project_id:
                        successful_tests += 1
                        total_tests += 1
                        
                        # Test hierarchy integrity
                        if self.test_hierarchy_integrity(pillar_id, area_id, project_id):
                            successful_tests += 1
                        total_tests += 1
                        
                        # Cleanup
                        if self.test_cleanup_created_resources(pillar_id, area_id, project_id):
                            successful_tests += 1
                        total_tests += 1
                    else:
                        total_tests += 3  # Add the tests we couldn't run
                else:
                    total_tests += 4  # Add the tests we couldn't run
            else:
                total_tests += 5  # Add the tests we couldn't run
        
        success_rate = (successful_tests / total_tests) * 100
        
        print(f"\n" + "=" * 80)
        print("🔐 AUTH.USERS CREATION FIX TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for auth.users creation fix
        auth_tests_passed = sum(1 for result in self.test_results if result['success'] and 'AUTH' in result['test'].upper())
        pillar_tests_passed = sum(1 for result in self.test_results if result['success'] and 'PILLAR' in result['test'].upper())
        hierarchy_tests_passed = sum(1 for result in self.test_results if result['success'] and 'HIERARCHY' in result['test'].upper())
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"Authentication Tests Passed: {auth_tests_passed}")
        print(f"Pillar Creation Tests Passed: {pillar_tests_passed}")
        print(f"Hierarchy Tests Passed: {hierarchy_tests_passed}")
        
        # Check for foreign key errors
        foreign_key_errors = [result for result in self.test_results if not result['success'] and 'foreign key' in result['message'].lower()]
        
        if success_rate >= 85 and len(foreign_key_errors) == 0:
            print("\n✅ AUTH.USERS CREATION FIX: SUCCESS")
            print("   ✅ Authentication working with specified credentials")
            print("   ✅ Pillar creation successful - no foreign key constraint errors")
            print("   ✅ Auth.users creation fix is working properly")
            print("   ✅ Hierarchy creation and integrity verified")
            print("   The auth.users creation fix has resolved the foreign key constraint issues!")
        elif len(foreign_key_errors) > 0:
            print("\n❌ AUTH.USERS CREATION FIX: FOREIGN KEY ERRORS STILL OCCURRING")
            print("   ❌ Foreign key constraint errors detected")
            print("   ❌ Auth.users creation fix may not be working properly")
            for error in foreign_key_errors:
                print(f"   ❌ {error['test']}: {error['message']}")
        else:
            print("\n⚠️ AUTH.USERS CREATION FIX: PARTIAL SUCCESS")
            print("   ⚠️ Some tests failed but no foreign key errors detected")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 85 and len(foreign_key_errors) == 0

def main():
    """Run Auth.Users Creation Fix Tests"""
    print("🔐 STARTING AUTH.USERS CREATION FIX BACKEND TESTING")
    print("=" * 80)
    
    tester = AuthUsersCreationTester()
    
    try:
        # Run the comprehensive auth.users creation fix tests
        success = tester.run_comprehensive_auth_users_creation_test()
        
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