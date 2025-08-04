#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from typing import Dict, Any, List

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://1b0a62f2-f882-476f-afb6-6747b2b238a1.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class ComprehensiveBackendReviewTest:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_results = []
        self.marc_user_email = "marc.alleyne@aurumtechnologyltd.com"
        self.marc_user_password = "password123"
        self.new_test_user_email = "backend.review.test@aurumlife.com"
        self.new_test_user_password = "TestPass123!"
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()
            
    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.auth_token}"}
        
    async def test_authentication_system(self):
        """Test 1: Authentication System - Test user login/registration with both new users and the fixed Marc user"""
        print("\n🧪 Test 1: Authentication System")
        
        try:
            # Test 1a: Marc user login (fixed user)
            print("  Testing Marc user login...")
            login_data = {
                "email": self.marc_user_email,
                "password": self.marc_user_password
            }
            
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data["access_token"]
                    print("  ✅ Marc user login successful")
                    
                    # Test auth/me endpoint
                    async with self.session.get(f"{API_BASE}/auth/me", headers=self.get_auth_headers()) as me_response:
                        if me_response.status == 200:
                            user_data = await me_response.json()
                            if user_data.get("email") == self.marc_user_email:
                                print("  ✅ Marc user authentication verification successful")
                            else:
                                print("  ❌ Marc user data mismatch")
                                self.test_results.append({"test": "Marc user auth verification", "status": "FAILED", "reason": "User data mismatch"})
                                return
                        else:
                            print(f"  ❌ Marc user auth verification failed: {me_response.status}")
                            self.test_results.append({"test": "Marc user auth verification", "status": "FAILED", "reason": f"HTTP {me_response.status}"})
                            return
                else:
                    print(f"  ❌ Marc user login failed: {response.status}")
                    error_text = await response.text()
                    print(f"  Error: {error_text}")
                    self.test_results.append({"test": "Marc user login", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    return
                    
            # Test 1b: New user registration and login
            print("  Testing new user registration...")
            register_data = {
                "username": "backendrviewtest",
                "email": self.new_test_user_email,
                "first_name": "Backend",
                "last_name": "ReviewTest",
                "password": self.new_test_user_password
            }
            
            async with self.session.post(f"{API_BASE}/auth/register", json=register_data) as response:
                if response.status in [200, 400]:  # 400 if user already exists
                    print("  ✅ New user registration successful (or already exists)")
                    
                    # Test new user login
                    new_login_data = {
                        "email": self.new_test_user_email,
                        "password": self.new_test_user_password
                    }
                    
                    async with self.session.post(f"{API_BASE}/auth/login", json=new_login_data) as login_response:
                        if login_response.status == 200:
                            login_result = await login_response.json()
                            new_user_token = login_result["access_token"]
                            print("  ✅ New user login successful")
                            
                            # Verify new user auth
                            new_user_headers = {"Authorization": f"Bearer {new_user_token}"}
                            async with self.session.get(f"{API_BASE}/auth/me", headers=new_user_headers) as new_me_response:
                                if new_me_response.status == 200:
                                    new_user_data = await new_me_response.json()
                                    if new_user_data.get("email") == self.new_test_user_email:
                                        print("  ✅ New user authentication verification successful")
                                        self.test_results.append({"test": "Authentication System", "status": "PASSED", "details": "Both Marc user and new user authentication working"})
                                    else:
                                        print("  ❌ New user data mismatch")
                                        self.test_results.append({"test": "New user auth verification", "status": "FAILED", "reason": "User data mismatch"})
                                else:
                                    print(f"  ❌ New user auth verification failed: {new_me_response.status}")
                                    self.test_results.append({"test": "New user auth verification", "status": "FAILED", "reason": f"HTTP {new_me_response.status}"})
                        else:
                            print(f"  ❌ New user login failed: {login_response.status}")
                            error_text = await login_response.text()
                            print(f"  Error: {error_text}")
                            self.test_results.append({"test": "New user login", "status": "FAILED", "reason": f"HTTP {login_response.status}"})
                else:
                    print(f"  ❌ New user registration failed: {response.status}")
                    error_text = await response.text()
                    print(f"  Error: {error_text}")
                    self.test_results.append({"test": "New user registration", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    
        except Exception as e:
            print(f"  ❌ Authentication system test failed: {e}")
            self.test_results.append({"test": "Authentication System", "status": "FAILED", "reason": str(e)})
            
    async def test_dashboard_functionality(self):
        """Test 2: Dashboard Functionality - Verify /api/dashboard endpoint works without timeout errors"""
        print("\n🧪 Test 2: Dashboard Functionality")
        
        if not self.auth_token:
            print("  ❌ No authentication token available")
            self.test_results.append({"test": "Dashboard Functionality", "status": "FAILED", "reason": "No authentication token"})
            return
            
        try:
            print("  Testing dashboard endpoint...")
            async with self.session.get(f"{API_BASE}/dashboard", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    dashboard_data = await response.json()
                    print("  ✅ Dashboard endpoint successful")
                    
                    # Verify required dashboard fields
                    required_fields = ["user_stats", "recent_activities", "upcoming_tasks"]
                    missing_fields = []
                    for field in required_fields:
                        if field not in dashboard_data:
                            missing_fields.append(field)
                            
                    if missing_fields:
                        print(f"  ⚠️ Dashboard missing fields: {missing_fields}")
                        self.test_results.append({"test": "Dashboard Functionality", "status": "PARTIAL", "details": f"Missing fields: {missing_fields}"})
                    else:
                        print("  ✅ Dashboard contains all required fields")
                        self.test_results.append({"test": "Dashboard Functionality", "status": "PASSED", "details": "Dashboard loads successfully with all required data"})
                        
                elif response.status == 500:
                    error_text = await response.text()
                    print(f"  ❌ Dashboard endpoint returned 500 error: {error_text}")
                    self.test_results.append({"test": "Dashboard Functionality", "status": "FAILED", "reason": f"500 Internal Server Error: {error_text}"})
                else:
                    print(f"  ❌ Dashboard endpoint failed: {response.status}")
                    error_text = await response.text()
                    print(f"  Error: {error_text}")
                    self.test_results.append({"test": "Dashboard Functionality", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    
        except Exception as e:
            print(f"  ❌ Dashboard functionality test failed: {e}")
            self.test_results.append({"test": "Dashboard Functionality", "status": "FAILED", "reason": str(e)})
            
    async def test_core_crud_operations(self):
        """Test 3: Core CRUD Operations - Test pillars, areas, projects, and tasks endpoints"""
        print("\n🧪 Test 3: Core CRUD Operations")
        
        if not self.auth_token:
            print("  ❌ No authentication token available")
            self.test_results.append({"test": "Core CRUD Operations", "status": "FAILED", "reason": "No authentication token"})
            return
            
        crud_results = []
        
        try:
            # Test 3a: Pillars CRUD
            print("  Testing Pillars CRUD...")
            async with self.session.get(f"{API_BASE}/pillars", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    pillars = await response.json()
                    print(f"  ✅ Pillars GET successful - Found {len(pillars)} pillars")
                    crud_results.append("Pillars GET: PASSED")
                else:
                    print(f"  ❌ Pillars GET failed: {response.status}")
                    crud_results.append(f"Pillars GET: FAILED ({response.status})")
                    
            # Test 3b: Areas CRUD
            print("  Testing Areas CRUD...")
            async with self.session.get(f"{API_BASE}/areas", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    areas = await response.json()
                    print(f"  ✅ Areas GET successful - Found {len(areas)} areas")
                    crud_results.append("Areas GET: PASSED")
                else:
                    print(f"  ❌ Areas GET failed: {response.status}")
                    crud_results.append(f"Areas GET: FAILED ({response.status})")
                    
            # Test 3c: Projects CRUD (Critical - this was failing)
            print("  Testing Projects CRUD...")
            async with self.session.get(f"{API_BASE}/projects", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    projects = await response.json()
                    print(f"  ✅ Projects GET successful - Found {len(projects)} projects")
                    crud_results.append("Projects GET: PASSED")
                elif response.status == 500:
                    error_text = await response.text()
                    print(f"  ❌ Projects GET returned 500 error: {error_text}")
                    crud_results.append(f"Projects GET: FAILED (500 - {error_text[:100]})")
                else:
                    print(f"  ❌ Projects GET failed: {response.status}")
                    error_text = await response.text()
                    crud_results.append(f"Projects GET: FAILED ({response.status})")
                    
            # Test 3d: Tasks CRUD
            print("  Testing Tasks CRUD...")
            async with self.session.get(f"{API_BASE}/tasks", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    tasks = await response.json()
                    print(f"  ✅ Tasks GET successful - Found {len(tasks)} tasks")
                    crud_results.append("Tasks GET: PASSED")
                else:
                    print(f"  ❌ Tasks GET failed: {response.status}")
                    crud_results.append(f"Tasks GET: FAILED ({response.status})")
                    
            # Determine overall CRUD status
            failed_operations = [op for op in crud_results if "FAILED" in op]
            if not failed_operations:
                self.test_results.append({"test": "Core CRUD Operations", "status": "PASSED", "details": "All CRUD operations successful"})
            else:
                self.test_results.append({"test": "Core CRUD Operations", "status": "FAILED", "details": f"Failed operations: {failed_operations}"})
                
        except Exception as e:
            print(f"  ❌ Core CRUD operations test failed: {e}")
            self.test_results.append({"test": "Core CRUD Operations", "status": "FAILED", "reason": str(e)})
            
    async def test_user_stats_system(self):
        """Test 4: User Stats System - Verify user_stats creation and updates work without foreign key constraint violations"""
        print("\n🧪 Test 4: User Stats System")
        
        if not self.auth_token:
            print("  ❌ No authentication token available")
            self.test_results.append({"test": "User Stats System", "status": "FAILED", "reason": "No authentication token"})
            return
            
        try:
            print("  Testing user stats retrieval...")
            async with self.session.get(f"{API_BASE}/stats", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    stats_data = await response.json()
                    print("  ✅ User stats retrieval successful")
                    
                    # Check for required stats fields
                    required_stats = ["total_tasks", "completed_tasks", "active_projects", "total_points"]
                    missing_stats = []
                    for stat in required_stats:
                        if stat not in stats_data:
                            missing_stats.append(stat)
                            
                    if missing_stats:
                        print(f"  ⚠️ Missing stats fields: {missing_stats}")
                        self.test_results.append({"test": "User Stats System", "status": "PARTIAL", "details": f"Missing fields: {missing_stats}"})
                    else:
                        print("  ✅ User stats contain all required fields")
                        
                        # Test stats update
                        print("  Testing user stats update...")
                        async with self.session.post(f"{API_BASE}/stats/update", headers=self.get_auth_headers()) as update_response:
                            if update_response.status == 200:
                                updated_stats = await update_response.json()
                                print("  ✅ User stats update successful")
                                self.test_results.append({"test": "User Stats System", "status": "PASSED", "details": "Stats retrieval and update working"})
                            else:
                                print(f"  ❌ User stats update failed: {update_response.status}")
                                error_text = await update_response.text()
                                self.test_results.append({"test": "User Stats System", "status": "FAILED", "reason": f"Update failed: {update_response.status}"})
                                
                elif response.status == 500:
                    error_text = await response.text()
                    print(f"  ❌ User stats returned 500 error: {error_text}")
                    if "foreign key constraint" in error_text.lower():
                        self.test_results.append({"test": "User Stats System", "status": "FAILED", "reason": "Foreign key constraint violation detected"})
                    else:
                        self.test_results.append({"test": "User Stats System", "status": "FAILED", "reason": f"500 error: {error_text}"})
                else:
                    print(f"  ❌ User stats retrieval failed: {response.status}")
                    self.test_results.append({"test": "User Stats System", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    
        except Exception as e:
            print(f"  ❌ User stats system test failed: {e}")
            self.test_results.append({"test": "User Stats System", "status": "FAILED", "reason": str(e)})
            
    async def test_ai_coach_service(self):
        """Test 5: AI Coach Service - Test /api/ai_coach/today endpoint to ensure no more NoneType errors"""
        print("\n🧪 Test 5: AI Coach Service")
        
        if not self.auth_token:
            print("  ❌ No authentication token available")
            self.test_results.append({"test": "AI Coach Service", "status": "FAILED", "reason": "No authentication token"})
            return
            
        try:
            print("  Testing AI Coach today endpoint...")
            
            # First check if the endpoint exists
            async with self.session.get(f"{API_BASE}/today", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    today_data = await response.json()
                    print("  ✅ Today view endpoint successful")
                    
                    # Check if AI Coach data is included
                    if "ai_priorities" in today_data or "ai_suggestions" in today_data:
                        print("  ✅ AI Coach data present in today view")
                        self.test_results.append({"test": "AI Coach Service", "status": "PASSED", "details": "AI Coach data available in today view"})
                    else:
                        print("  ⚠️ AI Coach data not found in today view")
                        self.test_results.append({"test": "AI Coach Service", "status": "PARTIAL", "details": "Today view works but no AI Coach data"})
                        
                elif response.status == 500:
                    error_text = await response.text()
                    print(f"  ❌ Today view returned 500 error: {error_text}")
                    if "nonetype" in error_text.lower() or "none" in error_text.lower():
                        self.test_results.append({"test": "AI Coach Service", "status": "FAILED", "reason": "NoneType error detected in AI Coach"})
                    else:
                        self.test_results.append({"test": "AI Coach Service", "status": "FAILED", "reason": f"500 error: {error_text}"})
                else:
                    print(f"  ❌ Today view failed: {response.status}")
                    self.test_results.append({"test": "AI Coach Service", "status": "FAILED", "reason": f"HTTP {response.status}"})
                    
        except Exception as e:
            print(f"  ❌ AI Coach service test failed: {e}")
            self.test_results.append({"test": "AI Coach Service", "status": "FAILED", "reason": str(e)})
            
    async def test_database_queries(self):
        """Test 6: Database Queries - Verify all MongoDB syntax has been eliminated and queries work with Supabase"""
        print("\n🧪 Test 6: Database Queries (MongoDB to Supabase Migration)")
        
        if not self.auth_token:
            print("  ❌ No authentication token available")
            self.test_results.append({"test": "Database Queries", "status": "FAILED", "reason": "No authentication token"})
            return
            
        try:
            # Test various endpoints that would use database queries
            endpoints_to_test = [
                ("/pillars", "Pillars"),
                ("/areas", "Areas"), 
                ("/projects", "Projects"),
                ("/tasks", "Tasks"),
                ("/journal", "Journal"),
                ("/stats", "Stats")
            ]
            
            mongodb_errors = []
            supabase_success = []
            
            for endpoint, name in endpoints_to_test:
                print(f"  Testing {name} database queries...")
                async with self.session.get(f"{API_BASE}{endpoint}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print(f"  ✅ {name} queries successful")
                        supabase_success.append(name)
                    elif response.status == 500:
                        error_text = await response.text()
                        if any(mongo_term in error_text.lower() for mongo_term in ["mongodb", "mongo", "$", "objectid", "bson"]):
                            print(f"  ❌ {name} contains MongoDB syntax: {error_text[:100]}")
                            mongodb_errors.append(f"{name}: MongoDB syntax detected")
                        else:
                            print(f"  ❌ {name} database error (non-MongoDB): {error_text[:100]}")
                            mongodb_errors.append(f"{name}: Database error")
                    else:
                        print(f"  ❌ {name} query failed: {response.status}")
                        mongodb_errors.append(f"{name}: HTTP {response.status}")
                        
            if not mongodb_errors:
                self.test_results.append({"test": "Database Queries", "status": "PASSED", "details": f"All queries working with Supabase: {supabase_success}"})
            else:
                self.test_results.append({"test": "Database Queries", "status": "FAILED", "details": f"Issues found: {mongodb_errors}"})
                
        except Exception as e:
            print(f"  ❌ Database queries test failed: {e}")
            self.test_results.append({"test": "Database Queries", "status": "FAILED", "reason": str(e)})
            
    async def test_error_handling(self):
        """Test 7: Error Handling - Confirm missing tables are handled gracefully"""
        print("\n🧪 Test 7: Error Handling")
        
        if not self.auth_token:
            print("  ❌ No authentication token available")
            self.test_results.append({"test": "Error Handling", "status": "FAILED", "reason": "No authentication token"})
            return
            
        try:
            # Test endpoints that might reference missing tables
            potentially_missing_tables = [
                ("/courses", "user_course_progress"),
                ("/achievements", "user_badges"),
                ("/notifications", "notifications")
            ]
            
            graceful_errors = []
            server_crashes = []
            
            for endpoint, table_name in potentially_missing_tables:
                print(f"  Testing {table_name} error handling...")
                async with self.session.get(f"{API_BASE}{endpoint}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print(f"  ✅ {table_name} endpoint working")
                        graceful_errors.append(f"{table_name}: Working")
                    elif response.status in [404, 400]:
                        print(f"  ✅ {table_name} gracefully handled with {response.status}")
                        graceful_errors.append(f"{table_name}: Graceful {response.status}")
                    elif response.status == 500:
                        error_text = await response.text()
                        if "table" in error_text.lower() and "not" in error_text.lower():
                            print(f"  ❌ {table_name} server crash on missing table")
                            server_crashes.append(f"{table_name}: Server crash on missing table")
                        else:
                            print(f"  ⚠️ {table_name} 500 error (not table-related)")
                            graceful_errors.append(f"{table_name}: 500 error (non-table)")
                    else:
                        print(f"  ⚠️ {table_name} unexpected status: {response.status}")
                        graceful_errors.append(f"{table_name}: Status {response.status}")
                        
            if not server_crashes:
                self.test_results.append({"test": "Error Handling", "status": "PASSED", "details": f"All errors handled gracefully: {graceful_errors}"})
            else:
                self.test_results.append({"test": "Error Handling", "status": "FAILED", "details": f"Server crashes detected: {server_crashes}"})
                
        except Exception as e:
            print(f"  ❌ Error handling test failed: {e}")
            self.test_results.append({"test": "Error Handling", "status": "FAILED", "reason": str(e)})
            
    async def test_archive_functionality(self):
        """Test 8: Archive Functionality - Test that all sections work without missing archived column errors"""
        print("\n🧪 Test 8: Archive Functionality")
        
        if not self.auth_token:
            print("  ❌ No authentication token available")
            self.test_results.append({"test": "Archive Functionality", "status": "FAILED", "reason": "No authentication token"})
            return
            
        try:
            # Test endpoints with archive functionality
            archive_endpoints = [
                ("/pillars?include_archived=true", "Pillars"),
                ("/areas?include_archived=true", "Areas"),
                ("/projects?include_archived=true", "Projects")
            ]
            
            archive_success = []
            archive_errors = []
            
            for endpoint, name in archive_endpoints:
                print(f"  Testing {name} archive functionality...")
                async with self.session.get(f"{API_BASE}{endpoint}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"  ✅ {name} archive query successful")
                        archive_success.append(name)
                    elif response.status == 500:
                        error_text = await response.text()
                        if "archived" in error_text.lower() and ("column" in error_text.lower() or "field" in error_text.lower()):
                            print(f"  ❌ {name} missing archived column: {error_text[:100]}")
                            archive_errors.append(f"{name}: Missing archived column")
                        else:
                            print(f"  ❌ {name} archive error (non-column): {error_text[:100]}")
                            archive_errors.append(f"{name}: Archive error")
                    else:
                        print(f"  ❌ {name} archive query failed: {response.status}")
                        archive_errors.append(f"{name}: HTTP {response.status}")
                        
            if not archive_errors:
                self.test_results.append({"test": "Archive Functionality", "status": "PASSED", "details": f"All archive queries working: {archive_success}"})
            else:
                self.test_results.append({"test": "Archive Functionality", "status": "FAILED", "details": f"Archive issues: {archive_errors}"})
                
        except Exception as e:
            print(f"  ❌ Archive functionality test failed: {e}")
            self.test_results.append({"test": "Archive Functionality", "status": "FAILED", "reason": str(e)})
            
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🎯 COMPREHENSIVE BACKEND REVIEW TEST - SUMMARY")
        print("="*80)
        
        passed = len([t for t in self.test_results if t["status"] == "PASSED"])
        failed = len([t for t in self.test_results if t["status"] == "FAILED"])
        partial = len([t for t in self.test_results if t["status"] == "PARTIAL"])
        total = len(self.test_results)
        
        print(f"📊 OVERALL RESULTS: {passed}/{total} tests passed")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️ Partial: {partial}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status_icon = {"PASSED": "✅", "FAILED": "❌", "PARTIAL": "⚠️"}
            icon = status_icon.get(result["status"], "❓")
            print(f"{i:2d}. {icon} {result['test']}: {result['status']}")
            
            if "details" in result:
                print(f"    📝 {result['details']}")
            if "reason" in result:
                print(f"    💬 {result['reason']}")
                
        print("\n" + "="*80)
        
        # Critical issues summary
        critical_failures = [r for r in self.test_results if r["status"] == "FAILED"]
        if critical_failures:
            print("🚨 CRITICAL ISSUES IDENTIFIED:")
            for failure in critical_failures:
                print(f"   ❌ {failure['test']}: {failure.get('reason', 'Unknown error')}")
        else:
            print("🎉 NO CRITICAL ISSUES IDENTIFIED!")
            
        print("="*80)
        
    async def run_all_tests(self):
        """Run all comprehensive backend review tests"""
        print("🚀 Starting Comprehensive Backend Review Testing...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        
        await self.setup_session()
        
        try:
            # Run all tests in sequence
            await self.test_authentication_system()
            await self.test_dashboard_functionality()
            await self.test_core_crud_operations()
            await self.test_user_stats_system()
            await self.test_ai_coach_service()
            await self.test_database_queries()
            await self.test_error_handling()
            await self.test_archive_functionality()
            
        finally:
            await self.cleanup_session()
            
        # Print summary
        self.print_test_summary()

async def main():
    """Main test execution"""
    test_suite = ComprehensiveBackendReviewTest()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())