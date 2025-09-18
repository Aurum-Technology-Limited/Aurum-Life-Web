#!/usr/bin/env python3
"""
Simple test for HRM integration with AI Coach services
Tests the service layer without authentication
"""

import asyncio
import sys
import os
sys.path.append('/app/backend')

from ai_coach_mvp_service import AiCoachMvpService
from alignment_score_service import AlignmentScoreService

async def test_service_integration():
    """Test HRM integration at the service layer"""
    
    # Use the test user ID
    test_user_id = 'f9ed7066-5954-46e2-8de3-92d38a28832f'
    
    print("🧪 Testing HRM Integration at Service Layer")
    print("=" * 50)
    
    # Test 1: AI Coach Service with HRM
    print("\n1. Testing AI Coach Service HRM Integration...")
    try:
        ai_coach = AiCoachMvpService()
        
        # Test basic functionality first
        basic_result = await ai_coach.get_today_priorities(
            user_id=test_user_id,
            coaching_top_n=2,
            use_hrm=False
        )
        
        print(f"✅ Basic AI Coach working: {len(basic_result.get('tasks', []))} tasks")
        
        # Test HRM enhancement
        enhanced_result = await ai_coach.get_today_priorities(
            user_id=test_user_id,
            coaching_top_n=2,
            use_hrm=True
        )
        
        print(f"✅ HRM-enhanced AI Coach working: {len(enhanced_result.get('tasks', []))} tasks")
        
        # Check for HRM insights
        for i, task in enumerate(enhanced_result.get('tasks', [])):
            if 'hrm_insight' in task:
                insight = task['hrm_insight']
                print(f"   Task {i+1}: Confidence {insight.get('confidence_score', 0):.2f}")
            else:
                print(f"   Task {i+1}: No HRM insight")
        
    except Exception as e:
        print(f"❌ AI Coach Service test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Alignment Service with HRM
    print("\n2. Testing Alignment Service HRM Integration...")
    try:
        alignment_service = AlignmentScoreService()
        
        # Test basic functionality
        basic_dashboard = await alignment_service.get_alignment_dashboard_data(
            user_id=test_user_id,
            use_hrm=False
        )
        
        print(f"✅ Basic Alignment Service working: {basic_dashboard.get('monthly_score', 0)} points")
        
        # Test HRM enhancement
        enhanced_dashboard = await alignment_service.get_alignment_dashboard_data(
            user_id=test_user_id,
            use_hrm=True
        )
        
        print(f"✅ HRM-enhanced Alignment Service working: {enhanced_dashboard.get('monthly_score', 0)} points")
        
        if 'hrm_enhancement' in enhanced_dashboard:
            hrm_data = enhanced_dashboard['hrm_enhancement']
            print(f"   HRM Confidence: {hrm_data.get('confidence_score', 0):.2f}")
            print(f"   Recommendations: {len(hrm_data.get('recommendations', []))}")
        
    except Exception as e:
        print(f"❌ Alignment Service test failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("🎉 Service Integration Testing Complete!")

if __name__ == "__main__":
    asyncio.run(test_service_integration())