#!/usr/bin/env python3
"""
Analytics User Data Sync - Ensure test user has data for analytics
"""

import asyncio
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime

# Load environment variables
load_dotenv('/app/backend/.env')

class AnalyticsDataSync:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.service_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        self.supabase = None
        self.auth_user_id = "272edb74-8be3-4504-818c-b1dd42c63ebe"  # Known working auth user ID
        
    async def initialize(self):
        """Initialize Supabase client"""
        self.supabase = create_client(self.supabase_url, self.service_key)
        print("✅ Supabase client initialized")
        
    async def create_analytics_test_data(self):
        """Create test data specifically for analytics testing"""
        try:
            print(f"📊 Creating analytics test data for user: {self.auth_user_id}")
            
            # Step 1: Create test pillars for the auth user
            pillars_data = [
                {
                    "id": str(uuid.uuid4()),
                    "user_id": self.auth_user_id,
                    "name": "Health & Wellness",
                    "description": "Physical and mental health",
                    "icon": "💪",
                    "color": "#4CAF50",
                    "created_at": datetime.utcnow().isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "user_id": self.auth_user_id,
                    "name": "Career Development",
                    "description": "Professional growth",
                    "icon": "🚀", 
                    "color": "#2196F3",
                    "created_at": datetime.utcnow().isoformat()
                },
                {
                    "id": str(uuid.uuid4()),
                    "user_id": self.auth_user_id,
                    "name": "Personal Relationships",
                    "description": "Family and friends",
                    "icon": "❤️",
                    "color": "#E91E63", 
                    "created_at": datetime.utcnow().isoformat()
                }
            ]
            
            created_pillars = []
            for pillar_data in pillars_data:
                result = self.supabase.table('pillars').insert(pillar_data).execute()
                if result.data:
                    created_pillars.append(result.data[0])
                    print(f"✅ Created pillar: {pillar_data['name']}")
                else:
                    print(f"❌ Failed to create pillar: {pillar_data['name']}")
            
            # Step 2: Create test areas for each pillar
            created_areas = []
            for i, pillar in enumerate(created_pillars):
                area_data = {
                    "id": str(uuid.uuid4()),
                    "user_id": self.auth_user_id,
                    "pillar_id": pillar['id'],
                    "name": f"Area for {pillar['name']}",
                    "description": f"Test area for {pillar['name']}",
                    "icon": "📁",
                    "color": pillar['color'],
                    "created_at": datetime.utcnow().isoformat()
                }
                
                result = self.supabase.table('areas').insert(area_data).execute()
                if result.data:
                    created_areas.append(result.data[0])
                    print(f"✅ Created area: {area_data['name']}")
            
            # Step 3: Create test projects for each area
            created_projects = []
            for area in created_areas:
                project_data = {
                    "id": str(uuid.uuid4()),
                    "user_id": self.auth_user_id,
                    "area_id": area['id'],
                    "name": f"Project in {area['name']}",
                    "description": f"Test project for analytics",
                    "status": "Completed",  # Mark as completed for analytics
                    "icon": "📋",
                    "created_at": datetime.utcnow().isoformat()
                }
                
                result = self.supabase.table('projects').insert(project_data).execute()
                if result.data:
                    created_projects.append(result.data[0])
                    print(f"✅ Created project: {project_data['name']}")
            
            # Step 4: Create completed tasks distributed across projects
            task_distribution = [
                # Health pillar tasks (40% of completed tasks)
                {"project_idx": 0, "count": 8},
                # Career pillar tasks (35% of completed tasks) 
                {"project_idx": 1, "count": 7},
                # Relationships pillar tasks (25% of completed tasks)
                {"project_idx": 2, "count": 5}
            ]
            
            total_completed_tasks = 0
            for dist in task_distribution:
                if dist["project_idx"] < len(created_projects):
                    project = created_projects[dist["project_idx"]]
                    
                    for i in range(dist["count"]):
                        task_data = {
                            "id": str(uuid.uuid4()),
                            "user_id": self.auth_user_id,
                            "project_id": project['id'],
                            "name": f"Completed Task {i+1} - {project['name']}",
                            "description": f"Test completed task for analytics",
                            "completed": True,
                            "priority": "medium",
                            "created_at": datetime.utcnow().isoformat()
                        }
                        
                        result = self.supabase.table('tasks').insert(task_data).execute()
                        if result.data:
                            total_completed_tasks += 1
                            print(f"✅ Created completed task: {task_data['name']}")
            
            print(f"\n📊 ANALYTICS TEST DATA SUMMARY:")
            print(f"   Pillars created: {len(created_pillars)}")
            print(f"   Areas created: {len(created_areas)}")
            print(f"   Projects created: {len(created_projects)}")
            print(f"   Completed tasks: {total_completed_tasks}")
            print(f"   Auth user ID: {self.auth_user_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating analytics test data: {e}")
            return False
            
    async def test_analytics_endpoints(self):
        """Test analytics endpoints with the created data"""
        print(f"\n🧪 TESTING ANALYTICS ENDPOINTS")
        
        try:
            # Test lifetime stats
            from analytics_service import AnalyticsService
            
            print("📊 Testing lifetime stats...")
            stats = await AnalyticsService.get_lifetime_stats(self.auth_user_id)
            print(f"   Tasks completed: {stats['total_tasks_completed']}")
            print(f"   Projects completed: {stats['total_projects_completed']}")
            
            print("🎯 Testing pillar alignment...")
            alignment = await AnalyticsService.get_pillar_alignment_distribution(self.auth_user_id)
            print(f"   Pillar alignment entries: {len(alignment)}")
            
            for pillar in alignment:
                print(f"   - {pillar['pillar_name']}: {pillar['task_count']} tasks ({pillar['percentage']}%)")
            
            print("📈 Testing alignment snapshot...")
            snapshot = await AnalyticsService.get_alignment_snapshot(self.auth_user_id)
            print(f"   Snapshot generated at: {snapshot['generated_at']}")
            print(f"   Lifetime stats: {snapshot['lifetime_stats']}")
            print(f"   Pillar entries: {len(snapshot['pillar_alignment'])}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing analytics endpoints: {e}")
            return False

async def main():
    """Create analytics test data and verify functionality"""
    sync = AnalyticsDataSync()
    
    try:
        await sync.initialize()
        
        print("🚀 ANALYTICS DATA SYNCHRONIZATION")
        print("="*50)
        print("This will create test data for the analytics feature testing")
        print(f"Target user: {sync.auth_user_id}")
        print()
        
        # Create test data
        success = await sync.create_analytics_test_data()
        
        if success:
            print("\n✅ Test data creation completed!")
            
            # Test analytics functionality
            test_success = await sync.test_analytics_endpoints()
            
            if test_success:
                print("\n🎉 ANALYTICS FEATURE READY!")
                print("The MVP v1.2 Insights & Analytics feature is now functional.")
            else:
                print("\n❌ Analytics testing failed")
        else:
            print("\n❌ Test data creation failed")
            
    except Exception as e:
        print(f"❌ Sync failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())