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

class AreaService:
    @staticmethod
    async def create_area(user_id: str, area_data: AreaCreate) -> Area:
        # Get the current max sort_order
        areas = await find_documents("areas", {"user_id": user_id})
        max_sort_order = max([area.get("sort_order", 0) for area in areas] + [0])
        
        area = Area(user_id=user_id, sort_order=max_sort_order + 1, **area_data.dict())
        area_dict = area.dict()
        await create_document("areas", area_dict)
        return area

    @staticmethod
    async def get_user_areas(user_id: str, include_projects: bool = False) -> List[AreaResponse]:
        areas_docs = await find_documents("areas", {"user_id": user_id})
        areas_docs.sort(key=lambda x: x.get("sort_order", 0))
        
        areas = []
        for doc in areas_docs:
            area_response = AreaResponse(**doc)
            
            if include_projects:
                # Get projects for this area
                projects = await ProjectService.get_area_projects(area_response.id)
                area_response.projects = projects
                area_response.project_count = len(projects)
                area_response.completed_project_count = len([p for p in projects if p.status == "Completed"])
                
                # Calculate task counts
                total_tasks = sum([p.task_count or 0 for p in projects])
                completed_tasks = sum([p.completed_task_count or 0 for p in projects])
                area_response.total_task_count = total_tasks
                area_response.completed_task_count = completed_tasks
            else:
                # Just get counts
                projects_docs = await find_documents("projects", {"user_id": user_id, "area_id": area_response.id})
                area_response.project_count = len(projects_docs)
                area_response.completed_project_count = len([p for p in projects_docs if p.get("status") == "Completed"])
            
            areas.append(area_response)
        
        return areas

    @staticmethod
    async def get_area(user_id: str, area_id: str) -> Optional[AreaResponse]:
        area_doc = await find_document("areas", {"id": area_id, "user_id": user_id})
        if not area_doc:
            return None
            
        area_response = AreaResponse(**area_doc)
        
        # Get projects for this area
        projects = await ProjectService.get_area_projects(area_id)
        area_response.projects = projects
        area_response.project_count = len(projects)
        area_response.completed_project_count = len([p for p in projects if p.status == "Completed"])
        
        return area_response

    @staticmethod
    async def update_area(user_id: str, area_id: str, area_data: AreaUpdate) -> bool:
        update_data = {k: v for k, v in area_data.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        return await update_document("areas", {"id": area_id, "user_id": user_id}, update_data)

    @staticmethod
    async def delete_area(user_id: str, area_id: str) -> bool:
        # First delete all projects (which will delete their tasks)
        projects = await find_documents("projects", {"user_id": user_id, "area_id": area_id})
        for project in projects:
            await ProjectService.delete_project(user_id, project["id"])
        
        # Then delete the area
        return await delete_document("areas", {"id": area_id, "user_id": user_id})

class ProjectService:
    @staticmethod
    async def create_project(user_id: str, project_data: ProjectCreate) -> Project:
        # Get the current max sort_order for this area
        projects = await find_documents("projects", {"user_id": user_id, "area_id": project_data.area_id})
        max_sort_order = max([project.get("sort_order", 0) for project in projects] + [0])
        
        project = Project(user_id=user_id, sort_order=max_sort_order + 1, **project_data.dict())
        project_dict = project.dict()
        await create_document("projects", project_dict)
        return project

    @staticmethod
    async def get_area_projects(area_id: str) -> List[ProjectResponse]:
        projects_docs = await find_documents("projects", {"area_id": area_id})
        projects_docs.sort(key=lambda x: x.get("sort_order", 0))
        
        projects = []
        for doc in projects_docs:
            project = await ProjectService._build_project_response(doc)
            projects.append(project)
        
        return projects

    @staticmethod
    async def get_user_projects(user_id: str, area_id: str = None) -> List[ProjectResponse]:
        query = {"user_id": user_id}
        if area_id:
            query["area_id"] = area_id
            
        projects_docs = await find_documents("projects", query)
        projects_docs.sort(key=lambda x: x.get("sort_order", 0))
        
        projects = []
        for doc in projects_docs:
            project = await ProjectService._build_project_response(doc)
            projects.append(project)
        
        return projects

    @staticmethod
    async def get_project(user_id: str, project_id: str, include_tasks: bool = False) -> Optional[ProjectResponse]:
        project_doc = await find_document("projects", {"id": project_id, "user_id": user_id})
        if not project_doc:
            return None
            
        return await ProjectService._build_project_response(project_doc, include_tasks)

    @staticmethod
    async def _build_project_response(project_doc: dict, include_tasks: bool = False) -> ProjectResponse:
        project_response = ProjectResponse(**project_doc)
        
        # Get task counts
        tasks_docs = await find_documents("tasks", {"project_id": project_response.id})
        project_response.task_count = len(tasks_docs)
        project_response.completed_task_count = len([t for t in tasks_docs if t.get("completed", False)])
        
        # Calculate completion percentage
        if project_response.task_count > 0:
            project_response.completion_percentage = (project_response.completed_task_count / project_response.task_count) * 100
        
        # Check if overdue
        if project_response.deadline and project_response.status != "Completed":
            project_response.is_overdue = project_response.deadline < datetime.utcnow()
        
        # Get area name
        area_doc = await find_document("areas", {"id": project_response.area_id})
        if area_doc:
            project_response.area_name = area_doc.get("name")
        
        # Include tasks if requested
        if include_tasks:
            tasks = await TaskService.get_project_tasks(project_response.id)
            project_response.tasks = tasks
        
        return project_response

    @staticmethod
    async def update_project(user_id: str, project_id: str, project_data: ProjectUpdate) -> bool:
        update_data = {k: v for k, v in project_data.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        return await update_document("projects", {"id": project_id, "user_id": user_id}, update_data)

    @staticmethod
    async def delete_project(user_id: str, project_id: str) -> bool:
        # First delete all tasks in this project
        await delete_document("tasks", {"project_id": project_id, "user_id": user_id})
        
        # Then delete the project
        return await delete_document("projects", {"id": project_id, "user_id": user_id})

class TaskService:
    @staticmethod
    async def create_task(user_id: str, task_data: TaskCreate) -> Task:
        # Get the current max sort_order for this project
        tasks = await find_documents("tasks", {"user_id": user_id, "project_id": task_data.project_id, "parent_task_id": task_data.parent_task_id})
        max_sort_order = max([task.get("sort_order", 0) for task in tasks] + [0])
        
        task = Task(user_id=user_id, sort_order=max_sort_order + 1, **task_data.dict())
        
        # Set initial kanban column based on status
        if task.status == TaskStatusEnum.in_progress:
            task.kanban_column = "in_progress"
        elif task.status == TaskStatusEnum.completed:
            task.kanban_column = "done"
            task.completed = True
            task.completed_at = datetime.utcnow()
        else:
            task.kanban_column = "to_do"
        
        task_dict = task.dict()
        await create_document("tasks", task_dict)
        return task

    @staticmethod
    async def get_project_tasks(project_id: str, include_subtasks: bool = True) -> List[TaskResponse]:
        # Get main tasks (no parent)
        tasks_docs = await find_documents("tasks", {"project_id": project_id, "parent_task_id": None})
        tasks_docs.sort(key=lambda x: x.get("sort_order", 0))
        
        tasks = []
        for doc in tasks_docs:
            task = await TaskService._build_task_response(doc, include_subtasks)
            tasks.append(task)
        
        return tasks

    @staticmethod
    async def get_user_tasks(user_id: str, project_id: str = None) -> List[TaskResponse]:
        query = {"user_id": user_id}
        if project_id:
            query["project_id"] = project_id
            
        tasks_docs = await find_documents("tasks", query)
        tasks = []
        
        for doc in tasks_docs:
            task = await TaskService._build_task_response(doc, include_subtasks=False)
            tasks.append(task)
        
        return tasks

    @staticmethod
    async def get_today_tasks(user_id: str) -> List[TaskResponse]:
        today = datetime.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        # Query for tasks due today or overdue
        pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "$or": [
                        {"due_date": {"$gte": today_start, "$lte": today_end}},
                        {"due_date": {"$lt": today_start}, "completed": False}
                    ]
                }
            },
            {"$sort": {"priority": -1, "due_date": 1}}
        ]
        
        tasks_docs = await aggregate_documents("tasks", pipeline)
        tasks = []
        
        for doc in tasks_docs:
            task = await TaskService._build_task_response(doc, include_subtasks=False)
            tasks.append(task)
        
        return tasks

    @staticmethod
    async def _build_task_response(task_doc: dict, include_subtasks: bool = True) -> TaskResponse:
        task_response = TaskResponse(**task_doc)
        
        # Check if overdue
        if task_response.due_date and not task_response.completed:
            task_response.is_overdue = task_response.due_date < datetime.utcnow()
        
        # Check if task can start (dependencies met)
        if task_response.dependency_task_ids:
            dependency_docs = await find_documents("tasks", {"id": {"$in": task_response.dependency_task_ids}})
            task_response.can_start = all([dep.get("completed", False) for dep in dependency_docs])
            task_response.dependency_tasks = [TaskResponse(**dep) for dep in dependency_docs]
        else:
            task_response.can_start = True
        
        # Get subtasks if requested
        if include_subtasks:
            subtasks_docs = await find_documents("tasks", {"parent_task_id": task_response.id})
            subtasks_docs.sort(key=lambda x: x.get("sort_order", 0))
            task_response.sub_tasks = [await TaskService._build_task_response(sub, False) for sub in subtasks_docs]
        
        return task_response

    @staticmethod
    async def update_task(user_id: str, task_id: str, task_data: TaskUpdate) -> bool:
        update_data = {k: v for k, v in task_data.dict().items() if v is not None}
        
        # Handle status changes
        if "status" in update_data:
            if update_data["status"] == TaskStatusEnum.completed:
                update_data["completed"] = True
                update_data["completed_at"] = datetime.utcnow()
                update_data["kanban_column"] = "done"
            elif update_data["status"] == TaskStatusEnum.in_progress:
                update_data["kanban_column"] = "in_progress"
            else:
                update_data["kanban_column"] = "to_do"
                
        # Handle completion toggle
        if "completed" in update_data:
            if update_data["completed"]:
                update_data["completed_at"] = datetime.utcnow()
                update_data["status"] = TaskStatusEnum.completed
                update_data["kanban_column"] = "done"
            else:
                update_data["completed_at"] = None
                update_data["status"] = TaskStatusEnum.not_started
                update_data["kanban_column"] = "to_do"
                
        update_data["updated_at"] = datetime.utcnow()
        return await update_document("tasks", {"id": task_id, "user_id": user_id}, update_data)

    @staticmethod
    async def delete_task(user_id: str, task_id: str) -> bool:
        # First delete all subtasks
        await delete_document("tasks", {"parent_task_id": task_id, "user_id": user_id})
        
        # Then delete the task
        return await delete_document("tasks", {"id": task_id, "user_id": user_id})

    @staticmethod
    async def get_kanban_board(user_id: str, project_id: str) -> KanbanBoard:
        project_doc = await find_document("projects", {"id": project_id, "user_id": user_id})
        if not project_doc:
            raise ValueError("Project not found")
        
        tasks_docs = await find_documents("tasks", {"project_id": project_id, "parent_task_id": None})
        
        columns = {
            "to_do": [],
            "in_progress": [],
            "done": []
        }
        
        for doc in tasks_docs:
            task = await TaskService._build_task_response(doc, include_subtasks=True)
            column = task.kanban_column or "to_do"
            if column in columns:
                columns[column].append(task)
        
        # Sort each column by sort_order
        for column in columns.values():
            column.sort(key=lambda x: x.sort_order)
        
        return KanbanBoard(
            project_id=project_id,
            project_name=project_doc.get("name", ""),
            columns=columns
        )

    @staticmethod
    async def move_task_column(user_id: str, task_id: str, new_column: str) -> bool:
        """Move task between kanban columns"""
        valid_columns = ["to_do", "in_progress", "done"]
        if new_column not in valid_columns:
            return False
        
        update_data = {"kanban_column": new_column, "updated_at": datetime.utcnow()}
        
        # Update status based on column
        if new_column == "done":
            update_data["status"] = TaskStatusEnum.completed
            update_data["completed"] = True
            update_data["completed_at"] = datetime.utcnow()
        elif new_column == "in_progress":
            update_data["status"] = TaskStatusEnum.in_progress
            update_data["completed"] = False
            update_data["completed_at"] = None
        else:  # to_do
            update_data["status"] = TaskStatusEnum.not_started
            update_data["completed"] = False
            update_data["completed_at"] = None
        
        return await update_document("tasks", {"id": task_id, "user_id": user_id}, update_data)


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