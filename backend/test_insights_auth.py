#!/usr/bin/env python3
"""
Test insights API with proper authentication to identify the issue
"""
import os
import sys
sys.path.append('/app/backend')

import asyncio
from fastapi.testclient import TestClient
from server import app
from supabase_auth import get_current_active_user

async def test_insights_with_mock_auth():
    """Test insights endpoint with proper authentication"""
    
    client = TestClient(app)
    user_id = 'f9ed7066-5954-46e2-8de3-92d38a28832f'
    
    print(f"Testing insights API for user {user_id}...")
    
    # Test 1: Check if the endpoint exists
    try:
        response = client.get('/api/hrm/insights')
        print(f"✅ Endpoint exists, returned {response.status_code}")
        if response.status_code == 403:
            print("❌ Authentication required but missing")
        
    except Exception as e:
        print(f"❌ Endpoint test failed: {e}")
    
    # Test 2: Check what's in the database directly
    try:
        from supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        insights_response = supabase.table('insights').select('*').eq('user_id', user_id).execute()
        insights = insights_response.data or []
        
        print(f"\n📊 Database contains {len(insights)} insights for user {user_id}:")
        for insight in insights:
            print(f"  - {insight.get('title', 'No title')}")
            print(f"    Type: {insight.get('insight_type', 'unknown')}")
            print(f"    Confidence: {insight.get('confidence_score', 0)}")
            print(f"    Active: {insight.get('is_active', False)}")
            print()
        
        return insights
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return []

def fix_frontend_auth_issue():
    """Provide steps to fix the frontend authentication issue"""
    
    print("\n🔧 FRONTEND AUTHENTICATION FIX STEPS:")
    print("=" * 50)
    
    print("1. Check if user is properly logged in:")
    print("   - Open browser DevTools → Application → LocalStorage")
    print("   - Look for 'auth_token' or 'token' entries")
    print("   - Verify token is not expired")
    print()
    
    print("2. Test authentication status:")
    print("   - In browser console: localStorage.getItem('auth_token')")
    print("   - Check if token exists and is valid")
    print()
    
    print("3. Manual token refresh:")
    print("   - Try logging out and logging back in")
    print("   - Clear browser cache and localStorage")
    print("   - Hard refresh the page (Ctrl+Shift+R)")
    print()
    
    print("4. API endpoint test:")
    print("   - Check if /api/auth/me returns user data")
    print("   - Verify /api/health is responding")
    print()
    
    print("5. Backend logs:")
    print("   - Check 'tail -f /var/log/supervisor/backend.*.log'")
    print("   - Look for authentication errors and token validation issues")

async def main():
    insights = await test_insights_with_mock_auth()
    
    if insights:
        print(f"\n✅ SUCCESS: Found {len(insights)} real insights in database")
        print("The issue is frontend authentication, not data availability")
    else:
        print(f"\n❌ ISSUE: No insights found in database")
        print("Need to generate insights first")
    
    fix_frontend_auth_issue()

if __name__ == "__main__":
    asyncio.run(main())