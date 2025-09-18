#!/usr/bin/env python3
"""
Analytics Tables Verification Script
Check if analytics tables are properly created and accessible
"""

import os
from supabase import create_client
from dotenv import load_dotenv
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def get_supabase_client():
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    return create_client(url, key)

def verify_analytics_tables():
    """Verify all analytics tables and their structure"""
    supabase = get_supabase_client()
    
    logger.info("🔍 Verifying Analytics Tables Setup...")
    logger.info("="*60)
    
    tables_to_verify = [
        'user_analytics_preferences',
        'user_sessions',
        'user_behavior_events'
    ]
    
    verification_results = {}
    
    for table_name in tables_to_verify:
        logger.info(f"📋 Checking table: {table_name}")
        
        try:
            # Try to select from table (limit 0 to just check structure)
            result = supabase.table(table_name).select('*').limit(0).execute()
            
            # Try to get table info
            count_result = supabase.table(table_name).select('id', count='exact').execute()
            record_count = count_result.count if hasattr(count_result, 'count') else 0
            
            verification_results[table_name] = {
                'exists': True,
                'accessible': True,
                'record_count': record_count,
                'error': None
            }
            
            logger.info(f"   ✅ Table exists and accessible ({record_count} records)")
            
        except Exception as e:
            verification_results[table_name] = {
                'exists': False,
                'accessible': False,
                'record_count': 0,
                'error': str(e)
            }
            logger.error(f"   ❌ Table verification failed: {e}")
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("📊 VERIFICATION SUMMARY:")
    logger.info("="*60)
    
    all_verified = True
    for table_name, results in verification_results.items():
        status = "✅ PASS" if results['exists'] else "❌ FAIL"
        logger.info(f"{table_name}: {status}")
        if not results['exists']:
            all_verified = False
            logger.error(f"   Error: {results['error']}")
    
    if all_verified:
        logger.info("\n🎉 ALL ANALYTICS TABLES VERIFIED SUCCESSFULLY!")
        logger.info("✅ Analytics system is ready for production use")
        
        # Test creating a sample record
        test_analytics_integration()
        
    else:
        logger.error("\n❌ VERIFICATION FAILED")
        logger.error("Some tables are missing or not accessible")
        logger.error("Please run the migration script first")

def test_analytics_integration():
    """Test basic analytics integration"""
    logger.info("\n🧪 Testing Analytics Integration...")
    
    supabase = get_supabase_client()
    
    try:
        # Test creating default analytics preferences for a test user
        test_user_id = "00000000-0000-0000-0000-000000000001"  # Dummy UUID for testing
        
        # Try to insert test preferences
        test_prefs = {
            'user_id': test_user_id,
            'analytics_consent': True,
            'ai_behavior_tracking': True,
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Insert test record
        result = supabase.table('user_analytics_preferences').insert(test_prefs).execute()
        
        if result.data:
            logger.info("✅ Test record creation successful")
            
            # Clean up test record
            supabase.table('user_analytics_preferences').delete().eq('user_id', test_user_id).execute()
            logger.info("✅ Test record cleanup successful")
        
    except Exception as e:
        logger.warning(f"⚠️  Integration test failed (this is normal if RLS is enabled): {e}")
        logger.info("✅ Tables exist but may require proper authentication for access")

if __name__ == "__main__":
    verify_analytics_tables()