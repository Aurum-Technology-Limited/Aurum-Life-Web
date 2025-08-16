"""
AI Coach MVP Features Implementation
Implements the three core MVP features for the AI Coach system
"""

import uuid
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Any
import logging
from models import (
    DailyReflection, 
    DailyReflectionCreate, 
    DailyReflectionResponse,
    ProjectDecompositionRequest,
    ProjectDecompositionResponse,
    TaskWhyStatement,
    TaskWhyStatementResponse
)
from supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

class AiCoachMvpService:
    """Service class for AI Coach MVP features"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    # ================================
    # TODAY PRIORITIZATION (MVP)
    # ================================
    async def get_today_priorities(self, user_id: str, coaching_top_n: int = 3) -> Dict[str, Any]:
        """
        Compute rule-based priority scores for all active tasks and optionally add
        Gemini coaching for the top N (default 3). Returns list sorted by score desc
        with a transparent scoring breakdown per task.
        """
        from datetime import timezone
        from zoneinfo import ZoneInfo
        import os
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        supabase = self.supabase
        # 1) Get user timezone (optional)
        tz_name = "UTC"
        try:
            profile_resp = supabase.table('user_profiles').select('timezone, time_zone, tz').eq('id', user_id).execute()
            if profile_resp.data:
                row = profile_resp.data[0]
                tz_name = row.get('timezone') or row.get('time_zone') or row.get('tz') or 'UTC'
        except Exception:
            tz_name = "UTC"
        try:
            user_tz = ZoneInfo(tz_name)
        except Exception:
            user_tz = ZoneInfo('UTC')
        
        # 2) Fetch active, incomplete tasks
        tasks_resp = supabase.table('tasks').select(
            'id, name, description, status, priority, due_date, project_id, completed, dependency_task_ids'
        ).eq('user_id', user_id).eq('completed', False).execute()
        tasks = tasks_resp.data or []
        
        # Filter active statuses
        active_statuses = {'todo', 'in_progress', 'review'}
        tasks = [t for t in tasks if (t.get('status') in active_statuses or not t.get('status'))]
        if not tasks:
            return { 'date': datetime.now(user_tz).isoformat(), 'tasks': [] }
        
        # 3) Fetch related projects and areas
        project_ids = list({t.get('project_id') for t in tasks if t.get('project_id')})
        projects = {}
        if project_ids:
            proj_resp = supabase.table('projects').select('id, name, area_id, importance').in_('id', project_ids).execute()
            for p in (proj_resp.data or []):
                projects[p['id']] = p
        area_ids = list({p.get('area_id') for p in projects.values() if p.get('area_id')})
        areas = {}
        if area_ids:
            area_resp = supabase.table('areas').select('id, name, importance').in_('id', area_ids).execute()
            for a in (area_resp.data or []):
                areas[a['id']] = a
        
        # 4) Preload all dependency tasks
        dep_ids = []
        for t in tasks:
            arr = t.get('dependency_task_ids') or []
            if isinstance(arr, list):
                dep_ids.extend(arr)
        dep_lookup = {}
        if dep_ids:
            # Unique
            dep_ids = list({d for d in dep_ids if d})
            if dep_ids:
                deps_resp = supabase.table('tasks').select('id, completed').in_('id', dep_ids).execute()
                for d in (deps_resp.data or []):
                    dep_lookup[d['id']] = d
        
        # 5) Score tasks
        from math import fsum
        today_local = datetime.now(user_tz).date()
        scored = []
        for t in tasks:
            breakdown = {
                'urgency': 0,
                'priority': 0,
                'project_importance': 0,
                'area_importance': 0,
                'dependencies': 0,
                'total': 0,
                'reasons': []
            }
            # Urgency: overdue +100, due today +80
            due_date_val = None
            if t.get('due_date'):
                try:
                    # Parse and convert to user's tz
                    dts = datetime.fromisoformat(str(t['due_date']).replace('Z', '+00:00'))
                    if dts.tzinfo is None:
                        dts = dts.replace(tzinfo=ZoneInfo('UTC'))
                    due_local = dts.astimezone(user_tz).date()
                    due_date_val = due_local
                except Exception:
                    due_date_val = None
            if due_date_val and due_date_val < today_local:
                breakdown['urgency'] = 100
                delta = (today_local - due_date_val).days
                breakdown['reasons'].append(f"Overdue by {delta} day{'s' if delta != 1 else ''}")
            elif due_date_val and due_date_val == today_local:
                breakdown['urgency'] = 80
                breakdown['reasons'].append('Due today')
            
            # Priority: task.priority high = +30
            pr = (t.get('priority') or '').lower()
            if pr == 'high':
                breakdown['priority'] = 30
                breakdown['reasons'].append('Task priority: High')
            
            # Vertical alignment: project importance high (>=4) +50, area importance high (>=4) +25
            proj = projects.get(t.get('project_id')) if t.get('project_id') else None
            if proj and proj.get('importance') is not None:
                try:
                    imp = int(proj['importance'])
                    if imp >= 4:
                        breakdown['project_importance'] = 50
                        breakdown['reasons'].append('Project importance: High')
                except Exception:
                    pass
            ar = areas.get(proj.get('area_id')) if proj and proj.get('area_id') else None
            if ar and ar.get('importance') is not None:
                try:
                    aimp = int(ar['importance'])
                    if aimp >= 4:
                        breakdown['area_importance'] = 25
                        breakdown['reasons'].append('Area importance: High')
                except Exception:
                    pass
            
            # Dependencies met: +60 when all prereqs completed or none
            deps = t.get('dependency_task_ids') or []
            all_met = True
            if deps and isinstance(deps, list) and len(deps) > 0:
                for dep_id in deps:
                    dep = dep_lookup.get(dep_id)
                    if not dep or not dep.get('completed'):
                        all_met = False
                        break
            if all_met:
                breakdown['dependencies'] = 60
                breakdown['reasons'].append('Dependencies met')
            
            breakdown['total'] = sum([breakdown['urgency'], breakdown['priority'], breakdown['project_importance'], breakdown['area_importance'], breakdown['dependencies']])
            scored.append({
                'task': t,
                'project': proj,
                'area': ar,
                'score': breakdown['total'],
                'breakdown': breakdown
            })
        
        # 6) Sort descending
        scored.sort(key=lambda x: x['score'], reverse=True)
        
        # 7) Optional: Gemini 2.0-flash coaching for top N
        def init_llm():
            api_key = os.environ.get('GEMINI_API_KEY')
            if not api_key:
                return None
            return LlmChat(api_key=api_key, session_id=f"coach-{user_id}", system_message="You are the Aurum Life AI Coach. Be concise (1-2 sentences), motivational, and explicitly connect the task to its Project/Area/Pillar when available.").with_model("gemini", "gemini-2.0-flash")
        
        llm = init_llm()
        top = scored[:max(0, int(coaching_top_n))]
        if llm and top:
            for item in top:
                t = item['task']
                p = item.get('project') or {}
                a = item.get('area') or {}
                prompt = (
                    f"Task: '{t.get('name','')}'\n"
                    f"Project: '{p.get('name','') or 'None'}'\n"
                    f"Area: '{a.get('name','') or 'None'}'\n"
                    f"Pillar: ''\n"
                    f"Instruction: In 1-2 sentences, motivate the user by explaining why this task matters today and how it ties to the project/area pillar context."
                )
                try:
                    msg = UserMessage(text=prompt)
                    resp = await llm.send_message(msg)
                    item['coaching_message'] = (resp or '').strip()
                    item['ai_powered'] = True
                except Exception as e:
                    logger = logging.getLogger(__name__)
                    logger.error(f"Gemini coaching failed: {e}")
                    item['coaching_message'] = None
                    item['ai_powered'] = False
        
        # 8) Build API response list
        out = []
        for item in scored:
            t = item['task']
            p = item.get('project') or {}
            a = item.get('area') or {}
            out.append({
                'id': t['id'],
                'title': t.get('name'),
                'description': t.get('description'),
                'status': t.get('status'),
                'priority': t.get('priority'),
                'due_date': t.get('due_date'),
                'project_id': t.get('project_id'),
                'project_name': p.get('name'),
                'area_id': p.get('area_id') if p else None,
                'area_name': a.get('name') if a else None,
                'score': item['score'],
                'breakdown': item['breakdown'],
                'coaching_message': item.get('coaching_message'),
                'ai_powered': item.get('ai_powered', False)
            })
        
        # Respect requested top-N limit for response size as well
        try:
            limit_n = max(0, int(coaching_top_n))
        except Exception:
            limit_n = 3
        if limit_n > 0:
            out = out[:limit_n]
        
        return { 'date': datetime.now(user_tz).isoformat(), 'tasks': out }
    
    # Feature 1: Contextual "Why" Statements
    async def generate_task_why_statements(self, user_id: str, task_ids: List[str] = None) -> TaskWhyStatementResponse:
        """
        Generate contextual why statements for tasks explaining their vertical alignment
        
        Args:
            user_id: User identifier
            task_ids: Optional list of specific task IDs, if None gets today's tasks
        
        Returns:
            TaskWhyStatementResponse with why statements for each task
        """
        try:
            supabase = self.supabase
            
            # If no specific task IDs provided, get today's tasks or recent incomplete tasks
            if not task_ids:
                # Get recent incomplete tasks (limit to 10 for performance)
                tasks_query = supabase.table('tasks').select(
                    'id, name, project_id, completed, due_date, priority'
                ).eq('user_id', user_id).eq('completed', False).limit(10)
                
                tasks_response = tasks_query.execute()
                tasks = tasks_response.data or []
            else:
                # Get specific tasks
                tasks_response = supabase.table('tasks').select(
                    'id, name, project_id, completed, due_date, priority'
                ).eq('user_id', user_id).in_('id', task_ids).execute()
                
                tasks = tasks_response.data or []
            
            if not tasks:
                return TaskWhyStatementResponse(tasks_with_why=[])
            
            # Get all projects for these tasks in one query
            project_ids = list(set([task['project_id'] for task in tasks if task.get('project_id')]))
            if not project_ids:
                return TaskWhyStatementResponse(tasks_with_why=[])
            
            projects_response = supabase.table('projects').select(
                'id, name, area_id, importance'
            ).in_('id', project_ids).execute()
            
            projects = {proj['id']: proj for proj in (projects_response.data or [])}
            
            # Get all areas for these projects in one query
            area_ids = list(set([proj['area_id'] for proj in projects.values() if proj.get('area_id')]))
            if not area_ids:
                return TaskWhyStatementResponse(tasks_with_why=[])
            
            areas_response = supabase.table('areas').select(
                'id, name, pillar_id, importance'
            ).in_('id', area_ids).execute()
            
            areas = {area['id']: area for area in (areas_response.data or [])}
            
            # Get all pillars for these areas in one query
            pillar_ids = list(set([area['pillar_id'] for area in areas.values() if area.get('pillar_id')]))
            pillars = {}
            if pillar_ids:
                pillars_response = supabase.table('pillars').select(
                    'id, name, description'
                ).in_('id', pillar_ids).execute()
                
                pillars = {pillar['id']: pillar for pillar in (pillars_response.data or [])}
            
            # Generate why statements for each task
            tasks_with_why = []
            for task in tasks:
                try:
                    project = projects.get(task['project_id'])
                    if not project:
                        continue
                    
                    area = areas.get(project['area_id']) if project.get('area_id') else None
                    pillar = pillars.get(area['pillar_id']) if area and area.get('pillar_id') else None
                    
                    # Generate the contextual why statement
                    why_statement = self._generate_why_statement(
                        task_name=task['name'],
                        project_name=project['name'],
                        area_name=area['name'] if area else None,
                        pillar_name=pillar['name'] if pillar else None,
                        task_priority=task.get('priority', 'medium'),
                        project_importance=project.get('importance', 3),
                        area_importance=area.get('importance', 3) if area else 3
                    )
                    
                    tasks_with_why.append(TaskWhyStatement(
                        task_id=task['id'],
                        task_name=task['name'],
                        why_statement=why_statement,
                        project_connection=project['name'],
                        pillar_connection=pillar['name'] if pillar else None,
                        area_connection=area['name'] if area else None
                    ))
                    
                except Exception as e:
                    logger.error(f"Error generating why statement for task {task['id']}: {e}")
                    continue
            
            logger.info(f"✅ Generated {len(tasks_with_why)} why statements for user: {user_id}")
            return TaskWhyStatementResponse(
                why_statements=tasks_with_why,
                tasks_analyzed=len(tasks),
                vertical_alignment={
                    'total_tasks_analyzed': len(tasks),
                    'successful_statements': len(tasks_with_why),
                    'hierarchy_depth': 'task -> project -> area -> pillar'
                }
            )
            
        except Exception as e:
            logger.error(f"Error generating task why statements: {e}")
            return TaskWhyStatementResponse(
                why_statements=[],
                tasks_analyzed=0,
                vertical_alignment={}
            )
    
    def _generate_why_statement(
        self, 
        task_name: str, 
        project_name: str, 
        area_name: Optional[str], 
        pillar_name: Optional[str],
        task_priority: str,
        project_importance: int,
        area_importance: int
    ) -> str:
        """Generate a contextual why statement for a task"""
        
        # Determine priority adjective
        priority_map = {
            'high': 'high priority',
            'medium': 'priority',
            'low': 'helpful'
        }
        
        priority_text = priority_map.get(task_priority, 'priority')
        
        # Build the why statement with vertical alignment
        if pillar_name and area_name:
            if project_importance >= 4 or area_importance >= 4:
                return f"This task is {priority_text} because it advances '{project_name}', a critical project in your '{area_name}' area under your '{pillar_name}' pillar."
            else:
                return f"This task supports '{project_name}' in your '{area_name}' area, contributing to your '{pillar_name}' pillar."
        elif area_name:
            return f"This task is {priority_text} for your '{project_name}' project in the '{area_name}' area."
        else:
            return f"This task is part of your '{project_name}' project and helps you make concrete progress."
    
    # Feature 2: Lean Goal Decomposition Assistance
    async def suggest_project_tasks(self, user_id: str, request: ProjectDecompositionRequest) -> ProjectDecompositionResponse:
        """
        Suggest placeholder tasks for a new project to help with the blank slate problem
        
        Args:
            user_id: User identifier
            request: Project decomposition request with project details
        
        Returns:
            ProjectDecompositionResponse with suggested tasks
        """
        try:
            # Get template tasks based on project type/category
            template_tasks = self._get_project_template_tasks(
                request.template_type,
                request.project_name,
                request.project_description
            )
            
            logger.info(f"✅ Generated {len(template_tasks)} task suggestions for project: {request.project_name}")
            
            return ProjectDecompositionResponse(
                project_name=request.project_name,
                template_type=request.template_type,
                suggested_tasks=template_tasks,
                total_tasks=len(template_tasks)
            )
            
        except Exception as e:
            logger.error(f"Error generating project task suggestions: {e}")
            return ProjectDecompositionResponse(
                project_name=request.project_name,
                template_type=request.template_type,
                suggested_tasks=[],
                total_tasks=0
            )
    
    def _get_project_template_tasks(self, template_type: str, project_name: str, project_description: Optional[str]) -> List[Dict[str, Any]]:
        """Get template tasks based on project type"""
        
        # Base templates for different project types
        templates = {
            "learning": [
                {"name": "Research learning resources and materials", "priority": "high", "estimated_duration": 60},
                {"name": "Create a structured study schedule", "priority": "high", "estimated_duration": 30},
                {"name": "Complete first learning module or chapter", "priority": "medium", "estimated_duration": 120},
                {"name": "Set up progress tracking system", "priority": "medium", "estimated_duration": 15},
                {"name": "Schedule regular review sessions", "priority": "low", "estimated_duration": 20}
            ],
            "health": [
                {"name": "Research and define specific health goals", "priority": "high", "estimated_duration": 45},
                {"name": "Create a baseline measurement or assessment", "priority": "high", "estimated_duration": 30},
                {"name": "Develop a daily/weekly routine", "priority": "high", "estimated_duration": 60},
                {"name": "Set up tracking tools or apps", "priority": "medium", "estimated_duration": 20},
                {"name": "Schedule regular progress check-ins", "priority": "medium", "estimated_duration": 15}
            ],
            "career": [
                {"name": "Define specific career objectives and outcomes", "priority": "high", "estimated_duration": 90},
                {"name": "Research requirements and necessary skills", "priority": "high", "estimated_duration": 120},
                {"name": "Create action plan with key milestones", "priority": "high", "estimated_duration": 60},
                {"name": "Identify networking opportunities", "priority": "medium", "estimated_duration": 45},
                {"name": "Set up progress tracking and review schedule", "priority": "medium", "estimated_duration": 30}
            ],
            "personal": [
                {"name": "Clarify the specific outcome you want", "priority": "high", "estimated_duration": 45},
                {"name": "Break down into smaller manageable steps", "priority": "high", "estimated_duration": 60},
                {"name": "Set realistic timeline and deadlines", "priority": "high", "estimated_duration": 30},
                {"name": "Identify potential obstacles and solutions", "priority": "medium", "estimated_duration": 45},
                {"name": "Create accountability system", "priority": "medium", "estimated_duration": 20}
            ],
            "work": [
                {"name": "Define project requirements and scope", "priority": "high", "estimated_duration": 90},
                {"name": "Create detailed project timeline", "priority": "high", "estimated_duration": 60},
                {"name": "Identify key stakeholders and communication plan", "priority": "high", "estimated_duration": 45},
                {"name": "Set up project tracking and status reporting", "priority": "medium", "estimated_duration": 30},
                {"name": "Plan regular milestone reviews", "priority": "medium", "estimated_duration": 20}
            ],
            "general": [
                {"name": "Research and gather necessary information", "priority": "high", "estimated_duration": 60},
                {"name": "Create a detailed action plan", "priority": "high", "estimated_duration": 45},
                {"name": "Set clear milestones and deadlines", "priority": "medium", "estimated_duration": 30},
                {"name": "Identify required resources and tools", "priority": "medium", "estimated_duration": 30},
                {"name": "Set up progress tracking system", "priority": "low", "estimated_duration": 15}
            ]
        }
        
        # Get template tasks, defaulting to general if type not found
        template_tasks = templates.get(template_type.lower(), templates["general"])
        
        # Customize first task with project name if possible
        customized_tasks = []
        for i, task in enumerate(template_tasks):
            task_copy = task.copy()
            if i == 0 and project_name:
                # Customize the first task to be more specific
                if "research" in task_copy["name"].lower():
                    task_copy["name"] = f"Research everything needed for '{project_name}'"
                elif "define" in task_copy["name"].lower():
                    task_copy["name"] = f"Define specific goals and outcomes for '{project_name}'"
            customized_tasks.append(task_copy)
        
        # Limit to 5 tasks max
        return customized_tasks[:5]
    
    async def create_tasks_from_suggestions(self, user_id: str, project_id: str, suggested_tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create actual tasks from suggested tasks
        
        Args:
            user_id: User identifier
            project_id: Project to add tasks to
            suggested_tasks: List of suggested task dictionaries
        
        Returns:
            List of created task dictionaries
        """
        try:
            supabase = self.supabase
            created_tasks = []
            
            for i, task_suggestion in enumerate(suggested_tasks):
                task_dict = {
                    'id': str(uuid.uuid4()),
                    'user_id': user_id,
                    'project_id': project_id,
                    'name': task_suggestion['name'],
                    'description': '',
                    'status': 'todo',
                    'priority': task_suggestion.get('priority', 'medium'),
                    'completed': False,
                    'sort_order': i,
                    'estimated_duration': task_suggestion.get('estimated_duration'),
                    'created_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat(),
                    'date_created': datetime.utcnow().isoformat()
                }
                
                response = supabase.table('tasks').insert(task_dict).execute()
                
                if response.data:
                    created_tasks.append(response.data[0])
            
            logger.info(f"✅ Created {len(created_tasks)} tasks from suggestions for project: {project_id}")
            return created_tasks
            
        except Exception as e:
            logger.error(f"Error creating tasks from suggestions: {e}")
            return []
    
    # Feature 3: Daily Reflection & Progress Prompt
    async def create_daily_reflection(self, user_id: str, reflection_data: DailyReflectionCreate) -> DailyReflectionResponse:
        """
        Create a daily reflection entry
        
        Args:
            user_id: User identifier
            reflection_data: Reflection data to store
        
        Returns:
            Created daily reflection response
        """
        try:
            supabase = self.supabase
            
            # Use provided date or default to today
            reflection_date = reflection_data.reflection_date or datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Check if reflection already exists for this date
            existing_response = supabase.table('daily_reflections').select('id').eq(
                'user_id', user_id
            ).eq('date', reflection_date.date().isoformat()).execute()
            
            if existing_response.data:
                # Update existing reflection
                update_dict = {
                    'reflection_text': reflection_data.reflection_text,
                    'completion_score': reflection_data.completion_score,
                    'mood': reflection_data.mood,
                    'biggest_accomplishment': reflection_data.biggest_accomplishment,
                    'challenges_faced': reflection_data.challenges_faced,
                    'tomorrow_focus': reflection_data.tomorrow_focus,
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                response = supabase.table('daily_reflections').update(update_dict).eq(
                    'id', existing_response.data[0]['id']
                ).execute()
                
                reflection_dict = response.data[0] if response.data else None
                logger.info(f"✅ Updated daily reflection for user: {user_id} on date: {reflection_date.date()}")
            else:
                # Create new reflection
                reflection_dict = {
                    'id': str(uuid.uuid4()),
                    'user_id': user_id,
                    'date': reflection_date.date().isoformat(),
                    'reflection_text': reflection_data.reflection_text,
                    'completion_score': reflection_data.completion_score,
                    'mood': reflection_data.mood,
                    'biggest_accomplishment': reflection_data.biggest_accomplishment,
                    'challenges_faced': reflection_data.challenges_faced,
                    'tomorrow_focus': reflection_data.tomorrow_focus,
                    'created_at': datetime.utcnow().isoformat()
                }
                
                response = supabase.table('daily_reflections').insert(reflection_dict).execute()
                reflection_dict = response.data[0] if response.data else None
                logger.info(f"✅ Created daily reflection for user: {user_id} on date: {reflection_date.date()}")
            
            if not reflection_dict:
                raise Exception("Failed to create/update daily reflection")
            
            # Update user's daily streak
            await self._update_daily_streak(user_id, reflection_date.date())
            
            return DailyReflectionResponse(
                id=reflection_dict['id'],
                user_id=reflection_dict['user_id'],
                reflection_date=reflection_date,
                reflection_text=reflection_dict['reflection_text'],
                completion_score=reflection_dict.get('completion_score'),
                mood=reflection_dict.get('mood'),
                biggest_accomplishment=reflection_dict.get('biggest_accomplishment'),
                challenges_faced=reflection_dict.get('challenges_faced'),
                tomorrow_focus=reflection_dict.get('tomorrow_focus'),
                created_at=datetime.fromisoformat(reflection_dict['created_at'])
            )
            
        except Exception as e:
            logger.error(f"Error creating daily reflection: {e}")
            raise
    
    async def get_user_reflections(self, user_id: str, days: int = 30) -> List[DailyReflectionResponse]:
        """Get user's recent daily reflections"""
        try:
            supabase = self.supabase
            
            # Get reflections from the last N days
            since_date = (datetime.utcnow() - timedelta(days=days)).date()
            
            response = supabase.table('daily_reflections').select('*').eq(
                'user_id', user_id
            ).gte('date', since_date.isoformat()).order('date', desc=True).execute()
            
            reflections = []
            for reflection_dict in (response.data or []):
                reflections.append(DailyReflectionResponse(
                    id=reflection_dict['id'],
                    user_id=reflection_dict['user_id'],
                    reflection_date=datetime.fromisoformat(reflection_dict['date']),
                    reflection_text=reflection_dict['reflection_text'],
                    completion_score=reflection_dict.get('completion_score'),
                    mood=reflection_dict.get('mood'),
                    biggest_accomplishment=reflection_dict.get('biggest_accomplishment'),
                    challenges_faced=reflection_dict.get('challenges_faced'),
                    tomorrow_focus=reflection_dict.get('tomorrow_focus'),
                    created_at=datetime.fromisoformat(reflection_dict['created_at'])
                ))
            
            logger.info(f"✅ Retrieved {len(reflections)} reflections for user: {user_id}")
            return reflections
            
        except Exception as e:
            logger.error(f"Error getting user reflections: {e}")
            return []
    
    async def get_user_streak(self, user_id: str) -> int:
        """Get user's current daily streak"""
        try:
            supabase = self.supabase
            
            # Get user profile with streak info
            response = supabase.table('user_profiles').select('current_streak').eq('id', user_id).execute()
            
            if response.data:
                return response.data[0].get('current_streak', 0)
            return 0
            
        except Exception as e:
            logger.error(f"Error getting user streak: {e}")
            return 0
    
    async def _update_daily_streak(self, user_id: str, reflection_date: date) -> None:
        """Update user's daily streak based on reflection activity"""
        try:
            supabase = self.supabase
            
            # Get current streak
            current_streak = await self.get_user_streak(user_id)
            
            # Check if there was a reflection yesterday
            yesterday = reflection_date - timedelta(days=1)
            yesterday_reflection = supabase.table('daily_reflections').select('id').eq(
                'user_id', user_id
            ).eq('date', yesterday.isoformat()).execute()
            
            if yesterday_reflection.data or current_streak == 0:
                # Continue or start streak
                new_streak = current_streak + 1
            else:
                # Reset streak if there's a gap
                new_streak = 1
            
            # Update user profile with new streak
            supabase.table('user_profiles').update({
                'current_streak': new_streak,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', user_id).execute()
            
            logger.info(f"✅ Updated daily streak for user {user_id}: {new_streak} days")
            
        except Exception as e:
            logger.error(f"Error updating daily streak: {e}")
    
    async def should_show_daily_prompt(self, user_id: str) -> bool:
        """Check if daily prompt should be shown to user"""
        try:
            supabase = self.supabase
            
            # Check if user has already completed reflection today
            today = datetime.utcnow().date()
            response = supabase.table('daily_reflections').select('id').eq(
                'user_id', user_id
            ).eq('date', today.isoformat()).execute()
            
            # Show prompt if no reflection today
            return not bool(response.data)
            
        except Exception as e:
            logger.error(f"Error checking daily prompt status: {e}")
            return True  # Default to showing prompt if there's an error