#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from typing import Dict, Any, List

# Configuration - Use localhost URL since backend is running locally
BACKEND_URL = "http://localhost:8001"
API_BASE = f"{BACKEND_URL}/api"

class DailyReflectionsSchemaTestSuite:
    """
    Focused testing for Daily Reflections database schema issue
    
    The review request specifically mentions:
    - POST /api/ai/daily-reflection (should return 500 error due to missing table)
    - But our initial test showed it working, so let's investigate deeper
    """
    
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "nav.test@aurumlife.com"
        self.test_user_password = "testpassword123"
        self.test_results = []
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()
            
    async def authenticate(self):
        """Authenticate with nav.test@aurumlife.com credentials"""
        try:
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data["access_token"]
                    print(f"✅ Authentication successful for {self.test_user_email}")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Authentication failed: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
            
    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.auth_token}"}
        
    async def test_daily_reflection_creation_detailed(self):
        """
        Detailed test of daily reflection creation to identify exact schema issues
        """
        print("\n🧪 Detailed Daily Reflection Creation Test")
        print("Testing various scenarios to identify database schema issues...")
        
        try:
            # Test 1: Basic reflection creation
            print("\n   Test 1: Basic reflection creation...")
            basic_reflection = {
                "reflection_text": "Today I worked on testing the daily reflections system."
            }
            
            async with self.session.post(f"{API_BASE}/ai/daily-reflection", json=basic_reflection, headers=self.get_auth_headers()) as response:
                response_text = await response.text()
                print(f"      Status: {response.status}")
                print(f"      Response: {response_text[:200]}...")
                
                if response.status == 500:
                    print("      ✅ Expected 500 error confirmed - table missing")
                    if 'daily_reflections' in response_text.lower():
                        print("      ✅ Error confirms missing daily_reflections table")
                elif response.status == 200:
                    print("      ⚠️ Unexpected success - table may exist")
                else:
                    print(f"      ❓ Unexpected status: {response.status}")
                    
            # Test 2: Full reflection creation with all fields
            print("\n   Test 2: Full reflection creation with all fields...")
            full_reflection = {
                "reflection_text": "Comprehensive daily reflection test",
                "completion_score": 8,
                "mood": "productive",
                "biggest_accomplishment": "Identified database schema issues",
                "challenges_faced": "Understanding the exact table structure",
                "tomorrow_focus": "Fix the daily_reflections table schema",
                "reflection_date": "2025-01-31"
            }
            
            async with self.session.post(f"{API_BASE}/ai/daily-reflection", json=full_reflection, headers=self.get_auth_headers()) as response:
                response_text = await response.text()
                print(f"      Status: {response.status}")
                print(f"      Response: {response_text[:200]}...")
                
                if response.status == 500:
                    print("      ✅ Expected 500 error confirmed")
                    # Check for specific error messages
                    if 'relation' in response_text.lower() and 'daily_reflections' in response_text.lower():
                        print("      ✅ PostgreSQL relation error - table doesn't exist")
                    elif 'column' in response_text.lower():
                        print("      ⚠️ Column error - table exists but schema mismatch")
                    elif 'constraint' in response_text.lower():
                        print("      ⚠️ Constraint error - foreign key issues")
                elif response.status == 200:
                    data = await response.json()
                    print("      ⚠️ Unexpected success - analyzing response...")
                    print(f"      Response data: {json.dumps(data, indent=2)}")
                    
            # Test 3: Invalid data to trigger validation
            print("\n   Test 3: Invalid data to trigger validation...")
            invalid_reflection = {
                "completion_score": 15,  # Invalid score (should be 1-10)
                "mood": "invalid_mood_value"
            }
            
            async with self.session.post(f"{API_BASE}/ai/daily-reflection", json=invalid_reflection, headers=self.get_auth_headers()) as response:
                response_text = await response.text()
                print(f"      Status: {response.status}")
                print(f"      Response: {response_text[:200]}...")
                
                if response.status == 422:
                    print("      ✅ Validation error as expected")
                elif response.status == 500:
                    print("      ⚠️ 500 error - may indicate database issue before validation")
                    
            return True
            
        except Exception as e:
            print(f"❌ Daily reflection creation test failed: {e}")
            return False
            
    async def test_daily_reflections_retrieval_detailed(self):
        """
        Detailed test of daily reflections retrieval
        """
        print("\n🧪 Detailed Daily Reflections Retrieval Test")
        
        try:
            # Test GET /api/ai/daily-reflections with different parameters
            print("\n   Testing GET /api/ai/daily-reflections...")
            
            # Test 1: Default retrieval
            async with self.session.get(f"{API_BASE}/ai/daily-reflections", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"      ✅ Default retrieval successful")
                    print(f"      Reflections count: {data.get('count', 0)}")
                    print(f"      Reflections data: {len(data.get('reflections', []))}")
                    
                    # If we have reflections, examine the structure
                    if data.get('reflections'):
                        sample_reflection = data['reflections'][0]
                        print(f"      Sample reflection fields: {list(sample_reflection.keys())}")
                else:
                    error_text = await response.text()
                    print(f"      ❌ Retrieval failed: {response.status} - {error_text}")
                    
            # Test 2: Retrieval with days parameter
            async with self.session.get(f"{API_BASE}/ai/daily-reflections?days=7", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"      ✅ Retrieval with days parameter successful")
                    print(f"      Last 7 days reflections: {data.get('count', 0)}")
                else:
                    error_text = await response.text()
                    print(f"      ❌ Retrieval with days failed: {response.status} - {error_text}")
                    
            return True
            
        except Exception as e:
            print(f"❌ Daily reflections retrieval test failed: {e}")
            return False
            
    async def test_backend_logs_for_errors(self):
        """
        Check backend logs for any database-related errors
        """
        print("\n🧪 Backend Logs Analysis")
        
        try:
            # Try to trigger an error and then check logs
            print("   Triggering potential database error...")
            
            # Make a request that might cause database issues
            problematic_data = {
                "reflection_text": "Test reflection to trigger potential database error",
                "completion_score": 5,
                "mood": "testing"
            }
            
            async with self.session.post(f"{API_BASE}/ai/daily-reflection", json=problematic_data, headers=self.get_auth_headers()) as response:
                response_text = await response.text()
                print(f"   Response status: {response.status}")
                
                if response.status == 500:
                    print("   ✅ 500 error detected - analyzing error message...")
                    
                    # Look for specific database error patterns
                    error_lower = response_text.lower()
                    
                    if 'relation "public.daily_reflections" does not exist' in error_lower:
                        print("   🎯 CONFIRMED: daily_reflections table does not exist in Supabase")
                        self.test_results.append({
                            "test": "Database Schema Issue", 
                            "status": "CONFIRMED", 
                            "details": "daily_reflections table missing from Supabase database"
                        })
                    elif 'column' in error_lower and 'does not exist' in error_lower:
                        print("   🎯 CONFIRMED: Column mismatch in daily_reflections table")
                        self.test_results.append({
                            "test": "Database Schema Issue", 
                            "status": "CONFIRMED", 
                            "details": "daily_reflections table exists but has column mismatch"
                        })
                    elif 'constraint' in error_lower:
                        print("   🎯 CONFIRMED: Foreign key constraint issue")
                        self.test_results.append({
                            "test": "Database Schema Issue", 
                            "status": "CONFIRMED", 
                            "details": "daily_reflections table has constraint issues"
                        })
                    else:
                        print(f"   ❓ Unknown database error: {response_text[:300]}")
                        self.test_results.append({
                            "test": "Database Schema Issue", 
                            "status": "UNKNOWN", 
                            "details": f"Unknown database error: {response_text[:100]}"
                        })
                        
                elif response.status == 200:
                    print("   ⚠️ No database error - daily_reflections may be working")
                    data = await response.json()
                    print(f"   Created reflection ID: {data.get('id', 'Unknown')}")
                    self.test_results.append({
                        "test": "Database Schema Issue", 
                        "status": "RESOLVED", 
                        "details": "daily_reflections table appears to be working correctly"
                    })
                    
            return True
            
        except Exception as e:
            print(f"❌ Backend logs analysis failed: {e}")
            return False
            
    def print_schema_test_summary(self):
        """Print schema test summary"""
        print("\n" + "="*80)
        print("🔍 DAILY REFLECTIONS DATABASE SCHEMA - DETAILED ANALYSIS")
        print("="*80)
        
        print("\n📋 TEST RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status_icon = {"CONFIRMED": "🎯", "RESOLVED": "✅", "UNKNOWN": "❓"}
            icon = status_icon.get(result["status"], "❓")
            print(f"{i:2d}. {icon} {result['test']}: {result['status']}")
            
            if "details" in result:
                print(f"    📝 {result['details']}")
                
        print("\n" + "="*80)
        
        # Provide recommendations based on findings
        if any(r["status"] == "CONFIRMED" and "missing" in r["details"] for r in self.test_results):
            print("🚨 CRITICAL ISSUE CONFIRMED:")
            print("   The daily_reflections table is missing from the Supabase database.")
            print("   This is blocking the Daily Reflection creation feature.")
            print("\n🔧 RECOMMENDED SOLUTION:")
            print("   Create the daily_reflections table in Supabase with the following schema:")
            print("   - id (UUID, primary key)")
            print("   - user_id (UUID, foreign key to users table)")
            print("   - date (DATE)")
            print("   - reflection_text (TEXT)")
            print("   - completion_score (INTEGER)")
            print("   - mood (VARCHAR)")
            print("   - biggest_accomplishment (TEXT)")
            print("   - challenges_faced (TEXT)")
            print("   - tomorrow_focus (TEXT)")
            print("   - created_at (TIMESTAMP)")
        elif any(r["status"] == "RESOLVED" for r in self.test_results):
            print("✅ ISSUE RESOLVED:")
            print("   The daily_reflections table appears to be working correctly now.")
            print("   The database schema issue mentioned in the review may have been fixed.")
        else:
            print("❓ INCONCLUSIVE RESULTS:")
            print("   Unable to definitively determine the database schema status.")
            
        print("="*80)
        
    async def run_schema_tests(self):
        """Run detailed schema tests"""
        print("🔍 Starting Detailed Daily Reflections Database Schema Analysis...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print(f"👤 Test User: {self.test_user_email}")
        
        await self.setup_session()
        
        try:
            # Authentication
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed with tests")
                return
                
            # Run detailed tests
            await self.test_daily_reflection_creation_detailed()
            await self.test_daily_reflections_retrieval_detailed()
            await self.test_backend_logs_for_errors()
            
        finally:
            await self.cleanup_session()
            
        # Print summary
        self.print_schema_test_summary()

async def main():
    """Main function to run schema tests"""
    test_suite = DailyReflectionsSchemaTestSuite()
    await test_suite.run_schema_tests()

if __name__ == "__main__":
    asyncio.run(main())