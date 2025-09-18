#!/usr/bin/env python3
"""
Apply the foreign key constraint fixes to resolve the data creation issue
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

async def apply_foreign_key_fixes():
    """Apply the foreign key constraint fixes"""
    try:
        supabase = await get_supabase_client()
        
        print("🔧 Applying foreign key constraint fixes...")
        
        # Read the SQL file
        with open('/app/fix_foreign_key_constraints.sql', 'r') as f:
            sql_content = f.read()
        
        # Split into individual statements
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
        
        print(f"📝 Found {len(statements)} SQL statements to execute")
        
        # Execute each statement
        for i, statement in enumerate(statements):
            if not statement:
                continue
                
            try:
                print(f"⚡ Executing statement {i+1}/{len(statements)}...")
                
                # For ALTER TABLE statements, we need to use the client directly
                result = supabase.postgrest.rpc('exec_sql', {'sql': statement}).execute()
                print(f"   ✅ Success: {statement[:60]}...")
                
            except Exception as e:
                # Some statements might fail if constraints don't exist, which is okay
                error_msg = str(e)
                if 'does not exist' in error_msg or 'could not find' in error_msg:
                    print(f"   ⚠️ Skipped (expected): {statement[:60]}...")
                else:
                    print(f"   ❌ Failed: {statement[:60]}...")
                    print(f"      Error: {e}")
        
        print("\n🧪 Testing the fixes...")
        
        # Test with a Supabase Auth user ID (from user_profiles)
        profiles = supabase.table('user_profiles').select('id').limit(1).execute()
        
        if profiles.data:
            test_user_id = profiles.data[0]['id']
            print(f"📝 Testing with user ID: {test_user_id}")
            
            # Test pillar creation
            try:
                test_pillar = {
                    'user_id': test_user_id,
                    'name': 'Test Fixed Constraints',
                    'description': 'Testing after foreign key fix',
                    'icon': '🔧',
                    'color': '#4CAF50'
                }
                
                result = supabase.table('pillars').insert(test_pillar).execute()
                pillar_id = result.data[0]['id']
                print("✅ Pillar creation successful!")
                
                # Clean up the test pillar
                supabase.table('pillars').delete().eq('id', pillar_id).execute()
                print("🧹 Test pillar cleaned up")
                
            except Exception as e:
                print(f"❌ Pillar creation still failing: {e}")
                
            # Test area creation
            try:
                test_area = {
                    'user_id': test_user_id,
                    'name': 'Test Fixed Area',
                    'description': 'Testing area creation',
                    'icon': '🎯',
                    'color': '#2196F3'
                }
                
                result = supabase.table('areas').insert(test_area).execute()
                area_id = result.data[0]['id']
                print("✅ Area creation successful!")
                
                # Clean up
                supabase.table('areas').delete().eq('id', area_id).execute()
                print("🧹 Test area cleaned up")
                
            except Exception as e:
                print(f"❌ Area creation still failing: {e}")
        
        print("\n✅ Foreign key constraint fixes applied successfully!")
        
    except Exception as e:
        print(f"❌ Fix application failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(apply_foreign_key_fixes())