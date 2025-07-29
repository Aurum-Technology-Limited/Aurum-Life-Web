#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import os
from datetime import datetime

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://008e000d-f023-448d-a17e-eec026cb8b9a.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

async def debug_auth():
    """Debug authentication endpoints"""
    print("🔍 Debugging Authentication Endpoints...")
    print(f"🔗 Backend URL: {BACKEND_URL}")
    print(f"🔗 API Base: {API_BASE}")
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Check if backend is reachable
        print("\n🧪 Test 1: Backend Health Check")
        try:
            async with session.get(f"{API_BASE}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Backend is reachable: {data}")
                else:
                    print(f"❌ Backend health check failed: {response.status}")
                    text = await response.text()
                    print(f"   Response: {text}")
        except Exception as e:
            print(f"❌ Backend connection error: {e}")
            return
            
        # Test 2: Try to register a user
        print("\n🧪 Test 2: User Registration")
        user_email = f"debug.test.{int(datetime.now().timestamp())}@aurumlife.com"
        register_data = {
            "username": f"debugtest{int(datetime.now().timestamp())}",
            "email": user_email,
            "first_name": "Debug",
            "last_name": "Test",
            "password": "TestPass123!"
        }
        
        try:
            async with session.post(f"{API_BASE}/auth/register", json=register_data) as response:
                print(f"Registration response status: {response.status}")
                text = await response.text()
                print(f"Registration response: {text}")
                
                if response.status == 200:
                    print("✅ User registration successful")
                elif response.status == 400:
                    print("⚠️ User might already exist or validation error")
                else:
                    print(f"❌ User registration failed: {response.status}")
                    return
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return
            
        # Test 3: Try to login
        print("\n🧪 Test 3: User Login")
        login_data = {
            "email": user_email,
            "password": "TestPass123!"
        }
        
        try:
            async with session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                print(f"Login response status: {response.status}")
                text = await response.text()
                print(f"Login response: {text}")
                
                if response.status == 200:
                    data = await response.json()
                    token = data.get("access_token")
                    if token:
                        print("✅ User login successful")
                        print(f"   Token received: {token[:50]}...")
                        
                        # Test 4: Try to access protected endpoint
                        print("\n🧪 Test 4: Protected Endpoint Access")
                        headers = {"Authorization": f"Bearer {token}"}
                        
                        async with session.get(f"{API_BASE}/auth/me", headers=headers) as me_response:
                            print(f"/auth/me response status: {me_response.status}")
                            me_text = await me_response.text()
                            print(f"/auth/me response: {me_text}")
                            
                            if me_response.status == 200:
                                print("✅ Protected endpoint access successful")
                                
                                # Test 5: Try to create a pillar
                                print("\n🧪 Test 5: Pillar Creation Test")
                                pillar_data = {
                                    "name": "Debug Test Pillar",
                                    "description": "Testing pillar creation for foreign key constraints",
                                    "icon": "🏛️",
                                    "color": "#2196F3",
                                    "time_allocation": 25
                                }
                                
                                async with session.post(f"{API_BASE}/pillars", json=pillar_data, headers=headers) as pillar_response:
                                    print(f"Pillar creation response status: {pillar_response.status}")
                                    pillar_text = await pillar_response.text()
                                    print(f"Pillar creation response: {pillar_text}")
                                    
                                    if pillar_response.status == 200:
                                        print("✅ Pillar creation successful - NO FOREIGN KEY CONSTRAINT VIOLATION!")
                                    else:
                                        if "foreign key" in pillar_text.lower() or "not present in table" in pillar_text.lower():
                                            print("🚨 FOREIGN KEY CONSTRAINT VIOLATION DETECTED!")
                                        else:
                                            print(f"❌ Pillar creation failed for other reason: {pillar_response.status}")
                            else:
                                print(f"❌ Protected endpoint access failed: {me_response.status}")
                    else:
                        print("❌ No token received in login response")
                elif response.status == 401:
                    print("❌ User login failed - likely due to email confirmation requirement")
                    print("🔍 Let's try with an existing confirmed user...")
                    
                    # Try with a known working user
                    existing_users = [
                        {"email": "nav.test@aurumlife.com", "password": "TestPass123!"},
                        {"email": "final.test@aurumlife.com", "password": "TestPass123!"},
                        {"email": "marc.alleyne@aurumtechnologyltd.com", "password": "TestPass123!"}
                    ]
                    
                    for existing_user in existing_users:
                        print(f"\n🧪 Trying existing user: {existing_user['email']}")
                        async with session.post(f"{API_BASE}/auth/login", json=existing_user) as existing_response:
                            print(f"Existing user login status: {existing_response.status}")
                            if existing_response.status == 200:
                                existing_data = await existing_response.json()
                                existing_token = existing_data.get("access_token")
                                if existing_token:
                                    print(f"✅ Existing user login successful: {existing_user['email']}")
                                    
                                    # Test with existing user
                                    headers = {"Authorization": f"Bearer {existing_token}"}
                                    
                                    # Test pillar creation with existing user
                                    print("\n🧪 Test 5: Pillar Creation with Existing User")
                                    pillar_data = {
                                        "name": "Existing User Test Pillar",
                                        "description": "Testing pillar creation with existing user",
                                        "icon": "🏛️",
                                        "color": "#2196F3",
                                        "time_allocation": 25
                                    }
                                    
                                    async with session.post(f"{API_BASE}/pillars", json=pillar_data, headers=headers) as pillar_response:
                                        print(f"Pillar creation response status: {pillar_response.status}")
                                        pillar_text = await pillar_response.text()
                                        print(f"Pillar creation response: {pillar_text}")
                                        
                                        if pillar_response.status == 200:
                                            print("✅ Pillar creation successful - NO FOREIGN KEY CONSTRAINT VIOLATION!")
                                            
                                            # Test area creation
                                            pillar_data_response = await pillar_response.json()
                                            pillar_id = pillar_data_response.get('id')
                                            
                                            print("\n🧪 Test 6: Area Creation with Existing User")
                                            area_data = {
                                                "name": "Existing User Test Area",
                                                "description": "Testing area creation with existing user",
                                                "pillar_id": pillar_id,
                                                "icon": "📁",
                                                "color": "#4CAF50",
                                                "importance": 3
                                            }
                                            
                                            async with session.post(f"{API_BASE}/areas", json=area_data, headers=headers) as area_response:
                                                print(f"Area creation response status: {area_response.status}")
                                                area_text = await area_response.text()
                                                print(f"Area creation response: {area_text}")
                                                
                                                if area_response.status == 200:
                                                    print("✅ Area creation successful - NO FOREIGN KEY CONSTRAINT VIOLATION!")
                                                else:
                                                    if "foreign key" in area_text.lower() or "not present in table" in area_text.lower():
                                                        print("🚨 FOREIGN KEY CONSTRAINT VIOLATION DETECTED!")
                                                    else:
                                                        print(f"❌ Area creation failed for other reason: {area_response.status}")
                                        else:
                                            if "foreign key" in pillar_text.lower() or "not present in table" in pillar_text.lower():
                                                print("🚨 FOREIGN KEY CONSTRAINT VIOLATION DETECTED!")
                                            else:
                                                print(f"❌ Pillar creation failed for other reason: {pillar_response.status}")
                                    
                                    return  # Exit after successful test with existing user
                            else:
                                existing_text = await existing_response.text()
                                print(f"   Failed: {existing_response.status} - {existing_text}")
                else:
                    print(f"❌ User login failed: {response.status}")
        except Exception as e:
            print(f"❌ Login error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_auth())