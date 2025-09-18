#!/usr/bin/env python3
"""
Test script to reproduce the foreign key constraint issue
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')
sys.path.append('/app/backend')

from supabase_client import get_supabase_client
from models import PillarCreate
from services import PillarService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_foreign_key_issue():
    """Test creating data with a Supabase Auth user ID"""
    try:
        # Get Supabase client
        supabase = await get_supabase_client()
        
        print("🔍 Testing foreign key constraint issue...")
        
        # Test 1: Check if there are users in both tables
        print("\n1️⃣ Checking user tables...")
        
        # Check users table
        try:
            users_result = supabase.table('users').select('id, email, username').limit(5).execute()
            print(f"✅ Legacy 'users' table: {len(users_result.data)} users found")
            if users_result.data:
                print(f"   Sample user: {users_result.data[0]}")
        except Exception as e:
            print(f"❌ Error accessing 'users' table: {e}")
        
        # Check user_profiles table
        try:
            profiles_result = supabase.table('user_profiles').select('id, username').limit(5).execute()
            print(f"✅ 'user_profiles' table: {len(profiles_result.data)} profiles found")
            if profiles_result.data:
                print(f"   Sample profile: {profiles_result.data[0]}")
        except Exception as e:
            print(f"❌ Error accessing 'user_profiles' table: {e}")
        
        # Check auth.users via RPC or admin query
        try:
            auth_users_result = supabase.rpc('get_auth_users_count').execute()
            print(f"✅ Supabase auth.users accessible")
        except Exception as e:
            print(f"⚠️ Cannot directly access auth.users (expected): {e}")
        
        # Test 2: Try creating a pillar with a test user ID
        print("\n2️⃣ Testing pillar creation...")
        
        # Get a test user ID from users table
        if users_result.data:
            test_user_id = users_result.data[0]['id']
            print(f"📝 Using test user ID: {test_user_id}")
            
            try:
                pillar_data = PillarCreate(
                    name="Test Foreign Key Pillar",
                    description="Testing foreign key constraints",
                    icon="🔧",
                    color="#FF5722"
                )
                
                pillar = await PillarService.create_pillar(test_user_id, pillar_data)
                print(f"✅ Pillar created successfully: {pillar.id}")
                
                # Clean up - delete the test pillar
                await PillarService.delete_pillar(test_user_id, pillar.id)
                print("🧹 Test pillar deleted")
                
            except Exception as e:
                print(f"❌ Failed to create pillar: {e}")
                print(f"   Error type: {type(e).__name__}")
                
        # Test 3: Try with user_profiles user ID
        print("\n3️⃣ Testing with user_profiles ID...")
        
        if profiles_result.data:
            profile_user_id = profiles_result.data[0]['id']
            print(f"📝 Using profile user ID: {profile_user_id}")
            
            try:
                pillar_data = PillarCreate(
                    name="Test Profile Pillar",
                    description="Testing with user_profiles ID",
                    icon="👤",
                    color="#2196F3"
                )
                
                pillar = await PillarService.create_pillar(profile_user_id, pillar_data)
                print(f"✅ Pillar created with profile ID: {pillar.id}")
                
                # Clean up
                await PillarService.delete_pillar(profile_user_id, pillar.id)
                print("🧹 Test pillar deleted")
                
            except Exception as e:
                print(f"❌ Failed to create pillar with profile ID: {e}")
                print(f"   Error type: {type(e).__name__}")
        
        # Test 4: Check table constraints
        print("\n4️⃣ Checking table constraints...")
        
        try:
            # Check pillars table structure
            pillars_result = supabase.table('pillars').select('user_id').limit(1).execute()
            print("✅ Pillars table accessible")
            
            # Get table information
            table_info = supabase.rpc('get_table_constraints', {'table_name': 'pillars'}).execute()
            print("✅ Table constraints query executed")
            
        except Exception as e:
            print(f"⚠️ Could not get detailed constraint info: {e}")
        
        print("\n✅ Foreign key constraint test completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_foreign_key_issue())