"""
Repository Pattern Implementation
Provides centralized data access with request-scoped caching to eliminate N+1 queries
Following industry standard architectural patterns
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import logging
from supabase_client import find_documents, find_document

logger = logging.getLogger(__name__)

class DataRepository:
    """
    Centralized repository for all data access operations
    Implements request-scoped caching to eliminate N+1 queries
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self._cache: Dict[str, Any] = {}
        self._loading: Dict[str, asyncio.Future] = {}
    
    async def get_all_user_data(self) -> Dict[str, List[Dict]]:
        """
        Fetch ALL user data in parallel (single batch operation)
        This is the core method that eliminates N+1 queries
        """
        if 'all_data' in self._cache:
            return self._cache['all_data']
        
        if 'all_data' in self._loading:
            return await self._loading['all_data']
        
        # Create future for concurrent requests
        future = asyncio.Future()
        self._loading['all_data'] = future
        
        try:
            logger.info(f"Repository: Fetching ALL user data for {self.user_id} (batch operation)")
            
            # Fetch ALL user data in parallel - single database round-trip
            tasks = await asyncio.gather(
                find_documents("users", {"id": self.user_id}),
                find_documents("pillars", {"user_id": self.user_id}),
                find_documents("areas", {"user_id": self.user_id}),  
                find_documents("projects", {"user_id": self.user_id}),
                find_documents("tasks", {"user_id": self.user_id}),
                return_exceptions=True
            )
            
            # Process results with error handling
            users, pillars, areas, projects, task_results = tasks
            
            # Handle exceptions gracefully
            for i, result in enumerate(tasks):
                if isinstance(result, Exception):
                    logger.warning(f"Repository: Query {i} failed: {result}")
                    tasks[i] = []
            
            all_data = {
                'users': users if not isinstance(users, Exception) else [],
                'pillars': pillars if not isinstance(pillars, Exception) else [],
                'areas': areas if not isinstance(areas, Exception) else [],
                'projects': projects if not isinstance(projects, Exception) else [],
                'tasks': task_results if not isinstance(task_results, Exception) else []
            }
            
            # Cache the result
            self._cache['all_data'] = all_data
            future.set_result(all_data)
            
            logger.info(f"Repository: Cached {len(pillars)} pillars, {len(areas)} areas, {len(projects)} projects, {len(task_results)} tasks")
            return all_data
            
        except Exception as e:
            logger.error(f"Repository: Failed to fetch user data: {e}")
            # Return empty structure on error
            empty_data = {
                'users': [], 'pillars': [], 'areas': [], 'projects': [], 'tasks': []
            }
            future.set_result(empty_data)
            return empty_data
        finally:
            if 'all_data' in self._loading:
                del self._loading['all_data']
    
    async def get_user(self) -> Optional[Dict]:
        """Get user with caching"""
        data = await self.get_all_user_data()
        users = data['users']
        return users[0] if users else None
    
    async def get_pillars(self, include_archived: bool = False) -> List[Dict]:
        """Get pillars with caching"""
        data = await self.get_all_user_data()
        pillars = data['pillars']
        
        if not include_archived:
            pillars = [p for p in pillars if not p.get("archived", False)]
        
        return sorted(pillars, key=lambda x: x.get("sort_order", 0))
    
    async def get_areas(self, include_archived: bool = False) -> List[Dict]:
        """Get areas with caching"""
        data = await self.get_all_user_data()
        areas = data['areas']
        
        if not include_archived:
            areas = [a for a in areas if not a.get("archived", False)]
        
        return sorted(areas, key=lambda x: x.get("sort_order", 0))
    
    async def get_projects(self, include_archived: bool = False) -> List[Dict]:
        """Get projects with caching"""
        data = await self.get_all_user_data()
        projects = data['projects']
        
        if not include_archived:
            projects = [p for p in projects if not p.get("archived", False)]
        
        return sorted(projects, key=lambda x: x.get("sort_order", 0))
    
    async def get_tasks(self) -> List[Dict]:
        """Get tasks with caching"""
        data = await self.get_all_user_data()
        return data['tasks']
    
    def get_areas_by_pillar_id(self, pillar_id: str, areas: List[Dict] = None) -> List[Dict]:
        """Get areas for a specific pillar (from cached data)"""
        if areas is None:
            # This should only be called after get_all_user_data()
            areas = self._cache.get('all_data', {}).get('areas', [])
        
        return [area for area in areas if area.get('pillar_id') == pillar_id]
    
    def get_projects_by_area_id(self, area_id: str, projects: List[Dict] = None) -> List[Dict]:
        """Get projects for a specific area (from cached data)"""
        if projects is None:
            projects = self._cache.get('all_data', {}).get('projects', [])
        
        return [project for project in projects if project.get('area_id') == area_id]
    
    def get_tasks_by_project_id(self, project_id: str, tasks: List[Dict] = None) -> List[Dict]:
        """Get tasks for a specific project (from cached data)"""
        if tasks is None:
            tasks = self._cache.get('all_data', {}).get('tasks', [])
        
        return [task for task in tasks if task.get('project_id') == project_id]
    
    def get_pillar_by_id(self, pillar_id: str, pillars: List[Dict] = None) -> Optional[Dict]:
        """Get pillar by ID (from cached data)"""
        if pillars is None:
            pillars = self._cache.get('all_data', {}).get('pillars', [])
        
        return next((p for p in pillars if p.get('id') == pillar_id), None)
    
    def clear_cache(self):
        """Clear the cache (for testing or cache invalidation)"""
        self._cache.clear()
        self._loading.clear()

class RepositoryManager:
    """
    Manages repository instances per request
    Implements request-scoped pattern
    """
    
    _repositories: Dict[str, DataRepository] = {}
    
    @classmethod  
    def get_repository(cls, user_id: str) -> DataRepository:
        """Get or create repository for user (request-scoped)"""
        if user_id not in cls._repositories:
            cls._repositories[user_id] = DataRepository(user_id)
        return cls._repositories[user_id]
    
    @classmethod
    def clear_repository(cls, user_id: str):
        """Clear repository for user (end of request)"""
        if user_id in cls._repositories:
            cls._repositories[user_id].clear_cache()
            del cls._repositories[user_id]
    
    @classmethod
    def clear_all_repositories(cls):
        """Clear all repositories (for testing)"""
        cls._repositories.clear()