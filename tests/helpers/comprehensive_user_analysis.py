#!/usr/bin/env python3
"""
Comprehensive User Table Analysis
Check all possible user tables and their relationships
"""

import asyncio
import aiohttp
import json
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

class ComprehensiveUserAnalysis:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        self.supabase = None
        self.test_user_id = "2d9fb107-0f47-42f9-b29b-605e96850599"
        
    async def initialize(self):
        """Initialize Supabase client"""
        self.supabase = create_client(self.supabase_url, self.service_key)
        print("✅ Supabase client initialized")
        
    async def check_all_user_tables(self):
        """Check all possible user-related tables"""
        print(f"\n🔍 COMPREHENSIVE USER TABLE ANALYSIS for user: {self.test_user_id}")
        
        tables_to_check = [
            'users',          # Legacy users table
            'user_profiles',  # Profile extension table
            'auth.users',     # Supabase auth users (may not be accessible)
        ]
        
        user_found_in = []
        
        for table in tables_to_check:
            try:
                print(f"\n📋 Checking table: {table}")
                
                if table == 'auth.users':
                    # Special handling for auth.users - may not be directly accessible
                    print("   ⚠️ auth.users is Supabase-managed, may not be directly queryable")
                    continue
                    
                result = self.supabase.table(table).select('*').eq('id', self.test_user_id).execute()
                
                if result.data:
                    user_data = result.data[0]
                    user_found_in.append(table)
                    print(f"   ✅ User FOUND in {table}:")
                    print(f"      ID: {user_data.get('id', 'NO_ID')}")
                    print(f"      Email: {user_data.get('email', 'NO_EMAIL')}")
                    print(f"      Username: {user_data.get('username', 'NO_USERNAME')}")
                    print(f"      Created: {user_data.get('created_at', 'NO_DATE')}")
                else:
                    print(f"   ❌ User NOT FOUND in {table}")
                    
            except Exception as e:
                print(f"   ❌ Error accessing {table}: {e}")
                
        return user_found_in
        
    async def create_direct_pillar_test(self):
        """Try to create a pillar with different approaches"""
        print(f"\n🧪 DIRECT PILLAR CREATION TESTS")
        
        # Test 1: Create pillar using the exact user_id that exists in legacy users table
        print("\n📝 Test 1: Using user_id from legacy users table")
        try:
            pillar_data_1 = {
                "id": "test-pillar-1",  # Explicit ID to avoid conflicts
                "user_id": self.test_user_id,
                "name": "Direct Test Pillar 1",
                "description": "Testing with legacy user_id"
            }
            
            result = self.supabase.table('pillars').insert(pillar_data_1).execute()
            if result.data:
                print("   ✅ SUCCESS: Pillar created with legacy user_id")
                # Clean up
                self.supabase.table('pillars').delete().eq('id', 'test-pillar-1').execute()
            else:
                print("   ❌ FAILED: No data returned")
                
        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            
        # Test 2: Check if there's a different user_id we should be using
        print("\n📝 Test 2: Check for user_id variations")
        try:
            # Get all users and see their IDs
            all_users = self.supabase.table('users').select('id, email, username').execute()
            print(f"   📊 Found {len(all_users.data)} users in legacy table:")
            
            for user in all_users.data[:10]:  # Show first 10
                user_id = user.get('id', 'NO_ID')
                email = user.get('email', 'NO_EMAIL')
                username = user.get('username', 'NO_USERNAME')
                
                if 'nav' in email or 'test' in email:
                    print(f"      🎯 TEST USER: {user_id} - {email} - {username}")
                    
                    # Try creating pillar with this user_id
                    try:
                        test_pillar = {
                            "user_id": user_id,
                            "name": f"Test with {username}",
                            "description": "Testing different user_id"
                        }
                        
                        result = self.supabase.table('pillars').insert(test_pillar).execute()
                        if result.data:
                            created_id = result.data[0]['id']
                            print(f"         ✅ SUCCESS with user_id: {user_id}")
                            # Clean up
                            self.supabase.table('pillars').delete().eq('id', created_id).execute()
                            return user_id  # Return successful user_id
                        else:
                            print(f"         ❌ Failed with user_id: {user_id}")
                    except Exception as pillar_error:
                        print(f"         ❌ Error with {user_id}: {pillar_error}")
                        
        except Exception as e:
            print(f"   ❌ Error in user_id variations test: {e}")
            
        return None
        
    async def investigate_constraint_details(self):
        """Try to get more details about the foreign key constraint"""
        print(f"\n🔍 CONSTRAINT INVESTIGATION")
        
        print("The error consistently shows:")
        print("  - Constraint: pillars_user_id_fkey") 
        print("  - Target table: 'users'")
        print(f"  - Missing key: {self.test_user_id}")
        print()
        print("But we confirmed the user EXISTS in the 'users' table!")
        print("This suggests:")
        print("  1. There might be multiple 'users' tables (different schemas)")
        print("  2. The constraint might be pointing to a different schema")
        print("  3. There might be a data type mismatch (UUID vs String)")
        print("  4. The constraint might be pointing to a table we haven't checked")
        
async def main():
    """Run comprehensive user analysis"""
    analysis = ComprehensiveUserAnalysis()
    
    try:
        await analysis.initialize()
        
        # Check all user tables
        user_found_in = await analysis.check_all_user_tables()
        
        if user_found_in:
            print(f"\n📊 SUMMARY: User found in {len(user_found_in)} tables: {user_found_in}")
            
            # Try direct pillar creation with different approaches
            working_user_id = await analysis.create_direct_pillar_test()
            
            if working_user_id:
                print(f"\n✅ SOLUTION FOUND: Use user_id {working_user_id} for pillar creation")
            else:
                print(f"\n❌ NO SOLUTION FOUND: All user_id attempts failed")
                await analysis.investigate_constraint_details()
        else:
            print(f"\n❌ CRITICAL: User not found in any accessible table")
            
    except Exception as e:
        print(f"❌ Analysis failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())