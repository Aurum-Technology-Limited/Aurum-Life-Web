#!/usr/bin/env python3
"""
SUPABASE JOURNAL TABLE SCHEMA VERIFICATION AND COLUMN ADDITION
This script checks the journal_entries table schema and adds missing columns if needed.
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')

def main():
    """Main execution"""
    print("🔍 SUPABASE JOURNAL TABLE SCHEMA VERIFICATION")
    print("="*60)
    
    try:
        # Initialize Supabase client
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not url or not key:
            print("❌ Supabase credentials not found in environment")
            return False
        
        client = create_client(url, key)
        print("✅ Supabase client initialized")
        
        # Try to get a sample record to understand the current schema
        print("\n📋 Checking current table schema...")
        result = client.table('journal_entries').select('*').limit(1).execute()
        
        if result.data:
            sample_record = result.data[0]
            print(f"✅ Found sample record with {len(sample_record.keys())} columns")
            print("📝 Current columns:")
            for key in sorted(sample_record.keys()):
                value = sample_record[key]
                value_type = type(value).__name__
                print(f"   - {key}: {value_type}")
            
            # Check for soft delete columns
            has_deleted = 'deleted' in sample_record
            has_deleted_at = 'deleted_at' in sample_record
            
            print(f"\n🗑️ Soft Delete Columns Status:")
            print(f"   - deleted: {'✅ EXISTS' if has_deleted else '❌ MISSING'}")
            print(f"   - deleted_at: {'✅ EXISTS' if has_deleted_at else '❌ MISSING'}")
            
            if has_deleted and has_deleted_at:
                print("\n🎉 All required columns exist!")
                
                # Check if there are any soft-deleted entries
                deleted_result = client.table('journal_entries').select('*').eq('deleted', True).limit(5).execute()
                print(f"📊 Found {len(deleted_result.data)} soft-deleted entries")
                
                if deleted_result.data:
                    print("🗂️ Sample soft-deleted entry:")
                    sample_deleted = deleted_result.data[0]
                    print(f"   - ID: {sample_deleted.get('id')}")
                    print(f"   - Title: {sample_deleted.get('title', 'N/A')}")
                    print(f"   - Deleted: {sample_deleted.get('deleted')}")
                    print(f"   - Deleted At: {sample_deleted.get('deleted_at')}")
                
                return True
            else:
                print("\n⚠️ Missing soft delete columns!")
                print("📝 Required SQL to add missing columns:")
                if not has_deleted:
                    print("   ALTER TABLE journal_entries ADD COLUMN deleted BOOLEAN DEFAULT FALSE;")
                if not has_deleted_at:
                    print("   ALTER TABLE journal_entries ADD COLUMN deleted_at TIMESTAMPTZ;")
                
                print("\n📊 Required indexes to create:")
                print("   CREATE INDEX IF NOT EXISTS idx_journal_user_deleted_created ON journal_entries(user_id, deleted, created_at DESC);")
                print("   CREATE INDEX IF NOT EXISTS idx_journal_deleted ON journal_entries(deleted);")
                
                return False
        else:
            print("⚠️ No records found in journal_entries table")
            print("📝 Table might be empty, but we can still check if columns exist")
            
            # Try to query with deleted column to see if it exists
            try:
                test_result = client.table('journal_entries').select('deleted, deleted_at').limit(1).execute()
                print("✅ Soft delete columns exist (table is just empty)")
                return True
            except Exception as e:
                print(f"❌ Soft delete columns missing: {e}")
                print("\n📝 Required SQL to add missing columns:")
                print("   ALTER TABLE journal_entries ADD COLUMN deleted BOOLEAN DEFAULT FALSE;")
                print("   ALTER TABLE journal_entries ADD COLUMN deleted_at TIMESTAMPTZ;")
                print("\n📊 Required indexes to create:")
                print("   CREATE INDEX IF NOT EXISTS idx_journal_user_deleted_created ON journal_entries(user_id, deleted, created_at DESC);")
                print("   CREATE INDEX IF NOT EXISTS idx_journal_deleted ON journal_entries(deleted);")
                return False
        
    except Exception as e:
        print(f"❌ Error checking table schema: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)