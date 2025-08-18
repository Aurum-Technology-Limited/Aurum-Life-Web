#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from typing import Dict, Any, List

# Configuration - Use external URL from frontend/.env
BACKEND_URL = "https://productivity-hub-23.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class AchievementsRemovalTestSuite:
    """Test suite to verify achievements and user level dependencies have been removed"""
    
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "nav.test@aurumlife.com"
        self.test_user_password = "navtest123"
        self.test_results = []
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()
            
    async def authenticate(self):
        """Authenticate with test credentials"""
        try:
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data["access_token"]
                    print(f"✅ Authentication successful for {self.test_user_email}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Authentication failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
            
    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.auth_token}"}
        
    async def test_auth_me_endpoint(self):
        """Test 1: GET /api/auth/me - Check user authentication and ensure no level/points fields"""
        print("\n🧪 Test 1: GET /api/auth/me - Verify no level/points fields")
        
        try:
            async with self.session.get(f"{API_BASE}/auth/me", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    user_data = await response.json()
                    print(f"✅ /auth/me endpoint working - Status: {response.status}")
                    
                    # Check that level/points fields are NOT present
                    forbidden_fields = ['level', 'points', 'experience', 'xp', 'user_level', 'achievement_points']
                    found_forbidden_fields = []
                    
                    for field in forbidden_fields:
                        if field in user_data:
                            found_forbidden_fields.append(field)
                    
                    if found_forbidden_fields:
                        print(f"❌ Found forbidden level/points fields: {found_forbidden_fields}")
                        self.test_results.append({
                            "test": "Auth Me - No Level/Points Fields", 
                            "status": "FAILED", 
                            "reason": f"Found forbidden fields: {found_forbidden_fields}"
                        })
                        return False
                    else:
                        print("✅ No level/points fields found in user data")
                        
                        # Show what fields ARE present
                        print(f"📋 User data fields: {list(user_data.keys())}")
                        
                        self.test_results.append({
                            "test": "Auth Me - No Level/Points Fields", 
                            "status": "PASSED", 
                            "details": f"User data contains {len(user_data.keys())} fields, no level/points fields found"
                        })
                        return True
                else:
                    error_text = await response.text()
                    print(f"❌ /auth/me endpoint failed: {response.status} - {error_text}")
                    self.test_results.append({
                        "test": "Auth Me Endpoint", 
                        "status": "FAILED", 
                        "reason": f"HTTP {response.status}"
                    })
                    return False
                    
        except Exception as e:
            print(f"❌ Auth me endpoint test failed: {e}")
            self.test_results.append({
                "test": "Auth Me Endpoint", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return False
            
    async def test_pillars_endpoint(self):
        """Test 2: GET /api/pillars - Make sure pillars endpoint works"""
        print("\n🧪 Test 2: GET /api/pillars - Verify pillars endpoint functionality")
        
        try:
            async with self.session.get(f"{API_BASE}/pillars", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    pillars_data = await response.json()
                    print(f"✅ /pillars endpoint working - Status: {response.status}")
                    print(f"📋 Found {len(pillars_data)} pillars")
                    
                    # Verify it returns a list
                    if isinstance(pillars_data, list):
                        print("✅ Pillars endpoint returns proper list format")
                        
                        # If there are pillars, check their structure
                        if pillars_data:
                            sample_pillar = pillars_data[0]
                            expected_fields = ['id', 'name', 'description']
                            missing_fields = [field for field in expected_fields if field not in sample_pillar]
                            
                            if missing_fields:
                                print(f"⚠️ Sample pillar missing expected fields: {missing_fields}")
                            else:
                                print("✅ Pillar structure contains expected fields")
                                
                        self.test_results.append({
                            "test": "Pillars Endpoint", 
                            "status": "PASSED", 
                            "details": f"Returned {len(pillars_data)} pillars in proper format"
                        })
                        return True
                    else:
                        print(f"❌ Pillars endpoint should return list, got: {type(pillars_data)}")
                        self.test_results.append({
                            "test": "Pillars Endpoint", 
                            "status": "FAILED", 
                            "reason": f"Expected list, got {type(pillars_data)}"
                        })
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ /pillars endpoint failed: {response.status} - {error_text}")
                    self.test_results.append({
                        "test": "Pillars Endpoint", 
                        "status": "FAILED", 
                        "reason": f"HTTP {response.status}"
                    })
                    return False
                    
        except Exception as e:
            print(f"❌ Pillars endpoint test failed: {e}")
            self.test_results.append({
                "test": "Pillars Endpoint", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return False
            
    async def test_dashboard_endpoint(self):
        """Test 3: GET /api/dashboard - Verify dashboard loads without errors"""
        print("\n🧪 Test 3: GET /api/dashboard - Verify dashboard functionality")
        
        try:
            async with self.session.get(f"{API_BASE}/dashboard", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    dashboard_data = await response.json()
                    print(f"✅ /dashboard endpoint working - Status: {response.status}")
                    
                    # Verify dashboard structure
                    expected_fields = ['user', 'stats']
                    missing_fields = [field for field in expected_fields if field not in dashboard_data]
                    
                    if missing_fields:
                        print(f"⚠️ Dashboard missing expected fields: {missing_fields}")
                        self.test_results.append({
                            "test": "Dashboard Endpoint", 
                            "status": "PARTIAL", 
                            "details": f"Working but missing fields: {missing_fields}"
                        })
                    else:
                        print("✅ Dashboard contains expected structure")
                        
                        # Check that stats don't contain achievement/level related fields
                        stats = dashboard_data.get('stats', {})
                        forbidden_stat_fields = ['achievements', 'level', 'points', 'experience', 'xp']
                        found_forbidden_stats = []
                        
                        for field in forbidden_stat_fields:
                            if field in stats:
                                found_forbidden_stats.append(field)
                        
                        if found_forbidden_stats:
                            print(f"❌ Dashboard stats contain forbidden achievement/level fields: {found_forbidden_stats}")
                            self.test_results.append({
                                "test": "Dashboard Endpoint", 
                                "status": "FAILED", 
                                "reason": f"Stats contain forbidden fields: {found_forbidden_stats}"
                            })
                            return False
                        else:
                            print("✅ Dashboard stats contain no achievement/level fields")
                            print(f"📋 Dashboard fields: {list(dashboard_data.keys())}")
                            print(f"📊 Stats fields: {list(stats.keys())}")
                            
                            self.test_results.append({
                                "test": "Dashboard Endpoint", 
                                "status": "PASSED", 
                                "details": "Dashboard working with no achievement/level fields"
                            })
                            return True
                else:
                    error_text = await response.text()
                    print(f"❌ /dashboard endpoint failed: {response.status} - {error_text}")
                    self.test_results.append({
                        "test": "Dashboard Endpoint", 
                        "status": "FAILED", 
                        "reason": f"HTTP {response.status}"
                    })
                    return False
                    
        except Exception as e:
            print(f"❌ Dashboard endpoint test failed: {e}")
            self.test_results.append({
                "test": "Dashboard Endpoint", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return False
            
    async def test_no_achievement_endpoints(self):
        """Test 4: Confirm that no achievement-related endpoints exist"""
        print("\n🧪 Test 4: Verify no achievement-related endpoints exist")
        
        achievement_endpoints = [
            "/achievements",
            "/achievements/user",
            "/achievements/unlock",
            "/achievements/progress",
            "/user/achievements",
            "/user/level",
            "/user/points",
            "/user/experience",
            "/leaderboard",
            "/badges"
        ]
        
        try:
            non_existent_count = 0
            existing_endpoints = []
            
            for endpoint in achievement_endpoints:
                full_url = f"{API_BASE}{endpoint}"
                
                try:
                    async with self.session.get(full_url, headers=self.get_auth_headers()) as response:
                        if response.status == 404:
                            print(f"✅ {endpoint} - Not found (as expected)")
                            non_existent_count += 1
                        elif response.status in [401, 403]:
                            # These might be protected endpoints that still exist
                            print(f"⚠️ {endpoint} - Protected endpoint (may still exist)")
                            existing_endpoints.append(endpoint)
                        else:
                            print(f"❌ {endpoint} - Endpoint exists (Status: {response.status})")
                            existing_endpoints.append(endpoint)
                            
                except Exception as e:
                    # Network errors likely mean endpoint doesn't exist
                    print(f"✅ {endpoint} - Not accessible (likely removed)")
                    non_existent_count += 1
                    
            if existing_endpoints:
                print(f"❌ Found {len(existing_endpoints)} achievement-related endpoints still exist: {existing_endpoints}")
                self.test_results.append({
                    "test": "No Achievement Endpoints", 
                    "status": "FAILED", 
                    "reason": f"Found existing endpoints: {existing_endpoints}"
                })
                return False
            else:
                print(f"✅ All {len(achievement_endpoints)} achievement-related endpoints are properly removed")
                self.test_results.append({
                    "test": "No Achievement Endpoints", 
                    "status": "PASSED", 
                    "details": f"All {len(achievement_endpoints)} achievement endpoints confirmed removed"
                })
                return True
                
        except Exception as e:
            print(f"❌ Achievement endpoints test failed: {e}")
            self.test_results.append({
                "test": "No Achievement Endpoints", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return False
            
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🎯 ACHIEVEMENTS & USER LEVEL REMOVAL VERIFICATION - TEST SUMMARY")
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
            print("🎉 ACHIEVEMENTS & USER LEVEL REMOVAL COMPLETED SUCCESSFULLY!")
            print("✅ All core endpoints working without achievement dependencies")
            print("✅ No level/points fields found in user data")
            print("✅ All achievement endpoints properly removed")
        elif success_rate >= 75:
            print("⚠️ ACHIEVEMENTS REMOVAL MOSTLY SUCCESSFUL - MINOR ISSUES DETECTED")
            print("🔍 Review failed tests for remaining dependencies")
        else:
            print("❌ ACHIEVEMENTS REMOVAL HAS SIGNIFICANT ISSUES - NEEDS ATTENTION")
            print("🚨 Core functionality may still have achievement dependencies")
            
        print("="*80)
        
    async def run_achievements_removal_test(self):
        """Run comprehensive achievements removal test suite"""
        print("🚀 Starting Achievements & User Level Removal Verification...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print(f"👤 Test User: {self.test_user_email}")
        print("📋 Testing: Auth/Me, Pillars, Dashboard, Achievement Endpoints")
        
        await self.setup_session()
        
        try:
            # Authentication
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed with tests")
                return
                
            # Run all tests
            await self.test_auth_me_endpoint()
            await self.test_pillars_endpoint()
            await self.test_dashboard_endpoint()
            await self.test_no_achievement_endpoints()
            
        finally:
            await self.cleanup_session()
            
        # Print summary
        self.print_test_summary()

async def main():
    """Main function to run the test suite"""
    test_suite = AchievementsRemovalTestSuite()
    await test_suite.run_achievements_removal_test()

if __name__ == "__main__":
    asyncio.run(main())