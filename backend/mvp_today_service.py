"""
MVP Today Service for Aurum Life v1.1
Optimized query for sub-150ms Today view performance
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from supabase_client import supabase_manager
from mvp_performance_monitor import db_perf_tracker
import logging

logger = logging.getLogger(__name__)

class MVPTodayService:
    """Optimized service for Today view"""
    
    @staticmethod
    @db_perf_tracker.track_query("tasks", "today_view")
    async def get_today_tasks(user_id: str) -> Dict:
        """
        Get all tasks for today with a single optimized query
        Uses compound index for maximum performance
        """
        try:
            # Define "today" - tasks due today or overdue
            today_end = datetime.utcnow().replace(hour=23, minute=59, second=59)
            
            # Use aggregation pipeline for single query
            pipeline = [
                # Match user's incomplete tasks
                {
                    "$match": {
                        "user_id": user_id,
                        "completed": False,
                        "$or": [
                            {"due_date": {"$lte": today_end}},
                            {"due_date": None}
                        ]
                    }
                },
                # Sort by score (uses index)
                {
                    "$sort": {"current_score": -1}
                },
                # Lookup project info
                {
                    "$lookup": {
                        "from": "projects",
                        "localField": "project_id",
                        "foreignField": "id",
                        "as": "project"
                    }
                },
                # Unwind project (should always exist)
                {
                    "$unwind": {
                        "path": "$project",
                        "preserveNullAndEmptyArrays": True
                    }
                },
                # Lookup area info
                {
                    "$lookup": {
                        "from": "areas",
                        "localField": "project.area_id",
                        "foreignField": "id",
                        "as": "area"
                    }
                },
                # Unwind area
                {
                    "$unwind": {
                        "path": "$area",
                        "preserveNullAndEmptyArrays": True
                    }
                },
                # Project only needed fields
                {
                    "$project": {
                        "id": 1,
                        "name": 1,
                        "description": 1,
                        "priority": 1,
                        "due_date": 1,
                        "due_time": 1,
                        "completed": 1,
                        "current_score": 1,
                        "project_id": 1,
                        "project_name": "$project.name",
                        "area_id": "$project.area_id",
                        "area_name": "$area.name"
                    }
                },
                # Limit to reasonable number
                {
                    "$limit": 50
                }
            ]
            
            # Execute aggregation
            tasks = await supabase_manager.aggregate_documents("tasks", pipeline)
            
            # Calculate stats
            total_tasks = len(tasks)
            completed_today = await supabase_manager.count_documents(
                "tasks",
                {
                    "user_id": user_id,
                    "completed": True,
                    "completed_at": {
                        "$gte": datetime.utcnow().replace(hour=0, minute=0, second=0)
                    }
                }
            )
            
            return {
                "tasks": tasks,
                "stats": {
                    "total_today": total_tasks,
                    "completed_today": completed_today,
                    "completion_rate": (completed_today / total_tasks * 100) if total_tasks > 0 else 0
                },
                "generated_at": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Failed to get today tasks: {e}")
            return {
                "tasks": [],
                "stats": {
                    "total_today": 0,
                    "completed_today": 0,
                    "completion_rate": 0
                },
                "error": str(e)
            }
    
    @staticmethod
    async def mark_task_complete(user_id: str, task_id: str, completed: bool = True) -> bool:
        """
        Mark a task as complete/incomplete
        Triggers score recalculation for dependent tasks
        """
        try:
            # Verify task belongs to user
            task = await supabase_manager.find_document(
                "tasks",
                {"id": task_id, "user_id": user_id}
            )
            
            if not task:
                logger.error(f"Task {task_id} not found for user {user_id}")
                return False
                
            # Update task
            update_data = {
                "completed": completed,
                "completed_at": datetime.utcnow() if completed else None
            }
            
            success = await supabase_manager.update_document(
                "tasks",
                {"id": task_id},
                update_data
            )
            
            if success:
                # Queue score update for dependent tasks
                from mvp_scoring_engine import update_user_task_scores
                update_user_task_scores.delay(user_id)
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to mark task complete: {e}")
            return False
    
    @staticmethod
    async def get_daily_summary(user_id: str) -> Dict:
        """
        Get a summary of the day's progress
        Used for evening reflection context
        """
        try:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0)
            
            # Get completed tasks today
            completed_tasks = await supabase_manager.find_documents(
                "tasks",
                {
                    "user_id": user_id,
                    "completed": True,
                    "completed_at": {"$gte": today_start}
                }
            )
            
            # Group by project
            projects_touched = {}
            for task in completed_tasks:
                project_id = task.get("project_id")
                if project_id:
                    if project_id not in projects_touched:
                        projects_touched[project_id] = 0
                    projects_touched[project_id] += 1
            
            # Get high priority tasks still pending
            pending_high_priority = await supabase_manager.count_documents(
                "tasks",
                {
                    "user_id": user_id,
                    "completed": False,
                    "priority": "high",
                    "due_date": {"$lte": datetime.utcnow()}
                }
            )
            
            return {
                "completed_count": len(completed_tasks),
                "projects_touched": len(projects_touched),
                "pending_high_priority": pending_high_priority,
                "top_project": max(projects_touched.items(), key=lambda x: x[1])[0] if projects_touched else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get daily summary: {e}")
            return {
                "completed_count": 0,
                "projects_touched": 0,
                "pending_high_priority": 0,
                "top_project": None
            }

# FastAPI endpoints
from fastapi import APIRouter, Depends, HTTPException
from supabase_auth import get_current_active_user
from models import User

today_router = APIRouter(prefix="/api/today", tags=["today"])

@today_router.get("/tasks")
async def get_today_tasks(current_user: User = Depends(get_current_active_user)):
    """Get today's tasks for the current user"""
    service = MVPTodayService()
    result = await service.get_today_tasks(current_user.id)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
        
    return result

@today_router.patch("/tasks/{task_id}")
async def update_task_completion(
    task_id: str,
    completed: bool,
    current_user: User = Depends(get_current_active_user)
):
    """Mark a task as complete/incomplete"""
    service = MVPTodayService()
    success = await service.mark_task_complete(current_user.id, task_id, completed)
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update task")
        
    return {"success": True, "task_id": task_id, "completed": completed}

@today_router.get("/summary")
async def get_daily_summary(current_user: User = Depends(get_current_active_user)):
    """Get daily summary for reflection"""
    service = MVPTodayService()
    return await service.get_daily_summary(current_user.id)