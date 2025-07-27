"""
Optimized Database Queries for Aurum Life MVP v1.2
Implements efficient PostgreSQL queries with proper joins and indexing
"""

from typing import List, Dict, Optional
from datetime import datetime
from supabase import Client
from config import settings
import logging

logger = logging.getLogger(__name__)

class OptimizedQueryService:
    """
    Service for executing optimized database queries
    All queries are designed to complete in <150ms with proper indexes
    """
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
        
    async def get_user_hierarchy(self, user_id: str) -> Dict:
        """
        Get complete user hierarchy in a single optimized query
        Uses PostgreSQL function for maximum performance
        """
        try:
            # Call optimized stored procedure
            response = await self.client.rpc(
                'get_user_hierarchy_optimized',
                {'p_user_id': user_id}
            ).execute()
            
            if response.data:
                return {
                    'pillars': response.data,
                    'total_tasks': sum(
                        task['count'] 
                        for pillar in response.data 
                        for area in pillar.get('areas', [])
                        for project in area.get('projects', [])
                        for task in [project.get('task_stats', {})]
                    ),
                    'query_time_ms': response.execution_time if hasattr(response, 'execution_time') else 0
                }
            
            return {'pillars': [], 'total_tasks': 0}
            
        except Exception as e:
            logger.error(f"Failed to get user hierarchy: {e}")
            return {'pillars': [], 'total_tasks': 0, 'error': str(e)}
    
    async def get_today_tasks_optimized(self, user_id: str) -> List[Dict]:
        """
        Get today's tasks with hierarchy info in a single query
        Optimized for the Today view
        """
        try:
            # Use raw SQL for maximum performance
            query = """
            SELECT 
                t.id,
                t.name,
                t.description,
                t.priority,
                t.due_date,
                t.due_time,
                t.completed,
                t.current_score,
                t.estimated_duration,
                p.id as project_id,
                p.name as project_name,
                p.icon as project_icon,
                a.id as area_id,
                a.name as area_name,
                a.icon as area_icon,
                pi.id as pillar_id,
                pi.name as pillar_name,
                pi.icon as pillar_icon
            FROM tasks t
            INNER JOIN projects p ON t.project_id = p.id
            INNER JOIN areas a ON p.area_id = a.id
            INNER JOIN pillars pi ON a.pillar_id = pi.id
            WHERE 
                t.user_id = %s
                AND t.completed = false
                AND (t.due_date <= CURRENT_DATE + INTERVAL '1 day' OR t.due_date IS NULL)
            ORDER BY t.current_score DESC
            LIMIT 50
            """
            
            response = await self.client.from_('tasks').select(
                """
                id, name, description, priority, due_date, due_time,
                completed, current_score, estimated_duration,
                projects!inner(
                    id, name, icon,
                    areas!inner(
                        id, name, icon,
                        pillars!inner(id, name, icon)
                    )
                )
                """
            ).eq('user_id', user_id).eq('completed', False).or_(
                f"due_date.lte.{datetime.utcnow().date()},due_date.is.null"
            ).order('current_score', desc=True).limit(50).execute()
            
            # Transform nested structure to flat structure
            tasks = []
            for task in response.data:
                project = task.pop('projects', {})
                area = project.pop('areas', {})
                pillar = area.pop('pillars', {})
                
                tasks.append({
                    **task,
                    'project_id': project.get('id'),
                    'project_name': project.get('name'),
                    'project_icon': project.get('icon'),
                    'area_id': area.get('id'),
                    'area_name': area.get('name'),
                    'area_icon': area.get('icon'),
                    'pillar_id': pillar.get('id'),
                    'pillar_name': pillar.get('name'),
                    'pillar_icon': pillar.get('icon'),
                })
            
            return tasks
            
        except Exception as e:
            logger.error(f"Failed to get today tasks: {e}")
            return []
    
    async def get_pillar_with_stats(self, user_id: str, pillar_id: str) -> Dict:
        """
        Get a single pillar with all statistics in one query
        """
        try:
            response = await self.client.rpc(
                'get_pillar_stats',
                {
                    'p_user_id': user_id,
                    'p_pillar_id': pillar_id
                }
            ).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get pillar stats: {e}")
            return None
    
    async def batch_update_task_scores(self, task_scores: List[Dict[str, float]]) -> bool:
        """
        Batch update task scores for performance
        """
        try:
            # Prepare batch update data
            updates = [
                {
                    'id': task_id,
                    'current_score': score,
                    'score_last_updated': datetime.utcnow()
                }
                for task_id, score in task_scores
            ]
            
            # Use upsert for batch update
            response = await self.client.from_('tasks').upsert(
                updates,
                on_conflict='id'
            ).execute()
            
            return len(response.data) == len(updates)
            
        except Exception as e:
            logger.error(f"Failed to batch update scores: {e}")
            return False

# PostgreSQL Functions to create in Supabase
OPTIMIZED_FUNCTIONS = """
-- Optimized function to get user hierarchy with stats
CREATE OR REPLACE FUNCTION get_user_hierarchy_optimized(p_user_id UUID)
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_agg(pillar_data) INTO result
    FROM (
        SELECT 
            p.id,
            p.name,
            p.description,
            p.icon,
            p.color,
            p.time_allocation_percentage,
            p.archived,
            p.created_at,
            (
                SELECT json_agg(area_data)
                FROM (
                    SELECT 
                        a.id,
                        a.name,
                        a.description,
                        a.icon,
                        a.color,
                        a.archived,
                        (
                            SELECT json_agg(project_data)
                            FROM (
                                SELECT 
                                    pr.id,
                                    pr.name,
                                    pr.description,
                                    pr.icon,
                                    pr.status,
                                    pr.priority,
                                    pr.deadline,
                                    pr.completion_percentage,
                                    (
                                        SELECT json_build_object(
                                            'total', COUNT(*),
                                            'completed', COUNT(*) FILTER (WHERE completed = true),
                                            'overdue', COUNT(*) FILTER (WHERE completed = false AND due_date < CURRENT_DATE)
                                        )
                                        FROM tasks t
                                        WHERE t.project_id = pr.id
                                    ) as task_stats
                                FROM projects pr
                                WHERE pr.area_id = a.id
                                    AND pr.archived = false
                                ORDER BY pr.sort_order, pr.created_at
                            ) project_data
                        ) as projects
                    FROM areas a
                    WHERE a.pillar_id = p.id
                        AND a.archived = false
                    ORDER BY a.sort_order, a.created_at
                ) area_data
            ) as areas
        FROM pillars p
        WHERE p.user_id = p_user_id::text
            AND p.archived = false
        ORDER BY p.sort_order, p.created_at
    ) pillar_data;
    
    RETURN COALESCE(result, '[]'::JSON);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get pillar statistics
CREATE OR REPLACE FUNCTION get_pillar_stats(p_user_id UUID, p_pillar_id UUID)
RETURNS TABLE (
    id UUID,
    name TEXT,
    description TEXT,
    icon TEXT,
    color TEXT,
    area_count BIGINT,
    project_count BIGINT,
    task_count BIGINT,
    completed_task_count BIGINT,
    progress_percentage NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id::UUID,
        p.name,
        p.description,
        p.icon,
        p.color,
        COUNT(DISTINCT a.id) as area_count,
        COUNT(DISTINCT pr.id) as project_count,
        COUNT(DISTINCT t.id) as task_count,
        COUNT(DISTINCT t.id) FILTER (WHERE t.completed = true) as completed_task_count,
        CASE 
            WHEN COUNT(DISTINCT t.id) > 0 
            THEN ROUND((COUNT(DISTINCT t.id) FILTER (WHERE t.completed = true)::NUMERIC / COUNT(DISTINCT t.id)) * 100, 2)
            ELSE 0
        END as progress_percentage
    FROM pillars p
    LEFT JOIN areas a ON a.pillar_id = p.id AND a.archived = false
    LEFT JOIN projects pr ON pr.area_id = a.id AND pr.archived = false
    LEFT JOIN tasks t ON t.project_id = pr.id
    WHERE p.id = p_pillar_id::text
        AND p.user_id = p_user_id::text
    GROUP BY p.id, p.name, p.description, p.icon, p.color;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create indexes for optimal performance
CREATE INDEX IF NOT EXISTS idx_tasks_user_completed_score 
    ON tasks(user_id, completed, current_score DESC);
    
CREATE INDEX IF NOT EXISTS idx_tasks_due_date_score 
    ON tasks(due_date, current_score DESC) 
    WHERE completed = false;

CREATE INDEX IF NOT EXISTS idx_projects_area_archived 
    ON projects(area_id, archived);
    
CREATE INDEX IF NOT EXISTS idx_areas_pillar_archived 
    ON areas(pillar_id, archived);
"""