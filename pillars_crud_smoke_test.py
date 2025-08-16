#!/usr/bin/env python3
"""
PILLARS CRUD SMOKE TEST - FOCUSED BACKEND TESTING
Testing the specific pillars CRUD operations as requested in review:

1) Auth login
2) POST /api/pillars {name:'Health', description:'Wellbeing', icon:'🎯', color:'#F4B400', time_allocation_percentage:10}
3) GET /api/pillars -> should include Health
4) PUT /api/pillars/{id} {name:'Health+', description:'Wellbeing+', icon:'🎯', color:'#F4B400', time_allocation_percentage:12}
5) DELETE /api/pillars/{id} -> ok

Return concise pass/fail and any 4xx/5xx response bodies.
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://focus-planner-3.preview.emergentagent.com/api"

class PillarsCRUDSmokeTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.auth_token = None
        self.test_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.test_user_password = "password123"
        self.created_pillar_id = None
        
    def log_result(self, test_name: str, success: bool, message: str = "", response_data: Any = None):
        """Log test results concisely"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if response_data and not success:
            print(f"   Response: {json.dumps(response_data, indent=2, default=str)}")

    def make_request(self, method: str, endpoint: str, data: Dict = None, use_auth: bool = False) -> Dict:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if use_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, headers=headers, timeout=30)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, headers=headers, timeout=30)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, headers=headers, timeout=30)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            try:
                response_data = response.json() if response.content else {}
            except:
                response_data = {"raw_content": response.text[:500] if response.text else "No content"}
                
            return {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'data': response_data,
                'error': f"HTTP {response.status_code}: {response_data}" if response.status_code >= 400 else None
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f"Request failed: {str(e)}",
                'status_code': None,
                'data': {}
            }

    def test_auth_login(self):
        """Test 1: Auth login"""
        print("\n=== TEST 1: AUTH LOGIN ===")
        
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        
        if result['success']:
            token_data = result['data']
            self.auth_token = token_data.get('access_token')
            self.log_result("Auth Login", True, f"Login successful for {self.test_user_email}")
            return True
        else:
            self.log_result("Auth Login", False, f"Login failed: {result.get('error', 'Unknown error')}", result['data'])
            return False

    def test_create_pillar(self):
        """Test 2: POST /api/pillars"""
        print("\n=== TEST 2: POST /api/pillars ===")
        
        pillar_data = {
            "name": "Health",
            "description": "Wellbeing",
            "icon": "🎯",
            "color": "#F4B400",
            "time_allocation_percentage": 10
        }
        
        result = self.make_request('POST', '/pillars', data=pillar_data, use_auth=True)
        
        if result['success']:
            pillar = result['data']
            self.created_pillar_id = pillar.get('id')
            self.log_result("Create Pillar", True, f"Pillar created successfully with ID: {self.created_pillar_id}")
            return True
        else:
            self.log_result("Create Pillar", False, f"Failed to create pillar: {result.get('error', 'Unknown error')}", result['data'])
            return False

    def test_get_pillars(self):
        """Test 3: GET /api/pillars -> should include Health"""
        print("\n=== TEST 3: GET /api/pillars ===")
        
        result = self.make_request('GET', '/pillars', use_auth=True)
        
        if result['success']:
            pillars = result['data']
            health_pillar = next((p for p in pillars if p.get('name') == 'Health'), None)
            
            if health_pillar:
                self.log_result("Get Pillars", True, f"Health pillar found in list (ID: {health_pillar.get('id')})")
                return True
            else:
                self.log_result("Get Pillars", False, "Health pillar not found in pillars list", pillars)
                return False
        else:
            self.log_result("Get Pillars", False, f"Failed to get pillars: {result.get('error', 'Unknown error')}", result['data'])
            return False

    def test_update_pillar(self):
        """Test 4: PUT /api/pillars/{id}"""
        print("\n=== TEST 4: PUT /api/pillars/{id} ===")
        
        if not self.created_pillar_id:
            self.log_result("Update Pillar", False, "No pillar ID available for update")
            return False
        
        update_data = {
            "name": "Health+",
            "description": "Wellbeing+",
            "icon": "🎯",
            "color": "#F4B400",
            "time_allocation_percentage": 12
        }
        
        result = self.make_request('PUT', f'/pillars/{self.created_pillar_id}', data=update_data, use_auth=True)
        
        if result['success']:
            updated_pillar = result['data']
            if updated_pillar.get('name') == 'Health+' and updated_pillar.get('time_allocation_percentage') == 12:
                self.log_result("Update Pillar", True, f"Pillar updated successfully: {updated_pillar.get('name')}")
                return True
            else:
                self.log_result("Update Pillar", False, "Pillar update did not reflect expected changes", updated_pillar)
                return False
        else:
            self.log_result("Update Pillar", False, f"Failed to update pillar: {result.get('error', 'Unknown error')}", result['data'])
            return False

    def test_delete_pillar(self):
        """Test 5: DELETE /api/pillars/{id}"""
        print("\n=== TEST 5: DELETE /api/pillars/{id} ===")
        
        if not self.created_pillar_id:
            self.log_result("Delete Pillar", False, "No pillar ID available for deletion")
            return False
        
        result = self.make_request('DELETE', f'/pillars/{self.created_pillar_id}', use_auth=True)
        
        if result['success']:
            self.log_result("Delete Pillar", True, f"Pillar deleted successfully (ID: {self.created_pillar_id})")
            return True
        else:
            self.log_result("Delete Pillar", False, f"Failed to delete pillar: {result.get('error', 'Unknown error')}", result['data'])
            return False

    def run_smoke_test(self):
        """Run the complete pillars CRUD smoke test"""
        print("🚀 STARTING PILLARS CRUD SMOKE TEST")
        print("=" * 60)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 60)
        
        tests = [
            ("Auth Login", self.test_auth_login),
            ("Create Pillar", self.test_create_pillar),
            ("Get Pillars", self.test_get_pillars),
            ("Update Pillar", self.test_update_pillar),
            ("Delete Pillar", self.test_delete_pillar)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_method in tests:
            try:
                if test_method():
                    passed_tests += 1
                else:
                    # If a test fails, we might still want to continue for diagnostic purposes
                    pass
            except Exception as e:
                print(f"❌ {test_name} raised exception: {e}")
        
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"\n" + "=" * 60)
        print("📊 PILLARS CRUD SMOKE TEST SUMMARY")
        print("=" * 60)
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("🎉 ALL TESTS PASSED - Pillars CRUD is working perfectly!")
        elif success_rate >= 80:
            print("⚠️ MOSTLY WORKING - Minor issues detected")
        else:
            print("❌ SIGNIFICANT ISSUES - Pillars CRUD needs attention")
        
        print("=" * 60)
        
        return success_rate >= 80

def main():
    """Run Pillars CRUD Smoke Test"""
    tester = PillarsCRUDSmokeTest()
    
    try:
        success = tester.run_smoke_test()
        return success
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)