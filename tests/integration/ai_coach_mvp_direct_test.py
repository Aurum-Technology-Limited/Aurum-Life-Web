#!/usr/bin/env python3
"""
🎯 AI COACH MVP DIRECT TEST - Test AI Coach MVP Service Directly
Tests the AI Coach MVP service methods directly to isolate authentication issues
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append('/app/backend')

# Load environment variables from .env file
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path('/app/backend/.env')
load_dotenv(env_path)

async def test_ai_coach_mvp_service():
    """Test AI Coach MVP service directly"""
    try:
        print("🎯 TESTING AI COACH MVP SERVICE DIRECTLY")
        print("=" * 60)
        
        # Import and initialize the service
        from ai_coach_mvp_service import AiCoachMvpService
        
        print("✅ Successfully imported AiCoachMvpService")
        
        service = AiCoachMvpService()
        print("✅ Successfully initialized AiCoachMvpService")
        
        # Get the correct user ID from the database
        from supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        # Try to find user by email in users table
        users_response = supabase.table('users').select('id').eq('email', 'marc.alleyne@aurumtechnologyltd.com').execute()
        
        if users_response.data:
            test_user_id = users_response.data[0]['id']
            print(f"✅ Found user ID: {test_user_id}")
        else:
            # Try user_profiles table
            profiles_response = supabase.table('user_profiles').select('id').execute()
            if profiles_response.data:
                test_user_id = profiles_response.data[0]['id']  # Use first available user
                print(f"✅ Using first available user ID: {test_user_id}")
            else:
                print("❌ No users found in database")
                return
        
        # Test 1: Generate task why statements (no specific task IDs)
        print("\n📝 Test 1: Generate task why statements (no task IDs)")
        try:
            result1 = await service.generate_task_why_statements(test_user_id, None)
            print(f"✅ Test 1 SUCCESS: Generated {len(result1.why_statements)} why statements")
            print(f"   Tasks analyzed: {result1.tasks_analyzed}")
            print(f"   Vertical alignment: {result1.vertical_alignment}")
            
            if result1.why_statements:
                print(f"   Sample why statement: {result1.why_statements[0].why_statement[:100]}...")
                
        except Exception as e:
            print(f"❌ Test 1 FAILED: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 2: Get today priorities (suggest focus)
        print("\n📝 Test 2: Get today priorities (suggest focus)")
        try:
            result2 = await service.get_today_priorities(test_user_id, coaching_top_n=3)
            print(f"✅ Test 2 SUCCESS: Generated focus suggestions")
            print(f"   Date: {result2.get('date')}")
            print(f"   Tasks count: {len(result2.get('tasks', []))}")
            
            if result2.get('tasks'):
                sample_task = result2['tasks'][0]
                print(f"   Sample task: {sample_task.get('title', 'N/A')} (score: {sample_task.get('score', 'N/A')})")
                
        except Exception as e:
            print(f"❌ Test 2 FAILED: {e}")
            import traceback
            traceback.print_exc()
            
        print("\n🎯 DIRECT AI COACH MVP SERVICE TEST COMPLETED!")
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ai_coach_mvp_service())