#!/usr/bin/env python3
"""
Database Foreign Key Diagnosis Script
Diagnose and fix the foreign key constraint issues
"""

import asyncio
import aiohttp
import json
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

class DatabaseDiagnostics:
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
        
    async def check_user_tables(self):
        """Check what user tables exist and their structure"""
        print("\n🔍 DIAGNOSING USER TABLES")
        
        # Check auth.users table (Supabase managed)
        try:
            auth_users = self.supabase.table('users').select('*').execute()
            print(f"✅ Legacy 'users' table found: {len(auth_users.data)} records")
            if auth_users.data:
                print(f"   Sample user: {auth_users.data[0].get('id', 'NO_ID')} - {auth_users.data[0].get('email', 'NO_EMAIL')}")
        except Exception as e:
            print(f"❌ Legacy 'users' table error: {e}")
            
        # Check user_profiles table (should extend auth.users)
        try:
            profiles = self.supabase.table('user_profiles').select('*').execute()
            print(f"✅ user_profiles table found: {len(profiles.data)} records")
            if profiles.data:
                print(f"   Sample profile: {profiles.data[0].get('id', 'NO_ID')} - {profiles.data[0].get('username', 'NO_USERNAME')}")
        except Exception as e:
            print(f"❌ user_profiles table error: {e}")
            
        # Try to query auth.users directly using SQL
        try:
            # Check if we can access auth.users through RPC
            result = self.supabase.rpc('get_auth_users').execute()
            print(f"✅ Auth users accessible via RPC: {len(result.data)} records")
        except:
            print("❌ Cannot access auth.users directly")
            
    async def check_foreign_key_constraints(self):
        """Check the current foreign key constraints"""
        print("\n🔍 DIAGNOSING FOREIGN KEY CONSTRAINTS")
        
        # Try to create test data to see exact error
        test_user_id = "ea5d3da8-41d2-4c73-842a-094224cf06c1"  # From logs
        
        # Test pillar creation
        try:
            pillar_data = {
                "user_id": test_user_id,
                "name": "Diagnostic Test Pillar",
                "description": "Testing foreign key constraints"
            }
            
            result = self.supabase.table('pillars').insert(pillar_data).execute()
            print(f"✅ Pillar creation successful: {result.data}")
            
            # Clean up test data
            if result.data:
                self.supabase.table('pillars').delete().eq('id', result.data[0]['id']).execute()
                print("✅ Test pillar cleaned up")
                
        except Exception as e:
            print(f"❌ Pillar creation failed: {e}")
            
            # Check if user exists in the target table
            try:
                # Check in legacy users table
                legacy_user = self.supabase.table('users').select('*').eq('id', test_user_id).execute()
                if legacy_user.data:
                    print(f"✅ User EXISTS in legacy 'users' table: {legacy_user.data[0].get('email', 'NO_EMAIL')}")
                else:
                    print("❌ User NOT FOUND in legacy 'users' table")
                    
                # Check in user_profiles table  
                profile_user = self.supabase.table('user_profiles').select('*').eq('id', test_user_id).execute()
                if profile_user.data:
                    print(f"✅ User EXISTS in 'user_profiles' table: {profile_user.data[0].get('username', 'NO_USERNAME')}")
                else:
                    print("❌ User NOT FOUND in 'user_profiles' table")
                    
            except Exception as check_error:
                print(f"❌ Error checking user existence: {check_error}")
                
    async def fix_foreign_key_constraints(self):
        """Attempt to fix foreign key constraints"""
        print("\n🔧 ATTEMPTING TO FIX FOREIGN KEY CONSTRAINTS")
        
        # The issue is likely that the constraints point to auth.users
        # but we're using a legacy users table
        # We need to either:
        # 1. Change constraints to point to legacy users table, OR
        # 2. Migrate users to auth.users properly
        
        # Let's try option 1 first - change constraints to point to legacy users
        try:
            # This would require SQL commands to alter constraints
            # But Supabase client doesn't support DDL commands directly
            print("⚠️ Cannot modify constraints through Supabase client")
            print("💡 SOLUTION NEEDED:")
            print("   1. Either modify foreign key constraints to reference 'users' table instead of 'auth.users'")
            print("   2. OR migrate user data from legacy 'users' table to 'auth.users' table")
            print("   3. OR create proper user_profiles entries for auth.users")
            
        except Exception as e:
            print(f"❌ Constraint fix attempt failed: {e}")
            
    async def suggest_solution(self):
        """Suggest the proper solution approach"""
        print("\n💡 RECOMMENDED SOLUTION")
        print("="*50)
        print("Based on the diagnosis, the issue is:")
        print("1. Schema expects foreign keys to reference 'auth.users(id)'")
        print("2. But the app is using a legacy 'users' table")
        print("3. Foreign key constraints are failing because of this mismatch")
        print()
        print("RECOMMENDED FIX:")
        print("Create a sync script that:")
        print("A. Takes users from legacy 'users' table")
        print("B. Creates corresponding entries in 'user_profiles' table")
        print("C. Ensures the user_profiles.id matches the user UUID")
        print("D. Updates foreign key constraints if needed")
        
async def main():
    """Run database diagnostics"""
    diagnostics = DatabaseDiagnostics()
    
    try:
        await diagnostics.initialize()
        await diagnostics.check_user_tables()
        await diagnostics.check_foreign_key_constraints()
        await diagnostics.fix_foreign_key_constraints()
        await diagnostics.suggest_solution()
        
    except Exception as e:
        print(f"❌ Diagnostics failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())