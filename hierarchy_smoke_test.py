#!/usr/bin/env python3
"""
HIERARCHY ENDPOINTS BACKEND SMOKE TEST
Testing the hierarchy endpoints as requested in review:
1) Auth login
2) GET /api/ultra/pillars -> expect 200 list
3) GET /api/ultra/areas -> expect 200 list
4) GET /api/ultra/projects -> expect 200 list

Return concise pass/fail and first item sample if present.
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, List, Any

# Configuration - Using the backend URL from frontend/.env
BACKEND_URL = "https://productivity-hub-23.preview.emergentagent.com/api"

class HierarchySmokeTest:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.auth_token = None
        # Use existing test credentials
        self.test_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.test_user_password = "password123"
        
    def make_request(self, method: str, endpoint: str, data: Dict = None, use_auth: bool = False) -> Dict:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if use_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, headers=headers, timeout=15)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, headers=headers, timeout=15)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            try:
                response_data = response.json() if response.content else {}
            except:
                response_data = {"raw_content": response.text[:200] if response.text else "No content"}
                
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'data': response_data,
                'error': f"HTTP {response.status_code}" if response.status_code != 200 else None
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
        print("1) Auth login...")
        
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        result = self.make_request('POST', '/auth/login', data=login_data)
        
        if result['success']:
            token_data = result['data']
            self.auth_token = token_data.get('access_token')
            if self.auth_token:
                print("   ✅ PASS - Login successful")
                return True
            else:
                print("   ❌ FAIL - No access token in response")
                return False
        else:
            print(f"   ❌ FAIL - Login failed: {result.get('error', 'Unknown error')}")
            return False

    def test_ultra_pillars(self):
        """Test 2: GET /api/ultra/pillars"""
        print("2) GET /api/ultra/pillars...")
        
        result = self.make_request('GET', '/ultra/pillars', use_auth=True)
        
        if result['success']:
            pillars = result['data']
            if isinstance(pillars, list):
                print(f"   ✅ PASS - Got {len(pillars)} pillars")
                if pillars:
                    first_pillar = pillars[0]
                    sample_fields = {k: v for k, v in first_pillar.items() if k in ['id', 'name', 'description']}
                    print(f"   📋 First item sample: {json.dumps(sample_fields, indent=2)}")
                return True
            else:
                print(f"   ❌ FAIL - Expected list, got: {type(pillars)}")
                return False
        else:
            print(f"   ❌ FAIL - Request failed: {result.get('error', 'Unknown error')}")
            return False

    def test_ultra_areas(self):
        """Test 3: GET /api/ultra/areas"""
        print("3) GET /api/ultra/areas...")
        
        result = self.make_request('GET', '/ultra/areas', use_auth=True)
        
        if result['success']:
            areas = result['data']
            if isinstance(areas, list):
                print(f"   ✅ PASS - Got {len(areas)} areas")
                if areas:
                    first_area = areas[0]
                    sample_fields = {k: v for k, v in first_area.items() if k in ['id', 'name', 'description', 'pillar_id']}
                    print(f"   📋 First item sample: {json.dumps(sample_fields, indent=2)}")
                return True
            else:
                print(f"   ❌ FAIL - Expected list, got: {type(areas)}")
                return False
        else:
            print(f"   ❌ FAIL - Request failed: {result.get('error', 'Unknown error')}")
            return False

    def test_ultra_projects(self):
        """Test 4: GET /api/ultra/projects"""
        print("4) GET /api/ultra/projects...")
        
        result = self.make_request('GET', '/ultra/projects', use_auth=True)
        
        if result['success']:
            projects = result['data']
            if isinstance(projects, list):
                print(f"   ✅ PASS - Got {len(projects)} projects")
                if projects:
                    first_project = projects[0]
                    sample_fields = {k: v for k, v in first_project.items() if k in ['id', 'name', 'description', 'area_id', 'status']}
                    print(f"   📋 First item sample: {json.dumps(sample_fields, indent=2)}")
                return True
            else:
                print(f"   ❌ FAIL - Expected list, got: {type(projects)}")
                return False
        else:
            print(f"   ❌ FAIL - Request failed: {result.get('error', 'Unknown error')}")
            return False

    def run_hierarchy_smoke_test(self):
        """Run the hierarchy smoke test"""
        print("🔍 HIERARCHY ENDPOINTS BACKEND SMOKE TEST")
        print("=" * 60)
        print(f"Backend URL: {self.base_url}")
        print(f"Test User: {self.test_user_email}")
        print("=" * 60)
        
        # Run tests in sequence
        tests = [
            ("Auth Login", self.test_auth_login),
            ("Ultra Pillars", self.test_ultra_pillars),
            ("Ultra Areas", self.test_ultra_areas),
            ("Ultra Projects", self.test_ultra_projects)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_method in tests:
            try:
                if test_method():
                    passed += 1
                else:
                    # If auth fails, skip remaining tests
                    if test_name == "Auth Login":
                        print("\n❌ Authentication failed - skipping remaining tests")
                        break
            except Exception as e:
                print(f"   ❌ FAIL - Exception: {e}")
        
        print("\n" + "=" * 60)
        print("📊 HIERARCHY SMOKE TEST RESULTS")
        print("=" * 60)
        print(f"Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("✅ ALL HIERARCHY ENDPOINTS WORKING")
        else:
            print("❌ SOME HIERARCHY ENDPOINTS FAILED")
        
        print("=" * 60)
        
        return passed == total

def main():
    """Run Hierarchy Smoke Test"""
    tester = HierarchySmokeTest()
    
    try:
        success = tester.run_hierarchy_smoke_test()
        return success
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR during testing: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)