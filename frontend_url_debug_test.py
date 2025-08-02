#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from typing import Dict, Any, List

# Configuration - Use frontend's configured URL
FRONTEND_BACKEND_URL = "https://b84aab6d-1bd6-4178-9176-a3c205280a1e.preview.emergentagent.com"
API_BASE = f"{FRONTEND_BACKEND_URL}/api"

class FrontendUrlDebugSuite:
    """Debug suite using frontend's configured backend URL"""
    
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "nav.test@aurumlife.com"
        self.test_user_password = "testpassword123"
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
            
            print(f"🔐 Authenticating with {self.test_user_email} using frontend URL...")
            print(f"🔗 Backend URL: {FRONTEND_BACKEND_URL}")
            
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
        
    async def test_daily_reflection_with_frontend_url(self):
        """Test Daily Reflection Creation with Frontend's Backend URL"""
        print("\n🧪 Testing Daily Reflection Creation with Frontend's Backend URL")
        print(f"🔗 Using URL: {FRONTEND_BACKEND_URL}")
        
        try:
            # Complete reflection data as specified in review request
            complete_reflection = {
                "reflection_text": "Test reflection for debugging with frontend URL",
                "completion_score": 7,
                "mood": "productive",
                "biggest_accomplishment": "Fixed the API",
                "challenges_faced": "Backend debugging",
                "tomorrow_focus": "Continue testing"
            }
            
            print(f"📤 Sending reflection data to: {API_BASE}/ai/daily-reflection")
            
            async with self.session.post(
                f"{API_BASE}/ai/daily-reflection", 
                json=complete_reflection, 
                headers=self.get_auth_headers()
            ) as response:
                
                print(f"📥 Response status: {response.status}")
                print(f"📥 Response headers: {dict(response.headers)}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Daily reflection created successfully with frontend URL!")
                    print(f"📝 Response data: {json.dumps(data, indent=2)}")
                    
                    self.test_results.append({
                        "test": "Daily Reflection with Frontend URL", 
                        "status": "PASSED", 
                        "details": "Successfully created using frontend's backend URL"
                    })
                    return True
                        
                elif response.status == 500:
                    error_text = await response.text()
                    print(f"❌ 500 SERVER ERROR DETECTED with frontend URL!")
                    print(f"💥 Error details: {error_text}")
                    
                    try:
                        error_json = await response.json()
                        print(f"💥 Error JSON: {json.dumps(error_json, indent=2)}")
                    except:
                        print("💥 Error response is not JSON")
                    
                    self.test_results.append({
                        "test": "Daily Reflection with Frontend URL", 
                        "status": "FAILED", 
                        "reason": f"500 Server Error: {error_text[:200]}"
                    })
                    return False
                    
                else:
                    error_text = await response.text()
                    print(f"❌ Daily reflection creation failed: {response.status}")
                    print(f"💥 Error details: {error_text}")
                    
                    self.test_results.append({
                        "test": "Daily Reflection with Frontend URL", 
                        "status": "FAILED", 
                        "reason": f"HTTP {response.status}: {error_text[:200]}"
                    })
                    return False
                    
        except Exception as e:
            print(f"❌ Daily reflection test with frontend URL failed: {e}")
            self.test_results.append({
                "test": "Daily Reflection with Frontend URL", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return False
            
    async def test_connectivity(self):
        """Test basic connectivity to frontend's backend URL"""
        print("\n🧪 Testing Basic Connectivity to Frontend's Backend URL")
        
        try:
            print(f"🔗 Testing connectivity to: {FRONTEND_BACKEND_URL}")
            
            async with self.session.get(f"{FRONTEND_BACKEND_URL}/") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Backend is accessible at frontend URL")
                    print(f"📝 Response: {data}")
                    
                    self.test_results.append({
                        "test": "Frontend URL Connectivity", 
                        "status": "PASSED", 
                        "details": "Backend accessible at frontend's configured URL"
                    })
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Backend not accessible: {response.status} - {error_text}")
                    
                    self.test_results.append({
                        "test": "Frontend URL Connectivity", 
                        "status": "FAILED", 
                        "reason": f"HTTP {response.status}: {error_text[:200]}"
                    })
                    return False
                    
        except Exception as e:
            print(f"❌ Connectivity test failed: {e}")
            self.test_results.append({
                "test": "Frontend URL Connectivity", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return False
            
    def print_debug_summary(self):
        """Print debug test summary"""
        print("\n" + "="*80)
        print("🔍 FRONTEND URL DEBUG - TEST SUMMARY")
        print("="*80)
        
        passed = len([t for t in self.test_results if t["status"] == "PASSED"])
        failed = len([t for t in self.test_results if t["status"] == "FAILED"])
        total = len(self.test_results)
        
        print(f"📊 OVERALL RESULTS: {passed}/{total} tests passed")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status_icon = {"PASSED": "✅", "FAILED": "❌", "PARTIAL": "⚠️", "SKIPPED": "⏭️"}
            icon = status_icon.get(result["status"], "❓")
            print(f"{i:2d}. {icon} {result['test']}: {result['status']}")
            
            if "details" in result:
                print(f"    📝 {result['details']}")
            if "reason" in result:
                print(f"    💬 {result['reason']}")
                
        print("\n" + "="*80)
        
        # Determine if URL is the issue
        connectivity_failed = any(
            "Connectivity" in t["test"] and t["status"] == "FAILED" 
            for t in self.test_results
        )
        
        reflection_failed = any(
            "Daily Reflection" in t["test"] and t["status"] == "FAILED" 
            for t in self.test_results
        )
        
        if connectivity_failed:
            print("🎯 ROOT CAUSE: FRONTEND URL CONNECTIVITY ISSUE")
            print("❌ The frontend's configured backend URL is not accessible")
            print("🔧 SOLUTION: Update frontend/.env REACT_APP_BACKEND_URL to correct URL")
        elif reflection_failed:
            print("🎯 ROOT CAUSE: DAILY REFLECTION ENDPOINT ISSUE WITH FRONTEND URL")
            print("❌ The endpoint fails when accessed via frontend's configured URL")
            print("🔧 SOLUTION: Check URL routing and backend configuration")
        else:
            print("🎯 FRONTEND URL CONFIGURATION APPEARS CORRECT")
            print("✅ Backend is accessible via frontend's configured URL")
            
        print("="*80)
        
    async def run_debug_tests(self):
        """Run debug tests with frontend's backend URL"""
        print("🚀 Starting Frontend URL Debug Testing...")
        print(f"🔗 Frontend Backend URL: {FRONTEND_BACKEND_URL}")
        print("🎯 Focus: Testing if frontend URL configuration causes 500 errors")
        
        await self.setup_session()
        
        try:
            # Test connectivity first
            connectivity_ok = await self.test_connectivity()
            
            if connectivity_ok:
                # Try authentication
                if await self.authenticate():
                    # Test daily reflection endpoint
                    await self.test_daily_reflection_with_frontend_url()
                else:
                    print("❌ Authentication failed - cannot test reflection endpoint")
            else:
                print("❌ Connectivity failed - cannot proceed with tests")
                
        finally:
            await self.cleanup_session()
            
        # Print summary
        self.print_debug_summary()

async def main():
    """Main function to run frontend URL debug tests"""
    debug_suite = FrontendUrlDebugSuite()
    await debug_suite.run_debug_tests()

if __name__ == "__main__":
    asyncio.run(main())