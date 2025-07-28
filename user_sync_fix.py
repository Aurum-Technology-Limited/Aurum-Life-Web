#!/usr/bin/env python3
"""
User Synchronization Fix
Ensure users exist in the correct table for foreign key constraints
"""

import asyncio
import aiohttp
import json
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

class UserSync:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        self.supabase = None
        
    async def initialize(self):
        """Initialize Supabase client"""
        if not self.supabase_url or not self.service_key:
            raise ValueError("Missing Supabase credentials")
        
        self.supabase = create_client(self.supabase_url, self.service_key)
        print("✅ Supabase client initialized")
        
    async def check_test_user(self):
        """Check the specific test user that's failing"""
        test_user_id = "2d9fb107-0f47-42f9-b29b-605e96850599"
        
        print(f"\n🔍 Checking user: {test_user_id}")
        
        # Check in legacy users table
        try:
            legacy_user = self.supabase.table('users').select('*').eq('id', test_user_id).execute()
            if legacy_user.data:
                user_data = legacy_user.data[0]
                print(f"✅ User EXISTS in legacy 'users' table:")
                print(f"   Email: {user_data.get('email', 'NO_EMAIL')}")
                print(f"   Username: {user_data.get('username', 'NO_USERNAME')}")
                print(f"   Created: {user_data.get('created_at', 'NO_DATE')}")
                return user_data
            else:
                print("❌ User NOT FOUND in legacy 'users' table")
                return None
        except Exception as e:
            print(f"❌ Error checking legacy users table: {e}")
            return None
            
    async def create_missing_user_profile(self, user_data):
        """Create a missing user profile entry if needed"""
        if not user_data:
            return False
            
        user_id = user_data['id']
        
        # Check if user_profiles entry exists
        try:
            profile = self.supabase.table('user_profiles').select('*').eq('id', user_id).execute()
            if profile.data:
                print(f"✅ User profile already exists for {user_id}")
                return True
            else:
                print(f"⚠️ User profile missing for {user_id}, creating...")
                
                # Create user_profiles entry
                profile_data = {
                    'id': user_id,
                    'username': user_data.get('username', 'user'),
                    'first_name': user_data.get('first_name', ''),
                    'last_name': user_data.get('last_name', ''),
                    'is_active': user_data.get('is_active', True),
                    'level': user_data.get('level', 1),
                    'total_points': user_data.get('total_points', 0),
                    'current_streak': user_data.get('current_streak', 0)
                }
                
                result = self.supabase.table('user_profiles').insert(profile_data).execute()
                if result.data:
                    print(f"✅ Created user_profiles entry for {user_id}")
                    return True
                else:
                    print(f"❌ Failed to create user_profiles entry")
                    return False
                    
        except Exception as e:
            print(f"❌ Error handling user_profiles: {e}")
            return False
            
    async def test_pillar_creation_after_fix(self):
        """Test pillar creation after user sync"""
        test_user_id = "2d9fb107-0f47-42f9-b29b-605e96850599"
        
        try:
            pillar_data = {
                "user_id": test_user_id,
                "name": "Post-Fix Test Pillar",
                "description": "Testing after user sync fix"
            }
            
            result = self.supabase.table('pillars').insert(pillar_data).execute()
            if result.data:
                pillar_id = result.data[0]['id']
                print(f"✅ Pillar creation successful after fix: {pillar_id}")
                
                # Clean up test data
                self.supabase.table('pillars').delete().eq('id', pillar_id).execute()
                print("✅ Test pillar cleaned up")
                return True
            else:
                print("❌ Pillar creation still failing")
                return False
                
        except Exception as e:
            print(f"❌ Pillar creation test failed: {e}")
            return False
            
    async def investigate_constraint_target(self):
        """Try to understand what table the constraint actually references"""
        print("\n🔍 INVESTIGATING FOREIGN KEY CONSTRAINT TARGET")
        
        # The error says the constraint is looking for the user in a "users" table
        # But the schema says it should reference "auth.users"
        # This suggests the actual constraint is different from the schema
        
        print("The error message indicates:")
        print("  - Constraint name: pillars_user_id_fkey")
        print("  - Target table: 'users' (not 'auth.users')")
        print("  - This means the actual database has constraints pointing to legacy 'users' table")
        print("  - But the schema file shows it should point to 'auth.users'")
        print()
        print("POSSIBLE SOLUTIONS:")
        print("1. The database was not updated to match supabase_schema.sql")
        print("2. The constraints need to be altered to point to the correct table")
        print("3. We need to ensure users exist in whichever table the constraints reference")

async def main():
    """Run user synchronization fix"""
    sync = UserSync()
    
    try:
        await sync.initialize()
        
        # Check the failing test user
        user_data = await sync.check_test_user()
        
        if user_data:
            # Try creating user profile
            await sync.create_missing_user_profile(user_data)
            
            # Test pillar creation
            success = await sync.test_pillar_creation_after_fix()
            
            if not success:
                await sync.investigate_constraint_target()
        else:
            print("❌ Cannot proceed without user data")
            
    except Exception as e:
        print(f"❌ User sync failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())