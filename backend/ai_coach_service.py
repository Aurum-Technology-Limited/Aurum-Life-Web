from datetime import datetime, timedelta
from typing import List, Dict, Optional
from database import find_documents
import logging
import os
from emergentintegrations.llm.chat import LlmChat, UserMessage

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
                    # Convert importance to int to handle string values
                    try:
                        project_importance = int(project['importance'])
                        importance_score = {5: 50, 4: 35, 3: 20, 2: 10, 1: 5}.get(project_importance, 20)
                        score += importance_score
                    except (ValueError, TypeError):
                        pass
                
                if area and area.get('importance'):
                    # Convert importance to int to handle string values
                    try:
                        area_importance = int(area['importance'])
                        area_score = {5: 25, 4: 20, 3: 10, 2: 5, 1: 2}.get(area_importance, 10)
                        score += area_score
                    except (ValueError, TypeError):
                        pass
                
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
                    message = UserMessage(text=coaching_prompt)
                    ai_response = await gemini_coach.send_message(message)
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
    async def chat_with_coach(user_id: str, user_message: str) -> str:
        """
        Interactive chat with AI coach about user's data and insights with FULL CONTEXT INJECTION
        """
        try:
            # PHASE 1: FETCH ALL USER DATA FOR CONTEXT
            logger.info(f"Fetching comprehensive user data for context injection - User: {user_id}")
            
            tasks = await find_documents("tasks", {"user_id": user_id})
            projects = await find_documents("projects", {"user_id": user_id})
            areas = await find_documents("areas", {"user_id": user_id})
            pillars = await find_documents("pillars", {"user_id": user_id})
            
            # PHASE 2: CONSTRUCT DETAILED CONTEXT BLOCK
            context_block = AiCoachService._build_user_context_block(
                pillars, areas, projects, tasks
            )
            
            # PHASE 3: CONSTRUCT COMPLETE PROMPT WITH CONTEXT
            system_message = """You are the Aurum Life AI Coach. Your role is to act as a personal growth companion. Analyze the provided user context to answer the user's question with actionable, personalized, and motivational advice. 

IMPORTANT: Use ONLY the data provided in the user context. Reference specific names of pillars, areas, projects, and tasks from their actual data. Be encouraging but realistic, and always provide actionable next steps."""

            final_prompt = f"""{system_message}

{context_block}

USER QUESTION: {user_message}

Provide a personalized, actionable response based on their actual data above."""

            # PHASE 4: MAKE API CALL WITH FULL CONTEXT
            logger.info(f"Sending context-aware prompt to Gemini API - User: {user_id}")
            gemini_coach = AiCoachService._initialize_gemini_coach(user_id)
            
            message = UserMessage(text=final_prompt)
            ai_response = await gemini_coach.send_message(message)
            
            logger.info(f"Received AI response - User: {user_id}, Response length: {len(ai_response)}")
            return ai_response.strip()
            
        except Exception as e:
            logger.error(f"Error in context-aware AI coach chat for user {user_id}: {str(e)}")
            return "I'm having trouble accessing your data right now. Please try asking again in a moment, and I'll provide personalized insights based on your goals and progress!"
    
    @staticmethod
    def _build_user_context_block(pillars: list, areas: list, projects: list, tasks: list) -> str:
        """
        Build a comprehensive, structured context block with user's actual data
        """
        # Helper function to safely get importance as integer
        def get_importance_int(item, default=3):
            try:
                return int(item.get('importance', default))
            except (ValueError, TypeError):
                return default
        
        def importance_label(level):
            labels = {5: "Critical", 4: "High", 3: "Medium", 2: "Low", 1: "Very Low"}
            return labels.get(level, "Medium")
        
        # Build context block
        context = "--- USER CONTEXT START ---\n\n"
        context += "Here is a snapshot of the user's current Aurum Life data. Use this information exclusively to answer their question.\n\n"
        
        # PILLARS SECTION
        context += "## PILLARS\n"
        if pillars:
            for pillar in pillars:
                importance = get_importance_int(pillar)
                context += f"- Pillar: \"{pillar.get('name', 'Unnamed')}\" (Importance: {importance} - {importance_label(importance)})\n"
                if pillar.get('description'):
                    context += f"  Description: {pillar['description']}\n"
        else:
            context += "- No pillars defined yet\n"
        context += "\n"
        
        # AREAS SECTION
        context += "## AREAS\n"
        if areas:
            for area in areas:
                importance = get_importance_int(area)
                pillar_name = "Unknown Pillar"
                
                # Find the pillar this area belongs to
                if area.get('pillar_id'):
                    for pillar in pillars:
                        if pillar.get('id') == area['pillar_id']:
                            pillar_name = pillar.get('name', 'Unknown Pillar')
                            break
                
                context += f"- Area: \"{area.get('name', 'Unnamed')}\" (in Pillar: {pillar_name}, Importance: {importance} - {importance_label(importance)})\n"
                if area.get('description'):
                    context += f"  Description: {area['description']}\n"
        else:
            context += "- No areas defined yet\n"
        context += "\n"
        
        # PROJECTS SECTION
        context += "## PROJECTS\n"
        active_projects = [p for p in projects if not p.get('archived')]
        if active_projects:
            for project in active_projects:
                importance = get_importance_int(project)
                area_name = "Unknown Area"
                status = project.get('status', 'not_started').replace('_', ' ').title()
                
                # Find the area this project belongs to
                if project.get('area_id'):
                    for area in areas:
                        if area.get('id') == project['area_id']:
                            area_name = area.get('name', 'Unknown Area')
                            break
                
                context += f"- Project: \"{project.get('name', 'Unnamed')}\" (in Area: {area_name}, Status: {status}, Importance: {importance} - {importance_label(importance)})\n"
                if project.get('description'):
                    context += f"  Description: {project['description']}\n"
                if project.get('deadline'):
                    try:
                        deadline = datetime.fromisoformat(project['deadline'].replace('Z', '+00:00')).strftime('%Y-%m-%d')
                        context += f"  Deadline: {deadline}\n"
                    except:
                        pass
        else:
            context += "- No active projects yet\n"
        context += "\n"
        
        # ACTIVE TASKS SECTION
        context += "## ACTIVE TASKS\n"
        active_tasks = [t for t in tasks if not t.get('completed') and not t.get('archived')]
        if active_tasks:
            today = datetime.utcnow().date()
            
            for task in active_tasks[:10]:  # Limit to 10 most relevant tasks
                project_name = "No Project"
                due_info = ""
                
                # Find the project this task belongs to
                if task.get('project_id'):
                    for project in projects:
                        if project.get('id') == task['project_id']:
                            project_name = project.get('name', 'Unknown Project')
                            break
                
                # Format due date information
                if task.get('due_date'):
                    try:
                        due_date = datetime.fromisoformat(task['due_date'].replace('Z', '+00:00')).date()
                        if due_date < today:
                            days_overdue = (today - due_date).days
                            due_info = f" (OVERDUE by {days_overdue} day{'s' if days_overdue > 1 else ''})"
                        elif due_date == today:
                            due_info = " (Due: TODAY)"
                        else:
                            due_info = f" (Due: {due_date.strftime('%Y-%m-%d')})"
                    except:
                        pass
                
                priority = task.get('priority', 'medium').title()
                status = task.get('status', 'todo').replace('_', ' ').title()
                
                context += f"- Task: \"{task.get('name', 'Unnamed')}\" (in Project: {project_name}, Priority: {priority}, Status: {status}{due_info})\n"
                if task.get('description'):
                    context += f"  Description: {task['description']}\n"
        else:
            context += "- No active tasks yet\n"
        
        context += "\n--- USER CONTEXT END ---\n\n"
        
        return context
    
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