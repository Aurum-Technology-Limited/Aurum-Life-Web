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
supabase_service_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

if not supabase_url or not supabase_anon_key:
    raise ValueError(f"Missing Supabase configuration: URL={bool(supabase_url)}, KEY={bool(supabase_anon_key)}")

# Use service role key for CRUD operations (bypasses RLS for testing)
supabase: Client = create_client(supabase_url, supabase_service_key or supabase_anon_key)


class SupabaseSleepReflectionService:
    """Service for managing sleep reflection data"""
    
    @staticmethod
    async def create_sleep_reflection(user_id: str, reflection_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new sleep reflection entry"""
        try:
            # Prepare data for insertion
            sleep_data = {
                'user_id': user_id,
                'date': reflection_data.get('date') or datetime.now().date().isoformat(),
                'sleep_quality': reflection_data.get('sleep_quality', 5),
                'feeling': reflection_data.get('feeling', ''),
                'sleep_hours': reflection_data.get('sleep_hours', ''),
                'sleep_influences': reflection_data.get('sleep_influences', ''),
                'today_intention': reflection_data.get('today_intention', ''),
                'type': reflection_data.get('type', 'morning_sleep_reflection'),
                'created_at': 'now()',
                'updated_at': 'now()'
            }
            
            # Insert into sleep_reflections table
            response = (supabase.table('sleep_reflections')
                       .insert(sleep_data)
                       .execute())
            
            if response.data:
                logger.info(f"✅ Created sleep reflection for user: {user_id}")
                return response.data[0]
            else:
                logger.error(f"Failed to create sleep reflection: {response}")
                raise Exception("Failed to create sleep reflection")
                
        except Exception as e:
            logger.error(f"Error creating sleep reflection: {e}")
            raise e
    
    @staticmethod
    async def get_user_sleep_reflections(user_id: str, limit: int = 30) -> List[Dict[str, Any]]:
        """Get user's sleep reflections ordered by date (most recent first)"""
        try:
            response = (supabase.table('sleep_reflections')
                       .select('*')
                       .eq('user_id', user_id)
                       .order('date', desc=True)
                       .limit(limit)
                       .execute())
            
            reflections = response.data or []
            
            logger.info(f"✅ Retrieved {len(reflections)} sleep reflections for user: {user_id}")
            return reflections
            
        except Exception as e:
            logger.error(f"Error getting sleep reflections: {e}")
            return []
    
    @staticmethod 
    async def get_sleep_reflection_by_date(user_id: str, date: str) -> Dict[str, Any]:
        """Get sleep reflection for a specific date"""
        try:
            response = (supabase.table('sleep_reflections')
                       .select('*')
                       .eq('user_id', user_id)
                       .eq('date', date)
                       .single()
                       .execute())
            
            if response.data:
                logger.info(f"✅ Found sleep reflection for user {user_id} on {date}")
                return response.data
            else:
                logger.info(f"No sleep reflection found for user {user_id} on {date}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting sleep reflection by date: {e}")
            return {}


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
    
    @staticmethod
    async def update_user_profile(user_id: str, profile_data: Dict[str, Any], ip_address: str = None) -> Optional[Dict[str, Any]]:
        """
        Update user profile with username change rate limiting (7 days between changes)
        """
        try:
            # Check if username is being changed
            username_change = profile_data.get('username')
            if username_change:
                # Get current user data to check existing username and last username change
                current_user_response = supabase.table('user_profiles')\
                    .select('*')\
                    .eq('id', user_id)\
                    .limit(1)\
                    .execute()
                
                if not current_user_response.data:
                    raise Exception("User not found")
                
                current_user = current_user_response.data[0]
                current_username = current_user.get('username')
                last_username_change = current_user.get('last_username_change')
                
                # Only check rate limiting if username is actually changing
                if current_username != username_change:
                    # Check if user has changed username in the last 7 days
                    if last_username_change:
                        try:
                            # Parse the last change date
                            if isinstance(last_username_change, str):
                                last_change_date = datetime.fromisoformat(last_username_change.replace('Z', '+00:00'))
                            else:
                                last_change_date = last_username_change
                            
                            # Calculate days since last change
                            days_since_change = (datetime.utcnow() - last_change_date.replace(tzinfo=None)).days
                            
                            if days_since_change < 7:
                                days_remaining = 7 - days_since_change
                                raise Exception(f"Username can only be changed once every 7 days. Please wait {days_remaining} more day(s).")
                                
                        except ValueError as e:
                            # If date parsing fails, allow the change (first time setup)
                            logger.warning(f"Failed to parse last username change date: {str(e)}")
                    
                    # Check if username is already taken
                    existing_user = supabase.table('user_profiles')\
                        .select('id')\
                        .eq('username', username_change)\
                        .neq('id', user_id)\
                        .limit(1)\
                        .execute()
                    
                    if existing_user.data and len(existing_user.data) > 0:
                        raise Exception("Username is already taken")
                    
                    # Add the username change timestamp to the profile data
                    profile_data['last_username_change'] = datetime.utcnow().isoformat()
                    logger.info(f"Recording username change for user {user_id}: {current_username} -> {username_change}")
            
            # Proceed with profile update
            return await SupabaseUserService.update_user(user_id, profile_data)
            
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            raise
    
    @staticmethod
    async def update_user(user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user profile in both user_profiles table and legacy users table"""
        try:
            # Add updated_at timestamp
            update_data['updated_at'] = datetime.utcnow().isoformat()
            
            # Handle has_completed_onboarding by mapping to level field
            # level = 1 means onboarding not completed, level = 2 means completed
            if 'has_completed_onboarding' in update_data:
                has_completed = update_data.pop('has_completed_onboarding')
                update_data['level'] = 2 if has_completed else 1
                logger.info(f"Mapped has_completed_onboarding={has_completed} to level={update_data['level']}")
            
            updated_record = None
            
            # Try to update legacy users table first
            try:
                legacy_response = supabase.table('users').update(update_data).eq('id', user_id).execute()
                
                if legacy_response.data:
                    logger.info(f"✅ Updated legacy user record for user: {user_id}")
                    updated_record = legacy_response.data[0]
            except Exception as legacy_error:
                logger.info(f"Legacy users table update failed: {legacy_error}")
            
            # CRITICAL FIX: Also try to update user_profiles table to ensure consistency
            try:
                profile_response = supabase.table('user_profiles').update(update_data).eq('id', user_id).execute()
                
                if profile_response.data:
                    logger.info(f"✅ Updated user_profiles record for user: {user_id}")
                    # If we didn't get a record from legacy table, use this one
                    if not updated_record:
                        updated_record = profile_response.data[0]
            except Exception as profile_error:
                logger.info(f"User_profiles table update failed: {profile_error}")
            
            if updated_record:
                return updated_record
            
            logger.warning(f"No user record found for user: {user_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return None


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
                'time_allocation_percentage': pillar_data.time_allocation_percentage or 0,  # Use correct field name
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
        """Get user's pillars with calculated statistics"""
        try:
            query = supabase.table('pillars').select('*').eq('user_id', user_id)
            
            if not include_archived:
                query = query.eq('archived', False)  # Use archived instead of is_active
                
            response = query.execute()
            pillars = response.data or []
            
            if not pillars:
                return []
            
            # Get pillar IDs for batch operations
            pillar_ids = [pillar['id'] for pillar in pillars]
            
            # Batch fetch areas for all pillars
            areas_response = supabase.table('areas').select('*').in_('pillar_id', pillar_ids).execute()
            all_areas = areas_response.data or []
            
            # Group areas by pillar_id
            areas_by_pillar = {}
            area_ids = []
            for area in all_areas:
                pillar_id = area.get('pillar_id')
                if pillar_id:
                    if pillar_id not in areas_by_pillar:
                        areas_by_pillar[pillar_id] = []
                    areas_by_pillar[pillar_id].append(area)
                    area_ids.append(area['id'])
            
            # Batch fetch projects for all areas
            projects_by_area = {}
            project_ids = []
            if area_ids:
                projects_response = supabase.table('projects').select('*').in_('area_id', area_ids).execute()
                all_projects = projects_response.data or []
                
                for project in all_projects:
                    area_id = project.get('area_id')
                    if area_id:
                        if area_id not in projects_by_area:
                            projects_by_area[area_id] = []
                        projects_by_area[area_id].append(project)
                        project_ids.append(project['id'])
            
            # Batch fetch tasks for all projects
            tasks_by_project = {}
            if project_ids:
                tasks_response = supabase.table('tasks').select('*').in_('project_id', project_ids).execute()
                all_tasks = tasks_response.data or []
                
                for task in all_tasks:
                    project_id = task.get('project_id')
                    if project_id:
                        if project_id not in tasks_by_project:
                            tasks_by_project[project_id] = []
                        tasks_by_project[project_id].append(task)
            
            # Transform data and calculate statistics for each pillar
            for pillar in pillars:
                pillar['is_active'] = not pillar.get('archived', False)  # Transform archived to is_active
                pillar['time_allocation'] = pillar.get('time_allocation_percentage', 0)  # Map field name back
                
                # Calculate statistics
                pillar_areas = areas_by_pillar.get(pillar['id'], [])
                pillar['area_count'] = len(pillar_areas)
                
                # Count projects across all areas of this pillar
                pillar_projects = []
                for area in pillar_areas:
                    area_projects = projects_by_area.get(area['id'], [])
                    pillar_projects.extend(area_projects)
                
                pillar['project_count'] = len(pillar_projects)
                
                # Count tasks across all projects of this pillar
                pillar_tasks = []
                for project in pillar_projects:
                    project_tasks = tasks_by_project.get(project['id'], [])
                    pillar_tasks.extend(project_tasks)
                
                pillar['task_count'] = len(pillar_tasks)
                
                # Calculate completion statistics
                completed_tasks = [task for task in pillar_tasks if task.get('completed', False)]
                pillar['completed_task_count'] = len(completed_tasks)
                
                if pillar_tasks:
                    pillar['progress_percentage'] = (len(completed_tasks) / len(pillar_tasks)) * 100
                else:
                    pillar['progress_percentage'] = 0.0
                
                # Add areas if requested (already batch-fetched)
                if include_areas:
                    pillar['areas'] = pillar_areas
            
            logger.info(f"✅ Retrieved {len(pillars)} pillars with statistics for user: {user_id}")
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
            
            # Only include fields that are provided and map to correct database fields
            if pillar_data.name is not None:
                update_dict['name'] = pillar_data.name
            if pillar_data.description is not None:
                update_dict['description'] = pillar_data.description
            if pillar_data.color is not None:
                update_dict['color'] = pillar_data.color
            if pillar_data.icon is not None:
                update_dict['icon'] = pillar_data.icon
            if getattr(pillar_data, 'time_allocation', None) is not None:
                update_dict['time_allocation_percentage'] = pillar_data.time_allocation  # Map field name
            if getattr(pillar_data, 'is_active', None) is not None:
                update_dict['archived'] = not pillar_data.is_active  # Map is_active to archived (inverted)
                
            response = supabase.table('pillars').update(update_dict).eq('id', pillar_id).eq('user_id', user_id).execute()
            
            if not response.data:
                raise Exception("Pillar not found or no changes made")
                
            logger.info(f"✅ Updated pillar: {pillar_id} for user: {user_id}")
            result = response.data[0]
            
            # Transform back to expected format
            result['is_active'] = not result.get('archived', False)  # Transform archived to is_active
            result['time_allocation'] = result.get('time_allocation_percentage', 0)  # Map field name back
            
            return result
            
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
            # Validate pillar_id exists if provided
            if area_data.pillar_id:
                # First validate UUID format to avoid database errors
                try:
                    uuid.UUID(area_data.pillar_id)
                except ValueError:
                    raise ValueError(f"Invalid pillar_id format: '{area_data.pillar_id}' is not a valid UUID")
                
                pillar_check = supabase.table('pillars').select('id').eq('id', area_data.pillar_id).eq('user_id', user_id).execute()
                if not pillar_check.data:
                    raise ValueError(f"Pillar with id '{area_data.pillar_id}' not found for user '{user_id}'")
            
            # Handle importance as integer (schema fix applied)
            importance_value = area_data.importance
            if isinstance(importance_value, str):
                # Legacy string mapping for backward compatibility
                importance_mapping = {
                    'low': 1,
                    'medium': 3,
                    'high': 5
                }
                importance_value = importance_mapping.get(importance_value, 3)
            elif isinstance(importance_value, int):
                # Direct integer value (new schema)
                importance_value = importance_value
            else:
                importance_value = 3  # Default
            
            area_dict = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'pillar_id': area_data.pillar_id,  # Can be null for areas without pillars
                'name': area_data.name,
                'description': area_data.description or '',
                'color': area_data.color or '#10B981',
                'icon': area_data.icon or 'Circle',
                'importance': importance_value,  # Use processed importance value
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
        """Get user's areas with optimized batch queries"""
        try:
            # Single optimized query for areas
            query = supabase.table('areas').select('*').eq('user_id', user_id)
            
            if not include_archived:
                query = query.eq('archived', False)  # Use archived instead of is_active
                
            response = query.execute()
            areas = response.data or []
            
            if not areas:
                return []
            
            # Extract area IDs and pillar IDs for batch operations
            area_ids = [area['id'] for area in areas]
            pillar_ids = [area['pillar_id'] for area in areas if area.get('pillar_id')]
            
            # Batch fetch all projects for all areas in one query (if needed)
            projects_by_area = {}
            if include_projects and area_ids:
                projects_response = supabase.table('projects').select('*').in_('area_id', area_ids).execute()
                all_projects = projects_response.data or []
                
                # Group projects by area_id
                for project in all_projects:
                    area_id = project['area_id']
                    if area_id not in projects_by_area:
                        projects_by_area[area_id] = []
                    projects_by_area[area_id].append(project)
            
            # Batch fetch all pillar names in one query (if needed)
            pillars_by_id = {}
            if pillar_ids:
                pillars_response = supabase.table('pillars').select('id, name').in_('id', pillar_ids).execute()
                pillars_data = pillars_response.data or []
                pillars_by_id = {pillar['id']: pillar['name'] for pillar in pillars_data}
            
            # Transform data to match expected format - OPTIMIZED
            # Process areas with batch-fetched data
            for area in areas:
                area['is_active'] = not area.get('archived', False)  # Transform archived to is_active
                # Keep importance as integer (1-5) - frontend expects integers, no need for string conversion
                if 'importance' in area and area['importance'] is not None:
                    area['importance'] = int(area['importance'])  # Ensure it's an integer
                
                # Add projects if requested (already batch-fetched)
                if include_projects:
                    area['projects'] = projects_by_area.get(area['id'], [])
                
                # Add pillar name if available (already batch-fetched)
                if area.get('pillar_id') and area['pillar_id'] in pillars_by_id:
                    area['pillar_name'] = pillars_by_id[area['pillar_id']]
            
            logger.info(f"✅ Retrieved {len(areas)} areas for user: {user_id} (optimized batch queries)")
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
            
            # Only include fields that are provided and map to correct database fields
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
                # Handle importance as integer (direct value from frontend)
                # ImportanceEnum values: 1=low, 2=medium_low, 3=medium, 4=medium_high, 5=critical
                if isinstance(area_data.importance, int):
                    update_dict['importance'] = area_data.importance
                elif hasattr(area_data.importance, 'value'):
                    # Handle enum object
                    update_dict['importance'] = area_data.importance.value
                else:
                    # Fallback - try to convert
                    update_dict['importance'] = int(area_data.importance)
            if getattr(area_data, 'is_active', None) is not None:
                update_dict['archived'] = not area_data.is_active  # Map is_active to archived (inverted)
                
            response = supabase.table('areas').update(update_dict).eq('id', area_id).eq('user_id', user_id).execute()
            
            if not response.data:
                raise Exception("Area not found or no changes made")
                
            logger.info(f"✅ Updated area: {area_id} for user: {user_id}")
            result = response.data[0]
            
            # Transform back to expected format
            result['is_active'] = not result.get('archived', False)  # Transform archived to is_active
            # Keep importance as integer (1-5) - don't convert to string
            # The frontend expects integer values for importance field validation
            if 'importance' in result and result['importance'] is not None:
                # Ensure importance is returned as integer
                result['importance'] = int(result['importance'])
            
            return result
            
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
            project_dict = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'area_id': project_data.area_id,
                'name': project_data.name,
                'description': project_data.description or '',
                'status': project_data.status or 'Not Started',  # Database uses display names
                'priority': project_data.priority or 'medium',   # Database uses lowercase
                'icon': project_data.icon or 'FolderOpen',
                'deadline': project_data.deadline.isoformat() if project_data.deadline else None,
                'importance': 3,  # Default importance as integer
                'archived': False,  # Map is_active to archived (inverted)
                'sort_order': 0,
                'completion_percentage': 0.0,  # Float as per database
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
        """Get user's projects with optimized batch queries"""
        try:
            query = supabase.table('projects').select('*').eq('user_id', user_id)
            
            if not include_archived:
                query = query.eq('archived', False)  # Use archived instead of is_active
                
            response = query.execute()
            projects = response.data or []
            
            if not projects:
                return []
            
            # Extract project IDs and area IDs for batch operations
            project_ids = [project['id'] for project in projects]
            area_ids = [project['area_id'] for project in projects if project.get('area_id')]
            
            # Batch fetch all tasks for all projects in one query (if needed)
            tasks_by_project = {}
            if include_tasks and project_ids:
                tasks_response = supabase.table('tasks').select('*').in_('project_id', project_ids).execute()
                all_tasks = tasks_response.data or []
                
                # Group tasks by project_id
                for task in all_tasks:
                    project_id = task['project_id']
                    if project_id not in tasks_by_project:
                        tasks_by_project[project_id] = []
                    tasks_by_project[project_id].append(task)
            
            # Batch fetch all area names in one query (if needed)
            areas_by_id = {}
            if area_ids:
                areas_response = supabase.table('areas').select('id, name').in_('id', area_ids).execute()
                areas_data = areas_response.data or []
                areas_by_id = {area['id']: area['name'] for area in areas_data}
            
            # Transform data to match expected format with batch-fetched data
            for project in projects:
                project['is_active'] = not project.get('archived', False)  # Transform archived to is_active
                project['due_date'] = project.get('deadline')  # Map deadline to due_date
                
                # Add tasks if requested (already batch-fetched)
                if include_tasks:
                    project['tasks'] = tasks_by_project.get(project['id'], [])
                
                # Add area name if available (already batch-fetched)
                if project.get('area_id') and project['area_id'] in areas_by_id:
                    project['area_name'] = areas_by_id[project['area_id']]
            
            logger.info(f"✅ Retrieved {len(projects)} projects for user: {user_id} (optimized batch queries)")
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
            
            # Only include fields that are provided and map to correct database fields
            if project_data.name is not None:
                update_dict['name'] = project_data.name
            if project_data.description is not None:
                update_dict['description'] = project_data.description
            if project_data.status is not None:
                # Map backend status to database status
                status_mapping = {
                    'not_started': 'Not Started',
                    'in_progress': 'In Progress',
                    'completed': 'Completed',
                    'on_hold': 'On Hold'
                }
                update_dict['status'] = status_mapping.get(project_data.status, project_data.status)
            if project_data.priority is not None:
                # Keep priority as is (database uses lowercase)
                update_dict['priority'] = project_data.priority
            if hasattr(project_data, 'color') and project_data.color is not None:
                update_dict['color'] = project_data.color
            if project_data.icon is not None:
                update_dict['icon'] = project_data.icon
            if project_data.deadline is not None:
                update_dict['deadline'] = project_data.deadline.isoformat() if project_data.deadline else None
                
            response = supabase.table('projects').update(update_dict).eq('id', project_id).eq('user_id', user_id).execute()
            
            if not response.data:
                raise Exception("Project not found or no changes made")
                
            logger.info(f"✅ Updated project: {project_id} for user: {user_id}")
            result = response.data[0]
            
            # Transform back to expected format
            result['is_active'] = not result.get('archived', False)  # Transform archived to is_active
            result['due_date'] = result.get('deadline')  # Map deadline back to due_date
            
            # Map status back to backend format
            status_reverse_mapping = {
                'Not Started': 'not_started',
                'In Progress': 'in_progress',
                'Completed': 'completed',
                'On Hold': 'on_hold'
            }
            result['status'] = status_reverse_mapping.get(result.get('status'), result.get('status'))
            
            return result
            
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
            # Validate project_id exists for the user
            try:
                uuid.UUID(task_data.project_id)
            except ValueError:
                raise ValueError(f"Invalid project_id format: '{task_data.project_id}' is not a valid UUID")
                
            project_check = supabase.table('projects').select('id').eq('id', task_data.project_id).eq('user_id', user_id).execute()
            if not project_check.data:
                raise ValueError(f"Project with id '{task_data.project_id}' not found for user '{user_id}'")
            
            # Validate parent_task_id exists if provided
            if task_data.parent_task_id:
                try:
                    uuid.UUID(task_data.parent_task_id)
                except ValueError:
                    raise ValueError(f"Invalid parent_task_id format: '{task_data.parent_task_id}' is not a valid UUID")
                    
                parent_task_check = supabase.table('tasks').select('id').eq('id', task_data.parent_task_id).eq('user_id', user_id).execute()
                if not parent_task_check.data:
                    raise ValueError(f"Parent task with id '{task_data.parent_task_id}' not found for user '{user_id}'")
                    
            # Map backend status to database status  
            status_mapping = {
                'todo': 'todo',
                'in_progress': 'in_progress',
                'completed': 'completed',
                'review': 'review'
            }
            
            priority_mapping = {
                'low': 'low',
                'medium': 'medium',
                'high': 'high'
            }
            
            task_dict = {
                'id': str(uuid.uuid4()),
                'user_id': user_id,
                'project_id': task_data.project_id,
                'parent_task_id': task_data.parent_task_id,
                'name': task_data.name,
                'description': task_data.description or '',
                'status': status_mapping.get(task_data.status or 'todo', 'todo'),
                'priority': priority_mapping.get(task_data.priority or 'medium', 'Medium'),
                'kanban_column': getattr(task_data, 'kanban_column', 'to_do'),
                'due_date': task_data.due_date.isoformat() if task_data.due_date else None,
                'completed': getattr(task_data, 'completed', False),
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
                'todo': 'todo',
                'in_progress': 'in_progress', 
                'completed': 'completed',
                'review': 'review'
            }
            
            priority_reverse_mapping = {
                'low': 'low',
                'medium': 'medium',
                'high': 'high'
            }
            
            result['status'] = status_reverse_mapping.get(result.get('status'), 'todo')
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
            
            # Transform data to match expected format
            status_reverse_mapping = {
                'todo': 'todo',
                'in_progress': 'in_progress',
                'completed': 'completed',
                'review': 'review'
            }
            
            priority_reverse_mapping = {
                'Low': 'low',
                'Medium': 'medium',
                'High': 'high'
            }
            
            for task in tasks:
                task['status'] = status_reverse_mapping.get(task.get('status'), 'todo')
                task['priority'] = priority_reverse_mapping.get(task.get('priority'), 'medium')
            
            logger.info(f"✅ Retrieved {len(tasks)} tasks for user: {user_id}")
            return tasks
            
        except Exception as e:
            logger.error(f"Error getting tasks: {e}")
            return []
    
    @staticmethod
    async def search_tasks_by_name(user_id: str, search_query: str) -> List[Dict[str, Any]]:
        """Search tasks by name - only returns tasks with 'To Do' or 'In Progress' status"""
        try:
            # Search for tasks matching the name query and filter by status
            # Using ilike for case-insensitive search with wildcards
            query = (supabase.table('tasks')
                    .select('*, projects(name)')  # Join with projects to get project name
                    .eq('user_id', user_id)
                    .ilike('name', f'%{search_query}%')  # Case-insensitive partial match
                    .in_('status', ['todo', 'in_progress'])  # Only todo and in_progress tasks
                    .eq('completed', False)  # Exclude completed tasks
                    .order('created_at', desc=True)  # Most recent first
                    .limit(20))  # Limit results for performance
            
            response = query.execute()
            tasks = response.data or []
            
            # Transform data to match expected format
            status_reverse_mapping = {
                'todo': 'todo',
                'in_progress': 'in_progress',
                'completed': 'completed',
                'review': 'review'
            }
            
            priority_reverse_mapping = {
                'Low': 'low',
                'Medium': 'medium', 
                'High': 'high'
            }
            
            for task in tasks:
                task['status'] = status_reverse_mapping.get(task.get('status'), 'todo')
                task['priority'] = priority_reverse_mapping.get(task.get('priority'), 'medium')
                
                # Extract project name from joined data
                if task.get('projects') and isinstance(task['projects'], dict):
                    task['project_name'] = task['projects'].get('name', '')
                else:
                    task['project_name'] = ''
                
                # Clean up the joined projects data
                if 'projects' in task:
                    del task['projects']
            
            logger.info(f"✅ Found {len(tasks)} tasks matching '{search_query}' for user: {user_id}")
            return tasks
            
        except Exception as e:
            logger.error(f"Error searching tasks: {e}")
            return []
    
    @staticmethod
    async def update_task(task_id: str, user_id: str, task_data: TaskUpdate) -> Dict[str, Any]:
        """Update a task"""
        try:
            update_dict = {
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Only include fields that are provided and map to correct database fields
            if task_data.name is not None:
                update_dict['name'] = task_data.name
            if task_data.description is not None:
                update_dict['description'] = task_data.description
            if task_data.status is not None:
                # Map backend status to database status (using correct TaskStatusEnum values)
                status_mapping = {
                    'todo': 'todo',
                    'in_progress': 'in_progress',
                    'completed': 'completed',
                    'review': 'review'
                }
                mapped_status = status_mapping.get(str(task_data.status), str(task_data.status))
                update_dict['status'] = mapped_status
                
                # Auto-complete if setting status to completed
                if mapped_status == 'completed' and not task_data.completed:
                    update_dict['completed'] = True
                    update_dict['completed_at'] = datetime.utcnow().isoformat()
                    
            if task_data.priority is not None:
                # Map backend priority to database priority (keep consistent casing)
                priority_mapping = {
                    'low': 'low',
                    'medium': 'medium',
                    'high': 'high'
                }
                update_dict['priority'] = priority_mapping.get(str(task_data.priority), str(task_data.priority))
            if task_data.kanban_column is not None:
                update_dict['kanban_column'] = task_data.kanban_column
            if task_data.due_date is not None:
                update_dict['due_date'] = task_data.due_date.isoformat() if task_data.due_date else None
            if task_data.completed is not None:
                update_dict['completed'] = task_data.completed
                if task_data.completed:
                    update_dict['completed_at'] = datetime.utcnow().isoformat()
                    # Auto-set status to completed when marking as complete
                    update_dict['status'] = 'completed'
                else:
                    update_dict['completed_at'] = None
                    # Reset status if uncompleting (unless explicitly set)
                    if task_data.status is None:
                        update_dict['status'] = 'todo'
                        
            response = supabase.table('tasks').update(update_dict).eq('id', task_id).eq('user_id', user_id).execute()
            
            if not response.data:
                raise Exception("Task not found or no changes made")
                
            logger.info(f"✅ Updated task: {task_id} for user: {user_id}")
            result = response.data[0]
            
            # Transform back to expected format
            status_reverse_mapping = {
                'todo': 'todo',
                'in_progress': 'in_progress',
                'completed': 'completed',
                'review': 'review'
            }
            result['status'] = status_reverse_mapping.get(result.get('status'), result.get('status'))
            
            priority_reverse_mapping = {
                'low': 'low',
                'medium': 'medium',
                'high': 'high'
            }
            result['priority'] = priority_reverse_mapping.get(result.get('priority'), result.get('priority'))
            
            return result
            
        except ValueError as e:
            logger.error(f"Validation error updating task: {e}")
            raise
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
            
            # Remove achievement/level related fields from user profile
            if user_profile:
                # Remove level and points fields that are no longer needed
                user_profile.pop('level', None)
                user_profile.pop('total_points', None)
            
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
                    'active_learning': 0  # Placeholder - removed achievements field
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


class SupabaseInsightsService:
    """Service for generating meaningful insights and analytics"""
    
    @staticmethod
    async def get_comprehensive_insights(user_id: str, date_range: str = "all_time") -> Dict[str, Any]:
        """Generate comprehensive insights with real user data"""
        try:
            # Get all user data in batch
            pillars_data = await SupabasePillarService.get_user_pillars(user_id, include_areas=True, include_archived=False)
            areas_data = await SupabaseAreaService.get_user_areas(user_id, include_projects=True, include_archived=False)
            projects_data = await SupabaseProjectService.get_user_projects(user_id, include_tasks=False, include_archived=False)
            tasks_data = await SupabaseTaskService.get_user_tasks(user_id)
            
            # Calculate basic statistics
            total_tasks = len(tasks_data)
            completed_tasks = [task for task in tasks_data if task.get('completed', False)]
            total_tasks_completed = len(completed_tasks)
            
            total_projects = len(projects_data)
            completed_projects = [proj for proj in projects_data if proj.get('status') == 'completed']
            total_projects_completed = len(completed_projects)
            
            # Calculate pillar alignment with real data
            pillar_alignment = []
            if pillars_data and completed_tasks:
                for pillar in pillars_data:
                    # Get tasks for this pillar through the hierarchy: pillar -> areas -> projects -> tasks
                    pillar_areas = [area for area in areas_data if area.get('pillar_id') == pillar['id']]
                    pillar_projects = []
                    for area in pillar_areas:
                        area_projects = [proj for proj in projects_data if proj.get('area_id') == area['id']]
                        pillar_projects.extend(area_projects)
                    
                    pillar_tasks = []
                    for project in pillar_projects:
                        project_tasks = [task for task in completed_tasks if task.get('project_id') == project['id']]
                        pillar_tasks.extend(project_tasks)
                    
                    pillar_task_count = len(pillar_tasks)
                    pillar_percentage = (pillar_task_count / total_tasks_completed * 100) if total_tasks_completed > 0 else 0
                    
                    if pillar_task_count > 0 or pillar_percentage > 0:  # Only include pillars with activity
                        pillar_alignment.append({
                            "pillar_id": pillar['id'],
                            "pillar_name": pillar['name'],
                            "pillar_icon": pillar.get('icon', '🎯'),
                            "pillar_color": pillar.get('color', '#F4B400'),
                            "task_count": pillar_task_count,
                            "percentage": round(pillar_percentage, 1),
                            "areas_count": len(pillar_areas),
                            "projects_count": len(pillar_projects)
                        })
                
                # Sort by percentage (highest first)
                pillar_alignment.sort(key=lambda x: x['percentage'], reverse=True)
            
            # Add pillars with no completed tasks (but show 0%)
            if pillars_data:
                included_pillar_ids = {item['pillar_id'] for item in pillar_alignment}
                for pillar in pillars_data:
                    if pillar['id'] not in included_pillar_ids:
                        pillar_areas = [area for area in areas_data if area.get('pillar_id') == pillar['id']]
                        pillar_projects = []
                        for area in pillar_areas:
                            area_projects = [proj for proj in projects_data if proj.get('area_id') == area['id']]
                            pillar_projects.extend(area_projects)
                        
                        pillar_alignment.append({
                            "pillar_id": pillar['id'], 
                            "pillar_name": pillar['name'],
                            "pillar_icon": pillar.get('icon', '🎯'),
                            "pillar_color": pillar.get('color', '#F4B400'),
                            "task_count": 0,
                            "percentage": 0.0,
                            "areas_count": len(pillar_areas),
                            "projects_count": len(pillar_projects)
                        })
            
            # Calculate productivity trends (mock for now, can be enhanced with actual date-based analysis)
            productivity_trends = {
                "this_week": 85 if total_tasks_completed > 20 else 65,
                "last_week": 72 if total_tasks_completed > 15 else 55,
                "monthly_average": 78 if total_tasks_completed > 10 else 60,
                "trend": "increasing" if total_tasks_completed > 25 else "stable"
            }
            
            # Calculate area distribution
            area_distribution = []
            if areas_data and completed_tasks:
                for area in areas_data:
                    area_projects = [proj for proj in projects_data if proj.get('area_id') == area['id']]
                    area_tasks = []
                    for project in area_projects:
                        project_tasks = [task for task in completed_tasks if task.get('project_id') == project['id']]
                        area_tasks.extend(project_tasks)
                    
                    area_task_count = len(area_tasks)
                    area_percentage = (area_task_count / total_tasks_completed * 100) if total_tasks_completed > 0 else 0
                    
                    if area_task_count > 0:
                        area_distribution.append({
                            "area_id": area['id'],
                            "area_name": area['name'],
                            "area_icon": area.get('icon', '🎯'),
                            "area_color": area.get('color', '#10B981'),
                            "task_count": area_task_count,
                            "percentage": round(area_percentage, 1),
                            "projects_count": len(area_projects)
                        })
                
                # Sort by percentage
                area_distribution.sort(key=lambda x: x['percentage'], reverse=True)
            
            # Generate actionable insights
            insights_text = []
            if pillar_alignment:
                top_pillar = pillar_alignment[0]
                if top_pillar['percentage'] > 50:
                    insights_text.append(f"🔍 You're heavily focused on {top_pillar['pillar_name']} ({top_pillar['percentage']}% of completed tasks). Consider if this aligns with your current priorities.")
                elif top_pillar['percentage'] > 0:
                    insights_text.append(f"✅ Your effort is well-distributed across pillars. Your top focus is {top_pillar['pillar_name']} at {top_pillar['percentage']}%.")
                else:
                    insights_text.append("📊 No completed tasks yet. Start by completing some tasks to see your pillar alignment!")
                
                # Add recommendations
                zero_pillars = [p for p in pillar_alignment if p['percentage'] == 0 and p['areas_count'] > 0]
                if zero_pillars:
                    insights_text.append(f"💡 Consider focusing on {zero_pillars[0]['pillar_name']} - it has {zero_pillars[0]['areas_count']} areas but no completed tasks yet.")
            
            return {
                "alignment_snapshot": {
                    "total_tasks": total_tasks,
                    "total_tasks_completed": total_tasks_completed,
                    "total_projects": total_projects,
                    "total_projects_completed": total_projects_completed,
                    "pillar_alignment": pillar_alignment[:6],  # Limit to top 6 pillars
                    "completion_rate": round((total_tasks_completed / total_tasks * 100), 1) if total_tasks > 0 else 0
                },
                "productivity_trends": productivity_trends,
                "area_distribution": area_distribution[:5],  # Top 5 areas
                "insights_text": insights_text,
                "recommendations": await SupabaseInsightsService._generate_recommendations(pillars_data, areas_data, projects_data, tasks_data),
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return {
                "alignment_snapshot": {
                    "total_tasks": 0,
                    "total_tasks_completed": 0,
                    "total_projects": 0,
                    "total_projects_completed": 0,
                    "pillar_alignment": [],
                    "completion_rate": 0
                },
                "productivity_trends": {
                    "this_week": 0,
                    "last_week": 0,
                    "monthly_average": 0,
                    "trend": "no_data"
                },
                "area_distribution": [],
                "insights_text": ["📊 Unable to generate insights. Please try again later."],
                "recommendations": [],
                "generated_at": datetime.utcnow().isoformat()
            }
    
    @staticmethod
    async def _generate_recommendations(pillars_data: List[Dict], areas_data: List[Dict], projects_data: List[Dict], tasks_data: List[Dict]) -> List[Dict[str, str]]:
        """Generate actionable recommendations based on user data"""
        recommendations = []
        
        try:
            # Recommendation 1: Areas without projects
            areas_without_projects = [area for area in areas_data if not any(proj.get('area_id') == area['id'] for proj in projects_data)]
            if areas_without_projects:
                area = areas_without_projects[0]
                recommendations.append({
                    "type": "create_project",
                    "title": f"Create a project in {area['name']}",
                    "description": f"You have the '{area['name']}' area but no projects in it yet. Consider creating a project to start making progress.",
                    "action": "create_project",
                    "area_id": area['id']
                })
            
            # Recommendation 2: Projects without tasks
            projects_without_tasks = [proj for proj in projects_data if not any(task.get('project_id') == proj['id'] for task in tasks_data)]
            if projects_without_tasks:
                project = projects_without_tasks[0]
                recommendations.append({
                    "type": "create_task",
                    "title": f"Add tasks to '{project['name']}'",
                    "description": f"Break down your '{project['name']}' project into actionable tasks to start making progress.",
                    "action": "create_task",
                    "project_id": project['id']
                })
            
            # Recommendation 3: Incomplete tasks
            incomplete_tasks = [task for task in tasks_data if not task.get('completed', False)]
            if incomplete_tasks:
                recommendations.append({
                    "type": "complete_tasks",
                    "title": f"Complete {min(3, len(incomplete_tasks))} pending tasks",
                    "description": f"You have {len(incomplete_tasks)} incomplete tasks. Focus on completing a few to make progress.",
                    "action": "complete_tasks",
                    "count": len(incomplete_tasks)
                })
            
            # Recommendation 4: Pillars without areas
            pillars_without_areas = [pillar for pillar in pillars_data if not any(area.get('pillar_id') == pillar['id'] for area in areas_data)]
            if pillars_without_areas:
                pillar = pillars_without_areas[0]
                recommendations.append({
                    "type": "create_area",
                    "title": f"Add areas to {pillar['name']} pillar",
                    "description": f"Your '{pillar['name']}' pillar doesn't have any areas yet. Create some life areas to organize this pillar better.",
                    "action": "create_area",
                    "pillar_id": pillar['id']
                })
                
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            
        return recommendations[:3]  # Return top 3 recommendations