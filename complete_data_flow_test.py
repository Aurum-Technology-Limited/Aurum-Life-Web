#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configuration
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://3f9f12c4-ff11-434a-aa0a-125c04b1de64.preview.emergentagent.com')
API_BASE = f"{BACKEND_URL}/api"

class CompleteDataFlowTestSuite:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "nav.test@aurumlife.com"
        self.test_user_password = "testpassword123"
        self.test_results = []
        self.created_pillars = []
        self.created_areas = []
        self.created_projects = []
        self.created_tasks = []
        
    async def setup_session(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup_session(self):
        """Clean up HTTP session"""
        if self.session:
            await self.session.close()
            
    async def authenticate(self):
        """Authenticate and get JWT token"""
        try:
            print(f"🔐 Authenticating with {self.test_user_email}...")
            
            # Login to get token
            login_data = {
                "email": self.test_user_email,
                "password": self.test_user_password
            }
            
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data["access_token"]
                    print("✅ Authentication successful")
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
        
    async def test_pillar_creation(self):
        """Test 1: Create multiple pillars"""
        print("\n🧪 Test 1: Pillar Creation")
        
        pillar_test_data = [
            {
                "name": "Health & Wellness",
                "description": "Physical and mental health pillar",
                "icon": "🏃‍♂️",
                "color": "#4CAF50",
                "time_allocation": 30
            },
            {
                "name": "Career & Growth",
                "description": "Professional development pillar",
                "icon": "💼",
                "color": "#2196F3",
                "time_allocation": 40
            },
            {
                "name": "Relationships",
                "description": "Family and social connections",
                "icon": "❤️",
                "color": "#E91E63",
                "time_allocation": 30
            }
        ]
        
        try:
            for i, pillar_data in enumerate(pillar_test_data):
                async with self.session.post(f"{API_BASE}/pillars", json=pillar_data, headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        pillar = await response.json()
                        self.created_pillars.append(pillar["id"])
                        print(f"✅ Created pillar: {pillar['name']} (ID: {pillar['id']})")
                    else:
                        error_text = await response.text()
                        print(f"❌ Failed to create pillar {pillar_data['name']}: {response.status} - {error_text}")
                        self.test_results.append({
                            "test": f"Pillar Creation - {pillar_data['name']}", 
                            "status": "FAILED", 
                            "reason": f"HTTP {response.status}: {error_text}"
                        })
                        return
                        
            if len(self.created_pillars) == len(pillar_test_data):
                self.test_results.append({
                    "test": "Pillar Creation", 
                    "status": "PASSED", 
                    "details": f"Created {len(self.created_pillars)} pillars successfully"
                })
            else:
                self.test_results.append({
                    "test": "Pillar Creation", 
                    "status": "FAILED", 
                    "reason": f"Expected {len(pillar_test_data)} pillars, created {len(self.created_pillars)}"
                })
                
        except Exception as e:
            print(f"❌ Pillar creation test failed: {e}")
            self.test_results.append({"test": "Pillar Creation", "status": "FAILED", "reason": str(e)})
            
    async def test_area_creation(self):
        """Test 2: Create areas linked to pillars"""
        print("\n🧪 Test 2: Area Creation (linked to pillars)")
        
        if not self.created_pillars:
            self.test_results.append({"test": "Area Creation", "status": "FAILED", "reason": "No pillars available"})
            return
            
        area_test_data = [
            {
                "name": "Exercise & Fitness",
                "description": "Regular workout and physical activity",
                "pillar_id": self.created_pillars[0],  # Health & Wellness
                "icon": "💪",
                "color": "#4CAF50",
                "importance": 5
            },
            {
                "name": "Skill Development",
                "description": "Learning new professional skills",
                "pillar_id": self.created_pillars[1],  # Career & Growth
                "icon": "📚",
                "color": "#2196F3",
                "importance": 4
            },
            {
                "name": "Family Time",
                "description": "Quality time with family members",
                "pillar_id": self.created_pillars[2],  # Relationships
                "icon": "👨‍👩‍👧‍👦",
                "color": "#E91E63",
                "importance": 5
            }
        ]
        
        try:
            for area_data in area_test_data:
                async with self.session.post(f"{API_BASE}/areas", json=area_data, headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        area = await response.json()
                        self.created_areas.append(area["id"])
                        print(f"✅ Created area: {area['name']} (ID: {area['id']}) linked to pillar {area_data['pillar_id']}")
                    else:
                        error_text = await response.text()
                        print(f"❌ Failed to create area {area_data['name']}: {response.status} - {error_text}")
                        self.test_results.append({
                            "test": f"Area Creation - {area_data['name']}", 
                            "status": "FAILED", 
                            "reason": f"HTTP {response.status}: {error_text}"
                        })
                        return
                        
            if len(self.created_areas) == len(area_test_data):
                self.test_results.append({
                    "test": "Area Creation", 
                    "status": "PASSED", 
                    "details": f"Created {len(self.created_areas)} areas successfully with pillar links"
                })
            else:
                self.test_results.append({
                    "test": "Area Creation", 
                    "status": "FAILED", 
                    "reason": f"Expected {len(area_test_data)} areas, created {len(self.created_areas)}"
                })
                
        except Exception as e:
            print(f"❌ Area creation test failed: {e}")
            self.test_results.append({"test": "Area Creation", "status": "FAILED", "reason": str(e)})
            
    async def test_project_creation(self):
        """Test 3: Create projects linked to areas"""
        print("\n🧪 Test 3: Project Creation (linked to areas)")
        
        if not self.created_areas:
            self.test_results.append({"test": "Project Creation", "status": "FAILED", "reason": "No areas available"})
            return
            
        project_test_data = [
            {
                "name": "Morning Workout Routine",
                "description": "Establish a consistent morning exercise routine",
                "area_id": self.created_areas[0],  # Exercise & Fitness
                "icon": "🌅",
                "priority": "high",
                "status": "In Progress"
            },
            {
                "name": "Python Certification",
                "description": "Complete Python programming certification course",
                "area_id": self.created_areas[1],  # Skill Development
                "icon": "🐍",
                "priority": "high",
                "status": "In Progress"
            },
            {
                "name": "Weekly Family Dinners",
                "description": "Organize weekly family dinner gatherings",
                "area_id": self.created_areas[2],  # Family Time
                "icon": "🍽️",
                "priority": "medium",
                "status": "In Progress"
            }
        ]
        
        try:
            for project_data in project_test_data:
                async with self.session.post(f"{API_BASE}/projects", json=project_data, headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        project = await response.json()
                        self.created_projects.append(project["id"])
                        print(f"✅ Created project: {project['name']} (ID: {project['id']}) linked to area {project_data['area_id']}")
                    else:
                        error_text = await response.text()
                        print(f"❌ Failed to create project {project_data['name']}: {response.status} - {error_text}")
                        self.test_results.append({
                            "test": f"Project Creation - {project_data['name']}", 
                            "status": "FAILED", 
                            "reason": f"HTTP {response.status}: {error_text}"
                        })
                        return
                        
            if len(self.created_projects) == len(project_test_data):
                self.test_results.append({
                    "test": "Project Creation", 
                    "status": "PASSED", 
                    "details": f"Created {len(self.created_projects)} projects successfully with area links"
                })
            else:
                self.test_results.append({
                    "test": "Project Creation", 
                    "status": "FAILED", 
                    "reason": f"Expected {len(project_test_data)} projects, created {len(self.created_projects)}"
                })
                
        except Exception as e:
            print(f"❌ Project creation test failed: {e}")
            self.test_results.append({"test": "Project Creation", "status": "FAILED", "reason": str(e)})
            
    async def test_task_creation(self):
        """Test 4: Create tasks linked to projects"""
        print("\n🧪 Test 4: Task Creation (linked to projects)")
        
        if not self.created_projects:
            self.test_results.append({"test": "Task Creation", "status": "FAILED", "reason": "No projects available"})
            return
            
        task_test_data = [
            {
                "name": "Set up home gym space",
                "description": "Prepare dedicated space for morning workouts",
                "project_id": self.created_projects[0],  # Morning Workout Routine
                "priority": "high",
                "status": "todo"
            },
            {
                "name": "Buy workout equipment",
                "description": "Purchase basic equipment: yoga mat, dumbbells, resistance bands",
                "project_id": self.created_projects[0],  # Morning Workout Routine
                "priority": "medium",
                "status": "todo"
            },
            {
                "name": "Enroll in Python course",
                "description": "Find and enroll in a comprehensive Python certification course",
                "project_id": self.created_projects[1],  # Python Certification
                "priority": "high",
                "status": "todo"
            },
            {
                "name": "Create study schedule",
                "description": "Plan daily study sessions for Python course",
                "project_id": self.created_projects[1],  # Python Certification
                "priority": "medium",
                "status": "todo"
            },
            {
                "name": "Plan first family dinner",
                "description": "Choose date, menu, and send invitations for first dinner",
                "project_id": self.created_projects[2],  # Weekly Family Dinners
                "priority": "high",
                "status": "todo"
            }
        ]
        
        try:
            for task_data in task_test_data:
                async with self.session.post(f"{API_BASE}/tasks", json=task_data, headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        task = await response.json()
                        self.created_tasks.append(task["id"])
                        print(f"✅ Created task: {task['name']} (ID: {task['id']}) linked to project {task_data['project_id']}")
                    else:
                        error_text = await response.text()
                        print(f"❌ Failed to create task {task_data['name']}: {response.status} - {error_text}")
                        self.test_results.append({
                            "test": f"Task Creation - {task_data['name']}", 
                            "status": "FAILED", 
                            "reason": f"HTTP {response.status}: {error_text}"
                        })
                        return
                        
            if len(self.created_tasks) == len(task_test_data):
                self.test_results.append({
                    "test": "Task Creation", 
                    "status": "PASSED", 
                    "details": f"Created {len(self.created_tasks)} tasks successfully with project links"
                })
            else:
                self.test_results.append({
                    "test": "Task Creation", 
                    "status": "FAILED", 
                    "reason": f"Expected {len(task_test_data)} tasks, created {len(self.created_tasks)}"
                })
                
        except Exception as e:
            print(f"❌ Task creation test failed: {e}")
            self.test_results.append({"test": "Task Creation", "status": "FAILED", "reason": str(e)})
            
    async def test_data_retrieval_consistency(self):
        """Test 5: Verify all created data appears in GET endpoints"""
        print("\n🧪 Test 5: Data Retrieval Consistency")
        
        try:
            # Test pillars retrieval
            async with self.session.get(f"{API_BASE}/pillars", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    pillars = await response.json()
                    retrieved_pillar_ids = [p["id"] for p in pillars]
                    missing_pillars = [pid for pid in self.created_pillars if pid not in retrieved_pillar_ids]
                    
                    if not missing_pillars:
                        print(f"✅ All {len(self.created_pillars)} created pillars found in GET /api/pillars")
                    else:
                        print(f"❌ Missing pillars in retrieval: {missing_pillars}")
                        self.test_results.append({
                            "test": "Pillars Retrieval", 
                            "status": "FAILED", 
                            "reason": f"Missing pillars: {missing_pillars}"
                        })
                        return
                else:
                    print(f"❌ Failed to retrieve pillars: {response.status}")
                    self.test_results.append({
                        "test": "Pillars Retrieval", 
                        "status": "FAILED", 
                        "reason": f"HTTP {response.status}"
                    })
                    return
                    
            # Test areas retrieval
            async with self.session.get(f"{API_BASE}/areas", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    areas = await response.json()
                    retrieved_area_ids = [a["id"] for a in areas]
                    missing_areas = [aid for aid in self.created_areas if aid not in retrieved_area_ids]
                    
                    if not missing_areas:
                        print(f"✅ All {len(self.created_areas)} created areas found in GET /api/areas")
                    else:
                        print(f"❌ Missing areas in retrieval: {missing_areas}")
                        self.test_results.append({
                            "test": "Areas Retrieval", 
                            "status": "FAILED", 
                            "reason": f"Missing areas: {missing_areas}"
                        })
                        return
                else:
                    print(f"❌ Failed to retrieve areas: {response.status}")
                    self.test_results.append({
                        "test": "Areas Retrieval", 
                        "status": "FAILED", 
                        "reason": f"HTTP {response.status}"
                    })
                    return
                    
            # Test projects retrieval
            async with self.session.get(f"{API_BASE}/projects", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    projects = await response.json()
                    retrieved_project_ids = [p["id"] for p in projects]
                    missing_projects = [pid for pid in self.created_projects if pid not in retrieved_project_ids]
                    
                    if not missing_projects:
                        print(f"✅ All {len(self.created_projects)} created projects found in GET /api/projects")
                    else:
                        print(f"❌ Missing projects in retrieval: {missing_projects}")
                        self.test_results.append({
                            "test": "Projects Retrieval", 
                            "status": "FAILED", 
                            "reason": f"Missing projects: {missing_projects}"
                        })
                        return
                else:
                    print(f"❌ Failed to retrieve projects: {response.status}")
                    self.test_results.append({
                        "test": "Projects Retrieval", 
                        "status": "FAILED", 
                        "reason": f"HTTP {response.status}"
                    })
                    return
                    
            # Test tasks retrieval
            async with self.session.get(f"{API_BASE}/tasks", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    tasks = await response.json()
                    retrieved_task_ids = [t["id"] for t in tasks]
                    missing_tasks = [tid for tid in self.created_tasks if tid not in retrieved_task_ids]
                    
                    if not missing_tasks:
                        print(f"✅ All {len(self.created_tasks)} created tasks found in GET /api/tasks")
                    else:
                        print(f"❌ Missing tasks in retrieval: {missing_tasks}")
                        self.test_results.append({
                            "test": "Tasks Retrieval", 
                            "status": "FAILED", 
                            "reason": f"Missing tasks: {missing_tasks}"
                        })
                        return
                else:
                    print(f"❌ Failed to retrieve tasks: {response.status}")
                    self.test_results.append({
                        "test": "Tasks Retrieval", 
                        "status": "FAILED", 
                        "reason": f"HTTP {response.status}"
                    })
                    return
                    
            self.test_results.append({
                "test": "Data Retrieval Consistency", 
                "status": "PASSED", 
                "details": "All created data found in respective GET endpoints"
            })
            
        except Exception as e:
            print(f"❌ Data retrieval consistency test failed: {e}")
            self.test_results.append({"test": "Data Retrieval Consistency", "status": "FAILED", "reason": str(e)})
            
    async def test_foreign_key_relationships(self):
        """Test 6: Verify foreign key relationships work properly"""
        print("\n🧪 Test 6: Foreign Key Relationships")
        
        try:
            # Test area-pillar relationships
            async with self.session.get(f"{API_BASE}/areas?include_projects=true", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    areas = await response.json()
                    
                    # Check if areas have correct pillar references
                    relationship_errors = []
                    for area in areas:
                        if area["id"] in self.created_areas:
                            if "pillar_id" not in area or not area["pillar_id"]:
                                relationship_errors.append(f"Area {area['id']} missing pillar_id")
                            elif area["pillar_id"] not in self.created_pillars:
                                relationship_errors.append(f"Area {area['id']} has invalid pillar_id: {area['pillar_id']}")
                                
                    if not relationship_errors:
                        print("✅ Area-Pillar relationships are correct")
                    else:
                        print(f"❌ Area-Pillar relationship errors: {relationship_errors}")
                        self.test_results.append({
                            "test": "Area-Pillar Relationships", 
                            "status": "FAILED", 
                            "reason": f"Relationship errors: {relationship_errors}"
                        })
                        return
                else:
                    print(f"❌ Failed to retrieve areas with relationships: {response.status}")
                    self.test_results.append({
                        "test": "Foreign Key Relationships", 
                        "status": "FAILED", 
                        "reason": f"Areas retrieval failed: HTTP {response.status}"
                    })
                    return
                    
            # Test project-area relationships
            async with self.session.get(f"{API_BASE}/projects", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    projects = await response.json()
                    
                    # Check if projects have correct area references
                    relationship_errors = []
                    for project in projects:
                        if project["id"] in self.created_projects:
                            if "area_id" not in project or not project["area_id"]:
                                relationship_errors.append(f"Project {project['id']} missing area_id")
                            elif project["area_id"] not in self.created_areas:
                                relationship_errors.append(f"Project {project['id']} has invalid area_id: {project['area_id']}")
                                
                    if not relationship_errors:
                        print("✅ Project-Area relationships are correct")
                    else:
                        print(f"❌ Project-Area relationship errors: {relationship_errors}")
                        self.test_results.append({
                            "test": "Project-Area Relationships", 
                            "status": "FAILED", 
                            "reason": f"Relationship errors: {relationship_errors}"
                        })
                        return
                else:
                    print(f"❌ Failed to retrieve projects with relationships: {response.status}")
                    self.test_results.append({
                        "test": "Foreign Key Relationships", 
                        "status": "FAILED", 
                        "reason": f"Projects retrieval failed: HTTP {response.status}"
                    })
                    return
                    
            # Test task-project relationships
            async with self.session.get(f"{API_BASE}/tasks", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    tasks = await response.json()
                    
                    # Check if tasks have correct project references
                    relationship_errors = []
                    for task in tasks:
                        if task["id"] in self.created_tasks:
                            if "project_id" not in task or not task["project_id"]:
                                relationship_errors.append(f"Task {task['id']} missing project_id")
                            elif task["project_id"] not in self.created_projects:
                                relationship_errors.append(f"Task {task['id']} has invalid project_id: {task['project_id']}")
                                
                    if not relationship_errors:
                        print("✅ Task-Project relationships are correct")
                    else:
                        print(f"❌ Task-Project relationship errors: {relationship_errors}")
                        self.test_results.append({
                            "test": "Task-Project Relationships", 
                            "status": "FAILED", 
                            "reason": f"Relationship errors: {relationship_errors}"
                        })
                        return
                else:
                    print(f"❌ Failed to retrieve tasks with relationships: {response.status}")
                    self.test_results.append({
                        "test": "Foreign Key Relationships", 
                        "status": "FAILED", 
                        "reason": f"Tasks retrieval failed: HTTP {response.status}"
                    })
                    return
                    
            self.test_results.append({
                "test": "Foreign Key Relationships", 
                "status": "PASSED", 
                "details": "All foreign key relationships are correct"
            })
            
        except Exception as e:
            print(f"❌ Foreign key relationships test failed: {e}")
            self.test_results.append({"test": "Foreign Key Relationships", "status": "FAILED", "reason": str(e)})
            
    async def test_authentication_flow(self):
        """Test 7: Confirm auth user ID is working correctly"""
        print("\n🧪 Test 7: Authentication Flow Verification")
        
        try:
            # Test /auth/me endpoint
            async with self.session.get(f"{API_BASE}/auth/me", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    user_data = await response.json()
                    user_id = user_data.get("id")
                    
                    if user_id:
                        print(f"✅ Authentication working - User ID: {user_id}")
                        
                        # Verify this user ID is consistent across all created data
                        # Check one pillar to verify user_id consistency
                        if self.created_pillars:
                            async with self.session.get(f"{API_BASE}/pillars/{self.created_pillars[0]}", headers=self.get_auth_headers()) as pillar_response:
                                if pillar_response.status == 200:
                                    pillar_data = await pillar_response.json()
                                    pillar_user_id = pillar_data.get("user_id")
                                    
                                    if pillar_user_id == user_id:
                                        print(f"✅ User ID consistency verified: {user_id}")
                                        self.test_results.append({
                                            "test": "Authentication Flow", 
                                            "status": "PASSED", 
                                            "details": f"User ID {user_id} consistent across all endpoints"
                                        })
                                    else:
                                        print(f"❌ User ID mismatch - Auth: {user_id}, Pillar: {pillar_user_id}")
                                        self.test_results.append({
                                            "test": "Authentication Flow", 
                                            "status": "FAILED", 
                                            "reason": f"User ID mismatch - Auth: {user_id}, Pillar: {pillar_user_id}"
                                        })
                                else:
                                    print(f"❌ Failed to retrieve pillar for user ID verification: {pillar_response.status}")
                                    self.test_results.append({
                                        "test": "Authentication Flow", 
                                        "status": "FAILED", 
                                        "reason": f"Pillar retrieval failed: HTTP {pillar_response.status}"
                                    })
                        else:
                            print("⚠️ No pillars created to verify user ID consistency")
                            self.test_results.append({
                                "test": "Authentication Flow", 
                                "status": "PARTIAL", 
                                "details": "Auth working but no data to verify consistency"
                            })
                    else:
                        print("❌ No user ID returned from /auth/me")
                        self.test_results.append({
                            "test": "Authentication Flow", 
                            "status": "FAILED", 
                            "reason": "No user ID in auth response"
                        })
                else:
                    error_text = await response.text()
                    print(f"❌ /auth/me endpoint failed: {response.status} - {error_text}")
                    self.test_results.append({
                        "test": "Authentication Flow", 
                        "status": "FAILED", 
                        "reason": f"/auth/me failed: HTTP {response.status}"
                    })
                    
        except Exception as e:
            print(f"❌ Authentication flow test failed: {e}")
            self.test_results.append({"test": "Authentication Flow", "status": "FAILED", "reason": str(e)})
            
    async def test_end_to_end_hierarchy(self):
        """Test 8: Complete hierarchy verification (Pillar → Area → Project → Task)"""
        print("\n🧪 Test 8: End-to-End Data Hierarchy")
        
        try:
            if not (self.created_pillars and self.created_areas and self.created_projects and self.created_tasks):
                self.test_results.append({
                    "test": "End-to-End Hierarchy", 
                    "status": "FAILED", 
                    "reason": "Incomplete data hierarchy - missing some entities"
                })
                return
                
            # Trace the complete hierarchy for one chain
            pillar_id = self.created_pillars[0]
            
            # Find area linked to this pillar
            async with self.session.get(f"{API_BASE}/areas", headers=self.get_auth_headers()) as response:
                if response.status != 200:
                    self.test_results.append({
                        "test": "End-to-End Hierarchy", 
                        "status": "FAILED", 
                        "reason": f"Areas retrieval failed: HTTP {response.status}"
                    })
                    return
                    
                areas = await response.json()
                linked_area = None
                for area in areas:
                    if area.get("pillar_id") == pillar_id:
                        linked_area = area
                        break
                        
                if not linked_area:
                    self.test_results.append({
                        "test": "End-to-End Hierarchy", 
                        "status": "FAILED", 
                        "reason": f"No area found linked to pillar {pillar_id}"
                    })
                    return
                    
            # Find project linked to this area
            async with self.session.get(f"{API_BASE}/projects", headers=self.get_auth_headers()) as response:
                if response.status != 200:
                    self.test_results.append({
                        "test": "End-to-End Hierarchy", 
                        "status": "FAILED", 
                        "reason": f"Projects retrieval failed: HTTP {response.status}"
                    })
                    return
                    
                projects = await response.json()
                linked_project = None
                for project in projects:
                    if project.get("area_id") == linked_area["id"]:
                        linked_project = project
                        break
                        
                if not linked_project:
                    self.test_results.append({
                        "test": "End-to-End Hierarchy", 
                        "status": "FAILED", 
                        "reason": f"No project found linked to area {linked_area['id']}"
                    })
                    return
                    
            # Find task linked to this project
            async with self.session.get(f"{API_BASE}/tasks", headers=self.get_auth_headers()) as response:
                if response.status != 200:
                    self.test_results.append({
                        "test": "End-to-End Hierarchy", 
                        "status": "FAILED", 
                        "reason": f"Tasks retrieval failed: HTTP {response.status}"
                    })
                    return
                    
                tasks = await response.json()
                linked_task = None
                for task in tasks:
                    if task.get("project_id") == linked_project["id"]:
                        linked_task = task
                        break
                        
                if not linked_task:
                    self.test_results.append({
                        "test": "End-to-End Hierarchy", 
                        "status": "FAILED", 
                        "reason": f"No task found linked to project {linked_project['id']}"
                    })
                    return
                    
            # If we reach here, the complete hierarchy is working
            hierarchy_chain = f"Pillar '{self.created_pillars[0]}' → Area '{linked_area['id']}' → Project '{linked_project['id']}' → Task '{linked_task['id']}'"
            print(f"✅ Complete hierarchy verified: {hierarchy_chain}")
            
            self.test_results.append({
                "test": "End-to-End Hierarchy", 
                "status": "PASSED", 
                "details": f"Complete hierarchy working: {hierarchy_chain}"
            })
            
        except Exception as e:
            print(f"❌ End-to-end hierarchy test failed: {e}")
            self.test_results.append({"test": "End-to-End Hierarchy", "status": "FAILED", "reason": str(e)})
            
    async def cleanup_test_data(self):
        """Clean up created test data"""
        print("\n🧹 Cleaning up test data...")
        
        try:
            # Delete in reverse order to respect foreign key constraints
            # Delete tasks first
            for task_id in self.created_tasks:
                async with self.session.delete(f"{API_BASE}/tasks/{task_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print(f"✅ Deleted task {task_id}")
                    else:
                        print(f"⚠️ Failed to delete task {task_id}: {response.status}")
                        
            # Delete projects
            for project_id in self.created_projects:
                async with self.session.delete(f"{API_BASE}/projects/{project_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print(f"✅ Deleted project {project_id}")
                    else:
                        print(f"⚠️ Failed to delete project {project_id}: {response.status}")
                        
            # Delete areas
            for area_id in self.created_areas:
                async with self.session.delete(f"{API_BASE}/areas/{area_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print(f"✅ Deleted area {area_id}")
                    else:
                        print(f"⚠️ Failed to delete area {area_id}: {response.status}")
                        
            # Delete pillars
            for pillar_id in self.created_pillars:
                async with self.session.delete(f"{API_BASE}/pillars/{pillar_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print(f"✅ Deleted pillar {pillar_id}")
                    else:
                        print(f"⚠️ Failed to delete pillar {pillar_id}: {response.status}")
                        
        except Exception as e:
            print(f"⚠️ Cleanup error: {e}")
            
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🎯 COMPLETE DATA CREATION AND RETRIEVAL FLOW - TEST SUMMARY")
        print("="*80)
        
        passed = len([t for t in self.test_results if t["status"] == "PASSED"])
        failed = len([t for t in self.test_results if t["status"] == "FAILED"])
        partial = len([t for t in self.test_results if t["status"] == "PARTIAL"])
        skipped = len([t for t in self.test_results if t["status"] == "SKIPPED"])
        total = len(self.test_results)
        
        print(f"📊 OVERALL RESULTS: {passed}/{total} tests passed")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️ Partial: {partial}")
        print(f"⏭️ Skipped: {skipped}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        print("\n📋 DETAILED RESULTS:")
        for i, result in enumerate(self.test_results, 1):
            status_icon = {"PASSED": "✅", "FAILED": "❌", "PARTIAL": "⚠️", "SKIPPED": "⏭️"}
            icon = status_icon.get(result["status"], "❓")
            print(f"{i:2d}. {icon} {result['test']}: {result['status']}")
            
            if "details" in result:
                print(f"    📝 {result['details']}")
            if "reason" in result:
                print(f"    💬 {result['reason']}")
                
        print("\n" + "="*80)
        
        # Determine overall system status
        if success_rate >= 90:
            print("🎉 COMPLETE DATA FLOW IS PRODUCTION-READY!")
            print("✅ All data creation and retrieval working perfectly")
            print("✅ Foreign key constraints resolved")
            print("✅ Authentication and user context working")
        elif success_rate >= 75:
            print("⚠️ COMPLETE DATA FLOW IS MOSTLY FUNCTIONAL - MINOR ISSUES DETECTED")
            print("⚠️ Some components may need attention")
        else:
            print("❌ COMPLETE DATA FLOW HAS SIGNIFICANT ISSUES - NEEDS IMMEDIATE ATTENTION")
            print("❌ Critical foreign key constraint or authentication issues detected")
            
        print("="*80)
        
        return success_rate
        
    async def run_all_tests(self):
        """Run all complete data flow tests"""
        print("🚀 Starting Complete Data Creation and Retrieval Flow Testing...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print(f"👤 Test User: {self.test_user_email}")
        
        await self.setup_session()
        
        try:
            # Authentication
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed with tests")
                return 0
                
            # Run all tests in sequence
            await self.test_pillar_creation()
            await self.test_area_creation()
            await self.test_project_creation()
            await self.test_task_creation()
            await self.test_data_retrieval_consistency()
            await self.test_foreign_key_relationships()
            await self.test_authentication_flow()
            await self.test_end_to_end_hierarchy()
            
            # Cleanup
            await self.cleanup_test_data()
            
        finally:
            await self.cleanup_session()
            
        # Print summary and return success rate
        return self.print_test_summary()

async def main():
    """Main test execution"""
    test_suite = CompleteDataFlowTestSuite()
    success_rate = await test_suite.run_all_tests()
    
    # Exit with appropriate code
    if success_rate >= 90:
        exit(0)  # Success
    elif success_rate >= 75:
        exit(1)  # Partial success
    else:
        exit(2)  # Failure

if __name__ == "__main__":
    asyncio.run(main())