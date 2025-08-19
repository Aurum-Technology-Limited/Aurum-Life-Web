#!/usr/bin/env python3
"""
🎯 AI COACH MVP FULL TEST - Create test data and test AI Coach MVP endpoints
Creates test data (pillar, area, project, tasks) and then tests AI Coach MVP endpoints
"""

import asyncio
import sys
import os
import uuid
from datetime import datetime

# Add backend to path
sys.path.append('/app/backend')

# Load environment variables from .env file
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path('/app/backend/.env')
load_dotenv(env_path)

async def create_test_data(supabase, user_id: str):
    """Create test data for AI Coach MVP testing"""
    try:
        print("📋 Creating test data...")
        
        # Create a test pillar
        pillar_data = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'name': 'AI Coach Test Pillar',
            'description': 'Test pillar for AI Coach MVP testing',
            'color': '#3B82F6',
            'icon': 'target',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        pillar_response = supabase.table('pillars').insert(pillar_data).execute()
        pillar_id = pillar_data['id']
        print(f"✅ Created test pillar: {pillar_id}")
        
        # Create a test area
        area_data = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'name': 'AI Coach Test Area',
            'description': 'Test area for AI Coach MVP testing',
            'pillar_id': pillar_id,
            'importance': 4,
            'color': '#10B981',
            'icon': 'folder',
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        area_response = supabase.table('areas').insert(area_data).execute()
        area_id = area_data['id']
        print(f"✅ Created test area: {area_id}")
        
        # Create a test project
        project_data = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'name': 'AI Coach Test Project',
            'description': 'Test project for AI Coach MVP testing',
            'area_id': area_id,
            'status': 'In Progress',
            'importance': 4,
            'created_at': datetime.utcnow().isoformat(),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        project_response = supabase.table('projects').insert(project_data).execute()
        project_id = project_data['id']
        print(f"✅ Created test project: {project_id}")
        
        # Create test tasks
        task_ids = []
        for i in range(3):
            task_data = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'name': f'AI Coach Test Task {i+1}',
                'description': f'Test task {i+1} for AI Coach MVP testing',
                'project_id': project_id,
                'status': 'Not Started',
                'priority': ['high', 'medium', 'low'][i],
                'completed': False,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            task_response = supabase.table('tasks').insert(task_data).execute()
            task_ids.append(task_data['id'])
            print(f"✅ Created test task {i+1}: {task_data['id']}")
        
        return {
            'pillar_id': pillar_id,
            'area_id': area_id,
            'project_id': project_id,
            'task_ids': task_ids
        }
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        import traceback
        traceback.print_exc()
        return None

async def cleanup_test_data(supabase, test_data):
    """Clean up test data"""
    try:
        print("🧹 Cleaning up test data...")
        
        # Delete tasks
        for task_id in test_data['task_ids']:
            supabase.table('tasks').delete().eq('id', task_id).execute()
            
        # Delete project
        supabase.table('projects').delete().eq('id', test_data['project_id']).execute()
        
        # Delete area
        supabase.table('areas').delete().eq('id', test_data['area_id']).execute()
        
        # Delete pillar
        supabase.table('pillars').delete().eq('id', test_data['pillar_id']).execute()
        
        print("✅ Test data cleaned up")
        
    except Exception as e:
        print(f"⚠️ Error cleaning up test data: {e}")

async def test_ai_coach_mvp_with_data():
    """Test AI Coach MVP service with real test data"""
    try:
        print("🎯 TESTING AI COACH MVP SERVICE WITH TEST DATA")
        print("=" * 60)
        
        # Import and initialize services
        from ai_coach_mvp_service import AiCoachMvpService
        from supabase_client import get_supabase_client
        
        supabase = get_supabase_client()
        service = AiCoachMvpService()
        
        print("✅ Successfully initialized services")
        
        # Get the correct user ID from the database
        # Try user_profiles table first (this is where active users are)
        profiles_response = supabase.table('user_profiles').select('id').limit(1).execute()
        
        if profiles_response.data:
            test_user_id = profiles_response.data[0]['id']
            print(f"✅ Using user ID from user_profiles: {test_user_id}")
        else:
            # Fallback to users table
            users_response = supabase.table('users').select('id').eq('email', 'marc.alleyne@aurumtechnologyltd.com').execute()
            
            if users_response.data:
                test_user_id = users_response.data[0]['id']
                print(f"✅ Found user ID from users table: {test_user_id}")
            else:
                print("❌ No users found in database")
                return
        
        # Create test data
        test_data = await create_test_data(supabase, test_user_id)
        if not test_data:
            print("❌ Failed to create test data")
            return
            
        try:
            # Test 1: Generate task why statements (no specific task IDs)
            print("\n📝 Test 1: Generate task why statements (no task IDs)")
            result1 = await service.generate_task_why_statements(test_user_id, None)
            print(f"✅ Test 1 SUCCESS: Generated {len(result1.why_statements)} why statements")
            print(f"   Tasks analyzed: {result1.tasks_analyzed}")
            print(f"   Vertical alignment: {result1.vertical_alignment}")
            
            if result1.why_statements:
                print(f"   Sample why statement: {result1.why_statements[0].why_statement}")
                
            # Test 2: Generate task why statements with specific task IDs
            print("\n📝 Test 2: Generate task why statements with specific task IDs")
            result2 = await service.generate_task_why_statements(test_user_id, test_data['task_ids'][:2])
            print(f"✅ Test 2 SUCCESS: Generated {len(result2.why_statements)} why statements")
            print(f"   Tasks analyzed: {result2.tasks_analyzed}")
            
            if result2.why_statements:
                print(f"   Sample why statement: {result2.why_statements[0].why_statement}")
            
            # Test 3: Get today priorities (suggest focus)
            print("\n📝 Test 3: Get today priorities (suggest focus)")
            result3 = await service.get_today_priorities(test_user_id, coaching_top_n=3)
            print(f"✅ Test 3 SUCCESS: Generated focus suggestions")
            print(f"   Date: {result3.get('date')}")
            print(f"   Tasks count: {len(result3.get('tasks', []))}")
            
            if result3.get('tasks'):
                sample_task = result3['tasks'][0]
                print(f"   Sample task: {sample_task.get('title', 'N/A')} (score: {sample_task.get('score', 'N/A')})")
                print(f"   Project: {sample_task.get('project_name', 'N/A')}")
                print(f"   Area: {sample_task.get('area_name', 'N/A')}")
                
            # Validate response structures
            print("\n🔍 Validating response structures...")
            
            # Validate task why statements response
            assert hasattr(result1, 'why_statements'), "Missing why_statements field"
            assert hasattr(result1, 'tasks_analyzed'), "Missing tasks_analyzed field"
            assert hasattr(result1, 'vertical_alignment'), "Missing vertical_alignment field"
            assert isinstance(result1.why_statements, list), "why_statements should be a list"
            assert isinstance(result1.tasks_analyzed, int), "tasks_analyzed should be an integer"
            assert isinstance(result1.vertical_alignment, dict), "vertical_alignment should be a dict"
            print("✅ Task why statements response structure is valid")
            
            # Validate suggest focus response
            assert isinstance(result3, dict), "suggest focus response should be a dict"
            assert 'date' in result3, "Missing date field"
            assert 'tasks' in result3, "Missing tasks field"
            assert isinstance(result3['date'], str), "date should be a string"
            assert isinstance(result3['tasks'], list), "tasks should be a list"
            
            # Validate task structure in suggest focus response
            if result3['tasks']:
                task = result3['tasks'][0]
                assert 'id' in task, "Task missing id field"
                assert 'score' in task, "Task missing score field"
                assert 'breakdown' in task, "Task missing breakdown field"
                assert 'title' in task or 'name' in task, "Task missing title/name field"
                
            print("✅ Suggest focus response structure is valid")
            
            print("\n🎉 ALL AI COACH MVP TESTS PASSED!")
            
        finally:
            # Clean up test data
            await cleanup_test_data(supabase, test_data)
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ai_coach_mvp_with_data())