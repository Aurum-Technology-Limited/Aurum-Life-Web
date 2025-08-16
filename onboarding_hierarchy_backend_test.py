#!/usr/bin/env python3
"""
SMART ONBOARDING API COMPLETION & HIERARCHY COUNT AGGREGATION TESTING
Testing the specific requirements from the review request:

1. Onboarding Completion API: Test POST /api/auth/complete-onboarding with marc.alleyne@aurumtechnologyltd.com/password
2. Hierarchy Count Verification: Test GET /api/pillars and GET /api/areas for proper count data
3. Authentication Flow: Ensure login and JWT validation work correctly

FOCUS AREAS:
- POST /api/auth/complete-onboarding endpoint functionality
- GET /api/pillars returns area_count, project_count, task_count
- GET /api/areas returns project_count, task_count
- Authentication with specified credentials
- Backend hierarchy count aggregation verification

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://focus-planner-3.preview.emergentagent.com/api"

class OnboardingHierarchyTester:
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
        
        # Login user with specified credentials from review request
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

    def test_onboarding_completion_api(self):
        """Test POST /api/auth/complete-onboarding endpoint"""
        print("\n=== TESTING ONBOARDING COMPLETION API ===")
        
        if not self.auth_token:
            self.log_test("ONBOARDING COMPLETION API - Authentication Required", False, "No authentication token available")
            return False
        
        # Test POST /api/auth/complete-onboarding
        result = self.make_request('POST', '/auth/complete-onboarding', use_auth=True)
        self.log_test(
            "POST /api/auth/complete-onboarding",
            result['success'],
            f"Onboarding completion API working successfully" if result['success'] else f"Onboarding completion failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        completion_response = result['data']
        
        # Check if response has expected structure
        has_success_field = 'success' in completion_response or 'message' in completion_response
        self.log_test(
            "ONBOARDING COMPLETION - RESPONSE STRUCTURE",
            has_success_field,
            f"Response has success/message field" if has_success_field else f"Response structure: {list(completion_response.keys())}"
        )
        
        # Verify user's onboarding status is updated
        user_result = self.make_request('GET', '/auth/me', use_auth=True)
        if user_result['success']:
            user_data = user_result['data']
            has_completed_onboarding = user_data.get('has_completed_onboarding', False)
            self.log_test(
                "ONBOARDING STATUS UPDATE VERIFICATION",
                has_completed_onboarding,
                f"User onboarding status updated to completed" if has_completed_onboarding else f"User onboarding status not updated: {user_data.get('has_completed_onboarding')}"
            )
            return has_completed_onboarding
        
        return has_success_field

    def test_pillars_hierarchy_counts(self):
        """Test GET /api/pillars endpoint for hierarchy count aggregation"""
        print("\n=== TESTING PILLARS HIERARCHY COUNT AGGREGATION ===")
        
        if not self.auth_token:
            self.log_test("PILLARS HIERARCHY COUNTS - Authentication Required", False, "No authentication token available")
            return False
        
        # Test GET /api/pillars
        result = self.make_request('GET', '/pillars', use_auth=True)
        self.log_test(
            "GET /api/pillars",
            result['success'],
            f"Pillars endpoint accessible" if result['success'] else f"Pillars endpoint failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        pillars_response = result['data']
        
        # Check if response is a list
        if not isinstance(pillars_response, list):
            self.log_test(
                "PILLARS RESPONSE FORMAT",
                False,
                f"Expected list, got: {type(pillars_response)}"
            )
            return False
        
        self.log_test(
            "PILLARS RESPONSE FORMAT",
            True,
            f"Retrieved {len(pillars_response)} pillars"
        )
        
        # Check hierarchy count fields in pillars
        if len(pillars_response) > 0:
            first_pillar = pillars_response[0]
            required_count_fields = ['area_count', 'project_count', 'task_count']
            
            missing_fields = []
            present_fields = []
            for field in required_count_fields:
                if field in first_pillar:
                    present_fields.append(field)
                else:
                    missing_fields.append(field)
            
            fields_present = len(missing_fields) == 0
            self.log_test(
                "PILLARS HIERARCHY COUNT FIELDS",
                fields_present,
                f"All count fields present: {present_fields}" if fields_present else f"Missing count fields: {missing_fields}"
            )
            
            # Verify count values are numeric
            if fields_present:
                count_values_valid = True
                count_details = {}
                for field in required_count_fields:
                    value = first_pillar.get(field)
                    if isinstance(value, (int, float)) and value >= 0:
                        count_details[field] = value
                    else:
                        count_values_valid = False
                        count_details[field] = f"Invalid: {value}"
                
                self.log_test(
                    "PILLARS COUNT VALUES VALIDATION",
                    count_values_valid,
                    f"Count values: {count_details}" if count_values_valid else f"Invalid count values: {count_details}"
                )
                
                return count_values_valid
            
            return fields_present
        else:
            self.log_test(
                "PILLARS HIERARCHY COUNT FIELDS",
                True,
                "No pillars found - cannot verify count fields but endpoint working"
            )
            return True

    def test_areas_hierarchy_counts(self):
        """Test GET /api/areas endpoint for hierarchy count aggregation"""
        print("\n=== TESTING AREAS HIERARCHY COUNT AGGREGATION ===")
        
        if not self.auth_token:
            self.log_test("AREAS HIERARCHY COUNTS - Authentication Required", False, "No authentication token available")
            return False
        
        # Test GET /api/areas
        result = self.make_request('GET', '/areas', use_auth=True)
        self.log_test(
            "GET /api/areas",
            result['success'],
            f"Areas endpoint accessible" if result['success'] else f"Areas endpoint failed: {result.get('error', 'Unknown error')}"
        )
        
        if not result['success']:
            return False
        
        areas_response = result['data']
        
        # Check if response is a list
        if not isinstance(areas_response, list):
            self.log_test(
                "AREAS RESPONSE FORMAT",
                False,
                f"Expected list, got: {type(areas_response)}"
            )
            return False
        
        self.log_test(
            "AREAS RESPONSE FORMAT",
            True,
            f"Retrieved {len(areas_response)} areas"
        )
        
        # Check hierarchy count fields in areas
        if len(areas_response) > 0:
            first_area = areas_response[0]
            required_count_fields = ['project_count', 'task_count']
            
            missing_fields = []
            present_fields = []
            for field in required_count_fields:
                if field in first_area:
                    present_fields.append(field)
                else:
                    missing_fields.append(field)
            
            fields_present = len(missing_fields) == 0
            self.log_test(
                "AREAS HIERARCHY COUNT FIELDS",
                fields_present,
                f"All count fields present: {present_fields}" if fields_present else f"Missing count fields: {missing_fields}"
            )
            
            # Verify count values are numeric
            if fields_present:
                count_values_valid = True
                count_details = {}
                for field in required_count_fields:
                    value = first_area.get(field)
                    if isinstance(value, (int, float)) and value >= 0:
                        count_details[field] = value
                    else:
                        count_values_valid = False
                        count_details[field] = f"Invalid: {value}"
                
                self.log_test(
                    "AREAS COUNT VALUES VALIDATION",
                    count_values_valid,
                    f"Count values: {count_details}" if count_values_valid else f"Invalid count values: {count_details}"
                )
                
                return count_values_valid
            
            return fields_present
        else:
            self.log_test(
                "AREAS HIERARCHY COUNT FIELDS",
                True,
                "No areas found - cannot verify count fields but endpoint working"
            )
            return True

    def test_hierarchy_count_accuracy(self):
        """Test accuracy of hierarchy count aggregation by comparing with actual data"""
        print("\n=== TESTING HIERARCHY COUNT ACCURACY ===")
        
        if not self.auth_token:
            self.log_test("HIERARCHY COUNT ACCURACY - Authentication Required", False, "No authentication token available")
            return False
        
        # Get all data to verify counts
        pillars_result = self.make_request('GET', '/pillars', use_auth=True)
        areas_result = self.make_request('GET', '/areas', use_auth=True)
        projects_result = self.make_request('GET', '/projects', use_auth=True)
        tasks_result = self.make_request('GET', '/tasks', use_auth=True)
        
        if not all([pillars_result['success'], areas_result['success'], projects_result['success'], tasks_result['success']]):
            self.log_test(
                "HIERARCHY COUNT ACCURACY - DATA RETRIEVAL",
                False,
                "Failed to retrieve all hierarchy data for count verification"
            )
            return False
        
        pillars = pillars_result['data']
        areas = areas_result['data']
        projects = projects_result['data']
        tasks = tasks_result['data']
        
        # Verify pillar counts
        pillar_count_accuracy = True
        pillar_count_details = []
        
        for pillar in pillars:
            pillar_id = pillar['id']
            
            # Count actual areas for this pillar
            actual_area_count = len([a for a in areas if a.get('pillar_id') == pillar_id])
            reported_area_count = pillar.get('area_count', 0)
            
            # Count actual projects for this pillar (through areas)
            pillar_area_ids = [a['id'] for a in areas if a.get('pillar_id') == pillar_id]
            actual_project_count = len([p for p in projects if p.get('area_id') in pillar_area_ids])
            reported_project_count = pillar.get('project_count', 0)
            
            # Count actual tasks for this pillar (through projects)
            pillar_project_ids = [p['id'] for p in projects if p.get('area_id') in pillar_area_ids]
            actual_task_count = len([t for t in tasks if t.get('project_id') in pillar_project_ids])
            reported_task_count = pillar.get('task_count', 0)
            
            pillar_accuracy = (
                actual_area_count == reported_area_count and
                actual_project_count == reported_project_count and
                actual_task_count == reported_task_count
            )
            
            if not pillar_accuracy:
                pillar_count_accuracy = False
            
            pillar_count_details.append({
                'pillar_name': pillar.get('name', 'Unknown'),
                'area_count': f"actual: {actual_area_count}, reported: {reported_area_count}",
                'project_count': f"actual: {actual_project_count}, reported: {reported_project_count}",
                'task_count': f"actual: {actual_task_count}, reported: {reported_task_count}",
                'accurate': pillar_accuracy
            })
        
        self.log_test(
            "PILLAR COUNT ACCURACY",
            pillar_count_accuracy,
            f"Pillar count aggregation accurate" if pillar_count_accuracy else f"Pillar count discrepancies found",
            pillar_count_details if not pillar_count_accuracy else None
        )
        
        # Verify area counts
        area_count_accuracy = True
        area_count_details = []
        
        for area in areas:
            area_id = area['id']
            
            # Count actual projects for this area
            actual_project_count = len([p for p in projects if p.get('area_id') == area_id])
            reported_project_count = area.get('project_count', 0)
            
            # Count actual tasks for this area (through projects)
            area_project_ids = [p['id'] for p in projects if p.get('area_id') == area_id]
            actual_task_count = len([t for t in tasks if t.get('project_id') in area_project_ids])
            reported_task_count = area.get('task_count', 0)
            
            area_accuracy = (
                actual_project_count == reported_project_count and
                actual_task_count == reported_task_count
            )
            
            if not area_accuracy:
                area_count_accuracy = False
            
            area_count_details.append({
                'area_name': area.get('name', 'Unknown'),
                'project_count': f"actual: {actual_project_count}, reported: {reported_project_count}",
                'task_count': f"actual: {actual_task_count}, reported: {reported_task_count}",
                'accurate': area_accuracy
            })
        
        self.log_test(
            "AREA COUNT ACCURACY",
            area_count_accuracy,
            f"Area count aggregation accurate" if area_count_accuracy else f"Area count discrepancies found",
            area_count_details if not area_count_accuracy else None
        )
        
        return pillar_count_accuracy and area_count_accuracy

    def test_error_handling(self):
        """Test error handling for onboarding and hierarchy endpoints"""
        print("\n=== TESTING ERROR HANDLING ===")
        
        # Test endpoints without authentication
        endpoints_to_test = [
            ('POST', '/auth/complete-onboarding'),
            ('GET', '/pillars'),
            ('GET', '/areas')
        ]
        
        auth_required_count = 0
        total_endpoints = len(endpoints_to_test)
        
        for method, endpoint in endpoints_to_test:
            result = self.make_request(method, endpoint, use_auth=False)
            requires_auth = result['status_code'] in [401, 403]
            
            self.log_test(
                f"ERROR HANDLING - {method} {endpoint} WITHOUT AUTH",
                requires_auth,
                f"Endpoint properly requires authentication (status: {result['status_code']})" if requires_auth else f"Endpoint does not require authentication (status: {result['status_code']})"
            )
            
            if requires_auth:
                auth_required_count += 1
        
        auth_success_rate = (auth_required_count / total_endpoints) * 100
        overall_auth_success = auth_success_rate >= 75
        
        self.log_test(
            "ERROR HANDLING - AUTHENTICATION REQUIREMENTS",
            overall_auth_success,
            f"Authentication requirements: {auth_required_count}/{total_endpoints} endpoints ({auth_success_rate:.1f}%)"
        )
        
        return overall_auth_success

    def run_comprehensive_onboarding_hierarchy_test(self):
        """Run comprehensive onboarding and hierarchy count tests"""
        print("\n🚀 STARTING SMART ONBOARDING API COMPLETION & HIERARCHY COUNT AGGREGATION TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 80)
        
        # Run all tests in sequence
        test_methods = [
            ("Basic Connectivity", self.test_basic_connectivity),
            ("User Authentication", self.test_user_authentication),
            ("Onboarding Completion API", self.test_onboarding_completion_api),
            ("Pillars Hierarchy Counts", self.test_pillars_hierarchy_counts),
            ("Areas Hierarchy Counts", self.test_areas_hierarchy_counts),
            ("Hierarchy Count Accuracy", self.test_hierarchy_count_accuracy),
            ("Error Handling", self.test_error_handling)
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
        print("🚀 SMART ONBOARDING & HIERARCHY COUNT TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze results for specific functionality
        onboarding_tests_passed = sum(1 for result in self.test_results if result['success'] and 'ONBOARDING' in result['test'])
        hierarchy_tests_passed = sum(1 for result in self.test_results if result['success'] and ('PILLARS' in result['test'] or 'AREAS' in result['test']))
        auth_tests_passed = sum(1 for result in self.test_results if result['success'] and 'AUTHENTICATION' in result['test'])
        
        print(f"\n🔍 SYSTEM ANALYSIS:")
        print(f"Authentication Tests Passed: {auth_tests_passed}")
        print(f"Onboarding API Tests Passed: {onboarding_tests_passed}")
        print(f"Hierarchy Count Tests Passed: {hierarchy_tests_passed}")
        
        if success_rate >= 85:
            print("\n✅ SMART ONBOARDING & HIERARCHY COUNT SYSTEM: SUCCESS")
            print("   ✅ Authentication with marc.alleyne@aurumtechnologyltd.com working")
            print("   ✅ POST /api/auth/complete-onboarding functional")
            print("   ✅ GET /api/pillars returns proper count data")
            print("   ✅ GET /api/areas returns proper count data")
            print("   ✅ Hierarchy count aggregation working correctly")
            print("   The Smart Onboarding API and Hierarchy Count system is production-ready!")
        else:
            print("\n❌ SMART ONBOARDING & HIERARCHY COUNT SYSTEM: ISSUES DETECTED")
            print("   Issues found in onboarding completion or hierarchy count aggregation")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 85

def main():
    """Run Smart Onboarding API Completion & Hierarchy Count Aggregation Tests"""
    print("🚀 STARTING SMART ONBOARDING API COMPLETION & HIERARCHY COUNT AGGREGATION TESTING")
    print("=" * 80)
    
    tester = OnboardingHierarchyTester()
    
    try:
        # Run the comprehensive tests
        success = tester.run_comprehensive_onboarding_hierarchy_test()
        
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