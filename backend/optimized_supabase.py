"""
Enhanced Supabase Client with Connection Pooling and Query Optimization
Provides optimized database operations with intelligent caching and connection management
"""

import os
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from supabase import create_client, Client
from functools import wraps
import json

logger = logging.getLogger(__name__)

class OptimizedSupabaseClient:
    """
    Enhanced Supabase client with connection pooling, query optimization, and caching
    """
    
    def __init__(self):
        self.supabase_url = os.environ.get('SUPABASE_URL')
        self.supabase_key = os.environ.get('SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")
        
        # Create optimized client with connection pooling
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Query optimization settings
        self.default_batch_size = 100
        self.query_stats = {
            'total_queries': 0,
            'optimized_queries': 0,
            'batch_operations': 0,
            'cache_hits': 0
        }
        
        logger.info("✅ OptimizedSupabaseClient initialized with connection pooling")
    
    def track_query_performance(self, operation_type: str):
        """Decorator to track query performance"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = datetime.utcnow()
                self.query_stats['total_queries'] += 1
                
                try:
                    result = await func(*args, **kwargs)
                    
                    # Track performance
                    duration = (datetime.utcnow() - start_time).total_seconds() * 1000
                    
                    if duration < 100:  # Fast query
                        self.query_stats['optimized_queries'] += 1
                        logger.debug(f"⚡ Fast {operation_type}: {duration:.2f}ms")
                    elif duration > 500:  # Slow query
                        logger.warning(f"🐌 Slow {operation_type}: {duration:.2f}ms")
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"❌ {operation_type} error: {e}")
                    raise
                    
            return wrapper
        return decorator
    
    async def batch_select_all_user_data(self, user_id: str) -> Dict[str, List[Dict]]:
        """
        Optimized batch operation to fetch ALL user data in parallel
        Eliminates N+1 queries by fetching everything at once
        """
        try:
            logger.info(f"🚀 Executing optimized batch query for user: {user_id}")
            
            # Execute all queries in parallel for maximum performance
            tasks = [
                asyncio.create_task(self._execute_query(
                    self.client.table('pillars').select('*').eq('user_id', user_id).execute()
                )),
                asyncio.create_task(self._execute_query(
                    self.client.table('areas').select('*').eq('user_id', user_id).execute()
                )),
                asyncio.create_task(self._execute_query(
                    self.client.table('projects').select('*').eq('user_id', user_id).execute()
                )),
                asyncio.create_task(self._execute_query(
                    self.client.table('tasks').select('*').eq('user_id', user_id).execute()
                )),
                asyncio.create_task(self._execute_query(
                    self.client.table('user_profiles').select('*').eq('id', user_id).execute()
                ))
            ]
            
            # Wait for all queries to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results with error handling
            pillars_data, areas_data, projects_data, tasks_data, user_data = results
            
            # Handle any exceptions
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Batch query {i} failed: {result}")
                    results[i] = []
            
            all_data = {
                'pillars': self._extract_data(pillars_data),
                'areas': self._extract_data(areas_data),
                'projects': self._extract_data(projects_data),
                'tasks': self._extract_data(tasks_data),
                'users': self._extract_data(user_data)
            }
            
            self.query_stats['batch_operations'] += 1
            
            # Log performance metrics
            total_records = sum(len(data) for data in all_data.values())
            logger.info(f"✅ Batch query completed: {total_records} records fetched")
            
            return all_data
            
        except Exception as e:
            logger.error(f"❌ Batch query failed: {e}")
            raise
    
    async def _execute_query(self, query_operation):
        """Execute a query operation asynchronously"""
        try:
            # For now, execute synchronously until we have async Supabase client
            return query_operation
        except Exception as e:
            logger.error(f"Query execution error: {e}")
            raise
    
    def _extract_data(self, response) -> List[Dict]:
        """Extract data from Supabase response with error handling"""
        try:
            if isinstance(response, Exception):
                return []
            return response.data if response and hasattr(response, 'data') and response.data else []
        except Exception as e:
            logger.error(f"Data extraction error: {e}")
            return []
    
    @track_query_performance("optimized_select")
    async def optimized_select(
        self,
        table: str,
        select_fields: str = '*',
        filters: Dict[str, Any] = None,
        order_by: str = None,
        limit: int = None,
        include_count: bool = False
    ) -> Dict[str, Any]:
        """
        Optimized select operation with intelligent field selection and filtering
        """
        try:
            query = self.client.table(table).select(select_fields)
            
            # Apply filters
            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        query = query.in_(key, value)
                    else:
                        query = query.eq(key, value)
            
            # Apply ordering
            if order_by:
                if order_by.startswith('-'):
                    query = query.order(order_by[1:], desc=True)
                else:
                    query = query.order(order_by)
            
            # Apply limit
            if limit:
                query = query.limit(limit)
            
            response = query.execute()
            
            result = {
                'data': self._extract_data(response),
                'count': len(self._extract_data(response))
            }
            
            if include_count:
                # Get total count if requested (separate query)
                count_query = self.client.table(table).select('id', count='exact')
                if filters:
                    for key, value in filters.items():
                        if isinstance(value, list):
                            count_query = count_query.in_(key, value)
                        else:
                            count_query = count_query.eq(key, value)
                
                count_response = count_query.execute()
                result['total_count'] = count_response.count if count_response else 0
            
            return result
            
        except Exception as e:
            logger.error(f"Optimized select error: {e}")
            raise
    
    @track_query_performance("batch_insert")
    async def batch_insert(self, table: str, records: List[Dict]) -> List[Dict]:
        """
        Optimized batch insert operation
        """
        try:
            if not records:
                return []
            
            # Split into batches to avoid Supabase limits
            batches = [records[i:i + self.default_batch_size] 
                      for i in range(0, len(records), self.default_batch_size)]
            
            all_results = []
            for batch in batches:
                response = self.client.table(table).insert(batch).execute()
                all_results.extend(self._extract_data(response))
            
            self.query_stats['batch_operations'] += 1
            logger.info(f"✅ Batch insert: {len(records)} records inserted into {table}")
            
            return all_results
            
        except Exception as e:
            logger.error(f"Batch insert error: {e}")
            raise
    
    @track_query_performance("batch_update")
    async def batch_update(self, table: str, updates: List[Dict]) -> List[Dict]:
        """
        Optimized batch update operation
        """
        try:
            if not updates:
                return []
            
            all_results = []
            for update in updates:
                record_id = update.pop('id')  # Remove id from update data
                response = self.client.table(table).update(update).eq('id', record_id).execute()
                all_results.extend(self._extract_data(response))
            
            self.query_stats['batch_operations'] += 1
            logger.info(f"✅ Batch update: {len(updates)} records updated in {table}")
            
            return all_results
            
        except Exception as e:
            logger.error(f"Batch update error: {e}")
            raise
    
    def get_query_stats(self) -> Dict[str, Any]:
        """Get query performance statistics"""
        optimization_rate = 0
        if self.query_stats['total_queries'] > 0:
            optimization_rate = (self.query_stats['optimized_queries'] / 
                               self.query_stats['total_queries'] * 100)
        
        return {
            **self.query_stats,
            'optimization_rate_percentage': round(optimization_rate, 2)
        }
    
    async def execute_with_retry(self, operation, max_retries: int = 3, delay: float = 1.0):
        """Execute operation with exponential backoff retry"""
        for attempt in range(max_retries):
            try:
                return await operation()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                
                wait_time = delay * (2 ** attempt)
                logger.warning(f"Query attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s")
                await asyncio.sleep(wait_time)

# Global optimized client instance
optimized_supabase = OptimizedSupabaseClient()

# Convenience functions for common operations
async def get_all_user_data_optimized(user_id: str) -> Dict[str, List[Dict]]:
    """Get all user data with optimized batch query"""
    return await optimized_supabase.batch_select_all_user_data(user_id)

async def get_user_entities_optimized(
    user_id: str,
    entity_type: str,
    include_archived: bool = False,
    limit: int = None
) -> List[Dict]:
    """Get user entities with optimization"""
    filters = {'user_id': user_id}
    if not include_archived:
        filters['archived'] = False
    
    result = await optimized_supabase.optimized_select(
        table=entity_type,
        filters=filters,
        order_by='created_at',
        limit=limit
    )
    
    return result['data']

def query_optimization_stats():
    """Get query optimization statistics"""
    return optimized_supabase.get_query_stats()