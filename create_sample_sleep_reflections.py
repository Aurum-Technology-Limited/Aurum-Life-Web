#!/usr/bin/env python3
"""
Create Sample Sleep Reflections
Creates realistic sample data for frontend testing
"""

import requests
import json
from datetime import datetime, date, timedelta

# Configuration
BACKEND_URL = "https://b7ef6377-f814-4d39-824c-6237cb92693c.preview.emergentagent.com/api"
TEST_EMAIL = "marc.alleyne@aurumtechnologyltd.com"
TEST_PASSWORD = "password"

def authenticate():
    """Authenticate and get token"""
    session = requests.Session()
    
    response = session.post(f"{BACKEND_URL}/auth/login", json={
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    })
    
    if response.status_code == 200:
        data = response.json()
        auth_token = data.get('access_token')
        
        if auth_token:
            session.headers.update({
                'Authorization': f'Bearer {auth_token}'
            })
            return session
    
    return None

def create_sample_reflections():
    """Create realistic sample sleep reflections"""
    session = authenticate()
    if not session:
        print("❌ Authentication failed")
        return
    
    # Sample sleep reflections with realistic data
    sample_reflections = [
        {
            "date": (date.today() - timedelta(days=1)).isoformat(),
            "sleep_quality": 8,
            "feeling": "refreshed and energetic",
            "sleep_hours": "7.5 hours",
            "sleep_influences": "Had a relaxing evening routine, avoided screens 1 hour before bed, room temperature was perfect",
            "today_intention": "Focus on completing the quarterly report and take a 20-minute walk during lunch break"
        },
        {
            "date": (date.today() - timedelta(days=2)).isoformat(),
            "sleep_quality": 6,
            "feeling": "somewhat tired",
            "sleep_hours": "6 hours",
            "sleep_influences": "Stayed up late watching a movie, had coffee after 4pm which might have affected sleep",
            "today_intention": "Prioritize the client presentation and make sure to get to bed earlier tonight"
        },
        {
            "date": (date.today() - timedelta(days=3)).isoformat(),
            "sleep_quality": 9,
            "feeling": "amazing and well-rested",
            "sleep_hours": "8 hours",
            "sleep_influences": "Perfect sleep environment, did meditation before bed, no caffeine after 2pm",
            "today_intention": "Tackle the challenging coding tasks first thing in the morning while energy is high"
        },
        {
            "date": (date.today() - timedelta(days=4)).isoformat(),
            "sleep_quality": 4,
            "feeling": "groggy and unfocused",
            "sleep_hours": "5 hours",
            "sleep_influences": "Stress from work deadline, neighbor's dog barking, room was too warm",
            "today_intention": "Take it easy today, focus on simple tasks and plan for better sleep tonight"
        },
        {
            "date": (date.today() - timedelta(days=5)).isoformat(),
            "sleep_quality": 7,
            "feeling": "decent but could be better",
            "sleep_hours": "7 hours",
            "sleep_influences": "Good bedtime routine but woke up once during the night, overall okay sleep",
            "today_intention": "Work on the project documentation and schedule that important meeting"
        }
    ]
    
    created_count = 0
    
    print("🌙 Creating sample sleep reflections...")
    
    for reflection in sample_reflections:
        try:
            response = session.post(f"{BACKEND_URL}/sleep-reflections", json=reflection)
            
            if response.status_code == 200:
                data = response.json()
                created_count += 1
                print(f"✅ Created reflection for {reflection['date']} (Quality: {reflection['sleep_quality']}/10)")
            else:
                print(f"❌ Failed to create reflection for {reflection['date']}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error creating reflection for {reflection['date']}: {str(e)}")
    
    print(f"\n🎉 Successfully created {created_count} sample sleep reflections!")
    
    # Verify by getting all reflections
    try:
        response = session.get(f"{BACKEND_URL}/sleep-reflections")
        if response.status_code == 200:
            reflections = response.json()
            print(f"📊 Total sleep reflections in database: {len(reflections)}")
        else:
            print(f"❌ Failed to verify reflections: {response.status_code}")
    except Exception as e:
        print(f"❌ Error verifying reflections: {str(e)}")

if __name__ == "__main__":
    create_sample_reflections()