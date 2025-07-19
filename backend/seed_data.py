"""
Seed script to populate the database with initial data
"""
import asyncio
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

from database import connect_to_mongo, create_document
from models import User, Course, Badge
from datetime import datetime

async def seed_database():
    """Seed the database with initial data"""
    await connect_to_mongo()
    print("🌱 Starting database seeding...")
    
    # Create default user
    default_user = User(
        id="demo-user-123",
        username="demo_user",
        email="demo@aurumlife.com",
        level=7,
        total_points=1250,
        current_streak=15,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    try:
        await create_document("users", default_user.dict())
        print("✅ Created default user")
    except Exception as e:
        print(f"⚠️  User already exists or error: {e}")
    
    # Create sample courses
    courses = [
        Course(
            id="course-1",
            title="Mindful Leadership",
            description="Develop leadership skills through mindfulness practices",
            instructor="Dr. Sarah Johnson",
            duration="8 weeks",
            category="leadership",
            image_url="https://images.unsplash.com/photo-1573164713714-d95e436ab8d6?w=400&h=250&fit=crop",
            lessons=[
                {"id": "lesson-1", "title": "Introduction & Overview", "duration": "12:30"},
                {"id": "lesson-2", "title": "Core Principles", "duration": "18:45"},
                {"id": "lesson-3", "title": "Practical Applications", "duration": "24:15"},
                {"id": "lesson-4", "title": "Advanced Techniques", "duration": "20:30"},
                {"id": "lesson-5", "title": "Case Studies", "duration": "16:20"},
                {"id": "lesson-6", "title": "Final Assessment", "duration": "8:10"}
            ]
        ),
        Course(
            id="course-2",
            title="Emotional Intelligence Mastery",
            description="Build emotional awareness and regulation skills",
            instructor="Prof. Michael Chen",
            duration="6 weeks",
            category="emotional-intelligence",
            image_url="https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=400&h=250&fit=crop",
            lessons=[
                {"id": "lesson-1", "title": "Understanding Emotions", "duration": "15:20"},
                {"id": "lesson-2", "title": "Self-Awareness", "duration": "22:10"},
                {"id": "lesson-3", "title": "Self-Regulation", "duration": "18:30"},
                {"id": "lesson-4", "title": "Empathy", "duration": "20:45"},
                {"id": "lesson-5", "title": "Social Skills", "duration": "25:15"}
            ]
        ),
        Course(
            id="course-3",
            title="Productivity & Flow States",
            description="Master deep work and achieve peak performance",
            instructor="Alex Rodriguez",
            duration="4 weeks",
            category="productivity",
            image_url="https://images.unsplash.com/photo-1551836022-deb4988cc6c0?w=400&h=250&fit=crop",
            lessons=[
                {"id": "lesson-1", "title": "Understanding Flow", "duration": "14:30"},
                {"id": "lesson-2", "title": "Deep Work Principles", "duration": "19:20"},
                {"id": "lesson-3", "title": "Eliminating Distractions", "duration": "16:45"},
                {"id": "lesson-4", "title": "Building Systems", "duration": "21:10"}
            ]
        )
    ]
    
    for course in courses:
        try:
            await create_document("courses", course.dict())
            print(f"✅ Created course: {course.title}")
        except Exception as e:
            print(f"⚠️  Course {course.title} already exists or error: {e}")
    
    # Create sample badges
    badges = [
        Badge(
            id="badge-1",
            name="Consistency Champion",
            description="Maintained habits for 30 consecutive days",
            icon="🏆",
            rarity="gold",
            category="habits",
            requirements={"habit_streak": 30}
        ),
        Badge(
            id="badge-2",
            name="Mindfulness Master",
            description="Completed 100 meditation sessions",
            icon="🧘",
            rarity="silver",
            category="mindfulness",
            requirements={"meditation_sessions": 100}
        ),
        Badge(
            id="badge-3",
            name="Learning Enthusiast",
            description="Finished 3 courses in personal development",
            icon="📚",
            rarity="bronze",
            category="learning",
            requirements={"courses_completed": 3}
        ),
        Badge(
            id="badge-4",
            name="Reflection Sage",
            description="Wrote 50 journal entries",
            icon="✍️",
            rarity="gold",
            category="reflection",
            requirements={"journal_entries": 50}
        ),
        Badge(
            id="badge-5",
            name="Task Master",
            description="Completed 100 tasks",
            icon="✅",
            rarity="silver",
            category="productivity",
            requirements={"tasks_completed": 100}
        ),
        Badge(
            id="badge-6",
            name="Growth Seeker",
            description="Used the platform for 7 consecutive days",
            icon="🌱",
            rarity="bronze",
            category="general",
            requirements={"login_streak": 7}
        )
    ]
    
    for badge in badges:
        try:
            await create_document("badges", badge.dict())
            print(f"✅ Created badge: {badge.name}")
        except Exception as e:
            print(f"⚠️  Badge {badge.name} already exists or error: {e}")
    
    print("🎉 Database seeding completed!")

if __name__ == "__main__":
    asyncio.run(seed_database())