#!/usr/bin/env python3
"""
Debug the foreign key constraint issue by checking the database state
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')
sys.path.append('/app/backend')

from supabase_client import get_supabase_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def debug_foreign_key_issue():
    """Debug the foreign key constraint issue"""
    
    print("🔍 Debugging Foreign Key Constraint Issue...")
    
    try:
        supabase = await get_supabase_client()
        
        # Step 1: Check what users exist in both tables
        print("\n1️⃣ Checking users in both tables...")
        
        # Check legacy users table
        users_result = supabase.table('users').select('id, email, username').execute()
        print(f"📊 Legacy users table: {len(users_result.data)} users")
        for user in users_result.data[:3]:
            print(f"   - {user['email']} ({user['id'][:8]}...)")
        
        # Check user_profiles table  
        profiles_result = supabase.table('user_profiles').select('id, username').execute()
        print(f"📊 User profiles table: {len(profiles_result.data)} profiles")
        for profile in profiles_result.data[:3]:
            print(f"   - {profile.get('username', 'no username')} ({profile['id'][:8]}...)")
        
        # Step 2: Test with an existing user from legacy table
        if users_result.data:
            test_user = users_result.data[0]
            user_id = test_user['id']
            user_email = test_user['email']
            
            print(f"\n2️⃣ Testing with existing user: {user_email} ({user_id[:8]}...)")
            
            # Try to create a pillar with this user
            pillar_data = {
                'user_id': user_id,
                'name': 'Debug Test Pillar',
                'description': 'Testing foreign key constraints',
                'icon': '🔍',
                'color': '#FF5722'
            }
            
            try:
                result = supabase.table('pillars').insert(pillar_data).execute()
                pillar_id = result.data[0]['id']
                print("✅ SUCCESS: Pillar created successfully!")
                print(f"   Pillar ID: {pillar_id}")
                
                # Clean up
                supabase.table('pillars').delete().eq('id', pillar_id).execute()
                print("🧹 Test pillar cleaned up")
                
            except Exception as e:
                print(f"❌ FAILED: {e}")
                error_msg = str(e)
                
                if "foreign key constraint" in error_msg.lower():
                    print("🚨 FOREIGN KEY CONSTRAINT VIOLATION!")
                    
                    # Check if the user_id actually exists
                    print(f"\n🔍 Checking if user {user_id} exists...")
                    check_result = supabase.table('users').select('id').eq('id', user_id).execute()
                    if check_result.data:
                        print(f"✅ User {user_id} DOES exist in users table")
                        print("🚨 This means the foreign key constraint is referencing the WRONG table!")
                    else:
                        print(f"❌ User {user_id} does NOT exist in users table")
        
        # Step 3: Check what table the foreign key constraint actually references
        print(f"\n3️⃣ Investigating the foreign key constraint...")
        
        # Try creating pillar with a known non-existent user ID
        fake_user_id = "00000000-0000-0000-0000-000000000000"
        fake_pillar_data = {
            'user_id': fake_user_id,
            'name': 'FK Test Pillar',
            'description': 'Testing constraints',
            'icon': '🧪',
            'color': '#4CAF50'
        }
        
        try:
            result = supabase.table('pillars').insert(fake_pillar_data).execute()
            print("⚠️ UNEXPECTED: Pillar created with fake user ID (no foreign key constraint)")
        except Exception as e:
            error_msg = str(e)
            print(f"📋 Expected error: {error_msg}")
            
            if 'not present in table "users"' in error_msg:
                print("✅ Foreign key constraint references legacy 'users' table")
            elif 'not present in table "auth"' in error_msg:
                print("✅ Foreign key constraint references correct 'auth.users' table")
            else:
                print("❓ Foreign key constraint references unknown table")
        
        # Step 4: Summary
        print(f"\n4️⃣ Summary:")
        print(f"   • Legacy users exist: {len(users_result.data) > 0}")
        print(f"   • User profiles exist: {len(profiles_result.data) > 0}")
        print(f"   • Foreign key constraint issue confirmed")
        
        return True
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(debug_foreign_key_issue())