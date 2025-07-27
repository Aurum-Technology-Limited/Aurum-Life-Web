"""
End-to-End Test for Core User Journey
Aurum Life MVP v1.2

Validates:
1. User registration and authentication
2. Creating full hierarchy (Pillar → Area → Project → Task)
3. Task completion workflow
4. RLS data isolation between users
"""

import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
import asyncio

@pytest.mark.e2e
@pytest.mark.asyncio
class TestCoreUserJourney:
    """Complete E2E test of the core user journey"""
    
    async def test_complete_user_journey(self, client: AsyncClient):
        """Test the complete user journey from registration to task completion"""
        
        # Step 1: Register new user
        user_data = {
            "email": "journey_test@example.com",
            "password": "Test123!@#",
            "first_name": "Journey",
            "last_name": "Test"
        }
        
        register_response = await client.post("/api/auth/register", json=user_data)
        assert register_response.status_code == 201
        
        # Get auth token
        auth_token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        # Step 2: Create Pillar
        pillar_data = {
            "name": "Health & Wellness",
            "description": "Physical and mental health goals",
            "icon": "💪",
            "color": "#4CAF50"
        }
        
        pillar_response = await client.post(
            "/api/pillars", 
            json=pillar_data, 
            headers=headers
        )
        assert pillar_response.status_code == 201
        pillar_id = pillar_response.json()["id"]
        
        # Verify pillar creation
        assert pillar_response.json()["name"] == pillar_data["name"]
        assert pillar_response.json()["user_id"] is not None
        
        # Step 3: Create Area within Pillar
        area_data = {
            "pillar_id": pillar_id,
            "name": "Exercise Routine",
            "description": "Regular physical activity",
            "icon": "🏃",
            "color": "#2196F3"
        }
        
        area_response = await client.post(
            "/api/areas",
            json=area_data,
            headers=headers
        )
        assert area_response.status_code == 201
        area_id = area_response.json()["id"]
        
        # Step 4: Create Project within Area
        project_data = {
            "area_id": area_id,
            "name": "30-Day Fitness Challenge",
            "description": "Complete a 30-day workout program",
            "icon": "🎯",
            "deadline": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            "priority": "high"
        }
        
        project_response = await client.post(
            "/api/projects",
            json=project_data,
            headers=headers
        )
        assert project_response.status_code == 201
        project_id = project_response.json()["id"]
        
        # Step 5: Create Task within Project
        task_data = {
            "project_id": project_id,
            "name": "Day 1: 20 minute cardio",
            "description": "Complete 20 minutes of cardio exercise",
            "priority": "high",
            "due_date": datetime.utcnow().isoformat(),
            "estimated_duration": 20
        }
        
        task_response = await client.post(
            "/api/tasks",
            json=task_data,
            headers=headers
        )
        assert task_response.status_code == 201
        task_id = task_response.json()["id"]
        
        # Step 6: Verify hierarchy is created
        hierarchy_response = await client.get(
            "/api/hierarchy",
            headers=headers
        )
        assert hierarchy_response.status_code == 200
        
        hierarchy = hierarchy_response.json()
        assert len(hierarchy["pillars"]) == 1
        assert hierarchy["pillars"][0]["area_count"] == 1
        assert hierarchy["pillars"][0]["project_count"] == 1
        assert hierarchy["pillars"][0]["task_count"] == 1
        
        # Step 7: Get Today view
        today_response = await client.get(
            "/api/today/tasks",
            headers=headers
        )
        assert today_response.status_code == 200
        
        today_tasks = today_response.json()["tasks"]
        assert len(today_tasks) == 1
        assert today_tasks[0]["id"] == task_id
        assert today_tasks[0]["project_name"] == project_data["name"]
        assert today_tasks[0]["area_name"] == area_data["name"]
        assert today_tasks[0]["pillar_name"] == pillar_data["name"]
        
        # Step 8: Complete the task
        complete_response = await client.patch(
            f"/api/tasks/{task_id}",
            json={"completed": True},
            headers=headers
        )
        assert complete_response.status_code == 200
        
        # Step 9: Verify task is completed
        task_detail_response = await client.get(
            f"/api/tasks/{task_id}",
            headers=headers
        )
        assert task_detail_response.status_code == 200
        assert task_detail_response.json()["completed"] is True
        assert task_detail_response.json()["completed_at"] is not None
        
        # Step 10: Verify progress is updated
        updated_hierarchy = await client.get(
            "/api/hierarchy",
            headers=headers
        )
        assert updated_hierarchy.status_code == 200
        assert updated_hierarchy.json()["pillars"][0]["completed_task_count"] == 1
        assert updated_hierarchy.json()["pillars"][0]["progress_percentage"] == 100.0
        
        # Success! Core journey completed
        print("✅ Core user journey test passed!")
    
    async def test_rls_data_isolation(self, client: AsyncClient):
        """Test that users cannot access each other's data"""
        
        # Create User A
        user_a_data = {
            "email": "user_a@example.com",
            "password": "UserA123!@#",
            "first_name": "User",
            "last_name": "A"
        }
        
        response_a = await client.post("/api/auth/register", json=user_a_data)
        assert response_a.status_code == 201
        token_a = response_a.json()["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}
        
        # Create User B
        user_b_data = {
            "email": "user_b@example.com",
            "password": "UserB123!@#",
            "first_name": "User",
            "last_name": "B"
        }
        
        response_b = await client.post("/api/auth/register", json=user_b_data)
        assert response_b.status_code == 201
        token_b = response_b.json()["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}
        
        # User A creates a pillar
        pillar_data = {
            "name": "User A's Private Pillar",
            "description": "This should only be visible to User A"
        }
        
        pillar_response = await client.post(
            "/api/pillars",
            json=pillar_data,
            headers=headers_a
        )
        assert pillar_response.status_code == 201
        pillar_id = pillar_response.json()["id"]
        
        # User B tries to access User A's pillar - should fail
        unauthorized_get = await client.get(
            f"/api/pillars/{pillar_id}",
            headers=headers_b
        )
        assert unauthorized_get.status_code == 404  # Not found due to RLS
        
        # User B tries to update User A's pillar - should fail
        unauthorized_update = await client.patch(
            f"/api/pillars/{pillar_id}",
            json={"name": "Hacked!"},
            headers=headers_b
        )
        assert unauthorized_update.status_code == 404
        
        # User B tries to delete User A's pillar - should fail
        unauthorized_delete = await client.delete(
            f"/api/pillars/{pillar_id}",
            headers=headers_b
        )
        assert unauthorized_delete.status_code == 404
        
        # User B lists their pillars - should not see User A's
        user_b_pillars = await client.get(
            "/api/pillars",
            headers=headers_b
        )
        assert user_b_pillars.status_code == 200
        assert len(user_b_pillars.json()) == 0  # User B has no pillars
        
        # User A can still access their own pillar
        user_a_get = await client.get(
            f"/api/pillars/{pillar_id}",
            headers=headers_a
        )
        assert user_a_get.status_code == 200
        assert user_a_get.json()["name"] == pillar_data["name"]
        
        print("✅ RLS data isolation test passed!")
    
    async def test_performance_requirements(self, client: AsyncClient):
        """Test that API responses meet performance requirements"""
        
        # Create test user
        user_data = {
            "email": "perf_test@example.com",
            "password": "Perf123!@#",
            "first_name": "Perf",
            "last_name": "Test"
        }
        
        register_response = await client.post("/api/auth/register", json=user_data)
        assert register_response.status_code == 201
        headers = {"Authorization": f"Bearer {register_response.json()['access_token']}"}
        
        # Create test data
        pillar_id = await self._create_test_hierarchy(client, headers)
        
        # Test critical endpoints for performance
        critical_endpoints = [
            ("/api/today/tasks", "Today view"),
            ("/api/hierarchy", "Hierarchy view"),
            (f"/api/pillars/{pillar_id}", "Single pillar"),
            ("/api/tasks?limit=50", "Task list")
        ]
        
        for endpoint, name in critical_endpoints:
            # Warm up
            await client.get(endpoint, headers=headers)
            
            # Measure response time
            start_time = asyncio.get_event_loop().time()
            response = await client.get(endpoint, headers=headers)
            end_time = asyncio.get_event_loop().time()
            
            response_time_ms = (end_time - start_time) * 1000
            
            assert response.status_code == 200
            assert response_time_ms < 150, f"{name} took {response_time_ms}ms (target: <150ms)"
            
            print(f"✅ {name}: {response_time_ms:.2f}ms")
        
        print("✅ Performance requirements test passed!")
    
    async def _create_test_hierarchy(self, client: AsyncClient, headers: dict) -> str:
        """Helper to create test hierarchy data"""
        # Create pillar
        pillar_resp = await client.post(
            "/api/pillars",
            json={"name": "Test Pillar"},
            headers=headers
        )
        pillar_id = pillar_resp.json()["id"]
        
        # Create area
        area_resp = await client.post(
            "/api/areas",
            json={"pillar_id": pillar_id, "name": "Test Area"},
            headers=headers
        )
        area_id = area_resp.json()["id"]
        
        # Create project
        project_resp = await client.post(
            "/api/projects",
            json={"area_id": area_id, "name": "Test Project"},
            headers=headers
        )
        project_id = project_resp.json()["id"]
        
        # Create multiple tasks
        for i in range(10):
            await client.post(
                "/api/tasks",
                json={
                    "project_id": project_id,
                    "name": f"Test Task {i+1}",
                    "due_date": (datetime.utcnow() + timedelta(days=i)).isoformat()
                },
                headers=headers
            )
        
        return pillar_id