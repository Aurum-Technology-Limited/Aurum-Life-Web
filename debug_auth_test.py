#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import os
from datetime import datetime

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://f3436837-b2f7-41f6-8f79-d2f18535f691.preview.emergentagent.com')
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
                else:
                    print(f"❌ User login failed: {response.status}")
        except Exception as e:
            print(f"❌ Login error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_auth())