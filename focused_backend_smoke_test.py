#!/usr/bin/env python3
"""
Focused Backend Smoke Test per test_result.md requirements
Tests login → profile → dashboard → core data endpoints → optional discovery
"""

import requests
import json
import time
import os
from datetime import datetime

# Get base URL from frontend/.env
def get_base_url():
    """Get the production-configured backend URL"""
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading frontend/.env: {e}")
    
    # Fallback
    return "https://hierarchy-master.preview.emergentagent.com"

BASE_URL = get_base_url()
print(f"🌐 Using base URL: {BASE_URL}")

# Test credentials in order
CREDENTIALS = [
    {"email": "marc.alleyne@aurumtechnologyltd.com", "password": "password123"},
    {"email": "marc.alleyne@aurumtechnologyltd.com", "password": "password"},
    {"email": "final.test@aurumlife.com", "password": "password123"}
]

class BackendSmokeTest:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Backend-Smoke-Test/1.0'
        })
        self.access_token = None
        self.test_results = []
        self.start_time = time.time()
    
    def log_result(self, endpoint, status_code, response_time_ms, note=""):
        """Log test result"""
        result = {
            'endpoint': endpoint,
            'status': status_code,
            'response_time_ms': response_time_ms,
            'note': note,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status_code == 200 else "❌" if status_code >= 400 else "⚠️"
        print(f"{status_emoji} {endpoint} → {status_code} ({response_time_ms}ms) {note}")
    
    def make_request(self, method, endpoint, **kwargs):
        """Make HTTP request with timing"""
        url = f"{BASE_URL}{endpoint}"
        start_time = time.time()
        
        try:
            response = self.session.request(method, url, timeout=10, **kwargs)
            response_time = int((time.time() - start_time) * 1000)
            return response, response_time
        except Exception as e:
            response_time = int((time.time() - start_time) * 1000)
            print(f"❌ Request failed: {e}")
            return None, response_time
    
    def test_login(self):
        """Test login with credentials in order, stop at first 200"""
        print("\n🔐 Testing Login Flow...")
        
        for i, creds in enumerate(CREDENTIALS, 1):
            print(f"  Trying credentials {i}: {creds['email']}")
            
            response, response_time = self.make_request(
                'POST', 
                '/api/auth/login',
                json=creds
            )
            
            if response is None:
                self.log_result('/api/auth/login', 0, response_time, f"Request failed for {creds['email']}")
                continue
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'access_token' in data and data.get('token_type') == 'bearer':
                        self.access_token = data['access_token']
                        self.session.headers['Authorization'] = f"Bearer {self.access_token}"
                        self.log_result('/api/auth/login', 200, response_time, f"Success with {creds['email']}")
                        return True
                    else:
                        self.log_result('/api/auth/login', 200, response_time, f"Missing token fields for {creds['email']}")
                except json.JSONDecodeError:
                    self.log_result('/api/auth/login', 200, response_time, f"Invalid JSON response for {creds['email']}")
            else:
                self.log_result('/api/auth/login', response.status_code, response_time, f"Failed for {creds['email']}")
        
        print("❌ All login attempts failed")
        return False
    
    def test_profile(self):
        """Test GET /api/auth/me with Bearer token"""
        print("\n👤 Testing Profile Endpoint...")
        
        if not self.access_token:
            self.log_result('/api/auth/me', 0, 0, "No access token available")
            return False
        
        response, response_time = self.make_request('GET', '/api/auth/me')
        
        if response is None:
            self.log_result('/api/auth/me', 0, response_time, "Request failed")
            return False
        
        if response.status_code == 200:
            try:
                data = response.json()
                user_fields = ['id', 'email']
                present_fields = [field for field in user_fields if field in data]
                self.log_result('/api/auth/me', 200, response_time, f"Profile fields: {', '.join(present_fields)}")
                return True
            except json.JSONDecodeError:
                self.log_result('/api/auth/me', 200, response_time, "Invalid JSON response")
        else:
            self.log_result('/api/auth/me', response.status_code, response_time, "Profile request failed")
        
        return False
    
    def test_dashboard(self):
        """Test dashboard endpoints with fallback logic"""
        print("\n📊 Testing Dashboard Endpoints...")
        
        if not self.access_token:
            self.log_result('/api/ultra/dashboard', 0, 0, "No access token available")
            return False
        
        # Try /api/ultra/dashboard first
        response, response_time = self.make_request('GET', '/api/ultra/dashboard')
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                self.log_result('/api/ultra/dashboard', 200, response_time, "Ultra dashboard success")
                return True
            except json.JSONDecodeError:
                self.log_result('/api/ultra/dashboard', 200, response_time, "Invalid JSON from ultra dashboard")
        else:
            status = response.status_code if response else 0
            note = "Ultra dashboard failed" if status in [401, 500] else f"Ultra dashboard error: {status}"
            self.log_result('/api/ultra/dashboard', status, response_time, note)
        
        # Fallback to /api/dashboard
        print("  Trying fallback dashboard...")
        response, response_time = self.make_request('GET', '/api/dashboard')
        
        if response and response.status_code == 200:
            try:
                data = response.json()
                self.log_result('/api/dashboard', 200, response_time, "Fallback dashboard success")
                return True
            except json.JSONDecodeError:
                self.log_result('/api/dashboard', 200, response_time, "Invalid JSON from fallback dashboard")
        else:
            status = response.status_code if response else 0
            self.log_result('/api/dashboard', status, response_time, "Fallback dashboard failed")
        
        return False
    
    def test_core_data_endpoints(self):
        """Test core data endpoints: pillars, areas, projects, tasks"""
        print("\n📋 Testing Core Data Endpoints...")
        
        if not self.access_token:
            print("❌ No access token available for core data tests")
            return 0
        
        endpoints = ['/api/pillars', '/api/areas', '/api/projects', '/api/tasks']
        success_count = 0
        
        for endpoint in endpoints:
            response, response_time = self.make_request('GET', endpoint)
            
            if response and response.status_code == 200:
                try:
                    data = response.json()
                    count = len(data) if isinstance(data, list) else "N/A"
                    self.log_result(endpoint, 200, response_time, f"Count: {count}")
                    success_count += 1
                except json.JSONDecodeError:
                    self.log_result(endpoint, 200, response_time, "Invalid JSON response")
            else:
                status = response.status_code if response else 0
                self.log_result(endpoint, status, response_time, "Request failed")
        
        return success_count
    
    def test_optional_discovery(self):
        """Optional discovery of Insights and AI Coach endpoints"""
        print("\n🔍 Testing Optional Discovery...")
        
        if not self.access_token:
            print("❌ No access token available for discovery")
            return
        
        # Try to get OpenAPI spec
        response, response_time = self.make_request('GET', '/api/openapi.json')
        
        if response and response.status_code == 200:
            try:
                openapi_data = response.json()
                self.log_result('/api/openapi.json', 200, response_time, "OpenAPI spec retrieved")
                
                # Look for insights and AI coach endpoints
                paths = openapi_data.get('paths', {})
                insights_endpoints = [path for path in paths.keys() if 'insight' in path.lower()]
                ai_coach_endpoints = [path for path in paths.keys() if 'ai' in path.lower() and 'coach' in path.lower()]
                
                # Test discovered endpoints (safe GETs only)
                discovered_endpoints = []
                
                # Common patterns to try
                common_endpoints = ['/api/insights', '/api/ai/coach', '/api/ai/coach/quota']
                
                for endpoint in common_endpoints:
                    if endpoint in paths:
                        discovered_endpoints.append(endpoint)
                
                # Test discovered endpoints
                for endpoint in discovered_endpoints[:3]:  # Limit to 3 to avoid overload
                    response, response_time = self.make_request('GET', endpoint)
                    if response:
                        note = "Discovered endpoint" if response.status_code == 200 else "Discovered but failed"
                        self.log_result(endpoint, response.status_code, response_time, note)
                
                if not discovered_endpoints:
                    print("  No primary Insights/AI Coach endpoints found in OpenAPI spec")
                    
            except json.JSONDecodeError:
                self.log_result('/api/openapi.json', 200, response_time, "Invalid OpenAPI JSON")
        else:
            status = response.status_code if response else 0
            self.log_result('/api/openapi.json', status, response_time, "OpenAPI spec not available")
            
            # Try common endpoints anyway
            common_endpoints = ['/api/insights', '/api/ai/coach', '/api/ai/quota']
            for endpoint in common_endpoints:
                response, response_time = self.make_request('GET', endpoint)
                if response and response.status_code == 200:
                    self.log_result(endpoint, 200, response_time, "Found without OpenAPI")
    
    def run_smoke_test(self):
        """Run the complete smoke test"""
        print("🚀 Starting Backend Smoke Test")
        print(f"📅 Test started at: {datetime.now().isoformat()}")
        print(f"🌐 Base URL: {BASE_URL}")
        print("=" * 60)
        
        # Step 1: Login
        login_success = self.test_login()
        if not login_success:
            print("\n❌ SMOKE TEST FAILED: Could not authenticate")
            return self.generate_final_report(False)
        
        # Step 2: Profile
        profile_success = self.test_profile()
        
        # Step 3: Dashboard
        dashboard_success = self.test_dashboard()
        
        # Step 4: Core data endpoints
        core_success_count = self.test_core_data_endpoints()
        
        # Step 5: Optional discovery
        self.test_optional_discovery()
        
        # Determine overall success
        # PASS if: login + profile + (ultra_dashboard OR dashboard) + at least 2 core endpoints
        overall_success = (
            login_success and 
            profile_success and 
            dashboard_success and 
            core_success_count >= 2
        )
        
        return self.generate_final_report(overall_success)
    
    def generate_final_report(self, overall_success):
        """Generate final test report"""
        total_time = int((time.time() - self.start_time) * 1000)
        
        print("\n" + "=" * 60)
        print("📊 SMOKE TEST RESULTS")
        print("=" * 60)
        
        # Summary by endpoint
        for result in self.test_results:
            status_emoji = "✅" if result['status'] == 200 else "❌" if result['status'] >= 400 else "⚠️"
            print(f"{status_emoji} {result['endpoint']} → {result['status']} ({result['response_time_ms']}ms) {result['note']}")
        
        print("\n" + "-" * 60)
        
        # Final verdict
        verdict = "PASS" if overall_success else "FAIL"
        verdict_emoji = "✅" if overall_success else "❌"
        
        print(f"{verdict_emoji} FINAL VERDICT: {verdict}")
        print(f"⏱️  Total test time: {total_time}ms")
        print(f"📈 Total requests: {len(self.test_results)}")
        
        # Success criteria breakdown
        login_results = [r for r in self.test_results if '/auth/login' in r['endpoint']]
        profile_results = [r for r in self.test_results if '/auth/me' in r['endpoint']]
        dashboard_results = [r for r in self.test_results if 'dashboard' in r['endpoint']]
        core_results = [r for r in self.test_results if r['endpoint'] in ['/api/pillars', '/api/areas', '/api/projects', '/api/tasks']]
        
        login_success = any(r['status'] == 200 for r in login_results)
        profile_success = any(r['status'] == 200 for r in profile_results)
        dashboard_success = any(r['status'] == 200 for r in dashboard_results)
        core_success_count = sum(1 for r in core_results if r['status'] == 200)
        
        print(f"🔐 Login: {'✅' if login_success else '❌'}")
        print(f"👤 Profile: {'✅' if profile_success else '❌'}")
        print(f"📊 Dashboard: {'✅' if dashboard_success else '❌'}")
        print(f"📋 Core endpoints (≥2): {'✅' if core_success_count >= 2 else '❌'} ({core_success_count}/4)")
        
        return {
            'success': overall_success,
            'verdict': verdict,
            'total_time_ms': total_time,
            'results': self.test_results,
            'summary': {
                'login_success': login_success,
                'profile_success': profile_success,
                'dashboard_success': dashboard_success,
                'core_success_count': core_success_count
            }
        }

if __name__ == "__main__":
    test = BackendSmokeTest()
    result = test.run_smoke_test()
    
    # Exit with appropriate code
    exit(0 if result['success'] else 1)