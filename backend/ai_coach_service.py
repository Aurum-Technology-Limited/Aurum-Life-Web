from datetime import datetime, timedelta
from typing import List, Dict, Optional
from database import find_documents
import logging
import os
from emergentintegrations.llm.chat import LlmChat

logger = logging.getLogger(__name__)

class AiCoachService:
    """AI Coach service with Gemini 2.0-flash for intelligent personal coaching"""
    
    @staticmethod
    def _initialize_gemini_coach(user_id: str) -> LlmChat:
        """Initialize Gemini AI coach with coaching context"""
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        system_message = """You are an expert personal growth coach integrated into Aurum Life, a comprehensive life management app. Your role is to provide intelligent, motivational, and actionable guidance to help users achieve their goals.

CONTEXT: You have access to the user's complete Aurum Life data:
- Pillars: Major life domains (health, career, relationships, etc.)
- Areas: Specific focus areas within pillars with importance levels (1-5)
- Projects: Goals and initiatives with importance levels (1-5) and deadlines
- Tasks: Individual actions with priorities, due dates, and completion status

IMPORTANCE LEVELS:
- 5 (Critical): Life-changing, fundamental goals
- 4 (High): Significant impact on major life areas  
- 3 (Medium): Important but not urgent
- 2 (Minor): Nice to have, low impact
- 1 (Low): Minimal importance

YOUR COACHING STYLE:
- Action-oriented: Always provide specific, actionable next steps
- Motivational but realistic: Encourage without being overly positive
- Context-aware: Connect daily tasks to bigger life goals
- Analytical: Use data patterns to provide insights
- Empathetic: Understand that personal growth is challenging

RESPONSE FORMAT:
- Keep responses concise (2-3 sentences max for daily priorities)
- Use encouraging language with occasional emojis
- Focus on immediate actionable steps
- Connect tasks to broader purpose when relevant

COACHING PRINCIPLES:
1. Important + Urgent = Critical focus
2. Important + Not Urgent = Strategic work  
3. Urgent + Not Important = Delegate/Quick wins
4. Neither = Eliminate or postpone

Remember: You're helping someone build their best life. Be their guide, motivator, and strategic thinking partner."""

        return LlmChat(
            api_key=api_key,
            session_id=f"coach-{user_id}",
            system_message=system_message
        ).with_model("gemini", "gemini-2.0-flash")
    
    @staticmethod
    async def get_todays_priorities(user_id: str, limit: int = 3) -> List[Dict]:
        """
        Get AI-powered priority recommendations using Gemini 2.0-flash with full user context
        """
        try:
            # Get comprehensive user data for AI context
            tasks = await find_documents(
                "tasks", 
                {
                    "user_id": user_id,
                    "completed": False,
                    "archived": {"$ne": True}
                }
            )
            
            if not tasks:
                return [{
                    'task_id': None,
                    'task_name': 'No active tasks',
                    'coaching_message': "🎉 You're all caught up! Perfect time to review your goals or start something new. What would you like to focus on today?",
                    'score': 0,
                    'reasons': []
                }]
            
            # Get supporting data for rich context
            projects = await find_documents("projects", {"user_id": user_id})
            areas = await find_documents("areas", {"user_id": user_id})
            pillars = await find_documents("pillars", {"user_id": user_id})
            
            # Create lookup dictionaries
            project_lookup = {p["id"]: p for p in projects}
            area_lookup = {a["id"]: a for a in areas}
            pillar_lookup = {p["id"]: p for p in pillars}
            
            # Calculate basic scores (same algorithm as before)
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
                
                # Scoring logic (same as before)
                if due_date and due_date < today:
                    score += 100
                    days_overdue = (today - due_date).days
                    reasons.append(f"Overdue by {days_overdue} day{'s' if days_overdue > 1 else ''}")
                elif due_date and due_date == today:
                    score += 80
                    reasons.append("Due today")
                
                if task.get('dependency_tasks') and task.get('can_start', True):
                    score += 60
                    reasons.append("Dependencies cleared")
                
                if task.get('status') == 'in_progress':
                    score += 40
                    reasons.append("In progress")
                
                # Priority and importance scoring
                priority_boost = {'high': 30, 'medium': 20, 'low': 10}.get(task.get('priority', 'medium'), 20)
                score += priority_boost
                
                # Add importance scoring from project/area
                project_id = task.get('project_id')
                project = project_lookup.get(project_id) if project_id else None
                area = area_lookup.get(project.get('area_id')) if project else None
                
                if project and project.get('importance'):
                    importance_score = {5: 50, 4: 35, 3: 20, 2: 10, 1: 5}.get(project['importance'], 20)
                    score += importance_score
                
                if area and area.get('importance'):
                    area_score = {5: 25, 4: 20, 3: 10, 2: 5, 1: 2}.get(area['importance'], 10)
                    score += area_score
                
                if score > 0:
                    scored_tasks.append({
                        'task': task,
                        'project': project,
                        'area': area,
                        'score': score,
                        'reasons': reasons
                    })
            
            # Sort by score and get top candidates
            scored_tasks.sort(key=lambda x: x['score'], reverse=True)
            top_tasks = scored_tasks[:limit]
            
            # Prepare comprehensive context for Gemini
            context_data = {
                'user_stats': {
                    'total_active_tasks': len(tasks),
                    'total_projects': len(projects),
                    'total_areas': len(areas),
                    'total_pillars': len(pillars)
                },
                'top_recommendations': []
            }
            
            for item in top_tasks:
                task = item['task']
                project = item.get('project')
                area = item.get('area')
                
                context_data['top_recommendations'].append({
                    'task_name': task['name'],
                    'task_description': task.get('description', ''),
                    'task_priority': task.get('priority', 'medium'),
                    'due_date': task.get('due_date'),
                    'score': item['score'],
                    'reasons': item['reasons'],
                    'project_name': project.get('name') if project else None,
                    'project_importance': project.get('importance') if project else None,
                    'area_name': area.get('name') if area else None,
                    'area_importance': area.get('importance') if area else None
                })
            
            # Get AI-powered coaching for each task
            gemini_coach = AiCoachService._initialize_gemini_coach(user_id)
            
            recommendations = []
            for i, item in enumerate(top_tasks):
                task = item['task']
                
                # Create specific coaching prompt for this task
                coaching_prompt = f"""
                Based on the user's Aurum Life data, provide a brief, motivational coaching message for this task:

                TASK: {task['name']}
                DESCRIPTION: {task.get('description', 'No description')}
                PRIORITY: {task.get('priority', 'medium')}
                SCORE: {item['score']} (higher = more urgent/important)
                REASONS: {', '.join(item['reasons'])}
                
                PROJECT: {item.get('project', {}).get('name', 'No project')} (Importance: {item.get('project', {}).get('importance', 'N/A')})
                AREA: {item.get('area', {}).get('name', 'No area')} (Importance: {item.get('area', {}).get('importance', 'N/A')})
                
                Provide a 1-2 sentence coaching message that:
                1. Acknowledges the urgency/importance
                2. Motivates action with specific reasoning
                3. Connects to bigger purpose if relevant
                4. Uses an encouraging, action-oriented tone
                
                Example: "🎯 This health goal is overdue but critical to your wellness pillar. Your past consistency shows you can do this - let's break it into a 15-minute session."
                """
                
                try:
                    # Get AI coaching response
                    ai_response = await gemini_coach.call_async(coaching_prompt)
                    coaching_message = ai_response.strip()
                except Exception as e:
                    logger.error(f"Error getting AI coaching for task {task['id']}: {str(e)}")
                    # Fallback to rule-based message
                    coaching_message = AiCoachService._build_fallback_message(item)
                
                recommendations.append({
                    'task_id': task['id'],
                    'task_name': task['name'],
                    'task_description': task.get('description', ''),
                    'project_name': item.get('project', {}).get('name', ''),
                    'due_date': task.get('due_date'),
                    'priority': task.get('priority', 'medium'),
                    'score': item['score'],
                    'coaching_message': coaching_message,
                    'reasons': item['reasons'],
                    'ai_powered': True
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting AI-powered priorities for user {user_id}: {str(e)}")
            return [{
                'task_id': None,
                'task_name': 'Error loading priorities',
                'coaching_message': "I'm having trouble analyzing your tasks right now. Please try refreshing or check back in a moment.",
                'score': 0,
                'reasons': [],
                'ai_powered': False
            }]
    
    @staticmethod
    def _build_fallback_message(scored_item: Dict) -> str:
        """Fallback coaching message when AI is unavailable"""
        task = scored_item['task']
        score = scored_item['score']
        reasons = scored_item['reasons']
        
        task_name = task.get('name', 'this task')
        
        if score >= 100:
            return f"⚡ {task_name} needs immediate attention - let's tackle this overdue item and get back on track!"
        elif score >= 80:
            return f"🎯 Perfect timing for {task_name}. Due today means maximum impact when completed!"
        elif score >= 60:
            return f"✅ {task_name} is ready for progress. Dependencies cleared - great time to move forward!"
        else:
            return f"📈 {task_name} is a solid choice for steady progress. Small steps create big wins!"