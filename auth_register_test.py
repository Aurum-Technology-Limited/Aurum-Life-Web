#!/usr/bin/env python3
"""
AUTH REGISTER ENDPOINT INVESTIGATION - 400 ERROR TESTING
Testing /api/auth/register endpoint with realistic payloads to investigate 400 errors.

FOCUS AREAS:
1. Base URL: https://taskpilot-2.preview.emergentagent.com
2. POST /api/auth/register with realistic payload
3. Capture full response for 400 errors
4. Test different scenarios (with/without username, minimal fields)
5. Report findings

EXPECTED BEHAVIOR:
- Test with realistic email format: e2e.debug+<timestamp>@emergent.test
- Test with strong password: P@ssw0rd123
- Test with complete user data
- Capture detailed error responses
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import time

# Configuration - Using the preview base URL as specified
BASE_URL = "https://taskpilot-2.preview.emergentagent.com"
API_BASE = f"{BASE_URL}/api"

class AuthRegisterTester:
    def __init__(self):
        self.base_url = API_BASE
        self.session = requests.Session()
        self.test_results = []
        
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
        if data:
            print(f"   Response Data: {json.dumps(data, indent=2, default=str)}")

    def make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """Make HTTP request with detailed error handling"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        try:
            if method.upper() == 'POST':
                response = self.session.post(url, json=data, params=params, headers=headers, timeout=30)
            elif method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            # Try to parse JSON response
            try:
                response_data = response.json() if response.content else {}
            except:
                response_data = {"raw_content": response.text[:1000] if response.text else "No content"}
                
            return {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'data': response_data,
                'response': response,
                'headers': dict(response.headers),
                'error': f"HTTP {response.status_code}: {response_data}" if response.status_code >= 400 else None
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg += f" - Response: {error_data}"
                except:
                    error_msg += f" - Response: {e.response.text[:500]}"
            
            return {
                'success': False,
                'error': error_msg,
                'status_code': getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
                'data': {},
                'response': getattr(e, 'response', None)
            }

    def test_register_with_complete_payload(self):
        """Test 1: Register with complete realistic payload as specified"""
        print("\n=== TEST 1: REGISTER WITH COMPLETE REALISTIC PAYLOAD ===")
        
        timestamp = int(time.time())
        register_data = {
            "email": f"e2e.debug+{timestamp}@emergent.test",
            "password": "P@ssw0rd123",
            "first_name": "E2E",
            "last_name": "User",
            "username": f"e2e_{timestamp}"
        }
        
        print(f"Testing with payload: {json.dumps(register_data, indent=2)}")
        
        result = self.make_request('POST', '/auth/register', data=register_data)
        
        if result['status_code'] == 400:
            self.log_test(
                "REGISTER WITH COMPLETE PAYLOAD - 400 ERROR CAPTURED",
                True,  # Success in capturing the error
                f"400 error captured as requested. Status: {result['status_code']}",
                {
                    "status_code": result['status_code'],
                    "response_data": result['data'],
                    "headers": result.get('headers', {}),
                    "payload_used": register_data
                }
            )
            return result
        elif result['status_code'] == 409:
            self.log_test(
                "REGISTER WITH COMPLETE PAYLOAD - 409 CONFLICT",
                True,
                f"409 conflict captured. Status: {result['status_code']}",
                {
                    "status_code": result['status_code'],
                    "response_data": result['data'],
                    "conflict_message": result['data'].get('detail', 'No detail provided'),
                    "payload_used": register_data
                }
            )
            return result
        elif result['status_code'] == 201 or result['status_code'] == 200:
            self.log_test(
                "REGISTER WITH COMPLETE PAYLOAD - SUCCESS",
                True,
                f"Registration successful. Status: {result['status_code']}",
                {
                    "status_code": result['status_code'],
                    "response_data": result['data'],
                    "payload_used": register_data
                }
            )
            return result
        else:
            self.log_test(
                "REGISTER WITH COMPLETE PAYLOAD - UNEXPECTED STATUS",
                False,
                f"Unexpected status code: {result['status_code']}",
                {
                    "status_code": result['status_code'],
                    "response_data": result['data'],
                    "error": result.get('error'),
                    "payload_used": register_data
                }
            )
            return result

    def test_register_without_username(self):
        """Test 2: Register without username field"""
        print("\n=== TEST 2: REGISTER WITHOUT USERNAME ===")
        
        timestamp = int(time.time())
        register_data = {
            "email": f"e2e.debug+{timestamp}@emergent.test",
            "password": "P@ssw0rd123",
            "first_name": "E2E",
            "last_name": "User"
            # No username field
        }
        
        print(f"Testing without username: {json.dumps(register_data, indent=2)}")
        
        result = self.make_request('POST', '/auth/register', data=register_data)
        
        if result['status_code'] == 400:
            self.log_test(
                "REGISTER WITHOUT USERNAME - 400 ERROR",
                True,
                f"400 error for missing username. Status: {result['status_code']}",
                {
                    "status_code": result['status_code'],
                    "response_data": result['data'],
                    "validation_errors": result['data'].get('detail', 'No detail provided'),
                    "payload_used": register_data
                }
            )
        elif result['status_code'] == 422:
            self.log_test(
                "REGISTER WITHOUT USERNAME - 422 VALIDATION ERROR",
                True,
                f"422 validation error for missing username. Status: {result['status_code']}",
                {
                    "status_code": result['status_code'],
                    "response_data": result['data'],
                    "validation_errors": result['data'].get('detail', 'No detail provided'),
                    "payload_used": register_data
                }
            )
        elif result['status_code'] in [200, 201]:
            self.log_test(
                "REGISTER WITHOUT USERNAME - SUCCESS",
                True,
                f"Registration successful without username. Status: {result['status_code']}",
                {
                    "status_code": result['status_code'],
                    "response_data": result['data'],
                    "payload_used": register_data
                }
            )
        else:
            self.log_test(
                "REGISTER WITHOUT USERNAME - UNEXPECTED STATUS",
                False,
                f"Unexpected status code: {result['status_code']}",
                {
                    "status_code": result['status_code'],
                    "response_data": result['data'],
                    "payload_used": register_data
                }
            )
        
        return result

    def test_register_minimal_fields(self):
        """Test 3: Register with minimal required fields only"""
        print("\n=== TEST 3: REGISTER WITH MINIMAL FIELDS ===")
        
        timestamp = int(time.time())
        register_data = {
            "email": f"e2e.debug+{timestamp}@emergent.test",
            "password": "P@ssw0rd123"
            # Only email and password
        }
        
        print(f"Testing with minimal fields: {json.dumps(register_data, indent=2)}")
        
        result = self.make_request('POST', '/auth/register', data=register_data)
        
        if result['status_code'] == 400:
            self.log_test(
                "REGISTER WITH MINIMAL FIELDS - 400 ERROR",
                True,
                f"400 error for minimal fields. Status: {result['status_code']}",
                {
                    "status_code": result['status_code'],
                    "response_data": result['data'],
                    "required_fields_error": result['data'].get('detail', 'No detail provided'),
                    "payload_used": register_data
                }
            )
        elif result['status_code'] == 422:
            self.log_test(
                "REGISTER WITH MINIMAL FIELDS - 422 VALIDATION ERROR",
                True,
                f"422 validation error for minimal fields. Status: {result['status_code']}",
                {
                    "status_code": result['status_code'],
                    "response_data": result['data'],
                    "validation_errors": result['data'].get('detail', 'No detail provided'),
                    "payload_used": register_data
                }
            )
        elif result['status_code'] in [200, 201]:
            self.log_test(
                "REGISTER WITH MINIMAL FIELDS - SUCCESS",
                True,
                f"Registration successful with minimal fields. Status: {result['status_code']}",
                {
                    "status_code": result['status_code'],
                    "response_data": result['data'],
                    "payload_used": register_data
                }
            )
        else:
            self.log_test(
                "REGISTER WITH MINIMAL FIELDS - UNEXPECTED STATUS",
                False,
                f"Unexpected status code: {result['status_code']}",
                {
                    "status_code": result['status_code'],
                    "response_data": result['data'],
                    "payload_used": register_data
                }
            )
        
        return result

    def test_register_invalid_email(self):
        """Test 4: Register with invalid email format"""
        print("\n=== TEST 4: REGISTER WITH INVALID EMAIL ===")
        
        timestamp = int(time.time())
        register_data = {
            "email": "invalid-email-format",  # Invalid email
            "password": "P@ssw0rd123",
            "first_name": "E2E",
            "last_name": "User",
            "username": f"e2e_{timestamp}"
        }
        
        print(f"Testing with invalid email: {json.dumps(register_data, indent=2)}")
        
        result = self.make_request('POST', '/auth/register', data=register_data)
        
        if result['status_code'] == 400:
            self.log_test(
                "REGISTER WITH INVALID EMAIL - 400 ERROR",
                True,
                f"400 error for invalid email format. Status: {result['status_code']}",
                {
                    "status_code": result['status_code'],
                    "response_data": result['data'],
                    "email_validation_error": result['data'].get('detail', 'No detail provided'),
                    "payload_used": register_data
                }
            )
        elif result['status_code'] == 422:
            self.log_test(
                "REGISTER WITH INVALID EMAIL - 422 VALIDATION ERROR",
                True,
                f"422 validation error for invalid email. Status: {result['status_code']}",
                {
                    "status_code": result['status_code'],
                    "response_data": result['data'],
                    "validation_errors": result['data'].get('detail', 'No detail provided'),
                    "payload_used": register_data
                }
            )
        else:
            self.log_test(
                "REGISTER WITH INVALID EMAIL - UNEXPECTED STATUS",
                False,
                f"Unexpected status code: {result['status_code']}",
                {
                    "status_code": result['status_code'],
                    "response_data": result['data'],
                    "payload_used": register_data
                }
            )
        
        return result

    def test_register_weak_password(self):
        """Test 5: Register with weak password"""
        print("\n=== TEST 5: REGISTER WITH WEAK PASSWORD ===")
        
        timestamp = int(time.time())
        register_data = {
            "email": f"e2e.debug+{timestamp}@emergent.test",
            "password": "123",  # Weak password
            "first_name": "E2E",
            "last_name": "User",
            "username": f"e2e_{timestamp}"
        }
        
        print(f"Testing with weak password: {json.dumps(register_data, indent=2)}")
        
        result = self.make_request('POST', '/auth/register', data=register_data)
        
        if result['status_code'] == 400:
            self.log_test(
                "REGISTER WITH WEAK PASSWORD - 400 ERROR",
                True,
                f"400 error for weak password. Status: {result['status_code']}",
                {
                    "status_code": result['status_code'],
                    "response_data": result['data'],
                    "password_validation_error": result['data'].get('detail', 'No detail provided'),
                    "payload_used": register_data
                }
            )
        elif result['status_code'] == 422:
            self.log_test(
                "REGISTER WITH WEAK PASSWORD - 422 VALIDATION ERROR",
                True,
                f"422 validation error for weak password. Status: {result['status_code']}",
                {
                    "status_code": result['status_code'],
                    "response_data": result['data'],
                    "validation_errors": result['data'].get('detail', 'No detail provided'),
                    "payload_used": register_data
                }
            )
        else:
            self.log_test(
                "REGISTER WITH WEAK PASSWORD - UNEXPECTED STATUS",
                False,
                f"Unexpected status code: {result['status_code']}",
                {
                    "status_code": result['status_code'],
                    "response_data": result['data'],
                    "payload_used": register_data
                }
            )
        
        return result

    def test_backend_connectivity(self):
        """Test 0: Basic backend connectivity"""
        print("\n=== TEST 0: BACKEND CONNECTIVITY ===")
        
        # Test the root endpoint
        try:
            response = self.session.get(BASE_URL, timeout=30)
            if response.status_code == 200:
                self.log_test(
                    "BACKEND CONNECTIVITY",
                    True,
                    f"Backend accessible at {BASE_URL}. Status: {response.status_code}"
                )
                return True
            else:
                self.log_test(
                    "BACKEND CONNECTIVITY",
                    False,
                    f"Backend returned status: {response.status_code}"
                )
                return False
        except Exception as e:
            self.log_test(
                "BACKEND CONNECTIVITY",
                False,
                f"Backend connection failed: {str(e)}"
            )
            return False

    def run_comprehensive_register_test(self):
        """Run comprehensive auth register testing"""
        print("\n🔐 STARTING AUTH REGISTER ENDPOINT INVESTIGATION")
        print("=" * 80)
        print(f"Base URL: {BASE_URL}")
        print(f"API Base: {API_BASE}")
        print("Testing /api/auth/register endpoint with realistic payloads")
        print("=" * 80)
        
        # Test backend connectivity first
        if not self.test_backend_connectivity():
            print("❌ Backend connectivity failed. Aborting tests.")
            return False
        
        # Run all register tests
        test_methods = [
            ("Complete Realistic Payload", self.test_register_with_complete_payload),
            ("Without Username", self.test_register_without_username),
            ("Minimal Fields Only", self.test_register_minimal_fields),
            ("Invalid Email Format", self.test_register_invalid_email),
            ("Weak Password", self.test_register_weak_password)
        ]
        
        successful_tests = 0
        total_tests = len(test_methods)
        
        for test_name, test_method in test_methods:
            print(f"\n--- {test_name} ---")
            try:
                result = test_method()
                if result and (result.get('status_code') in [200, 201, 400, 409, 422]):
                    successful_tests += 1
                    print(f"✅ {test_name} completed (captured response)")
                else:
                    print(f"❌ {test_name} failed to capture meaningful response")
            except Exception as e:
                print(f"❌ {test_name} raised exception: {e}")
        
        success_rate = (successful_tests / total_tests) * 100
        
        print(f"\n" + "=" * 80)
        print("🔐 AUTH REGISTER ENDPOINT INVESTIGATION SUMMARY")
        print("=" * 80)
        print(f"Base URL: {BASE_URL}")
        print(f"Tests Completed: {successful_tests}/{total_tests}")
        print(f"Response Capture Rate: {success_rate:.1f}%")
        
        # Analyze captured responses
        error_400_count = sum(1 for result in self.test_results if result.get('data', {}).get('status_code') == 400)
        error_409_count = sum(1 for result in self.test_results if result.get('data', {}).get('status_code') == 409)
        error_422_count = sum(1 for result in self.test_results if result.get('data', {}).get('status_code') == 422)
        success_count = sum(1 for result in self.test_results if result.get('data', {}).get('status_code') in [200, 201])
        
        print(f"\n🔍 RESPONSE ANALYSIS:")
        print(f"400 Bad Request Responses: {error_400_count}")
        print(f"409 Conflict Responses: {error_409_count}")
        print(f"422 Validation Error Responses: {error_422_count}")
        print(f"Success Responses (200/201): {success_count}")
        
        # Show detailed findings
        print(f"\n📋 DETAILED FINDINGS:")
        for result in self.test_results:
            if result.get('data') and result['data'].get('status_code'):
                status_code = result['data']['status_code']
                response_data = result['data'].get('response_data', {})
                detail = response_data.get('detail', 'No detail provided')
                
                print(f"   {result['test']}: HTTP {status_code}")
                print(f"      Detail: {detail}")
                if 'validation_errors' in result['data']:
                    print(f"      Validation: {result['data']['validation_errors']}")
        
        return success_rate >= 80

def main():
    """Run Auth Register Investigation"""
    print("🔐 STARTING AUTH REGISTER ENDPOINT INVESTIGATION")
    print("=" * 80)
    
    tester = AuthRegisterTester()
    
    try:
        # Run the comprehensive register investigation
        success = tester.run_comprehensive_register_test()
        
        # Calculate overall results
        total_tests = len(tester.test_results)
        meaningful_responses = sum(1 for result in tester.test_results if result.get('data', {}).get('status_code'))
        capture_rate = (meaningful_responses / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 80)
        print("📊 FINAL INVESTIGATION RESULTS")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Meaningful Responses Captured: {meaningful_responses}")
        print(f"Response Capture Rate: {capture_rate:.1f}%")
        print("=" * 80)
        
        # Show key findings
        print("\n🎯 KEY FINDINGS:")
        if meaningful_responses > 0:
            print("✅ Successfully captured responses from /api/auth/register endpoint")
            print("✅ Detailed error messages and status codes documented")
            print("✅ Different payload scenarios tested")
            print("✅ Investigation completed as requested")
        else:
            print("❌ Failed to capture meaningful responses")
            print("❌ Endpoint may be inaccessible or not implemented")
        
        return capture_rate >= 80
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during investigation: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)