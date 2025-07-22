import secrets
import hashlib
import os
from typing import List, Optional
from datetime import datetime, timedelta
from database import (
    create_document, find_document, find_documents,
    update_document, delete_document, count_documents, aggregate_documents
)
from models import *
from auth import get_password_hash, verify_password
import json

class UserService:
    @staticmethod
    async def create_user(user_data: UserCreate) -> User:
        # Check if user already exists
        existing_user = await UserService.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Hash the password
        password_hash = get_password_hash(user_data.password)
        
        # Create user without the plain password
        user_dict = user_data.dict()
        user_dict.pop('password')  # Remove plain password
        user_dict['password_hash'] = password_hash
        
        user = User(**user_dict)
        user_dict = user.dict()
        await create_document("users", user_dict)
        
        # Initialize user stats
        stats = UserStats(user_id=user.id)
        await create_document("user_stats", stats.dict())
        
        return user

    @staticmethod
    async def authenticate_user(email: str, password: str) -> Optional[User]:
        user = await UserService.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        user_doc = await find_document("users", {"email": email})
        return User(**user_doc) if user_doc else None

    @staticmethod
    async def get_user(user_id: str) -> Optional[User]:
        user_doc = await find_document("users", {"id": user_id})
        return User(**user_doc) if user_doc else None

    @staticmethod
    async def update_user(user_id: str, user_data: UserUpdate) -> bool:
        update_data = {k: v for k, v in user_data.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        return await update_document("users", {"id": user_id}, update_data)

    @staticmethod
    async def update_user_profile(user_id: str, first_name: str = None, last_name: str = None) -> bool:
        update_data = {"updated_at": datetime.utcnow()}
        if first_name is not None:
            update_data["first_name"] = first_name
        if last_name is not None:
            update_data["last_name"] = last_name
        return await update_document("users", {"id": user_id}, update_data)

    @staticmethod
    async def create_password_reset_token(email: str) -> Optional[str]:
        """
        Create a password reset token for the user
        Returns the token if user exists, None otherwise
        """
        # Check if user exists
        user = await UserService.get_user_by_email(email)
        if not user:
            return None
        
        # Generate secure reset token
        reset_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(reset_token.encode()).hexdigest()
        
        # Calculate expiration time
        expiry_hours = int(os.getenv('RESET_TOKEN_EXPIRY_HOURS', 24))
        expires_at = datetime.utcnow() + timedelta(hours=expiry_hours)
        
        # Invalidate any existing reset tokens for this user
        existing_tokens = await find_documents("password_reset_tokens", 
                                              {"user_id": user.id, "is_used": False})
        for token_doc in existing_tokens:
            await update_document("password_reset_tokens", 
                                {"id": token_doc["id"]}, 
                                {"is_used": True})
        
        # Create new reset token
        reset_token_obj = PasswordResetToken(
            user_id=user.id,
            token=token_hash,
            expires_at=expires_at
        )
        
        await create_document("password_reset_tokens", reset_token_obj.dict())
        
        return reset_token  # Return the plain token, not the hash

    @staticmethod
    async def verify_reset_token(token: str) -> Optional[User]:
        """
        Verify password reset token and return associated user
        Returns User if token is valid, None otherwise
        """
        # Hash the provided token to match stored hash
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Find the token
        token_data = await find_document("password_reset_tokens", {
            "token": token_hash,
            "is_used": False
        })
        
        if not token_data:
            return None
        
        # Check if token has expired
        token_obj = PasswordResetToken(**token_data)
        if datetime.utcnow() > token_obj.expires_at:
            # Mark token as used (expired)
            await update_document("password_reset_tokens", 
                                {"token": token_hash}, 
                                {"is_used": True})
            return None
        
        # Get the user associated with this token
        return await UserService.get_user(token_obj.user_id)

    @staticmethod
    async def reset_password(token: str, new_password: str) -> bool:
        """
        Reset user password using the reset token
        Returns True if successful, False otherwise
        """
        # Verify token and get user
        user = await UserService.verify_reset_token(token)
        if not user:
            return False
        
        # Hash the provided token to mark as used
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Update user's password
        new_password_hash = get_password_hash(new_password)
        await update_document("users", {"id": user.id}, {"password_hash": new_password_hash})
        
        # Mark token as used
        await update_document("password_reset_tokens", 
                            {"token": token_hash}, 
                            {"is_used": True})
        
        return True

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

class ProjectTemplateService:
    @staticmethod
    async def create_template(user_id: str, template_data: ProjectTemplateCreate) -> ProjectTemplate:
        template = ProjectTemplate(user_id=user_id, **template_data.dict(exclude={'tasks'}))
        template_dict = template.dict()
        await create_document("project_templates", template_dict)
        
        # Create task templates
        for i, task_data in enumerate(template_data.tasks):
            task_template = TaskTemplate(
                template_id=template.id,
                user_id=user_id,
                sort_order=i + 1,
                **task_data.dict()
            )
            await create_document("task_templates", task_template.dict())
        
        return template

    @staticmethod
    async def get_user_templates(user_id: str) -> List[ProjectTemplateResponse]:
        templates_docs = await find_documents("project_templates", {"user_id": user_id})
        templates = []
        
        for doc in templates_docs:
            template_response = ProjectTemplateResponse(**doc)
            
            # Get task templates for this template
            task_templates_docs = await find_documents("task_templates", {"template_id": template_response.id})
            task_templates_docs.sort(key=lambda x: x.get("sort_order", 0))
            template_response.tasks = [TaskTemplate(**task_doc) for task_doc in task_templates_docs]
            template_response.task_count = len(task_templates_docs)
            
            templates.append(template_response)
        
        return templates

    @staticmethod
    async def get_template(user_id: str, template_id: str) -> Optional[ProjectTemplateResponse]:
        template_doc = await find_document("project_templates", {"id": template_id, "user_id": user_id})
        if not template_doc:
            return None
            
        template_response = ProjectTemplateResponse(**template_doc)
        
        # Get task templates
        task_templates_docs = await find_documents("task_templates", {"template_id": template_id})
        task_templates_docs.sort(key=lambda x: x.get("sort_order", 0))
        template_response.tasks = [TaskTemplate(**task_doc) for task_doc in task_templates_docs]
        template_response.task_count = len(task_templates_docs)
        
        return template_response

    @staticmethod
    async def update_template(user_id: str, template_id: str, template_data: ProjectTemplateUpdate) -> bool:
        update_data = {k: v for k, v in template_data.dict(exclude={'tasks'}).items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        # Update the template
        success = await update_document("project_templates", {"id": template_id, "user_id": user_id}, update_data)
        
        # Update task templates if provided
        if template_data.tasks is not None:
            # Delete existing task templates
            await delete_document("task_templates", {"template_id": template_id})
            
            # Create new task templates
            for i, task_data in enumerate(template_data.tasks):
                task_template = TaskTemplate(
                    template_id=template_id,
                    user_id=user_id,
                    sort_order=i + 1,
                    **task_data.dict()
                )
                await create_document("task_templates", task_template.dict())
        
        return success

    @staticmethod
    async def delete_template(user_id: str, template_id: str) -> bool:
        # First delete all task templates
        await delete_document("task_templates", {"template_id": template_id})
        
        # Then delete the project template
        return await delete_document("project_templates", {"id": template_id, "user_id": user_id})

    @staticmethod
    async def use_template(user_id: str, template_id: str, project_data: ProjectCreate) -> Project:
        """Create a new project from a template"""
        # Get the template
        template = await ProjectTemplateService.get_template(user_id, template_id)
        if not template:
            raise ValueError("Template not found")
        
        # Create the project
        project = await ProjectService.create_project(user_id, project_data)
        
        # Create tasks from template
        for task_template in template.tasks:
            task_data = TaskCreate(
                name=task_template.name,
                description=task_template.description,
                priority=task_template.priority,
                estimated_duration=task_template.estimated_duration,
                project_id=project.id
            )
            await TaskService.create_task(user_id, task_data)
        
        # Increment usage count
        await update_document(
            "project_templates", 
            {"id": template_id, "user_id": user_id}, 
            {"usage_count": template.usage_count + 1, "updated_at": datetime.utcnow()}
        )
        
        return project


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
    async def get_user_areas(user_id: str, include_projects: bool = False, include_archived: bool = False) -> List[AreaResponse]:
        query = {"user_id": user_id}
        if not include_archived:
            query["archived"] = {"$ne": True}
            
        areas_docs = await find_documents("areas", query)
        areas_docs.sort(key=lambda x: x.get("sort_order", 0))
        
        areas = []
        for doc in areas_docs:
            area_response = AreaResponse(**doc)
            
            if include_projects:
                # Get projects for this area
                projects = await ProjectService.get_area_projects(area_response.id, include_archived=include_archived)
                area_response.projects = projects
                area_response.project_count = len(projects)
                area_response.completed_project_count = len([p for p in projects if p.status == "Completed"])
                
                # Calculate task counts
                total_tasks = sum([p.task_count or 0 for p in projects])
                completed_tasks = sum([p.completed_task_count or 0 for p in projects])
                area_response.total_task_count = total_tasks
                area_response.completed_task_count = completed_tasks
            else:
                # Just get counts (exclude archived projects unless specifically requested)
                project_query = {"user_id": user_id, "area_id": area_response.id}
                if not include_archived:
                    project_query["archived"] = {"$ne": True}
                    
                projects_docs = await find_documents("projects", project_query)
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
    async def archive_area(user_id: str, area_id: str) -> bool:
        """Archive an area and optionally its projects"""
        return await update_document(
            "areas", 
            {"id": area_id, "user_id": user_id}, 
            {"archived": True, "updated_at": datetime.utcnow()}
        )
    
    @staticmethod
    async def unarchive_area(user_id: str, area_id: str) -> bool:
        """Unarchive an area"""
        return await update_document(
            "areas", 
            {"id": area_id, "user_id": user_id}, 
            {"archived": False, "updated_at": datetime.utcnow()}
        )

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
    async def get_area_projects(area_id: str, include_archived: bool = False) -> List[ProjectResponse]:
        query = {"area_id": area_id}
        if not include_archived:
            query["archived"] = {"$ne": True}
            
        projects_docs = await find_documents("projects", query)
        projects_docs.sort(key=lambda x: x.get("sort_order", 0))
        
        projects = []
        for doc in projects_docs:
            project = await ProjectService._build_project_response(doc)
            projects.append(project)
        
        return projects

    @staticmethod
    async def get_user_projects(user_id: str, area_id: str = None, include_archived: bool = False) -> List[ProjectResponse]:
        query = {"user_id": user_id}
        if area_id:
            query["area_id"] = area_id
        if not include_archived:
            query["archived"] = {"$ne": True}
            
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
        
        # Get task counts - FIXED: Filter by user_id to ensure data consistency
        tasks_docs = await find_documents("tasks", {
            "project_id": project_response.id,
            "user_id": project_doc["user_id"]  # Add user_id filter
        })
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
    async def archive_project(user_id: str, project_id: str) -> bool:
        """Archive a project"""
        return await update_document(
            "projects", 
            {"id": project_id, "user_id": user_id}, 
            {"archived": True, "updated_at": datetime.utcnow()}
        )
    
    @staticmethod
    async def unarchive_project(user_id: str, project_id: str) -> bool:
        """Unarchive a project"""
        return await update_document(
            "projects", 
            {"id": project_id, "user_id": user_id}, 
            {"archived": False, "updated_at": datetime.utcnow()}
        )

    @staticmethod
    async def delete_project(user_id: str, project_id: str) -> bool:
        # First delete all tasks in this project
        await delete_document("tasks", {"project_id": project_id, "user_id": user_id})
        
        # Then delete the project
        return await delete_document("projects", {"id": project_id, "user_id": user_id})

class RecurringTaskService:
    @staticmethod
    async def create_recurring_task(user_id: str, task_data: RecurringTaskCreate) -> RecurringTaskTemplate:
        """Create a new recurring task template"""
        # Validate project exists
        project = await find_document("projects", {"id": task_data.project_id, "user_id": user_id})
        if not project:
            raise ValueError("Project not found")
        
        # Calculate next due date based on pattern
        next_due = RecurringTaskService._calculate_next_due_date(
            task_data.recurrence_pattern, 
            datetime.now()
        )
        
        template = RecurringTaskTemplate(
            user_id=user_id,
            next_due=next_due,
            **task_data.dict()
        )
        
        await create_document("recurring_task_templates", template.dict())
        return template

    @staticmethod
    async def get_user_recurring_tasks(user_id: str) -> List[RecurringTaskResponse]:
        """Get all recurring task templates for a user"""
        templates_docs = await find_documents("recurring_task_templates", {"user_id": user_id})
        
        responses = []
        for doc in templates_docs:
            template_response = RecurringTaskResponse(**doc)
            
            # Get project name
            if template_response.project_id:
                project = await find_document("projects", {"id": template_response.project_id})
                if project:
                    template_response.project_name = project["name"]
            
            # Calculate statistics
            instances = await find_documents("recurring_task_instances", {
                "template_id": template_response.id
            })
            
            template_response.total_instances = len(instances)
            template_response.completed_instances = len([i for i in instances if i.get("completed")])
            
            if template_response.total_instances > 0:
                template_response.completion_rate = (
                    template_response.completed_instances / template_response.total_instances * 100
                )
            
            responses.append(template_response)
        
        return responses

    @staticmethod
    async def update_recurring_task(user_id: str, template_id: str, task_data: RecurringTaskUpdate) -> bool:
        """Update a recurring task template"""
        update_data = {k: v for k, v in task_data.dict().items() if v is not None}
        
        # If recurrence pattern changed, recalculate next due date
        if "recurrence_pattern" in update_data:
            next_due = RecurringTaskService._calculate_next_due_date(
                update_data["recurrence_pattern"], 
                datetime.now()
            )
            update_data["next_due"] = next_due
        
        update_data["updated_at"] = datetime.utcnow()
        
        return await update_document("recurring_task_templates", {
            "id": template_id, 
            "user_id": user_id
        }, update_data)

    @staticmethod
    async def delete_recurring_task(user_id: str, template_id: str) -> bool:
        """Delete a recurring task template and all its instances"""
        # Delete all instances first
        await delete_document("recurring_task_instances", {"template_id": template_id})
        
        # Delete the template
        return await delete_document("recurring_task_templates", {
            "id": template_id, 
            "user_id": user_id
        })

    @staticmethod
    async def generate_recurring_task_instances():
        """Scheduled job to generate recurring task instances"""
        try:
            now = datetime.now()
            
            # Find templates that need new instances
            templates_docs = await find_documents("recurring_task_templates", {
                "is_active": True,
                "$or": [
                    {"next_due": {"$lte": now}},
                    {"next_due": None}
                ]
            })
            
            for template_doc in templates_docs:
                template = RecurringTaskTemplate(**template_doc)
                
                # Check if we should create instances for this template
                if await RecurringTaskService._should_generate_instances(template, now):
                    instances = await RecurringTaskService._generate_instances_for_template(
                        template, now
                    )
                    
                    # Create the instances
                    for instance in instances:
                        await create_document("recurring_task_instances", instance.dict())
                    
                    # Update template's last_generated and next_due
                    next_due = RecurringTaskService._calculate_next_due_date(
                        template.recurrence_pattern, 
                        now
                    )
                    
                    await update_document("recurring_task_templates", {
                        "id": template.id
                    }, {
                        "last_generated": now,
                        "next_due": next_due
                    })
                    
                    print(f"Generated {len(instances)} instances for template {template.name}")
            
        except Exception as e:
            print(f"Error generating recurring task instances: {e}")

    @staticmethod
    async def _should_generate_instances(template: RecurringTaskTemplate, now: datetime) -> bool:
        """Check if we should generate new instances for a template"""
        if not template.is_active:
            return False
        
        # Check if we've reached max instances
        if template.recurrence_pattern.max_instances:
            existing_count = len(await find_documents("recurring_task_instances", {
                "template_id": template.id
            }))
            if existing_count >= template.recurrence_pattern.max_instances:
                return False
        
        # Check if we've passed end date
        if template.recurrence_pattern.end_date and now > template.recurrence_pattern.end_date:
            return False
        
        return True

    @staticmethod
    async def _generate_instances_for_template(template: RecurringTaskTemplate, now: datetime) -> List[RecurringTaskInstance]:
        """Generate task instances for a template"""
        instances = []
        pattern = template.recurrence_pattern
        
        # Generate instances for the next period (next 30 days max)
        end_date = min(
            now + timedelta(days=30),
            pattern.end_date or now + timedelta(days=365)
        )
        
        current_date = template.next_due or now
        
        while current_date <= end_date:
            # Don't create instances too far in the past
            if current_date >= now - timedelta(days=1):
                instance = RecurringTaskInstance(
                    user_id=template.user_id,
                    template_id=template.id,
                    name=template.name,
                    description=template.description,
                    priority=template.priority,
                    project_id=template.project_id,
                    category=template.category,
                    estimated_duration=template.estimated_duration,
                    due_date=current_date
                )
                instances.append(instance)
            
            # Calculate next occurrence
            current_date = RecurringTaskService._calculate_next_occurrence(
                current_date, pattern
            )
            
            # Prevent infinite loops
            if len(instances) >= 100:
                break
        
        return instances

    @staticmethod
    def _calculate_next_due_date(pattern: RecurrencePattern, from_date: datetime) -> datetime:
        """Calculate the next due date based on recurrence pattern"""
        if pattern.type == RecurrenceEnum.none:
            return from_date
        
        return RecurringTaskService._calculate_next_occurrence(from_date, pattern)

    @staticmethod
    def _calculate_next_occurrence(from_date: datetime, pattern: RecurrencePattern) -> datetime:
        """Calculate next occurrence based on recurrence pattern"""
        if pattern.type == RecurrenceEnum.daily:
            return from_date + timedelta(days=pattern.interval)
        
        elif pattern.type == RecurrenceEnum.weekly:
            if pattern.weekdays:
                # Find next occurrence on specified weekdays
                current_weekday = from_date.weekday()  # 0 = Monday
                target_weekdays = [
                    ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"].index(day.value)
                    for day in pattern.weekdays
                ]
                target_weekdays.sort()
                
                # Find next target weekday
                next_weekday = None
                for weekday in target_weekdays:
                    if weekday > current_weekday:
                        next_weekday = weekday
                        break
                
                if next_weekday is None:
                    # Go to first weekday of next week
                    next_weekday = target_weekdays[0]
                    days_ahead = 7 - current_weekday + next_weekday
                else:
                    days_ahead = next_weekday - current_weekday
                
                return from_date + timedelta(days=days_ahead)
            else:
                return from_date + timedelta(weeks=pattern.interval)
        
        elif pattern.type == RecurrenceEnum.monthly:
            # Add months (approximate - may need adjustment for day overflow)
            next_month = from_date.month + pattern.interval
            next_year = from_date.year + (next_month - 1) // 12
            next_month = ((next_month - 1) % 12) + 1
            
            # Handle day overflow (e.g., Jan 31 -> Feb 28)
            day = pattern.month_day or from_date.day
            try:
                return from_date.replace(year=next_year, month=next_month, day=day)
            except ValueError:
                # Day doesn't exist in target month, use last day of month
                import calendar
                last_day = calendar.monthrange(next_year, next_month)[1]
                return from_date.replace(year=next_year, month=next_month, day=last_day)
        
        # Default fallback
        return from_date + timedelta(days=1)

    @staticmethod
    async def get_recurring_task_instances(user_id: str, template_id: Optional[str] = None, 
                                          start_date: Optional[datetime] = None,
                                          end_date: Optional[datetime] = None) -> List[RecurringTaskInstance]:
        """Get recurring task instances with optional filtering"""
        query = {"user_id": user_id}
        
        if template_id:
            query["template_id"] = template_id
        
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            query["due_date"] = date_query
        
        instances_docs = await find_documents("recurring_task_instances", query)
        instances_docs.sort(key=lambda x: x.get("due_date", datetime.min))
        
        return [RecurringTaskInstance(**doc) for doc in instances_docs]

    @staticmethod
    async def complete_recurring_task_instance(user_id: str, instance_id: str) -> bool:
        """Mark a recurring task instance as complete"""
        return await update_document("recurring_task_instances", {
            "id": instance_id,
            "user_id": user_id
        }, {
            "completed": True,
            "completed_at": datetime.utcnow(),
            "status": TaskStatusEnum.completed,
            "kanban_column": "done"
        })

    @staticmethod
    async def skip_recurring_task_instance(user_id: str, instance_id: str) -> bool:
        """Skip a recurring task instance"""
        return await update_document("recurring_task_instances", {
            "id": instance_id,
            "user_id": user_id
        }, {
            "skipped": True,
            "status": TaskStatusEnum.completed  # Consider it done but skipped
        })


class TaskService:
    @staticmethod
    async def create_task(user_id: str, task_data: TaskCreate) -> Task:
        # Validate that the project exists and belongs to the user
        project = await find_document("projects", {"id": task_data.project_id, "user_id": user_id})
        if not project:
            raise ValueError(f"Project with ID {task_data.project_id} not found or does not belong to user")
        
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
        """Get curated tasks for today's view"""
        today = datetime.now().date()
        
        # Get tasks specifically added to today's view
        daily_tasks_docs = await find_documents("daily_tasks", {
            "user_id": user_id,
            "date": {
                "$gte": datetime.combine(today, datetime.min.time()),
                "$lte": datetime.combine(today, datetime.max.time())
            }
        })
        
        if daily_tasks_docs:
            # Sort by user-defined order
            daily_tasks_docs.sort(key=lambda x: x.get("sort_order", 0))
            task_ids = [dt["task_id"] for dt in daily_tasks_docs]
            
            # Get the actual task data
            tasks_docs = await find_documents("tasks", {
                "id": {"$in": task_ids},
                "user_id": user_id
            })
            
            # Build task responses
            tasks = []
            for task_doc in tasks_docs:
                task = await TaskService._build_task_response(task_doc, include_subtasks=True)
                tasks.append(task)
            
            # Sort tasks by daily_tasks sort_order
            task_order_map = {dt["task_id"]: dt["sort_order"] for dt in daily_tasks_docs}
            tasks.sort(key=lambda t: task_order_map.get(t.id, 999))
            
            return tasks
        else:
            # Fallback to original behavior: tasks due today or overdue
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
            
            # Get tasks from aggregation pipeline
            tasks_docs = await aggregate_documents("tasks", pipeline)
            
            tasks = []
            for doc in tasks_docs:
                task = await TaskService._build_task_response(doc, include_subtasks=False)
                tasks.append(task)
            
            return tasks

    @staticmethod
    async def get_available_tasks_for_today(user_id: str) -> List[TaskResponse]:
        """Get tasks available to add to today's view (not yet added)"""
        today = datetime.now().date()
        
        # Get task IDs already in today's view
        daily_tasks_docs = await find_documents("daily_tasks", {
            "user_id": user_id,
            "date": {
                "$gte": datetime.combine(today, datetime.min.time()),
                "$lte": datetime.combine(today, datetime.max.time())
            }
        })
        
        existing_task_ids = [dt["task_id"] for dt in daily_tasks_docs]
        
        # Get all incomplete tasks not in today's view
        query = {
            "user_id": user_id,
            "completed": False,
            "parent_task_id": None  # Only main tasks, not sub-tasks
        }
        
        if existing_task_ids:
            query["id"] = {"$nin": existing_task_ids}
        
        tasks_docs = await find_documents("tasks", query)
        
        # Sort by priority and due date
        tasks_docs.sort(key=lambda x: (
            0 if x.get("priority") == "high" else 1 if x.get("priority") == "medium" else 2,
            x.get("due_date") or datetime.max
        ))
        
        # Limit to top 20 to avoid overwhelming the UI
        tasks_docs = tasks_docs[:20]
        
        tasks = []
        for doc in tasks_docs:
            task = await TaskService._build_task_response(doc, include_subtasks=False)
            tasks.append(task)
        
        return tasks

    @staticmethod
    async def add_task_to_today(user_id: str, task_id: str) -> bool:
        """Add a task to today's curated list"""
        today = datetime.now().date()
        
        # Verify task exists and belongs to user
        task = await find_document("tasks", {"id": task_id, "user_id": user_id})
        if not task:
            raise ValueError("Task not found")
        
        # Check if task is already in today's view
        existing = await find_document("daily_tasks", {
            "user_id": user_id,
            "task_id": task_id,
            "date": {
                "$gte": datetime.combine(today, datetime.min.time()),
                "$lte": datetime.combine(today, datetime.max.time())
            }
        })
        
        if existing:
            return True  # Already added
        
        # Get current max sort_order for today
        daily_tasks = await find_documents("daily_tasks", {
            "user_id": user_id,
            "date": {
                "$gte": datetime.combine(today, datetime.min.time()),
                "$lte": datetime.combine(today, datetime.max.time())
            }
        })
        
        max_sort_order = max([dt.get("sort_order", 0) for dt in daily_tasks] + [0])
        
        # Create daily task entry
        daily_task = DailyTask(
            user_id=user_id,
            task_id=task_id,
            date=datetime.combine(today, datetime.min.time()),
            sort_order=max_sort_order + 1
        )
        
        await create_document("daily_tasks", daily_task.dict())
        return True

    @staticmethod
    async def remove_task_from_today(user_id: str, task_id: str) -> bool:
        """Remove a task from today's curated list"""
        today = datetime.now().date()
        
        return await delete_document("daily_tasks", {
            "user_id": user_id,
            "task_id": task_id,
            "date": {
                "$gte": datetime.combine(today, datetime.min.time()),
                "$lte": datetime.combine(today, datetime.max.time())
            }
        })

    @staticmethod
    async def reorder_daily_tasks(user_id: str, task_ids: List[str]) -> bool:
        """Reorder tasks in today's view"""
        today = datetime.now().date()
        
        for i, task_id in enumerate(task_ids):
            await update_document("daily_tasks", {
                "user_id": user_id,
                "task_id": task_id,
                "date": {
                    "$gte": datetime.combine(today, datetime.min.time()),
                    "$lte": datetime.combine(today, datetime.max.time())
                }
            }, {"sort_order": i + 1})
        
        return True

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
        
        # Update the task
        success = await update_document("tasks", {"id": task_id, "user_id": user_id}, update_data)
        
        if success:
            # Get the updated task to check for parent task completion logic
            updated_task = await find_document("tasks", {"id": task_id, "user_id": user_id})
            if updated_task:
                # If this is a sub-task, check if parent task completion should be updated
                if updated_task.get("parent_task_id"):
                    await TaskService._update_parent_task_completion(updated_task["parent_task_id"], user_id)
                    
                # If this task has sub_task_completion_required and we're marking it complete,
                # check if all sub-tasks are complete first
                if (updated_task.get("sub_task_completion_required") and 
                    update_data.get("completed") and 
                    not await TaskService._all_subtasks_completed(task_id)):
                    # Revert the completion if not all sub-tasks are done
                    await update_document("tasks", {"id": task_id, "user_id": user_id}, {
                        "completed": False,
                        "completed_at": None,
                        "status": TaskStatusEnum.in_progress,
                        "kanban_column": "in_progress"
                    })
                    return False
        
        return success

    @staticmethod
    async def _update_parent_task_completion(parent_task_id: str, user_id: str):
        """Update parent task completion status based on sub-tasks"""
        parent_task = await find_document("tasks", {"id": parent_task_id, "user_id": user_id})
        if not parent_task or not parent_task.get("sub_task_completion_required"):
            return
        
        # Check if all sub-tasks are completed
        all_subtasks_complete = await TaskService._all_subtasks_completed(parent_task_id)
        
        if all_subtasks_complete and not parent_task.get("completed"):
            # Mark parent as complete
            await update_document("tasks", {"id": parent_task_id, "user_id": user_id}, {
                "completed": True,
                "completed_at": datetime.utcnow(),
                "status": TaskStatusEnum.completed,
                "kanban_column": "done",
                "updated_at": datetime.utcnow()
            })
        elif not all_subtasks_complete and parent_task.get("completed"):
            # Mark parent as incomplete
            await update_document("tasks", {"id": parent_task_id, "user_id": user_id}, {
                "completed": False,
                "completed_at": None,
                "status": TaskStatusEnum.in_progress,
                "kanban_column": "in_progress",
                "updated_at": datetime.utcnow()
            })

    @staticmethod
    async def _all_subtasks_completed(parent_task_id: str) -> bool:
        """Check if all sub-tasks of a parent task are completed"""
        subtasks = await find_documents("tasks", {"parent_task_id": parent_task_id})
        if not subtasks:
            return True  # No sub-tasks means parent can be completed
        
        return all(subtask.get("completed", False) for subtask in subtasks)

    @staticmethod
    async def get_task_with_subtasks(user_id: str, task_id: str) -> Optional[TaskResponse]:
        """Get a task with all its sub-tasks"""
        task_doc = await find_document("tasks", {"id": task_id, "user_id": user_id})
        if not task_doc:
            return None
        
        return await TaskService._build_task_response(task_doc, include_subtasks=True)

    @staticmethod
    async def create_subtask(user_id: str, parent_task_id: str, subtask_data: TaskCreate) -> Task:
        """Create a sub-task under a parent task"""
        # Validate that the parent task exists and belongs to the user
        parent_task = await find_document("tasks", {"id": parent_task_id, "user_id": user_id})
        if not parent_task:
            raise ValueError(f"Parent task with ID {parent_task_id} not found or does not belong to user")
        
        # Set the parent_task_id and inherit project_id from parent
        subtask_data.parent_task_id = parent_task_id
        subtask_data.project_id = parent_task["project_id"]
        
        # Create the sub-task
        return await TaskService.create_task(user_id, subtask_data)

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

class InsightsService:
    @staticmethod
    async def get_insights_data(user_id: str, date_range: str = 'all_time'):
        """Get comprehensive insights data for visualization"""
        from datetime import datetime, timedelta
        
        # Calculate date range filter
        now = datetime.utcnow()
        date_filter = {}
        
        if date_range == 'weekly':
            week_ago = now - timedelta(days=7)
            date_filter = {"created_at": {"$gte": week_ago}}
        elif date_range == 'monthly':
            month_ago = now - timedelta(days=30)
            date_filter = {"created_at": {"$gte": month_ago}}
        elif date_range == 'yearly':
            year_ago = now - timedelta(days=365)
            date_filter = {"created_at": {"$gte": year_ago}}
        # 'all_time' uses no date filter
        
        # Base filter for user
        base_filter = {"user_id": user_id}
        if date_filter:
            base_filter.update(date_filter)
        
        # Overall Task Status Counts
        total_tasks = await count_documents("tasks", base_filter)
        completed_tasks = await count_documents("tasks", {**base_filter, "status": "completed"})
        in_progress_tasks = await count_documents("tasks", {**base_filter, "status": "in-progress"})
        todo_tasks = await count_documents("tasks", {**base_filter, "status": "todo"})
        overdue_tasks = 0  # We'll calculate this separately
        
        # Get tasks that are overdue
        overdue_filter = {
            **base_filter,
            "due_date": {"$lt": now},
            "status": {"$ne": "completed"}
        }
        overdue_tasks = await count_documents("tasks", overdue_filter)
        
        # Areas with their progress
        areas = await find_documents("areas", {"user_id": user_id})
        areas_data = []
        
        for area in areas:
            area_projects = await find_documents("projects", {"user_id": user_id, "area_id": area["id"]})
            area_tasks = []
            
            # Get all tasks for projects in this area
            for project in area_projects:
                project_tasks = await find_documents("tasks", {"user_id": user_id, "project_id": project["id"]})
                area_tasks.extend(project_tasks)
            
            # Apply date filtering to tasks
            if date_filter.get("created_at"):
                area_tasks = [t for t in area_tasks if t["created_at"] >= date_filter["created_at"]["$gte"]]
            
            total_area_tasks = len(area_tasks)
            completed_area_tasks = len([t for t in area_tasks if t["status"] == "completed"])
            
            completion_percentage = (completed_area_tasks / total_area_tasks * 100) if total_area_tasks > 0 else 0
            
            areas_data.append({
                "id": area["id"],
                "name": area["name"],
                "color": area.get("color", "#F4B400"),
                "total_projects": len(area_projects),
                "total_tasks": total_area_tasks,
                "completed_tasks": completed_area_tasks,
                "completion_percentage": round(completion_percentage, 1),
                "projects": []  # Will be populated when drilling down
            })
        
        # Projects overview
        all_projects = await find_documents("projects", {"user_id": user_id})
        projects_data = []
        
        for project in all_projects:
            project_tasks = await find_documents("tasks", {"user_id": user_id, "project_id": project["id"]})
            
            # Apply date filtering
            if date_filter.get("created_at"):
                project_tasks = [t for t in project_tasks if t["created_at"] >= date_filter["created_at"]["$gte"]]
            
            total_project_tasks = len(project_tasks)
            completed_project_tasks = len([t for t in project_tasks if t["status"] == "completed"])
            
            completion_percentage = (completed_project_tasks / total_project_tasks * 100) if total_project_tasks > 0 else 0
            
            projects_data.append({
                "id": project["id"],
                "name": project["name"],
                "area_id": project.get("area_id"),
                "status": project.get("status", "Not Started"),
                "priority": project.get("priority", "medium"),
                "total_tasks": total_project_tasks,
                "completed_tasks": completed_project_tasks,
                "completion_percentage": round(completion_percentage, 1)
            })
        
        # Time-based analytics
        productivity_by_day = {}  # Could implement daily completion tracking
        
        return {
            "date_range": date_range,
            "generated_at": now.isoformat(),
            "overall_stats": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "in_progress_tasks": in_progress_tasks,
                "todo_tasks": todo_tasks,
                "overdue_tasks": overdue_tasks,
                "completion_rate": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
            },
            "task_status_breakdown": {
                "completed": completed_tasks,
                "in_progress": in_progress_tasks,
                "todo": todo_tasks,
                "overdue": overdue_tasks
            },
            "areas": areas_data,
            "projects": projects_data,
            "productivity_trends": productivity_by_day
        }

    @staticmethod
    async def get_area_drill_down(user_id: str, area_id: str, date_range: str = 'all_time'):
        """Get detailed breakdown for a specific area"""
        from datetime import datetime, timedelta
        
        # Calculate date range filter
        now = datetime.utcnow()
        date_filter = {}
        
        if date_range == 'weekly':
            week_ago = now - timedelta(days=7)
            date_filter = {"created_at": {"$gte": week_ago}}
        elif date_range == 'monthly':
            month_ago = now - timedelta(days=30)
            date_filter = {"created_at": {"$gte": month_ago}}
        elif date_range == 'yearly':
            year_ago = now - timedelta(days=365)
            date_filter = {"created_at": {"$gte": year_ago}}
        
        # Get area info
        area = await find_document("areas", {"id": area_id, "user_id": user_id})
        if not area:
            raise ValueError("Area not found")
        
        # Get projects in this area
        projects = await find_documents("projects", {"user_id": user_id, "area_id": area_id})
        projects_data = []
        
        for project in projects:
            project_tasks = await find_documents("tasks", {"user_id": user_id, "project_id": project["id"]})
            
            # Apply date filtering
            if date_filter.get("created_at"):
                project_tasks = [t for t in project_tasks if t["created_at"] >= date_filter["created_at"]["$gte"]]
            
            total_tasks = len(project_tasks)
            completed_tasks = len([t for t in project_tasks if t["status"] == "completed"])
            in_progress_tasks = len([t for t in project_tasks if t["status"] == "in-progress"])
            todo_tasks = len([t for t in project_tasks if t["status"] == "todo"])
            
            completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            projects_data.append({
                "id": project["id"],
                "name": project["name"],
                "status": project.get("status", "Not Started"),
                "priority": project.get("priority", "medium"),
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "in_progress_tasks": in_progress_tasks,
                "todo_tasks": todo_tasks,
                "completion_percentage": round(completion_percentage, 1)
            })
        
        return {
            "area": {
                "id": area["id"],
                "name": area["name"],
                "color": area.get("color", "#F4B400")
            },
            "projects": projects_data,
            "date_range": date_range
        }

    @staticmethod
    async def get_project_drill_down(user_id: str, project_id: str, date_range: str = 'all_time'):
        """Get detailed task breakdown for a specific project"""
        from datetime import datetime, timedelta
        
        # Calculate date range filter
        now = datetime.utcnow()
        date_filter = {}
        
        if date_range == 'weekly':
            week_ago = now - timedelta(days=7)
            date_filter = {"created_at": {"$gte": week_ago}}
        elif date_range == 'monthly':
            month_ago = now - timedelta(days=30)
            date_filter = {"created_at": {"$gte": month_ago}}
        elif date_range == 'yearly':
            year_ago = now - timedelta(days=365)
            date_filter = {"created_at": {"$gte": year_ago}}
        
        # Get project info
        project = await find_document("projects", {"id": project_id, "user_id": user_id})
        if not project:
            raise ValueError("Project not found")
        
        # Get area info
        area = None
        if project.get("area_id"):
            area = await find_document("areas", {"id": project["area_id"], "user_id": user_id})
        
        # Get tasks for this project
        tasks = await find_documents("tasks", {"user_id": user_id, "project_id": project_id})
        
        # Apply date filtering
        if date_filter.get("created_at"):
            tasks = [t for t in tasks if t["created_at"] >= date_filter["created_at"]["$gte"]]
        
        # Sort tasks by priority and due date
        def task_sort_key(task):
            priority_order = {"high": 0, "medium": 1, "low": 2}
            return (
                priority_order.get(task.get("priority", "medium"), 1),
                task.get("due_date") or "9999-12-31"
            )
        
        tasks.sort(key=task_sort_key)
        
        return {
            "project": {
                "id": project["id"],
                "name": project["name"],
                "status": project.get("status", "Not Started"),
                "priority": project.get("priority", "medium")
            },
            "area": {
                "id": area["id"] if area else None,
                "name": area["name"] if area else None,
                "color": area.get("color", "#F4B400") if area else "#F4B400"
            } if area else None,
            "tasks": tasks,
            "date_range": date_range
        }

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
        
        # Updated task counts to work with projects
        total_tasks = await count_documents("tasks", {"user_id": user_id})
        tasks_completed = await count_documents("tasks", {"user_id": user_id, "completed": True})
        
        # New counts for areas and projects
        total_areas = await count_documents("areas", {"user_id": user_id})
        total_projects = await count_documents("projects", {"user_id": user_id})
        completed_projects = await count_documents("projects", {"user_id": user_id, "status": "Completed"})
        
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
            "total_areas": total_areas,
            "total_projects": total_projects,
            "completed_projects": completed_projects,
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
        total_points = (habits_completed_today * 10) + (tasks_completed * 15) + (badges_earned * 50) + (courses_completed * 100) + (completed_projects * 25)
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
        today_tasks = await TaskService.get_today_tasks(user_id)
        
        # Get areas with projects
        areas = await AreaService.get_user_areas(user_id, include_projects=True)
        
        # Get badges (placeholder for now)
        recent_achievements = []
        
        return UserDashboard(
            user=user,
            stats=stats,
            recent_habits=recent_habits[:5],  # Limit to 5 most recent
            recent_tasks=recent_tasks[:5],
            recent_courses=recent_courses[:3],
            recent_achievements=recent_achievements,
            areas=areas,
            today_tasks=today_tasks
        )

    @staticmethod
    async def get_today_view(user_id: str) -> TodayView:
        """Get today's focused view with curated tasks"""
        today_tasks = await TaskService.get_today_tasks(user_id)
        available_tasks = await TaskService.get_available_tasks_for_today(user_id)
        habits = await HabitService.get_user_habits(user_id)
        
        # Calculate totals
        total_tasks = len(today_tasks)
        completed_tasks = len([t for t in today_tasks if t.completed])
        estimated_duration = sum([t.estimated_duration or 0 for t in today_tasks])
        
        return TodayView(
            date=datetime.now(),
            tasks=today_tasks,
            habits=habits,
            available_tasks=available_tasks,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            estimated_duration=estimated_duration,
            pomodoro_sessions=0  # TODO: Implement pomodoro session tracking
        )