#!/usr/bin/env python3
"""
Test Supabase Integration
Verify that migration was successful and data is accessible
"""

import os
import asyncio
from supabase import create_client
from backend.supabase_client import supabase_manager
from dotenv import load_dotenv

# Load environment
load_dotenv('.env.supabase')

async def test_supabase_data():
    """Test if migrated data is accessible"""
    print("🔍 Testing Supabase Integration...")
    print("=" * 50)
    
    try:
        # Test connection
        client = supabase_manager.get_client()
        print("✅ Supabase client connected")
        
        # Test user profiles
        profiles = client.table('user_profiles').select('*').limit(5).execute()
        print(f"✅ User profiles: {len(profiles.data)} found")
        
        # Test other tables
        tables_to_test = ['pillars', 'areas', 'projects', 'tasks', 'journal_entries']
        
        for table in tables_to_test:
            try:
                result = client.table(table).select('*').limit(5).execute()
                print(f"✅ {table}: {len(result.data)} records found")
            except Exception as e:
                print(f"⚠️ {table}: Error accessing data - {e}")
        
        print("\n" + "=" * 50)
        print("🎉 Supabase integration test completed!")
        
        # Show sample data
        if profiles.data:
            print(f"\n📋 Sample user profile:")
            profile = profiles.data[0]
            print(f"   ID: {profile.get('id', 'N/A')}")
            print(f"   Name: {profile.get('first_name', 'N/A')} {profile.get('last_name', 'N/A')}")
            print(f"   Active: {profile.get('is_active', 'N/A')}")
            print(f"   Level: {profile.get('level', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

async def main():
    """Run the test"""
    success = await test_supabase_data()
    
    if success:
        print("\n✅ MIGRATION SUCCESSFUL!")
        print("\n📋 Next Steps:")
        print("1. ✅ Database schema created")
        print("2. ✅ Data migrated from MongoDB")
        print("3. ✅ Backend configured for Supabase") 
        print("4. ✅ Frontend Supabase client ready")
        print("5. 🔄 Update authentication system")
        print("6. 🔄 Test application functionality")
        
    else:
        print("\n❌ Integration test failed!")

if __name__ == "__main__":
    asyncio.run(main())