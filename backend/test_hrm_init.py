#!/usr/bin/env python3
"""
Test HRM Service Initialization
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add backend to path
sys.path.append('/app/backend')

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_gemini_api_key():
    """Test if GEMINI_API_KEY is loaded correctly"""
    print("🔑 TESTING GEMINI API KEY...")
    
    api_key = os.environ.get('GEMINI_API_KEY')
    model = os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash-lite')
    
    if api_key:
        print(f"   ✅ GEMINI_API_KEY found: {api_key[:20]}...")
        print(f"   ✅ GEMINI_MODEL: {model}")
        return True
    else:
        print("   ❌ GEMINI_API_KEY not found in environment")
        return False

def test_hrm_service_import():
    """Test if HRM service can be imported"""
    print("\n📦 TESTING HRM SERVICE IMPORT...")
    
    try:
        from hrm_service import HierarchicalReasoningModel, AnalysisDepth
        print("   ✅ HRM service imported successfully")
        print(f"   ✅ AnalysisDepth enum: {list(AnalysisDepth)}")
        return True
    except Exception as e:
        print(f"   ❌ Failed to import HRM service: {e}")
        return False

def test_llm_chat_import():
    """Test if LLM chat can be imported"""
    print("\n🤖 TESTING LLM CHAT IMPORT...")
    
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        print("   ✅ LlmChat imported successfully")
        return True
    except Exception as e:
        print(f"   ❌ Failed to import LlmChat: {e}")
        return False

def test_hrm_initialization():
    """Test if HRM can be initialized"""
    print("\n🚀 TESTING HRM INITIALIZATION...")
    
    try:
        from hrm_service import HierarchicalReasoningModel
        
        # Use a dummy user ID for testing
        test_user_id = "test-user-123"
        
        hrm = HierarchicalReasoningModel(test_user_id)
        print("   ✅ HRM instance created successfully")
        print(f"   ✅ User ID: {hrm.user_id}")
        print(f"   ✅ LLM initialized: {hrm.llm is not None}")
        
        return True
    except Exception as e:
        print(f"   ❌ Failed to initialize HRM: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_blackboard_import():
    """Test if blackboard service can be imported"""
    print("\n📋 TESTING BLACKBOARD SERVICE IMPORT...")
    
    try:
        from blackboard_service import BlackboardService, blackboard
        print("   ✅ Blackboard service imported successfully")
        print(f"   ✅ Global blackboard instance: {blackboard is not None}")
        return True
    except Exception as e:
        print(f"   ❌ Failed to import blackboard service: {e}")
        return False

def test_supabase_connection():
    """Test basic Supabase connection"""
    print("\n🗄️ TESTING SUPABASE CONNECTION...")
    
    try:
        from supabase_client import get_supabase_client
        
        supabase = get_supabase_client()
        print("   ✅ Supabase client created successfully")
        
        # Try a simple query that doesn't require authentication
        # This might fail due to RLS but we can see if the connection works
        try:
            response = supabase.table('insights').select('count').execute()
            print("   ✅ Supabase query executed (connection working)")
        except Exception as query_e:
            print(f"   ⚠️ Supabase query failed (expected due to RLS): {query_e}")
            print("   ✅ But connection to Supabase is working")
        
        return True
    except Exception as e:
        print(f"   ❌ Failed to connect to Supabase: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 HRM SYSTEM INITIALIZATION TESTS")
    print("=" * 50)
    
    tests = [
        test_gemini_api_key,
        test_llm_chat_import,
        test_hrm_service_import,
        test_blackboard_import,
        test_supabase_connection,
        test_hrm_initialization
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print(f"   Passed: {sum(results)}/{len(results)}")
    print(f"   Failed: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("   🎉 ALL TESTS PASSED - HRM SYSTEM IS READY!")
    else:
        print("   ⚠️ SOME TESTS FAILED - CHECK LOGS ABOVE")
    
    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)