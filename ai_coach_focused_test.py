#!/usr/bin/env python3
"""
Focused AI Coach MVP Test - Weekly Review and Obstacle Analysis
"""

import requests
import json
import time
from datetime import datetime

def authenticate():
    """Authenticate with the API"""
    try:
        response = requests.post(
            "https://hierarchy-enforcer.preview.emergentagent.com/api/auth/login",
            json={"email": "marc.alleyne@aurumtechnologyltd.com", "password": "Alleyne2025!"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("access_token")
        else:
            print(f"Authentication failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"Authentication error: {e}")
        return None

def test_weekly_review(token):
    """Test weekly strategic review"""
    print("\n📈 TESTING WEEKLY STRATEGIC REVIEW")
    print("=" * 50)
    
    try:
        response = requests.post(
            "https://hierarchy-enforcer.preview.emergentagent.com/api/ai/weekly-review",
            json={},
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Weekly Review Success!")
            print(f"Weekly Summary: {data.get('weekly_summary', 'N/A')}")
            print(f"Projects Completed: {data.get('projects_completed', 0)}")
            print(f"Weekly Points: {data.get('weekly_points', 0)}")
        elif response.status_code == 429:
            print("⏱️ Rate limited - this is expected behavior")
        elif response.status_code == 402:
            print("💰 Quota exceeded - this is expected behavior")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def get_or_create_project(token):
    """Get existing project or create one for testing"""
    try:
        # Try to get existing projects
        response = requests.get(
            "https://hierarchy-enforcer.preview.emergentagent.com/api/projects",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            projects = response.json()
            if projects and len(projects) > 0:
                return projects[0].get("id")
        
        print("No existing projects found, creating test project...")
        
        # Get areas first
        areas_response = requests.get(
            "https://hierarchy-enforcer.preview.emergentagent.com/api/areas",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        area_id = None
        if areas_response.status_code == 200:
            areas = areas_response.json()
            if areas and len(areas) > 0:
                area_id = areas[0].get("id")
        
        if not area_id:
            print("No areas found, cannot create project")
            return None
        
        # Create project
        project_data = {
            "name": "AI Coach Test Project",
            "description": "Test project for AI Coach obstacle analysis",
            "area_id": area_id,
            "priority": "medium",
            "status": "In Progress"
        }
        
        project_response = requests.post(
            "https://hierarchy-enforcer.preview.emergentagent.com/api/projects",
            json=project_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        if project_response.status_code == 200:
            return project_response.json().get("id")
        else:
            print(f"Failed to create project: {project_response.status_code} - {project_response.text}")
            return None
            
    except Exception as e:
        print(f"Error getting/creating project: {e}")
        return None

def test_obstacle_analysis(token):
    """Test obstacle analysis"""
    print("\n🚧 TESTING OBSTACLE ANALYSIS")
    print("=" * 50)
    
    project_id = get_or_create_project(token)
    if not project_id:
        print("❌ Could not get project for testing")
        return
    
    print(f"Using project ID: {project_id}")
    
    # Test valid obstacle analysis
    try:
        request_data = {
            "project_id": project_id,
            "problem_description": "I'm stuck on planning and don't know where to start"
        }
        
        response = requests.post(
            "https://hierarchy-enforcer.preview.emergentagent.com/api/ai/obstacle-analysis",
            json=request_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Obstacle Analysis Success!")
            print(f"Project Name: {data.get('project_name', 'N/A')}")
            suggestions = data.get('suggestions', [])
            print(f"Suggestions ({len(suggestions)}):")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")
        elif response.status_code == 429:
            print("⏱️ Rate limited - this is expected behavior")
        elif response.status_code == 402:
            print("💰 Quota exceeded - this is expected behavior")
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test with invalid project ID
    try:
        print("\nTesting with invalid project ID...")
        invalid_request = {
            "project_id": "invalid-project-id-12345",
            "problem_description": "Test problem"
        }
        
        response = requests.post(
            "https://hierarchy-enforcer.preview.emergentagent.com/api/ai/obstacle-analysis",
            json=invalid_request,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )
        
        print(f"Invalid Project ID Status: {response.status_code}")
        if response.status_code == 404:
            print("✅ Correctly returned 404 for invalid project ID")
        elif response.status_code == 429:
            print("⏱️ Rate limited - cannot test invalid project ID")
        else:
            print(f"❌ Expected 404, got {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing invalid project ID: {e}")

def main():
    print("🤖 AI COACH MVP FOCUSED TESTING")
    print("=" * 50)
    
    # Authenticate
    token = authenticate()
    if not token:
        print("❌ Authentication failed, cannot proceed")
        return
    
    print("✅ Authentication successful")
    
    # Test features
    test_weekly_review(token)
    test_obstacle_analysis(token)
    
    print("\n🎉 Focused testing completed!")

if __name__ == "__main__":
    main()