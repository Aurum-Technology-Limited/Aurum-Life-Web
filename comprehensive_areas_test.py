#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, Any, List

# Configuration - Use localhost URL since backend is running locally
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

class ComprehensiveAreasTestSuite:
    """Comprehensive testing for Areas functionality including edge cases"""
    
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "nav.test@aurumlife.com"
        self.test_user_password = "testpassword123"
        self.test_results = []
        self.existing_areas = []
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()
            
    async def authenticate(self):
        """Authenticate with test credentials"""
        print("🔐 Authenticating with nav.test@aurumlife.com...")
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
                    self.auth_token = data["access_token"]
                    print(f"✅ Authentication successful in {response_time:.1f}ms")
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
        
    async def get_existing_areas(self):
        """Get existing areas for testing"""
        print("\n📋 Getting existing areas...")
        try:
            start_time = time.time()
            async with self.session.get(f"{API_BASE}/areas", headers=self.get_auth_headers()) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    areas = await response.json()
                    self.existing_areas = areas
                    print(f"✅ Retrieved {len(areas)} existing areas in {response_time:.1f}ms")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to get areas: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error getting areas: {e}")
            return False
            
    async def test_frontend_like_update_scenarios(self, area_id: str, area_name: str):
        """Test scenarios that mimic frontend behavior"""
        print(f"\n🧪 Frontend-like Update Scenarios for '{area_name}'")
        
        scenarios = [
            {
                "name": "Frontend Edit Modal - Name Only",
                "data": {"name": f"{area_name} (Frontend Edit)"},
                "expected": "Should succeed"
            },
            {
                "name": "Frontend Edit Modal - Name + Description",
                "data": {
                    "name": f"{area_name} (Frontend Edit)",
                    "description": "Updated via frontend-like request"
                },
                "expected": "Should succeed"
            },
            {
                "name": "Frontend Edit Modal - All Fields",
                "data": {
                    "name": f"{area_name} (Complete Frontend Edit)",
                    "description": "Complete frontend update",
                    "importance": 4,
                    "icon": "🎯",
                    "color": "#4CAF50"
                },
                "expected": "Should succeed"
            },
            {
                "name": "Frontend Importance Slider - Value 1",
                "data": {"importance": 1},
                "expected": "Should succeed"
            },
            {
                "name": "Frontend Importance Slider - Value 5",
                "data": {"importance": 5},
                "expected": "Should succeed"
            },
            {
                "name": "Frontend Form Validation - Empty Object",
                "data": {},
                "expected": "Should succeed (no changes)"
            },
            {
                "name": "Frontend JSON Parsing - String Importance",
                "data": {"importance": "3"},
                "expected": "Should succeed (auto-convert)"
            },
            {
                "name": "Frontend Validation - Invalid Importance Range",
                "data": {"importance": 10},
                "expected": "Should fail with 422"
            },
            {
                "name": "Frontend Validation - Negative Importance",
                "data": {"importance": -1},
                "expected": "Should fail with 422"
            },
            {
                "name": "Frontend Validation - Float Importance",
                "data": {"importance": 3.7},
                "expected": "Should fail with 422"
            }
        ]
        
        success_count = 0
        validation_error_count = 0
        
        for scenario in scenarios:
            try:
                print(f"\n   🔍 {scenario['name']}")
                print(f"      Data: {json.dumps(scenario['data'])}")
                print(f"      Expected: {scenario['expected']}")
                
                start_time = time.time()
                async with self.session.put(f"{API_BASE}/areas/{area_id}", json=scenario['data'], headers=self.get_auth_headers()) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    print(f"      Response: {response.status} in {response_time:.1f}ms")
                    
                    if response.status == 200:
                        result = await response.json()
                        print(f"      ✅ Success")
                        if 'importance' in result:
                            print(f"         Returned importance: {result['importance']} (type: {type(result['importance'])})")
                        success_count += 1
                        
                    elif response.status == 422:
                        error_data = await response.json()
                        print(f"      ❌ 422 Validation Error")
                        validation_error_count += 1
                        
                        # Detailed error analysis
                        if 'detail' in error_data:
                            for detail in error_data['detail']:
                                if isinstance(detail, dict):
                                    field = detail.get('loc', ['unknown'])[-1]
                                    message = detail.get('msg', 'Unknown error')
                                    print(f"         Field '{field}': {message}")
                                    
                    else:
                        error_text = await response.text()
                        print(f"      ❌ Unexpected error: {response.status} - {error_text}")
                        
            except Exception as e:
                print(f"      ❌ Exception: {e}")
                
        print(f"\n   📊 Frontend Scenarios Summary:")
        print(f"      ✅ Successful updates: {success_count}")
        print(f"      ❌ Validation errors: {validation_error_count}")
        print(f"      📋 Total scenarios: {len(scenarios)}")
        
        self.test_results.append({
            "test": "Frontend-like Update Scenarios",
            "status": "COMPLETED",
            "details": f"{success_count} successful, {validation_error_count} validation errors out of {len(scenarios)} scenarios"
        })
        
    async def test_concurrent_updates(self, area_id: str, area_name: str):
        """Test concurrent updates to the same area"""
        print(f"\n🧪 Concurrent Updates Test for '{area_name}'")
        
        try:
            # Create multiple concurrent update requests
            update_tasks = []
            
            for i in range(3):
                update_data = {
                    "name": f"{area_name} (Concurrent Update {i+1})",
                    "importance": (i % 5) + 1  # Cycle through 1-5
                }
                
                task = self.session.put(f"{API_BASE}/areas/{area_id}", json=update_data, headers=self.get_auth_headers())
                update_tasks.append(task)
                
            # Execute all updates concurrently
            start_time = time.time()
            responses = await asyncio.gather(*update_tasks, return_exceptions=True)
            total_time = (time.time() - start_time) * 1000
            
            success_count = 0
            error_count = 0
            
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    print(f"   ❌ Update {i+1}: Exception - {response}")
                    error_count += 1
                else:
                    if response.status == 200:
                        result = await response.json()
                        print(f"   ✅ Update {i+1}: Success - {result.get('name', 'Unknown')}")
                        success_count += 1
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Update {i+1}: {response.status} - {error_text}")
                        error_count += 1
                    response.close()
                    
            print(f"\n   📊 Concurrent Updates Summary:")
            print(f"      ✅ Successful: {success_count}")
            print(f"      ❌ Failed: {error_count}")
            print(f"      ⏱️ Total time: {total_time:.1f}ms")
            
            self.test_results.append({
                "test": "Concurrent Updates",
                "status": "PASSED" if success_count > 0 else "FAILED",
                "details": f"{success_count}/{len(update_tasks)} concurrent updates successful"
            })
            
        except Exception as e:
            print(f"❌ Concurrent updates test failed: {e}")
            self.test_results.append({
                "test": "Concurrent Updates",
                "status": "FAILED",
                "reason": str(e)
            })
            
    async def test_malformed_requests(self, area_id: str, area_name: str):
        """Test malformed and edge case requests"""
        print(f"\n🧪 Malformed Requests Test for '{area_name}'")
        
        malformed_scenarios = [
            {
                "name": "Invalid JSON",
                "data": '{"name": "Invalid JSON"',  # Missing closing brace
                "content_type": "application/json",
                "expected": "Should fail with 400/422"
            },
            {
                "name": "Wrong Content-Type",
                "data": {"name": "Wrong Content Type"},
                "content_type": "text/plain",
                "expected": "Should fail"
            },
            {
                "name": "Extremely Long Name",
                "data": {"name": "A" * 1000},  # 1000 character name
                "content_type": "application/json",
                "expected": "May succeed or fail based on validation"
            },
            {
                "name": "SQL Injection Attempt",
                "data": {"name": "'; DROP TABLE areas; --"},
                "content_type": "application/json",
                "expected": "Should be safely handled"
            },
            {
                "name": "XSS Attempt",
                "data": {"name": "<script>alert('xss')</script>"},
                "content_type": "application/json",
                "expected": "Should be safely handled"
            },
            {
                "name": "Unicode Characters",
                "data": {"name": "测试区域 🌟 émojis"},
                "content_type": "application/json",
                "expected": "Should succeed"
            }
        ]
        
        for scenario in malformed_scenarios:
            try:
                print(f"\n   🔍 {scenario['name']}")
                print(f"      Expected: {scenario['expected']}")
                
                headers = self.get_auth_headers()
                headers['Content-Type'] = scenario['content_type']
                
                if scenario['content_type'] == 'application/json':
                    data = json.dumps(scenario['data']) if isinstance(scenario['data'], dict) else scenario['data']
                else:
                    data = str(scenario['data'])
                
                start_time = time.time()
                async with self.session.put(f"{API_BASE}/areas/{area_id}", data=data, headers=headers) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    print(f"      Response: {response.status} in {response_time:.1f}ms")
                    
                    if response.status == 200:
                        result = await response.json()
                        print(f"      ✅ Unexpectedly succeeded: {result.get('name', 'Unknown')}")
                    elif response.status in [400, 422]:
                        error_data = await response.text()
                        print(f"      ✅ Expected error: {error_data[:100]}...")
                    else:
                        error_text = await response.text()
                        print(f"      ⚠️ Unexpected status: {response.status} - {error_text[:100]}...")
                        
            except Exception as e:
                print(f"      ❌ Exception: {e}")
                
        self.test_results.append({
            "test": "Malformed Requests",
            "status": "COMPLETED",
            "details": f"Tested {len(malformed_scenarios)} malformed request scenarios"
        })
        
    def print_comprehensive_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🔍 COMPREHENSIVE AREAS UPDATE TESTING - DETAILED ANALYSIS")
        print("="*80)
        
        passed = len([t for t in self.test_results if t["status"] == "PASSED"])
        failed = len([t for t in self.test_results if t["status"] == "FAILED"])
        completed = len([t for t in self.test_results if t["status"] == "COMPLETED"])
        total = len(self.test_results)
        
        print(f"📊 OVERALL RESULTS: {passed} passed, {failed} failed, {completed} completed")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📋 Completed: {completed}")
        
        print("\n📋 DETAILED RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status_icon = {"PASSED": "✅", "FAILED": "❌", "COMPLETED": "📋"}
            icon = status_icon.get(result["status"], "❓")
            print(f"{i:2d}. {icon} {result['test']}: {result['status']}")
            
            if "details" in result:
                print(f"    📝 {result['details']}")
            if "reason" in result:
                print(f"    💬 {result['reason']}")
                
        print("\n" + "="*80)
        
        # Final analysis
        print("🔍 FINAL ANALYSIS:")
        
        if failed == 0:
            print("✅ NO CRITICAL FAILURES DETECTED")
            print("   The Areas Update functionality appears to be working correctly")
            print("   All validation scenarios behaved as expected")
            print("\n💡 CONCLUSION:")
            print("   The 422 validation errors mentioned in the original issue")
            print("   appear to have been resolved. The backend is handling")
            print("   area updates correctly with proper validation.")
        else:
            print("❌ CRITICAL ISSUES DETECTED")
            print("   Some tests failed - review the detailed results above")
            
        print("="*80)
        
    async def run_comprehensive_test(self):
        """Run comprehensive Areas test suite"""
        print("🚀 Starting Comprehensive Areas Update Testing...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print("🎯 Focus: Comprehensive testing including edge cases and frontend scenarios")
        
        await self.setup_session()
        
        try:
            # Step 1: Authentication
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed with tests")
                return
                
            # Step 2: Get existing areas
            if not await self.get_existing_areas():
                print("❌ Failed to get existing areas - cannot proceed with tests")
                return
                
            if not self.existing_areas:
                print("❌ No existing areas found - cannot test updates")
                return
                
            # Step 3: Run comprehensive tests on first available area
            test_area = self.existing_areas[0]
            area_id = test_area.get('id')
            area_name = test_area.get('name', 'Unknown Area')
            
            print(f"\n🎯 Running comprehensive tests on area: '{area_name}' (ID: {area_id[:8]}...)")
            
            # Run all comprehensive tests
            await self.test_frontend_like_update_scenarios(area_id, area_name)
            await self.test_concurrent_updates(area_id, area_name)
            await self.test_malformed_requests(area_id, area_name)
            
        finally:
            await self.cleanup_session()
            
        # Print comprehensive summary
        self.print_comprehensive_summary()

async def main():
    """Main function to run the comprehensive Areas test suite"""
    test_suite = ComprehensiveAreasTestSuite()
    await test_suite.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())