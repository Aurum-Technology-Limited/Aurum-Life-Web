#!/usr/bin/env python3
"""
Final Supabase Migration Test - 100% Completion Verification
Tests complete authentication and CRUD functionality
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8001/api"

class FinalSupabaseTest:
    def __init__(self):
        self.test_results = []
        self.auth_token = None
        self.test_user_email = "final.test@aurumlife.com"
        self.test_user_password = "FinalTest123!"
        self.created_entities = {}

    def log_test(self, test_name, status, details="", error=""):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASSED" else "❌" if status == "FAILED" else "⚠️"
        print(f"{status_emoji} {test_name}: {details}")
        if error:
            print(f"   Error: {error}")

    def test_1_health_check(self):
        """Test 1: Basic health check"""
        print("\n🧪 Test 1: Health Check")
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Health Check", "PASSED", f"Backend healthy: {data}")
                return True
            else:
                self.log_test("Health Check", "FAILED", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Health Check", "FAILED", error=str(e))
            return False

    def test_2_user_registration(self):
        """Test 2: User Registration (Supabase Auth)"""
        print("\n🧪 Test 2: User Registration")
        try:
            register_data = {
                "username": "finaltest123",
                "email": self.test_user_email,
                "first_name": "Final",
                "last_name": "Test",
                "password": self.test_user_password
            }
            
            response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
            if response.status_code in [200, 400]:  # 400 if user already exists
                if response.status_code == 200:
                    user_data = response.json()
                    self.created_entities['user_id'] = user_data['id']
                    self.log_test("User Registration", "PASSED", f"User created: {user_data['email']}")
                else:
                    self.log_test("User Registration", "PASSED", "User already exists (expected)")
                return True
            else:
                self.log_test("User Registration", "FAILED", f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("User Registration", "FAILED", error=str(e))
            return False

    def test_3_user_authentication(self):
        """Test 3: User Authentication"""
        print("\n🧪 Test 3: User Authentication")
        try:
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data["access_token"]
                self.log_test("User Authentication", "PASSED", "JWT token received")
                return True
            else:
                self.log_test("User Authentication", "FAILED", f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("User Authentication", "FAILED", error=str(e))
            return False

    def get_auth_headers(self):
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}

    def test_4_user_profile(self):
        """Test 4: User Profile Access"""
        print("\n🧪 Test 4: User Profile Access")
        try:
            response = requests.get(f"{BASE_URL}/auth/me", headers=self.get_auth_headers())
            if response.status_code == 200:
                user_data = response.json()
                self.log_test("User Profile", "PASSED", f"Profile retrieved: {user_data.get('email')}")
                return True
            else:
                self.log_test("User Profile", "FAILED", f"HTTP {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("User Profile", "FAILED", error=str(e))
            return False

    def test_5_pillar_crud(self):
        """Test 5: Pillar CRUD Operations"""
        print("\n🧪 Test 5: Pillar CRUD Operations")
        try:
            # Create Pillar
            pillar_data = {
                "name": "Health & Fitness",
                "description": "Physical and mental wellness",
                "icon": "💪",
                "color": "#4CAF50"
            }
            
            response = requests.post(f"{BASE_URL}/pillars", json=pillar_data, headers=self.get_auth_headers())
            if response.status_code == 200:
                pillar = response.json()
                pillar_id = pillar['id']
                self.created_entities['pillar_id'] = pillar_id
                
                # Read Pillar
                read_response = requests.get(f"{BASE_URL}/pillars/{pillar_id}", headers=self.get_auth_headers())
                if read_response.status_code == 200:
                    
                    # Update Pillar
                    update_data = {"description": "Updated description for health pillar"}
                    update_response = requests.put(f"{BASE_URL}/pillars/{pillar_id}", json=update_data, headers=self.get_auth_headers())
                    
                    if update_response.status_code == 200:
                        self.log_test("Pillar CRUD", "PASSED", "Create, Read, Update operations successful")
                        return True
                    
            self.log_test("Pillar CRUD", "FAILED", f"HTTP {response.status_code}", response.text)
            return False
        except Exception as e:
            self.log_test("Pillar CRUD", "FAILED", error=str(e))
            return False

    def test_6_hierarchical_operations(self):
        """Test 6: Hierarchical Operations (Area → Project → Task)"""
        print("\n🧪 Test 6: Hierarchical Operations")
        try:
            if 'pillar_id' not in self.created_entities:
                self.log_test("Hierarchical Operations", "FAILED", "No pillar available")
                return False
            
            pillar_id = self.created_entities['pillar_id']
            
            # Create Area
            area_data = {
                "name": "Exercise Routine",
                "pillar_id": pillar_id,
                "description": "Daily exercise activities"
            }
            
            area_response = requests.post(f"{BASE_URL}/areas", json=area_data, headers=self.get_auth_headers())
            if area_response.status_code == 200:
                area = area_response.json()
                area_id = area['id']
                self.created_entities['area_id'] = area_id
                
                # Create Project
                project_data = {
                    "name": "Morning Workout Plan",
                    "area_id": area_id,
                    "description": "30-minute morning exercise routine"
                }
                
                project_response = requests.post(f"{BASE_URL}/projects", json=project_data, headers=self.get_auth_headers())
                if project_response.status_code == 200:
                    project = project_response.json()
                    project_id = project['id']
                    self.created_entities['project_id'] = project_id
                    
                    # Create Task
                    task_data = {
                        "name": "10 Push-ups",
                        "project_id": project_id,
                        "description": "Daily push-up exercise"
                    }
                    
                    task_response = requests.post(f"{BASE_URL}/tasks", json=task_data, headers=self.get_auth_headers())
                    if task_response.status_code == 200:
                        task = task_response.json()
                        self.created_entities['task_id'] = task['id']
                        
                        self.log_test("Hierarchical Operations", "PASSED", "Full hierarchy (Pillar→Area→Project→Task) created")
                        return True
                        
            self.log_test("Hierarchical Operations", "FAILED", "Failed to create complete hierarchy")
            return False
        except Exception as e:
            self.log_test("Hierarchical Operations", "FAILED", error=str(e))
            return False

    def test_7_journal_operations(self):
        """Test 7: Journal Operations"""
        print("\n🧪 Test 7: Journal Operations")
        try:
            journal_data = {
                "title": "Supabase Migration Complete",
                "content": "Successfully migrated from MongoDB to Supabase! The system is working perfectly.",
                "mood": "excited"
            }
            
            response = requests.post(f"{BASE_URL}/journal", json=journal_data, headers=self.get_auth_headers())
            if response.status_code == 200:
                journal = response.json()
                self.created_entities['journal_id'] = journal['id']
                
                # Test journal retrieval
                get_response = requests.get(f"{BASE_URL}/journal", headers=self.get_auth_headers())
                if get_response.status_code == 200:
                    journals = get_response.json()
                    if len(journals) > 0:
                        self.log_test("Journal Operations", "PASSED", f"Created and retrieved journal entries: {len(journals)} entries")
                        return True
                        
            self.log_test("Journal Operations", "FAILED", f"HTTP {response.status_code}")
            return False
        except Exception as e:
            self.log_test("Journal Operations", "FAILED", error=str(e))
            return False

    def test_8_dashboard_and_stats(self):
        """Test 8: Dashboard and Statistics"""
        print("\n🧪 Test 8: Dashboard and Statistics")
        try:
            # Test dashboard
            dashboard_response = requests.get(f"{BASE_URL}/dashboard", headers=self.get_auth_headers())
            
            # Test stats
            stats_response = requests.get(f"{BASE_URL}/stats", headers=self.get_auth_headers())
            
            # Test insights
            insights_response = requests.get(f"{BASE_URL}/insights", headers=self.get_auth_headers())
            
            if (dashboard_response.status_code == 200 and 
                stats_response.status_code == 200 and 
                insights_response.status_code == 200):
                
                self.log_test("Dashboard and Stats", "PASSED", "All analytics endpoints working")
                return True
            else:
                self.log_test("Dashboard and Stats", "FAILED", "Some analytics endpoints failed")
                return False
                
        except Exception as e:
            self.log_test("Dashboard and Stats", "FAILED", error=str(e))
            return False

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 FINAL SUPABASE MIGRATION TEST - 100% COMPLETION VERIFICATION")
        print("=" * 70)
        
        tests = [
            self.test_1_health_check,
            self.test_2_user_registration,
            self.test_3_user_authentication,
            self.test_4_user_profile,
            self.test_5_pillar_crud,
            self.test_6_hierarchical_operations,
            self.test_7_journal_operations,
            self.test_8_dashboard_and_stats
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            time.sleep(0.5)  # Small delay between tests
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 FINAL TEST SUMMARY")
        print("=" * 70)
        
        success_rate = (passed / total) * 100
        print(f"✅ Tests Passed: {passed}/{total} ({success_rate:.1f}%)")
        
        if success_rate >= 100:
            print("🎉 SUPABASE MIGRATION 100% COMPLETE!")
            print("✅ All systems operational")
            print("✅ Authentication working")
            print("✅ CRUD operations functional")
            print("✅ Data hierarchy maintained")
            print("✅ Analytics and insights working")
        elif success_rate >= 85:
            print("✅ SUPABASE MIGRATION MOSTLY COMPLETE!")
            print("⚠️ Some minor issues need attention")
        else:
            print("❌ MIGRATION NEEDS MORE WORK")
            
        # Show failed tests
        failed_tests = [r for r in self.test_results if r['status'] == 'FAILED']
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"   - {test['test']}: {test['error']}")
        
        print(f"\n📝 Created test data: {len(self.created_entities)} entities")
        print(f"🔗 Test entities: {list(self.created_entities.keys())}")
        
        return success_rate >= 100

if __name__ == "__main__":
    tester = FinalSupabaseTest()
    success = tester.run_all_tests()
    exit(0 if success else 1)