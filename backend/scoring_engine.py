"""
🚀 THE ARCHITECT'S DEFINITIVE SCORING ENGINE
Event-driven task priority calculation system for Aurum Life
Eliminates N+1 queries and guarantees sub-200ms API responses
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from celery_app import app
from supabase_client import find_document, find_documents, update_document
from models import TaskResponse
import logging

logger = logging.getLogger(__name__)

class ScoringEngine:
    """The definitive task scoring algorithm for Aurum Life"""
    
    # Scoring algorithm constants
    MAX_SCORE = 100.0
    URGENCY_WEIGHT = 40.0  # Due date urgency (0-40 points)
    PRIORITY_WEIGHT = 20.0  # Task priority (0-20 points) 
    HIERARCHY_WEIGHT = 25.0  # Area/Project/Pillar importance (0-25 points)
    DEPENDENCY_WEIGHT = 15.0  # Dependency availability (0-15 points)
    PROGRESS_WEIGHT = 10.0  # Completion progress bonus (0-10 points)
    
    @staticmethod
    def calculate_priority_score(
        task: dict, 
        area_importance: int, 
        project_importance: int, 
        pillar_weight: float, 
        dependencies_met: bool
    ) -> float:
        """
        Calculate the definitive priority score (0-100)
        Higher scores = higher priority for Today view
        
        Args:
            task: Task document from database
            area_importance: 1-5 scale from parent area
            project_importance: 1-5 scale from parent project  
            pillar_weight: 0.1-2.0 scale from root pillar
            dependencies_met: True if all dependencies are completed
            
        Returns:
            Priority score between 0-100
        """
        base_score = 0.0
        
        # 1. DUE DATE URGENCY (0-40 points) - Most critical factor
        due_date = task.get("due_date")
        if due_date:
            if isinstance(due_date, str):
                due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            
            days_until_due = (due_date - datetime.utcnow()).days
            
            if days_until_due <= 0:
                urgency_score = 40.0  # Overdue = maximum urgency
            elif days_until_due <= 1:
                urgency_score = 35.0  # Due today/tomorrow
            elif days_until_due <= 3:
                urgency_score = 25.0  # Due within 3 days
            elif days_until_due <= 7:
                urgency_score = 15.0  # Due this week
            elif days_until_due <= 14:
                urgency_score = 8.0   # Due within 2 weeks
            else:
                urgency_score = max(0, 5 - (days_until_due * 0.1))  # Decay over time
        else:
            urgency_score = 5.0  # No due date = low urgency baseline
            
        base_score += urgency_score
        
        # 2. TASK PRIORITY (0-20 points) - User-defined importance
        priority = task.get("priority", "medium")
        priority_map = {
            "high": 20.0,
            "medium": 12.0, 
            "low": 5.0
        }
        priority_score = priority_map.get(priority.lower() if isinstance(priority, str) else "medium", 12.0)
        base_score += priority_score
        
        # 3. HIERARCHICAL IMPORTANCE (0-25 points) - Context significance
        # Area importance contributes 0-10 points
        area_score = (area_importance / 5.0) * 10.0
        
        # Project importance contributes 0-10 points  
        project_score = (project_importance / 5.0) * 10.0
        
        # Pillar weight contributes 0-5 points
        pillar_score = min(pillar_weight * 2.5, 5.0)
        
        hierarchy_score = area_score + project_score + pillar_score
        base_score += hierarchy_score
        
        # 4. DEPENDENCY AVAILABILITY (0-15 points) - Can work start immediately?
        if dependencies_met:
            dependency_score = 15.0  # Can start immediately
        else:
            dependency_score = 2.0   # Blocked but still valuable for planning
            
        base_score += dependency_score
        
        # 5. COMPLETION PROGRESS BONUS (0-10 points) - Momentum factor
        progress_percentage = task.get("progress_percentage", 0)
        if progress_percentage > 0:
            # Tasks closer to completion get priority boost
            progress_bonus = min(progress_percentage / 10.0, 10.0)
            base_score += progress_bonus
        
        # 6. TASK AGE FACTOR - Slight boost for older tasks to prevent stagnation
        created_at = task.get("created_at")
        if created_at:
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            
            days_old = (datetime.utcnow() - created_at).days
            if days_old > 7:  # Tasks older than a week get small boost
                age_bonus = min(days_old * 0.1, 3.0)  # Max 3 points
                base_score += age_bonus
        
        # Ensure score is within bounds
        final_score = min(base_score, ScoringEngine.MAX_SCORE)
        
        logger.debug(
            f"Score calculated for task {task.get('id', 'unknown')}: "
            f"urgency={urgency_score:.1f}, priority={priority_score:.1f}, "
            f"hierarchy={hierarchy_score:.1f}, dependency={dependency_score:.1f}, "
            f"progress={progress_percentage/10.0:.1f}, final={final_score:.1f}"
        )
        
        return final_score

    @staticmethod
    async def get_task_hierarchy_data(task_doc: dict) -> tuple:
        """
        Efficiently fetch hierarchy data for a task
        Returns: (area_importance, project_importance, pillar_weight)
        """
        area_importance = 3  # Default
        project_importance = 3  # Default  
        pillar_weight = 1.0  # Default
        
        try:
            # Get project data if task has project_id
            if task_doc.get("project_id"):
                project_doc = await find_document("projects", {"id": task_doc["project_id"]})
                if project_doc:
                    project_importance = project_doc.get("importance", 3)
                    
                    # Get area data if project has area_id
                    if project_doc.get("area_id"):
                        area_doc = await find_document("areas", {"id": project_doc["area_id"]})
                        if area_doc:
                            area_importance = area_doc.get("importance", 3)
                            
                            # Get pillar data if area has pillar_id
                            if area_doc.get("pillar_id"):
                                pillar_doc = await find_document("pillars", {"id": area_doc["pillar_id"]})
                                if pillar_doc:
                                    pillar_weight = pillar_doc.get("weight", 1.0)
            
            # Direct area assignment (for tasks without projects)
            elif task_doc.get("area_id"):
                area_doc = await find_document("areas", {"id": task_doc["area_id"]})
                if area_doc:
                    area_importance = area_doc.get("importance", 3)
                    
                    if area_doc.get("pillar_id"):
                        pillar_doc = await find_document("pillars", {"id": area_doc["pillar_id"]})
                        if pillar_doc:
                            pillar_weight = pillar_doc.get("weight", 1.0)
                            
        except Exception as e:
            logger.error(f"Error fetching hierarchy data for task {task_doc.get('id')}: {e}")
        
        return area_importance, project_importance, pillar_weight

    @staticmethod
    async def check_dependencies_met(task_doc: dict) -> bool:
        """
        Efficiently check if all task dependencies are completed
        Returns: True if all dependencies are met or no dependencies exist
        """
        dependency_ids = task_doc.get("dependency_task_ids", [])
        if not dependency_ids:
            return True
            
        try:
            # Single query to check if any dependencies are incomplete
            incomplete_deps = await find_documents("tasks", {
                "id": {"$in": dependency_ids},
                "completed": False
            })
            
            # Dependencies are met if no incomplete dependencies found
            return len(incomplete_deps) == 0
            
        except Exception as e:
            logger.error(f"Error checking dependencies for task {task_doc.get('id')}: {e}")
            return True  # Assume dependencies met on error to avoid blocking tasks


# 🚀 CELERY TASKS FOR ASYNCHRONOUS SCORING

@app.task(bind=True, max_retries=3, name='scoring_engine.recalculate_task_score')
def recalculate_task_score(self, task_id: str) -> dict:
    """
    Celery task: Recalculate priority score for a single task
    This runs asynchronously and updates the task's current_score field
    """
    try:
        logger.info(f"🎯 Starting score recalculation for task: {task_id}")
        result = asyncio.run(_recalculate_single_task_score(task_id))
        logger.info(f"✅ Score recalculation completed for task: {task_id}, score: {result.get('new_score', 'unknown')}")
        return result
        
    except Exception as exc:
        logger.error(f"❌ Score recalculation failed for task {task_id}: {exc}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

async def _recalculate_single_task_score(task_id: str) -> dict:
    """Internal async function to recalculate a task score"""
    try:
        # Fetch the task
        task_doc = await find_document("tasks", {"id": task_id})
        if not task_doc:
            return {"error": "Task not found", "task_id": task_id}
        
        # Skip completed tasks - they don't need active scoring
        if task_doc.get("completed", False):
            return {"message": "Skipped completed task", "task_id": task_id}
        
        # Get hierarchy data efficiently
        area_importance, project_importance, pillar_weight = await ScoringEngine.get_task_hierarchy_data(task_doc)
        
        # Check dependencies
        dependencies_met = await ScoringEngine.check_dependencies_met(task_doc)
        
        # Calculate the new score
        new_score = ScoringEngine.calculate_priority_score(
            task_doc,
            area_importance,
            project_importance, 
            pillar_weight,
            dependencies_met
        )
        
        # Update the task with new score and cached hierarchy data
        update_data = {
            "current_score": new_score,
            "score_last_updated": datetime.utcnow(),
            "area_importance": area_importance,
            "project_importance": project_importance,
            "pillar_weight": pillar_weight,
            "dependencies_met": dependencies_met,
            "score_calculation_version": 1
        }
        
        await update_document("tasks", {"id": task_id}, update_data)
        
        return {
            "task_id": task_id,
            "new_score": new_score,
            "hierarchy_data": {
                "area_importance": area_importance,
                "project_importance": project_importance,
                "pillar_weight": pillar_weight
            },
            "dependencies_met": dependencies_met,
            "updated_at": update_data["score_last_updated"].isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in _recalculate_single_task_score for {task_id}: {e}")
        return {"error": str(e), "task_id": task_id}

@app.task(bind=True, max_retries=3, name='scoring_engine.recalculate_dependent_tasks')
def recalculate_dependent_tasks(self, completed_task_id: str) -> dict:
    """
    Celery task: When a task is completed, recalculate tasks that depend on it
    This unlocks blocked tasks and updates their scores
    """
    try:
        logger.info(f"🔗 Starting dependent task recalculation for completed task: {completed_task_id}")
        result = asyncio.run(_recalculate_dependent_tasks(completed_task_id))
        logger.info(f"✅ Dependent task recalculation completed: {result.get('tasks_updated', 0)} tasks updated")
        return result
        
    except Exception as exc:
        logger.error(f"❌ Dependent task recalculation failed for {completed_task_id}: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

async def _recalculate_dependent_tasks(completed_task_id: str) -> dict:
    """Internal async function to recalculate dependent tasks"""
    try:
        # Find all incomplete tasks that depend on the completed task
        dependent_tasks = await find_documents("tasks", {
            "dependency_task_ids": completed_task_id,
            "completed": False
        })
        
        if not dependent_tasks:
            return {"message": "No dependent tasks found", "completed_task_id": completed_task_id, "tasks_updated": 0}
        
        # Recalculate each dependent task score
        updated_tasks = []
        for task in dependent_tasks:
            try:
                # Trigger individual score recalculation
                recalculate_task_score.delay(task["id"])
                updated_tasks.append(task["id"])
            except Exception as e:
                logger.error(f"Failed to trigger recalculation for dependent task {task['id']}: {e}")
        
        return {
            "completed_task_id": completed_task_id,
            "tasks_updated": len(updated_tasks),
            "updated_task_ids": updated_tasks
        }
        
    except Exception as e:
        logger.error(f"Error in _recalculate_dependent_tasks for {completed_task_id}: {e}")
        return {"error": str(e), "completed_task_id": completed_task_id}

@app.task(bind=True, max_retries=3, name='scoring_engine.recalculate_area_tasks')
def recalculate_area_tasks(self, area_id: str, new_importance: int) -> dict:
    """
    Celery task: When an area's importance changes, recalculate all its tasks
    """
    try:
        logger.info(f"🏢 Starting area task recalculation for area: {area_id}, new importance: {new_importance}")
        result = asyncio.run(_recalculate_area_tasks(area_id, new_importance))
        logger.info(f"✅ Area task recalculation completed: {result.get('tasks_updated', 0)} tasks updated")
        return result
        
    except Exception as exc:
        logger.error(f"❌ Area task recalculation failed for {area_id}: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

async def _recalculate_area_tasks(area_id: str, new_importance: int) -> dict:
    """Internal async function to recalculate area tasks"""
    try:
        # Find all incomplete tasks in this area (direct and through projects)
        
        # Tasks directly in the area
        direct_tasks = await find_documents("tasks", {
            "area_id": area_id,
            "completed": False
        })
        
        # Tasks in projects within this area
        projects_in_area = await find_documents("projects", {"area_id": area_id})
        project_ids = [p["id"] for p in projects_in_area]
        
        project_tasks = []
        if project_ids:
            project_tasks = await find_documents("tasks", {
                "project_id": {"$in": project_ids},
                "completed": False
            })
        
        # Combine all tasks
        all_tasks = direct_tasks + project_tasks
        
        if not all_tasks:
            return {"message": "No tasks found in area", "area_id": area_id, "tasks_updated": 0}
        
        # Trigger recalculation for each task
        updated_tasks = []
        for task in all_tasks:
            try:
                recalculate_task_score.delay(task["id"])
                updated_tasks.append(task["id"])
            except Exception as e:
                logger.error(f"Failed to trigger recalculation for area task {task['id']}: {e}")
        
        return {
            "area_id": area_id,
            "new_importance": new_importance,
            "tasks_updated": len(updated_tasks),
            "updated_task_ids": updated_tasks
        }
        
    except Exception as e:
        logger.error(f"Error in _recalculate_area_tasks for {area_id}: {e}")
        return {"error": str(e), "area_id": area_id}

@app.task(bind=True, max_retries=3, name='scoring_engine.recalculate_project_tasks')
def recalculate_project_tasks(self, project_id: str, new_importance: int) -> dict:
    """
    Celery task: When a project's importance changes, recalculate all its tasks
    """
    try:
        logger.info(f"📁 Starting project task recalculation for project: {project_id}, new importance: {new_importance}")
        result = asyncio.run(_recalculate_project_tasks(project_id, new_importance))
        logger.info(f"✅ Project task recalculation completed: {result.get('tasks_updated', 0)} tasks updated")
        return result
        
    except Exception as exc:
        logger.error(f"❌ Project task recalculation failed for {project_id}: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

async def _recalculate_project_tasks(project_id: str, new_importance: int) -> dict:
    """Internal async function to recalculate project tasks"""
    try:
        # Find all incomplete tasks in this project
        project_tasks = await find_documents("tasks", {
            "project_id": project_id,
            "completed": False
        })
        
        if not project_tasks:
            return {"message": "No tasks found in project", "project_id": project_id, "tasks_updated": 0}
        
        # Trigger recalculation for each task
        updated_tasks = []
        for task in project_tasks:
            try:
                recalculate_task_score.delay(task["id"])
                updated_tasks.append(task["id"])
            except Exception as e:
                logger.error(f"Failed to trigger recalculation for project task {task['id']}: {e}")
        
        return {
            "project_id": project_id,
            "new_importance": new_importance,
            "tasks_updated": len(updated_tasks),
            "updated_task_ids": updated_tasks
        }
        
    except Exception as e:
        logger.error(f"Error in _recalculate_project_tasks for {project_id}: {e}")
        return {"error": str(e), "project_id": project_id}


# 🚀 BULK SCORING OPERATIONS FOR MIGRATION AND MAINTENANCE

@app.task(bind=True, name='scoring_engine.initialize_all_task_scores')
def initialize_all_task_scores(self, user_id: Optional[str] = None, batch_size: int = 100) -> dict:
    """
    Celery task: Initialize scores for all tasks (or all tasks for a specific user)
    Used for initial migration and periodic maintenance
    """
    try:
        logger.info(f"🚀 Starting bulk score initialization for user: {user_id or 'ALL'}")
        result = asyncio.run(_initialize_all_task_scores(user_id, batch_size))
        logger.info(f"✅ Bulk score initialization completed: {result.get('tasks_processed', 0)} tasks processed")
        return result
        
    except Exception as exc:
        logger.error(f"❌ Bulk score initialization failed: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

async def _initialize_all_task_scores(user_id: Optional[str] = None, batch_size: int = 100) -> dict:
    """Internal async function to initialize all task scores"""
    try:
        # Build query filter
        query_filter = {"completed": False}
        if user_id:
            query_filter["user_id"] = user_id
        
        # Get all incomplete tasks
        all_tasks = await find_documents("tasks", query_filter)
        
        if not all_tasks:
            return {"message": "No tasks found to initialize", "tasks_processed": 0}
        
        # Process tasks in batches to avoid overwhelming the system
        processed_count = 0
        error_count = 0
        
        for i in range(0, len(all_tasks), batch_size):
            batch = all_tasks[i:i + batch_size]
            
            for task in batch:
                try:
                    # Trigger individual score calculation
                    recalculate_task_score.delay(task["id"])
                    processed_count += 1
                except Exception as e:
                    logger.error(f"Failed to trigger initialization for task {task['id']}: {e}")
                    error_count += 1
            
            # Small delay between batches to prevent system overload
            await asyncio.sleep(1)
        
        return {
            "user_id": user_id or "ALL",
            "tasks_processed": processed_count,
            "errors": error_count,
            "total_tasks": len(all_tasks),
            "batch_size": batch_size
        }
        
    except Exception as e:
        logger.error(f"Error in _initialize_all_task_scores: {e}")
        return {"error": str(e)}