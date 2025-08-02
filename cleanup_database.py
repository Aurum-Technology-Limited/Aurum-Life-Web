#!/usr/bin/env python3
"""
Database Cleanup Script
Removes all accounts and data except for marc.alleyne@aurumtechnologyltd.com
"""

import os
import sys
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

# Initialize Supabase client
supabase_url = os.environ.get('SUPABASE_URL')
supabase_service_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

if not supabase_url or not supabase_service_key:
    print('❌ Missing Supabase configuration')
    sys.exit(1)

supabase = create_client(supabase_url, supabase_service_key)

# Target user to preserve
TARGET_EMAIL = 'marc.alleyne@aurumtechnologyltd.com'
TARGET_USER_ID = None

def get_target_user():
    """Find and validate the target user"""
    global TARGET_USER_ID
    try:
        response = supabase.table('users').select('*').eq('email', TARGET_EMAIL).execute()
        if response.data:
            TARGET_USER_ID = response.data[0]['id']
            print(f'✅ Found target user: {TARGET_EMAIL} (ID: {TARGET_USER_ID})')
            return True
        else:
            print(f'❌ Target user {TARGET_EMAIL} not found!')
            return False
    except Exception as e:
        print(f'❌ Error finding target user: {e}')
        return False

def get_data_counts():
    """Get current data counts"""
    try:
        users = len(supabase.table('users').select('id').execute().data or [])
        pillars = len(supabase.table('pillars').select('id').execute().data or [])
        areas = len(supabase.table('areas').select('id').execute().data or [])
        projects = len(supabase.table('projects').select('id').execute().data or [])
        tasks = len(supabase.table('tasks').select('id').execute().data or [])
        
        # Check for other tables that might have user data
        daily_reflections = 0
        try:
            daily_reflections = len(supabase.table('daily_reflections').select('id').execute().data or [])
        except:
            pass
            
        return {
            'users': users,
            'pillars': pillars,
            'areas': areas,
            'projects': projects,
            'tasks': tasks,
            'daily_reflections': daily_reflections
        }
    except Exception as e:
        print(f'❌ Error getting data counts: {e}')
        return {}

def delete_user_data(user_ids_to_delete):
    """Delete all data for specified users"""
    try:
        print(f"🗑️  Deleting data for {len(user_ids_to_delete)} users...")
        
        # Delete in reverse dependency order
        
        # 1. Delete daily reflections
        try:
            response = supabase.table('daily_reflections').delete().in_('user_id', user_ids_to_delete).execute()
            print(f"   Deleted {len(response.data or [])} daily reflections")
        except Exception as e:
            print(f"   Warning: Could not delete daily reflections: {e}")
        
        # 2. Delete tasks
        response = supabase.table('tasks').delete().in_('user_id', user_ids_to_delete).execute()
        print(f"   Deleted {len(response.data or [])} tasks")
        
        # 3. Delete projects
        response = supabase.table('projects').delete().in_('user_id', user_ids_to_delete).execute()
        print(f"   Deleted {len(response.data or [])} projects")
        
        # 4. Delete areas
        response = supabase.table('areas').delete().in_('user_id', user_ids_to_delete).execute()
        print(f"   Deleted {len(response.data or [])} areas")
        
        # 5. Delete pillars
        response = supabase.table('pillars').delete().in_('user_id', user_ids_to_delete).execute()
        print(f"   Deleted {len(response.data or [])} pillars")
        
        # 6. Delete users
        response = supabase.table('users').delete().in_('id', user_ids_to_delete).execute()
        print(f"   Deleted {len(response.data or [])} users")
        
        return True
        
    except Exception as e:
        print(f'❌ Error deleting user data: {e}')
        return False

def cleanup_supabase_auth():
    """Clean up Supabase Auth users (excluding target)"""
    try:
        print("🔐 Checking Supabase Auth users...")
        
        # Note: We cannot directly delete auth users via the client library
        # This would require admin API access or manual cleanup
        print("   Warning: Supabase Auth users need to be cleaned up manually")
        print("   Target email to preserve: marc.alleyne@aurumtechnologyltd.com")
        
    except Exception as e:
        print(f"❌ Error with auth cleanup: {e}")

def main():
    """Main cleanup process"""
    print("🧹 Starting Database Cleanup")
    print("="*50)
    
    # Step 1: Find target user
    if not get_target_user():
        return False
    
    # Step 2: Get current counts
    print("\n📊 Current Data Counts:")
    before_counts = get_data_counts()
    for table, count in before_counts.items():
        print(f"   {table}: {count}")
    
    # Step 3: Get all user IDs except target
    try:
        all_users_response = supabase.table('users').select('id, email').execute()
        all_users = all_users_response.data or []
        
        users_to_delete = []
        users_to_keep = []
        
        for user in all_users:
            if user['id'] == TARGET_USER_ID:
                users_to_keep.append(user['email'])
            else:
                users_to_delete.append(user['id'])
        
        print(f"\n🎯 Users to keep: {len(users_to_keep)}")
        for email in users_to_keep:
            print(f"   ✅ {email}")
        
        print(f"\n🗑️  Users to delete: {len(users_to_delete)}")
        print(f"   Will delete {len(users_to_delete)} users and all their associated data")
        
    except Exception as e:
        print(f'❌ Error getting user lists: {e}')
        return False
    
    # Step 4: Confirm deletion
    print(f"\n⚠️  WARNING: This will permanently delete {len(users_to_delete)} users and all their data!")
    print(f"   Only keeping: {TARGET_EMAIL}")
    
    confirm = input("\n🤔 Are you sure you want to proceed? Type 'YES' to confirm: ")
    if confirm.upper() != 'YES':
        print("❌ Operation cancelled.")
        return False
    
    # Step 5: Perform deletion
    print(f"\n🗑️  Starting deletion process...")
    if delete_user_data(users_to_delete):
        print("✅ Data deletion completed successfully!")
    else:
        print("❌ Data deletion failed!")
        return False
    
    # Step 6: Auth cleanup warning
    cleanup_supabase_auth()
    
    # Step 7: Final counts
    print("\n📊 Final Data Counts:")
    after_counts = get_data_counts()
    for table, count in after_counts.items():
        before = before_counts.get(table, 0)
        print(f"   {table}: {before} → {count} (deleted: {before - count})")
    
    print(f"\n🎉 Cleanup completed!")
    print(f"✅ Preserved user: {TARGET_EMAIL}")
    print(f"🗑️  Deleted {len(users_to_delete)} other users and their data")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)