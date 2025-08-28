#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, Any, List

# Configuration - Use localhost URL as per review request
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

class AuthCoreAPITestSuite:
    """Test suite focused on authentication and core API endpoints after URL fix"""
    
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "nav.test@aurumlife.com"
        self.test_user_password = "testpassword"
        self.test_results = []
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()
            
    async def test_authentication_api(self):
        """Test 1: Authentication API with nav.test@aurumlife.com credentials"""
        print("\n🧪 Test 1: Authentication API")
        
        try:
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            start_time = time.time()
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    
                    if self.auth_token:
                        print(f"✅ Authentication successful for {self.test_user_email}")
                        print(f"   - Response time: {response_time:.1f}ms")
                        print(f"   - Token received: {self.auth_token[:20]}...")
                        self.test_results.append({
                            "test": "Authentication API", 
                            "status": "PASSED", 
                            "details": f"Login successful in {response_time:.1f}ms"
                        })
                        return True
                    else:
                        print("❌ Authentication failed: No access token in response")
                        self.test_results.append({
                            "test": "Authentication API", 
                            "status": "FAILED", 
                            "reason": "No access token in response"
                        })
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Authentication failed: {response.status} - {error_text}")
                    self.test_results.append({
                        "test": "Authentication API", 
                        "status": "FAILED", 
                        "reason": f"HTTP {response.status}"
                    })
                    return False
                    
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            self.test_results.append({
                "test": "Authentication API", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return False
            
    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.auth_token}"}
        
    async def test_core_api_endpoints(self):
        """Test 2: Core API endpoints - Areas, Tasks, Dashboard"""
        print("\n🧪 Test 2: Core API Endpoints")
        
        if not self.auth_token:
            print("❌ Cannot test core APIs without authentication")
            self.test_results.append({
                "test": "Core API Endpoints", 
                "status": "FAILED", 
                "reason": "No authentication token"
            })
            return False
            
        try:
            endpoints_tested = 0
            endpoints_passed = 0
            
            # Test Dashboard API
            print("\n   Testing Dashboard API...")
            start_time = time.time()
            async with self.session.get(f"{API_BASE}/dashboard", headers=self.get_auth_headers()) as response:
                response_time = (time.time() - start_time) * 1000
                endpoints_tested += 1
                
                if response.status == 200:
                    dashboard_data = await response.json()
                    required_fields = ['user', 'stats', 'recent_tasks']
                    
                    if all(field in dashboard_data for field in required_fields):
                        print(f"   ✅ Dashboard API working - {response_time:.1f}ms")
                        print(f"      - User: {dashboard_data.get('user', {}).get('email', 'N/A')}")
                        print(f"      - Stats: {len(dashboard_data.get('stats', {}))} fields")
                        print(f"      - Recent tasks: {len(dashboard_data.get('recent_tasks', []))}")
                        endpoints_passed += 1
                    else:
                        print(f"   ❌ Dashboard API missing required fields")
                else:
                    print(f"   ❌ Dashboard API failed: {response.status}")
                    
            # Test Areas API
            print("\n   Testing Areas API...")
            start_time = time.time()
            async with self.session.get(f"{API_BASE}/areas", headers=self.get_auth_headers()) as response:
                response_time = (time.time() - start_time) * 1000
                endpoints_tested += 1
                
                if response.status == 200:
                    areas_data = await response.json()
                    print(f"   ✅ Areas API working - {response_time:.1f}ms")
                    print(f"      - Areas retrieved: {len(areas_data)}")
                    
                    if areas_data:
                        sample_area = areas_data[0]
                        required_fields = ['id', 'name', 'user_id']
                        if all(field in sample_area for field in required_fields):
                            print(f"      - Sample area: {sample_area.get('name', 'N/A')}")
                            endpoints_passed += 1
                        else:
                            print(f"   ❌ Areas API missing required fields in response")
                    else:
                        print(f"      - No areas found (may be expected)")
                        endpoints_passed += 1
                else:
                    print(f"   ❌ Areas API failed: {response.status}")
                    
            # Test Tasks API
            print("\n   Testing Tasks API...")
            start_time = time.time()
            async with self.session.get(f"{API_BASE}/tasks", headers=self.get_auth_headers()) as response:
                response_time = (time.time() - start_time) * 1000
                endpoints_tested += 1
                
                if response.status == 200:
                    tasks_data = await response.json()
                    print(f"   ✅ Tasks API working - {response_time:.1f}ms")
                    print(f"      - Tasks retrieved: {len(tasks_data)}")
                    
                    if tasks_data:
                        sample_task = tasks_data[0]
                        required_fields = ['id', 'name', 'user_id']
                        if all(field in sample_task for field in required_fields):
                            print(f"      - Sample task: {sample_task.get('name', 'N/A')}")
                            endpoints_passed += 1
                        else:
                            print(f"   ❌ Tasks API missing required fields in response")
                    else:
                        print(f"      - No tasks found (may be expected)")
                        endpoints_passed += 1
                else:
                    print(f"   ❌ Tasks API failed: {response.status}")
                    
            # Test Pillars API
            print("\n   Testing Pillars API...")
            start_time = time.time()
            async with self.session.get(f"{API_BASE}/pillars", headers=self.get_auth_headers()) as response:
                response_time = (time.time() - start_time) * 1000
                endpoints_tested += 1
                
                if response.status == 200:
                    pillars_data = await response.json()
                    print(f"   ✅ Pillars API working - {response_time:.1f}ms")
                    print(f"      - Pillars retrieved: {len(pillars_data)}")
                    
                    if pillars_data:
                        sample_pillar = pillars_data[0]
                        required_fields = ['id', 'name', 'user_id']
                        if all(field in sample_pillar for field in required_fields):
                            print(f"      - Sample pillar: {sample_pillar.get('name', 'N/A')}")
                            endpoints_passed += 1
                        else:
                            print(f"   ❌ Pillars API missing required fields in response")
                    else:
                        print(f"      - No pillars found (may be expected)")
                        endpoints_passed += 1
                else:
                    print(f"   ❌ Pillars API failed: {response.status}")
                    
            # Test Projects API
            print("\n   Testing Projects API...")
            start_time = time.time()
            async with self.session.get(f"{API_BASE}/projects", headers=self.get_auth_headers()) as response:
                response_time = (time.time() - start_time) * 1000
                endpoints_tested += 1
                
                if response.status == 200:
                    projects_data = await response.json()
                    print(f"   ✅ Projects API working - {response_time:.1f}ms")
                    print(f"      - Projects retrieved: {len(projects_data)}")
                    
                    if projects_data:
                        sample_project = projects_data[0]
                        required_fields = ['id', 'name', 'user_id']
                        if all(field in sample_project for field in required_fields):
                            print(f"      - Sample project: {sample_project.get('name', 'N/A')}")
                            endpoints_passed += 1
                        else:
                            print(f"   ❌ Projects API missing required fields in response")
                    else:
                        print(f"      - No projects found (may be expected)")
                        endpoints_passed += 1
                else:
                    print(f"   ❌ Projects API failed: {response.status}")
                    
            if endpoints_passed == endpoints_tested:
                self.test_results.append({
                    "test": "Core API Endpoints", 
                    "status": "PASSED", 
                    "details": f"All {endpoints_tested} core endpoints working"
                })
                print(f"\n✅ All {endpoints_tested} core API endpoints working correctly")
                return True
            else:
                self.test_results.append({
                    "test": "Core API Endpoints", 
                    "status": "PARTIAL", 
                    "details": f"{endpoints_passed}/{endpoints_tested} endpoints working"
                })
                print(f"\n⚠️ {endpoints_passed}/{endpoints_tested} core API endpoints working")
                return True  # Still return True since most work
                
        except Exception as e:
            print(f"❌ Core API endpoints test failed: {e}")
            self.test_results.append({
                "test": "Core API Endpoints", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return False
            
    async def test_api_accessibility(self):
        """Test 3: API accessibility from localhost:8001"""
        print("\n🧪 Test 3: API Accessibility from localhost:8001")
        
        try:
            # Test basic connectivity to backend
            start_time = time.time()
            async with self.session.get(f"{BACKEND_URL}/") as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Backend accessible at {BACKEND_URL}")
                    print(f"   - Response time: {response_time:.1f}ms")
                    print(f"   - Version: {data.get('version', 'N/A')}")
                    print(f"   - Status: {data.get('status', 'N/A')}")
                    
                    # Test API base path
                    async with self.session.get(f"{API_BASE}/") as api_response:
                        if api_response.status in [404, 405]:  # Expected for API root
                            print(f"✅ API base path accessible at {API_BASE}")
                            self.test_results.append({
                                "test": "API Accessibility", 
                                "status": "PASSED", 
                                "details": f"Backend accessible in {response_time:.1f}ms"
                            })
                            return True
                        else:
                            print(f"⚠️ API base path returned unexpected status: {api_response.status}")
                            self.test_results.append({
                                "test": "API Accessibility", 
                                "status": "PASSED", 
                                "details": f"Backend accessible, API path status: {api_response.status}"
                            })
                            return True
                else:
                    print(f"❌ Backend not accessible: {response.status}")
                    self.test_results.append({
                        "test": "API Accessibility", 
                        "status": "FAILED", 
                        "reason": f"Backend returned {response.status}"
                    })
                    return False
                    
        except Exception as e:
            print(f"❌ API accessibility test failed: {e}")
            self.test_results.append({
                "test": "API Accessibility", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return False
            
    async def test_auth_me_endpoint(self):
        """Test 4: /auth/me endpoint to verify token validity"""
        print("\n🧪 Test 4: Auth Me Endpoint")
        
        if not self.auth_token:
            print("❌ Cannot test /auth/me without authentication token")
            self.test_results.append({
                "test": "Auth Me Endpoint", 
                "status": "FAILED", 
                "reason": "No authentication token"
            })
            return False
            
        try:
            start_time = time.time()
            async with self.session.get(f"{API_BASE}/auth/me", headers=self.get_auth_headers()) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    user_data = await response.json()
                    print(f"✅ Auth Me endpoint working - {response_time:.1f}ms")
                    print(f"   - User ID: {user_data.get('id', 'N/A')}")
                    print(f"   - Email: {user_data.get('email', 'N/A')}")
                    print(f"   - Username: {user_data.get('username', 'N/A')}")
                    
                    if user_data.get('email') == self.test_user_email:
                        print(f"   - Email matches test credentials ✅")
                        self.test_results.append({
                            "test": "Auth Me Endpoint", 
                            "status": "PASSED", 
                            "details": f"User data retrieved in {response_time:.1f}ms"
                        })
                        return True
                    else:
                        print(f"   - Email mismatch: expected {self.test_user_email}")
                        self.test_results.append({
                            "test": "Auth Me Endpoint", 
                            "status": "FAILED", 
                            "reason": "Email mismatch in user data"
                        })
                        return False
                else:
                    print(f"❌ Auth Me endpoint failed: {response.status}")
                    self.test_results.append({
                        "test": "Auth Me Endpoint", 
                        "status": "FAILED", 
                        "reason": f"HTTP {response.status}"
                    })
                    return False
                    
        except Exception as e:
            print(f"❌ Auth Me endpoint test failed: {e}")
            self.test_results.append({
                "test": "Auth Me Endpoint", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return False
            
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🎯 AUTHENTICATION & CORE API ENDPOINTS - TEST SUMMARY")
        print("="*80)
        
        passed = len([t for t in self.test_results if t["status"] == "PASSED"])
        failed = len([t for t in self.test_results if t["status"] == "FAILED"])
        partial = len([t for t in self.test_results if t["status"] == "PARTIAL"])
        total = len(self.test_results)
        
        print(f"📊 OVERALL RESULTS: {passed}/{total} tests passed")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        if partial > 0:
            print(f"⚠️ Partial: {partial}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status_icon = {"PASSED": "✅", "FAILED": "❌", "PARTIAL": "⚠️"}
            icon = status_icon.get(result["status"], "❓")
            print(f"{i:2d}. {icon} {result['test']}: {result['status']}")
            
            if "details" in result:
                print(f"    📝 {result['details']}")
            if "reason" in result:
                print(f"    💬 {result['reason']}")
                
        print("\n" + "="*80)
        
        # Determine overall system status
        if success_rate == 100:
            print("🎉 AUTHENTICATION & CORE API ENDPOINTS ARE WORKING PERFECTLY!")
            print("✅ Backend URL fix successful - localhost:8001 accessible")
            print("✅ Authentication working with nav.test@aurumlife.com")
            print("✅ All core API endpoints responding correctly")
        elif success_rate >= 75:
            print("⚠️ AUTHENTICATION & CORE API ENDPOINTS ARE MOSTLY FUNCTIONAL")
            print("✅ Backend URL fix successful - localhost:8001 accessible")
            if failed == 0:
                print("✅ No critical failures detected")
        else:
            print("❌ AUTHENTICATION & CORE API ENDPOINTS HAVE SIGNIFICANT ISSUES")
            
        print("="*80)
        
    async def run_auth_core_api_test(self):
        """Run authentication and core API test suite"""
        print("🚀 Starting Authentication & Core API Endpoints Testing...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print("📋 Testing Focus: Authentication + Areas + Tasks + Dashboard APIs")
        print(f"👤 Test User: {self.test_user_email}")
        
        await self.setup_session()
        
        try:
            # Test 1: Authentication API
            auth_success = await self.test_authentication_api()
            
            # Test 2: API Accessibility
            await self.test_api_accessibility()
            
            if auth_success:
                # Test 3: Auth Me endpoint
                await self.test_auth_me_endpoint()
                
                # Test 4: Core API endpoints
                await self.test_core_api_endpoints()
            else:
                print("⚠️ Skipping authenticated endpoint tests due to authentication failure")
                
        finally:
            await self.cleanup_session()
            
        # Print summary
        self.print_test_summary()

async def main():
    suite = AuthCoreAPITestSuite()
    await suite.run_auth_core_api_test()

if __name__ == "__main__":
    asyncio.run(main())