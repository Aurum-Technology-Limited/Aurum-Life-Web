"""
Refactored Services Layer
Eliminates service-to-service calls and N+1 queries using Repository Pattern
Following Clean Architecture and SOLID principles
"""

from typing import List, Optional
from datetime import datetime
import logging

from repository import RepositoryManager
from performance_monitor import track_endpoint_performance
from models import (
    PillarResponse, AreaResponse, ProjectResponse, TaskResponse,
    User, UserStats, UserDashboard
)

logger = logging.getLogger(__name__)

class OptimizedPillarService:
    """
    REFACTORED Pillar Service - No service-to-service calls
    Uses Repository Pattern for all data access
    """
    
    @staticmethod
    @track_endpoint_performance("pillars.get_user_pillars")
    async def get_user_pillars(user_id: str, include_areas: bool = False, include_archived: bool = False) -> List[PillarResponse]:
        """
        Get user pillars with optimized single-batch data fetching
        NO service-to-service calls, NO N+1 queries
        """
        logger.info(f"OptimizedPillarService: Getting pillars for user {user_id} (include_areas: {include_areas})")
        
        # Get repository for this request
        repo = RepositoryManager.get_repository(user_id)
        
        # Single batch operation - fetches ALL data at once
        pillars = await repo.get_pillars(include_archived=include_archived)
        
        if not pillars:
            logger.info(f"OptimizedPillarService: No pillars found for user {user_id}")
            return []
        
        # If we need areas, get all data in batch
        if include_areas:
            # Get all data in single operation (cached from above)
            all_data = await repo.get_all_user_data()
            areas = all_data['areas']
            projects = all_data['projects'] 
            tasks = all_data['tasks']
            
            # Process pillars with batch-fetched data
            return [
                OptimizedPillarService._build_pillar_response_optimized(
                    pillar, areas, projects, tasks, include_areas=True
                )
                for pillar in pillars
            ]
        else:
            # Simple pillar responses without nested data
            return [PillarResponse(**pillar) for pillar in pillars]
    
    @staticmethod
    def _build_pillar_response_optimized(
        pillar_doc: dict, 
        areas: List[dict], 
        projects: List[dict], 
        tasks: List[dict],
        include_areas: bool = False
    ) -> PillarResponse:
        """
        Build pillar response using pre-fetched batch data
        NO database calls, NO service calls - pure data processing
        """
        pillar_response = PillarResponse(**pillar_doc)
        
        # Filter areas for this pillar (in-memory operation)
        pillar_areas = [area for area in areas if area.get('pillar_id') == pillar_response.id and not area.get("archived", False)]
        pillar_response.area_count = len(pillar_areas)
        
        if not pillar_areas:
            # No areas, set defaults
            pillar_response.project_count = 0
            pillar_response.task_count = 0
            pillar_response.completed_task_count = 0
            pillar_response.progress_percentage = 0
            if include_areas:
                pillar_response.areas = []
            return pillar_response
        
        # Calculate stats using in-memory data processing
        total_projects = 0
        total_tasks = 0
        completed_tasks = 0
        area_responses = []
        
        for area_doc in pillar_areas:
            # Get projects for this area (in-memory filter)
            area_projects = [p for p in projects if p.get('area_id') == area_doc['id'] and not p.get("archived", False)]
            
            # Build area response with batch data
            area_response = OptimizedAreaService._build_area_response_optimized(
                area_doc, area_projects, tasks, include_projects=True
            )
            
            # Aggregate stats
            total_projects += area_response.project_count
            total_tasks += area_response.total_task_count
            completed_tasks += area_response.completed_task_count
            
            if include_areas:
                area_responses.append(area_response)
        
        # Set pillar totals
        pillar_response.project_count = total_projects
        pillar_response.task_count = total_tasks
        pillar_response.completed_task_count = completed_tasks
        pillar_response.progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        if include_areas:
            pillar_response.areas = area_responses
        
        return pillar_response

class OptimizedAreaService:
    """
    REFACTORED Area Service - No service-to-service calls
    Uses Repository Pattern for all data access
    """
    
    @staticmethod
    @track_endpoint_performance("areas.get_user_areas")
    async def get_user_areas(user_id: str, include_projects: bool = False, include_archived: bool = False) -> List[AreaResponse]:
        """
        Get user areas with optimized single-batch data fetching  
        NO service-to-service calls, NO N+1 queries
        """
        logger.info(f"OptimizedAreaService: Getting areas for user {user_id} (include_projects: {include_projects})")
        
        # Get repository for this request
        repo = RepositoryManager.get_repository(user_id)
        
        # Single batch operation - fetches ALL data at once
        areas = await repo.get_areas(include_archived=include_archived)
        
        if not areas:
            logger.info(f"OptimizedAreaService: No areas found for user {user_id}")
            return []
        
        if include_projects:
            # Get all data in single batch operation  
            all_data = await repo.get_all_user_data()
            pillars = all_data['pillars']
            projects = all_data['projects']
            tasks = all_data['tasks']
            
            # Process areas with batch-fetched data (NO individual queries)
            return [
                OptimizedAreaService._build_area_response_optimized(
                    area, projects, tasks, include_projects=True, pillars=pillars
                )
                for area in areas
            ]
        else:
            # Simple area responses without nested data
            return [AreaResponse(**area) for area in areas]
    
    @staticmethod
    def _build_area_response_optimized(
        area_doc: dict,
        projects: List[dict],
        tasks: List[dict], 
        include_projects: bool = False,
        pillars: List[dict] = None
    ) -> AreaResponse:
        """
        Build area response using pre-fetched batch data
        NO database calls, NO service calls - pure data processing  
        """
        area_response = AreaResponse(**area_doc)
        
        # Get pillar name from batch data (if available)
        if area_response.pillar_id and pillars:
            pillar = next((p for p in pillars if p['id'] == area_response.pillar_id), None)
            area_response.pillar_name = pillar['name'] if pillar else None
        
        # Filter projects for this area (in-memory operation)
        area_projects = [p for p in projects if p.get('area_id') == area_response.id and not p.get("archived", False)]
        
        if include_projects:
            # Build project responses with task counts from batch data
            project_responses = []
            
            for project_doc in area_projects:
                project_response = OptimizedProjectService._build_project_response_optimized(
                    project_doc, tasks
                )
                project_responses.append(project_response)
            
            area_response.projects = project_responses
            area_response.project_count = len(project_responses)
            area_response.completed_project_count = len([p for p in project_responses if p.status == "Completed"])
            
            # Calculate task counts from project data
            total_tasks = sum([p.task_count or 0 for p in project_responses])
            completed_tasks = sum([p.completed_task_count or 0 for p in project_responses])
            area_response.total_task_count = total_tasks
            area_response.completed_task_count = completed_tasks
        else:
            # Set basic counts without nested projects
            area_response.project_count = len(area_projects)
            area_response.completed_project_count = len([p for p in area_projects if p.get("status") == "Completed"])
            area_response.total_task_count = 0  # Not calculated without include_projects
            area_response.completed_task_count = 0
        
        return area_response

class OptimizedProjectService:
    """
    REFACTORED Project Service - No service-to-service calls
    Uses Repository Pattern for all data access
    """
    
    @staticmethod
    @track_endpoint_performance("projects.get_user_projects")
    async def get_user_projects(user_id: str, area_id: str = None, include_archived: bool = False) -> List[ProjectResponse]:
        """
        Get user projects with optimized single-batch data fetching
        NO service-to-service calls, NO N+1 queries
        """
        logger.info(f"OptimizedProjectService: Getting projects for user {user_id} (area_id: {area_id})")
        
        # Get repository for this request
        repo = RepositoryManager.get_repository(user_id)
        
        # Single batch operation
        all_data = await repo.get_all_user_data()
        projects = all_data['projects']
        tasks = all_data['tasks']
        areas = all_data['areas']
        
        # Filter projects
        if area_id:
            projects = [p for p in projects if p.get('area_id') == area_id]
        
        if not include_archived:
            projects = [p for p in projects if not p.get("archived", False)]
        
        projects.sort(key=lambda x: x.get("sort_order", 0))
        
        # Build responses with batch data
        return [
            OptimizedProjectService._build_project_response_optimized(project, tasks, areas)
            for project in projects
        ]
    
    @staticmethod
    def _build_project_response_optimized(
        project_doc: dict,
        tasks: List[dict],
        areas: List[dict] = None
    ) -> ProjectResponse:
        """
        Build project response using pre-fetched batch data
        NO database calls - pure data processing
        """
        project_response = ProjectResponse(**project_doc)
        
        # Get tasks for this project (in-memory filter)
        project_tasks = [t for t in tasks if t.get('project_id') == project_response.id]
        
        # Calculate task statistics
        project_response.task_count = len(project_tasks)
        project_response.completed_task_count = len([t for t in project_tasks if t.get("status") == "completed"])
        project_response.active_task_count = project_response.task_count - project_response.completed_task_count
        
        # Calculate completion percentage
        if project_response.task_count > 0:
            completion_rate = (project_response.completed_task_count / project_response.task_count) * 100
            project_response.completion_percentage = round(completion_rate, 1)
        else:
            project_response.completion_percentage = 0.0
        
        # Get area name from batch data (if available)
        if project_response.area_id and areas:
            area = next((a for a in areas if a['id'] == project_response.area_id), None)
            project_response.area_name = area['name'] if area else None
        
        # Check if overdue
        if project_response.deadline and project_response.status != "Completed":
            project_response.is_overdue = project_response.deadline < datetime.utcnow()
        
        return project_response

class OptimizedStatsService:
    """
    REFACTORED Stats Service - Optimized dashboard data
    Uses Repository Pattern for all data access
    """
    
    @staticmethod
    @track_endpoint_performance("stats.get_dashboard_data")
    async def get_dashboard_data(user_id: str) -> UserDashboard:
        """
        Get dashboard data with single batch operation
        NO N+1 queries, NO service calls
        """
        logger.info(f"OptimizedStatsService: Getting dashboard data for user {user_id}")
        
        # Get repository for this request
        repo = RepositoryManager.get_repository(user_id)
        
        # Single batch operation gets ALL data
        all_data = await repo.get_all_user_data()
        
        # Get user
        users = all_data['users']
        user = users[0] if users else None
        if not user:
            raise ValueError("User not found")
        user_obj = User(**user)
        
        # Calculate stats from batch data
        tasks = all_data['tasks']
        projects = all_data['projects']
        areas = all_data['areas']
        
        # Build user stats
        stats_data = {
            "user_id": user_id,
            "total_areas": len([a for a in areas if not a.get("archived", False)]),
            "total_projects": len([p for p in projects if not p.get("archived", False)]),
            "completed_projects": len([p for p in projects if p.get("status") == "Completed"]),
            "total_tasks": len(tasks),
            "tasks_completed": len([t for t in tasks if t.get("status") == "completed"]),
            "total_journal_entries": 0,  # Would need journal data
            "courses_enrolled": 0,
            "courses_completed": 0,
            "badges_earned": 0
        }
        stats = UserStats(**stats_data)
        
        # Get recent tasks (limit to 5 for performance)
        recent_tasks = sorted(tasks, key=lambda x: x.get("created_at", ""), reverse=True)[:5]
        recent_task_responses = [TaskResponse(**task) for task in recent_tasks]
        
        return UserDashboard(
            user=user_obj,
            stats=stats,
            recent_tasks=recent_task_responses,
            recent_courses=[],
            recent_achievements=[],
            areas=[],  # Skip areas for dashboard speed
            today_tasks=[]
        )