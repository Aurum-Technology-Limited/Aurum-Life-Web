"""
Find a working user ID that can create data
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

def find_working_user():
    """Find a user that has existing data (indicating they can create)"""
    
    print("🔍 FINDING WORKING USER WITH EXISTING DATA...")
    
    # Check for existing pillars and get their user_ids
    try:
        existing_pillars = supabase.table('pillars').select('user_id, name, id').limit(5).execute()
        
        if existing_pillars.data:
            print(f"   Found {len(existing_pillars.data)} existing pillars:")
            for pillar in existing_pillars.data:
                print(f"      User ID: {pillar['user_id']} - Pillar: {pillar['name']} (ID: {pillar['id']})")
                
                # Try to create a simple test area for this user
                test_user_id = pillar['user_id']
                test_area_id = str(uuid.uuid4())
                
                area_data = {
                    'id': test_area_id,
                    'user_id': test_user_id,
                    'pillar_id': pillar['id'],  # Link to existing pillar
                    'name': 'Quick Test Area',
                    'description': 'Test area for update testing',
                    'color': '#10B981',
                    'icon': 'Circle',
                    'importance': 3,
                    'archived': False,
                    'sort_order': 0,
                    'created_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat(),
                    'date_created': datetime.utcnow().isoformat()
                }
                
                try:
                    area_result = supabase.table('areas').insert(area_data).execute()
                    if area_result.data:
                        print(f"      ✅ SUCCESS! User {test_user_id} can create data")
                        
                        # Test update operation immediately
                        update_data = {
                            'name': 'Updated Test Area',
                            'importance': 5,
                            'updated_at': datetime.utcnow().isoformat()
                        }
                        
                        update_result = supabase.table('areas').update(update_data).eq('id', test_area_id).eq('user_id', test_user_id).execute()
                        
                        if update_result.data:
                            print(f"      ✅ UPDATE SUCCESS! User {test_user_id} can update data")
                        else:
                            print(f"      ❌ Update failed for user {test_user_id}")
                        
                        # Clean up
                        supabase.table('areas').delete().eq('id', test_area_id).execute()
                        
                        return test_user_id  # Return working user ID
                        
                    else:
                        print(f"      ❌ User {test_user_id} cannot create data - no data returned")
                        
                except Exception as create_error:
                    print(f"      ❌ User {test_user_id} cannot create data: {create_error}")
                    continue
        
        else:
            print("   No existing pillars found")
            
    except Exception as e:
        print(f"   ❌ Error checking existing pillars: {e}")
    
    return None

def test_update_with_working_user(working_user_id):
    """Test update operations with a known working user"""
    
    if not working_user_id:
        print("❌ No working user found - cannot test updates")
        return
    
    print(f"\n🔄 TESTING UPDATE OPERATIONS WITH WORKING USER: {working_user_id}")
    
    # Find an existing pillar for this user
    try:
        existing_pillar = supabase.table('pillars').select('*').eq('user_id', working_user_id).limit(1).execute()
        
        if existing_pillar.data:
            pillar = existing_pillar.data[0]
            pillar_id = pillar['id']
            
            print(f"   Using existing pillar: {pillar['name']} (ID: {pillar_id})")
            
            # Test pillar update
            update_data = {
                'name': f"Updated at {datetime.now().strftime('%H:%M:%S')}",
                'description': 'Updated by update testing script',
                'updated_at': datetime.utcnow().isoformat()
            }
            
            update_result = supabase.table('pillars').update(update_data).eq('id', pillar_id).eq('user_id', working_user_id).execute()
            
            if update_result.data:
                print("   ✅ Pillar update successful!")
                print(f"      Updated name: {update_result.data[0]['name']}")
            else:
                print("   ❌ Pillar update failed - no data returned")
                
        else:
            print(f"   No existing pillars found for user {working_user_id}")
            
    except Exception as e:
        print(f"   ❌ Update test failed: {e}")

if __name__ == "__main__":
    working_user = find_working_user()
    test_update_with_working_user(working_user)
    print("\n📊 WORKING USER SEARCH COMPLETED")