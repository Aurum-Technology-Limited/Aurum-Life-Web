#!/usr/bin/env python3
"""
Check if users table exists in Supabase
"""

import os
from supabase import create_client

# Load environment
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

def check_users_table():
    """Check if users table exists"""
    try:
        # Initialize Supabase client
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not url or not key:
            print("❌ Supabase credentials not found")
            return False
        
        supabase = create_client(url, key)
        print("✅ Supabase client connected")
        
        # Try to query users table
        result = supabase.table('users').select('id').limit(1).execute()
        print("✅ Users table exists and is accessible!")
        print(f"   Found {len(result.data)} records (if any)")
        return True
        
    except Exception as e:
        error_str = str(e)
        if "relation \"public.users\" does not exist" in error_str or "does not exist" in error_str:
            print("❌ Users table does NOT exist")
            print("📋 SOLUTION: Please execute add_users_table.sql in Supabase SQL Editor")
            return False
        else:
            print(f"❌ Error accessing users table: {e}")
            return False

def check_other_tables():
    """Check if other tables exist"""
    try:
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        supabase = create_client(url, key)
        
        tables_to_check = ['user_profiles', 'pillars', 'areas', 'projects', 'tasks']
        
        print("\n🔍 Checking other tables...")
        for table in tables_to_check:
            try:
                result = supabase.table(table).select('id').limit(1).execute()
                print(f"✅ {table}: {len(result.data)} records")
            except Exception as e:
                print(f"❌ {table}: Error - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return False

if __name__ == "__main__":
    print("🔍 SUPABASE USERS TABLE STATUS CHECK")
    print("=" * 40)
    
    users_exist = check_users_table()
    check_other_tables()
    
    print("\n" + "=" * 40)
    if users_exist:
        print("🎉 READY FOR 100% MIGRATION TEST!")
        print("   → Run: python final_supabase_test.py")
    else:
        print("⚠️  USERS TABLE MISSING")
        print("   → Execute add_users_table.sql in Supabase")
        print("   → Then run final test")
    print("=" * 40)