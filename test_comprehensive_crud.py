#!/usr/bin/env python3
"""
Comprehensive CRUD Testing for Entire Hierarchy
Test Create, Read, Update, Delete for Pillars → Areas → Projects → Tasks
"""

import asyncio
import aiohttp
import json

class ComprehensiveCRUDTest:
    def __init__(self):
        self.base_url = "http://localhost:8001/api"
        self.session = None
        self.auth_token = None
        self.test_data = {}
        
    async def setup(self):
        """Setup and authenticate"""
        self.session = aiohttp.ClientSession()
        
        # Login
        login_data = {
            "email": "nav.test@aurumlife.com",
            "password": "testpassword123"
        }
        
        async with self.session.post(f"{self.base_url}/auth/login", json=login_data) as response:
            if response.status == 200:
                data = await response.json()
                self.auth_token = data["access_token"]
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status}")
                return False
                
    async def test_pillar_crud(self):
        """Test Pillar CRUD operations"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        print("\n🏛️ TESTING PILLAR CRUD")
        print("="*30)
        
        # CREATE Pillar
        print("1️⃣ Testing Pillar Creation...")
        pillar_data = {
            "name": "CRUD Test Pillar",
            "description": "Testing pillar CRUD operations",
            "icon": "🧪",
            "color": "#FF5722"
        }
        
        async with self.session.post(f"{self.base_url}/pillars", json=pillar_data, headers=headers) as response:
            if response.status == 200:
                pillar = await response.json()
                self.test_data['pillar_id'] = pillar['id']
                print(f"✅ Pillar created: {pillar['id']}")
            else:
                error_text = await response.text()
                print(f"❌ Pillar creation failed: {response.status} - {error_text}")
                return False
        
        # READ Pillar
        print("2️⃣ Testing Pillar Read...")
        async with self.session.get(f"{self.base_url}/pillars/{self.test_data['pillar_id']}", headers=headers) as response:
            if response.status == 200:
                pillar = await response.json()
                print(f"✅ Pillar read: {pillar['name']}")
            else:
                print(f"❌ Pillar read failed: {response.status}")
                return False
        
        # UPDATE Pillar
        print("3️⃣ Testing Pillar Update...")
        update_data = {
            "name": "CRUD Test Pillar (Updated)",
            "description": "Updated description"
        }
        
        async with self.session.put(f"{self.base_url}/pillars/{self.test_data['pillar_id']}", json=update_data, headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Pillar updated successfully")
            else:
                error_text = await response.text()
                print(f"❌ Pillar update failed: {response.status} - {error_text}")
                return False
        
        print("✅ Pillar CRUD tests passed!")
        return True
        
    async def test_area_crud(self):
        """Test Area CRUD operations"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        print("\n🗂️ TESTING AREA CRUD")
        print("="*30)
        
        # CREATE Area
        print("1️⃣ Testing Area Creation...")
        area_data = {
            "name": "CRUD Test Area",
            "description": "Testing area CRUD operations",
            "pillar_id": self.test_data['pillar_id'],
            "icon": "📁",
            "color": "#2196F3"
        }
        
        async with self.session.post(f"{self.base_url}/areas", json=area_data, headers=headers) as response:
            if response.status == 200:
                area = await response.json()
                self.test_data['area_id'] = area['id']
                print(f"✅ Area created: {area['id']}")
            else:
                error_text = await response.text()
                print(f"❌ Area creation failed: {response.status} - {error_text}")
                return False
        
        # READ Area
        print("2️⃣ Testing Area Read...")
        async with self.session.get(f"{self.base_url}/areas/{self.test_data['area_id']}", headers=headers) as response:
            if response.status == 200:
                area = await response.json()
                print(f"✅ Area read: {area['name']}")
            else:
                print(f"❌ Area read failed: {response.status}")
                return False
        
        # UPDATE Area
        print("3️⃣ Testing Area Update...")
        update_data = {
            "name": "CRUD Test Area (Updated)",
            "description": "Updated area description"
        }
        
        async with self.session.put(f"{self.base_url}/areas/{self.test_data['area_id']}", json=update_data, headers=headers) as response:
            if response.status == 200:
                print(f"✅ Area updated successfully")
            else:
                error_text = await response.text()
                print(f"❌ Area update failed: {response.status} - {error_text}")
                return False
        
        print("✅ Area CRUD tests passed!")
        return True
        
    async def test_project_crud(self):
        """Test Project CRUD operations"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        print("\n📂 TESTING PROJECT CRUD")
        print("="*30)
        
        # CREATE Project
        print("1️⃣ Testing Project Creation...")
        project_data = {
            "name": "CRUD Test Project",
            "description": "Testing project CRUD operations",
            "area_id": self.test_data['area_id'],
            "status": "Active"
        }
        
        async with self.session.post(f"{self.base_url}/projects", json=project_data, headers=headers) as response:
            if response.status == 200:
                project = await response.json()
                self.test_data['project_id'] = project['id']
                print(f"✅ Project created: {project['id']}")
            else:
                error_text = await response.text()
                print(f"❌ Project creation failed: {response.status} - {error_text}")
                return False
        
        # READ Project
        print("2️⃣ Testing Project Read...")
        async with self.session.get(f"{self.base_url}/projects/{self.test_data['project_id']}", headers=headers) as response:
            if response.status == 200:
                project = await response.json()
                print(f"✅ Project read: {project['name']}")
            else:
                print(f"❌ Project read failed: {response.status}")
                return False
        
        # UPDATE Project
        print("3️⃣ Testing Project Update...")
        update_data = {
            "name": "CRUD Test Project (Updated)",
            "status": "In Progress"
        }
        
        async with self.session.put(f"{self.base_url}/projects/{self.test_data['project_id']}", json=update_data, headers=headers) as response:
            if response.status == 200:
                print(f"✅ Project updated successfully")
            else:
                error_text = await response.text()
                print(f"❌ Project update failed: {response.status} - {error_text}")
                return False
        
        print("✅ Project CRUD tests passed!")
        return True
        
    async def test_task_crud(self):
        """Test Task CRUD operations"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        print("\n✅ TESTING TASK CRUD")
        print("="*30)
        
        # CREATE Task
        print("1️⃣ Testing Task Creation...")
        task_data = {
            "name": "CRUD Test Task",
            "description": "Testing task CRUD operations",
            "project_id": self.test_data['project_id'],
            "priority": "medium",
            "completed": False
        }
        
        async with self.session.post(f"{self.base_url}/tasks", json=task_data, headers=headers) as response:
            if response.status == 200:
                task = await response.json()
                self.test_data['task_id'] = task['id']
                print(f"✅ Task created: {task['id']}")
            else:
                error_text = await response.text()
                print(f"❌ Task creation failed: {response.status} - {error_text}")
                return False
        
        # READ Task
        print("2️⃣ Testing Task Read...")
        async with self.session.get(f"{self.base_url}/tasks/{self.test_data['task_id']}", headers=headers) as response:
            if response.status == 200:
                task = await response.json()
                print(f"✅ Task read: {task['name']}")
            else:
                print(f"❌ Task read failed: {response.status}")
                return False
        
        # UPDATE Task
        print("3️⃣ Testing Task Update...")
        update_data = {
            "name": "CRUD Test Task (Updated)",
            "completed": True
        }
        
        async with self.session.put(f"{self.base_url}/tasks/{self.test_data['task_id']}", json=update_data, headers=headers) as response:
            if response.status == 200:
                print(f"✅ Task updated successfully")
            else:
                error_text = await response.text()
                print(f"❌ Task update failed: {response.status} - {error_text}")
                return False
        
        print("✅ Task CRUD tests passed!")
        return True
        
    async def test_deletion_cascade(self):
        """Test deletion operations in reverse order"""
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        print("\n🗑️ TESTING DELETION CASCADE")
        print("="*30)
        
        # DELETE Task
        print("1️⃣ Testing Task Deletion...")
        async with self.session.delete(f"{self.base_url}/tasks/{self.test_data['task_id']}", headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Task deleted: {result['message']}")
            else:
                error_text = await response.text()
                print(f"❌ Task deletion failed: {response.status} - {error_text}")
                return False
        
        # DELETE Project
        print("2️⃣ Testing Project Deletion...")
        async with self.session.delete(f"{self.base_url}/projects/{self.test_data['project_id']}", headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Project deleted: {result['message']}")
            else:
                error_text = await response.text()
                print(f"❌ Project deletion failed: {response.status} - {error_text}")
                return False
        
        # DELETE Area
        print("3️⃣ Testing Area Deletion...")
        async with self.session.delete(f"{self.base_url}/areas/{self.test_data['area_id']}", headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Area deleted: {result['message']}")
            else:
                error_text = await response.text()
                print(f"❌ Area deletion failed: {response.status} - {error_text}")
                return False
        
        # DELETE Pillar
        print("4️⃣ Testing Pillar Deletion...")
        async with self.session.delete(f"{self.base_url}/pillars/{self.test_data['pillar_id']}", headers=headers) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✅ Pillar deleted: {result['message']}")
            else:
                error_text = await response.text()
                print(f"❌ Pillar deletion failed: {response.status} - {error_text}")
                return False
        
        print("✅ All deletion tests passed!")
        return True
        
    async def cleanup(self):
        """Cleanup session"""
        if self.session:
            await self.session.close()

async def main():
    """Run comprehensive CRUD testing"""
    test = ComprehensiveCRUDTest()
    
    try:
        print("🧪 COMPREHENSIVE CRUD TESTING FOR HIERARCHY")
        print("="*60)
        print("Testing: Pillars → Areas → Projects → Tasks")
        print("Operations: Create, Read, Update, Delete")
        print()
        
        if not await test.setup():
            return
        
        # Test creation and CRUD operations
        tests = [
            ("Pillar CRUD", test.test_pillar_crud),
            ("Area CRUD", test.test_area_crud),
            ("Project CRUD", test.test_project_crud),
            ("Task CRUD", test.test_task_crud),
            ("Deletion CASCADE", test.test_deletion_cascade)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if await test_func():
                    passed += 1
                else:
                    print(f"❌ {test_name} FAILED")
                    break
            except Exception as e:
                print(f"❌ {test_name} ERROR: {e}")
                break
        
        print(f"\n📊 FINAL RESULTS")
        print("="*30)
        print(f"Passed: {passed}/{total} tests")
        
        if passed == total:
            print("🎉 ALL CRUD OPERATIONS WORKING PERFECTLY!")
        else:
            print("⚠️ Some CRUD operations need attention")
            
    finally:
        await test.cleanup()

if __name__ == "__main__":
    asyncio.run(main())