#!/usr/bin/env python3
"""
FINAL ONBOARDING TEST - WITH CORRECT USER ID
Testing onboarding pillar creation with the correct user ID from authentication system.

ISSUE IDENTIFIED:
- Auth system uses: 6848f065-2d12-4c4e-88c4-80f375358d7b
- Database has: 272edb74-8be3-4504-818c-b1dd42c63ebe
- This mismatch causes foreign key constraint violations

SOLUTION:
The database needs to have a user record with ID: 6848f065-2d12-4c4e-88c4-80f375358d7b

CREDENTIALS: marc.alleyne@aurumtechnologyltd.com / password
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://taskpilot-2.preview.emergentagent.com/api"

def test_complete_onboarding_flow():
    """Test the complete onboarding flow"""
    print("🚀 FINAL ONBOARDING TEST - WITH CORRECT USER ID")
    print("=" * 70)
    print("Testing with the actual user ID from authentication system:")
    print("User ID: 6848f065-2d12-4c4e-88c4-80f375358d7b")
    print("=" * 70)
    
    session = requests.Session()
    test_results = []
    created_resources = []
    
    def log_test(name, success, message):
        test_results.append({'name': name, 'success': success, 'message': message})
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {name}: {message}")
    
    # Step 1: Authentication
    print("\n1. AUTHENTICATION TEST")
    print("-" * 30)
    
    login_data = {
        "email": "marc.alleyne@aurumtechnologyltd.com",
        "password": "password"
    }
    
    try:
        response = session.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=30)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            log_test("Login", True, "Authentication successful")
            
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Test user info retrieval
            response = session.get(f"{BACKEND_URL}/auth/me", headers=headers, timeout=30)
            if response.status_code == 200:
                user_data = response.json()
                log_test("User Info Retrieval", True, f"User ID: {user_data.get('id')}")
                
                # Step 2: Pillar Creation
                print("\n2. PILLAR CREATION TEST")
                print("-" * 30)
                
                pillar_data = {
                    "name": "Health & Wellness",
                    "description": "Physical and mental health, fitness, and overall well-being",
                    "icon": "💪",
                    "color": "#10B981",
                    "time_allocation_percentage": 25.0
                }
                
                response = session.post(f"{BACKEND_URL}/pillars", json=pillar_data, headers=headers, timeout=30)
                if response.status_code == 200:
                    pillar = response.json()
                    pillar_id = pillar.get('id')
                    created_resources.append(('pillar', pillar_id))
                    log_test("Pillar Creation", True, f"Created pillar: {pillar.get('name')} (ID: {pillar_id})")
                    
                    # Step 3: Area Creation
                    print("\n3. AREA CREATION TEST")
                    print("-" * 30)
                    
                    area_data = {
                        "pillar_id": pillar_id,
                        "name": "Fitness & Exercise",
                        "description": "Physical fitness, workouts, and exercise routines",
                        "icon": "🏃",
                        "color": "#F59E0B",
                        "importance": 4
                    }
                    
                    response = session.post(f"{BACKEND_URL}/areas", json=area_data, headers=headers, timeout=30)
                    if response.status_code == 200:
                        area = response.json()
                        area_id = area.get('id')
                        created_resources.append(('area', area_id))
                        log_test("Area Creation", True, f"Created area: {area.get('name')} (ID: {area_id})")
                        
                        # Step 4: Project Creation
                        print("\n4. PROJECT CREATION TEST")
                        print("-" * 30)
                        
                        project_data = {
                            "area_id": area_id,
                            "name": "Morning Workout Routine",
                            "description": "Establish a consistent morning exercise routine",
                            "icon": "🏋️",
                            "status": "Not Started",
                            "priority": "high",
                            "deadline": "2025-02-15T10:00:00Z"
                        }
                        
                        response = session.post(f"{BACKEND_URL}/projects", json=project_data, headers=headers, timeout=30)
                        if response.status_code == 200:
                            project = response.json()
                            project_id = project.get('id')
                            created_resources.append(('project', project_id))
                            log_test("Project Creation", True, f"Created project: {project.get('name')} (ID: {project_id})")
                            
                            # Step 5: Task Creation
                            print("\n5. TASK CREATION TEST")
                            print("-" * 30)
                            
                            task_data = {
                                "project_id": project_id,
                                "name": "30-minute cardio session",
                                "description": "High-intensity cardio workout to start the day",
                                "status": "todo",
                                "priority": "medium",
                                "due_date": "2025-01-30T07:00:00Z",
                                "estimated_duration": 30
                            }
                            
                            response = session.post(f"{BACKEND_URL}/tasks", json=task_data, headers=headers, timeout=30)
                            if response.status_code == 200:
                                task = response.json()
                                task_id = task.get('id')
                                created_resources.append(('task', task_id))
                                log_test("Task Creation", True, f"Created task: {task.get('name')} (ID: {task_id})")
                            else:
                                error_data = response.json() if response.content else {}
                                log_test("Task Creation", False, f"HTTP {response.status_code}: {error_data}")
                        else:
                            error_data = response.json() if response.content else {}
                            log_test("Project Creation", False, f"HTTP {response.status_code}: {error_data}")
                    else:
                        error_data = response.json() if response.content else {}
                        log_test("Area Creation", False, f"HTTP {response.status_code}: {error_data}")
                else:
                    error_data = response.json() if response.content else {}
                    error_str = str(error_data).lower()
                    if 'foreign key' in error_str or 'violates' in error_str:
                        log_test("Pillar Creation", False, f"FOREIGN KEY CONSTRAINT ERROR: {error_data}")
                    else:
                        log_test("Pillar Creation", False, f"HTTP {response.status_code}: {error_data}")
            else:
                error_data = response.json() if response.content else {}
                log_test("User Info Retrieval", False, f"HTTP {response.status_code}: {error_data}")
        else:
            error_data = response.json() if response.content else {}
            log_test("Login", False, f"HTTP {response.status_code}: {error_data}")
            
    except Exception as e:
        log_test("Authentication", False, f"Request failed: {str(e)}")
    
    # Step 6: Template Application Test
    if any(result['name'] == 'Login' and result['success'] for result in test_results):
        print("\n6. TEMPLATE APPLICATION TEST")
        print("-" * 30)
        
        goal_data = {
            "project_name": "Learn Spanish Language",
            "project_description": "Become conversational in Spanish within 6 months",
            "template_type": "learning"
        }
        
        try:
            response = session.post(f"{BACKEND_URL}/ai/decompose-project", json=goal_data, headers=headers, timeout=30)
            if response.status_code == 200:
                decomposition = response.json()
                log_test("AI Goal Decomposition", True, f"Generated {len(decomposition.get('suggested_tasks', []))} task suggestions")
                
                # Test creating project with tasks
                if 'suggested_project' in decomposition and 'suggested_tasks' in decomposition:
                    create_data = {
                        "project": decomposition['suggested_project'],
                        "tasks": decomposition['suggested_tasks']
                    }
                    
                    response = session.post(f"{BACKEND_URL}/projects/create-with-tasks", json=create_data, headers=headers, timeout=30)
                    if response.status_code == 200:
                        created_project = response.json()
                        log_test("Template Application", True, f"Created project with {len(created_project.get('tasks', []))} tasks")
                    else:
                        error_data = response.json() if response.content else {}
                        log_test("Template Application", False, f"HTTP {response.status_code}: {error_data}")
                else:
                    log_test("Template Application", False, "Invalid decomposition response structure")
            else:
                error_data = response.json() if response.content else {}
                log_test("AI Goal Decomposition", False, f"HTTP {response.status_code}: {error_data}")
        except Exception as e:
            log_test("Template Application", False, f"Request failed: {str(e)}")
    
    # Results Summary
    print("\n" + "=" * 70)
    print("📊 FINAL TEST RESULTS")
    print("=" * 70)
    
    passed_tests = sum(1 for result in test_results if result['success'])
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    
    # Check for foreign key errors
    foreign_key_errors = sum(1 for result in test_results if not result['success'] and 'FOREIGN KEY' in result['message'])
    
    print(f"\n🔍 ANALYSIS:")
    print(f"Foreign Key Constraint Errors: {foreign_key_errors}")
    print(f"Created Resources: {len(created_resources)}")
    
    if success_rate >= 85 and foreign_key_errors == 0:
        print(f"\n✅ SUCCESS: Onboarding pillar creation is working!")
        print(f"   The database fixes have resolved the foreign key constraint issues.")
        print(f"   Complete onboarding flow is functional.")
    elif foreign_key_errors > 0:
        print(f"\n❌ FAILURE: Foreign key constraint errors still occurring")
        print(f"   The user ID mismatch issue needs to be resolved.")
        print(f"   Database needs user record with ID: 6848f065-2d12-4c4e-88c4-80f375358d7b")
    else:
        print(f"\n⚠️ PARTIAL SUCCESS: Some issues detected")
        print(f"   Success rate: {success_rate:.1f}%")
    
    # Show failed tests
    failed_tests = [result for result in test_results if not result['success']]
    if failed_tests:
        print(f"\n🔍 FAILED TESTS ({len(failed_tests)}):")
        for test in failed_tests:
            print(f"   ❌ {test['name']}: {test['message']}")
    
    print("=" * 70)
    return success_rate >= 85 and foreign_key_errors == 0

def main():
    """Run the final onboarding test"""
    success = test_complete_onboarding_flow()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)