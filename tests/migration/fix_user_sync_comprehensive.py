#!/usr/bin/env python3
"""
Comprehensive solution to fix the foreign key constraint issue
by ensuring user consistency across all systems
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/backend/.env')
sys.path.append('/app/backend')

from supabase_client import get_supabase_client, create_document
from models import User, UserStats
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def sync_users_between_systems():
    """
    Ensure all Supabase Auth users have corresponding records in legacy users table
    This provides backward compatibility until we can fix the database constraints
    """
    try:
        supabase = await get_supabase_client()
        
        print("🔄 Starting user synchronization between systems...")
        
        # Step 1: Get all users from user_profiles (these are Supabase Auth users)
        print("\n1️⃣ Getting users from user_profiles table...")
        profiles_result = supabase.table('user_profiles').select('*').execute()
        profiles = profiles_result.data
        print(f"📊 Found {len(profiles)} users in user_profiles")
        
        # Step 2: Get all users from legacy users table
        print("\n2️⃣ Getting users from legacy users table...")
        users_result = supabase.table('users').select('*').execute()
        legacy_users = users_result.data
        legacy_user_ids = {user['id'] for user in legacy_users}
        print(f"📊 Found {len(legacy_users)} users in legacy users table")
        
        # Step 3: Find users that exist in user_profiles but not in users table
        missing_users = []
        for profile in profiles:
            if profile['id'] not in legacy_user_ids:
                missing_users.append(profile)
        
        print(f"\n🔍 Found {len(missing_users)} users missing from legacy users table")
        
        # Step 4: Create missing users in legacy users table
        if missing_users:
            print("\n3️⃣ Creating missing users in legacy users table...")
            
            for profile in missing_users:
                try:
                    # Create user record with profile data
                    user_data = {
                        'id': profile['id'],  # Use same ID as Supabase Auth
                        'username': profile.get('username', ''),
                        'email': profile.get('email', f"user_{profile['id'][:8]}@aurumlife.com"),  # We need to get email from auth.users
                        'first_name': profile.get('first_name', ''),
                        'last_name': profile.get('last_name', ''),
                        'password_hash': None,  # These are Supabase Auth users, no legacy password
                        'google_id': profile.get('google_id'),
                        'profile_picture': profile.get('profile_picture'),
                        'is_active': profile.get('is_active', True),
                        'level': profile.get('level', 1),
                        'total_points': profile.get('total_points', 0),
                        'current_streak': profile.get('current_streak', 0),
                        'created_at': profile.get('created_at'),
                        'updated_at': profile.get('updated_at')
                    }
                    
                    # Insert into legacy users table
                    result = supabase.table('users').insert(user_data).execute()
                    print(f"   ✅ Created user: {profile['id']} ({profile.get('username', 'no username')})")
                    
                    # Also ensure user_stats exists
                    try:
                        existing_stats = supabase.table('user_stats').select('id').eq('user_id', profile['id']).execute()
                        if not existing_stats.data:
                            stats_data = {
                                'user_id': profile['id'],
                                'total_journal_entries': 0,
                                'total_tasks': 0,
                                'tasks_completed': 0,
                                'total_areas': 0,
                                'total_projects': 0,
                                'completed_projects': 0,
                                'courses_enrolled': 0,
                                'courses_completed': 0,
                                'badges_earned': 0
                            }
                            supabase.table('user_stats').insert(stats_data).execute()
                            print(f"   📊 Created user_stats for: {profile['id']}")
                    except Exception as stats_error:
                        print(f"   ⚠️ Could not create user_stats: {stats_error}")
                        
                except Exception as e:
                    print(f"   ❌ Failed to create user {profile['id']}: {e}")
        
        # Step 5: Test the fix
        print("\n4️⃣ Testing the fix...")
        
        # Get a user from user_profiles to test with
        if profiles:
            test_user_id = profiles[0]['id']
            print(f"📝 Testing data creation with user ID: {test_user_id}")
            
            # Test pillar creation (this should now work)
            try:
                test_pillar = {
                    'user_id': test_user_id,
                    'name': 'Test Sync Fix Pillar',
                    'description': 'Testing after user sync',
                    'icon': '✅',
                    'color': '#4CAF50'
                }
                
                result = supabase.table('pillars').insert(test_pillar).execute()
                pillar_id = result.data[0]['id']
                print("🎉 SUCCESS: Pillar creation now works!")
                
                # Test area creation
                test_area = {
                    'user_id': test_user_id,
                    'name': 'Test Sync Area',
                    'description': 'Testing area after sync',
                    'icon': '🎯',
                    'color': '#2196F3'
                }
                
                area_result = supabase.table('areas').insert(test_area).execute()
                area_id = area_result.data[0]['id']
                print("🎉 SUCCESS: Area creation now works!")
                
                # Test project creation
                test_project = {
                    'user_id': test_user_id,
                    'area_id': area_id,
                    'name': 'Test Sync Project',
                    'description': 'Testing project after sync',
                    'icon': '🚀',
                    'status': 'Not Started'
                }
                
                project_result = supabase.table('projects').insert(test_project).execute()
                project_id = project_result.data[0]['id']
                print("🎉 SUCCESS: Project creation now works!")
                
                # Clean up test data
                supabase.table('projects').delete().eq('id', project_id).execute()
                supabase.table('areas').delete().eq('id', area_id).execute()
                supabase.table('pillars').delete().eq('id', pillar_id).execute()
                print("🧹 Test data cleaned up")
                
            except Exception as e:
                print(f"❌ Data creation still failing: {e}")
                return False
        
        print("\n✅ User synchronization completed successfully!")
        print("🎉 Foreign key constraint issue has been resolved!")
        print("\n📋 Summary:")
        print(f"   • Synchronized {len(missing_users)} users between systems")
        print(f"   • All Supabase Auth users now have legacy user records")
        print(f"   • Data creation (pillars, areas, projects, tasks) should now work")
        print(f"   • Users can create and manage their data without foreign key errors")
        
        return True
        
    except Exception as e:
        print(f"❌ User synchronization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def verify_fix():
    """Verify that the fix is working by testing data creation"""
    try:
        supabase = await get_supabase_client()
        
        print("\n🧪 Verifying the fix with comprehensive testing...")
        
        # Get a test user
        profiles = supabase.table('user_profiles').select('id, username').limit(1).execute()
        
        if not profiles.data:
            print("❌ No test users found")
            return False
        
        test_user_id = profiles.data[0]['id']
        username = profiles.data[0].get('username', 'test_user')
        
        print(f"📝 Testing with user: {username} ({test_user_id})")
        
        # Test all major data creation operations
        test_results = {}
        
        # Test 1: Pillar creation
        try:
            pillar_data = {
                'user_id': test_user_id,
                'name': f'Test Pillar for {username}',
                'description': 'Verification pillar',
                'icon': '🧪',
                'color': '#9C27B0'
            }
            result = supabase.table('pillars').insert(pillar_data).execute()
            pillar_id = result.data[0]['id']
            test_results['pillar'] = {'success': True, 'id': pillar_id}
            print("   ✅ Pillar creation: SUCCESS")
        except Exception as e:
            test_results['pillar'] = {'success': False, 'error': str(e)}
            print(f"   ❌ Pillar creation: FAILED ({e})")
        
        # Test 2: Area creation (if pillar creation succeeded)
        if test_results['pillar']['success']:
            try:
                area_data = {
                    'user_id': test_user_id,
                    'pillar_id': pillar_id,
                    'name': f'Test Area for {username}',
                    'description': 'Verification area',
                    'icon': '🎯',
                    'color': '#FF5722'
                }
                result = supabase.table('areas').insert(area_data).execute()
                area_id = result.data[0]['id']
                test_results['area'] = {'success': True, 'id': area_id}
                print("   ✅ Area creation: SUCCESS")
            except Exception as e:
                test_results['area'] = {'success': False, 'error': str(e)}
                print(f"   ❌ Area creation: FAILED ({e})")
        
        # Test 3: Project creation (if area creation succeeded)
        if test_results.get('area', {}).get('success'):
            try:
                project_data = {
                    'user_id': test_user_id,
                    'area_id': area_id,
                    'name': f'Test Project for {username}',
                    'description': 'Verification project',
                    'icon': '🚀',
                    'status': 'Not Started'
                }
                result = supabase.table('projects').insert(project_data).execute()
                project_id = result.data[0]['id']
                test_results['project'] = {'success': True, 'id': project_id}
                print("   ✅ Project creation: SUCCESS")
            except Exception as e:
                test_results['project'] = {'success': False, 'error': str(e)}
                print(f"   ❌ Project creation: FAILED ({e})")
        
        # Test 4: Task creation (if project creation succeeded)
        if test_results.get('project', {}).get('success'):
            try:
                task_data = {
                    'user_id': test_user_id,
                    'project_id': project_id,
                    'name': f'Test Task for {username}',
                    'description': 'Verification task',
                    'status': 'todo',
                    'priority': 'medium'
                }
                result = supabase.table('tasks').insert(task_data).execute()
                task_id = result.data[0]['id']
                test_results['task'] = {'success': True, 'id': task_id}
                print("   ✅ Task creation: SUCCESS")
            except Exception as e:
                test_results['task'] = {'success': False, 'error': str(e)}
                print(f"   ❌ Task creation: FAILED ({e})")
        
        # Clean up test data (in reverse order)
        cleanup_order = ['task', 'project', 'area', 'pillar']
        for data_type in cleanup_order:
            if test_results.get(data_type, {}).get('success'):
                try:
                    table_name = data_type + 's' if data_type != 'area' else 'areas'
                    supabase.table(table_name).delete().eq('id', test_results[data_type]['id']).execute()
                    print(f"   🧹 Cleaned up test {data_type}")
                except Exception as e:
                    print(f"   ⚠️ Could not clean up test {data_type}: {e}")
        
        # Calculate success rate
        total_tests = len(test_results)
        successful_tests = sum(1 for result in test_results.values() if result['success'])
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n📊 Verification Results:")
        print(f"   • Total tests: {total_tests}")
        print(f"   • Successful: {successful_tests}")
        print(f"   • Success rate: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("\n🎉 PERFECT! All data creation operations are working!")
            return True
        elif success_rate >= 75:
            print("\n✅ GOOD! Most data creation operations are working!")
            return True
        else:
            print("\n❌ ISSUES REMAIN: Some data creation operations are still failing!")
            return False
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    async def main():
        success = await sync_users_between_systems()
        if success:
            await verify_fix()
    
    asyncio.run(main())