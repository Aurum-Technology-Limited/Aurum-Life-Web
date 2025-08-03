#!/usr/bin/env python3

import asyncio
import aiohttp
import json
from datetime import datetime

# Configuration - Use external URL from frontend/.env
BACKEND_URL = "https://7b39a747-36d6-44f7-9408-a498365475ba.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

async def test_areas_update_validation_fix():
    """Test the specific requirements from the review request"""
    print("🎯 AREAS UPDATE FUNCTIONALITY VALIDATION FIX VERIFICATION")
    print("="*70)
    print("Testing the specific requirements from the review request:")
    print("1. Authenticate with nav.test@aurumlife.com / navtest123")
    print("2. Get list of areas to find one to update")
    print("3. Test updating area with integer importance values (1-5)")
    print("4. Test updating other fields like name and description")
    print("5. Verify updates are successful and return proper responses")
    print("="*70)
    
    async with aiohttp.ClientSession() as session:
        # Step 1: Authenticate with test user
        print("\n🔐 Step 1: Authentication")
        login_data = {
            "email": "nav.test@aurumlife.com",
            "password": "navtest123"
        }
        
        async with session.post(f"{API_BASE}/auth/login", json=login_data) as response:
            if response.status == 200:
                data = await response.json()
                auth_token = data["access_token"]
                headers = {"Authorization": f"Bearer {auth_token}"}
                print("✅ Authentication successful with nav.test@aurumlife.com")
            else:
                print(f"❌ Authentication failed: {response.status}")
                return
        
        # Step 2: Get list of areas
        print("\n📋 Step 2: Get list of areas")
        async with session.get(f"{API_BASE}/areas", headers=headers) as response:
            if response.status == 200:
                areas = await response.json()
                print(f"✅ Retrieved {len(areas)} areas")
                
                if not areas:
                    print("⚠️ No areas found, creating a test area...")
                    # Create a test area
                    area_data = {
                        "name": "Test Area for Validation Fix",
                        "description": "Area created to test importance validation fix",
                        "icon": "🧪",
                        "color": "#10B981",
                        "importance": 3
                    }
                    
                    async with session.post(f"{API_BASE}/areas", json=area_data, headers=headers) as response:
                        if response.status == 200:
                            new_area = await response.json()
                            areas = [new_area]
                            print(f"✅ Created test area: {new_area.get('name')}")
                        else:
                            print(f"❌ Failed to create test area: {response.status}")
                            return
                
                test_area = areas[0]
                area_id = test_area['id']
                print(f"📍 Using area: {test_area.get('name', 'Unknown')} (ID: {area_id})")
                print(f"   Current importance: {test_area.get('importance', 'Unknown')}")
                
            else:
                print(f"❌ Failed to get areas: {response.status}")
                return
        
        # Step 3: Test updating area with integer importance values (1-5)
        print("\n🔢 Step 3: Test integer importance values (1-5) - THE MAIN FIX")
        importance_test_results = []
        
        for importance in [1, 2, 3, 4, 5]:
            print(f"   Testing importance value: {importance}")
            
            update_data = {"importance": importance}
            async with session.put(f"{API_BASE}/areas/{area_id}", json=update_data, headers=headers) as response:
                if response.status == 200:
                    updated_area = await response.json()
                    returned_importance = updated_area.get('importance')
                    
                    if returned_importance == importance and isinstance(returned_importance, int):
                        print(f"   ✅ SUCCESS: {importance} → {returned_importance} (correct type: {type(returned_importance).__name__})")
                        importance_test_results.append(True)
                    else:
                        print(f"   ❌ FAILED: {importance} → {returned_importance} (type: {type(returned_importance).__name__})")
                        importance_test_results.append(False)
                elif response.status == 422:
                    print(f"   ❌ 422 VALIDATION ERROR: The bug is still present!")
                    try:
                        error_data = await response.json()
                        print(f"      Error details: {json.dumps(error_data, indent=2)}")
                    except:
                        pass
                    importance_test_results.append(False)
                else:
                    print(f"   ❌ HTTP ERROR {response.status}")
                    importance_test_results.append(False)
        
        importance_success_rate = sum(importance_test_results) / len(importance_test_results) * 100
        print(f"\n📊 Importance validation fix results: {sum(importance_test_results)}/{len(importance_test_results)} successful ({importance_success_rate:.1f}%)")
        
        # Step 4: Test updating other fields
        print("\n📝 Step 4: Test updating other fields (name, description)")
        other_fields_results = []
        
        # Test name update
        timestamp = datetime.now().strftime("%H:%M:%S")
        new_name = f"Updated Area Name {timestamp}"
        update_data = {"name": new_name}
        
        async with session.put(f"{API_BASE}/areas/{area_id}", json=update_data, headers=headers) as response:
            if response.status == 200:
                updated_area = await response.json()
                if updated_area.get('name') == new_name:
                    print(f"   ✅ Name update successful: '{new_name}'")
                    other_fields_results.append(True)
                else:
                    print(f"   ❌ Name update failed: expected '{new_name}', got '{updated_area.get('name')}'")
                    other_fields_results.append(False)
            else:
                print(f"   ❌ Name update failed with status: {response.status}")
                other_fields_results.append(False)
        
        # Test description update
        new_description = f"Updated description at {timestamp}"
        update_data = {"description": new_description}
        
        async with session.put(f"{API_BASE}/areas/{area_id}", json=update_data, headers=headers) as response:
            if response.status == 200:
                updated_area = await response.json()
                if updated_area.get('description') == new_description:
                    print(f"   ✅ Description update successful")
                    other_fields_results.append(True)
                else:
                    print(f"   ❌ Description update failed")
                    other_fields_results.append(False)
            else:
                print(f"   ❌ Description update failed with status: {response.status}")
                other_fields_results.append(False)
        
        other_fields_success_rate = sum(other_fields_results) / len(other_fields_results) * 100 if other_fields_results else 0
        print(f"\n📊 Other fields update results: {sum(other_fields_results)}/{len(other_fields_results)} successful ({other_fields_success_rate:.1f}%)")
        
        # Step 5: Verify final state
        print("\n🔍 Step 5: Verify updates are successful and return proper responses")
        async with session.get(f"{API_BASE}/areas", headers=headers) as response:
            if response.status == 200:
                final_areas = await response.json()
                updated_area = next((area for area in final_areas if area['id'] == area_id), None)
                
                if updated_area:
                    print("✅ Area found in final verification")
                    print(f"   Final name: {updated_area.get('name', 'Unknown')}")
                    print(f"   Final description: {updated_area.get('description', 'Unknown')}")
                    print(f"   Final importance: {updated_area.get('importance', 'Unknown')} (type: {type(updated_area.get('importance', 'Unknown')).__name__})")
                else:
                    print("❌ Area not found in final verification")
            else:
                print(f"❌ Final verification failed: {response.status}")
        
        # Final Summary
        print("\n" + "="*70)
        print("🎯 FINAL VERIFICATION RESULTS")
        print("="*70)
        
        overall_success = importance_success_rate >= 90 and other_fields_success_rate >= 90
        
        if importance_success_rate == 100:
            print("🎉 IMPORTANCE VALIDATION FIX: COMPLETELY SUCCESSFUL!")
            print("   ✅ All integer importance values (1-5) work correctly")
            print("   ✅ No more 422 validation errors")
            print("   ✅ Proper integer types returned in responses")
        elif importance_success_rate >= 80:
            print("⚠️ IMPORTANCE VALIDATION FIX: MOSTLY SUCCESSFUL")
            print(f"   ⚠️ {importance_success_rate:.1f}% of importance values working")
        else:
            print("❌ IMPORTANCE VALIDATION FIX: STILL HAS ISSUES")
            print(f"   ❌ Only {importance_success_rate:.1f}% of importance values working")
        
        if other_fields_success_rate == 100:
            print("✅ OTHER FIELDS UPDATE: WORKING PERFECTLY")
        elif other_fields_success_rate >= 80:
            print("⚠️ OTHER FIELDS UPDATE: MOSTLY WORKING")
        else:
            print("❌ OTHER FIELDS UPDATE: HAS ISSUES")
        
        if overall_success:
            print("\n🎉 OVERALL RESULT: AREAS UPDATE FUNCTIONALITY IS WORKING CORRECTLY!")
            print("✅ The validation fix has resolved the 422 error issue")
            print("✅ Update button should now work properly in the frontend")
        else:
            print("\n⚠️ OVERALL RESULT: AREAS UPDATE FUNCTIONALITY NEEDS MORE WORK")
        
        print("="*70)

if __name__ == "__main__":
    asyncio.run(test_areas_update_validation_fix())