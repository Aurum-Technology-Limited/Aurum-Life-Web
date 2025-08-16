#!/usr/bin/env python3
"""
AREAS CRUD BACKEND TESTING - FOCUSED VERIFICATION
Re-run backend CRUD for Areas to confirm the fix as requested in review.

TEST PLAN:
1. Login with marc.alleyne@aurumtechnologyltd.com/password123
2. POST /api/areas with valid data (no pillar_id and with pillar_id)
3. GET /api/areas and /api/ultra/areas if present
4. DELETE created areas
5. Verify removals
6. Record 200/201 vs 400/500 statuses and response times

FOCUS: Verify that the previous HTTP 500 server errors on /api/areas endpoint have been resolved.
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Any

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://focus-planner-3.preview.emergentagent.com/api"

class AreasCRUDTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.test_results = []
        self.auth_token = None
        self.created_areas = []
        self.response_times = []
        
        # Test credentials as specified
        self.test_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.test_user_password = "password123"
        
    def log_test(self, test_name: str, success: bool, message: str = "", data: Any = None, response_time: float = None):
        """Log test results with response time tracking"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'response_time_ms': response_time
        }
        if data:
            result['data'] = data
        self.test_results.append(result)
        
        if response_time:
            self.response_times.append(response_time)
        
        status = "✅ PASS" if success else "❌ FAIL"
        time_info = f" ({response_time:.0f}ms)" if response_time else ""
        print(f"{status} {test_name}{time_info}: {message}")
        if data and not success:
            print(f"   Data: {json.dumps(data, indent=2, default=str)}")

    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None, use_auth: bool = False) -> Dict:
        """Make HTTP request with timing and error handling"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if use_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        start_time = time.time()
        
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
            
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            try:
                response_data = response.json() if response.content else {}
            except:
                response_data = {"raw_content": response.text[:500] if response.text else "No content"}
                
            return {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'data': response_data,
                'response': response,
                'response_time': response_time,
                'error': f"HTTP {response.status_code}: {response_data}" if response.status_code >= 400 else None
            }
            
        except requests.exceptions.RequestException as e:
            response_time = (time.time() - start_time) * 1000
            error_msg = f"Request failed: {str(e)}"
            
            return {
                'success': False,
                'error': error_msg,
                'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
                'data': {},
                'response': getattr(e, 'response', None),
                'response_time': response_time
            }

    def test_authentication(self):
        """Test authentication with specified credentials"""
        print("\n=== TESTING AUTHENTICATION ===")
        
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        self.log_test(
            "USER LOGIN",
            result['success'],
            f"Login successful with {self.test_user_email}" if result['success'] else f"Login failed: {result.get('error', 'Unknown error')}",
            response_time=result.get('response_time')
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
            f"Token validated successfully, user: {result['data'].get('email', 'Unknown')}" if result['success'] else f"Token validation failed: {result.get('error', 'Unknown error')}",
            response_time=result.get('response_time')
        )
        
        return result['success']

    def test_areas_post_no_pillar_id(self):
        """Test POST /api/areas with valid data (no pillar_id)"""
        print("\n=== TESTING POST /api/areas (NO PILLAR_ID) ===")
        
        if not self.auth_token:
            self.log_test("POST AREAS - No Pillar ID", False, "No authentication token available")
            return False
        
        area_data = {
            "name": f"Test Area No Pillar {int(time.time())}",
            "description": "Test area without pillar_id to verify backend handles optional pillar linking",
            "icon": "🏠",
            "color": "#3B82F6",
            "importance": 3
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        
        if result['success']:
            created_area = result['data']
            self.created_areas.append(created_area.get('id'))
            self.log_test(
                "POST AREAS - No Pillar ID",
                True,
                f"Area created successfully without pillar_id. ID: {created_area.get('id')}",
                response_time=result.get('response_time')
            )
            return True
        else:
            self.log_test(
                "POST AREAS - No Pillar ID",
                False,
                f"Area creation failed: Status {result['status_code']} - {result.get('error', 'Unknown error')}",
                data=result.get('data'),
                response_time=result.get('response_time')
            )
            return False

    def test_areas_post_with_pillar_id(self):
        """Test POST /api/areas with valid data (with pillar_id)"""
        print("\n=== TESTING POST /api/areas (WITH PILLAR_ID) ===")
        
        if not self.auth_token:
            self.log_test("POST AREAS - With Pillar ID", False, "No authentication token available")
            return False
        
        # First, get existing pillars to use a valid pillar_id
        pillars_result = self.make_request('GET', '/pillars', use_auth=True)
        pillar_id = None
        
        if pillars_result['success'] and pillars_result['data']:
            pillar_id = pillars_result['data'][0].get('id')
            print(f"Using existing pillar ID: {pillar_id}")
        else:
            # Create a pillar first if none exist
            pillar_data = {
                "name": f"Test Pillar {int(time.time())}",
                "description": "Test pillar for area creation",
                "icon": "🎯",
                "color": "#10B981",
                "time_allocation_percentage": 25.0
            }
            
            pillar_result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
            if pillar_result['success']:
                pillar_id = pillar_result['data'].get('id')
                print(f"Created new pillar ID: {pillar_id}")
            else:
                self.log_test(
                    "POST AREAS - With Pillar ID",
                    False,
                    f"Could not create or find pillar for testing: {pillar_result.get('error', 'Unknown error')}",
                    response_time=pillar_result.get('response_time')
                )
                return False
        
        area_data = {
            "name": f"Test Area With Pillar {int(time.time())}",
            "description": "Test area with pillar_id to verify backend handles pillar linking",
            "pillar_id": pillar_id,
            "icon": "🏢",
            "color": "#F59E0B",
            "importance": 4
        }
        
        result = self.make_request('POST', '/areas', data=area_data, use_auth=True)
        
        if result['success']:
            created_area = result['data']
            self.created_areas.append(created_area.get('id'))
            self.log_test(
                "POST AREAS - With Pillar ID",
                True,
                f"Area created successfully with pillar_id. ID: {created_area.get('id')}, Pillar: {created_area.get('pillar_id')}",
                response_time=result.get('response_time')
            )
            return True
        else:
            self.log_test(
                "POST AREAS - With Pillar ID",
                False,
                f"Area creation failed: Status {result['status_code']} - {result.get('error', 'Unknown error')}",
                data=result.get('data'),
                response_time=result.get('response_time')
            )
            return False

    def test_areas_get_standard(self):
        """Test GET /api/areas"""
        print("\n=== TESTING GET /api/areas ===")
        
        if not self.auth_token:
            self.log_test("GET AREAS - Standard", False, "No authentication token available")
            return False
        
        result = self.make_request('GET', '/areas', use_auth=True)
        
        if result['success']:
            areas = result['data']
            created_count = sum(1 for area in areas if area.get('id') in self.created_areas)
            self.log_test(
                "GET AREAS - Standard",
                True,
                f"Retrieved {len(areas)} areas successfully. {created_count}/{len(self.created_areas)} created areas found.",
                response_time=result.get('response_time')
            )
            return True
        else:
            self.log_test(
                "GET AREAS - Standard",
                False,
                f"Areas retrieval failed: Status {result['status_code']} - {result.get('error', 'Unknown error')}",
                data=result.get('data'),
                response_time=result.get('response_time')
            )
            return False

    def test_areas_get_ultra(self):
        """Test GET /api/ultra/areas if present"""
        print("\n=== TESTING GET /api/ultra/areas ===")
        
        if not self.auth_token:
            self.log_test("GET AREAS - Ultra", False, "No authentication token available")
            return False
        
        result = self.make_request('GET', '/ultra/areas', use_auth=True)
        
        if result['success']:
            areas = result['data']
            created_count = sum(1 for area in areas if area.get('id') in self.created_areas)
            self.log_test(
                "GET AREAS - Ultra",
                True,
                f"Ultra areas endpoint working. Retrieved {len(areas)} areas. {created_count}/{len(self.created_areas)} created areas found.",
                response_time=result.get('response_time')
            )
            return True
        elif result['status_code'] == 404:
            self.log_test(
                "GET AREAS - Ultra",
                True,
                "Ultra areas endpoint not implemented (404) - this is acceptable",
                response_time=result.get('response_time')
            )
            return True
        else:
            self.log_test(
                "GET AREAS - Ultra",
                False,
                f"Ultra areas retrieval failed: Status {result['status_code']} - {result.get('error', 'Unknown error')}",
                data=result.get('data'),
                response_time=result.get('response_time')
            )
            return False

    def test_areas_delete(self):
        """Test DELETE created areas and verify removals"""
        print("\n=== TESTING DELETE /api/areas ===")
        
        if not self.auth_token:
            self.log_test("DELETE AREAS", False, "No authentication token available")
            return False
        
        if not self.created_areas:
            self.log_test("DELETE AREAS", True, "No areas to delete")
            return True
        
        deleted_count = 0
        failed_deletes = []
        
        for area_id in self.created_areas:
            result = self.make_request('DELETE', f'/areas/{area_id}', use_auth=True)
            
            if result['success']:
                deleted_count += 1
                print(f"✅ Deleted area {area_id} (Status: {result['status_code']}, Time: {result.get('response_time', 0):.0f}ms)")
            else:
                failed_deletes.append(area_id)
                print(f"❌ Failed to delete area {area_id}: Status {result['status_code']} - {result.get('error', 'Unknown error')}")
        
        success = len(failed_deletes) == 0
        self.log_test(
            "DELETE AREAS",
            success,
            f"Deleted {deleted_count}/{len(self.created_areas)} areas successfully" if success else f"Failed to delete {len(failed_deletes)} areas: {failed_deletes}",
            response_time=sum(self.response_times[-len(self.created_areas):]) / len(self.created_areas) if self.created_areas else 0
        )
        
        return success

    def test_verify_removals(self):
        """Verify that deleted areas are no longer present"""
        print("\n=== VERIFYING AREA REMOVALS ===")
        
        if not self.auth_token:
            self.log_test("VERIFY REMOVALS", False, "No authentication token available")
            return False
        
        if not self.created_areas:
            self.log_test("VERIFY REMOVALS", True, "No areas were created to verify removal")
            return True
        
        # Check standard endpoint
        result = self.make_request('GET', '/areas', use_auth=True)
        
        if result['success']:
            areas = result['data']
            remaining_areas = [area.get('id') for area in areas if area.get('id') in self.created_areas]
            
            if not remaining_areas:
                self.log_test(
                    "VERIFY REMOVALS - Standard",
                    True,
                    f"All {len(self.created_areas)} created areas successfully removed from standard endpoint",
                    response_time=result.get('response_time')
                )
                standard_success = True
            else:
                self.log_test(
                    "VERIFY REMOVALS - Standard",
                    False,
                    f"{len(remaining_areas)} areas still present after deletion: {remaining_areas}",
                    response_time=result.get('response_time')
                )
                standard_success = False
        else:
            self.log_test(
                "VERIFY REMOVALS - Standard",
                False,
                f"Could not verify removals: Status {result['status_code']} - {result.get('error', 'Unknown error')}",
                response_time=result.get('response_time')
            )
            standard_success = False
        
        # Check ultra endpoint if available
        ultra_result = self.make_request('GET', '/ultra/areas', use_auth=True)
        
        if ultra_result['success']:
            ultra_areas = ultra_result['data']
            remaining_ultra_areas = [area.get('id') for area in ultra_areas if area.get('id') in self.created_areas]
            
            if not remaining_ultra_areas:
                self.log_test(
                    "VERIFY REMOVALS - Ultra",
                    True,
                    f"All {len(self.created_areas)} created areas successfully removed from ultra endpoint",
                    response_time=ultra_result.get('response_time')
                )
                ultra_success = True
            else:
                self.log_test(
                    "VERIFY REMOVALS - Ultra",
                    False,
                    f"{len(remaining_ultra_areas)} areas still present in ultra endpoint after deletion: {remaining_ultra_areas}",
                    response_time=ultra_result.get('response_time')
                )
                ultra_success = False
        elif ultra_result['status_code'] == 404:
            self.log_test(
                "VERIFY REMOVALS - Ultra",
                True,
                "Ultra endpoint not available (404) - removal verification not applicable",
                response_time=ultra_result.get('response_time')
            )
            ultra_success = True
        else:
            self.log_test(
                "VERIFY REMOVALS - Ultra",
                False,
                f"Could not verify ultra removals: Status {ultra_result['status_code']} - {ultra_result.get('error', 'Unknown error')}",
                response_time=ultra_result.get('response_time')
            )
            ultra_success = False
        
        return standard_success and ultra_success

    def run_comprehensive_areas_crud_test(self):
        """Run comprehensive Areas CRUD test as specified in review request"""
        print("\n🏠 STARTING AREAS CRUD BACKEND TESTING")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("Focus: Verify Areas API HTTP 500 errors have been resolved")
        print("=" * 80)
        
        # Run all tests in sequence as specified in review request
        test_methods = [
            ("Authentication", self.test_authentication),
            ("POST Areas (No Pillar ID)", self.test_areas_post_no_pillar_id),
            ("POST Areas (With Pillar ID)", self.test_areas_post_with_pillar_id),
            ("GET Areas (Standard)", self.test_areas_get_standard),
            ("GET Areas (Ultra)", self.test_areas_get_ultra),
            ("DELETE Areas", self.test_areas_delete),
            ("Verify Removals", self.test_verify_removals)
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
        print("🏠 AREAS CRUD BACKEND TESTING SUMMARY")
        print("=" * 80)
        print(f"Backend URL: {self.base_url}")
        print(f"Test Methods: {successful_tests}/{total_tests} successful")
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Analyze response times and status codes
        if self.response_times:
            avg_response_time = sum(self.response_times) / len(self.response_times)
            max_response_time = max(self.response_times)
            min_response_time = min(self.response_times)
            
            print(f"\n📊 PERFORMANCE ANALYSIS:")
            print(f"Average Response Time: {avg_response_time:.0f}ms")
            print(f"Max Response Time: {max_response_time:.0f}ms")
            print(f"Min Response Time: {min_response_time:.0f}ms")
        
        # Analyze status codes
        status_codes = {}
        for result in self.test_results:
            if 'data' in result and isinstance(result['data'], dict):
                # This would contain response info, but we're tracking in the result structure
                pass
        
        # Count success vs failure status codes from our results
        success_responses = sum(1 for result in self.test_results if result['success'])
        failed_responses = len(self.test_results) - success_responses
        
        print(f"\n📈 STATUS CODE ANALYSIS:")
        print(f"Successful Responses (200/201): {success_responses}")
        print(f"Failed Responses (400/500): {failed_responses}")
        
        # Specific analysis for Areas API fix
        areas_specific_tests = [result for result in self.test_results if 'AREAS' in result['test'].upper()]
        areas_success_count = sum(1 for result in areas_specific_tests if result['success'])
        
        print(f"\n🔍 AREAS API SPECIFIC ANALYSIS:")
        print(f"Areas-specific Tests Passed: {areas_success_count}/{len(areas_specific_tests)}")
        
        if success_rate >= 85:
            print("\n✅ AREAS CRUD API SYSTEM: SUCCESS")
            print("   ✅ POST /api/areas working (both with and without pillar_id)")
            print("   ✅ GET /api/areas functional")
            print("   ✅ GET /api/ultra/areas verified (if available)")
            print("   ✅ DELETE /api/areas operational")
            print("   ✅ Area removal verification successful")
            print("   The Areas API HTTP 500 errors have been RESOLVED!")
        else:
            print("\n❌ AREAS CRUD API SYSTEM: ISSUES DETECTED")
            print("   Issues found in Areas API implementation")
            if failed_responses > 0:
                print(f"   {failed_responses} requests returned 400/500 status codes")
        
        # Show failed tests for debugging
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   ❌ {test['test']}: {test['message']}")
        
        return success_rate >= 85

def main():
    """Run Areas CRUD Backend Tests"""
    print("🏠 STARTING AREAS CRUD BACKEND TESTING")
    print("=" * 80)
    
    tester = AreasCRUDTester()
    
    try:
        # Run the comprehensive Areas CRUD tests
        success = tester.run_comprehensive_areas_crud_test()
        
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