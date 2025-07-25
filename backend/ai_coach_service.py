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
        - IMPORTANCE BOOST: Critical=50, High=35, Medium=20, Medium-Low=10, Low=5 points
        - AREA/PROJECT IMPORTANCE: Inherited from parent area/project
        """
        try:
            # Get all active (non-completed) tasks with project and area info
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
            
            # Get projects and areas to access importance data
            projects = await find_documents("projects", {"user_id": user_id})
            areas = await find_documents("areas", {"user_id": user_id})
            
            # Create lookup dictionaries for easy access
            project_lookup = {p["id"]: p for p in projects}
            area_lookup = {a["id"]: a for a in areas}
            
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
                if task.get('dependency_tasks'):
                    if task.get('can_start', True):
                        score += 60
                        reasons.append("Dependencies cleared")
                
                # LOW WEIGHT: Oldest "In Progress" tasks (40 points)
                if task.get('status') == 'in_progress':
                    score += 40
                    reasons.append("In progress")
                
                # TASK PRIORITY BOOST: Add points based on task priority
                priority_boost = {
                    'high': 30,
                    'medium': 20,
                    'low': 10
                }.get(task.get('priority', 'medium'), 20)
                score += priority_boost
                
                # NEW: IMPORTANCE BOOST from project and area
                importance_score = 0
                project_importance = None
                area_importance = None
                
                # Get project importance
                project_id = task.get('project_id')
                if project_id and project_id in project_lookup:
                    project = project_lookup[project_id]
                    project_importance = project.get('importance', 3)  # Default to medium (3)
                    
                    # Get area importance from project's area
                    area_id = project.get('area_id')
                    if area_id and area_id in area_lookup:
                        area = area_lookup[area_id]
                        area_importance = area.get('importance', 3)  # Default to medium (3)
                
                # Calculate combined importance score (project importance has higher weight)
                if project_importance:
                    # Project importance: Critical=50, High=35, Medium=20, Medium-Low=10, Low=5
                    project_score = {5: 50, 4: 35, 3: 20, 2: 10, 1: 5}.get(project_importance, 20)
                    importance_score += project_score
                    reasons.append(f"High-importance project" if project_importance >= 4 else f"Important project")
                
                if area_importance:
                    # Area importance (lower weight): Critical=25, High=20, Medium=10, Medium-Low=5, Low=2
                    area_score = {5: 25, 4: 20, 3: 10, 2: 5, 1: 2}.get(area_importance, 10)
                    importance_score += area_score
                    if area_importance >= 4:
                        reasons.append(f"Critical life area")
                
                score += importance_score
                
                # Only include tasks with some score (avoid recommending random low-priority tasks)
                if score > 0:
                    scored_tasks.append({
                        'task': task,
                        'score': score,
                        'reasons': reasons,
                        'priority_boost': priority_boost,
                        'importance_score': importance_score,
                        'project_importance': project_importance,
                        'area_importance': area_importance
                    })
            
            # Sort by score (highest first) and return top N
            scored_tasks.sort(key=lambda x: x['score'], reverse=True)
            
            # Format for frontend consumption
            recommendations = []
            for item in scored_tasks[:limit]:
                task = item['task']
                
                # Build enhanced coaching message with importance context
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
                    'reasons': item['reasons'],
                    'importance_context': {
                        'project_importance': item['project_importance'],
                        'area_importance': item['area_importance'],
                        'importance_score': item['importance_score']
                    }
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting today's priorities for user {user_id}: {str(e)}")
            return []
    
    @staticmethod
    def _build_coaching_message(scored_item: Dict) -> str:
        """Build an encouraging, action-oriented coaching message for the task with importance context"""
        task = scored_item['task']
        reasons = scored_item['reasons']
        score = scored_item['score']
        importance_score = scored_item.get('importance_score', 0)
        project_importance = scored_item.get('project_importance', 3)
        
        task_name = task.get('name', 'this task')
        
        # High importance + urgent tasks (critical path)
        if score >= 100 and importance_score >= 35:
            if 'Overdue' in ' '.join(reasons):
                return f"🚨 Critical: {task_name} is both overdue AND high-importance. This needs immediate attention to avoid major impact."
            elif 'Due today' in ' '.join(reasons):
                return f"🎯 Perfect timing: {task_name} is due today and highly important. Completing this will have maximum impact."
        
        # High priority messages (overdue, due today)
        elif score >= 80:
            if 'Overdue' in ' '.join(reasons):
                if importance_score >= 35:
                    return f"⚡ Priority focus: {task_name} is overdue for an important project. Let's get this back on track."
                else:
                    return f"Time to tackle {task_name}. Breaking through overdue tasks builds momentum for everything else."
            elif 'Due today' in ' '.join(reasons):
                if importance_score >= 35:
                    return f"🏆 Today's key win: {task_name} is due and important. This completion will drive significant progress."
                else:
                    return f"Perfect timing to complete {task_name}. Finishing today's priorities feels amazing."
        
        # High importance but not urgent (important strategic work)
        elif importance_score >= 35:
            if project_importance >= 4:
                return f"💡 Strategic focus: {task_name} is part of a critical project. Steady progress here creates lasting value."
            else:
                return f"🎯 Important work: {task_name} may not be urgent, but it's highly valuable. Great time to make progress."
        
        # Medium priority messages (unblocked dependencies)
        elif score >= 60:
            if 'Dependencies cleared' in ' '.join(reasons):
                return f"✅ Ready to roll: {task_name} is unblocked and ready for progress. Dependencies are cleared!"
        
        # Lower priority but still recommended
        else:
            if importance_score >= 20:
                return f"📈 Solid choice: {task_name} contributes to important goals. Small steps lead to big wins."
            else:
                return f"Ready to advance {task_name}? Consistent progress keeps momentum going."
        
        return f"Focus on {task_name} to keep your momentum going."