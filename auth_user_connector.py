#!/usr/bin/env python3
"""
Find and Connect Existing Supabase Auth Users
Find existing auth users and create proper user_profiles connections
"""

import asyncio
import aiohttp
import json
import os
from supabase import create_client, Client
from supabase.client import AuthClientError
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

class AuthUserConnector:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        self.supabase = None
        
    async def initialize(self):
        """Initialize Supabase client"""
        self.supabase = create_client(self.supabase_url, self.service_key)
        print("✅ Supabase client initialized")
        
    async def find_auth_user_by_email(self, email):
        """Try to find auth user by email using different methods"""
        try:
            # Method 1: Try admin list users (may work with service role)
            try:
                response = self.supabase.auth.admin.list_users()
                if hasattr(response, 'data') and response.data:
                    for user in response.data:
                        if hasattr(user, 'email') and user.email == email:
                            print(f"✅ Found auth user by admin list: {user.email} (ID: {user.id})")
                            return user
                elif hasattr(response, '__iter__'):
                    # Response might be iterable directly
                    for user in response:
                        if hasattr(user, 'email') and user.email == email:
                            print(f"✅ Found auth user by iteration: {user.email} (ID: {user.id})")
                            return user
            except Exception as e:
                print(f"⚠️ Admin list users failed: {e}")
                
            # Method 2: Try to get user by email (may not work)
            try:
                result = self.supabase.auth.admin.get_user_by_email(email)
                if result and hasattr(result, 'user') and result.user:
                    print(f"✅ Found auth user by email lookup: {result.user.email} (ID: {result.user.id})")
                    return result.user
            except Exception as e:
                print(f"⚠️ Get user by email failed: {e}")
                
            # Method 3: Try login to get user ID (hacky but might work)
            try:
                # This won't actually log in but might give us user info
                login_result = self.supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": "wrongpassword"  # Intentionally wrong
                })
            except Exception as e:
                # Check if error contains user info
                error_str = str(e)
                if "Invalid login credentials" in error_str:
                    print(f"⚠️ User exists in auth but password wrong (expected)")
                else:
                    print(f"⚠️ Login test error: {e}")
                    
            return None
            
        except Exception as e:
            print(f"❌ Error finding auth user: {e}")
            return None
            
    async def create_user_profile_for_auth_id(self, auth_user_id, legacy_user_data):
        """Create user_profiles entry for a known auth user ID"""
        try:
            profile_data = {
                "id": auth_user_id,
                "username": legacy_user_data.get("username", ""),
                "first_name": legacy_user_data.get("first_name", ""),
                "last_name": legacy_user_data.get("last_name", ""),
                "is_active": legacy_user_data.get("is_active", True),
                "level": legacy_user_data.get("level", 1),
                "total_points": legacy_user_data.get("total_points", 0),
                "current_streak": legacy_user_data.get("current_streak", 0)
            }
            
            result = self.supabase.table('user_profiles').upsert(profile_data).execute()
            if result.data:
                print(f"✅ Created/updated user_profiles for auth ID: {auth_user_id}")
                return True
            else:
                print(f"❌ Failed to create user_profiles for {auth_user_id}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating user profile: {e}")
            return False
            
    async def test_pillar_with_auth_id(self, auth_user_id):
        """Test pillar creation with auth user ID"""
        try:
            pillar_data = {
                "user_id": auth_user_id,
                "name": "Auth ID Test Pillar",
                "description": "Testing with found auth user ID"
            }
            
            result = self.supabase.table('pillars').insert(pillar_data).execute()
            if result.data:
                pillar_id = result.data[0]['id']
                print(f"🎉 SUCCESS: Pillar created with auth user ID {auth_user_id}")
                
                # Clean up
                self.supabase.table('pillars').delete().eq('id', pillar_id).execute()
                return True
            else:
                print(f"❌ Pillar creation failed with auth ID {auth_user_id}")
                return False
                
        except Exception as e:
            print(f"❌ Pillar creation error with auth ID {auth_user_id}: {e}")
            return False
            
    async def try_common_auth_user_patterns(self):
        """Try to guess auth user IDs based on common patterns"""
        print("\n🔍 TRYING COMMON AUTH USER ID PATTERNS")
        
        # Get the legacy user data
        test_user_id = "2d9fb107-0f47-42f9-b29b-605e96850599"
        legacy_user = self.supabase.table('users').select('*').eq('id', test_user_id).execute()
        
        if not legacy_user.data:
            print("❌ Legacy user not found")
            return False
            
        user_data = legacy_user.data[0]
        email = user_data['email']
        
        # Pattern 1: Try the exact same UUID (sometimes auth.users uses same ID)
        print(f"📝 Pattern 1: Testing exact same UUID {test_user_id}")
        success = await self.test_pillar_with_auth_id(test_user_id)
        if success:
            await self.create_user_profile_for_auth_id(test_user_id, user_data)
            return test_user_id
            
        # Pattern 2: Try some common UUID variations (just in case)
        print(f"📝 Pattern 2: Testing UUID variations")
        
        # We could try variations but that's not practical
        # Instead, let's try a different approach
        
        return None
        
    async def manual_auth_user_setup(self):
        """Manual setup approach"""
        print("\n🔧 MANUAL AUTH USER SETUP APPROACH")
        print("Since automatic detection failed, we need to:")
        print()
        print("1. Check the Supabase Dashboard → Authentication → Users")
        print("2. Find the user: nav.test@aurumlife.com")
        print("3. Copy their auth user ID")
        print("4. Create a user_profiles entry with that ID")
        print()
        print("Alternatively, we can try to manually create the auth user with known credentials:")
        
        # Try to create auth user with known password
        try:
            # Create with the password we know they should have
            auth_data = {
                "email": "nav.test@aurumlife.com",
                "password": "testpassword123",
                "email_confirm": True
            }
            
            # Force create even if exists (upsert style)
            result = self.supabase.auth.admin.create_user(auth_data)
            if result and hasattr(result, 'user'):
                print(f"✅ Successfully created/found auth user: {result.user.id}")
                return result.user.id
            else:
                print(f"⚠️ Auth user creation returned: {result}")
                
        except Exception as e:
            error_msg = str(e)
            if "already been registered" in error_msg:
                print("⚠️ User already exists in auth - need to find their ID")
            else:
                print(f"❌ Auth user creation error: {e}")
                
        return None

async def main():
    """Connect existing auth users"""
    connector = AuthUserConnector()
    
    try:
        await connector.initialize()
        
        print("🔍 FINDING EXISTING SUPABASE AUTH USERS")
        print("="*50)
        
        # Try to find the test user in auth
        auth_user = await connector.find_auth_user_by_email("nav.test@aurumlife.com")
        
        if auth_user:
            # Test pillar creation with found auth user
            auth_user_id = auth_user.id
            success = await connector.test_pillar_with_auth_id(auth_user_id)
            
            if success:
                print(f"\n🎉 SOLUTION FOUND!")
                print(f"Auth User ID: {auth_user_id}")
                print("Foreign key constraint issue resolved!")
            else:
                print(f"\n❌ Auth user found but pillar creation still fails")
        else:
            # Try pattern matching
            auth_user_id = await connector.try_common_auth_user_patterns()
            
            if not auth_user_id:
                # Manual setup required
                auth_user_id = await connector.manual_auth_user_setup()
                
        if not auth_user_id:
            print("\n💡 NEXT STEPS:")
            print("1. Check Supabase Dashboard for existing auth users")
            print("2. Note the auth user ID for nav.test@aurumlife.com") 
            print("3. Run this script with the correct auth user ID")
            
    except Exception as e:
        print(f"❌ Connection attempt failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())