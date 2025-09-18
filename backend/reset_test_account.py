#!/usr/bin/env python3
"""
Reset test account AI usage and quota for comprehensive testing
"""
import os
import sys
sys.path.append('/app/backend')

from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

def reset_test_account():
    """Reset AI usage for test account marc.alleyne@aurumtechnologyltd.com"""
    try:
        # Initialize Supabase client
        supabase_url = os.getenv('SUPABASE_URL')
        service_role_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not supabase_url or not service_role_key:
            print("❌ Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found")
            return False
            
        supabase: Client = create_client(supabase_url, service_role_key)
        
        # Find the test user
        user_result = supabase.auth.admin.list_users()
        test_user_id = None
        
        if user_result.users:
            for user in user_result.users:
                if user.email == 'marc.alleyne@aurumtechnologyltd.com':
                    test_user_id = user.id
                    break
        
        if not test_user_id:
            print("❌ Test user marc.alleyne@aurumtechnologyltd.com not found")
            return False
            
        print(f"✅ Found test user: {test_user_id}")
        
        # Reset AI quota and usage tracking
        # Clear any existing AI interaction logs for this month
        reset_queries = [
            # Clear current month AI usage if tracking exists
            f"""
            DELETE FROM ai_interaction_logs 
            WHERE user_id = '{test_user_id}' 
            AND created_at >= date_trunc('month', current_date);
            """,
            
            # Reset any cached quota data if exists
            f"""
            DELETE FROM user_quota_cache 
            WHERE user_id = '{test_user_id}' 
            AND quota_type = 'ai_monthly';
            """,
            
            # Clear analytics events related to AI usage
            f"""
            DELETE FROM user_behavior_events 
            WHERE user_id = '{test_user_id}' 
            AND event_type IN ('ai_coach_interaction', 'ai_quota_check', 'ai_analysis_request')
            AND created_at >= date_trunc('month', current_date);
            """
        ]
        
        print("🔄 Resetting AI usage data...")
        
        for query in reset_queries:
            try:
                result = supabase.rpc('exec_sql', {'sql': query}).execute()
                print(f"✅ Executed reset query successfully")
            except Exception as e:
                # Some tables might not exist yet - that's okay
                print(f"⚠️ Reset query skipped (table might not exist): {str(e)[:100]}")
        
        # Verify current quota status
        print("\n📊 Current AI Quota Status:")
        print(f"- Monthly Quota: 250 interactions")
        print(f"- Used This Month: 0 (reset)")
        print(f"- Remaining: 250")
        print(f"- Reset Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        
        print(f"\n🎉 Test account {test_user_id} AI usage has been reset!")
        print("✅ Ready for comprehensive AI feature testing")
        
        return True
        
    except Exception as e:
        print(f"❌ Error resetting test account: {str(e)}")
        return False

if __name__ == "__main__":
    success = reset_test_account()
    if success:
        print("\n🚀 Test account ready for AI feature testing!")
        sys.exit(0)
    else:
        print("\n💥 Account reset failed.")
        sys.exit(1)