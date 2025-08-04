"""
Database Query Optimization
Implements database-level optimizations for sub-200ms performance
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
from functools import wraps

logger = logging.getLogger(__name__)

class QueryOptimizer:
    """
    Database query optimization strategies
    """
    
    @staticmethod
    def optimize_user_data_query(user_id: str) -> Dict[str, str]:
        """
        Generate optimized queries with proper indexing hints and field selection
        """
        
        # Only select essential fields to reduce data transfer (fixed to match actual database schema)
        essential_fields = {
            'pillars': 'id, user_id, name, description, color, icon, sort_order, archived, created_at, updated_at, date_created, time_allocation_percentage',
            'areas': 'id, user_id, pillar_id, name, description, color, icon, importance, sort_order, archived, created_at, updated_at, date_created',
            'projects': 'id, user_id, area_id, name, description, status, priority, deadline, archived, sort_order, created_at, updated_at',
            'tasks': 'id, user_id, project_id, name, description, status, priority, due_date, completed, completed_at, sort_order, created_at, updated_at',
            'user_profiles': 'id, username, first_name, last_name, created_at, updated_at, is_active'
        }
        
        return essential_fields
    
    @staticmethod
    def get_optimized_filters(include_archived: bool = False) -> Dict[str, Any]:
        """Get optimized filter conditions"""
        filters = {}
        
        if not include_archived:
            filters['archived'] = False
            
        return filters
    
    @staticmethod
    def get_sort_optimization() -> str:
        """Get optimized sorting strategy"""
        # Use indexed fields for sorting
        return 'sort_order, created_at'

class FastSupabaseClient:
    """
    Ultra-fast Supabase client optimized for sub-200ms performance
    """
    
    def __init__(self):
        from supabase_client import get_supabase_client
        self.client = get_supabase_client()
        self.query_optimizer = QueryOptimizer()
        self._connection_pool = None
        
    async def ultra_fast_user_data_batch(self, user_id: str) -> Dict[str, List[Dict]]:
        """
        Ultra-optimized batch query with connection reuse and minimal data transfer
        Target: <50ms database query time
        """
        try:
            start_time = datetime.utcnow()
            
            # Get optimized field selections
            fields = self.query_optimizer.optimize_user_data_query(user_id)
            
            # Execute optimized parallel queries with minimal field selection
            tasks = []
            
            # Pillars with optimized fields
            pillars_task = asyncio.create_task(
                self._execute_optimized_query('pillars', fields['pillars'], user_id)
            )
            tasks.append(pillars_task)
            
            # Areas with optimized fields  
            areas_task = asyncio.create_task(
                self._execute_optimized_query('areas', fields['areas'], user_id)
            )
            tasks.append(areas_task)
            
            # Projects with optimized fields
            projects_task = asyncio.create_task(
                self._execute_optimized_query('projects', fields['projects'], user_id)
            )
            tasks.append(projects_task)
            
            # Tasks with optimized fields
            tasks_task = asyncio.create_task(
                self._execute_optimized_query('tasks', fields['tasks'], user_id)
            )
            tasks.append(tasks_task)
            
            # User profile with optimized fields
            user_task = asyncio.create_task(
                self._execute_optimized_query('user_profiles', fields['user_profiles'], user_id, user_query=True)
            )
            tasks.append(user_task)
            
            # Wait for all queries to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            pillars, areas, projects, tasks_data, users = results
            
            # Handle exceptions gracefully
            processed_results = {
                'pillars': self._safe_extract_data(pillars),
                'areas': self._safe_extract_data(areas),
                'projects': self._safe_extract_data(projects),
                'tasks': self._safe_extract_data(tasks_data),
                'users': self._safe_extract_data(users)
            }
            
            # Log performance
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger.info(f"⚡ Ultra-fast batch query completed in {duration:.2f}ms")
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Ultra-fast batch query error: {e}")
            # Return empty structure on error
            return {
                'pillars': [], 'areas': [], 'projects': [], 'tasks': [], 'users': []
            }
    
    async def _execute_optimized_query(
        self, 
        table: str, 
        fields: str, 
        user_id: str, 
        user_query: bool = False
    ) -> Any:
        """Execute optimized query with proper indexing"""
        try:
            query = self.client.table(table).select(fields)
            
            # Apply user filter
            if user_query:
                query = query.eq('id', user_id)
            else:
                query = query.eq('user_id', user_id)
            
            # Apply archived filter for better performance
            if table in ['pillars', 'areas', 'projects']:
                query = query.eq('archived', False)
            
            # Apply sorting for consistent results
            query = query.order('sort_order', desc=False).order('created_at', desc=False)
            
            # Execute query
            response = query.execute()
            return response
            
        except Exception as e:
            logger.error(f"Optimized query error for {table}: {e}")
            raise
    
    def _safe_extract_data(self, response) -> List[Dict]:
        """Safely extract data from Supabase response"""
        try:
            if isinstance(response, Exception):
                logger.error(f"Query response is exception: {response}")
                return []
            
            if response and hasattr(response, 'data') and response.data:
                return response.data
            
            return []
            
        except Exception as e:
            logger.error(f"Data extraction error: {e}")
            return []

# Global optimized client
fast_supabase = FastSupabaseClient()

async def get_ultra_fast_user_data(user_id: str) -> Dict[str, List[Dict]]:
    """Get user data with ultra-fast optimization"""
    return await fast_supabase.ultra_fast_user_data_batch(user_id)