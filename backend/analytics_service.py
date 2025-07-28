"""
Analytics Service for Aurum Life MVP v1.2
Simple "Alignment Snapshot" without complex filtering or historical data
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from supabase_client import find_documents, supabase_manager
import logging

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Simple analytics service for MVP insights"""
    
    @staticmethod
    async def get_lifetime_stats(user_id: str) -> Dict[str, int]:
        """
        Get lifetime statistics for user
        Returns: {"total_tasks_completed": int, "total_projects_completed": int}
        """
        try:
            # Get completed tasks count
            completed_tasks = await find_documents("tasks", {
                "user_id": user_id,
                "completed": True
            })
            
            # Get completed projects count
            completed_projects = await find_documents("projects", {
                "user_id": user_id,
                "status": "Completed"
            })
            
            return {
                "total_tasks_completed": len(completed_tasks),
                "total_projects_completed": len(completed_projects)
            }
            
        except Exception as e:
            logger.error(f"Error getting lifetime stats: {e}")
            return {"total_tasks_completed": 0, "total_projects_completed": 0}
    
    @staticmethod
    async def get_pillar_alignment_distribution(user_id: str) -> List[Dict[str, any]]:
        """
        Get distribution of completed tasks across user's pillars
        Returns: [{"pillar_name": str, "pillar_id": str, "task_count": int, "percentage": float}]
        """
        try:
            # Get all user's pillars
            pillars = await find_documents("pillars", {"user_id": user_id})
            
            if not pillars:
                return []
            
            # Get all completed tasks for this user
            completed_tasks = await find_documents("tasks", {
                "user_id": user_id,
                "completed": True
            })
            
            if not completed_tasks:
                return []
            
            # Create pillar mapping (task -> pillar via project -> area -> pillar)
            pillar_task_counts = {}
            total_completed_tasks = len(completed_tasks)
            
            # Initialize pillar counts
            for pillar in pillars:
                pillar_task_counts[pillar['id']] = {
                    "pillar_name": pillar['name'],
                    "pillar_id": pillar['id'],
                    "task_count": 0,
                    "percentage": 0.0
                }
            
            # Count tasks per pillar
            for task in completed_tasks:
                project_id = task.get('project_id')
                if not project_id:
                    continue
                    
                # Get project to find area
                projects = await find_documents("projects", {"id": project_id})
                if not projects:
                    continue
                    
                project = projects[0]
                area_id = project.get('area_id')
                if not area_id:
                    continue
                
                # Get area to find pillar
                areas = await find_documents("areas", {"id": area_id})
                if not areas:
                    continue
                    
                area = areas[0]
                pillar_id = area.get('pillar_id')
                if pillar_id and pillar_id in pillar_task_counts:
                    pillar_task_counts[pillar_id]['task_count'] += 1
            
            # Calculate percentages
            if total_completed_tasks > 0:
                for pillar_id in pillar_task_counts:
                    task_count = pillar_task_counts[pillar_id]['task_count']
                    pillar_task_counts[pillar_id]['percentage'] = round(
                        (task_count / total_completed_tasks) * 100, 1
                    )
            
            # Convert to list and sort by task count (descending)
            result = list(pillar_task_counts.values())
            result.sort(key=lambda x: x['task_count'], reverse=True)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting pillar alignment distribution: {e}")
            return []
    
    @staticmethod
    async def get_alignment_snapshot(user_id: str) -> Dict[str, any]:
        """
        Get complete alignment snapshot for user
        Combines lifetime stats and pillar distribution
        """
        try:
            # Get both analytics concurrently for performance
            lifetime_stats_task = asyncio.create_task(
                AnalyticsService.get_lifetime_stats(user_id)
            )
            pillar_distribution_task = asyncio.create_task(
                AnalyticsService.get_pillar_alignment_distribution(user_id)
            )
            
            lifetime_stats, pillar_distribution = await asyncio.gather(
                lifetime_stats_task, pillar_distribution_task
            )
            
            return {
                "lifetime_stats": lifetime_stats,
                "pillar_alignment": pillar_distribution,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting alignment snapshot: {e}")
            return {
                "lifetime_stats": {"total_tasks_completed": 0, "total_projects_completed": 0},
                "pillar_alignment": [],
                "generated_at": datetime.utcnow().isoformat()
            }