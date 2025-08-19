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

# Set environment variables
os.environ['SUPABASE_URL'] = 'https://sftppbnqlsumjlrgyzgo.supabase.co'
os.environ['SUPABASE_ANON_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNmdHBwYm5xbHN1bWpscmd5emdvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM1MTYwOTksImV4cCI6MjA2OTA5MjA5OX0.EE8EW1fr2GyUo_exh7Sj_kA2mXGWwffxU4aEHXPWjrQ'

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
        
        # Test user ID (from the test account)
        test_user_id = "marc.alleyne@aurumtechnologyltd.com"  # This might be the user ID format
        
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