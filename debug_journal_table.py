#!/usr/bin/env python3
"""
Debug script to check journal_entries table structure in Supabase
"""

import asyncio
from backend.supabase_client import supabase_manager

async def debug_journal_table():
    """Check what columns exist in journal_entries table"""
    try:
        # Try to get one journal entry to see the structure
        client = supabase_manager.get_client()
        
        # Get table info
        result = client.table('journal_entries').select('*').limit(1).execute()
        
        print("=== JOURNAL_ENTRIES TABLE DEBUG ===")
        print(f"Number of entries found: {len(result.data)}")
        
        if result.data:
            print("\nFirst entry structure:")
            entry = result.data[0]
            for key, value in entry.items():
                print(f"  {key}: {type(value).__name__} = {value}")
        else:
            print("No entries found in table")
            
        # Try to get table schema info
        print("\n=== ATTEMPTING TO GET SCHEMA INFO ===")
        try:
            # This might not work but let's try
            schema_result = client.rpc('get_table_columns', {'table_name': 'journal_entries'}).execute()
            print(f"Schema result: {schema_result.data}")
        except Exception as e:
            print(f"Schema query failed (expected): {e}")
            
    except Exception as e:
        print(f"Error debugging table: {e}")

if __name__ == "__main__":
    asyncio.run(debug_journal_table())