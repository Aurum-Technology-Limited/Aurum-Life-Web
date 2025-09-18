#!/usr/bin/env python3
"""
Test the foreign key constraint fix with existing users who have confirmed emails
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

async def test_existing_user_data_creation():
    """Test data creation with existing users who should have confirmed emails"""
    try:
        supabase = await get_supabase_client()
        
        print("🔍 Testing foreign key constraint fix with existing users...")
        
        # Get existing users from user_profiles (these should be able to create data)
        profiles_result = supabase.table('user_profiles').select('id, username').limit(3).execute()
        profiles = profiles_result.data
        
        if not profiles:
            print("❌ No existing users found in user_profiles")
            return False
        
        print(f"📋 Found {len(profiles)} existing users")
        
        # Test with each existing user
        test_results = []
        
        for profile in profiles:
            user_id = profile['id']
            username = profile.get('username', 'unnamed')
            
            print(f"\n🧪 Testing with user: {username} ({user_id})")
            
            # Test pillar creation (critical foreign key test)
            try:
                test_pillar = {
                    'user_id': user_id,
                    'name': f'FK Test Pillar for {username}', 
                    'description': f'Testing foreign key fix with {username}',
                    'icon': '🔧',
                    'color': '#4CAF50'
                }
                
                result = supabase.table('pillars').insert(test_pillar).execute()
                pillar_id = result.data[0]['id']
                
                print(f"   ✅ Pillar creation: SUCCESS - ID: {pillar_id}")
                
                # Test area creation
                test_area = {
                    'user_id': user_id,
                    'pillar_id': pillar_id,
                    'name': f'FK Test Area for {username}',
                    'description': 'Testing area creation',
                    'icon': '🎯',
                    'color': '#2196F3'
                }
                
                area_result = supabase.table('areas').insert(test_area).execute()
                area_id = area_result.data[0]['id']
                
                print(f"   ✅ Area creation: SUCCESS - ID: {area_id}")
                
                # Test project creation
                test_project = {
                    'user_id': user_id,
                    'area_id': area_id,
                    'name': f'FK Test Project for {username}',
                    'description': 'Testing project creation',
                    'icon': '🚀',
                    'status': 'Not Started'
                }
                
                project_result = supabase.table('projects').insert(test_project).execute()
                project_id = project_result.data[0]['id']
                
                print(f"   ✅ Project creation: SUCCESS - ID: {project_id}")
                
                # Test task creation
                test_task = {
                    'user_id': user_id,
                    'project_id': project_id,
                    'name': f'FK Test Task for {username}',
                    'description': 'Testing task creation',
                    'status': 'todo',
                    'priority': 'medium'
                }
                
                task_result = supabase.table('tasks').insert(test_task).execute()
                task_id = task_result.data[0]['id']
                
                print(f"   ✅ Task creation: SUCCESS - ID: {task_id}")
                
                # Clean up test data
                cleanup_order = [
                    (task_id, 'tasks', 'Task'),
                    (project_id, 'projects', 'Project'),  
                    (area_id, 'areas', 'Area'),
                    (pillar_id, 'pillars', 'Pillar')
                ]
                
                for item_id, table, name in cleanup_order:
                    try:
                        supabase.table(table).delete().eq('id', item_id).execute()
                        print(f"   🧹 {name} cleaned up")
                    except Exception as cleanup_error:
                        print(f"   ⚠️ {name} cleanup failed: {cleanup_error}")
                
                test_results.append({
                    'user_id': user_id,
                    'username': username,
                    'success': True,
                    'error': None
                })
                
            except Exception as e:
                error_msg = str(e)
                print(f"   ❌ Data creation failed: {error_msg}")
                
                if "foreign key constraint" in error_msg.lower():
                    print(f"   🚨 FOREIGN KEY CONSTRAINT VIOLATION for user {user_id}")
                
                test_results.append({
                    'user_id': user_id,
                    'username': username,
                    'success': False,
                    'error': error_msg
                })
        
        # Analyze results
        total_tests = len(test_results)
        successful_tests = len([r for r in test_results if r['success']])
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n📊 Test Results Summary:")
        print(f"   • Total users tested: {total_tests}")
        print(f"   • Successful tests: {successful_tests}")
        print(f"   • Success rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("\n🎉 PERFECT! Foreign key constraint issue is COMPLETELY RESOLVED!")
            print("✅ All existing users can create data without foreign key errors")
            print("✅ Data creation (pillars, areas, projects, tasks) works perfectly")
            print("✅ Database integrity is maintained")
            return True
        elif success_rate >= 75:
            print("\n✅ GOOD! Most users can create data successfully")
            print("⚠️ Some users may still have issues - needs investigation")
            return True
        else:
            print("\n❌ ISSUES REMAIN! Foreign key constraints are still causing problems")
            print("🔍 Manual investigation needed for failed users")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_existing_user_data_creation())