#!/usr/bin/env python3
"""
Check user_profiles table and fix user lookup
"""

import asyncio
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

async def check_user_profiles():
    """Check user_profiles table"""
    supabase_url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    supabase = create_client(supabase_url, service_key)
    
    auth_user_id = "272edb74-8be3-4504-818c-b1dd42c63ebe"
    
    print(f"🔍 Checking user_profiles for auth user ID: {auth_user_id}")
    
    # Check user_profiles table
    try:
        result = supabase.table('user_profiles').select('*').eq('id', auth_user_id).execute()
        if result.data:
            print("✅ User found in user_profiles:")
            user_data = result.data[0]
            for key, value in user_data.items():
                print(f"   {key}: {value}")
        else:
            print("❌ User NOT found in user_profiles table")
            print("Creating user_profiles entry...")
            
            # Create user_profiles entry
            profile_data = {
                "id": auth_user_id,
                "username": "navtest",
                "first_name": "Nav",
                "last_name": "Test",
                "is_active": True,
                "level": 1,
                "total_points": 0,
                "current_streak": 0
            }
            
            create_result = supabase.table('user_profiles').insert(profile_data).execute()
            if create_result.data:
                print("✅ Created user_profiles entry")
            else:
                print("❌ Failed to create user_profiles entry")
                
    except Exception as e:
        print(f"❌ Error checking user_profiles: {e}")
        
    # Also check legacy users table
    try:
        result = supabase.table('users').select('*').eq('id', auth_user_id).execute()
        if result.data:
            print("✅ User found in legacy users table")
        else:
            print("❌ User NOT found in legacy users table")
    except Exception as e:
        print(f"❌ Error checking users table: {e}")

if __name__ == "__main__":
    asyncio.run(check_user_profiles())