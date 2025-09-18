"""
Debug Update Operations
Test update operations to identify exact issues
"""

import os
import logging
from supabase import create_client, Client
from dotenv import load_dotenv
from pathlib import Path
import uuid
from datetime import datetime

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize Supabase client
supabase_url = os.environ.get('SUPABASE_URL')
supabase_service_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
supabase: Client = create_client(supabase_url, supabase_service_key)

def test_update_operations():
    """Test update operations for each entity type"""
    
    print("🔧 TESTING UPDATE OPERATIONS...")
    
    # Test user ID (known to work from previous tests)
    test_user_id = "2d9fb107-0f47-42f9-b29b-605e96850599"  # nav.test@aurumlife.com
    
    # Create test entities first
    test_pillar_id = str(uuid.uuid4())
    test_area_id = str(uuid.uuid4())
    test_project_id = str(uuid.uuid4())
    test_task_id = str(uuid.uuid4())
    
    try:
        print("\n📋 Creating test entities for update testing...")
        
        # Create pillar
        pillar_data = {
            'id': test_pillar_id,
            'user_id': test_user_id,
            'name': 'Update Test Pillar',
            'description': 'Original description',
            'color': '#3B82F6',
            'icon': 'Target',
            'time_allocation_percentage': 25,
            'archived': False,
            'sort_order': 0,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'date_created': datetime.utcnow().isoformat()
        }
        
        pillar_result = supabase.table('pillars').insert(pillar_data).execute()
        if not pillar_result.data:
            raise Exception("Failed to create test pillar")
        print("   ✅ Test pillar created")
        
        # Create area
        area_data = {
            'id': test_area_id,
            'user_id': test_user_id,
            'pillar_id': test_pillar_id,
            'name': 'Update Test Area',
            'description': 'Original description',
            'color': '#10B981',
            'icon': 'Circle',
            'importance': 3,
            'archived': False,
            'sort_order': 0,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'date_created': datetime.utcnow().isoformat()
        }
        
        area_result = supabase.table('areas').insert(area_data).execute()
        if not area_result.data:
            raise Exception("Failed to create test area")
        print("   ✅ Test area created")
        
        # Create project
        project_data = {
            'id': test_project_id,
            'user_id': test_user_id,
            'area_id': test_area_id,
            'name': 'Update Test Project',
            'description': 'Original description',
            'status': 'Not Started',
            'priority': 'medium',
            'color': '#F59E0B',
            'icon': 'FolderOpen',
            'importance': 3,
            'archived': False,
            'sort_order': 0,
            'completion_percentage': 0.0,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'date_created': datetime.utcnow().isoformat()
        }
        
        project_result = supabase.table('projects').insert(project_data).execute()
        if not project_result.data:
            raise Exception("Failed to create test project")
        print("   ✅ Test project created")
        
        # Create task
        task_data = {
            'id': test_task_id,
            'user_id': test_user_id,
            'project_id': test_project_id,
            'name': 'Update Test Task',
            'description': 'Original description',
            'status': 'todo',
            'priority': 'Medium',
            'kanban_column': 'todo',
            'completed': False,
            'sort_order': 0,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat(),
            'date_created': datetime.utcnow().isoformat()
        }
        
        task_result = supabase.table('tasks').insert(task_data).execute()
        if not task_result.data:
            raise Exception("Failed to create test task")
        print("   ✅ Test task created")
        
        print("\n🔄 Testing UPDATE operations...")
        
        # Test pillar update
        try:
            pillar_update = {
                'name': 'Updated Pillar Name',
                'description': 'Updated description',
                'time_allocation_percentage': 30,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            pillar_update_result = supabase.table('pillars').update(pillar_update).eq('id', test_pillar_id).eq('user_id', test_user_id).execute()
            
            if pillar_update_result.data:
                print("   ✅ Pillar update successful")
            else:
                print("   ❌ Pillar update failed - no data returned")
                
        except Exception as e:
            print(f"   ❌ Pillar update failed: {e}")
        
        # Test area update
        try:
            area_update = {
                'name': 'Updated Area Name',
                'description': 'Updated description',
                'importance': 5,  # Change importance
                'updated_at': datetime.utcnow().isoformat()
            }
            
            area_update_result = supabase.table('areas').update(area_update).eq('id', test_area_id).eq('user_id', test_user_id).execute()
            
            if area_update_result.data:
                print("   ✅ Area update successful")
            else:
                print("   ❌ Area update failed - no data returned")
                
        except Exception as e:
            print(f"   ❌ Area update failed: {e}")
        
        # Test project update
        try:
            project_update = {
                'name': 'Updated Project Name',
                'description': 'Updated description',
                'status': 'In Progress',  # Change status
                'completion_percentage': 25.0,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            project_update_result = supabase.table('projects').update(project_update).eq('id', test_project_id).eq('user_id', test_user_id).execute()
            
            if project_update_result.data:
                print("   ✅ Project update successful")
            else:
                print("   ❌ Project update failed - no data returned")
                
        except Exception as e:
            print(f"   ❌ Project update failed: {e}")
        
        # Test task update
        try:
            task_update = {
                'name': 'Updated Task Name',
                'description': 'Updated description',
                'status': 'in_progress',  # Change status
                'completed': True,
                'completed_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            task_update_result = supabase.table('tasks').update(task_update).eq('id', test_task_id).eq('user_id', test_user_id).execute()
            
            if task_update_result.data:
                print("   ✅ Task update successful")
            else:
                print("   ❌ Task update failed - no data returned")
                
        except Exception as e:
            print(f"   ❌ Task update failed: {e}")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
    
    finally:
        # Clean up test data
        print("\n🧹 Cleaning up test data...")
        try:
            supabase.table('tasks').delete().eq('id', test_task_id).execute()
            supabase.table('projects').delete().eq('id', test_project_id).execute()
            supabase.table('areas').delete().eq('id', test_area_id).execute()
            supabase.table('pillars').delete().eq('id', test_pillar_id).execute()
            print("✅ Test data cleaned up")
        except Exception as cleanup_error:
            print(f"⚠️ Cleanup error: {cleanup_error}")

if __name__ == "__main__":
    test_update_operations()
    print("\n📊 UPDATE OPERATIONS DEBUG COMPLETED")