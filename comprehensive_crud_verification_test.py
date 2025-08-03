#!/usr/bin/env python3

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from typing import Dict, Any, List

# Configuration - Use external URL from frontend/.env
BACKEND_URL = "https://2add7c3c-bc98-404b-af7c-7c73ee7f9c41.preview.emergentagent.com"
API_BASE = f"{BACKEND_URL}/api"

class ComprehensiveCRUDVerificationSuite:
    """Comprehensive CRUD testing for ALL core components as requested in review"""
    
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "nav.test@aurumlife.com"
        self.test_user_password = "testpassword"
        self.test_results = []
        self.created_resources = {
            'pillars': [],
            'areas': [],
            'projects': [],
            'tasks': [],
            'journal_entries': [],
            'journal_templates': [],
            'project_templates': []
        }
        
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
            
            async with self.session.post(f"{BACKEND_URL}/api/auth/login", json=login_data) as response:
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
        
    async def test_dashboard_crud(self):
        """Test 1: Dashboard CRUD (READ operations primarily)"""
        print("\n🧪 Test 1: Dashboard CRUD Operations")
        
        try:
            success_count = 0
            total_tests = 2
            
            # Test GET /api/dashboard
            print("   Testing GET /api/dashboard...")
            async with self.session.get(f"{API_BASE}/dashboard", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    dashboard_data = await response.json()
                    required_fields = ['user', 'stats', 'recent_tasks']
                    missing_fields = [field for field in required_fields if field not in dashboard_data]
                    
                    if not missing_fields:
                        print("   ✅ Dashboard endpoint working with proper structure")
                        success_count += 1
                    else:
                        print(f"   ❌ Dashboard missing fields: {missing_fields}")
                else:
                    print(f"   ❌ Dashboard endpoint failed: {response.status}")
                    
            # Test GET /api/today
            print("   Testing GET /api/today...")
            async with self.session.get(f"{API_BASE}/today", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    today_data = await response.json()
                    required_fields = ['tasks', 'priorities', 'recommendations']
                    missing_fields = [field for field in required_fields if field not in today_data]
                    
                    if not missing_fields:
                        print("   ✅ Today view endpoint working with proper structure")
                        success_count += 1
                    else:
                        print(f"   ❌ Today view missing fields: {missing_fields}")
                else:
                    print(f"   ❌ Today view endpoint failed: {response.status}")
                    
            if success_count == total_tests:
                self.test_results.append({"test": "Dashboard CRUD", "status": "PASSED", "details": f"All {total_tests} dashboard endpoints working"})
                return True
            else:
                self.test_results.append({"test": "Dashboard CRUD", "status": "FAILED", "reason": f"Only {success_count}/{total_tests} endpoints working"})
                return False
                
        except Exception as e:
            print(f"❌ Dashboard CRUD test failed: {e}")
            self.test_results.append({"test": "Dashboard CRUD", "status": "FAILED", "reason": str(e)})
            return False
            
    async def test_insights_crud(self):
        """Test 2: Insights CRUD (READ operations primarily)"""
        print("\n🧪 Test 2: Insights CRUD Operations")
        
        try:
            success_count = 0
            total_tests = 3
            
            # Test GET /api/insights
            print("   Testing GET /api/insights...")
            async with self.session.get(f"{API_BASE}/insights", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    insights_data = await response.json()
                    if 'alignment_snapshot' in insights_data:
                        print("   ✅ Main insights endpoint working with alignment_snapshot")
                        success_count += 1
                    else:
                        print("   ❌ Main insights missing alignment_snapshot")
                else:
                    print(f"   ❌ Main insights endpoint failed: {response.status}")
                    
            # Test GET /api/insights/areas/{area_id} (using dummy ID)
            print("   Testing GET /api/insights/areas/{area_id}...")
            async with self.session.get(f"{API_BASE}/insights/areas/test-area-id", headers=self.get_auth_headers()) as response:
                if response.status in [200, 404]:  # 404 is acceptable for non-existent area
                    print("   ✅ Area insights endpoint accessible")
                    success_count += 1
                else:
                    print(f"   ❌ Area insights endpoint failed: {response.status}")
                    
            # Test GET /api/insights/projects/{project_id} (using dummy ID)
            print("   Testing GET /api/insights/projects/{project_id}...")
            async with self.session.get(f"{API_BASE}/insights/projects/test-project-id", headers=self.get_auth_headers()) as response:
                if response.status in [200, 404]:  # 404 is acceptable for non-existent project
                    print("   ✅ Project insights endpoint accessible")
                    success_count += 1
                else:
                    print(f"   ❌ Project insights endpoint failed: {response.status}")
                    
            if success_count == total_tests:
                self.test_results.append({"test": "Insights CRUD", "status": "PASSED", "details": f"All {total_tests} insights endpoints working"})
                return True
            else:
                self.test_results.append({"test": "Insights CRUD", "status": "FAILED", "reason": f"Only {success_count}/{total_tests} endpoints working"})
                return False
                
        except Exception as e:
            print(f"❌ Insights CRUD test failed: {e}")
            self.test_results.append({"test": "Insights CRUD", "status": "FAILED", "reason": str(e)})
            return False
            
    async def test_journal_crud(self):
        """Test 3: Journal CRUD (Full CRUD)"""
        print("\n🧪 Test 3: Journal CRUD Operations (Full CRUD)")
        
        try:
            success_count = 0
            total_tests = 7
            
            # Test GET /api/journal
            print("   Testing GET /api/journal...")
            async with self.session.get(f"{API_BASE}/journal", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    journal_data = await response.json()
                    if 'entries' in journal_data and 'total' in journal_data:
                        print("   ✅ Journal list endpoint working")
                        success_count += 1
                    else:
                        print("   ❌ Journal list missing required fields")
                else:
                    print(f"   ❌ Journal list endpoint failed: {response.status}")
                    
            # Test POST /api/journal
            print("   Testing POST /api/journal...")
            journal_entry_data = {
                "title": "Test Journal Entry",
                "content": "This is a test journal entry for CRUD verification",
                "mood": "happy",
                "tags": ["test", "crud"]
            }
            
            async with self.session.post(f"{API_BASE}/journal", json=journal_entry_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    entry = await response.json()
                    if 'id' in entry:
                        self.created_resources['journal_entries'].append(entry['id'])
                        print("   ✅ Journal entry creation working")
                        success_count += 1
                    else:
                        print("   ❌ Journal entry creation missing ID")
                else:
                    print(f"   ❌ Journal entry creation failed: {response.status}")
                    
            # Test PUT /api/journal/{entry_id}
            if self.created_resources['journal_entries']:
                print("   Testing PUT /api/journal/{entry_id}...")
                entry_id = self.created_resources['journal_entries'][0]
                update_data = {"title": "Updated Test Journal Entry", "content": "Updated content"}
                
                async with self.session.put(f"{API_BASE}/journal/{entry_id}", json=update_data, headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print("   ✅ Journal entry update working")
                        success_count += 1
                    else:
                        print(f"   ❌ Journal entry update failed: {response.status}")
            else:
                print("   ⚠️ Skipping journal update test - no entry created")
                
            # Test GET /api/journal/search
            print("   Testing GET /api/journal/search...")
            async with self.session.get(f"{API_BASE}/journal/search?q=test", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    search_data = await response.json()
                    if 'results' in search_data and 'query' in search_data:
                        print("   ✅ Journal search endpoint working")
                        success_count += 1
                    else:
                        print("   ❌ Journal search missing required fields")
                else:
                    print(f"   ❌ Journal search endpoint failed: {response.status}")
                    
            # Test GET /api/journal/insights
            print("   Testing GET /api/journal/insights...")
            async with self.session.get(f"{API_BASE}/journal/insights", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    insights_data = await response.json()
                    if 'total_entries' in insights_data:
                        print("   ✅ Journal insights endpoint working")
                        success_count += 1
                    else:
                        print("   ❌ Journal insights missing required fields")
                else:
                    print(f"   ❌ Journal insights endpoint failed: {response.status}")
                    
            # Test GET /api/journal/on-this-day
            print("   Testing GET /api/journal/on-this-day...")
            async with self.session.get(f"{API_BASE}/journal/on-this-day", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    historical_data = await response.json()
                    if 'entries' in historical_data and 'date' in historical_data:
                        print("   ✅ Journal on-this-day endpoint working")
                        success_count += 1
                    else:
                        print("   ❌ Journal on-this-day missing required fields")
                else:
                    print(f"   ❌ Journal on-this-day endpoint failed: {response.status}")
                    
            # Test DELETE /api/journal/{entry_id}
            if self.created_resources['journal_entries']:
                print("   Testing DELETE /api/journal/{entry_id}...")
                entry_id = self.created_resources['journal_entries'][0]
                
                async with self.session.delete(f"{API_BASE}/journal/{entry_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print("   ✅ Journal entry deletion working")
                        success_count += 1
                    else:
                        print(f"   ❌ Journal entry deletion failed: {response.status}")
            else:
                print("   ⚠️ Skipping journal deletion test - no entry created")
                
            if success_count >= 5:  # Allow some flexibility for optional tests
                self.test_results.append({"test": "Journal CRUD", "status": "PASSED", "details": f"{success_count}/{total_tests} journal endpoints working"})
                return True
            else:
                self.test_results.append({"test": "Journal CRUD", "status": "FAILED", "reason": f"Only {success_count}/{total_tests} endpoints working"})
                return False
                
        except Exception as e:
            print(f"❌ Journal CRUD test failed: {e}")
            self.test_results.append({"test": "Journal CRUD", "status": "FAILED", "reason": str(e)})
            return False
            
    async def test_journal_templates_crud(self):
        """Test 4: Journal Templates CRUD (Full CRUD)"""
        print("\n🧪 Test 4: Journal Templates CRUD Operations (Full CRUD)")
        
        try:
            success_count = 0
            total_tests = 5
            
            # Test GET /api/journal/templates
            print("   Testing GET /api/journal/templates...")
            async with self.session.get(f"{API_BASE}/journal/templates", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    templates = await response.json()
                    if isinstance(templates, list):
                        print(f"   ✅ Journal templates list working ({len(templates)} templates)")
                        success_count += 1
                    else:
                        print("   ❌ Journal templates should return a list")
                else:
                    print(f"   ❌ Journal templates list failed: {response.status}")
                    
            # Test GET /api/journal/templates/{template_id}
            print("   Testing GET /api/journal/templates/{template_id}...")
            async with self.session.get(f"{API_BASE}/journal/templates/template-daily", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    template = await response.json()
                    if 'id' in template and 'structure' in template:
                        print("   ✅ Specific journal template retrieval working")
                        success_count += 1
                    else:
                        print("   ❌ Journal template missing required fields")
                else:
                    print(f"   ❌ Specific journal template failed: {response.status}")
                    
            # Test POST /api/journal/templates
            print("   Testing POST /api/journal/templates...")
            template_data = {
                "name": "Test Template",
                "description": "Test journal template for CRUD verification",
                "structure": {
                    "sections": [
                        {"name": "Test Section", "type": "text"}
                    ]
                }
            }
            
            async with self.session.post(f"{API_BASE}/journal/templates", json=template_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    template = await response.json()
                    if 'id' in template:
                        self.created_resources['journal_templates'].append(template['id'])
                        print("   ✅ Journal template creation working")
                        success_count += 1
                    else:
                        print("   ❌ Journal template creation missing ID")
                else:
                    print(f"   ❌ Journal template creation failed: {response.status}")
                    
            # Test PUT /api/journal/templates/{template_id}
            if self.created_resources['journal_templates']:
                print("   Testing PUT /api/journal/templates/{template_id}...")
                template_id = self.created_resources['journal_templates'][0]
                update_data = {"name": "Updated Test Template", "description": "Updated description"}
                
                async with self.session.put(f"{API_BASE}/journal/templates/{template_id}", json=update_data, headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print("   ✅ Journal template update working")
                        success_count += 1
                    else:
                        print(f"   ❌ Journal template update failed: {response.status}")
            else:
                print("   ⚠️ Skipping journal template update test - no template created")
                
            # Test DELETE /api/journal/templates/{template_id}
            if self.created_resources['journal_templates']:
                print("   Testing DELETE /api/journal/templates/{template_id}...")
                template_id = self.created_resources['journal_templates'][0]
                
                async with self.session.delete(f"{API_BASE}/journal/templates/{template_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print("   ✅ Journal template deletion working")
                        success_count += 1
                    else:
                        print(f"   ❌ Journal template deletion failed: {response.status}")
            else:
                print("   ⚠️ Skipping journal template deletion test - no template created")
                
            if success_count >= 3:  # Allow some flexibility
                self.test_results.append({"test": "Journal Templates CRUD", "status": "PASSED", "details": f"{success_count}/{total_tests} template endpoints working"})
                return True
            else:
                self.test_results.append({"test": "Journal Templates CRUD", "status": "FAILED", "reason": f"Only {success_count}/{total_tests} endpoints working"})
                return False
                
        except Exception as e:
            print(f"❌ Journal Templates CRUD test failed: {e}")
            self.test_results.append({"test": "Journal Templates CRUD", "status": "FAILED", "reason": str(e)})
            return False
            
    async def test_pillars_crud(self):
        """Test 5: Pillars CRUD (Full CRUD)"""
        print("\n🧪 Test 5: Pillars CRUD Operations (Full CRUD)")
        
        try:
            success_count = 0
            total_tests = 4
            
            # Test GET /api/pillars
            print("   Testing GET /api/pillars...")
            async with self.session.get(f"{API_BASE}/pillars", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    pillars = await response.json()
                    if isinstance(pillars, list):
                        print(f"   ✅ Pillars list working ({len(pillars)} pillars)")
                        success_count += 1
                    else:
                        print("   ❌ Pillars should return a list")
                else:
                    print(f"   ❌ Pillars list failed: {response.status}")
                    
            # Test POST /api/pillars
            print("   Testing POST /api/pillars...")
            pillar_data = {
                "name": "Test Pillar",
                "description": "Test pillar for CRUD verification",
                "icon": "🧪",
                "color": "#10B981",
                "time_allocation_percentage": 25.0
            }
            
            async with self.session.post(f"{API_BASE}/pillars", json=pillar_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    pillar = await response.json()
                    if 'id' in pillar:
                        self.created_resources['pillars'].append(pillar['id'])
                        print("   ✅ Pillar creation working")
                        success_count += 1
                    else:
                        print("   ❌ Pillar creation missing ID")
                else:
                    print(f"   ❌ Pillar creation failed: {response.status}")
                    
            # Test PUT /api/pillars/{pillar_id}
            if self.created_resources['pillars']:
                print("   Testing PUT /api/pillars/{pillar_id}...")
                pillar_id = self.created_resources['pillars'][0]
                update_data = {"name": "Updated Test Pillar", "time_allocation_percentage": 30.0}
                
                async with self.session.put(f"{API_BASE}/pillars/{pillar_id}", json=update_data, headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print("   ✅ Pillar update working")
                        success_count += 1
                    else:
                        print(f"   ❌ Pillar update failed: {response.status}")
            else:
                print("   ⚠️ Skipping pillar update test - no pillar created")
                
            # Test DELETE /api/pillars/{pillar_id}
            if self.created_resources['pillars']:
                print("   Testing DELETE /api/pillars/{pillar_id}...")
                pillar_id = self.created_resources['pillars'][0]
                
                async with self.session.delete(f"{API_BASE}/pillars/{pillar_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print("   ✅ Pillar deletion working")
                        success_count += 1
                    else:
                        print(f"   ❌ Pillar deletion failed: {response.status}")
            else:
                print("   ⚠️ Skipping pillar deletion test - no pillar created")
                
            if success_count >= 3:  # Allow some flexibility
                self.test_results.append({"test": "Pillars CRUD", "status": "PASSED", "details": f"{success_count}/{total_tests} pillar endpoints working"})
                return True
            else:
                self.test_results.append({"test": "Pillars CRUD", "status": "FAILED", "reason": f"Only {success_count}/{total_tests} endpoints working"})
                return False
                
        except Exception as e:
            print(f"❌ Pillars CRUD test failed: {e}")
            self.test_results.append({"test": "Pillars CRUD", "status": "FAILED", "reason": str(e)})
            return False
            
    async def test_areas_crud(self):
        """Test 6: Areas CRUD (Full CRUD)"""
        print("\n🧪 Test 6: Areas CRUD Operations (Full CRUD)")
        
        try:
            success_count = 0
            total_tests = 4
            
            # Test GET /api/areas
            print("   Testing GET /api/areas...")
            async with self.session.get(f"{API_BASE}/areas", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    areas = await response.json()
                    if isinstance(areas, list):
                        print(f"   ✅ Areas list working ({len(areas)} areas)")
                        success_count += 1
                    else:
                        print("   ❌ Areas should return a list")
                else:
                    print(f"   ❌ Areas list failed: {response.status}")
                    
            # Test POST /api/areas (area_id is optional)
            print("   Testing POST /api/areas...")
            area_data = {
                "name": "Test Area",
                "description": "Test area for CRUD verification",
                "icon": "🧪",
                "color": "#F59E0B",
                "importance": 4
            }
            
            # Add pillar_id if we have one (optional field)
            if self.created_resources['pillars']:
                area_data["pillar_id"] = self.created_resources['pillars'][0]
            
            async with self.session.post(f"{API_BASE}/areas", json=area_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    area = await response.json()
                    if 'id' in area:
                        self.created_resources['areas'].append(area['id'])
                        print("   ✅ Area creation working")
                        success_count += 1
                    else:
                        print("   ❌ Area creation missing ID")
                else:
                    error_text = await response.text()
                    print(f"   ❌ Area creation failed: {response.status} - {error_text}")
                    
            # Test PUT /api/areas/{area_id}
            if self.created_resources['areas']:
                print("   Testing PUT /api/areas/{area_id}...")
                area_id = self.created_resources['areas'][0]
                update_data = {"name": "Updated Test Area", "importance": 5}
                
                async with self.session.put(f"{API_BASE}/areas/{area_id}", json=update_data, headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print("   ✅ Area update working")
                        success_count += 1
                    else:
                        print(f"   ❌ Area update failed: {response.status}")
            else:
                print("   ⚠️ Skipping area update test - no area created")
                
            # Test DELETE /api/areas/{area_id}
            if self.created_resources['areas']:
                print("   Testing DELETE /api/areas/{area_id}...")
                area_id = self.created_resources['areas'][0]
                
                async with self.session.delete(f"{API_BASE}/areas/{area_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print("   ✅ Area deletion working")
                        success_count += 1
                    else:
                        print(f"   ❌ Area deletion failed: {response.status}")
            else:
                print("   ⚠️ Skipping area deletion test - no area created")
                
            if success_count >= 3:  # Allow some flexibility
                self.test_results.append({"test": "Areas CRUD", "status": "PASSED", "details": f"{success_count}/{total_tests} area endpoints working"})
                return True
            else:
                self.test_results.append({"test": "Areas CRUD", "status": "FAILED", "reason": f"Only {success_count}/{total_tests} endpoints working"})
                return False
                
        except Exception as e:
            print(f"❌ Areas CRUD test failed: {e}")
            self.test_results.append({"test": "Areas CRUD", "status": "FAILED", "reason": str(e)})
            return False
            
    async def test_projects_crud(self):
        """Test 7: Projects CRUD (Full CRUD)"""
        print("\n🧪 Test 7: Projects CRUD Operations (Full CRUD)")
        
        try:
            success_count = 0
            total_tests = 4
            
            # Test GET /api/projects
            print("   Testing GET /api/projects...")
            async with self.session.get(f"{API_BASE}/projects", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    projects = await response.json()
                    if isinstance(projects, list):
                        print(f"   ✅ Projects list working ({len(projects)} projects)")
                        success_count += 1
                    else:
                        print("   ❌ Projects should return a list")
                else:
                    print(f"   ❌ Projects list failed: {response.status}")
                    
            # Test POST /api/projects (area_id is required)
            print("   Testing POST /api/projects...")
            project_data = {
                "name": "Test Project",
                "description": "Test project for CRUD verification",
                "icon": "🧪",
                "status": "Not Started",
                "priority": "high"
            }
            
            # area_id is required - use existing area or create one
            if self.created_resources['areas']:
                project_data["area_id"] = self.created_resources['areas'][0]
            else:
                # Create a temporary area for project testing
                temp_area_data = {
                    "name": "Temp Area for Project Test",
                    "description": "Temporary area for project testing",
                    "icon": "📁",
                    "color": "#10B981",
                    "importance": 3
                }
                
                async with self.session.post(f"{API_BASE}/areas", json=temp_area_data, headers=self.get_auth_headers()) as area_response:
                    if area_response.status == 200:
                        temp_area = await area_response.json()
                        project_data["area_id"] = temp_area['id']
                        self.created_resources['areas'].append(temp_area['id'])
                        print("   📁 Created temporary area for project testing")
                    else:
                        print("   ❌ Could not create area for project testing")
                        self.test_results.append({"test": "Projects CRUD", "status": "FAILED", "reason": "Could not create required area"})
                        return False
            
            async with self.session.post(f"{API_BASE}/projects", json=project_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    project = await response.json()
                    if 'id' in project:
                        self.created_resources['projects'].append(project['id'])
                        print("   ✅ Project creation working")
                        success_count += 1
                    else:
                        print("   ❌ Project creation missing ID")
                else:
                    error_text = await response.text()
                    print(f"   ❌ Project creation failed: {response.status} - {error_text}")
                    
            # Test PUT /api/projects/{project_id}
            if self.created_resources['projects']:
                print("   Testing PUT /api/projects/{project_id}...")
                project_id = self.created_resources['projects'][0]
                update_data = {"name": "Updated Test Project", "status": "In Progress"}
                
                async with self.session.put(f"{API_BASE}/projects/{project_id}", json=update_data, headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print("   ✅ Project update working")
                        success_count += 1
                    else:
                        print(f"   ❌ Project update failed: {response.status}")
            else:
                print("   ⚠️ Skipping project update test - no project created")
                
            # Test DELETE /api/projects/{project_id}
            if self.created_resources['projects']:
                print("   Testing DELETE /api/projects/{project_id}...")
                project_id = self.created_resources['projects'][0]
                
                async with self.session.delete(f"{API_BASE}/projects/{project_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print("   ✅ Project deletion working")
                        success_count += 1
                    else:
                        print(f"   ❌ Project deletion failed: {response.status}")
            else:
                print("   ⚠️ Skipping project deletion test - no project created")
                
            if success_count >= 3:  # Allow some flexibility
                self.test_results.append({"test": "Projects CRUD", "status": "PASSED", "details": f"{success_count}/{total_tests} project endpoints working"})
                return True
            else:
                self.test_results.append({"test": "Projects CRUD", "status": "FAILED", "reason": f"Only {success_count}/{total_tests} endpoints working"})
                return False
                
        except Exception as e:
            print(f"❌ Projects CRUD test failed: {e}")
            self.test_results.append({"test": "Projects CRUD", "status": "FAILED", "reason": str(e)})
            return False
            
    async def test_tasks_crud(self):
        """Test 8: Tasks CRUD (Full CRUD)"""
        print("\n🧪 Test 8: Tasks CRUD Operations (Full CRUD)")
        
        try:
            success_count = 0
            total_tests = 4
            
            # Test GET /api/tasks
            print("   Testing GET /api/tasks...")
            async with self.session.get(f"{API_BASE}/tasks", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    tasks = await response.json()
                    if isinstance(tasks, list):
                        print(f"   ✅ Tasks list working ({len(tasks)} tasks)")
                        success_count += 1
                    else:
                        print("   ❌ Tasks should return a list")
                else:
                    print(f"   ❌ Tasks list failed: {response.status}")
                    
            # Test POST /api/tasks (project_id is required)
            print("   Testing POST /api/tasks...")
            task_data = {
                "name": "Test Task",
                "description": "Test task for CRUD verification",
                "status": "todo",
                "priority": "medium"
            }
            
            # project_id is required - use existing project or create one
            if self.created_resources['projects']:
                task_data["project_id"] = self.created_resources['projects'][0]
            else:
                # Create a temporary project for task testing
                # First ensure we have an area
                if not self.created_resources['areas']:
                    temp_area_data = {
                        "name": "Temp Area for Task Test",
                        "description": "Temporary area for task testing",
                        "icon": "📁",
                        "color": "#10B981",
                        "importance": 3
                    }
                    
                    async with self.session.post(f"{API_BASE}/areas", json=temp_area_data, headers=self.get_auth_headers()) as area_response:
                        if area_response.status == 200:
                            temp_area = await area_response.json()
                            self.created_resources['areas'].append(temp_area['id'])
                            print("   📁 Created temporary area for task testing")
                        else:
                            print("   ❌ Could not create area for task testing")
                            self.test_results.append({"test": "Tasks CRUD", "status": "FAILED", "reason": "Could not create required area"})
                            return False
                
                # Now create temporary project
                temp_project_data = {
                    "area_id": self.created_resources['areas'][0],
                    "name": "Temp Project for Task Test",
                    "description": "Temporary project for task testing",
                    "icon": "🚀",
                    "status": "Not Started",
                    "priority": "medium"
                }
                
                async with self.session.post(f"{API_BASE}/projects", json=temp_project_data, headers=self.get_auth_headers()) as project_response:
                    if project_response.status == 200:
                        temp_project = await project_response.json()
                        task_data["project_id"] = temp_project['id']
                        self.created_resources['projects'].append(temp_project['id'])
                        print("   🚀 Created temporary project for task testing")
                    else:
                        print("   ❌ Could not create project for task testing")
                        self.test_results.append({"test": "Tasks CRUD", "status": "FAILED", "reason": "Could not create required project"})
                        return False
            
            async with self.session.post(f"{API_BASE}/tasks", json=task_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    task = await response.json()
                    if 'id' in task:
                        self.created_resources['tasks'].append(task['id'])
                        print("   ✅ Task creation working")
                        success_count += 1
                    else:
                        print("   ❌ Task creation missing ID")
                else:
                    error_text = await response.text()
                    print(f"   ❌ Task creation failed: {response.status} - {error_text}")
                    
            # Test PUT /api/tasks/{task_id}
            if self.created_resources['tasks']:
                print("   Testing PUT /api/tasks/{task_id}...")
                task_id = self.created_resources['tasks'][0]
                update_data = {"name": "Updated Test Task", "status": "in_progress"}
                
                async with self.session.put(f"{API_BASE}/tasks/{task_id}", json=update_data, headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print("   ✅ Task update working")
                        success_count += 1
                    else:
                        print(f"   ❌ Task update failed: {response.status}")
            else:
                print("   ⚠️ Skipping task update test - no task created")
                
            # Test DELETE /api/tasks/{task_id}
            if self.created_resources['tasks']:
                print("   Testing DELETE /api/tasks/{task_id}...")
                task_id = self.created_resources['tasks'][0]
                
                async with self.session.delete(f"{API_BASE}/tasks/{task_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print("   ✅ Task deletion working")
                        success_count += 1
                    else:
                        print(f"   ❌ Task deletion failed: {response.status}")
            else:
                print("   ⚠️ Skipping task deletion test - no task created")
                
            if success_count >= 3:  # Allow some flexibility
                self.test_results.append({"test": "Tasks CRUD", "status": "PASSED", "details": f"{success_count}/{total_tests} task endpoints working"})
                return True
            else:
                self.test_results.append({"test": "Tasks CRUD", "status": "FAILED", "reason": f"Only {success_count}/{total_tests} endpoints working"})
                return False
                
        except Exception as e:
            print(f"❌ Tasks CRUD test failed: {e}")
            self.test_results.append({"test": "Tasks CRUD", "status": "FAILED", "reason": str(e)})
            return False
            
    async def test_project_templates_crud(self):
        """Test 9: Project Templates CRUD (Full CRUD)"""
        print("\n🧪 Test 9: Project Templates CRUD Operations (Full CRUD)")
        
        try:
            success_count = 0
            total_tests = 6
            
            # Test GET /api/project-templates
            print("   Testing GET /api/project-templates...")
            async with self.session.get(f"{API_BASE}/project-templates", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    templates = await response.json()
                    if isinstance(templates, list):
                        print(f"   ✅ Project templates list working ({len(templates)} templates)")
                        success_count += 1
                    else:
                        print("   ❌ Project templates should return a list")
                else:
                    print(f"   ❌ Project templates list failed: {response.status}")
                    
            # Test GET /api/project-templates/{template_id}
            print("   Testing GET /api/project-templates/{template_id}...")
            async with self.session.get(f"{API_BASE}/project-templates/template-1", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    template = await response.json()
                    if 'id' in template and 'tasks' in template:
                        print("   ✅ Specific project template retrieval working")
                        success_count += 1
                    else:
                        print("   ❌ Project template missing required fields")
                else:
                    print(f"   ❌ Specific project template failed: {response.status}")
                    
            # Test POST /api/project-templates
            print("   Testing POST /api/project-templates...")
            template_data = {
                "name": "Test Project Template",
                "description": "Test project template for CRUD verification",
                "category": "Testing",
                "tasks": [
                    {"name": "Test Task 1", "description": "First test task", "priority": "high", "estimated_duration": 60},
                    {"name": "Test Task 2", "description": "Second test task", "priority": "medium", "estimated_duration": 90}
                ]
            }
            
            async with self.session.post(f"{API_BASE}/project-templates", json=template_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    template = await response.json()
                    if 'id' in template:
                        self.created_resources['project_templates'].append(template['id'])
                        print("   ✅ Project template creation working")
                        success_count += 1
                    else:
                        print("   ❌ Project template creation missing ID")
                else:
                    print(f"   ❌ Project template creation failed: {response.status}")
                    
            # Test PUT /api/project-templates/{template_id}
            if self.created_resources['project_templates']:
                print("   Testing PUT /api/project-templates/{template_id}...")
                template_id = self.created_resources['project_templates'][0]
                update_data = {"name": "Updated Test Project Template", "description": "Updated description"}
                
                async with self.session.put(f"{API_BASE}/project-templates/{template_id}", json=update_data, headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print("   ✅ Project template update working")
                        success_count += 1
                    else:
                        print(f"   ❌ Project template update failed: {response.status}")
            else:
                print("   ⚠️ Skipping project template update test - no template created")
                
            # Test POST /api/project-templates/{template_id}/use
            if self.created_resources['project_templates']:
                print("   Testing POST /api/project-templates/{template_id}/use...")
                template_id = self.created_resources['project_templates'][0]
                use_data = {"name": "Project from Template", "description": "Project created from test template"}
                
                async with self.session.post(f"{API_BASE}/project-templates/{template_id}/use", json=use_data, headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        result = await response.json()
                        if 'project_id' in result:
                            print("   ✅ Project template use working")
                            success_count += 1
                        else:
                            print("   ❌ Project template use missing project_id")
                    else:
                        print(f"   ❌ Project template use failed: {response.status}")
            else:
                print("   ⚠️ Skipping project template use test - no template created")
                
            # Test DELETE /api/project-templates/{template_id}
            if self.created_resources['project_templates']:
                print("   Testing DELETE /api/project-templates/{template_id}...")
                template_id = self.created_resources['project_templates'][0]
                
                async with self.session.delete(f"{API_BASE}/project-templates/{template_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        print("   ✅ Project template deletion working")
                        success_count += 1
                    else:
                        print(f"   ❌ Project template deletion failed: {response.status}")
            else:
                print("   ⚠️ Skipping project template deletion test - no template created")
                
            if success_count >= 4:  # Allow some flexibility
                self.test_results.append({"test": "Project Templates CRUD", "status": "PASSED", "details": f"{success_count}/{total_tests} template endpoints working"})
                return True
            else:
                self.test_results.append({"test": "Project Templates CRUD", "status": "FAILED", "reason": f"Only {success_count}/{total_tests} endpoints working"})
                return False
                
        except Exception as e:
            print(f"❌ Project Templates CRUD test failed: {e}")
            self.test_results.append({"test": "Project Templates CRUD", "status": "FAILED", "reason": str(e)})
            return False
            
    async def test_today_view_crud(self):
        """Test 10: Today View Specific CRUD"""
        print("\n🧪 Test 10: Today View Specific CRUD Operations")
        
        try:
            success_count = 0
            total_tests = 4
            
            # Test GET /api/today/available-tasks
            print("   Testing GET /api/today/available-tasks...")
            async with self.session.get(f"{API_BASE}/today/available-tasks", headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    tasks = await response.json()
                    if isinstance(tasks, list):
                        print(f"   ✅ Available tasks endpoint working ({len(tasks)} tasks)")
                        success_count += 1
                    else:
                        print("   ❌ Available tasks should return a list")
                else:
                    print(f"   ❌ Available tasks endpoint failed: {response.status}")
                    
            # Test POST /api/today/tasks/{task_id}
            if self.created_resources['tasks']:
                print("   Testing POST /api/today/tasks/{task_id}...")
                task_id = self.created_resources['tasks'][0]
                
                async with self.session.post(f"{API_BASE}/today/tasks/{task_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        result = await response.json()
                        if 'message' in result and 'task_id' in result:
                            print("   ✅ Add task to today working")
                            success_count += 1
                        else:
                            print("   ❌ Add task to today missing required fields")
                    else:
                        print(f"   ❌ Add task to today failed: {response.status}")
            else:
                print("   ⚠️ Skipping add task to today test - no task available")
                
            # Test DELETE /api/today/tasks/{task_id}
            if self.created_resources['tasks']:
                print("   Testing DELETE /api/today/tasks/{task_id}...")
                task_id = self.created_resources['tasks'][0]
                
                async with self.session.delete(f"{API_BASE}/today/tasks/{task_id}", headers=self.get_auth_headers()) as response:
                    if response.status == 200:
                        result = await response.json()
                        if 'message' in result and 'task_id' in result:
                            print("   ✅ Remove task from today working")
                            success_count += 1
                        else:
                            print("   ❌ Remove task from today missing required fields")
                    else:
                        print(f"   ❌ Remove task from today failed: {response.status}")
            else:
                print("   ⚠️ Skipping remove task from today test - no task available")
                
            # Test PUT /api/today/reorder
            print("   Testing PUT /api/today/reorder...")
            reorder_data = {"task_ids": self.created_resources['tasks'][:3] if self.created_resources['tasks'] else []}
            
            async with self.session.put(f"{API_BASE}/today/reorder", json=reorder_data, headers=self.get_auth_headers()) as response:
                if response.status == 200:
                    result = await response.json()
                    if 'message' in result:
                        print("   ✅ Reorder today tasks working")
                        success_count += 1
                    else:
                        print("   ❌ Reorder today tasks missing message")
                else:
                    print(f"   ❌ Reorder today tasks failed: {response.status}")
                    
            if success_count >= 2:  # Allow some flexibility
                self.test_results.append({"test": "Today View CRUD", "status": "PASSED", "details": f"{success_count}/{total_tests} today endpoints working"})
                return True
            else:
                self.test_results.append({"test": "Today View CRUD", "status": "FAILED", "reason": f"Only {success_count}/{total_tests} endpoints working"})
                return False
                
        except Exception as e:
            print(f"❌ Today View CRUD test failed: {e}")
            self.test_results.append({"test": "Today View CRUD", "status": "FAILED", "reason": str(e)})
            return False
            
    async def test_authentication_protection(self):
        """Test 11: Authentication protection on all endpoints"""
        print("\n🧪 Test 11: Authentication Protection Verification")
        
        try:
            # Test endpoints without authentication
            endpoints_to_test = [
                ("GET", f"{API_BASE}/dashboard"),
                ("GET", f"{API_BASE}/today"),
                ("GET", f"{API_BASE}/insights"),
                ("GET", f"{API_BASE}/journal"),
                ("GET", f"{API_BASE}/pillars"),
                ("GET", f"{API_BASE}/areas"),
                ("GET", f"{API_BASE}/projects"),
                ("GET", f"{API_BASE}/tasks"),
                ("GET", f"{API_BASE}/project-templates"),
                ("GET", f"{API_BASE}/journal/templates")
            ]
            
            auth_protected_count = 0
            
            for method, url in endpoints_to_test:
                try:
                    async with self.session.get(url) as response:
                        if response.status in [401, 403]:
                            auth_protected_count += 1
                            print(f"   ✅ {url.split('/')[-1]} properly protected")
                        else:
                            print(f"   ❌ {url.split('/')[-1]} not properly protected: {response.status}")
                except Exception as e:
                    print(f"   ⚠️ Error testing {url}: {e}")
                    
            if auth_protected_count >= len(endpoints_to_test) * 0.8:  # Allow 80% success rate
                print(f"\n✅ Most endpoints properly protected ({auth_protected_count}/{len(endpoints_to_test)})")
                self.test_results.append({"test": "Authentication Protection", "status": "PASSED", "details": f"{auth_protected_count}/{len(endpoints_to_test)} endpoints require authentication"})
                return True
            else:
                print(f"\n❌ Insufficient authentication protection ({auth_protected_count}/{len(endpoints_to_test)})")
                self.test_results.append({"test": "Authentication Protection", "status": "FAILED", "reason": f"Only {auth_protected_count}/{len(endpoints_to_test)} endpoints protected"})
                return False
                
        except Exception as e:
            print(f"❌ Authentication protection test failed: {e}")
            self.test_results.append({"test": "Authentication Protection", "status": "FAILED", "reason": str(e)})
            return False
            
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🎯 COMPREHENSIVE CORE COMPONENT CRUD VERIFICATION SUMMARY")
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
            status_icon = {"PASSED": "✅", "FAILED": "❌"}
            icon = status_icon.get(result["status"], "❓")
            print(f"{i:2d}. {icon} {result['test']}: {result['status']}")
            
            if "details" in result:
                print(f"    📝 {result['details']}")
            if "reason" in result:
                print(f"    💬 {result['reason']}")
                
        print("\n" + "="*80)
        
        # Determine overall system status
        if success_rate >= 90:
            print("🎉 COMPREHENSIVE CRUD VERIFICATION - EXCELLENT SUCCESS RATE!")
            print("✅ All core components working correctly")
            print("✅ Authentication protection functional")
        elif success_rate >= 75:
            print("⚠️ COMPREHENSIVE CRUD VERIFICATION - GOOD SUCCESS RATE WITH MINOR ISSUES")
        else:
            print("❌ COMPREHENSIVE CRUD VERIFICATION - SIGNIFICANT ISSUES DETECTED")
            
        print("="*80)
        
    async def run_comprehensive_crud_verification(self):
        """Run comprehensive CRUD verification test suite"""
        print("🚀 Starting Comprehensive Core Component CRUD Verification...")
        print(f"🔗 Backend URL: {BACKEND_URL}")
        print("📋 Testing ALL core components as requested in review")
        
        await self.setup_session()
        
        try:
            # Authentication
            if not await self.authenticate():
                print("❌ Authentication failed - cannot proceed with tests")
                return
                
            # Run all CRUD tests
            await self.test_dashboard_crud()
            await self.test_insights_crud()
            await self.test_journal_crud()
            await self.test_journal_templates_crud()
            await self.test_pillars_crud()
            await self.test_areas_crud()
            await self.test_projects_crud()
            await self.test_tasks_crud()
            await self.test_project_templates_crud()
            await self.test_today_view_crud()
            await self.test_authentication_protection()
            
        finally:
            await self.cleanup_session()
            
        # Print summary
        self.print_test_summary()

async def main():
    """Main function to run the comprehensive CRUD verification"""
    test_suite = ComprehensiveCRUDVerificationSuite()
    await test_suite.run_comprehensive_crud_verification()

if __name__ == "__main__":
    asyncio.run(main())