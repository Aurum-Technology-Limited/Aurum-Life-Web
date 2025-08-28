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

class AreasUpdateTestSuite:
    """Focused testing for Areas Update functionality to reproduce 422 validation errors"""
    
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
                    
                    # Show first few areas for reference
                    if areas:
                        print("📝 Sample areas:")
                        for i, area in enumerate(areas[:3]):
                            print(f"   {i+1}. {area.get('name', 'Unknown')} (ID: {area.get('id', 'Unknown')[:8]}...)")
                            print(f"      Importance: {area.get('importance', 'Unknown')} (type: {type(area.get('importance', 'Unknown'))})")
                            print(f"      Icon: {area.get('icon', 'Unknown')}, Color: {area.get('color', 'Unknown')}")
                    
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to get areas: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error getting areas: {e}")
            return False
            
    async def test_simple_name_update(self, area_id: str, area_name: str):
        """Test 1: Simple name/description changes"""
        print(f"\n🧪 Test 1: Simple name/description update for '{area_name}'")
        
        try:
            update_data = {
                "name": f"{area_name} (Updated)",
                "description": "Updated description for testing"
            }
            
            print(f"📤 Sending PUT request with data: {json.dumps(update_data, indent=2)}")
            
            start_time = time.time()
            async with self.session.put(f"{API_BASE}/areas/{area_id}", json=update_data, headers=self.get_auth_headers()) as response:
                response_time = (time.time() - start_time) * 1000
                
                print(f"📥 Response: {response.status} in {response_time:.1f}ms")
                
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Simple update successful")
                    print(f"   Updated name: {result.get('name', 'Unknown')}")
                    self.test_results.append({
                        "test": "Simple Name/Description Update",
                        "status": "PASSED",
                        "details": f"Successfully updated name and description"
                    })
                    return True
                elif response.status == 422:
                    error_data = await response.json()
                    print(f"❌ 422 Validation Error detected!")
                    print(f"   Error details: {json.dumps(error_data, indent=2)}")
                    self.test_results.append({
                        "test": "Simple Name/Description Update",
                        "status": "FAILED",
                        "reason": f"422 Validation Error: {error_data}"
                    })
                    return False
                else:
                    error_text = await response.text()
                    print(f"❌ Update failed: {response.status} - {error_text}")
                    self.test_results.append({
                        "test": "Simple Name/Description Update",
                        "status": "FAILED",
                        "reason": f"HTTP {response.status}: {error_text}"
                    })
                    return False
                    
        except Exception as e:
            print(f"❌ Simple update test failed: {e}")
            self.test_results.append({
                "test": "Simple Name/Description Update",
                "status": "FAILED",
                "reason": str(e)
            })
            return False
            
    async def test_importance_field_updates(self, area_id: str, area_name: str):
        """Test 2: Importance field updates (integer values 1-5)"""
        print(f"\n🧪 Test 2: Importance field updates for '{area_name}'")
        
        importance_values = [1, 2, 3, 4, 5]
        success_count = 0
        
        for importance in importance_values:
            try:
                update_data = {
                    "importance": importance
                }
                
                print(f"📤 Testing importance value: {importance} (type: {type(importance)})")
                
                start_time = time.time()
                async with self.session.put(f"{API_BASE}/areas/{area_id}", json=update_data, headers=self.get_auth_headers()) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    print(f"📥 Response: {response.status} in {response_time:.1f}ms")
                    
                    if response.status == 200:
                        result = await response.json()
                        returned_importance = result.get('importance')
                        print(f"✅ Importance {importance} update successful")
                        print(f"   Returned importance: {returned_importance} (type: {type(returned_importance)})")
                        
                        # Check if returned value matches sent value and is correct type
                        if returned_importance == importance and isinstance(returned_importance, int):
                            print(f"✅ Importance value and type correct")
                            success_count += 1
                        else:
                            print(f"⚠️ Importance value or type mismatch")
                            print(f"   Expected: {importance} (int), Got: {returned_importance} ({type(returned_importance)})")
                            
                    elif response.status == 422:
                        error_data = await response.json()
                        print(f"❌ 422 Validation Error for importance {importance}!")
                        print(f"   Error details: {json.dumps(error_data, indent=2)}")
                        
                        # This is the key issue we're trying to identify
                        if 'detail' in error_data:
                            for detail in error_data['detail']:
                                if 'loc' in detail and 'msg' in detail:
                                    print(f"   Field: {detail['loc']}, Message: {detail['msg']}")
                                    
                    else:
                        error_text = await response.text()
                        print(f"❌ Update failed: {response.status} - {error_text}")
                        
            except Exception as e:
                print(f"❌ Importance {importance} test failed: {e}")
                
        if success_count == len(importance_values):
            self.test_results.append({
                "test": "Importance Field Updates",
                "status": "PASSED",
                "details": f"All {len(importance_values)} importance values working correctly"
            })
            return True
        else:
            self.test_results.append({
                "test": "Importance Field Updates",
                "status": "FAILED",
                "reason": f"Only {success_count}/{len(importance_values)} importance values working"
            })
            return False
            
    async def test_icon_color_updates(self, area_id: str, area_name: str):
        """Test 3: Icon and color changes"""
        print(f"\n🧪 Test 3: Icon and color updates for '{area_name}'")
        
        try:
            update_data = {
                "icon": "🎨",
                "color": "#FF6B6B"
            }
            
            print(f"📤 Sending icon/color update: {json.dumps(update_data, indent=2)}")
            
            start_time = time.time()
            async with self.session.put(f"{API_BASE}/areas/{area_id}", json=update_data, headers=self.get_auth_headers()) as response:
                response_time = (time.time() - start_time) * 1000
                
                print(f"📥 Response: {response.status} in {response_time:.1f}ms")
                
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Icon/color update successful")
                    print(f"   Updated icon: {result.get('icon', 'Unknown')}")
                    print(f"   Updated color: {result.get('color', 'Unknown')}")
                    self.test_results.append({
                        "test": "Icon/Color Updates",
                        "status": "PASSED",
                        "details": "Successfully updated icon and color"
                    })
                    return True
                elif response.status == 422:
                    error_data = await response.json()
                    print(f"❌ 422 Validation Error for icon/color update!")
                    print(f"   Error details: {json.dumps(error_data, indent=2)}")
                    self.test_results.append({
                        "test": "Icon/Color Updates",
                        "status": "FAILED",
                        "reason": f"422 Validation Error: {error_data}"
                    })
                    return False
                else:
                    error_text = await response.text()
                    print(f"❌ Icon/color update failed: {response.status} - {error_text}")
                    self.test_results.append({
                        "test": "Icon/Color Updates",
                        "status": "FAILED",
                        "reason": f"HTTP {response.status}: {error_text}"
                    })
                    return False
                    
        except Exception as e:
            print(f"❌ Icon/color update test failed: {e}")
            self.test_results.append({
                "test": "Icon/Color Updates",
                "status": "FAILED",
                "reason": str(e)
            })
            return False
            
    async def test_all_fields_together(self, area_id: str, area_name: str):
        """Test 4: All fields together"""
        print(f"\n🧪 Test 4: All fields update together for '{area_name}'")
        
        try:
            update_data = {
                "name": f"{area_name} (Complete Update)",
                "description": "Complete update with all fields",
                "importance": 3,
                "icon": "🔥",
                "color": "#8B5CF6"
            }
            
            print(f"📤 Sending complete update: {json.dumps(update_data, indent=2)}")
            
            start_time = time.time()
            async with self.session.put(f"{API_BASE}/areas/{area_id}", json=update_data, headers=self.get_auth_headers()) as response:
                response_time = (time.time() - start_time) * 1000
                
                print(f"📥 Response: {response.status} in {response_time:.1f}ms")
                
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Complete update successful")
                    print(f"   Name: {result.get('name', 'Unknown')}")
                    print(f"   Description: {result.get('description', 'Unknown')}")
                    print(f"   Importance: {result.get('importance', 'Unknown')} (type: {type(result.get('importance', 'Unknown'))})")
                    print(f"   Icon: {result.get('icon', 'Unknown')}")
                    print(f"   Color: {result.get('color', 'Unknown')}")
                    
                    self.test_results.append({
                        "test": "All Fields Update",
                        "status": "PASSED",
                        "details": "Successfully updated all fields together"
                    })
                    return True
                elif response.status == 422:
                    error_data = await response.json()
                    print(f"❌ 422 Validation Error for complete update!")
                    print(f"   Error details: {json.dumps(error_data, indent=2)}")
                    
                    # Detailed analysis of validation errors
                    if 'detail' in error_data and isinstance(error_data['detail'], list):
                        print(f"   Validation errors breakdown:")
                        for i, detail in enumerate(error_data['detail']):
                            print(f"     {i+1}. Field: {detail.get('loc', 'Unknown')}")
                            print(f"        Message: {detail.get('msg', 'Unknown')}")
                            print(f"        Type: {detail.get('type', 'Unknown')}")
                            if 'input' in detail:
                                print(f"        Input: {detail['input']}")
                                
                    self.test_results.append({
                        "test": "All Fields Update",
                        "status": "FAILED",
                        "reason": f"422 Validation Error: {error_data}"
                    })
                    return False
                else:
                    error_text = await response.text()
                    print(f"❌ Complete update failed: {response.status} - {error_text}")
                    self.test_results.append({
                        "test": "All Fields Update",
                        "status": "FAILED",
                        "reason": f"HTTP {response.status}: {error_text}"
                    })
                    return False
                    
        except Exception as e:
            print(f"❌ Complete update test failed: {e}")
            self.test_results.append({
                "test": "All Fields Update",
                "status": "FAILED",
                "reason": str(e)
            })
            return False
            
    async def test_problematic_data_scenarios(self, area_id: str, area_name: str):
        """Test 5: Potentially problematic data scenarios"""
        print(f"\n🧪 Test 5: Problematic data scenarios for '{area_name}'")
        
        test_scenarios = [
            {
                "name": "String importance",
                "data": {"importance": "3"},
                "expected": "Should fail - importance should be integer"
            },
            {
                "name": "Out of range importance",
                "data": {"importance": 6},
                "expected": "Should fail - importance should be 1-5"
            },
            {
                "name": "Zero importance",
                "data": {"importance": 0},
                "expected": "Should fail - importance should be 1-5"
            },
            {
                "name": "Negative importance",
                "data": {"importance": -1},
                "expected": "Should fail - importance should be 1-5"
            },
            {
                "name": "Float importance",
                "data": {"importance": 3.5},
                "expected": "Should fail - importance should be integer"
            },
            {
                "name": "Empty name",
                "data": {"name": ""},
                "expected": "Should fail - name should not be empty"
            },
            {
                "name": "None importance",
                "data": {"importance": None},
                "expected": "May pass - importance might be optional"
            }
        ]
        
        for scenario in test_scenarios:
            try:
                print(f"\n   Testing: {scenario['name']}")
                print(f"   Data: {json.dumps(scenario['data'], indent=2)}")
                print(f"   Expected: {scenario['expected']}")
                
                start_time = time.time()
                async with self.session.put(f"{API_BASE}/areas/{area_id}", json=scenario['data'], headers=self.get_auth_headers()) as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    print(f"   Response: {response.status} in {response_time:.1f}ms")
                    
                    if response.status == 200:
                        result = await response.json()
                        print(f"   ✅ Update successful (unexpected for some scenarios)")
                        if 'importance' in result:
                            print(f"   Returned importance: {result['importance']} (type: {type(result['importance'])})")
                    elif response.status == 422:
                        error_data = await response.json()
                        print(f"   ❌ 422 Validation Error (expected for most scenarios)")
                        if 'detail' in error_data:
                            for detail in error_data['detail']:
                                if isinstance(detail, dict):
                                    print(f"      Field: {detail.get('loc', 'Unknown')}, Message: {detail.get('msg', 'Unknown')}")
                    else:
                        error_text = await response.text()
                        print(f"   ❌ Other error: {response.status} - {error_text}")
                        
            except Exception as e:
                print(f"   ❌ Scenario '{scenario['name']}' failed: {e}")
                
        self.test_results.append({
            "test": "Problematic Data Scenarios",
            "status": "COMPLETED",
            "details": f"Tested {len(test_scenarios)} edge case scenarios"
        })
        
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🔍 AREAS UPDATE FUNCTIONALITY - 422 VALIDATION ERROR ANALYSIS")
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
        
        # Analysis and recommendations
        print("🔍 ROOT CAUSE ANALYSIS:")
        
        validation_errors = [t for t in self.test_results if t["status"] == "FAILED" and "422" in str(t.get("reason", ""))]
        if validation_errors:
            print("❌ 422 Validation errors detected in the following tests:")
            for error in validation_errors:
                print(f"   - {error['test']}")
            print("\n💡 RECOMMENDATIONS:")
            print("   1. Check backend validation logic in SupabaseAreaService.update_area()")
            print("   2. Verify Pydantic model validation in AreaUpdate model")
            print("   3. Check field mapping and data type conversions")
            print("   4. Review importance field validation (should accept integers 1-5)")
        else:
            print("✅ No 422 validation errors detected")
            print("   The areas update functionality appears to be working correctly")
            
        print("="*80)
        
    async def run_areas_update_test(self):
        """Run comprehensive Areas Update test suite"""
        print("🚀 Starting Areas Update Functionality Testing...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print("🎯 Focus: Reproducing 422 validation errors in Areas update")
        
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
                
            # Step 3: Test updates on first available area
            test_area = self.existing_areas[0]
            area_id = test_area.get('id')
            area_name = test_area.get('name', 'Unknown Area')
            
            print(f"\n🎯 Testing updates on area: '{area_name}' (ID: {area_id[:8]}...)")
            
            # Run all update tests
            await self.test_simple_name_update(area_id, area_name)
            await self.test_importance_field_updates(area_id, area_name)
            await self.test_icon_color_updates(area_id, area_name)
            await self.test_all_fields_together(area_id, area_name)
            await self.test_problematic_data_scenarios(area_id, area_name)
            
        finally:
            await self.cleanup_session()
            
        # Print summary
        self.print_test_summary()

async def main():
    """Main function to run the Areas Update test suite"""
    test_suite = AreasUpdateTestSuite()
    await test_suite.run_areas_update_test()

if __name__ == "__main__":
    asyncio.run(main())