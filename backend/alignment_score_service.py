"""
Alignment Score Service - Manages the point calculation and tracking system
"""
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from supabase import create_client, Client
import logging

logger = logging.getLogger(__name__)

class AlignmentScoreService:
    def __init__(self):
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
        if not supabase_url or not supabase_key:
            raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY environment variables")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)

    def calculate_task_points(self, task_data: Dict, project_data: Optional[Dict] = None, area_data: Optional[Dict] = None) -> Dict:
        """
        Calculate points for a completed task using additive scoring system
        
        Algorithm:
        - Base Points: +5 for any completed task
        - Task Priority Bonus: +10 for "High" priority task  
        - Project Priority Bonus: +15 for task in "High" priority project
        - Area Importance Bonus: +20 for task in top-level importance Area (5/5)
        
        Maximum possible: 50 points (5+10+15+20)
        """
        points = 5  # Base points
        breakdown = {'base': 5}
        
        # Task Priority Bonus
        task_priority = task_data.get('priority', '').lower()
        if task_priority == 'high':
            points += 10
            breakdown['task_priority'] = 10
        
        # Project Priority Bonus
        if project_data and project_data.get('priority', '').lower() == 'high':
            points += 15
            breakdown['project_priority'] = 15
        
        # Area Importance Bonus  
        if area_data and area_data.get('importance') == 5:
            points += 20
            breakdown['area_importance'] = 20
        
        return {
            'total_points': points,
            'breakdown': breakdown,
            'task_priority': task_priority,
            'project_priority': project_data.get('priority') if project_data else None,
            'area_importance': area_data.get('importance') if area_data else None
        }

    async def record_task_completion(self, user_id: str, task_id: str) -> Optional[Dict]:
        """
        Record points for a completed task by fetching task hierarchy and calculating scores
        """
        try:
            # Fetch task details
            task_response = self.supabase.table('tasks').select('*').eq('id', task_id).single().execute()
            if not task_response.data:
                logger.error(f"Task {task_id} not found")
                return None
            
            task_data = task_response.data
            project_data = None
            area_data = None
            
            # Fetch project details if task has project_id
            if task_data.get('project_id'):
                project_response = self.supabase.table('projects').select('*').eq('id', task_data['project_id']).single().execute()
                if project_response.data:
                    project_data = project_response.data
                    
                    # Fetch area details if project has area_id
                    if project_data.get('area_id'):
                        area_response = self.supabase.table('areas').select('*').eq('id', project_data['area_id']).single().execute()
                        if area_response.data:
                            area_data = area_response.data
            
            # Calculate points
            score_data = self.calculate_task_points(task_data, project_data, area_data)
            
            # Record the alignment score
            alignment_record = {
                'user_id': user_id,
                'task_id': task_id,
                'points_earned': score_data['total_points'],
                'task_priority': score_data['task_priority'],
                'project_priority': score_data['project_priority'],
                'area_importance': score_data['area_importance']
            }
            
            response = self.supabase.table('alignment_scores').insert(alignment_record).execute()
            
            if response.data:
                logger.info(f"Recorded {score_data['total_points']} points for task {task_id} by user {user_id}")
                return {
                    'alignment_score': response.data[0],
                    'breakdown': score_data['breakdown']
                }
            else:
                logger.error(f"Failed to record alignment score: {response}")
                return None
                
        except Exception as e:
            logger.error(f"Error recording task completion: {e}")
            return None

    async def get_rolling_weekly_score(self, user_id: str) -> int:
        """
        Get user's rolling 7-day alignment score
        """
        try:
            seven_days_ago = datetime.now() - timedelta(days=7)
            
            response = self.supabase.table('alignment_scores')\
                .select('points_earned')\
                .eq('user_id', user_id)\
                .gte('created_at', seven_days_ago.isoformat())\
                .execute()
            
            if response.data:
                total_points = sum(record['points_earned'] for record in response.data)
                return total_points
            return 0
            
        except Exception as e:
            logger.error(f"Error fetching rolling weekly score: {e}")
            return 0

    async def get_monthly_score(self, user_id: str) -> int:
        """
        Get user's current month alignment score
        """
        try:
            # Get first day of current month
            now = datetime.now()
            first_day_of_month = datetime(now.year, now.month, 1)
            
            response = self.supabase.table('alignment_scores')\
                .select('points_earned')\
                .eq('user_id', user_id)\
                .gte('created_at', first_day_of_month.isoformat())\
                .execute()
            
            if response.data:
                total_points = sum(record['points_earned'] for record in response.data)
                return total_points
            return 0
            
        except Exception as e:
            logger.error(f"Error fetching monthly score: {e}")
            return 0

    async def get_user_monthly_goal(self, user_id: str) -> Optional[int]:
        """
        Get user's monthly alignment goal
        """
        try:
            response = self.supabase.table('user_profiles')\
                .select('monthly_alignment_goal')\
                .eq('id', user_id)\
                .single()\
                .execute()
            
            if response.data and response.data['monthly_alignment_goal']:
                return response.data['monthly_alignment_goal']
            return None
            
        except Exception as e:
            logger.error(f"Error fetching monthly goal: {e}")
            return None

    async def set_user_monthly_goal(self, user_id: str, goal: int) -> bool:
        """
        Set user's monthly alignment goal
        """
        try:
            response = self.supabase.table('user_profiles')\
                .update({'monthly_alignment_goal': goal})\
                .eq('id', user_id)\
                .execute()
            
            return bool(response.data)
            
        except Exception as e:
            logger.error(f"Error setting monthly goal: {e}")
            return False

    async def get_alignment_dashboard_data(self, user_id: str) -> Dict:
        """
        Get comprehensive alignment data for dashboard widget
        """
        try:
            rolling_weekly = await self.get_rolling_weekly_score(user_id)
            monthly_score = await self.get_monthly_score(user_id)
            monthly_goal = await self.get_user_monthly_goal(user_id)
            
            # Calculate progress percentage (use 1000 as silent placeholder if no goal set)
            effective_goal = monthly_goal if monthly_goal else 1000
            progress_percentage = min((monthly_score / effective_goal) * 100, 100) if effective_goal > 0 else 0
            
            return {
                'rolling_weekly_score': rolling_weekly,
                'monthly_score': monthly_score,
                'monthly_goal': monthly_goal,
                'progress_percentage': round(progress_percentage, 1),
                'has_goal_set': monthly_goal is not None
            }
            
        except Exception as e:
            logger.error(f"Error fetching alignment dashboard data: {e}")
            return {
                'rolling_weekly_score': 0,
                'monthly_score': 0,
                'monthly_goal': None,
                'progress_percentage': 0,
                'has_goal_set': False
            }