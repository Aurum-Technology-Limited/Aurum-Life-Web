#!/usr/bin/env python3
"""
Find the actual constraint names by analyzing the error messages
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')
sys.path.append('/app/backend')

from supabase_client import get_supabase_client
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def find_constraint_names():
    """Find actual constraint names by triggering the errors"""
    try:
        supabase = await get_supabase_client()
        
        print("🔍 Finding actual constraint names...")
        
        # Use a non-existent user ID to trigger foreign key errors
        fake_user_id = "00000000-0000-0000-0000-000000000000"
        
        tables_to_test = [
            ('pillars', {'user_id': fake_user_id, 'name': 'test'}),
            ('areas', {'user_id': fake_user_id, 'name': 'test'}), 
            ('projects', {'user_id': fake_user_id, 'area_id': fake_user_id, 'name': 'test'}),
            ('tasks', {'user_id': fake_user_id, 'project_id': fake_user_id, 'name': 'test'}),
            ('journal_entries', {'user_id': fake_user_id, 'title': 'test', 'content': 'test'}),
            ('resources', {'user_id': fake_user_id, 'filename': 'test', 'original_filename': 'test', 'file_type': 'document', 'mime_type': 'text/plain', 'file_size': 100}),
            ('user_stats', {'user_id': fake_user_id}),
            ('project_templates', {'user_id': fake_user_id, 'name': 'test'}),
        ]
        
        constraint_info = {}
        
        for table_name, test_data in tables_to_test:
            try:
                print(f"\n🧪 Testing {table_name} table...")
                result = supabase.table(table_name).insert(test_data).execute()
                print(f"   ⚠️ {table_name}: Insert succeeded (no foreign key constraint)")
                
            except Exception as e:
                error_msg = str(e)
                print(f"   📋 {table_name} error: {error_msg}")
                
                # Extract constraint name from error message
                if 'violates foreign key constraint' in error_msg:
                    # Look for pattern: constraint "constraint_name"
                    import re
                    constraint_match = re.search(r'constraint "([^"]+)"', error_msg)
                    if constraint_match:
                        constraint_name = constraint_match.group(1)
                        constraint_info[table_name] = constraint_name
                        print(f"   🎯 Found constraint: {constraint_name}")
                        
                        # Check what table it references
                        if 'not present in table "users"' in error_msg:
                            print(f"   ❌ {constraint_name} references legacy 'users' table")
                        elif 'not present in table "auth"' in error_msg:
                            print(f"   ✅ {constraint_name} references correct 'auth.users' table")
        
        print(f"\n📊 Summary of constraints found:")
        for table, constraint in constraint_info.items():
            print(f"   {table}: {constraint}")
        
        print(f"\n📝 Generating targeted SQL fixes...")
        
        # Generate specific DROP and ADD statements
        sql_fixes = []
        
        for table, constraint in constraint_info.items():
            # Drop existing constraint
            sql_fixes.append(f"ALTER TABLE public.{table} DROP CONSTRAINT IF EXISTS {constraint};")
            
            # Add correct constraint
            sql_fixes.append(f"ALTER TABLE public.{table} ADD CONSTRAINT {constraint} FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;")
        
        # Write the targeted SQL file
        with open('/app/targeted_foreign_key_fix.sql', 'w') as f:
            f.write("-- Targeted Foreign Key Constraint Fixes\n")
            f.write("-- Generated based on actual constraint names found in database\n\n")
            for sql in sql_fixes:
                f.write(sql + "\n")
        
        print(f"✅ Generated targeted SQL fixes in /app/targeted_foreign_key_fix.sql")
        
        return constraint_info
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return {}

if __name__ == "__main__":
    asyncio.run(find_constraint_names())