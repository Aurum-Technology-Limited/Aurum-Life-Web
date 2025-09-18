#!/usr/bin/env python3
"""
Quick fix for user_stats table
"""

import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

def fix_user_stats():
    """Fix user_stats table by adding updated_at"""
    try:
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        supabase = create_client(url, key)
        
        # Try to query user_stats to see current structure
        result = supabase.table('user_stats').select('*').limit(1).execute()
        
        if result.data:
            print("✅ user_stats table exists")
            sample_record = result.data[0]
            if 'updated_at' in sample_record:
                print("✅ updated_at column already exists")
            else:
                print("❌ updated_at column missing")
                print("📋 Please execute fix_user_stats_table.sql in Supabase SQL Editor")
        else:
            print("✅ user_stats table exists (no data yet)")
            
        return True
        
    except Exception as e:
        error_str = str(e)
        if "updated_at" in error_str:
            print("❌ user_stats missing updated_at column")
            print("📋 Please execute fix_user_stats_table.sql in Supabase SQL Editor")
        else:
            print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    fix_user_stats()