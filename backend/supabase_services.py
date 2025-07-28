"""
Supabase-only CRUD Services
Clean implementation without MongoDB dependencies
"""

import os
import uuid
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from supabase import create_client, Client
from models import *
import bcrypt
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase_url = os.environ.get('SUPABASE_URL')
supabase_anon_key = os.environ.get('SUPABASE_ANON_KEY')

if not supabase_url or not supabase_anon_key:
    raise ValueError(f"Missing Supabase configuration: URL={bool(supabase_url)}, KEY={bool(supabase_anon_key)}")

supabase: Client = create_client(supabase_url, supabase_anon_key)


class SupabaseUserService:
    """User management with Supabase Auth"""
    
    @staticmethod
    async def get_user_profile(user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile from user_profiles table"""
        try:
            response = supabase.table('user_profiles').select('*').eq('id', user_id).single().execute()
            return response.data
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return None
    
    @staticmethod
    async def create_user_profile(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create user profile in user_profiles table"""
        try:
            response = supabase.table('user_profiles').insert(user_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating user profile: {e}")
            raise


class SupabasePillarService:
    """Pillar CRUD operations with Supabase"""
    
    @staticmethod
    async def create_pillar(user_id: str, pillar_data: PillarCreate) -> Dict[str, Any]:
        """Create a new pillar"""
        try:
            pillar_dict = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'name': pillar_data.name,
                'description': pillar_data.description or '',
                'color': pillar_data.color or '#3B82F6',
                'icon': pillar_data.icon or 'Target',
                'time_allocation_percentage': pillar_data.time_allocation or 0,  # Map to existing column
                'archived': False,  # Map is_active to archived (inverted)
                'sort_order': 0,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'date_created': datetime.utcnow().isoformat()
            }
            
            response = supabase.table('pillars').insert(pillar_dict).execute()
            
            if not response.data:
                raise Exception("Failed to create pillar")
                
            logger.info(f"✅ Created pillar: {pillar_data.name} for user: {user_id}")
            return response.data[0]
            
        except Exception as e:
            logger.error(f"Error creating pillar: {e}")
            raise
    
    @staticmethod
    async def get_user_pillars(user_id: str, include_areas: bool = False, include_archived: bool = False) -> List[Dict[str, Any]]:
        """Get user's pillars"""
        try:
            query = supabase.table('pillars').select('*').eq('user_id', user_id)
            
            if not include_archived:
                query = query.eq('archived', False)  # Use archived instead of is_active
                
            response = query.execute()
            pillars = response.data or []
            
            # Transform data to match expected format
            for pillar in pillars:
                pillar['is_active'] = not pillar.get('archived', False)  # Transform archived to is_active
                pillar['time_allocation'] = pillar.get('time_allocation_percentage', 0)  # Map field name
            
            # If include_areas is True, fetch areas for each pillar
            if include_areas and pillars:
                for pillar in pillars:
                    areas_response = supabase.table('areas').select('*').eq('pillar_id', pillar['id']).execute()
                    pillar['areas'] = areas_response.data or []
            
            logger.info(f"✅ Retrieved {len(pillars)} pillars for user: {user_id}")
            return pillars
            
        except Exception as e:
            logger.error(f"Error getting pillars: {e}")
            return []
    
    @staticmethod
    async def update_pillar(pillar_id: str, user_id: str, pillar_data: PillarUpdate) -> Dict[str, Any]:
        """Update a pillar"""
        try:
            update_dict = {
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Only include fields that are provided
            if pillar_data.name is not None:
                update_dict['name'] = pillar_data.name
            if pillar_data.description is not None:
                update_dict['description'] = pillar_data.description
            if pillar_data.color is not None:
                update_dict['color'] = pillar_data.color
            if pillar_data.icon is not None:
                update_dict['icon'] = pillar_data.icon
            if pillar_data.time_allocation is not None:
                update_dict['time_allocation'] = pillar_data.time_allocation
            if pillar_data.is_active is not None:
                update_dict['is_active'] = pillar_data.is_active
                
            response = supabase.table('pillars').update(update_dict).eq('id', pillar_id).eq('user_id', user_id).execute()
            
            if not response.data:
                raise Exception("Pillar not found or no changes made")
                
            logger.info(f"✅ Updated pillar: {pillar_id} for user: {user_id}")
            return response.data[0]
            
        except Exception as e:
            logger.error(f"Error updating pillar: {e}")
            raise
    
    @staticmethod
    async def delete_pillar(pillar_id: str, user_id: str) -> bool:
        """Delete a pillar and unlink its areas"""
        try:
            # First, unlink areas from this pillar
            areas_response = supabase.table('areas').update({
                'pillar_id': None,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('pillar_id', pillar_id).execute()
            
            # Then delete the pillar
            response = supabase.table('pillars').delete().eq('id', pillar_id).eq('user_id', user_id).execute()
            
            logger.info(f"✅ Deleted pillar: {pillar_id} and unlinked {len(areas_response.data or [])} areas")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting pillar: {e}")
            return False


class SupabaseAreaService:
    """Area CRUD operations with Supabase"""
    
    @staticmethod
    async def create_area(user_id: str, area_data: AreaCreate) -> Dict[str, Any]:
        """Create a new area"""
        try:
            area_dict = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'pillar_id': area_data.pillar_id,
                'name': area_data.name,
                'description': area_data.description or '',
                'color': area_data.color or '#10B981',
                'icon': area_data.icon or 'Circle',
                'importance': area_data.importance or 'medium',
                'archived': False,  # Map is_active to archived (inverted)
                'sort_order': 0,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'date_created': datetime.utcnow().isoformat()
            }
            
            response = supabase.table('areas').insert(area_dict).execute()
            
            if not response.data:
                raise Exception("Failed to create area")
                
            logger.info(f"✅ Created area: {area_data.name} for user: {user_id}")
            return response.data[0]
            
        except Exception as e:
            logger.error(f"Error creating area: {e}")
            raise
    
    @staticmethod
    async def get_user_areas(user_id: str, include_projects: bool = False, include_archived: bool = False) -> List[Dict[str, Any]]:
        """Get user's areas"""
        try:
            query = supabase.table('areas').select('*').eq('user_id', user_id)
            
            if not include_archived:
                query = query.eq('archived', False)  # Use archived instead of is_active
                
            response = query.execute()
            areas = response.data or []
            
            # Transform data to match expected format
            for area in areas:
                area['is_active'] = not area.get('archived', False)  # Transform archived to is_active
            
            # If include_projects is True, fetch projects for each area
            if include_projects and areas:
                for area in areas:
                    projects_response = supabase.table('projects').select('*').eq('area_id', area['id']).execute()
                    area['projects'] = projects_response.data or []
                    
                    # Get pillar name if pillar_id exists
                    if area.get('pillar_id'):
                        pillar_response = supabase.table('pillars').select('name').eq('id', area['pillar_id']).single().execute()
                        area['pillar_name'] = pillar_response.data.get('name') if pillar_response.data else None
            
            logger.info(f"✅ Retrieved {len(areas)} areas for user: {user_id}")
            return areas
            
        except Exception as e:
            logger.error(f"Error getting areas: {e}")
            return []
    
    @staticmethod
    async def update_area(area_id: str, user_id: str, area_data: AreaUpdate) -> Dict[str, Any]:
        """Update an area"""
        try:
            update_dict = {
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Only include fields that are provided
            if area_data.name is not None:
                update_dict['name'] = area_data.name
            if area_data.description is not None:
                update_dict['description'] = area_data.description
            if area_data.pillar_id is not None:
                update_dict['pillar_id'] = area_data.pillar_id
            if area_data.color is not None:
                update_dict['color'] = area_data.color
            if area_data.icon is not None:
                update_dict['icon'] = area_data.icon
            if area_data.importance is not None:
                update_dict['importance'] = area_data.importance
            if area_data.is_active is not None:
                update_dict['is_active'] = area_data.is_active
                
            response = supabase.table('areas').update(update_dict).eq('id', area_id).eq('user_id', user_id).execute()
            
            if not response.data:
                raise Exception("Area not found or no changes made")
                
            logger.info(f"✅ Updated area: {area_id} for user: {user_id}")
            return response.data[0]
            
        except Exception as e:
            logger.error(f"Error updating area: {e}")
            raise
    
    @staticmethod
    async def delete_area(area_id: str, user_id: str) -> bool:
        """Delete an area and unlink its projects"""
        try:
            # First, unlink projects from this area
            projects_response = supabase.table('projects').update({
                'area_id': None,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('area_id', area_id).execute()
            
            # Then delete the area
            response = supabase.table('areas').delete().eq('id', area_id).eq('user_id', user_id).execute()
            
            logger.info(f"✅ Deleted area: {area_id} and unlinked {len(projects_response.data or [])} projects")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting area: {e}")
            return False


class SupabaseProjectService:
    """Project CRUD operations with Supabase"""
    
    @staticmethod
    async def create_project(user_id: str, project_data: ProjectCreate) -> Dict[str, Any]:
        """Create a new project"""
        try:
            # Map backend status to database status
            status_mapping = {
                'not_started': 'Not Started',
                'in_progress': 'In Progress', 
                'completed': 'Completed',
                'on_hold': 'On Hold'
            }
            
            priority_mapping = {
                'low': 'Low',
                'medium': 'Medium',
                'high': 'High'
            }
            
            project_dict = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'area_id': project_data.area_id,
                'name': project_data.name,
                'description': project_data.description or '',
                'status': status_mapping.get(project_data.status or 'not_started', 'Not Started'),
                'priority': priority_mapping.get(project_data.priority or 'medium', 'Medium'),
                'color': project_data.color or '#F59E0B',
                'icon': project_data.icon or 'FolderOpen',
                'deadline': project_data.due_date.isoformat() if project_data.due_date else None,
                'archived': False,  # Map is_active to archived (inverted)
                'sort_order': 0,
                'completion_percentage': 0,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'date_created': datetime.utcnow().isoformat()
            }
            
            response = supabase.table('projects').insert(project_dict).execute()
            
            if not response.data:
                raise Exception("Failed to create project")
                
            logger.info(f"✅ Created project: {project_data.name} for user: {user_id}")
            result = response.data[0]
            
            # Transform back to expected format
            result['due_date'] = result.get('deadline')
            result['is_active'] = not result.get('archived', False)
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            raise
    
    @staticmethod
    async def get_user_projects(user_id: str, include_tasks: bool = False, include_archived: bool = False) -> List[Dict[str, Any]]:
        """Get user's projects"""
        try:
            query = supabase.table('projects').select('*').eq('user_id', user_id)
            
            if not include_archived:
                query = query.eq('archived', False)  # Use archived instead of is_active
                
            response = query.execute()
            projects = response.data or []
            
            # Transform data to match expected format
            status_reverse_mapping = {
                'Not Started': 'not_started',
                'In Progress': 'in_progress',
                'Completed': 'completed',
                'On Hold': 'on_hold'
            }
            
            priority_reverse_mapping = {
                'Low': 'low',
                'Medium': 'medium', 
                'High': 'high'
            }
            
            for project in projects:
                project['is_active'] = not project.get('archived', False)  # Transform archived to is_active
                project['due_date'] = project.get('deadline')  # Map deadline to due_date
                project['status'] = status_reverse_mapping.get(project.get('status'), 'not_started')
                project['priority'] = priority_reverse_mapping.get(project.get('priority'), 'medium')
            
            # If include_tasks is True, fetch tasks for each project
            if include_tasks and projects:
                for project in projects:
                    tasks_response = supabase.table('tasks').select('*').eq('project_id', project['id']).execute()
                    project['tasks'] = tasks_response.data or []
                    
                    # Get area name if area_id exists
                    if project.get('area_id'):
                        area_response = supabase.table('areas').select('name').eq('id', project['area_id']).single().execute()
                        project['area_name'] = area_response.data.get('name') if area_response.data else None
            
            logger.info(f"✅ Retrieved {len(projects)} projects for user: {user_id}")
            return projects
            
        except Exception as e:
            logger.error(f"Error getting projects: {e}")
            return []
    
    @staticmethod
    async def update_project(project_id: str, user_id: str, project_data: ProjectUpdate) -> Dict[str, Any]:
        """Update a project"""
        try:
            update_dict = {
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Only include fields that are provided
            if project_data.name is not None:
                update_dict['name'] = project_data.name
            if project_data.description is not None:
                update_dict['description'] = project_data.description
            if project_data.area_id is not None:
                update_dict['area_id'] = project_data.area_id
            if project_data.status is not None:
                update_dict['status'] = project_data.status
            if project_data.priority is not None:
                update_dict['priority'] = project_data.priority
            if project_data.color is not None:
                update_dict['color'] = project_data.color
            if project_data.icon is not None:
                update_dict['icon'] = project_data.icon
            if project_data.due_date is not None:
                update_dict['due_date'] = project_data.due_date.isoformat() if project_data.due_date else None
            if project_data.is_active is not None:
                update_dict['is_active'] = project_data.is_active
                
            response = supabase.table('projects').update(update_dict).eq('id', project_id).eq('user_id', user_id).execute()
            
            if not response.data:
                raise Exception("Project not found or no changes made")
                
            logger.info(f"✅ Updated project: {project_id} for user: {user_id}")
            return response.data[0]
            
        except Exception as e:
            logger.error(f"Error updating project: {e}")
            raise
    
    @staticmethod
    async def delete_project(project_id: str, user_id: str) -> bool:
        """Delete a project and all its tasks"""
        try:
            # First, delete all tasks in this project
            tasks_response = supabase.table('tasks').delete().eq('project_id', project_id).execute()
            
            # Then delete the project
            response = supabase.table('projects').delete().eq('id', project_id).eq('user_id', user_id).execute()
            
            logger.info(f"✅ Deleted project: {project_id} and {len(tasks_response.data or [])} tasks")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting project: {e}")
            return False


class SupabaseTaskService:
    """Task CRUD operations with Supabase"""
    
    @staticmethod
    async def create_task(user_id: str, task_data: TaskCreate) -> Dict[str, Any]:
        """Create a new task"""
        try:
            # Map backend status to database status  
            status_mapping = {
                'pending': 'todo',
                'in_progress': 'in_progress',
                'completed': 'completed',
                'cancelled': 'cancelled'
            }
            
            priority_mapping = {
                'low': 'Low',
                'medium': 'Medium',
                'high': 'High'
            }
            
            task_dict = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'project_id': task_data.project_id,
                'parent_task_id': task_data.parent_task_id,
                'name': task_data.name,
                'description': task_data.description or '',
                'status': status_mapping.get(task_data.status or 'pending', 'todo'),
                'priority': priority_mapping.get(task_data.priority or 'medium', 'Medium'),
                'kanban_column': task_data.kanban_column or 'todo',
                'due_date': task_data.due_date.isoformat() if task_data.due_date else None,
                'completed': task_data.completed or False,
                'completed_at': None,
                'sort_order': 0,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'date_created': datetime.utcnow().isoformat()
            }
            
            response = supabase.table('tasks').insert(task_dict).execute()
            
            if not response.data:
                raise Exception("Failed to create task")
                
            logger.info(f"✅ Created task: {task_data.name} for user: {user_id}")
            result = response.data[0]
            
            # Transform back to expected format
            status_reverse_mapping = {
                'todo': 'pending',
                'in_progress': 'in_progress', 
                'completed': 'completed',
                'cancelled': 'cancelled'
            }
            
            priority_reverse_mapping = {
                'Low': 'low',
                'Medium': 'medium',
                'High': 'high'
            }
            
            result['status'] = status_reverse_mapping.get(result.get('status'), 'pending')
            result['priority'] = priority_reverse_mapping.get(result.get('priority'), 'medium')
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            raise
    
    @staticmethod
    async def get_user_tasks(user_id: str, project_id: str = None, completed: bool = None) -> List[Dict[str, Any]]:
        """Get user's tasks"""
        try:
            query = supabase.table('tasks').select('*').eq('user_id', user_id)
            
            if project_id:
                query = query.eq('project_id', project_id)
            if completed is not None:
                query = query.eq('completed', completed)
                
            response = query.execute()
            tasks = response.data or []
            
            logger.info(f"✅ Retrieved {len(tasks)} tasks for user: {user_id}")
            return tasks
            
        except Exception as e:
            logger.error(f"Error getting tasks: {e}")
            return []
    
    @staticmethod
    async def update_task(task_id: str, user_id: str, task_data: TaskUpdate) -> Dict[str, Any]:
        """Update a task"""
        try:
            update_dict = {
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Only include fields that are provided
            if task_data.name is not None:
                update_dict['name'] = task_data.name
            if task_data.description is not None:
                update_dict['description'] = task_data.description
            if task_data.project_id is not None:
                update_dict['project_id'] = task_data.project_id
            if task_data.status is not None:
                update_dict['status'] = task_data.status
            if task_data.priority is not None:
                update_dict['priority'] = task_data.priority
            if task_data.kanban_column is not None:
                update_dict['kanban_column'] = task_data.kanban_column
            if task_data.due_date is not None:
                update_dict['due_date'] = task_data.due_date.isoformat() if task_data.due_date else None
            if task_data.completed is not None:
                update_dict['completed'] = task_data.completed
                if task_data.completed:
                    update_dict['completed_at'] = datetime.utcnow().isoformat()
                else:
                    update_dict['completed_at'] = None
                    
            response = supabase.table('tasks').update(update_dict).eq('id', task_id).eq('user_id', user_id).execute()
            
            if not response.data:
                raise Exception("Task not found or no changes made")
                
            logger.info(f"✅ Updated task: {task_id} for user: {user_id}")
            return response.data[0]
            
        except Exception as e:
            logger.error(f"Error updating task: {e}")
            raise
    
    @staticmethod
    async def delete_task(task_id: str, user_id: str) -> bool:
        """Delete a task and all its subtasks"""
        try:
            # First, delete all subtasks
            subtasks_response = supabase.table('tasks').delete().eq('parent_task_id', task_id).execute()
            
            # Then delete the task
            response = supabase.table('tasks').delete().eq('id', task_id).eq('user_id', user_id).execute()
            
            logger.info(f"✅ Deleted task: {task_id} and {len(subtasks_response.data or [])} subtasks")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting task: {e}")
            return False


class SupabaseDashboardService:
    """Dashboard data with Supabase"""
    
    @staticmethod
    async def get_dashboard_data(user_id: str) -> Dict[str, Any]:
        """Get dashboard data for user"""
        try:
            # Get user profile
            user_profile = await SupabaseUserService.get_user_profile(user_id)
            
            # Get basic stats
            tasks_response = supabase.table('tasks').select('completed').eq('user_id', user_id).execute()
            tasks = tasks_response.data or []
            
            completed_tasks = len([t for t in tasks if t.get('completed')])
            total_tasks = len(tasks)
            
            projects_response = supabase.table('projects').select('status').eq('user_id', user_id).execute()
            projects = projects_response.data or []
            completed_projects = len([p for p in projects if p.get('status') == 'completed'])
            
            # Get recent incomplete tasks
            recent_tasks_response = supabase.table('tasks').select('*').eq('user_id', user_id).eq('completed', False).limit(5).execute()
            recent_tasks = recent_tasks_response.data or []
            
            # Get areas count
            areas_response = supabase.table('areas').select('id').eq('user_id', user_id).execute()
            areas_count = len(areas_response.data or [])
            
            dashboard_data = {
                'user': user_profile,
                'stats': {
                    'completed_tasks': completed_tasks,
                    'total_tasks': total_tasks,
                    'completion_rate': int((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0),
                    'active_projects': len(projects),
                    'completed_projects': completed_projects,
                    'active_areas': areas_count,
                    'current_streak': 0,  # Can be calculated based on completed tasks
                    'habits_today': 0,    # Placeholder
                    'active_learning': 0, # Placeholder
                    'achievements': 0     # Placeholder
                },
                'recent_tasks': recent_tasks,
                'areas': []  # Can be added if needed
            }
            
            logger.info(f"✅ Retrieved dashboard data for user: {user_id}")
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {
                'user': None,
                'stats': {},
                'recent_tasks': [],
                'areas': []
            }