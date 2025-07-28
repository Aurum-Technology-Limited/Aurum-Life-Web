#!/usr/bin/env python3
"""
Supabase Auth User Migration Script
Migrate users from legacy public.users to proper Supabase auth.users structure
"""

import asyncio
import aiohttp
import json
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

class SupabaseAuthMigration:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        self.supabase = None
        
    async def initialize(self):
        """Initialize Supabase client"""
        self.supabase = create_client(self.supabase_url, self.service_key)
        print("✅ Supabase client initialized")
        
    async def create_supabase_auth_user(self, user_data):
        """Create a user in Supabase Auth system"""
        try:
            # Use Supabase Admin API to create auth user
            auth_data = {
                "email": user_data["email"],
                "password": "temppassword123",  # Temporary password
                "email_confirm": True,  # Skip email confirmation
                "user_metadata": {
                    "username": user_data.get("username", ""),
                    "first_name": user_data.get("first_name", ""),
                    "last_name": user_data.get("last_name", ""),
                    "migrated_from_legacy": True,
                    "original_id": user_data["id"]
                }
            }
            
            # Create user via Supabase Auth Admin API
            result = self.supabase.auth.admin.create_user(auth_data)
            
            if result.user:
                print(f"✅ Created Supabase auth user: {result.user.email}")
                return result.user
            else:
                print(f"❌ Failed to create auth user for {user_data['email']}")
                return None
                
        except Exception as e:
            if "User already registered" in str(e):
                print(f"⚠️ User {user_data['email']} already exists in auth")
                # Try to get existing user
                try:
                    users = self.supabase.auth.admin.list_users()
                    for auth_user in users:
                        if auth_user.email == user_data["email"]:
                            return auth_user
                except:
                    pass
            else:
                print(f"❌ Error creating auth user for {user_data['email']}: {e}")
            return None
            
    async def create_user_profile(self, auth_user, legacy_user_data):
        """Create user_profiles entry for the auth user"""
        try:
            profile_data = {
                "id": auth_user.id,  # Use auth user ID
                "username": legacy_user_data.get("username", ""),
                "first_name": legacy_user_data.get("first_name", ""),
                "last_name": legacy_user_data.get("last_name", ""),
                "is_active": legacy_user_data.get("is_active", True),
                "level": legacy_user_data.get("level", 1),
                "total_points": legacy_user_data.get("total_points", 0),
                "current_streak": legacy_user_data.get("current_streak", 0)
            }
            
            result = self.supabase.table('user_profiles').insert(profile_data).execute()
            if result.data:
                print(f"✅ Created user_profiles entry for {auth_user.email}")
                return True
            else:
                print(f"❌ Failed to create user_profiles for {auth_user.email}")
                return False
                
        except Exception as e:
            if "duplicate key" in str(e):
                print(f"⚠️ User profile already exists for {auth_user.email}")
                return True
            else:
                print(f"❌ Error creating user profile: {e}")
                return False
                
    async def migrate_test_user(self):
        """Migrate the specific test user that's failing"""
        test_user_id = "2d9fb107-0f47-42f9-b29b-605e96850599"
        
        try:
            # Get the test user from legacy table
            legacy_user = self.supabase.table('users').select('*').eq('id', test_user_id).execute()
            
            if not legacy_user.data:
                print(f"❌ Test user {test_user_id} not found in legacy table")
                return False
                
            user_data = legacy_user.data[0]
            print(f"🎯 Migrating test user: {user_data['email']} ({user_data['username']})")
            
            # Create Supabase auth user
            auth_user = await self.create_supabase_auth_user(user_data)
            if not auth_user:
                return False
                
            # Create user profile
            profile_created = await self.create_user_profile(auth_user, user_data)
            if not profile_created:
                return False
                
            print(f"✅ Successfully migrated test user!")
            print(f"   Auth ID: {auth_user.id}")
            print(f"   Email: {auth_user.email}")
            
            return auth_user.id
            
        except Exception as e:
            print(f"❌ Test user migration failed: {e}")
            return False
            
    async def test_pillar_creation_with_auth_user(self, auth_user_id):
        """Test pillar creation with the migrated auth user"""
        try:
            pillar_data = {
                "user_id": auth_user_id,
                "name": "Auth User Test Pillar",
                "description": "Testing with proper auth.users ID"
            }
            
            result = self.supabase.table('pillars').insert(pillar_data).execute()
            if result.data:
                pillar_id = result.data[0]['id']
                print(f"✅ BREAKTHROUGH: Pillar creation SUCCESSFUL with auth user ID!")
                print(f"   Pillar ID: {pillar_id}")
                print(f"   Auth User ID: {auth_user_id}")
                
                # Clean up test data
                self.supabase.table('pillars').delete().eq('id', pillar_id).execute()
                print("✅ Test pillar cleaned up")
                return True
            else:
                print("❌ Pillar creation failed - no data returned")
                return False
                
        except Exception as e:
            print(f"❌ Pillar creation test failed: {e}")
            return False
            
    async def alternative_fix_attempt(self):
        """Alternative approach: Try to create user_profiles entries that match auth.users"""
        print("\n🔄 ALTERNATIVE APPROACH: Create user_profiles with auth.users IDs")
        
        try:
            # This is a simpler approach - create user_profiles entries with the
            # assumption that auth.users already has some users
            
            # Check if we can list auth users (may not work with client library)
            # For now, let's create a user_profiles entry with a known auth user ID format
            
            print("⚠️ This approach requires direct database access to auth.users")
            print("   The client library may not have access to list auth.users directly")
            print("   Consider using Supabase dashboard to:")
            print("   1. Check existing auth.users")
            print("   2. Create user_profiles entries that match auth.users IDs")
            
        except Exception as e:
            print(f"❌ Alternative approach failed: {e}")

async def main():
    """Run Supabase auth migration"""
    migration = SupabaseAuthMigration()
    
    try:
        await migration.initialize()
        
        print("🚀 SUPABASE AUTH USER MIGRATION")
        print("="*50)
        print("This script will:")
        print("1. Create a Supabase auth user for the test user")
        print("2. Create corresponding user_profiles entry")
        print("3. Test pillar creation with proper auth user ID")
        print()
        
        # Migrate the test user
        auth_user_id = await migration.migrate_test_user()
        
        if auth_user_id:
            # Test pillar creation
            success = await migration.test_pillar_creation_with_auth_user(auth_user_id)
            
            if success:
                print("\n🎉 MIGRATION SUCCESSFUL!")
                print("The foreign key constraint issue has been resolved!")
                print("Users now exist in the proper auth.users table.")
            else:
                print("\n❌ Migration created user but pillar creation still fails")
                await migration.alternative_fix_attempt()
        else:
            print("\n❌ User migration failed")
            await migration.alternative_fix_attempt()
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())