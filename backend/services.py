from typing import List, Optional
from datetime import datetime, timedelta
from database import (
    create_document, find_document, find_documents, 
    update_document, delete_document, count_documents, aggregate_documents
)
from models import *
import json

class UserService:
    @staticmethod
    async def create_user(user_data: UserCreate) -> User:
        user = User(**user_data.dict())
        user_dict = user.dict()
        await create_document("users", user_dict)
        
        # Initialize user stats
        stats = UserStats(user_id=user.id)
        await create_document("user_stats", stats.dict())
        
        return user

    @staticmethod
    async def get_user(user_id: str) -> Optional[User]:
        user_doc = await find_document("users", {"id": user_id})
        return User(**user_doc) if user_doc else None

    @staticmethod
    async def update_user(user_id: str, user_data: UserUpdate) -> bool:
        update_data = {k: v for k, v in user_data.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        return await update_document("users", {"id": user_id}, update_data)

class HabitService:
    @staticmethod
    async def create_habit(user_id: str, habit_data: HabitCreate) -> Habit:
        habit = Habit(user_id=user_id, **habit_data.dict())
        habit_dict = habit.dict()
        await create_document("habits", habit_dict)
        return habit

    @staticmethod
    async def get_user_habits(user_id: str) -> List[HabitResponse]:
        habits_docs = await find_documents("habits", {"user_id": user_id})
        habits = []
        for doc in habits_docs:
            habit = HabitResponse(**doc)
            # Calculate progress percentage
            habit.progress_percentage = (habit.current_streak / habit.target_days * 100) if habit.target_days > 0 else 0
            habits.append(habit)
        return habits

    @staticmethod
    async def update_habit(habit_id: str, habit_data: HabitUpdate) -> bool:
        update_data = {k: v for k, v in habit_data.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        return await update_document("habits", {"id": habit_id}, update_data)

    @staticmethod
    async def toggle_habit_completion(user_id: str, habit_id: str, completed: bool) -> bool:
        habit_doc = await find_document("habits", {"id": habit_id, "user_id": user_id})
        if not habit_doc:
            return False

        today = datetime.now().date()
        last_completed = habit_doc.get("last_completed_date")
        
        update_data = {
            "is_completed_today": completed,
            "updated_at": datetime.utcnow()
        }
        
        if completed:
            # Check if this is a new completion (not same day)
            if not last_completed or datetime.fromisoformat(last_completed.replace('Z', '+00:00')).date() < today:
                update_data["current_streak"] = habit_doc.get("current_streak", 0) + 1
                update_data["total_completed"] = habit_doc.get("total_completed", 0) + 1
            update_data["last_completed_date"] = datetime.utcnow()
        else:
            # If uncompleting and it was completed today, reduce streak
            if habit_doc.get("is_completed_today", False):
                update_data["current_streak"] = max(0, habit_doc.get("current_streak", 0) - 1)
                update_data["total_completed"] = max(0, habit_doc.get("total_completed", 0) - 1)
        
        return await update_document("habits", {"id": habit_id}, update_data)

    @staticmethod
    async def delete_habit(user_id: str, habit_id: str) -> bool:
        return await delete_document("habits", {"id": habit_id, "user_id": user_id})

class JournalService:
    @staticmethod
    async def create_entry(user_id: str, entry_data: JournalEntryCreate) -> JournalEntry:
        entry = JournalEntry(user_id=user_id, **entry_data.dict())
        entry_dict = entry.dict()
        await create_document("journal_entries", entry_dict)
        return entry

    @staticmethod
    async def get_user_entries(user_id: str, skip: int = 0, limit: int = 20) -> List[JournalEntry]:
        entries_docs = await find_documents(
            "journal_entries", 
            {"user_id": user_id}, 
            skip=skip, 
            limit=limit
        )
        # Sort by created_at descending
        entries_docs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return [JournalEntry(**doc) for doc in entries_docs]

    @staticmethod
    async def update_entry(user_id: str, entry_id: str, entry_data: JournalEntryUpdate) -> bool:
        update_data = {k: v for k, v in entry_data.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        return await update_document("journal_entries", {"id": entry_id, "user_id": user_id}, update_data)

    @staticmethod
    async def delete_entry(user_id: str, entry_id: str) -> bool:
        return await delete_document("journal_entries", {"id": entry_id, "user_id": user_id})

class TaskService:
    @staticmethod
    async def create_task(user_id: str, task_data: TaskCreate) -> Task:
        task = Task(user_id=user_id, **task_data.dict())
        task_dict = task.dict()
        await create_document("tasks", task_dict)
        return task

    @staticmethod
    async def get_user_tasks(user_id: str) -> List[TaskResponse]:
        tasks_docs = await find_documents("tasks", {"user_id": user_id})
        tasks = []
        today = datetime.now()
        
        for doc in tasks_docs:
            task = TaskResponse(**doc)
            # Check if task is overdue
            if task.due_date and not task.completed:
                task.is_overdue = task.due_date < today
            else:
                task.is_overdue = False
            tasks.append(task)
        
        return tasks

    @staticmethod
    async def update_task(user_id: str, task_id: str, task_data: TaskUpdate) -> bool:
        update_data = {k: v for k, v in task_data.dict().items() if v is not None}
        
        # Set completion timestamp if completing task
        if update_data.get("completed") == True:
            update_data["completed_at"] = datetime.utcnow()
        elif update_data.get("completed") == False:
            update_data["completed_at"] = None
            
        update_data["updated_at"] = datetime.utcnow()
        return await update_document("tasks", {"id": task_id, "user_id": user_id}, update_data)

    @staticmethod
    async def delete_task(user_id: str, task_id: str) -> bool:
        return await delete_document("tasks", {"id": task_id, "user_id": user_id})

class ChatService:
    @staticmethod
    async def create_message(user_id: str, message_data: ChatMessageCreate) -> ChatMessage:
        message = ChatMessage(user_id=user_id, **message_data.dict())
        message_dict = message.dict()
        await create_document("chat_messages", message_dict)
        return message

    @staticmethod
    async def get_session_messages(user_id: str, session_id: str) -> List[ChatMessage]:
        messages_docs = await find_documents(
            "chat_messages", 
            {"user_id": user_id, "session_id": session_id}
        )
        # Sort by timestamp ascending
        messages_docs.sort(key=lambda x: x.get("timestamp", ""))
        return [ChatMessage(**doc) for doc in messages_docs]

    @staticmethod
    async def generate_ai_response(user_message: str) -> str:
        """Simple AI response generator - can be enhanced with real LLM integration"""
        responses = [
            "That's a great insight! Building self-awareness is the first step toward meaningful change. Have you considered setting specific daily practices to reinforce this?",
            "I understand your perspective. It's normal to feel overwhelmed sometimes. Let's break this down into smaller, manageable steps.",
            "Your commitment to growth is inspiring! Based on what you've shared, I'd recommend focusing on consistency rather than perfection.",
            "That's a common challenge many people face. What if we explored some mindfulness techniques that could help you navigate these situations?",
            "I can sense you're making real progress. Remember, growth isn't always linear - every step forward counts, even the small ones.",
            "Your reflection shows deep self-awareness. How do you think you could apply this insight to other areas of your life?",
            "That's a wonderful goal! Let's create a specific action plan that aligns with your values and current habits.",
            "I appreciate your honesty. Vulnerability is actually a strength and shows you're ready for genuine growth."
        ]
        import random
        return random.choice(responses)

class CourseService:
    @staticmethod
    async def get_all_courses() -> List[CourseResponse]:
        courses_docs = await find_documents("courses", {})
        return [CourseResponse(**doc) for doc in courses_docs]

    @staticmethod
    async def get_user_courses(user_id: str) -> List[CourseResponse]:
        # Get user's enrolled courses with progress
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$lookup": {
                "from": "courses",
                "localField": "course_id",
                "foreignField": "id",
                "as": "course"
            }},
            {"$unwind": "$course"},
            {"$project": {
                "course_id": 1,
                "progress_percentage": 1,
                "course.title": 1,
                "course.description": 1,
                "course.instructor": 1,
                "course.duration": 1,
                "course.category": 1,
                "course.image_url": 1
            }}
        ]
        
        progress_docs = await aggregate_documents("user_course_progress", pipeline)
        courses = []
        
        for doc in progress_docs:
            course_data = doc["course"]
            course_data["progress_percentage"] = doc["progress_percentage"]
            course_data["is_enrolled"] = True
            courses.append(CourseResponse(**course_data))
        
        return courses

    @staticmethod
    async def enroll_user(user_id: str, course_id: str) -> UserCourseProgress:
        # Check if already enrolled
        existing = await find_document("user_course_progress", {"user_id": user_id, "course_id": course_id})
        if existing:
            return UserCourseProgress(**existing)
        
        enrollment = UserCourseProgress(user_id=user_id, course_id=course_id)
        enrollment_dict = enrollment.dict()
        await create_document("user_course_progress", enrollment_dict)
        return enrollment

class StatsService:
    @staticmethod
    async def get_user_stats(user_id: str) -> UserStats:
        stats_doc = await find_document("user_stats", {"user_id": user_id})
        if not stats_doc:
            # Create default stats
            stats = UserStats(user_id=user_id)
            await create_document("user_stats", stats.dict())
            return stats
        return UserStats(**stats_doc)

    @staticmethod
    async def update_user_stats(user_id: str) -> UserStats:
        """Recalculate and update user statistics"""
        # Get current counts
        total_habits = await count_documents("habits", {"user_id": user_id})
        habits_completed_today = await count_documents("habits", {"user_id": user_id, "is_completed_today": True})
        total_journal_entries = await count_documents("journal_entries", {"user_id": user_id})
        total_tasks = await count_documents("tasks", {"user_id": user_id})
        tasks_completed = await count_documents("tasks", {"user_id": user_id, "completed": True})
        courses_enrolled = await count_documents("user_course_progress", {"user_id": user_id})
        courses_completed = await count_documents("user_course_progress", {"user_id": user_id, "progress_percentage": 100})
        badges_earned = await count_documents("user_badges", {"user_id": user_id, "earned": True})
        
        # Calculate current streak (from habits)
        habits = await find_documents("habits", {"user_id": user_id})
        current_streak = max([h.get("current_streak", 0) for h in habits] + [0])
        
        stats_data = {
            "user_id": user_id,
            "total_habits": total_habits,
            "habits_completed_today": habits_completed_today,
            "total_journal_entries": total_journal_entries,
            "total_tasks": total_tasks,
            "tasks_completed": tasks_completed,
            "courses_enrolled": courses_enrolled,
            "courses_completed": courses_completed,
            "badges_earned": badges_earned,
            "meditation_sessions": 127,  # Placeholder
            "meditation_minutes": 1110,  # Placeholder
            "last_updated": datetime.utcnow()
        }
        
        # Update or create stats
        existing_stats = await find_document("user_stats", {"user_id": user_id})
        if existing_stats:
            await update_document("user_stats", {"user_id": user_id}, stats_data)
        else:
            stats = UserStats(**stats_data)
            await create_document("user_stats", stats.dict())
        
        # Update user's current streak and total points
        total_points = (habits_completed_today * 10) + (tasks_completed * 15) + (badges_earned * 50) + (courses_completed * 100)
        await update_document("users", {"id": user_id}, {
            "current_streak": current_streak,
            "total_points": total_points,
            "updated_at": datetime.utcnow()
        })
        
        return UserStats(**stats_data)

    @staticmethod
    async def get_dashboard_data(user_id: str) -> UserDashboard:
        """Get all dashboard data for a user"""
        # Update stats first
        stats = await StatsService.update_user_stats(user_id)
        
        # Get user data
        user = await UserService.get_user(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Get recent data
        recent_habits = await HabitService.get_user_habits(user_id)
        recent_tasks = await TaskService.get_user_tasks(user_id)
        recent_courses = await CourseService.get_user_courses(user_id)
        
        # Get badges (placeholder for now)
        recent_achievements = []
        
        return UserDashboard(
            user=user,
            stats=stats,
            recent_habits=recent_habits[:5],  # Limit to 5 most recent
            recent_tasks=recent_tasks[:5],
            recent_courses=recent_courses[:3],
            recent_achievements=recent_achievements
        )