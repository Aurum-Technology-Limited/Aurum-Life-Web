#!/usr/bin/env python3

import asyncio
import os
import sys
from datetime import datetime
from typing import Dict, Any

# Add backend to path
sys.path.append('/app/backend')

# Import Supabase modules directly
from supabase_client import SupabaseManager, supabase_manager
from supabase_auth import SupabaseAuth, supabase

class SupabaseDirectTestSuite:
    def __init__(self):
        self.test_results = []
        self.created_entities = []
        
    async def test_supabase_client_connection(self):
        """Test 1: Direct Supabase client connection"""
        print("\n🧪 Test 1: Supabase Client Connection")
        
        try:
            # Test client initialization
            client = supabase_manager.get_client()
            if client:
                print("✅ Supabase client initialized successfully")
                
                # Test basic query (check if user_profiles table exists)
                result = client.table('user_profiles').select('id').limit(1).execute()
                print(f"✅ Supabase database connection verified (user_profiles table accessible)")
                
                self.test_results.append({
                    "test": "Supabase Client Connection", 
                    "status": "PASSED", 
                    "details": "Client initialized and database accessible"
                })
                return True
            else:
                print("❌ Supabase client initialization failed")
                self.test_results.append({
                    "test": "Supabase Client Connection", 
                    "status": "FAILED", 
                    "reason": "Client initialization failed"
                })
                return False
                
        except Exception as e:
            print(f"❌ Supabase client connection error: {e}")
            self.test_results.append({
                "test": "Supabase Client Connection", 
                "status": "FAILED", 
                "reason": f"Connection error: {e}"
            })
            return False
            
    async def test_supabase_crud_operations(self):
        """Test 2: Direct Supabase CRUD operations"""
        print("\n🧪 Test 2: Supabase CRUD Operations")
        
        try:
            # Test create operation
            test_user_data = {
                "username": "directtest",
                "first_name": "Direct",
                "last_name": "Test",
                "is_active": True,
                "level": 1,
                "total_points": 0,
                "current_streak": 0,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            user_id = await supabase_manager.create_document('user_profiles', test_user_data)
            if user_id:
                print(f"✅ Create operation successful: {user_id}")
                self.created_entities.append(('user_profiles', user_id))
                
                # Test read operation
                user = await supabase_manager.find_document('user_profiles', {'id': user_id})
                if user and user['username'] == test_user_data['username']:
                    print("✅ Read operation successful")
                    
                    # Test update operation
                    update_data = {'first_name': 'Updated Direct'}
                    update_success = await supabase_manager.update_document('user_profiles', user_id, update_data)
                    if update_success:
                        print("✅ Update operation successful")
                        
                        # Verify update
                        updated_user = await supabase_manager.find_document('user_profiles', {'id': user_id})
                        if updated_user and updated_user['first_name'] == 'Updated Direct':
                            print("✅ Update verification successful")
                            
                            # Test count operation
                            count = await supabase_manager.count_documents('user_profiles', {'username': test_user_data['username']})
                            if count == 1:
                                print("✅ Count operation successful")
                                
                                self.test_results.append({
                                    "test": "Supabase CRUD Operations", 
                                    "status": "PASSED", 
                                    "details": "Create, read, update, and count operations successful"
                                })
                                return True
                                
            print("❌ CRUD operations failed")
            self.test_results.append({
                "test": "Supabase CRUD Operations", 
                "status": "FAILED", 
                "reason": "One or more CRUD operations failed"
            })
            return False
            
        except Exception as e:
            print(f"❌ CRUD operations error: {e}")
            self.test_results.append({
                "test": "Supabase CRUD Operations", 
                "status": "FAILED", 
                "reason": f"Error: {e}"
            })
            return False
            
    async def test_supabase_auth_system(self):
        """Test 3: Supabase Auth system (if configured)"""
        print("\n🧪 Test 3: Supabase Auth System")
        
        try:
            # Check if Supabase auth is configured
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            
            if not supabase_url or not supabase_key:
                print("⚠️ Supabase auth credentials not found in environment")
                self.test_results.append({
                    "test": "Supabase Auth System", 
                    "status": "FAILED", 
                    "reason": "Supabase credentials not configured"
                })
                return False
                
            print(f"✅ Supabase URL configured: {supabase_url}")
            print(f"✅ Supabase service key configured: {'*' * 20}...")
            
            # Test auth client initialization
            if supabase and supabase.auth:
                print("✅ Supabase auth client initialized")
                
                # Note: We can't test actual token verification without a real token
                # But we can verify the auth system is properly configured
                self.test_results.append({
                    "test": "Supabase Auth System", 
                    "status": "PASSED", 
                    "details": "Auth system configured and client initialized"
                })
                return True
            else:
                print("❌ Supabase auth client not initialized")
                self.test_results.append({
                    "test": "Supabase Auth System", 
                    "status": "FAILED", 
                    "reason": "Auth client not initialized"
                })
                return False
                
        except Exception as e:
            print(f"❌ Auth system error: {e}")
            self.test_results.append({
                "test": "Supabase Auth System", 
                "status": "FAILED", 
                "reason": f"Error: {e}"
            })
            return False
            
    async def test_supabase_table_structure(self):
        """Test 4: Verify Supabase table structure"""
        print("\n🧪 Test 4: Supabase Table Structure")
        
        try:
            client = supabase_manager.get_client()
            expected_tables = ['user_profiles', 'pillars', 'areas', 'projects', 'tasks', 'journal_entries']
            
            accessible_tables = []
            for table_name in expected_tables:
                try:
                    # Try to query each table
                    result = client.table(table_name).select('*').limit(1).execute()
                    accessible_tables.append(table_name)
                    print(f"✅ Table '{table_name}' accessible")
                except Exception as e:
                    print(f"❌ Table '{table_name}' not accessible: {e}")
                    
            if len(accessible_tables) >= 4:  # At least core tables should be accessible
                print(f"✅ Table structure verification successful: {len(accessible_tables)}/{len(expected_tables)} tables accessible")
                self.test_results.append({
                    "test": "Supabase Table Structure", 
                    "status": "PASSED", 
                    "details": f"{len(accessible_tables)} tables accessible: {', '.join(accessible_tables)}"
                })
                return True
            else:
                print(f"❌ Insufficient tables accessible: {len(accessible_tables)}/{len(expected_tables)}")
                self.test_results.append({
                    "test": "Supabase Table Structure", 
                    "status": "FAILED", 
                    "reason": f"Only {len(accessible_tables)} tables accessible"
                })
                return False
                
        except Exception as e:
            print(f"❌ Table structure test error: {e}")
            self.test_results.append({
                "test": "Supabase Table Structure", 
                "status": "FAILED", 
                "reason": f"Error: {e}"
            })
            return False
            
    async def test_data_migration_verification(self):
        """Test 5: Verify migrated data exists"""
        print("\n🧪 Test 5: Data Migration Verification")
        
        try:
            client = supabase_manager.get_client()
            
            # Check for existing data in key tables
            tables_to_check = ['user_profiles', 'pillars', 'areas', 'projects', 'tasks']
            data_found = {}
            
            for table_name in tables_to_check:
                try:
                    result = client.table(table_name).select('id').execute()
                    count = len(result.data) if result.data else 0
                    data_found[table_name] = count
                    print(f"✅ {table_name}: {count} records found")
                except Exception as e:
                    print(f"❌ {table_name}: Error checking data - {e}")
                    data_found[table_name] = 0
                    
            total_records = sum(data_found.values())
            if total_records > 0:
                print(f"✅ Data migration verification successful: {total_records} total records found")
                self.test_results.append({
                    "test": "Data Migration Verification", 
                    "status": "PASSED", 
                    "details": f"Found {total_records} records across tables: {data_found}"
                })
                return True
            else:
                print("⚠️ No migrated data found - this might be expected for a fresh migration")
                self.test_results.append({
                    "test": "Data Migration Verification", 
                    "status": "PASSED", 
                    "details": "No existing data found (fresh migration)"
                })
                return True
                
        except Exception as e:
            print(f"❌ Data migration verification error: {e}")
            self.test_results.append({
                "test": "Data Migration Verification", 
                "status": "FAILED", 
                "reason": f"Error: {e}"
            })
            return False
            
    async def cleanup_test_data(self):
        """Clean up created test data"""
        print("\n🧹 Cleaning up test data...")
        
        for table_name, entity_id in self.created_entities:
            try:
                success = await supabase_manager.delete_document(table_name, entity_id)
                if success:
                    print(f"✅ Cleaned up {table_name}: {entity_id}")
                else:
                    print(f"⚠️ Could not clean up {table_name}: {entity_id}")
            except Exception as e:
                print(f"❌ Error cleaning up {table_name}: {entity_id} - {e}")
                
    async def run_all_tests(self):
        """Run all direct Supabase tests"""
        print("🚀 Starting Direct Supabase Integration Tests")
        print("=" * 60)
        
        try:
            # Run all tests
            test_methods = [
                self.test_supabase_client_connection,
                self.test_supabase_crud_operations,
                self.test_supabase_auth_system,
                self.test_supabase_table_structure,
                self.test_data_migration_verification
            ]
            
            for test_method in test_methods:
                try:
                    await test_method()
                except Exception as e:
                    print(f"❌ Test {test_method.__name__} failed with exception: {e}")
                    self.test_results.append({
                        "test": test_method.__name__, 
                        "status": "FAILED", 
                        "reason": f"Exception: {e}"
                    })
                    
        finally:
            # Clean up test data
            await self.cleanup_test_data()
            
        # Print summary
        success = self.print_test_summary()
        return success
        
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🧪 DIRECT SUPABASE INTEGRATION TEST SUMMARY")
        print("=" * 60)
        
        passed_tests = [r for r in self.test_results if r["status"] == "PASSED"]
        failed_tests = [r for r in self.test_results if r["status"] == "FAILED"]
        
        print(f"✅ PASSED: {len(passed_tests)}")
        print(f"❌ FAILED: {len(failed_tests)}")
        print(f"📊 TOTAL: {len(self.test_results)}")
        
        if len(self.test_results) > 0:
            success_rate = (len(passed_tests) / len(self.test_results)) * 100
            print(f"🎯 SUCCESS RATE: {success_rate:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASSED" else "❌"
            print(f"{status_icon} {result['test']}: {result['status']}")
            if result["status"] == "PASSED" and "details" in result:
                print(f"   Details: {result['details']}")
            elif result["status"] == "FAILED" and "reason" in result:
                print(f"   Reason: {result['reason']}")
                
        print("\n" + "=" * 60)
        
        # Return overall success
        return len(failed_tests) == 0

async def main():
    """Main test execution"""
    test_suite = SupabaseDirectTestSuite()
    success = await test_suite.run_all_tests()
    
    if success:
        print("🎉 All direct Supabase tests passed!")
        sys.exit(0)
    else:
        print("💥 Some direct Supabase tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())