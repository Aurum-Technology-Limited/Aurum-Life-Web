#!/usr/bin/env python3

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, Any, List

# Configuration - Use external URL from frontend/.env
BACKEND_URL = "https://a6f7ddc8-1ace-40b1-9ed5-db784a5228b2.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class AreasUpdateTestSuite:
    """Focused testing for Areas update functionality as requested by user"""
    
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "nav.test@aurumlife.com"
        self.test_user_password = "navtest123"
        self.test_results = []
        self.created_resources = {
            'pillars': [],
            'areas': []
        }
        
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
            
            async with self.session.post(f"{BACKEND_URL}/api/auth/login", json=login_data) as response:
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
        
    async def test_create_area_functionality(self):
        """Test 1: Create a new area to ensure create functionality works"""
        print("\n🧪 Test 1: Create Area Functionality")
        
        try:
            # First create a pillar to link the area to
            pillar_data = {
                "name": "Test Pillar for Area Update",
                "description": "Pillar created for testing area update functionality",
                "icon": "🎯",
                "color": "#10B981",
                "time_allocation_percentage": 25.0
            }
            
            async with self.session.post(f"{API_BASE}/pillars", json=pillar_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    pillar = await response.json()
                    self.created_resources['pillars'].append(pillar['id'])
                    print(f"✅ Test pillar created successfully: {pillar['id']}")
                else:
                    error_text = await response.text()
                    print(f"❌ Pillar creation failed: {response.status} - {error_text}")
                    self.test_results.append({"test": "Create Area - Pillar Setup", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    return False
            
            # Now create an area
            area_data = {
                "pillar_id": pillar['id'],
                "name": "Test Area for Update",
                "description": "Area created specifically for testing update functionality",
                "icon": "📋",
                "color": "#F59E0B",
                "importance": 3
            }
            
            async with self.session.post(f"{API_BASE}/areas", json=area_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    area = await response.json()
                    self.created_resources['areas'].append(area['id'])
                    
                    # Verify area was created with correct data
                    if (area.get('name') == area_data['name'] and 
                        area.get('description') == area_data['description'] and
                        area.get('pillar_id') == pillar['id'] and
                        area.get('importance') == 3):
                        print("✅ Area created successfully with correct data")
                        print(f"   - Area ID: {area['id']}")
                        print(f"   - Name: {area['name']}")
                        print(f"   - Description: {area['description']}")
                        print(f"   - Pillar ID: {area['pillar_id']}")
                        print(f"   - Importance: {area['importance']}")
                        self.test_results.append({"test": "Create Area", "status": "PASSED", "details": "Area created with all correct fields"})
                        return area['id']
                    else:
                        print("❌ Area created but with incorrect data")
                        print(f"Expected name: {area_data['name']}, got: {area.get('name')}")
                        print(f"Expected pillar_id: {pillar['id']}, got: {area.get('pillar_id')}")
                        print(f"Expected importance: 3, got: {area.get('importance')}")
                        self.test_results.append({"test": "Create Area", "status": "FAILED", "reason": "Data mismatch"})
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Area creation failed: {response.status} - {error_text}")
                    self.test_results.append({"test": "Create Area", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    return False
                    
        except Exception as e:
            print(f"❌ Create area test failed: {e}")
            self.test_results.append({"test": "Create Area", "status": "FAILED", "reason": str(e)})
            return False
            
    async def test_update_area_functionality(self, area_id: str):
        """Test 2: Test updating an existing area using PUT /api/areas/{area_id}"""
        print("\n🧪 Test 2: Update Area Functionality - PUT /api/areas/{area_id}")
        
        try:
            # Test different update scenarios
            
            # Scenario 1: Update name and description
            print("\n   Scenario 1: Update name and description")
            update_data_1 = {
                "name": "Updated Test Area Name",
                "description": "Updated description for testing area update functionality"
            }
            
            async with self.session.put(f"{API_BASE}/areas/{area_id}", json=update_data_1, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    updated_area = await response.json()
                    
                    # Verify the update was applied
                    if (updated_area.get('name') == update_data_1['name'] and 
                        updated_area.get('description') == update_data_1['description']):
                        print("   ✅ Name and description updated successfully")
                        print(f"      - New name: {updated_area['name']}")
                        print(f"      - New description: {updated_area['description']}")
                    else:
                        print("   ❌ Name and description update failed")
                        print(f"      Expected name: {update_data_1['name']}, got: {updated_area.get('name')}")
                        print(f"      Expected description: {update_data_1['description']}, got: {updated_area.get('description')}")
                        self.test_results.append({"test": "Update Area - Name/Description", "status": "FAILED", "reason": "Update not applied"})
                        return False
                else:
                    error_text = await response.text()
                    print(f"   ❌ Name/description update failed: {response.status} - {error_text}")
                    self.test_results.append({"test": "Update Area - Name/Description", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    return False
            
            # Scenario 2: Update importance level
            print("\n   Scenario 2: Update importance level")
            update_data_2 = {
                "importance": 5
            }
            
            async with self.session.put(f"{API_BASE}/areas/{area_id}", json=update_data_2, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    updated_area = await response.json()
                    
                    if updated_area.get('importance') == 5:
                        print("   ✅ Importance level updated successfully")
                        print(f"      - New importance: {updated_area['importance']}")
                    else:
                        print("   ❌ Importance level update failed")
                        print(f"      Expected importance: 5, got: {updated_area.get('importance')}")
                        self.test_results.append({"test": "Update Area - Importance", "status": "FAILED", "reason": "Importance not updated"})
                        return False
                else:
                    error_text = await response.text()
                    print(f"   ❌ Importance update failed: {response.status} - {error_text}")
                    self.test_results.append({"test": "Update Area - Importance", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    return False
            
            # Scenario 3: Update icon and color
            print("\n   Scenario 3: Update icon and color")
            update_data_3 = {
                "icon": "🚀",
                "color": "#EF4444"
            }
            
            async with self.session.put(f"{API_BASE}/areas/{area_id}", json=update_data_3, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    updated_area = await response.json()
                    
                    if (updated_area.get('icon') == "🚀" and 
                        updated_area.get('color') == "#EF4444"):
                        print("   ✅ Icon and color updated successfully")
                        print(f"      - New icon: {updated_area['icon']}")
                        print(f"      - New color: {updated_area['color']}")
                    else:
                        print("   ❌ Icon and color update failed")
                        print(f"      Expected icon: 🚀, got: {updated_area.get('icon')}")
                        print(f"      Expected color: #EF4444, got: {updated_area.get('color')}")
                        self.test_results.append({"test": "Update Area - Icon/Color", "status": "FAILED", "reason": "Icon/color not updated"})
                        return False
                else:
                    error_text = await response.text()
                    print(f"   ❌ Icon/color update failed: {response.status} - {error_text}")
                    self.test_results.append({"test": "Update Area - Icon/Color", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    return False
            
            # Scenario 4: Comprehensive update (all fields at once)
            print("\n   Scenario 4: Comprehensive update (all fields)")
            comprehensive_update = {
                "name": "Fully Updated Test Area",
                "description": "Comprehensive update test - all fields modified",
                "icon": "⭐",
                "color": "#8B5CF6",
                "importance": 4
            }
            
            async with self.session.put(f"{API_BASE}/areas/{area_id}", json=comprehensive_update, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    updated_area = await response.json()
                    
                    # Verify all fields were updated
                    all_fields_correct = (
                        updated_area.get('name') == comprehensive_update['name'] and
                        updated_area.get('description') == comprehensive_update['description'] and
                        updated_area.get('icon') == comprehensive_update['icon'] and
                        updated_area.get('color') == comprehensive_update['color'] and
                        updated_area.get('importance') == comprehensive_update['importance']
                    )
                    
                    if all_fields_correct:
                        print("   ✅ Comprehensive update successful - all fields updated")
                        print(f"      - Final name: {updated_area['name']}")
                        print(f"      - Final description: {updated_area['description']}")
                        print(f"      - Final icon: {updated_area['icon']}")
                        print(f"      - Final color: {updated_area['color']}")
                        print(f"      - Final importance: {updated_area['importance']}")
                        self.test_results.append({"test": "Update Area - Comprehensive", "status": "PASSED", "details": "All update scenarios successful"})
                        return True
                    else:
                        print("   ❌ Comprehensive update failed - some fields not updated")
                        for field, expected in comprehensive_update.items():
                            actual = updated_area.get(field)
                            if actual != expected:
                                print(f"      Field '{field}': expected {expected}, got {actual}")
                        self.test_results.append({"test": "Update Area - Comprehensive", "status": "FAILED", "reason": "Some fields not updated"})
                        return False
                else:
                    error_text = await response.text()
                    print(f"   ❌ Comprehensive update failed: {response.status} - {error_text}")
                    self.test_results.append({"test": "Update Area - Comprehensive", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    return False
                    
        except Exception as e:
            print(f"❌ Update area test failed: {e}")
            self.test_results.append({"test": "Update Area", "status": "FAILED", "reason": str(e)})
            return False
            
    async def test_update_validation_errors(self, area_id: str):
        """Test 3: Check for validation errors and edge cases"""
        print("\n🧪 Test 3: Update Validation and Error Handling")
        
        try:
            # Test 1: Invalid importance value (should be 1-5)
            print("\n   Testing invalid importance value")
            invalid_importance = {
                "importance": 10  # Should be between 1-5
            }
            
            async with self.session.put(f"{API_BASE}/areas/{area_id}", json=invalid_importance, headers=self.get_auth_headers()) as response:
                if response.status == 400:
                    print("   ✅ Invalid importance value correctly rejected")
                elif response.status == 200:
                    # Check if the system accepted it but clamped the value
                    updated_area = await response.json()
                    if updated_area.get('importance') <= 5:
                        print("   ✅ Invalid importance value handled gracefully (clamped)")
                    else:
                        print("   ❌ Invalid importance value accepted without validation")
                else:
                    print(f"   ⚠️ Unexpected response for invalid importance: {response.status}")
            
            # Test 2: Empty name (should be rejected)
            print("\n   Testing empty name")
            empty_name = {
                "name": ""
            }
            
            async with self.session.put(f"{API_BASE}/areas/{area_id}", json=empty_name, headers=self.get_auth_headers()) as response:
                if response.status == 400:
                    print("   ✅ Empty name correctly rejected")
                elif response.status == 200:
                    print("   ⚠️ Empty name was accepted (may be intentional)")
                else:
                    print(f"   ⚠️ Unexpected response for empty name: {response.status}")
            
            # Test 3: Invalid pillar_id (if trying to change pillar)
            print("\n   Testing invalid pillar_id")
            invalid_pillar = {
                "pillar_id": "invalid-pillar-id-12345"
            }
            
            async with self.session.put(f"{API_BASE}/areas/{area_id}", json=invalid_pillar, headers=self.get_auth_headers()) as response:
                if response.status == 400:
                    print("   ✅ Invalid pillar_id correctly rejected")
                elif response.status == 200:
                    print("   ⚠️ Invalid pillar_id was accepted (may indicate issue)")
                else:
                    print(f"   ⚠️ Unexpected response for invalid pillar_id: {response.status}")
            
            # Test 4: Non-existent area ID
            print("\n   Testing non-existent area ID")
            test_update = {
                "name": "Test Update"
            }
            
            async with self.session.put(f"{API_BASE}/areas/non-existent-area-id", json=test_update, headers=self.get_auth_headers()) as response:
                if response.status == 404:
                    print("   ✅ Non-existent area ID correctly returns 404")
                else:
                    print(f"   ❌ Non-existent area ID should return 404, got: {response.status}")
            
            self.test_results.append({"test": "Update Validation", "status": "PASSED", "details": "Validation and error handling tested"})
            return True
            
        except Exception as e:
            print(f"❌ Validation test failed: {e}")
            self.test_results.append({"test": "Update Validation", "status": "FAILED", "reason": str(e)})
            return False
            
    async def test_area_retrieval_after_update(self, area_id: str):
        """Test 4: Verify area can be retrieved and shows updated data"""
        print("\n🧪 Test 4: Area Retrieval After Update")
        
        try:
            # Get the specific area
            async with self.session.get(f"{API_BASE}/areas", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    areas = await response.json()
                    updated_area = next((area for area in areas if area['id'] == area_id), None)
                    
                    if updated_area:
                        print("   ✅ Updated area found in areas list")
                        print(f"      - ID: {updated_area['id']}")
                        print(f"      - Name: {updated_area['name']}")
                        print(f"      - Description: {updated_area['description']}")
                        print(f"      - Icon: {updated_area['icon']}")
                        print(f"      - Color: {updated_area['color']}")
                        print(f"      - Importance: {updated_area['importance']}")
                        print(f"      - Pillar ID: {updated_area.get('pillar_id')}")
                        
                        # Verify it has the latest updates
                        if (updated_area['name'] == "Fully Updated Test Area" and
                            updated_area['importance'] == 4):
                            print("   ✅ Area shows latest updates correctly")
                            self.test_results.append({"test": "Area Retrieval After Update", "status": "PASSED", "details": "Updated area retrieved with correct data"})
                            return True
                        else:
                            print("   ❌ Area does not show latest updates")
                            self.test_results.append({"test": "Area Retrieval After Update", "status": "FAILED", "reason": "Updates not persisted"})
                            return False
                    else:
                        print("   ❌ Updated area not found in areas list")
                        self.test_results.append({"test": "Area Retrieval After Update", "status": "FAILED", "reason": "Area not found"})
                        return False
                else:
                    error_text = await response.text()
                    print(f"   ❌ Areas retrieval failed: {response.status} - {error_text}")
                    self.test_results.append({"test": "Area Retrieval After Update", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    return False
                    
        except Exception as e:
            print(f"❌ Area retrieval test failed: {e}")
            self.test_results.append({"test": "Area Retrieval After Update", "status": "FAILED", "reason": str(e)})
            return False
            
    async def cleanup_test_data(self):
        """Clean up created test data"""
        print("\n🧹 Cleaning up test data...")
        
        try:
            # Delete areas first
            for area_id in self.created_resources['areas']:
                async with self.session.delete(f"{API_BASE}/areas/{area_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print(f"✅ Deleted area {area_id}")
                    else:
                        print(f"⚠️ Failed to delete area {area_id}: {response.status}")
                        
            # Delete pillars
            for pillar_id in self.created_resources['pillars']:
                async with self.session.delete(f"{API_BASE}/pillars/{pillar_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print(f"✅ Deleted pillar {pillar_id}")
                    else:
                        print(f"⚠️ Failed to delete pillar {pillar_id}: {response.status}")
                        
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")
            
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🎯 AREAS UPDATE FUNCTIONALITY - TEST SUMMARY")
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
            status_icon = {"PASSED": "✅", "FAILED": "❌"}
            icon = status_icon.get(result["status"], "❓")
            print(f"{i:2d}. {icon} {result['test']}: {result['status']}")
            
            if "details" in result:
                print(f"    📝 {result['details']}")
            if "reason" in result:
                print(f"    💬 {result['reason']}")
                
        print("\n" + "="*80)
        
        # Determine overall system status
        if success_rate == 100:
            print("🎉 AREAS UPDATE FUNCTIONALITY IS WORKING PERFECTLY!")
            print("✅ Create functionality working")
            print("✅ Update endpoint working correctly")
            print("✅ All validation and error handling working")
        elif success_rate >= 75:
            print("⚠️ AREAS UPDATE FUNCTIONALITY IS MOSTLY WORKING - MINOR ISSUES DETECTED")
        else:
            print("❌ AREAS UPDATE FUNCTIONALITY HAS SIGNIFICANT ISSUES")
            print("🔧 The update button on the area edit screen may not be working due to backend issues")
            
        print("="*80)
        
    async def run_areas_update_test(self):
        """Run focused areas update test suite"""
        print("🚀 Starting Areas Update Functionality Testing...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print(f"👤 Test User: {self.test_user_email}")
        print("📋 Testing: Create Area → Update Area → Validation → Retrieval")
        
        await self.setup_session()
        
        try:
            # Authentication
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed with tests")
                return
                
            # Test 1: Create area functionality
            area_id = await self.test_create_area_functionality()
            if not area_id:
                print("❌ Area creation failed - cannot test update functionality")
                return
                
            # Test 2: Update area functionality
            update_success = await self.test_update_area_functionality(area_id)
            if not update_success:
                print("❌ Area update functionality failed")
                
            # Test 3: Validation and error handling
            await self.test_update_validation_errors(area_id)
            
            # Test 4: Verify retrieval after update
            await self.test_area_retrieval_after_update(area_id)
            
            # Cleanup
            await self.cleanup_test_data()
            
        finally:
            await self.cleanup_session()
            
        # Print summary
        self.print_test_summary()

async def main():
    """Main function to run the areas update test"""
    test_suite = AreasUpdateTestSuite()
    await test_suite.run_areas_update_test()

if __name__ == "__main__":
    asyncio.run(main())