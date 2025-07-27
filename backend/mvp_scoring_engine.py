"""
MVP Scoring Engine for Aurum Life v1.1
Simple, deterministic task prioritization
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
from celery_app import app
from supabase_client import supabase_manager
import logging

logger = logging.getLogger(__name__)

class MVPScoringEngine:
    """Simplified scoring algorithm for MVP"""
    
    # Priority weights
    PRIORITY_WEIGHTS = {
        "high": 100,
        "medium": 60,
        "low": 30
    }
    
    @staticmethod
    def calculate_urgency_score(due_date: Optional[datetime]) -> float:
        """
        Calculate urgency score based on due date
        Returns: 0-100, where 100 is most urgent
        """
        if not due_date:
            return 0  # No due date = no urgency
            
        now = datetime.utcnow()
        days_until_due = (due_date - now).days
        
        # Overdue tasks get maximum urgency
        if days_until_due < 0:
            return 100
            
        # Linear decay: lose 10 points per day
        urgency = max(0, 100 - (days_until_due * 10))
        return urgency
    
    @staticmethod
    def calculate_task_score(task: Dict) -> float:
        """
        Calculate simple priority score for a task
        Formula: (user_priority * 0.6) + (urgency_score * 0.4)
        Returns: 0-100
        """
        # Get priority weight
        priority = task.get("priority", "medium")
        priority_weight = MVPScoringEngine.PRIORITY_WEIGHTS.get(priority, 60)
        
        # Get urgency score
        due_date = task.get("due_date")
        if due_date and isinstance(due_date, str):
            due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        urgency_score = MVPScoringEngine.calculate_urgency_score(due_date)
        
        # Calculate final score
        final_score = (priority_weight * 0.6) + (urgency_score * 0.4)
        
        return round(final_score, 2)

# Celery Tasks
@app.task
def update_task_score(task_id: str):
    """Update score for a single task"""
    try:
        # Get task
        task = asyncio.run(supabase_manager.find_document("tasks", {"id": task_id}))
        if not task:
            logger.error(f"Task {task_id} not found")
            return
            
        # Calculate new score
        new_score = MVPScoringEngine.calculate_task_score(task)
        
        # Update task
        asyncio.run(supabase_manager.update_document(
            "tasks", 
            {"id": task_id},
            {"current_score": new_score, "score_last_updated": datetime.utcnow()}
        ))
        
        logger.info(f"Updated task {task_id} score to {new_score}")
        
    except Exception as e:
        logger.error(f"Failed to update task score: {e}")

@app.task
def update_user_task_scores(user_id: str):
    """Update scores for all tasks belonging to a user"""
    try:
        # Get all incomplete tasks for user
        tasks = asyncio.run(supabase_manager.find_documents(
            "tasks",
            {"user_id": user_id, "completed": False}
        ))
        
        updated_count = 0
        for task in tasks:
            # Calculate new score
            new_score = MVPScoringEngine.calculate_task_score(task)
            
            # Update if changed
            if task.get("current_score") != new_score:
                asyncio.run(supabase_manager.update_document(
                    "tasks",
                    {"id": task["id"]},
                    {"current_score": new_score, "score_last_updated": datetime.utcnow()}
                ))
                updated_count += 1
                
        logger.info(f"Updated {updated_count} task scores for user {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to update user task scores: {e}")

@app.task
def daily_score_update():
    """Daily task to update all task scores (run at midnight)"""
    try:
        # Get all users
        users = asyncio.run(supabase_manager.find_documents("users", {}))
        
        for user in users:
            # Queue score update for each user
            update_user_task_scores.delay(user["id"])
            
        logger.info(f"Queued score updates for {len(users)} users")
        
    except Exception as e:
        logger.error(f"Failed to queue daily score updates: {e}")

# Async helper for non-Celery contexts
async def update_task_score_async(task_id: str):
    """Async version for immediate score updates"""
    try:
        # Get task
        task = await supabase_manager.find_document("tasks", {"id": task_id})
        if not task:
            return
            
        # Calculate new score
        new_score = MVPScoringEngine.calculate_task_score(task)
        
        # Update task
        await supabase_manager.update_document(
            "tasks",
            {"id": task_id},
            {"current_score": new_score, "score_last_updated": datetime.utcnow()}
        )
        
        return new_score
        
    except Exception as e:
        logger.error(f"Failed to update task score: {e}")
        return None

# Schedule daily score update
from celery.schedules import crontab

app.conf.beat_schedule = {
    'daily-score-update': {
        'task': 'mvp_scoring_engine.daily_score_update',
        'schedule': crontab(hour=0, minute=0),  # Run at midnight
    },
}

import asyncio  # Import at end to avoid circular imports