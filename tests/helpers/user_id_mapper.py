#!/usr/bin/env python3
"""
Create User ID Mapping Table
Create a mapping between legacy user IDs and Supabase Auth user IDs
"""

import asyncio
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

class UserIDMapper:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        self.supabase = None
        
    async def initialize(self):
        """Initialize Supabase client"""
        self.supabase = create_client(self.supabase_url, self.service_key)
        print("✅ Supabase client initialized")
        
    async def create_mapping_for_test_user(self):
        """Create mapping for the test user"""
        legacy_user_id = "2d9fb107-0f47-42f9-b29b-605e96850599"
        auth_user_id = "272edb74-8be3-4504-818c-b1dd42c63ebe"
        email = "nav.test@aurumlife.com" 
        
        # Create user_profiles entry with auth user ID
        try:
            # Get legacy user data
            legacy_user = self.supabase.table('users').select('*').eq('id', legacy_user_id).execute()
            if not legacy_user.data:
                print("❌ Legacy user not found")
                return False
                
            user_data = legacy_user.data[0]
            
            # Create/update user_profiles with auth user ID
            profile_data = {
                "id": auth_user_id,  # Use auth user ID as primary key
                "username": user_data.get("username", ""),
                "first_name": user_data.get("first_name", ""),
                "last_name": user_data.get("last_name", ""),
                "is_active": user_data.get("is_active", True),
                "level": user_data.get("level", 1),
                "total_points": user_data.get("total_points", 0),
                "current_streak": user_data.get("current_streak", 0)
            }
            
            result = self.supabase.table('user_profiles').upsert(profile_data).execute()
            if result.data:
                print(f"✅ Created user_profiles entry with auth ID: {auth_user_id}")
                
                # Test pillar creation
                await self.test_pillar_creation(auth_user_id)
                return True
            else:
                print("❌ Failed to create user_profiles entry")
                return False
                
        except Exception as e:
            print(f"❌ Error creating mapping: {e}")
            return False
            
    async def test_pillar_creation(self, auth_user_id):
        """Test pillar creation with auth user ID"""
        try:
            pillar_data = {
                "user_id": auth_user_id,
                "name": "Final Test Pillar",
                "description": "Testing with proper auth user ID mapping"
            }
            
            result = self.supabase.table('pillars').insert(pillar_data).execute()
            if result.data:
                pillar_id = result.data[0]['id']
                print(f"🎉 SUCCESS: Pillar created with auth user ID!")
                print(f"   Pillar ID: {pillar_id}")
                print(f"   Auth User ID: {auth_user_id}")
                
                # Clean up test data
                self.supabase.table('pillars').delete().eq('id', pillar_id).execute()
                print("✅ Test pillar cleaned up")
                return True
            else:
                print("❌ Pillar creation failed")
                return False
                
        except Exception as e:
            print(f"❌ Pillar creation error: {e}")
            return False

async def main():
    """Create user ID mapping"""
    mapper = UserIDMapper()
    
    try:
        await mapper.initialize()  
        
        print("🗺️ CREATING USER ID MAPPING")
        print("="*40)
        print("Mapping legacy user ID to Supabase Auth user ID")
        print(f"Legacy ID: 2d9fb107-0f47-42f9-b29b-605e96850599")
        print(f"Auth ID:   272edb74-8be3-4504-818c-b1dd42c63ebe")
        print()
        
        success = await mapper.create_mapping_for_test_user()
        
        if success:
            print("\n🎉 USER ID MAPPING SUCCESSFUL!")
            print("The database is now properly configured.")
            print("Next step: Update authentication system to use auth user IDs.")
        else:
            print("\n❌ User ID mapping failed")
            
    except Exception as e:
        print(f"❌ Mapping failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())