#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from typing import Dict, Any, List

# Test multiple URL configurations
URLS_TO_TEST = [
    "http://localhost:8001",
    "https://15d7219c-892b-4111-8d96-e95547e179d6.preview.emergentagent.com",
    "https://smart-tasks-7.preview.emergentgent.com"
]

class UrlConfigurationDebugSuite:
    """Debug suite to test multiple URL configurations"""
    
    def __init__(self):
        self.session = None
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
            
    async def test_url_connectivity(self, base_url):
        """Test connectivity to a specific URL"""
        try:
            print(f"\n🔗 Testing connectivity to: {base_url}")
            
            # Test root endpoint
            async with self.session.get(f"{base_url}/") as response:
                if response.status == 200:
                    try:
                        data = await response.json()
                        if "message" in data and "Aurum Life API" in data["message"]:
                            print(f"✅ Backend accessible at {base_url}")
                            print(f"📝 Response: {data}")
                            return True
                        else:
                            print(f"⚠️ Unexpected JSON response from {base_url}")
                            return False
                    except:
                        # Not JSON, might be HTML
                        text = await response.text()
                        if "html" in text.lower():
                            print(f"❌ {base_url} returns HTML (not API)")
                            return False
                        else:
                            print(f"⚠️ {base_url} returns non-JSON: {text[:100]}")
                            return False
                else:
                    error_text = await response.text()
                    print(f"❌ {base_url} not accessible: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error testing {base_url}: {e}")
            return False
            
    async def test_daily_reflection_endpoint(self, base_url):
        """Test daily reflection endpoint with a specific URL"""
        try:
            api_base = f"{base_url}/api"
            
            # First authenticate
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            print(f"🔐 Authenticating with {api_base}/auth/login...")
            
            async with self.session.post(f"{api_base}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    auth_token = data["access_token"]
                    print(f"✅ Authentication successful")
                    
                    # Test daily reflection endpoint
                    headers = {"Authorization": f"Bearer {auth_token}"}
                    reflection_data = {
                        "reflection_text": "Test reflection for URL debugging",
                        "completion_score": 8,
                        "mood": "focused"
                    }
                    
                    print(f"📤 Testing daily reflection endpoint...")
                    
                    async with self.session.post(
                        f"{api_base}/ai/daily-reflection", 
                        json=reflection_data, 
                        headers=headers
                    ) as reflection_response:
                        
                        if reflection_response.status == 200:
                            reflection_result = await reflection_response.json()
                            print(f"✅ Daily reflection endpoint working at {base_url}")
                            print(f"📝 Created reflection ID: {reflection_result.get('id', 'N/A')}")
                            return True
                        elif reflection_response.status == 500:
                            error_text = await reflection_response.text()
                            print(f"❌ 500 ERROR at {base_url}/api/ai/daily-reflection")
                            print(f"💥 Error: {error_text}")
                            return False
                        else:
                            error_text = await reflection_response.text()
                            print(f"❌ Daily reflection failed at {base_url}: {reflection_response.status}")
                            print(f"💥 Error: {error_text}")
                            return False
                            
                else:
                    error_text = await response.text()
                    print(f"❌ Authentication failed at {base_url}: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error testing daily reflection at {base_url}: {e}")
            return False
            
    async def run_comprehensive_url_test(self):
        """Test all URL configurations"""
        print("🚀 Starting Comprehensive URL Configuration Testing...")
        print("🎯 Goal: Find which URL configuration works for Evening Reflection API")
        
        await self.setup_session()
        
        working_urls = []
        
        try:
            for base_url in URLS_TO_TEST:
                print(f"\n{'='*60}")
                print(f"🧪 Testing URL: {base_url}")
                print(f"{'='*60}")
                
                # Test connectivity first
                if await self.test_url_connectivity(base_url):
                    # If connectivity works, test the daily reflection endpoint
                    if await self.test_daily_reflection_endpoint(base_url):
                        working_urls.append(base_url)
                        self.test_results.append({
                            "url": base_url,
                            "status": "WORKING",
                            "details": "Both connectivity and daily reflection endpoint working"
                        })
                    else:
                        self.test_results.append({
                            "url": base_url,
                            "status": "PARTIAL",
                            "details": "Connectivity works but daily reflection endpoint fails"
                        })
                else:
                    self.test_results.append({
                        "url": base_url,
                        "status": "FAILED",
                        "details": "No connectivity to backend"
                    })
                    
        finally:
            await self.cleanup_session()
            
        # Print summary
        self.print_url_test_summary(working_urls)
        
    def print_url_test_summary(self, working_urls):
        """Print URL test summary"""
        print("\n" + "="*80)
        print("🔍 URL CONFIGURATION TEST - SUMMARY")
        print("="*80)
        
        print(f"📊 TESTED URLS: {len(URLS_TO_TEST)}")
        print(f"✅ WORKING URLS: {len(working_urls)}")
        print(f"❌ FAILED URLS: {len(URLS_TO_TEST) - len(working_urls)}")
        
        print("\n📋 DETAILED RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status_icon = {"WORKING": "✅", "PARTIAL": "⚠️", "FAILED": "❌"}
            icon = status_icon.get(result["status"], "❓")
            print(f"{i:2d}. {icon} {result['url']}")
            print(f"    📝 {result['details']}")
                
        print("\n" + "="*80)
        
        if working_urls:
            print("🎯 SOLUTION FOUND!")
            print(f"✅ Working URL(s): {working_urls}")
            print("\n🔧 RECOMMENDED ACTION:")
            print(f"Update frontend/.env REACT_APP_BACKEND_URL to: {working_urls[0]}")
            print("This will fix the Evening Reflection 500 errors in the frontend.")
        else:
            print("❌ NO WORKING URLS FOUND")
            print("🔧 INVESTIGATION NEEDED:")
            print("- Check backend service status")
            print("- Verify URL routing configuration")
            print("- Check network connectivity")
            
        print("="*80)

async def main():
    """Main function to run URL configuration debug tests"""
    debug_suite = UrlConfigurationDebugSuite()
    await debug_suite.run_comprehensive_url_test()

if __name__ == "__main__":
    asyncio.run(main())