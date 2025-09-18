"""
Memory-Efficient Data Processing
Optimizes data processing for minimal memory usage and maximum speed
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class MemoryEfficientProcessor:
    """
    Memory-efficient data processing for high-performance operations
    """
    
    @staticmethod
    def process_user_data_ultra_fast(all_data: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        Ultra-fast data processing with minimal memory allocation
        Uses generator expressions and list comprehensions for maximum speed
        """
        try:
            # Extract data arrays
            pillars = all_data.get('pillars', [])
            areas = all_data.get('areas', [])
            projects = all_data.get('projects', [])
            tasks = all_data.get('tasks', [])
            
            # Filter archived items in single pass
            active_pillars = [p for p in pillars if not p.get('archived', False)]
            active_areas = [a for a in areas if not a.get('archived', False)]
            active_projects = [p for p in projects if not p.get('archived', False)]
            
            # Create lookup dictionaries for O(1) access
            pillar_lookup = {p['id']: p for p in active_pillars}
            area_lookup = {a['id']: a for a in active_areas}
            project_lookup = {p['id']: p for p in active_projects}
            
            # Build area-to-pillar mapping
            area_to_pillar = {a['id']: a.get('pillar_id') for a in active_areas}
            
            # Build project-to-area mapping  
            project_to_area = {p['id']: p.get('area_id') for p in active_projects}
            
            # Group tasks by project for O(1) lookup
            tasks_by_project = {}
            for task in tasks:
                project_id = task.get('project_id')
                if project_id:
                    if project_id not in tasks_by_project:
                        tasks_by_project[project_id] = []
                    tasks_by_project[project_id].append(task)
            
            return {
                'active_pillars': active_pillars,
                'active_areas': active_areas,
                'active_projects': active_projects,
                'all_tasks': tasks,
                'lookups': {
                    'pillar_lookup': pillar_lookup,
                    'area_lookup': area_lookup,
                    'project_lookup': project_lookup,
                    'area_to_pillar': area_to_pillar,
                    'project_to_area': project_to_area,
                    'tasks_by_project': tasks_by_project
                }
            }
            
        except Exception as e:
            logger.error(f"Memory-efficient processing error: {e}")
            return {
                'active_pillars': [],
                'active_areas': [],
                'active_projects': [],
                'all_tasks': [],
                'lookups': {}
            }
    
    @staticmethod
    def calculate_stats_ultra_fast(processed_data: Dict[str, Any]) -> Dict[str, int]:
        """
        Ultra-fast statistics calculation using pre-processed data
        """
        try:
            tasks = processed_data.get('all_tasks', [])
            
            # Single-pass statistics calculation
            total_tasks = len(tasks)
            completed_tasks = sum(1 for t in tasks if t.get('status') == 'completed')
            
            return {
                'total_areas': len(processed_data.get('active_areas', [])),
                'total_projects': len(processed_data.get('active_projects', [])),
                'completed_projects': len([p for p in processed_data.get('active_projects', []) 
                                         if p.get('status') == 'Completed']),
                'total_tasks': total_tasks,
                'tasks_completed': completed_tasks,
                'completion_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Stats calculation error: {e}")
            return {
                'total_areas': 0,
                'total_projects': 0,
                'completed_projects': 0,
                'total_tasks': 0,
                'tasks_completed': 0,
                'completion_rate': 0
            }
    
    @staticmethod
    def build_pillar_response_ultra_fast(
        pillar: dict,
        processed_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ultra-fast pillar response building using pre-processed lookup data
        """
        try:
            lookups = processed_data.get('lookups', {})
            tasks_by_project = lookups.get('tasks_by_project', {})
            
            # Get areas for this pillar using O(1) lookup
            pillar_areas = [a for a in processed_data.get('active_areas', []) 
                           if a.get('pillar_id') == pillar['id']]
            
            # Calculate stats with minimal loops
            total_projects = 0
            total_tasks = 0
            completed_tasks = 0
            
            for area in pillar_areas:
                # Get projects for this area
                area_projects = [p for p in processed_data.get('active_projects', [])
                               if p.get('area_id') == area['id']]
                
                total_projects += len(area_projects)
                
                # Calculate task stats
                for project in area_projects:
                    project_tasks = tasks_by_project.get(project['id'], [])
                    total_tasks += len(project_tasks)
                    completed_tasks += sum(1 for t in project_tasks if t.get('status') == 'completed')
            
            return {
                **pillar,
                'area_count': len(pillar_areas),
                'project_count': total_projects,
                'task_count': total_tasks,
                'completed_task_count': completed_tasks,
                'progress_percentage': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Pillar response building error: {e}")
            return {**pillar, 'area_count': 0, 'project_count': 0, 'task_count': 0}
    
    @staticmethod
    def build_area_response_ultra_fast(
        area: dict,
        processed_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ultra-fast area response building
        """
        try:
            lookups = processed_data.get('lookups', {})
            pillar_lookup = lookups.get('pillar_lookup', {})
            tasks_by_project = lookups.get('tasks_by_project', {})
            
            # Get pillar name using O(1) lookup
            pillar_name = None
            if area.get('pillar_id') and area['pillar_id'] in pillar_lookup:
                pillar_name = pillar_lookup[area['pillar_id']].get('name')
            
            # Get projects for this area
            area_projects = [p for p in processed_data.get('active_projects', [])
                           if p.get('area_id') == area['id']]
            
            # Calculate task stats efficiently
            total_tasks = 0
            completed_tasks = 0
            
            for project in area_projects:
                project_tasks = tasks_by_project.get(project['id'], [])
                total_tasks += len(project_tasks)
                completed_tasks += sum(1 for t in project_tasks if t.get('status') == 'completed')
            
            return {
                **area,
                'pillar_name': pillar_name,
                'project_count': len(area_projects),
                'completed_project_count': len([p for p in area_projects if p.get('status') == 'Completed']),
                'total_task_count': total_tasks,
                'completed_task_count': completed_tasks
            }
            
        except Exception as e:
            logger.error(f"Area response building error: {e}")
            return {**area, 'project_count': 0, 'total_task_count': 0}
    
    @staticmethod  
    def build_project_response_ultra_fast(
        project: dict,
        processed_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ultra-fast project response building
        """
        try:
            lookups = processed_data.get('lookups', {})
            area_lookup = lookups.get('area_lookup', {})
            tasks_by_project = lookups.get('tasks_by_project', {})
            
            # Get area name using O(1) lookup
            area_name = None
            if project.get('area_id') and project['area_id'] in area_lookup:
                area_name = area_lookup[project['area_id']].get('name')
            
            # Get tasks for this project using O(1) lookup
            project_tasks = tasks_by_project.get(project['id'], [])
            
            # Calculate stats instantly
            task_count = len(project_tasks)
            completed_count = sum(1 for t in project_tasks if t.get('status') == 'completed')
            
            return {
                **project,
                'area_name': area_name,
                'task_count': task_count,
                'completed_task_count': completed_count,
                'active_task_count': task_count - completed_count,
                'completion_percentage': (completed_count / task_count * 100) if task_count > 0 else 0.0,
                'is_overdue': (project.get('deadline') and 
                             project.get('status') != 'Completed' and 
                             project['deadline'] < datetime.utcnow()) if project.get('deadline') else False
            }
            
        except Exception as e:
            logger.error(f"Project response building error: {e}")
            return {**project, 'task_count': 0, 'completed_task_count': 0}

# Global processor instance
memory_processor = MemoryEfficientProcessor()