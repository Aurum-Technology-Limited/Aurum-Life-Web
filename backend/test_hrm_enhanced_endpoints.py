#!/usr/bin/env python3
"""
Test script for HRM-enhanced AI Coach endpoints
Tests the integration between legacy AI Coach features and new HRM system
"""

import asyncio
import sys
import os
sys.path.append('/app/backend')

from ai_coach_mvp_service import AiCoachMvpService
from alignment_score_service import AlignmentScoreService
from hrm_service import HierarchicalReasoningModel

async def test_hrm_enhanced_endpoints():
    """Test all HRM-enhanced AI Coach endpoints"""
    
    # Use the test user ID
    test_user_id = 'f9ed7066-5954-46e2-8de3-92d38a28832f'
    
    print("🧪 Testing HRM-Enhanced AI Coach Endpoints")
    print("=" * 50)
    
    # Test 1: Enhanced Today Priorities
    print("\n1. Testing Enhanced Today Priorities...")
    try:
        ai_coach = AiCoachMvpService()
        
        # Test without HRM
        basic_priorities = await ai_coach.get_today_priorities(
            user_id=test_user_id,
            coaching_top_n=3,
            use_hrm=False
        )
        print(f"✅ Basic priorities: {len(basic_priorities.get('tasks', []))} tasks")
        
        # Test with HRM
        enhanced_priorities = await ai_coach.get_today_priorities(
            user_id=test_user_id,
            coaching_top_n=3,
            use_hrm=True
        )
        print(f"✅ Enhanced priorities: {len(enhanced_priorities.get('tasks', []))} tasks")
        
        # Check if HRM insights were added
        hrm_enhanced_count = 0
        for task in enhanced_priorities.get('tasks', []):
            if 'hrm_insight' in task:
                hrm_enhanced_count += 1
        
        print(f"✅ HRM insights added to {hrm_enhanced_count} tasks")
        
    except Exception as e:
        print(f"❌ Enhanced Today Priorities test failed: {e}")
    
    # Test 2: Enhanced Why Statements
    print("\n2. Testing Enhanced Why Statements...")
    try:
        ai_coach = AiCoachMvpService()
        
        # Test without HRM
        basic_why = await ai_coach.generate_task_why_statements(
            user_id=test_user_id,
            use_hrm=False
        )
        print(f"✅ Basic why statements: {len(basic_why.why_statements)} statements")
        
        # Test with HRM
        enhanced_why = await ai_coach.generate_task_why_statements(
            user_id=test_user_id,
            use_hrm=True
        )
        print(f"✅ Enhanced why statements: {len(enhanced_why.why_statements)} statements")
        
        # Check if HRM enhancements were added
        hrm_enhanced_count = 0
        for statement in enhanced_why.why_statements:
            if hasattr(statement, 'hrm_enhancement') and statement.hrm_enhancement:
                hrm_enhanced_count += 1
        
        print(f"✅ HRM enhancements added to {hrm_enhanced_count} statements")
        
    except Exception as e:
        print(f"❌ Enhanced Why Statements test failed: {e}")
    
    # Test 3: Enhanced Alignment Dashboard
    print("\n3. Testing Enhanced Alignment Dashboard...")
    try:
        alignment_service = AlignmentScoreService()
        
        # Test without HRM
        basic_dashboard = await alignment_service.get_alignment_dashboard_data(
            user_id=test_user_id,
            use_hrm=False
        )
        print(f"✅ Basic dashboard data: {basic_dashboard.get('monthly_score', 0)} monthly score")
        
        # Test with HRM
        enhanced_dashboard = await alignment_service.get_alignment_dashboard_data(
            user_id=test_user_id,
            use_hrm=True
        )
        print(f"✅ Enhanced dashboard data: {enhanced_dashboard.get('monthly_score', 0)} monthly score")
        
        # Check if HRM enhancement was added
        if 'hrm_enhancement' in enhanced_dashboard:
            hrm_data = enhanced_dashboard['hrm_enhancement']
            print(f"✅ HRM enhancement added with confidence: {hrm_data.get('confidence_score', 0)}")
        else:
            print("⚠️ No HRM enhancement found in dashboard data")
        
    except Exception as e:
        print(f"❌ Enhanced Alignment Dashboard test failed: {e}")
    
    # Test 4: Direct HRM Service
    print("\n4. Testing Direct HRM Service...")
    try:
        hrm = HierarchicalReasoningModel(test_user_id)
        
        # Test global analysis
        global_insight = await hrm.analyze_entity(
            entity_type='global',
            entity_id=None,
            analysis_depth=hrm.AnalysisDepth.MINIMAL
        )
        
        print(f"✅ Global HRM analysis completed")
        print(f"   - Confidence: {global_insight.confidence_score}")
        print(f"   - Summary: {global_insight.summary[:100]}...")
        print(f"   - Recommendations: {len(global_insight.recommendations)}")
        
    except Exception as e:
        print(f"❌ Direct HRM Service test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 HRM Enhancement Testing Complete!")

if __name__ == "__main__":
    asyncio.run(test_hrm_enhanced_endpoints())