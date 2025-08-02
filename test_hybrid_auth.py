#!/usr/bin/env python3
"""
Create a test user for authentication testing and verify the hybrid auth system works
"""

import asyncio
import sys
import os
from dotenv import load_dotenv
import aiohttp
import json
import uuid

# Load environment variables
load_dotenv('/app/backend/.env')
sys.path.append('/app/backend')

from supabase_client import get_supabase_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://f4646b2e-0ec9-404e-813c-ae5666a33561.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

async def create_test_user_and_verify_auth():
    """Create a test user and verify the hybrid authentication system works"""
    
    print("🔐 Testing Hybrid Authentication System...")
    
    try:
        supabase = await get_supabase_client()
        
        # Step 1: Create a test user directly in the legacy system
        print("\n1️⃣ Creating test user in legacy system...")
        
        test_user_id = str(uuid.uuid4())
        test_email = f"authtest.{test_user_id[:8]}@aurumlife.com"
        test_username = f"authtest_{test_user_id[:8]}"
        test_password = "TestPass123!"
        
        # Create user in legacy users table
        legacy_user_data = {
            "id": test_user_id,
            "username": test_username,
            "email": test_email,
            "first_name": "Auth",
            "last_name": "Test",
            "password_hash": "dummy_hash",  # Not used in our hybrid auth
            "is_active": True,
            "level": 1,
            "total_points": 0,
            "current_streak": 0
        }
        
        try:
            result = supabase.table('users').insert(legacy_user_data).execute()
            print(f"✅ Legacy user created: {test_email}")
        except Exception as e:
            print(f"❌ Failed to create legacy user: {e}")
            return False
        
        # Create user_profiles entry
        profile_data = {
            "id": test_user_id,
            "username": test_username,
            "first_name": "Auth",
            "last_name": "Test",
            "is_active": True,
            "level": 1,
            "total_points": 0,
            "current_streak": 0
        }
        
        try:
            result = supabase.table('user_profiles').insert(profile_data).execute()
            print(f"✅ User profile created: {test_email}")
        except Exception as e:
            print(f"⚠️ Profile creation failed (might already exist): {e}")
        
        # Create user stats
        stats_data = {
            "user_id": test_user_id,
            "total_journal_entries": 0,
            "total_tasks": 0,
            "tasks_completed": 0,
            "total_areas": 0,
            "total_projects": 0,
            "completed_projects": 0,
            "courses_enrolled": 0,
            "courses_completed": 0,
            "badges_earned": 0
        }
        
        try:
            result = supabase.table('user_stats').insert(stats_data).execute()
            print(f"✅ User stats created: {test_email}")
        except Exception as e:
            print(f"⚠️ Stats creation failed (might already exist): {e}")
        
        # Step 2: Test authentication via API
        print(f"\n2️⃣ Testing authentication for: {test_email}")
        
        async with aiohttp.ClientSession() as session:
            # Test login
            login_data = {
                "email": test_email,
                "password": test_password
            }
            
            try:
                async with session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                    print(f"Login response status: {response.status}")
                    response_text = await response.text()
                    
                    if response.status == 200:
                        response_data = await response.json()
                        access_token = response_data.get("access_token")
                        
                        if access_token:
                            print("✅ LOGIN SUCCESSFUL!")
                            print(f"   Token received: {access_token[:50]}...")
                            
                            # Step 3: Test protected endpoint
                            print(f"\n3️⃣ Testing protected endpoint access...")
                            
                            headers = {"Authorization": f"Bearer {access_token}"}
                            
                            async with session.get(f"{API_BASE}/auth/me", headers=headers) as me_response:
                                print(f"/auth/me response status: {me_response.status}")
                                me_text = await me_response.text()
                                
                                if me_response.status == 200:
                                    me_data = await me_response.json()
                                    print("✅ PROTECTED ENDPOINT ACCESS SUCCESSFUL!")
                                    print(f"   User data: {me_data.get('email')} ({me_data.get('id')[:8]}...)")
                                    
                                    # Step 4: Test data creation (pillar)
                                    print(f"\n4️⃣ Testing data creation...")
                                    
                                    pillar_data = {
                                        "name": "Auth Test Pillar",
                                        "description": "Testing authentication and data creation",
                                        "icon": "🔐",
                                        "color": "#4CAF50"
                                    }
                                    
                                    async with session.post(f"{API_BASE}/pillars", json=pillar_data, headers=headers) as pillar_response:
                                        print(f"Pillar creation response status: {pillar_response.status}")
                                        pillar_text = await pillar_response.text()
                                        
                                        if pillar_response.status == 200:
                                            pillar_data_response = await pillar_response.json()
                                            pillar_id = pillar_data_response.get('id')
                                            print("🎉 DATA CREATION SUCCESSFUL!")
                                            print(f"   Pillar created: {pillar_id}")
                                            
                                            # Clean up test pillar
                                            try:
                                                async with session.delete(f"{API_BASE}/pillars/{pillar_id}", headers=headers) as delete_response:
                                                    if delete_response.status in [200, 204]:
                                                        print("🧹 Test pillar cleaned up")
                                            except:
                                                pass
                                                
                                            return True
                                        else:
                                            print(f"❌ Data creation failed: {pillar_response.status}")
                                            print(f"   Response: {pillar_text}")
                                            if "foreign key" in pillar_text.lower():
                                                print("🚨 FOREIGN KEY CONSTRAINT VIOLATION!")
                                            return False
                                else:
                                    print(f"❌ Protected endpoint failed: {me_response.status}")
                                    print(f"   Response: {me_text}")
                                    return False
                        else:
                            print("❌ No access token in response")
                            return False
                    else:
                        print(f"❌ Login failed: {response.status}")
                        print(f"   Response: {response_text}")
                        return False
                        
            except Exception as e:
                print(f"❌ Authentication test failed: {e}")
                return False
        
        # Clean up test user
        print(f"\n5️⃣ Cleaning up test user...")
        try:
            supabase.table('user_stats').delete().eq('user_id', test_user_id).execute()
            supabase.table('user_profiles').delete().eq('id', test_user_id).execute()  
            supabase.table('users').delete().eq('id', test_user_id).execute()
            print("🧹 Test user cleaned up")
        except Exception as cleanup_error:
            print(f"⚠️ Cleanup failed: {cleanup_error}")
        
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(create_test_user_and_verify_auth())
    
    if success:
        print("\n" + "="*60)
        print("🎉 AUTHENTICATION SYSTEM IS WORKING!")
        print("✅ User creation: SUCCESS")
        print("✅ Login: SUCCESS") 
        print("✅ Protected endpoints: SUCCESS")
        print("✅ Data creation: SUCCESS")
        print("✅ Foreign key constraints: RESOLVED")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ AUTHENTICATION SYSTEM HAS ISSUES")
        print("🔍 Manual debugging required")
        print("="*60)