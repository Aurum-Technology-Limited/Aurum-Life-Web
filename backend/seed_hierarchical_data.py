"""
Seed script to populate the database with hierarchical goal management data
"""
import asyncio
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from database import connect_to_mongo, create_document
from models import Area, Project, Task, ProjectStatusEnum, TaskStatusEnum, PriorityEnum
from datetime import datetime, timedelta

async def seed_hierarchical_data():
    """Seed the database with Areas, Projects, and Tasks"""
    await connect_to_mongo()
    print("🌱 Starting hierarchical data seeding...")
    
    user_id = "demo-user-123"
    
    # Create Areas
    areas_data = [
        {
            "name": "Health & Fitness",
            "description": "Physical and mental well-being",
            "icon": "💪",
            "color": "#22C55E",
            "sort_order": 1
        },
        {
            "name": "Career & Finance",
            "description": "Professional growth and financial stability",
            "icon": "💼",
            "color": "#3B82F6",
            "sort_order": 2
        },
        {
            "name": "Personal Growth",
            "description": "Learning, skills, and self-development",
            "icon": "🧠",
            "color": "#F4B400",
            "sort_order": 3
        },
        {
            "name": "Relationships",
            "description": "Family, friends, and social connections",
            "icon": "❤️",
            "color": "#EF4444",
            "sort_order": 4
        },
        {
            "name": "Creativity & Hobbies",
            "description": "Creative pursuits and recreational activities",
            "icon": "🎨",
            "color": "#8B5CF6",
            "sort_order": 5
        }
    ]
    
    created_areas = []
    for area_data in areas_data:
        area = Area(
            id=f"area-{area_data['sort_order']}",
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            **area_data
        )
        try:
            await create_document("areas", area.dict())
            created_areas.append(area)
            print(f"✅ Created area: {area.name}")
        except Exception as e:
            print(f"⚠️  Area {area.name} already exists or error: {e}")
    
    # Create Projects
    projects_data = [
        # Health & Fitness Projects
        {
            "area_id": "area-1",
            "name": "Marathon Training",
            "description": "Train for and complete a full marathon",
            "deadline": datetime.utcnow() + timedelta(days=120),
            "status": ProjectStatusEnum.in_progress,
            "priority": PriorityEnum.high,
            "sort_order": 1
        },
        {
            "area_id": "area-1", 
            "name": "Nutrition Optimization",
            "description": "Develop and maintain healthy eating habits",
            "deadline": datetime.utcnow() + timedelta(days=90),
            "status": ProjectStatusEnum.not_started,
            "priority": PriorityEnum.medium,
            "sort_order": 2
        },
        
        # Career & Finance Projects
        {
            "area_id": "area-2",
            "name": "Skills Certification",
            "description": "Obtain industry certification to advance career",
            "deadline": datetime.utcnow() + timedelta(days=180),
            "status": ProjectStatusEnum.in_progress,
            "priority": PriorityEnum.high,
            "sort_order": 1
        },
        {
            "area_id": "area-2",
            "name": "Emergency Fund",
            "description": "Build 6-month emergency fund",
            "deadline": datetime.utcnow() + timedelta(days=365),
            "status": ProjectStatusEnum.not_started,
            "priority": PriorityEnum.medium,
            "sort_order": 2
        },
        
        # Personal Growth Projects
        {
            "area_id": "area-3",
            "name": "Mindfulness Practice",
            "description": "Establish daily meditation and mindfulness routine",
            "deadline": datetime.utcnow() + timedelta(days=60),
            "status": ProjectStatusEnum.in_progress,
            "priority": PriorityEnum.high,
            "sort_order": 1
        },
        {
            "area_id": "area-3",
            "name": "Language Learning",
            "description": "Achieve conversational fluency in Spanish",
            "deadline": datetime.utcnow() + timedelta(days=300),
            "status": ProjectStatusEnum.not_started,
            "priority": PriorityEnum.low,
            "sort_order": 2
        }
    ]
    
    created_projects = []
    for i, project_data in enumerate(projects_data):
        project = Project(
            id=f"project-{i+1}",
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            **project_data
        )
        try:
            await create_document("projects", project.dict())
            created_projects.append(project)
            print(f"✅ Created project: {project.name}")
        except Exception as e:
            print(f"⚠️  Project {project.name} already exists or error: {e}")
    
    # Create Tasks
    tasks_data = [
        # Marathon Training Tasks
        {
            "project_id": "project-1",
            "name": "Create training schedule",
            "description": "Design 16-week marathon training plan",
            "status": TaskStatusEnum.completed,
            "priority": PriorityEnum.high,
            "due_date": datetime.utcnow() - timedelta(days=7),
            "completed": True,
            "completed_at": datetime.utcnow() - timedelta(days=7),
            "kanban_column": "done",
            "sort_order": 1
        },
        {
            "project_id": "project-1",
            "name": "Buy running shoes",
            "description": "Get proper running shoes for training",
            "status": TaskStatusEnum.in_progress,
            "priority": PriorityEnum.medium,
            "due_date": datetime.utcnow() + timedelta(days=3),
            "kanban_column": "in_progress",
            "sort_order": 2
        },
        {
            "project_id": "project-1",
            "name": "Complete week 1 training",
            "description": "3 runs totaling 15 miles",
            "status": TaskStatusEnum.not_started,
            "priority": PriorityEnum.high,
            "due_date": datetime.utcnow() + timedelta(days=7),
            "kanban_column": "to_do",
            "sort_order": 3
        },
        
        # Skills Certification Tasks
        {
            "project_id": "project-3",
            "name": "Research certification requirements",
            "description": "Study exam format and requirements",
            "status": TaskStatusEnum.completed,
            "priority": PriorityEnum.high,
            "due_date": datetime.utcnow() - timedelta(days=14),
            "completed": True,
            "completed_at": datetime.utcnow() - timedelta(days=14),
            "kanban_column": "done",
            "sort_order": 1
        },
        {
            "project_id": "project-3",
            "name": "Purchase study materials",
            "description": "Buy books and online course",
            "status": TaskStatusEnum.in_progress,
            "priority": PriorityEnum.medium,
            "due_date": datetime.utcnow() + timedelta(days=2),
            "kanban_column": "in_progress",
            "sort_order": 2
        },
        {
            "project_id": "project-3",
            "name": "Study Chapter 1-3",
            "description": "Complete first three chapters",
            "status": TaskStatusEnum.not_started,
            "priority": PriorityEnum.high,
            "due_date": datetime.utcnow() + timedelta(days=10),
            "kanban_column": "to_do",
            "sort_order": 3
        },
        
        # Mindfulness Practice Tasks
        {
            "project_id": "project-5",
            "name": "Set up meditation space",
            "description": "Create quiet, comfortable meditation area",
            "status": TaskStatusEnum.completed,
            "priority": PriorityEnum.medium,
            "due_date": datetime.utcnow() - timedelta(days=3),
            "completed": True,
            "completed_at": datetime.utcnow() - timedelta(days=3),
            "kanban_column": "done",
            "sort_order": 1
        },
        {
            "project_id": "project-5",
            "name": "Download meditation app",
            "description": "Install and set up guided meditation app",
            "status": TaskStatusEnum.in_progress,
            "priority": PriorityEnum.low,
            "due_date": datetime.utcnow() + timedelta(days=1),
            "kanban_column": "in_progress",
            "sort_order": 2
        },
        {
            "project_id": "project-5",
            "name": "Meditate for 7 days",
            "description": "Complete 10-minute daily meditation",
            "status": TaskStatusEnum.not_started,
            "priority": PriorityEnum.high,
            "due_date": datetime.utcnow() + timedelta(days=7),
            "kanban_column": "to_do",
            "sort_order": 3
        },
        
        # Today's tasks (some due today)
        {
            "project_id": "project-1",
            "name": "Morning run - 5 miles",
            "description": "Easy pace training run",
            "status": TaskStatusEnum.not_started,
            "priority": PriorityEnum.high,
            "due_date": datetime.utcnow().replace(hour=23, minute=59),
            "kanban_column": "to_do",
            "sort_order": 4,
            "estimated_duration": 45
        },
        {
            "project_id": "project-3",
            "name": "Review study notes",
            "description": "30-minute review session",
            "status": TaskStatusEnum.not_started,
            "priority": PriorityEnum.medium,
            "due_date": datetime.utcnow().replace(hour=20, minute=0),
            "kanban_column": "to_do",
            "sort_order": 4,
            "estimated_duration": 30
        }
    ]
    
    for i, task_data in enumerate(tasks_data):
        task = Task(
            id=f"task-{i+1}",
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            **task_data
        )
        try:
            await create_document("tasks", task.dict())
            print(f"✅ Created task: {task.name}")
        except Exception as e:
            print(f"⚠️  Task {task.name} already exists or error: {e}")
    
    print("🎉 Hierarchical data seeding completed!")

if __name__ == "__main__":
    asyncio.run(seed_hierarchical_data())