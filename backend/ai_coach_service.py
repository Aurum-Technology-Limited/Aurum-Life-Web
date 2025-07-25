from datetime import datetime, timedelta
from typing import List, Dict, Optional
from database import find_documents
import logging

logger = logging.getLogger(__name__)

class AiCoachService:
    """AI Coach service focused on daily task prioritization"""
    
    @staticmethod
    async def get_todays_priorities(user_id: str, limit: int = 3) -> List[Dict]:
        """
        Get the top priority tasks for the user today using a weighted scoring algorithm
        
        Scoring weights:
        - Highest: Overdue tasks (100 points)
        - High: Due today (80 points)  
        - Medium: Recently unblocked dependencies (60 points)
        - Low: Oldest "In Progress" tasks (40 points)
        """
        try:
            # Get all active (non-completed) tasks for the user
            tasks = await find_documents(
                "tasks", 
                {
                    "user_id": user_id,
                    "completed": False,
                    "archived": {"$ne": True}
                }
            )
            
            if not tasks:
                return []
            
            today = datetime.utcnow().date()
            scored_tasks = []
            
            for task in tasks:
                score = 0
                reasons = []
                
                # Get task due date
                due_date = None
                if task.get('due_date'):
                    try:
                        due_date = datetime.fromisoformat(task['due_date'].replace('Z', '+00:00')).date()
                    except:
                        pass
                
                # HIGHEST WEIGHT: Overdue tasks (100 points)
                if due_date and due_date < today:
                    score += 100
                    days_overdue = (today - due_date).days
                    reasons.append(f"Overdue by {days_overdue} day{'s' if days_overdue > 1 else ''}")
                
                # HIGH WEIGHT: Due today (80 points)
                elif due_date and due_date == today:
                    score += 80
                    reasons.append("Due today")
                
                # MEDIUM WEIGHT: Recently unblocked dependencies (60 points)
                # Check if task has dependencies and they're recently completed
                if task.get('dependency_tasks'):
                    # For MVP, we'll check if task is not blocked (can_start != False)
                    if task.get('can_start', True):
                        score += 60
                        reasons.append("Dependencies cleared")
                
                # LOW WEIGHT: Oldest "In Progress" tasks (40 points)
                if task.get('status') == 'in_progress':
                    score += 40
                    reasons.append("In progress")
                
                # PRIORITY BOOST: Add points based on task priority
                priority_boost = {
                    'high': 30,
                    'medium': 20,
                    'low': 10
                }.get(task.get('priority', 'medium'), 20)
                
                score += priority_boost
                
                # Only include tasks with some score (avoid recommending random low-priority tasks)
                if score > 0:
                    scored_tasks.append({
                        'task': task,
                        'score': score,
                        'reasons': reasons,
                        'priority_boost': priority_boost
                    })
            
            # Sort by score (highest first) and return top N
            scored_tasks.sort(key=lambda x: x['score'], reverse=True)
            
            # Format for frontend consumption
            recommendations = []
            for item in scored_tasks[:limit]:
                task = item['task']
                
                # Build coaching message
                coaching_message = AiCoachService._build_coaching_message(item)
                
                recommendations.append({
                    'task_id': task['id'],
                    'task_name': task['name'],
                    'task_description': task.get('description', ''),
                    'project_name': task.get('project_name', ''),
                    'due_date': task.get('due_date'),
                    'priority': task.get('priority', 'medium'),
                    'score': item['score'],
                    'coaching_message': coaching_message,
                    'reasons': item['reasons']
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting today's priorities for user {user_id}: {str(e)}")
            return []
    
    @staticmethod
    def _build_coaching_message(scored_item: Dict) -> str:
        """Build an encouraging, action-oriented coaching message for the task"""
        task = scored_item['task']
        reasons = scored_item['reasons']
        score = scored_item['score']
        
        task_name = task.get('name', 'this task')
        
        # High priority messages (overdue, due today)
        if score >= 80:
            if 'Overdue' in ' '.join(reasons):
                return f"Time to tackle {task_name}. Breaking through overdue tasks builds momentum for everything else."
            elif 'Due today' in ' '.join(reasons):
                return f"Perfect timing to complete {task_name}. Finishing today's priorities feels amazing."
        
        # Medium priority messages (unblocked dependencies)
        elif score >= 60:
            if 'Dependencies cleared' in ' '.join(reasons):
                return f"Great news! {task_name} is ready to go. Dependencies are cleared - let's make progress."
        
        # Lower priority but still recommended
        else:
            return f"Ready to advance {task_name}? Small consistent steps lead to big wins."
        
        return f"Focus on {task_name} to keep your momentum going."