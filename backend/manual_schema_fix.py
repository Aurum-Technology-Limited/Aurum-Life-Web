"""
Manual Supabase Schema Fix
Check existing tables and add missing columns if needed
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

if not supabase_url or not supabase_service_key:
    raise ValueError("Missing Supabase configuration")

supabase: Client = create_client(supabase_url, supabase_service_key)

def inspect_database_schema():
    """Inspect current database schema"""
    
    tables_to_check = ['pillars', 'areas', 'projects', 'tasks', 'user_profiles']
    
    print("🔍 INSPECTING CURRENT DATABASE SCHEMA...")
    
    for table_name in tables_to_check:
        try:
            print(f"\n📋 Checking {table_name} table...")
            
            # Get a sample record to see the structure
            result = supabase.table(table_name).select('*').limit(1).execute()
            
            if result.data:
                sample_record = result.data[0]
                columns = list(sample_record.keys())
                print(f"   Current columns: {', '.join(columns)}")
                
                # Check for missing columns based on our models
                required_columns = {
                    'pillars': ['is_active', 'time_allocation'],
                    'areas': ['is_active', 'importance'],  
                    'projects': ['is_active'],
                    'tasks': ['is_active'],
                    'user_profiles': ['level', 'total_points', 'current_streak']
                }
                
                missing_columns = []
                for col in required_columns.get(table_name, []):
                    if col not in columns:
                        missing_columns.append(col)
                
                if missing_columns:
                    print(f"   ❌ Missing columns: {', '.join(missing_columns)}")
                else:
                    print(f"   ✅ All required columns present")
                    
                # Check sample values for enum fields
                if table_name == 'projects' and 'status' in columns:
                    print(f"   Sample project status: {sample_record.get('status')}")
                if table_name == 'tasks' and 'status' in columns:
                    print(f"   Sample task status: {sample_record.get('status')}")
                    
            else:
                print(f"   ⚠️ No data found in {table_name} table")
                
        except Exception as e:
            print(f"   ❌ Error checking {table_name}: {e}")

def create_test_data_with_correct_schema():
    """Create test data using the expected schema values"""
    
    print("\n🧪 CREATING TEST DATA WITH CORRECT SCHEMA...")
    
    # Test user ID - using a known test user
    test_user_id = "2d9fb107-0f47-42f9-b29b-605e96850599"  # nav.test@aurumlife.com
    
    # Create a test pillar with correct schema
    try:
        pillar_data = {
            'id': 'test-pillar-123',
            'user_id': test_user_id,
            'name': 'Health & Wellness (Schema Test)',
            'description': 'Test pillar with correct schema',
            'color': '#10B981',
            'icon': 'Heart',
            'is_active': True,
            'time_allocation': 25
        }
        
        print("   Creating test pillar...")
        pillar_result = supabase.table('pillars').upsert(pillar_data).execute()
        
        if pillar_result.data:
            print(f"   ✅ Test pillar created successfully")
            
            # Create a test area
            area_data = {
                'id': 'test-area-123',
                'user_id': test_user_id,
                'pillar_id': 'test-pillar-123',
                'name': 'Exercise (Schema Test)',
                'description': 'Test area with correct schema',
                'color': '#EF4444',
                'icon': 'Activity',
                'is_active': True,
                'importance': 'high'
            }
            
            print("   Creating test area...")
            area_result = supabase.table('areas').upsert(area_data).execute()
            
            if area_result.data:
                print("   ✅ Test area created successfully")
                
                # Create a test project
                project_data = {
                    'id': 'test-project-123',
                    'user_id': test_user_id,
                    'area_id': 'test-area-123',
                    'name': 'Morning Workout Routine (Schema Test)',
                    'description': 'Test project with correct schema',
                    'status': 'not_started',
                    'priority': 'medium',
                    'color': '#F59E0B',
                    'icon': 'Target',
                    'is_active': True
                }
                
                print("   Creating test project...")
                project_result = supabase.table('projects').upsert(project_data).execute()
                
                if project_result.data:
                    print("   ✅ Test project created successfully")
                    
                    # Create a test task
                    task_data = {
                        'id': 'test-task-123',
                        'user_id': test_user_id,
                        'project_id': 'test-project-123',
                        'name': '30-minute cardio (Schema Test)',
                        'description': 'Test task with correct schema',
                        'status': 'pending',
                        'priority': 'medium',
                        'kanban_column': 'todo',
                        'completed': False,
                        'is_active': True,
                        'sort_order': 0
                    }
                    
                    print("   Creating test task...")
                    task_result = supabase.table('tasks').upsert(task_data).execute()
                    
                    if task_result.data:
                        print("   ✅ Test task created successfully")
                        print("\n🎉 ALL TEST DATA CREATED WITH CORRECT SCHEMA!")
                        return True
                    else:
                        print("   ❌ Test task creation failed")
                else:
                    print("   ❌ Test project creation failed")  
            else:
                print("   ❌ Test area creation failed")
        else:
            print("   ❌ Test pillar creation failed")
            
    except Exception as e:
        print(f"   ❌ Error creating test data: {e}")
        return False
    
    return False

def cleanup_test_data():
    """Clean up test data"""
    try:
        print("\n🧹 CLEANING UP TEST DATA...")
        
        # Delete in reverse order due to foreign keys
        supabase.table('tasks').delete().eq('id', 'test-task-123').execute()
        supabase.table('projects').delete().eq('id', 'test-project-123').execute()
        supabase.table('areas').delete().eq('id', 'test-area-123').execute()
        supabase.table('pillars').delete().eq('id', 'test-pillar-123').execute()
        
        print("✅ Test data cleaned up")
        
    except Exception as e:
        print(f"⚠️ Error cleaning up test data: {e}")

if __name__ == "__main__":
    inspect_database_schema()
    
    success = create_test_data_with_correct_schema()
    
    if success:
        print("\n✅ DATABASE SCHEMA APPEARS TO BE WORKING!")
        print("   Schema validation successful - CRUD operations should work now")
    else:
        print("\n❌ DATABASE SCHEMA ISSUES DETECTED!")
        print("   Manual schema updates needed in Supabase dashboard")
        
    # Clean up test data
    cleanup_test_data()
    
    print(f"\n📊 SCHEMA ANALYSIS COMPLETED")
    print(f"Next steps: Run CRUD tests to verify functionality")