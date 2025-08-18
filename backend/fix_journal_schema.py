#!/usr/bin/env python3
"""
Fix Journal Entries Table Schema
Add missing columns for trash functionality: deleted, deleted_at
"""

from supabase_client import supabase_manager
import asyncio

async def fix_journal_schema():
    """Add missing columns to journal_entries table"""
    try:
        supabase = supabase_manager.get_client()
        
        print("🔧 Adding missing columns to journal_entries table...")
        
        # Add deleted column (boolean, default false)
        try:
            result = supabase.rpc('exec_sql', {
                'sql': 'ALTER TABLE journal_entries ADD COLUMN IF NOT EXISTS deleted BOOLEAN DEFAULT FALSE;'
            }).execute()
            print("✅ Added 'deleted' column")
        except Exception as e:
            print(f"⚠️ Error adding 'deleted' column: {e}")
        
        # Add deleted_at column (timestamp, nullable)
        try:
            result = supabase.rpc('exec_sql', {
                'sql': 'ALTER TABLE journal_entries ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;'
            }).execute()
            print("✅ Added 'deleted_at' column")
        except Exception as e:
            print(f"⚠️ Error adding 'deleted_at' column: {e}")
        
        # Add word_count column (integer, default 0)
        try:
            result = supabase.rpc('exec_sql', {
                'sql': 'ALTER TABLE journal_entries ADD COLUMN IF NOT EXISTS word_count INTEGER DEFAULT 0;'
            }).execute()
            print("✅ Added 'word_count' column")
        except Exception as e:
            print(f"⚠️ Error adding 'word_count' column: {e}")
        
        # Add reading_time_minutes column (integer, default 1)
        try:
            result = supabase.rpc('exec_sql', {
                'sql': 'ALTER TABLE journal_entries ADD COLUMN IF NOT EXISTS reading_time_minutes INTEGER DEFAULT 1;'
            }).execute()
            print("✅ Added 'reading_time_minutes' column")
        except Exception as e:
            print(f"⚠️ Error adding 'reading_time_minutes' column: {e}")
        
        print("🎉 Journal entries table schema update completed!")
        
    except Exception as e:
        print(f"❌ Error fixing journal schema: {e}")

if __name__ == "__main__":
    asyncio.run(fix_journal_schema())