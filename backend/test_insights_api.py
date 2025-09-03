#!/usr/bin/env python3
"""
Test the insights API directly to see what's being returned
"""
import os
import sys
sys.path.append('/app/backend')

from fastapi.testclient import TestClient
from server import app
import json

def test_insights_api():
    """Test the insights API endpoint directly"""
    
    client = TestClient(app)
    user_id = 'f9ed7066-5954-46e2-8de3-92d38a28832f'
    
    # Create a mock user object for testing
    class MockUser:
        def __init__(self, user_id):
            self.id = user_id
    
    # Test the insights endpoint
    print("Testing /api/hrm/insights endpoint...")
    
    try:
        # This would normally require authentication, but let's test the underlying data
        from supabase_client import get_supabase_client
        from blackboard_service import blackboard
        
        print(f"Testing direct database query for user {user_id}...")
        
        # Query insights directly from database
        supabase = get_supabase_client()
        response = supabase.table('insights').select('*').eq('user_id', user_id).execute()
        
        insights = response.data or []
        print(f"Direct database query returned {len(insights)} insights")
        
        for i, insight in enumerate(insights):
            print(f"Insight {i+1}: {insight.get('title', 'No title')} (type: {insight.get('insight_type', 'unknown')}, confidence: {insight.get('confidence_score', 0)})")
        
        # Test the blackboard service directly
        print("\nTesting blackboard service...")
        insights_via_blackboard = await blackboard.get_insights(user_id=user_id, limit=50)
        print(f"Blackboard service returned {len(insights_via_blackboard)} insights")
        
        return insights
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return []

async def main():
    insights = test_insights_api()
    print(f"\n=== SUMMARY ===")
    print(f"Total insights found: {len(insights)}")
    print("If this number doesn't match what you see in the UI, there may be:")
    print("1. Frontend caching issues (try hard refresh)")
    print("2. Different user being used in frontend")
    print("3. API returning demo/fallback data")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())