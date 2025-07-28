"""
Debug Project Creation Issues
Test project creation directly to identify exact issues
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

def test_project_creation():
    """Test project creation with minimal data"""
    
    print("🧪 TESTING PROJECT CREATION...")
    
    # Test user ID
    test_user_id = "2d9fb107-0f47-42f9-b29b-605e96850599"  # nav.test@aurumlife.com
    
    # Create a test area first
    test_area_id = str(uuid.uuid4())
    area_data = {
        'id': test_area_id,
        'user_id': test_user_id,
        'name': 'Test Area for Project Debug',
        'description': 'Debug area',
        'color': '#10B981',
        'icon': 'Circle',
        'importance': 'medium',
        'archived': False,
        'sort_order': 0,
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat(),
        'date_created': datetime.utcnow().isoformat()
    }
    
    try:
        print("   Creating test area...")
        area_result = supabase.table('areas').insert(area_data).execute()
        if area_result.data:
            print("   ✅ Test area created successfully")
            
            # Now test project creation with minimal data
            project_id = str(uuid.uuid4())
            
            # Test different project data variations
            project_variations = [
                {
                    'name': 'Minimal Project Test',
                    'description': 'Minimal test',
                    'status': 'Not Started',
                    'priority': 'medium'
                },
                {
                    'name': 'Medium Project Test', 
                    'description': 'Medium test',
                    'status': 'Not Started',
                    'priority': 'Medium'  # Capitalized
                },
                {
                    'name': 'Full Project Test',
                    'description': 'Full test', 
                    'status': 'Not Started',
                    'priority': 'medium',
                    'deadline': None  # Test with None deadline
                }
            ]
            
            for i, project_extra in enumerate(project_variations, 1):
                try:
                    test_project_id = f"test-project-{i}-{uuid.uuid4()}"
                    
                    project_data = {
                        'id': test_project_id,
                        'user_id': test_user_id,
                        'area_id': test_area_id,
                        'name': project_extra['name'],
                        'description': project_extra['description'],
                        'status': project_extra['status'],
                        'priority': project_extra['priority'],
                        'color': '#F59E0B',
                        'icon': 'FolderOpen', 
                        'archived': False,
                        'sort_order': 0,
                        'completion_percentage': 0,
                        'created_at': datetime.utcnow().isoformat(),
                        'updated_at': datetime.utcnow().isoformat(),
                        'date_created': datetime.utcnow().isoformat()
                    }
                    
                    # Add deadline if specified
                    if 'deadline' in project_extra:
                        project_data['deadline'] = project_extra['deadline']
                    
                    print(f"   Testing project variation {i}: {project_extra['name']}")
                    project_result = supabase.table('projects').insert(project_data).execute()
                    
                    if project_result.data:
                        print(f"   ✅ Project variation {i} created successfully!")
                        print(f"      ID: {project_result.data[0]['id']}")
                        print(f"      Status: {project_result.data[0]['status']}")
                        print(f"      Priority: {project_result.data[0]['priority']}")
                    else:
                        print(f"   ❌ Project variation {i} creation failed - no data returned")
                        
                except Exception as e:
                    print(f"   ❌ Project variation {i} creation failed: {e}")
                    print(f"      Data attempted: {project_data}")
            
            # Clean up test data
            print("\n🧹 Cleaning up test data...")
            try:
                # Delete test projects
                supabase.table('projects').delete().like('id', 'test-project-%').execute()
                # Delete test area
                supabase.table('areas').delete().eq('id', test_area_id).execute()
                print("✅ Test data cleaned up")
            except Exception as cleanup_error:
                print(f"⚠️ Cleanup error: {cleanup_error}")
                
        else:
            print("   ❌ Test area creation failed - cannot proceed with project tests")
            
    except Exception as e:
        print(f"   ❌ Area creation failed: {e}")

def inspect_projects_table():
    """Inspect the projects table to understand its structure"""
    
    print("\n🔍 INSPECTING PROJECTS TABLE STRUCTURE...")
    
    try:
        # Get a sample project to see the structure
        result = supabase.table('projects').select('*').limit(1).execute()
        
        if result.data:
            sample_project = result.data[0]
            columns = list(sample_project.keys())
            print(f"   Available columns: {', '.join(columns)}")
            
            # Show sample values
            print(f"   Sample project data:")
            for key, value in sample_project.items():
                print(f"      {key}: {value} ({type(value).__name__})")
                
        else:
            print("   No existing projects found - table might be empty")
            
    except Exception as e:
        print(f"   ❌ Error inspecting projects table: {e}")

if __name__ == "__main__":
    inspect_projects_table()
    test_project_creation()
    print("\n📊 PROJECT CREATION DEBUG COMPLETED")