"""
Check available test users in the database
"""

import os
import logging
from supabase import create_client, Client
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize Supabase client
supabase_url = os.environ.get('SUPABASE_URL')
supabase_service_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
supabase: Client = create_client(supabase_url, supabase_service_key)

def check_available_users():
    """Check what test users are available"""
    
    print("🔍 CHECKING AVAILABLE TEST USERS...")
    
    # Check user_profiles table
    try:
        print("\n📋 Checking user_profiles table...")
        user_profiles = supabase.table('user_profiles').select('*').execute()
        
        if user_profiles.data:
            print(f"   Found {len(user_profiles.data)} user profiles:")
            for user in user_profiles.data:
                print(f"      ID: {user['id']}")
                print(f"      Username: {user.get('username', 'N/A')}")
                print(f"      Name: {user.get('first_name', '')} {user.get('last_name', '')}")
                print(f"      Active: {user.get('is_active', 'N/A')}")
                print("      ---")
        else:
            print("   No user profiles found")
            
    except Exception as e:
        print(f"   ❌ Error checking user_profiles: {e}")
    
    # Check users table (legacy)
    try:
        print("\n📋 Checking users table (legacy)...")
        users = supabase.table('users').select('*').execute()
        
        if users.data:
            print(f"   Found {len(users.data)} users:")
            for user in users.data[:5]:  # Show first 5
                print(f"      ID: {user['id']}")
                print(f"      Email: {user.get('email', 'N/A')}")
                print(f"      Username: {user.get('username', 'N/A')}")
                print(f"      Active: {user.get('is_active', 'N/A')}")
                print("      ---")
                
            if len(users.data) > 5:
                print(f"   ... and {len(users.data) - 5} more users")
                
        else:
            print("   No users found in legacy table")
            
    except Exception as e:
        print(f"   ❌ Error checking users table: {e}")
        
    # Look for nav.test specifically
    try:
        print("\n🎯 Looking for nav.test@aurumlife.com specifically...")
        
        # Check in users table
        nav_user = supabase.table('users').select('*').ilike('email', '%nav.test%').execute()
        if nav_user.data:
            print(f"   Found in users table:")
            for user in nav_user.data:
                print(f"      ID: {user['id']}")
                print(f"      Email: {user.get('email')}")
        
        # Check in user_profiles
        nav_profile = supabase.table('user_profiles').select('*').execute()
        # Filter manually since ilike might not work on UUID
        for profile in nav_profile.data or []:
            if 'nav' in str(profile).lower() or 'test' in str(profile).lower():
                print(f"   Possible match in user_profiles:")
                print(f"      ID: {profile['id']}")
                print(f"      Username: {profile.get('username')}")
        
    except Exception as e:
        print(f"   ⚠️ Error searching for nav.test user: {e}")

def use_existing_user_for_test():
    """Use the first available user for testing"""
    
    print("\n🧪 USING FIRST AVAILABLE USER FOR CRUD TEST...")
    
    try:
        # Get first user from users table
        users = supabase.table('users').select('*').limit(1).execute()
        
        if users.data:
            test_user = users.data[0]
            test_user_id = test_user['id']
            print(f"   Using user: {test_user.get('email', 'Unknown')} (ID: {test_user_id})")
            
            # Test area creation with this user
            area_data = {
                'id': 'test-area-existing-user',
                'user_id': test_user_id,
                'name': 'Test Area with Existing User',
                'description': 'Test area for existing user',
                'color': '#10B981',
                'icon': 'Circle',
                'importance': 3,
                'archived': False,
                'sort_order': 0
            }
            
            area_result = supabase.table('areas').insert(area_data).execute()
            
            if area_result.data:
                print("   ✅ Area created successfully with existing user!")
                
                # Test project creation
                project_data = {
                    'id': 'test-project-existing-user',
                    'user_id': test_user_id,
                    'area_id': 'test-area-existing-user',
                    'name': 'Test Project with Existing User',
                    'description': 'Test project',
                    'status': 'Not Started',
                    'priority': 'medium',
                    'importance': 3,
                    'archived': False,
                    'sort_order': 0,
                    'completion_percentage': 0.0
                }
                
                project_result = supabase.table('projects').insert(project_data).execute()
                
                if project_result.data:
                    print("   ✅ Project created successfully!")
                    print(f"      Project ID: {project_result.data[0]['id']}")
                    print("   🎉 CRUD OPERATIONS ARE WORKING!")
                else:
                    print("   ❌ Project creation failed")
                    
                # Clean up
                supabase.table('projects').delete().eq('id', 'test-project-existing-user').execute()
                supabase.table('areas').delete().eq('id', 'test-area-existing-user').execute()
                print("   🧹 Test data cleaned up")
                
            else:
                print("   ❌ Area creation failed even with existing user")
                
        else:
            print("   ❌ No users found in database")
            
    except Exception as e:
        print(f"   ❌ Error using existing user: {e}")

if __name__ == "__main__":
    check_available_users()
    use_existing_user_for_test()
    print("\n📊 USER CHECK COMPLETED")