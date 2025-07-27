#!/usr/bin/env python3

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

async def sync_specific_user(user_id: str):
    """
    Sync a specific user from user_profiles to legacy users table
    """
    try:
        supabase = await get_supabase_client()
        
        print(f"🔄 Syncing specific user: {user_id}")
        
        # Get user from user_profiles
        profile_result = supabase.table('user_profiles').select('*').eq('id', user_id).execute()
        
        if not profile_result.data:
            print(f"❌ User {user_id} not found in user_profiles")
            return False
            
        profile = profile_result.data[0]
        print(f"📝 Found user profile: {profile.get('username', 'no username')}")
        
        # Check if user already exists in legacy users table
        existing_user = supabase.table('users').select('id').eq('id', user_id).execute()
        
        if existing_user.data:
            print(f"✅ User {user_id} already exists in legacy users table")
            return True
        
        # Create user record with profile data
        user_data = {
            'id': profile['id'],
            'username': profile.get('username', f'user_{profile["id"][:8]}'),
            'email': profile.get('email', f"user_{profile['id'][:8]}@aurumlife.com"),
            'first_name': profile.get('first_name', ''),
            'last_name': profile.get('last_name', ''),
            'password_hash': None,  # Supabase Auth user
            'google_id': profile.get('google_id'),
            'profile_picture': profile.get('profile_picture'),
            'is_active': profile.get('is_active', True),
            'level': profile.get('level', 1),
            'total_points': profile.get('total_points', 0),
            'current_streak': profile.get('current_streak', 0),
            'created_at': profile.get('created_at'),
            'updated_at': profile.get('updated_at')
        }
        
        # Insert into legacy users table
        result = supabase.table('users').insert(user_data).execute()
        print(f"✅ Created user in legacy table: {user_id}")
        
        # Also ensure user_stats exists
        try:
            existing_stats = supabase.table('user_stats').select('id').eq('user_id', user_id).execute()
            if not existing_stats.data:
                stats_data = {
                    'user_id': user_id,
                    'total_journal_entries': 0,
                    'total_tasks': 0,
                    'tasks_completed': 0,
                    'total_areas': 0,
                    'total_projects': 0,
                    'completed_projects': 0,
                    'courses_enrolled': 0,
                    'courses_completed': 0,
                    'badges_earned': 0
                }
                supabase.table('user_stats').insert(stats_data).execute()
                print(f"📊 Created user_stats for: {user_id}")
        except Exception as stats_error:
            print(f"⚠️ Could not create user_stats: {stats_error}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to sync user {user_id}: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python sync_user.py <user_id>")
        sys.exit(1)
    
    user_id = sys.argv[1]
    asyncio.run(sync_specific_user(user_id))