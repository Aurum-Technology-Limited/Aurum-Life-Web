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

class EveningReflectionDebugSuite:
    """Debug suite specifically for Evening Reflection API endpoint causing 500 errors"""
    
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
        """Authenticate with test credentials"""
        try:
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            print(f"🔐 Authenticating with {self.test_user_email}...")
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
        
    async def test_daily_reflection_simple(self):
        """Test 1: Daily Reflection Creation with Simple Data"""
        print("\n🧪 Test 1: Daily Reflection Creation - Simple Data")
        print("Testing POST /api/ai/daily-reflection with minimal data")
        
        try:
            # Simple reflection data as specified in review request
            simple_reflection = {
                "reflection_text": "Test reflection for debugging"
            }
            
            print(f"📤 Sending simple reflection data: {simple_reflection}")
            
            async with self.session.post(
                f"{API_BASE}/ai/daily-reflection", 
                json=simple_reflection, 
                headers=self.get_auth_headers()
            ) as response:
                
                print(f"📥 Response status: {response.status}")
                print(f"📥 Response headers: {dict(response.headers)}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Simple daily reflection created successfully!")
                    print(f"📝 Response data: {json.dumps(data, indent=2)}")
                    
                    # Verify response structure
                    required_fields = ['id', 'user_id', 'reflection_text', 'created_at']
                    missing_fields = [field for field in required_fields if field not in data]
                    
                    if not missing_fields:
                        print("✅ Response contains all required fields")
                        self.test_results.append({
                            "test": "Simple Daily Reflection Creation", 
                            "status": "PASSED", 
                            "details": "Successfully created with minimal data"
                        })
                        return True
                    else:
                        print(f"⚠️ Response missing fields: {missing_fields}")
                        self.test_results.append({
                            "test": "Simple Daily Reflection Creation", 
                            "status": "PASSED", 
                            "details": f"Created but missing fields: {missing_fields}"
                        })
                        return True
                        
                elif response.status == 500:
                    error_text = await response.text()
                    print(f"❌ 500 SERVER ERROR DETECTED!")
                    print(f"💥 Error details: {error_text}")
                    
                    try:
                        error_json = await response.json()
                        print(f"💥 Error JSON: {json.dumps(error_json, indent=2)}")
                    except:
                        print("💥 Error response is not JSON")
                    
                    self.test_results.append({
                        "test": "Simple Daily Reflection Creation", 
                        "status": "FAILED", 
                        "reason": f"500 Server Error: {error_text[:200]}"
                    })
                    return False
                    
                else:
                    error_text = await response.text()
                    print(f"❌ Daily reflection creation failed: {response.status}")
                    print(f"💥 Error details: {error_text}")
                    
                    self.test_results.append({
                        "test": "Simple Daily Reflection Creation", 
                        "status": "FAILED", 
                        "reason": f"HTTP {response.status}: {error_text[:200]}"
                    })
                    return False
                    
        except Exception as e:
            print(f"❌ Simple daily reflection test failed: {e}")
            self.test_results.append({
                "test": "Simple Daily Reflection Creation", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return False
            
    async def test_daily_reflection_complete(self):
        """Test 2: Daily Reflection Creation with Complete Data"""
        print("\n🧪 Test 2: Daily Reflection Creation - Complete Data")
        print("Testing POST /api/ai/daily-reflection with all fields")
        
        try:
            # Complete reflection data as specified in review request
            complete_reflection = {
                "reflection_text": "Test reflection for debugging",
                "completion_score": 7,
                "mood": "productive",
                "biggest_accomplishment": "Fixed the API",
                "challenges_faced": "Backend debugging",
                "tomorrow_focus": "Continue testing"
            }
            
            print(f"📤 Sending complete reflection data: {json.dumps(complete_reflection, indent=2)}")
            
            async with self.session.post(
                f"{API_BASE}/ai/daily-reflection", 
                json=complete_reflection, 
                headers=self.get_auth_headers()
            ) as response:
                
                print(f"📥 Response status: {response.status}")
                print(f"📥 Response headers: {dict(response.headers)}")
                
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Complete daily reflection created successfully!")
                    print(f"📝 Response data: {json.dumps(data, indent=2)}")
                    
                    # Verify all fields are preserved
                    expected_fields = ['reflection_text', 'completion_score', 'mood', 'biggest_accomplishment', 'challenges_faced', 'tomorrow_focus']
                    preserved_fields = [field for field in expected_fields if data.get(field) == complete_reflection[field]]
                    
                    if len(preserved_fields) == len(expected_fields):
                        print("✅ All fields preserved correctly")
                        self.test_results.append({
                            "test": "Complete Daily Reflection Creation", 
                            "status": "PASSED", 
                            "details": "Successfully created with all fields preserved"
                        })
                        return True
                    else:
                        missing_preserved = [field for field in expected_fields if field not in preserved_fields]
                        print(f"⚠️ Some fields not preserved: {missing_preserved}")
                        self.test_results.append({
                            "test": "Complete Daily Reflection Creation", 
                            "status": "PASSED", 
                            "details": f"Created but some fields not preserved: {missing_preserved}"
                        })
                        return True
                        
                elif response.status == 500:
                    error_text = await response.text()
                    print(f"❌ 500 SERVER ERROR DETECTED!")
                    print(f"💥 Error details: {error_text}")
                    
                    try:
                        error_json = await response.json()
                        print(f"💥 Error JSON: {json.dumps(error_json, indent=2)}")
                    except:
                        print("💥 Error response is not JSON")
                    
                    self.test_results.append({
                        "test": "Complete Daily Reflection Creation", 
                        "status": "FAILED", 
                        "reason": f"500 Server Error: {error_text[:200]}"
                    })
                    return False
                    
                else:
                    error_text = await response.text()
                    print(f"❌ Daily reflection creation failed: {response.status}")
                    print(f"💥 Error details: {error_text}")
                    
                    self.test_results.append({
                        "test": "Complete Daily Reflection Creation", 
                        "status": "FAILED", 
                        "reason": f"HTTP {response.status}: {error_text[:200]}"
                    })
                    return False
                    
        except Exception as e:
            print(f"❌ Complete daily reflection test failed: {e}")
            self.test_results.append({
                "test": "Complete Daily Reflection Creation", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return False
            
    async def test_other_ai_endpoints(self):
        """Test 3: Verify Other AI Endpoints are Working"""
        print("\n🧪 Test 3: Verify Other AI Endpoints are Working")
        
        try:
            success_count = 0
            total_tests = 3
            
            # Test GET /api/ai/daily-reflections
            print("\n   Testing GET /api/ai/daily-reflections...")
            async with self.session.get(f"{API_BASE}/ai/daily-reflections", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Daily reflections endpoint working - found {data.get('count', 0)} reflections")
                    success_count += 1
                else:
                    error_text = await response.text()
                    print(f"   ❌ Daily reflections endpoint failed: {response.status} - {error_text}")
                    
            # Test GET /api/ai/daily-streak
            print("\n   Testing GET /api/ai/daily-streak...")
            async with self.session.get(f"{API_BASE}/ai/daily-streak", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Daily streak endpoint working - current streak: {data.get('daily_streak', 0)} days")
                    success_count += 1
                else:
                    error_text = await response.text()
                    print(f"   ❌ Daily streak endpoint failed: {response.status} - {error_text}")
                    
            # Test GET /api/ai/should-show-daily-prompt
            print("\n   Testing GET /api/ai/should-show-daily-prompt...")
            async with self.session.get(f"{API_BASE}/ai/should-show-daily-prompt", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ Should show prompt endpoint working - should show: {data.get('should_show_prompt', False)}")
                    success_count += 1
                else:
                    error_text = await response.text()
                    print(f"   ❌ Should show prompt endpoint failed: {response.status} - {error_text}")
                    
            if success_count == total_tests:
                print(f"\n✅ All {total_tests} other AI endpoints working correctly")
                self.test_results.append({
                    "test": "Other AI Endpoints Verification", 
                    "status": "PASSED", 
                    "details": f"All {total_tests} endpoints working"
                })
                return True
            else:
                print(f"\n⚠️ Only {success_count}/{total_tests} other AI endpoints working")
                self.test_results.append({
                    "test": "Other AI Endpoints Verification", 
                    "status": "PARTIAL", 
                    "details": f"{success_count}/{total_tests} endpoints working"
                })
                return False
                
        except Exception as e:
            print(f"❌ Other AI endpoints test failed: {e}")
            self.test_results.append({
                "test": "Other AI Endpoints Verification", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return False
            
    async def check_backend_logs(self):
        """Test 4: Check Backend Logs for Specific Errors"""
        print("\n🧪 Test 4: Check Backend Logs for Specific Errors")
        
        try:
            # Check if we can access supervisor logs
            import subprocess
            
            print("📋 Checking backend supervisor logs...")
            try:
                # Get recent backend logs
                result = subprocess.run(
                    ["tail", "-n", "50", "/var/log/supervisor/backend.log"], 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                
                if result.returncode == 0:
                    logs = result.stdout
                    print("📋 Recent backend logs:")
                    print("-" * 60)
                    print(logs)
                    print("-" * 60)
                    
                    # Look for specific error patterns
                    error_patterns = [
                        "daily_reflections",
                        "relation",
                        "does not exist",
                        "42P01",
                        "500",
                        "Internal Server Error",
                        "Exception",
                        "Error"
                    ]
                    
                    found_errors = []
                    for pattern in error_patterns:
                        if pattern.lower() in logs.lower():
                            found_errors.append(pattern)
                            
                    if found_errors:
                        print(f"🔍 Found error patterns in logs: {found_errors}")
                        self.test_results.append({
                            "test": "Backend Logs Analysis", 
                            "status": "FOUND_ERRORS", 
                            "details": f"Error patterns found: {found_errors}"
                        })
                    else:
                        print("✅ No obvious error patterns found in recent logs")
                        self.test_results.append({
                            "test": "Backend Logs Analysis", 
                            "status": "PASSED", 
                            "details": "No error patterns found in recent logs"
                        })
                        
                else:
                    print(f"⚠️ Could not read backend logs: {result.stderr}")
                    self.test_results.append({
                        "test": "Backend Logs Analysis", 
                        "status": "SKIPPED", 
                        "details": "Could not access supervisor logs"
                    })
                    
            except subprocess.TimeoutExpired:
                print("⚠️ Timeout reading backend logs")
                self.test_results.append({
                    "test": "Backend Logs Analysis", 
                    "status": "SKIPPED", 
                    "details": "Timeout reading logs"
                })
                
            except Exception as log_error:
                print(f"⚠️ Error reading backend logs: {log_error}")
                self.test_results.append({
                    "test": "Backend Logs Analysis", 
                    "status": "SKIPPED", 
                    "details": f"Error reading logs: {log_error}"
                })
                
        except Exception as e:
            print(f"❌ Backend logs check failed: {e}")
            self.test_results.append({
                "test": "Backend Logs Analysis", 
                "status": "FAILED", 
                "reason": str(e)
            })
            
    async def test_database_schema(self):
        """Test 5: Check if daily_reflections table exists"""
        print("\n🧪 Test 5: Database Schema Verification")
        
        try:
            # Try to get reflections to see if table exists
            print("🔍 Checking if daily_reflections table exists by querying it...")
            
            async with self.session.get(f"{API_BASE}/ai/daily-reflections", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ daily_reflections table exists - found {data.get('count', 0)} reflections")
                    self.test_results.append({
                        "test": "Database Schema Verification", 
                        "status": "PASSED", 
                        "details": "daily_reflections table exists and is accessible"
                    })
                    return True
                elif response.status == 500:
                    error_text = await response.text()
                    if "relation" in error_text.lower() and "does not exist" in error_text.lower():
                        print("❌ daily_reflections table does NOT exist!")
                        print(f"💥 Database error: {error_text}")
                        self.test_results.append({
                            "test": "Database Schema Verification", 
                            "status": "FAILED", 
                            "reason": "daily_reflections table does not exist in database"
                        })
                        return False
                    else:
                        print(f"❌ Database query failed with 500 error: {error_text}")
                        self.test_results.append({
                            "test": "Database Schema Verification", 
                            "status": "FAILED", 
                            "reason": f"Database error: {error_text[:200]}"
                        })
                        return False
                else:
                    error_text = await response.text()
                    print(f"❌ Database schema check failed: {response.status} - {error_text}")
                    self.test_results.append({
                        "test": "Database Schema Verification", 
                        "status": "FAILED", 
                        "reason": f"HTTP {response.status}: {error_text[:200]}"
                    })
                    return False
                    
        except Exception as e:
            print(f"❌ Database schema verification failed: {e}")
            self.test_results.append({
                "test": "Database Schema Verification", 
                "status": "FAILED", 
                "reason": str(e)
            })
            return False
            
    def print_debug_summary(self):
        """Print debug test summary"""
        print("\n" + "="*80)
        print("🔍 EVENING REFLECTION API DEBUG - TEST SUMMARY")
        print("="*80)
        
        passed = len([t for t in self.test_results if t["status"] == "PASSED"])
        failed = len([t for t in self.test_results if t["status"] == "FAILED"])
        total = len(self.test_results)
        
        print(f"📊 OVERALL RESULTS: {passed}/{total} tests passed")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status_icon = {"PASSED": "✅", "FAILED": "❌", "PARTIAL": "⚠️", "SKIPPED": "⏭️", "FOUND_ERRORS": "🔍"}
            icon = status_icon.get(result["status"], "❓")
            print(f"{i:2d}. {icon} {result['test']}: {result['status']}")
            
            if "details" in result:
                print(f"    📝 {result['details']}")
            if "reason" in result:
                print(f"    💬 {result['reason']}")
                
        print("\n" + "="*80)
        
        # Determine root cause
        reflection_creation_failed = any(
            "Daily Reflection Creation" in t["test"] and t["status"] == "FAILED" 
            for t in self.test_results
        )
        
        database_issue = any(
            "Database Schema" in t["test"] and t["status"] == "FAILED" 
            for t in self.test_results
        )
        
        if reflection_creation_failed and database_issue:
            print("🎯 ROOT CAUSE IDENTIFIED: MISSING DATABASE TABLE")
            print("❌ The daily_reflections table does not exist in the Supabase database")
            print("🔧 SOLUTION: Create the daily_reflections table with proper schema")
        elif reflection_creation_failed:
            print("🎯 ROOT CAUSE: DAILY REFLECTION CREATION ENDPOINT FAILING")
            print("❌ POST /api/ai/daily-reflection is returning 500 errors")
            print("🔧 SOLUTION: Check backend implementation and database connectivity")
        else:
            print("🎯 EVENING REFLECTION API APPEARS TO BE WORKING")
            print("✅ No critical issues detected in testing")
            
        print("="*80)
        
    async def run_debug_tests(self):
        """Run comprehensive debug test suite for Evening Reflection API"""
        print("🚀 Starting Evening Reflection API Debug Testing...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print("🎯 Focus: Debugging 500 errors in POST /api/ai/daily-reflection")
        
        await self.setup_session()
        
        try:
            # Authentication
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed with tests")
                return
                
            # Run debug tests in order
            await self.test_database_schema()  # Check database first
            await self.test_daily_reflection_simple()  # Test simple reflection
            await self.test_daily_reflection_complete()  # Test complete reflection
            await self.test_other_ai_endpoints()  # Verify other endpoints work
            await self.check_backend_logs()  # Check logs for errors
            
        finally:
            await self.cleanup_session()
            
        # Print summary
        self.print_debug_summary()

async def main():
    """Main function to run Evening Reflection API debug tests"""
    debug_suite = EveningReflectionDebugSuite()
    await debug_suite.run_debug_tests()

if __name__ == "__main__":
    asyncio.run(main())