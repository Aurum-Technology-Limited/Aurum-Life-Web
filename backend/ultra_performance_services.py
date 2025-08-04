"""
Ultra-High Performance Services Layer
Integrates advanced caching, optimized database operations, and performance monitoring
Target: <200ms response times for all endpoints
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from functools import wraps

# Import our optimization modules
from cache_service import cache_service, cache_dashboard_data, cache_user_projects, cache_user_areas, cache_user_pillars, cache_insights_data
from query_optimizer import get_ultra_fast_user_data
from performance_monitor import track_endpoint_performance

# Import existing models
from models import (
    PillarResponse, AreaResponse, ProjectResponse, TaskResponse,
    User, UserStats, UserDashboard
)

logger = logging.getLogger(__name__)

class UltraPerformanceService:
    """
    Ultra-high performance service layer
    Combines intelligent caching, optimized queries, and performance monitoring
    """
    
    @staticmethod
    def performance_optimized(endpoint_name: str, cache_ttl: int = 300):
        """Combined decorator for performance tracking and caching"""
        def decorator(func):
            @track_endpoint_performance(endpoint_name)
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Enhanced performance logging
                start_time = datetime.utcnow()
                
                try:
                    result = await func(*args, **kwargs)
                    
                    # Log performance achievement
                    duration = (datetime.utcnow() - start_time).total_seconds() * 1000
                    
                    if duration < 200:
                        logger.info(f"🎯 PERFORMANCE TARGET ACHIEVED: {endpoint_name} - {duration:.2f}ms")
                    elif duration < 300:
                        logger.warning(f"⚠️ APPROACHING LIMIT: {endpoint_name} - {duration:.2f}ms")
                    else:
                        logger.error(f"🚨 PERFORMANCE TARGET MISSED: {endpoint_name} - {duration:.2f}ms")
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"❌ Performance service error in {endpoint_name}: {e}")
                    raise
                    
            return wrapper
        return decorator

class UltraPerformancePillarService:
    """Ultra-high performance Pillar service with advanced caching"""
    
    @staticmethod
    @UltraPerformanceService.performance_optimized("pillars.get_user_pillars", cache_ttl=300)
    @cache_user_pillars(ttl_seconds=300)
    async def get_user_pillars(user_id: str, include_areas: bool = False, include_archived: bool = False) -> List[PillarResponse]:
        """
        Ultra-optimized pillar retrieval with multi-level caching
        Target: <150ms response time
        """
        logger.info(f"🚀 UltraPerformancePillarService: Getting pillars for user {user_id}")
        
        try:
            # Get all data in single optimized batch operation
            all_data = await get_ultra_fast_user_data(user_id)
            
            pillars = all_data['pillars']
            
            if not include_archived:
                pillars = [p for p in pillars if not p.get("archived", False)]
            
            if not pillars:
                logger.info(f"No pillars found for user {user_id}")
                return []
            
            # Sort by priority/order
            pillars.sort(key=lambda x: x.get("sort_order", 0))
            
            if include_areas:
                areas = all_data['areas']
                projects = all_data['projects']
                tasks = all_data['tasks']
                
                return [
                    UltraPerformancePillarService._build_pillar_response_ultra_fast(
                        pillar, areas, projects, tasks, include_areas=True
                    )
                    for pillar in pillars
                ]
            else:
                # Simple pillar responses - maximum speed
                return [PillarResponse(**pillar) for pillar in pillars]
                
        except Exception as e:
            logger.error(f"Ultra pillar service error: {e}")
            raise
    
    @staticmethod
    def _build_pillar_response_ultra_fast(
        pillar_doc: dict,
        areas: List[dict],
        projects: List[dict],
        tasks: List[dict],
        include_areas: bool = False
    ) -> PillarResponse:
        """
        Ultra-fast pillar response building with in-memory data processing
        No database calls - pure computational speed
        """
        pillar_response = PillarResponse(**pillar_doc)
        
        # Lightning-fast in-memory filtering
        pillar_areas = [area for area in areas 
                       if area.get('pillar_id') == pillar_response.id and not area.get("archived", False)]
        
        pillar_response.area_count = len(pillar_areas)
        
        if not pillar_areas:
            # Zero-time defaults
            pillar_response.project_count = 0
            pillar_response.task_count = 0
            pillar_response.completed_task_count = 0
            pillar_response.progress_percentage = 0
            if include_areas:
                pillar_response.areas = []
            return pillar_response
        
        # Ultra-fast stats calculation using list comprehensions
        total_projects = 0
        total_tasks = 0
        completed_tasks = 0
        area_responses = []
        
        for area_doc in pillar_areas:
            # Lightning-fast project filtering
            area_projects = [p for p in projects 
                           if p.get('area_id') == area_doc['id'] and not p.get("archived", False)]
            
            # Ultra-fast area response building
            area_response = UltraPerformanceAreaService._build_area_response_ultra_fast(
                area_doc, area_projects, tasks, include_projects=True
            )
            
            # Immediate stats aggregation
            total_projects += area_response.project_count
            total_tasks += area_response.total_task_count
            completed_tasks += area_response.completed_task_count
            
            if include_areas:
                area_responses.append(area_response)
        
        # Set pillar totals with maximum efficiency
        pillar_response.project_count = total_projects
        pillar_response.task_count = total_tasks
        pillar_response.completed_task_count = completed_tasks
        pillar_response.progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        if include_areas:
            pillar_response.areas = area_responses
        
        return pillar_response

class UltraPerformanceAreaService:
    """Ultra-high performance Area service"""
    
    @staticmethod
    @UltraPerformanceService.performance_optimized("areas.get_user_areas", cache_ttl=300)
    @cache_user_areas(ttl_seconds=300)  
    async def get_user_areas(user_id: str, include_projects: bool = False, include_archived: bool = False) -> List[AreaResponse]:
        """
        Ultra-optimized area retrieval 
        Target: <120ms response time
        """
        logger.info(f"🚀 UltraPerformanceAreaService: Getting areas for user {user_id}")
        
        try:
            # Single batch operation for maximum speed
            all_data = await get_ultra_fast_user_data(user_id)
            
            areas = all_data['areas']
            
            if not include_archived:
                areas = [a for a in areas if not a.get("archived", False)]
            
            if not areas:
                return []
            
            # Ultra-fast sorting
            areas.sort(key=lambda x: x.get("sort_order", 0))
            
            if include_projects:
                pillars = all_data['pillars']
                projects = all_data['projects']
                tasks = all_data['tasks']
                
                return [
                    UltraPerformanceAreaService._build_area_response_ultra_fast(
                        area, projects, tasks, include_projects=True, pillars=pillars
                    )
                    for area in areas
                ]
            else:
                return [AreaResponse(**area) for area in areas]
                
        except Exception as e:
            logger.error(f"Ultra area service error: {e}")
            raise
    
    @staticmethod
    def _build_area_response_ultra_fast(
        area_doc: dict,
        projects: List[dict],
        tasks: List[dict],
        include_projects: bool = False,
        pillars: List[dict] = None
    ) -> AreaResponse:
        """Ultra-fast area response building"""
        area_response = AreaResponse(**area_doc)
        
        # Lightning-fast pillar name lookup
        if area_response.pillar_id and pillars:
            pillar = next((p for p in pillars if p['id'] == area_response.pillar_id), None)
            area_response.pillar_name = pillar['name'] if pillar else None
        
        # Ultra-fast project filtering
        area_projects = [p for p in projects 
                        if p.get('area_id') == area_response.id and not p.get("archived", False)]
        
        if include_projects:
            # Build project responses with lightning speed
            project_responses = [
                UltraPerformanceProjectService._build_project_response_ultra_fast(project_doc, tasks)
                for project_doc in area_projects
            ]
            
            area_response.projects = project_responses
            area_response.project_count = len(project_responses)
            area_response.completed_project_count = len([p for p in project_responses if p.status == "Completed"])
            
            # Ultra-fast task count aggregation
            area_response.total_task_count = sum(p.task_count or 0 for p in project_responses)
            area_response.completed_task_count = sum(p.completed_task_count or 0 for p in project_responses)
        else:
            # Minimal processing for maximum speed
            area_response.project_count = len(area_projects)
            area_response.completed_project_count = len([p for p in area_projects if p.get("status") == "Completed"])
            area_response.total_task_count = 0
            area_response.completed_task_count = 0
        
        return area_response

class UltraPerformanceProjectService:
    """Ultra-high performance Project service"""
    
    @staticmethod
    @UltraPerformanceService.performance_optimized("projects.get_user_projects", cache_ttl=300)
    @cache_user_projects(ttl_seconds=300)
    async def get_user_projects(user_id: str, area_id: str = None, include_archived: bool = False) -> List[ProjectResponse]:
        """
        Ultra-optimized project retrieval
        Target: <100ms response time  
        """
        logger.info(f"🚀 UltraPerformanceProjectService: Getting projects for user {user_id}")
        
        try:
            # Lightning-fast batch data retrieval
            all_data = await get_ultra_fast_user_data(user_id)
            
            projects = all_data['projects']
            tasks = all_data['tasks']
            areas = all_data['areas']
            
            # Ultra-fast filtering with list comprehensions
            if area_id:
                projects = [p for p in projects if p.get('area_id') == area_id]
            
            if not include_archived:
                projects = [p for p in projects if not p.get("archived", False)]
            
            # Lightning-fast sorting
            projects.sort(key=lambda x: x.get("sort_order", 0))
            
            # Ultra-fast response building
            return [
                UltraPerformanceProjectService._build_project_response_ultra_fast(project, tasks, areas)
                for project in projects
            ]
            
        except Exception as e:
            logger.error(f"Ultra project service error: {e}")
            raise
    
    @staticmethod
    def _build_project_response_ultra_fast(
        project_doc: dict,
        tasks: List[dict],
        areas: List[dict] = None
    ) -> ProjectResponse:
        """Ultra-fast project response building with maximum computational efficiency"""
        project_response = ProjectResponse(**project_doc)
        
        # Lightning-fast task filtering and counting
        project_tasks = [t for t in tasks if t.get('project_id') == project_response.id]
        
        # Immediate stats calculation
        task_count = len(project_tasks)
        completed_count = len([t for t in project_tasks if t.get("status") == "completed"])
        
        project_response.task_count = task_count
        project_response.completed_task_count = completed_count
        project_response.active_task_count = task_count - completed_count
        
        # Ultra-fast completion percentage
        if task_count > 0:
            project_response.completion_percentage = round((completed_count / task_count) * 100, 1)
        else:
            project_response.completion_percentage = 0.0
        
        # Lightning-fast area name lookup
        if project_response.area_id and areas:
            area = next((a for a in areas if a['id'] == project_response.area_id), None)
            project_response.area_name = area['name'] if area else None
        
        # Instant overdue check
        if project_response.deadline and project_response.status != "Completed":
            try:
                # Handle timezone-aware vs timezone-naive datetime comparison
                now = datetime.utcnow()
                deadline = project_response.deadline
                
                # If deadline is timezone-aware, make now timezone-aware too
                if hasattr(deadline, 'tzinfo') and deadline.tzinfo is not None:
                    from datetime import timezone
                    now = now.replace(tzinfo=timezone.utc)
                # If deadline is timezone-naive but now is timezone-aware, make deadline timezone-aware
                elif hasattr(now, 'tzinfo') and now.tzinfo is not None:
                    deadline = deadline.replace(tzinfo=timezone.utc) if deadline.tzinfo is None else deadline
                
                project_response.is_overdue = deadline < now
            except Exception as e:
                logger.warning(f"Error comparing deadline dates: {e}")
                project_response.is_overdue = False
        
        return project_response

class UltraPerformanceDashboardService:
    """Ultra-high performance Dashboard service"""
    
    @staticmethod
    @UltraPerformanceService.performance_optimized("dashboard.get_dashboard_data", cache_ttl=180)
    @cache_dashboard_data(ttl_seconds=180)
    async def get_dashboard_data(user_id: str) -> UserDashboard:
        """
        Ultra-optimized dashboard data retrieval
        Target: <150ms response time
        """
        logger.info(f"🚀 UltraPerformanceDashboardService: Getting dashboard for user {user_id}")
        
        try:
            # Single lightning-fast batch operation
            all_data = await get_ultra_fast_user_data(user_id)
            
            # Extract data with immediate processing
            users = all_data['users']
            tasks = all_data['tasks']
            projects = all_data['projects']
            areas = all_data['areas']
            
            # Lightning-fast user validation with proper User object creation
            user = users[0] if users else None
            if not user:
                # Fallback: try to get user data from regular service
                from supabase_services import SupabaseUserService
                user_data = await SupabaseUserService.get_user_profile(user_id)
                if not user_data:
                    # Second fallback: try to get from users table (for legacy users)
                    try:
                        from supabase_client import supabase
                        response = supabase.table('users').select('*').eq('id', user_id).single().execute()
                        user_data = response.data
                    except Exception as e:
                        logger.error(f"Failed to get user from users table: {e}")
                        raise ValueError("User not found")
                user = user_data
            
            # Create proper User object with required fields
            user_obj = User(
                id=user.get('id', user_id),
                email='',  # user_profiles table doesn't have email field
                username=user.get('username', ''),
                first_name=user.get('first_name', ''),
                last_name=user.get('last_name', ''),
                has_completed_onboarding=user.get('is_active', True)  # Use is_active as proxy
            )
            
            # Ultra-fast stats calculation with list comprehensions
            stats_data = {
                "user_id": user_id,
                "total_areas": len([a for a in areas if not a.get("archived", False)]),
                "total_projects": len([p for p in projects if not p.get("archived", False)]),
                "completed_projects": len([p for p in projects if p.get("status") == "Completed"]),
                "total_tasks": len(tasks),
                "tasks_completed": len([t for t in tasks if t.get("status") == "completed"]),
                "total_journal_entries": 0,
                "courses_enrolled": 0,
                "courses_completed": 0,
                "badges_earned": 0
            }
            
            stats = UserStats(**stats_data)
            
            # Lightning-fast recent tasks (top 5)
            recent_tasks = sorted(tasks, key=lambda x: x.get("created_at", ""), reverse=True)[:5]
            recent_task_responses = []
            for task in recent_tasks:
                # Map database fields to TaskResponse fields
                task_data = {
                    "id": task.get("id", ""),
                    "user_id": task.get("user_id", ""),
                    "title": task.get("name", ""),  # Map 'name' to 'title'
                    "description": task.get("description", ""),
                    "completed": task.get("status") == "completed",
                    "priority": task.get("priority", "medium"),
                    "due_date": task.get("due_date"),
                    "project_id": task.get("project_id"),
                    "status": task.get("status", "todo"),
                    "created_at": task.get("created_at"),
                    "updated_at": task.get("updated_at")
                }
                recent_task_responses.append(TaskResponse(**task_data))
            
            return UserDashboard(
                user=user_obj,
                stats=stats,
                recent_tasks=recent_task_responses,
                recent_courses=[],
                recent_achievements=[],
                areas=[],
                today_tasks=[]
            )
            
        except Exception as e:
            logger.error(f"Ultra dashboard service error: {e}")
            raise

class UltraPerformanceInsightsService:
    """Ultra-high performance Insights service"""
    
    @staticmethod
    @UltraPerformanceService.performance_optimized("insights.get_comprehensive_insights", cache_ttl=600)
    @cache_insights_data(ttl_seconds=600)
    async def get_comprehensive_insights(user_id: str, date_range: str = "all_time") -> Dict[str, Any]:
        """
        Ultra-optimized insights generation
        Target: <200ms response time
        """
        logger.info(f"🚀 UltraPerformanceInsightsService: Generating insights for user {user_id}")
        
        try:
            # Single ultra-fast batch operation
            all_data = await get_ultra_fast_user_data(user_id)
            
            # Lightning-fast data processing
            tasks = all_data['tasks']
            projects = all_data['projects'] 
            areas = all_data['areas']
            pillars = all_data['pillars']
            
            # Ultra-fast insights calculation
            insights = {
                'overview': {
                    'total_pillars': len([p for p in pillars if not p.get("archived", False)]),
                    'total_areas': len([a for a in areas if not a.get("archived", False)]),
                    'total_projects': len([p for p in projects if not p.get("archived", False)]),
                    'total_tasks': len(tasks),
                    'completed_tasks': len([t for t in tasks if t.get("status") == "completed"]),
                    'completion_rate': 0
                },
                'productivity_trends': [],
                'area_performance': [],
                'recommendations': []
            }
            
            # Lightning-fast completion rate calculation
            if insights['overview']['total_tasks'] > 0:
                insights['overview']['completion_rate'] = round(
                    (insights['overview']['completed_tasks'] / insights['overview']['total_tasks']) * 100, 2
                )
            
            # Ultra-fast area performance analysis
            for area in areas:
                if area.get("archived", False):
                    continue
                    
                area_projects = [p for p in projects if p.get('area_id') == area['id']]
                area_tasks = []
                for project in area_projects:
                    area_tasks.extend([t for t in tasks if t.get('project_id') == project['id']])
                
                if area_tasks:
                    completed_area_tasks = len([t for t in area_tasks if t.get("status") == "completed"])
                    area_completion_rate = (completed_area_tasks / len(area_tasks)) * 100
                    
                    insights['area_performance'].append({
                        'area_name': area['name'],
                        'completion_rate': round(area_completion_rate, 2),
                        'total_tasks': len(area_tasks),
                        'completed_tasks': completed_area_tasks
                    })
            
            # Sort by completion rate for easy analysis
            insights['area_performance'].sort(key=lambda x: x['completion_rate'], reverse=True)
            
            return insights
            
        except Exception as e:
            logger.error(f"Ultra insights service error: {e}")
            raise

# Performance monitoring and stats
def get_ultra_performance_stats():
    """Get comprehensive performance statistics"""
    return {
        'cache_stats': cache_service.get_stats(),
        'timestamp': datetime.utcnow().isoformat()
    }