#!/usr/bin/env python3
"""
Check user data in database to understand the user profile mapping issue
"""

import sys
import os
sys.path.append('/app/backend')

import asyncio
from supabase_client import supabase_manager

async def check_user_data():
    try:
        print("🔍 CHECKING USER DATA IN DATABASE")
        print("=" * 60)
        
        # Check users table for marc.alleyne
        print("\n1. Looking for marc.alleyne in users table:")
        marc_user = await supabase_manager.find_document('users', {'email': 'marc.alleyne@aurumtechnologyltd.com'})
        if marc_user:
            print(f"   ✅ Found: ID={marc_user.get('id')}, Username={marc_user.get('username')}, Email={marc_user.get('email')}")
        else:
            print("   ❌ Not found in users table")
        
        # Check user_profiles table for all users
        print("\n2. All user profiles in user_profiles table:")
        all_profiles = await supabase_manager.find_documents('user_profiles', {}, limit=10)
        for profile in all_profiles:
            print(f"   ID: {profile.get('id')}, Username: {profile.get('username')}, First: {profile.get('first_name')}, Last: {profile.get('last_name')}")
            
        # Check users table for all users
        print("\n3. All users in users table:")
        all_users = await supabase_manager.find_documents('users', {}, limit=10)
        for user in all_users:
            print(f"   ID: {user.get('id')}, Username: {user.get('username')}, Email: {user.get('email')}, First: {user.get('first_name')}, Last: {user.get('last_name')}")
            
        # Check the specific problematic user ID
        print(f"\n4. Checking problematic user ID: 6848f065-2d12-4c4e-88c4-80f375358d7b")
        problem_profile = await supabase_manager.find_document('user_profiles', {'id': '6848f065-2d12-4c4e-88c4-80f375358d7b'})
        if problem_profile:
            print(f"   user_profiles: Username={problem_profile.get('username')}, First={problem_profile.get('first_name')}, Last={problem_profile.get('last_name')}")
        
        problem_user = await supabase_manager.find_document('users', {'id': '6848f065-2d12-4c4e-88c4-80f375358d7b'})
        if problem_user:
            print(f"   users: Username={problem_user.get('username')}, Email={problem_user.get('email')}, First={problem_user.get('first_name')}, Last={problem_user.get('last_name')}")
            
        # Check if there's a marc.alleyne user with different ID
        print(f"\n5. Looking for marc.alleyne users by name:")
        marc_profiles = await supabase_manager.find_documents('user_profiles', {}, limit=50)
        marc_users = await supabase_manager.find_documents('users', {}, limit=50)
        
        for profile in marc_profiles:
            if 'marc' in str(profile.get('username', '')).lower() or 'alleyne' in str(profile.get('username', '')).lower() or \
               'marc' in str(profile.get('first_name', '')).lower() or 'alleyne' in str(profile.get('last_name', '')).lower():
                print(f"   user_profiles match: ID={profile.get('id')}, Username={profile.get('username')}, First={profile.get('first_name')}, Last={profile.get('last_name')}")
        
        for user in marc_users:
            if 'marc' in str(user.get('username', '')).lower() or 'alleyne' in str(user.get('username', '')).lower() or \
               'marc' in str(user.get('first_name', '')).lower() or 'alleyne' in str(user.get('last_name', '')).lower() or \
               'marc.alleyne' in str(user.get('email', '')).lower():
                print(f"   users match: ID={user.get('id')}, Username={user.get('username')}, Email={user.get('email')}, First={user.get('first_name')}, Last={user.get('last_name')}")
            
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_user_data())