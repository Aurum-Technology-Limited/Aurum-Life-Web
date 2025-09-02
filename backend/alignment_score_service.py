"""
Alignment Score Service - Manages the point calculation and tracking system
STRATEGIC SHIFT: Project-Based Scoring (Outcomes over Activities)
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

    def calculate_project_points(self, project_data: Dict, area_data: Optional[Dict] = None) -> Dict:
        """
        Calculate points for a completed project using new project-based scoring system
        
        NEW PROJECT-BASED ALGORITHM:
        - Base Points: +50 points for any completed Project
        - Project Priority Bonus: +25 points for "High" priority Project  
        - Area Importance Bonus: +50 points if Project is within top-level importance Area (5/5)
        
        Maximum possible: 125 points (50+25+50)
        """
        points = 50  # Base points for any completed project
        breakdown = {'base': 50}
        
        # Project Priority Bonus
        project_priority = project_data.get('priority', '').lower()
        if project_priority == 'high':
            points += 25
            breakdown['project_priority'] = 25
        
        # Area Importance Bonus - top-level importance (5/5)
        if area_data and area_data.get('importance') == 5:
            points += 50
            breakdown['area_importance'] = 50
        
        return {
            'total_points': points,
            'breakdown': breakdown,
            'project_priority': project_priority,
            'area_importance': area_data.get('importance') if area_data else None
        }

    async def record_project_completion(self, user_id: str, project_id: str) -> Optional[Dict]:
        """
        Record points for a completed project by fetching project hierarchy and calculating scores
        """
        try:
            # Fetch project details
            project_response = self.supabase.table('projects').select('*').eq('id', project_id).single().execute()
            if not project_response.data:
                logger.error(f"Project {project_id} not found")
                return None
            
            project_data = project_response.data
            area_data = None
            
            # Fetch area details if project has area_id
            if project_data.get('area_id'):
                area_response = self.supabase.table('areas').select('*').eq('id', project_data['area_id']).single().execute()
                if area_response.data:
                    area_data = area_response.data
            
            # Calculate points using new project-based algorithm
            score_data = self.calculate_project_points(project_data, area_data)
            
            # Record the alignment score - use task_id column for project_id (backwards compatibility)
            alignment_record = {
                'user_id': user_id,
                'task_id': project_id,  # Use existing task_id column to store project_id
                'points_earned': score_data['total_points'],
                'task_priority': score_data['project_priority'],  # Use existing task_priority column
                'area_importance': score_data['area_importance']
            }
            
            response = self.supabase.table('alignment_scores').insert(alignment_record).execute()
            
            if response.data:
                logger.info(f"Recorded {score_data['total_points']} points for project {project_id} by user {user_id}")
                return {
                    'alignment_score': response.data[0],
                    'breakdown': score_data['breakdown']
                }
            else:
                logger.error(f"Failed to record alignment score: {response}")
                return None
                
        except Exception as e:
            logger.error(f"Error recording project completion: {e}")
            return None

    # DEPRECATED: Task-based scoring methods (keeping for backwards compatibility)
    def calculate_task_points(self, task_data: Dict, project_data: Optional[Dict] = None, area_data: Optional[Dict] = None) -> Dict:
        """
        DEPRECATED: Task-based scoring algorithm (replaced by project-based scoring)
        This method is kept for backwards compatibility but should not be used.
        """
        logger.warning("DEPRECATED: Task-based scoring is disabled. Use project-based scoring instead.")
        return {
            'total_points': 0,
            'breakdown': {'deprecated': 'Task-based scoring disabled'},
            'task_priority': task_data.get('priority') if task_data else None,
            'project_priority': project_data.get('priority') if project_data else None,
            'area_importance': area_data.get('importance') if area_data else None
        }

    async def record_task_completion(self, user_id: str, task_id: str) -> Optional[Dict]:
        """
        DEPRECATED: Task completion scoring (replaced by project completion scoring)
        This method is kept for backwards compatibility but no longer awards points.
        """
        logger.warning(f"DEPRECATED: Task completion scoring disabled for task {task_id}. Points now awarded only on project completion.")
        return None

    async def get_rolling_weekly_score(self, user_id: str) -> int:
        """
        Get user's rolling 7-day alignment score from project completions
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
        Get user's current month alignment score from project completions
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
        Set user's monthly alignment goal with verification readback
        """
        try:
            # Perform update
            _ = self.supabase.table('user_profiles') \
                .update({'monthly_alignment_goal': goal}) \
                .eq('id', user_id) \
                .execute()

            # Read-back to verify persistence (more reliable than relying on update return data)
            verify = self.supabase.table('user_profiles') \
                .select('monthly_alignment_goal') \
                .eq('id', user_id) \
                .single() \
                .execute()
            if verify.data is not None:
                stored = verify.data.get('monthly_alignment_goal')
                try:
                    # Supabase may return Decimal/str; normalize to int
                    stored_int = int(stored) if stored is not None else None
                except Exception:
                    stored_int = None
                return stored_int == int(goal)
            return False
        except Exception as e:
            logger.error(f"Error setting monthly goal: {e}")
            return False

    async def get_alignment_dashboard_data(self, user_id: str, use_hrm: bool = False) -> Dict:
        """
        Get comprehensive alignment data for dashboard widget
        Enhanced with optional HRM insights for deeper analysis
        """
        try:
            rolling_weekly = await self.get_rolling_weekly_score(user_id)
            monthly_score = await self.get_monthly_score(user_id)
            monthly_goal = await self.get_user_monthly_goal(user_id)
            
            # Calculate progress percentage (use 1000 as silent placeholder if no goal set)
            effective_goal = monthly_goal if monthly_goal else 1000
            progress_percentage = min((monthly_score / effective_goal) * 100, 100) if effective_goal > 0 else 0
            
            dashboard_data = {
                'rolling_weekly_score': rolling_weekly,
                'monthly_score': monthly_score,
                'monthly_goal': monthly_goal,
                'progress_percentage': round(progress_percentage, 1),
                'has_goal_set': monthly_goal is not None
            }
            
            # Optional HRM enhancement
            if use_hrm:
                try:
                    from hrm_service import HierarchicalReasoningModel, AnalysisDepth
                    hrm = HierarchicalReasoningModel(user_id)
                    
                    # Get global alignment analysis
                    insight = await hrm.analyze_entity(
                        entity_type='global',
                        entity_id=None,
                        analysis_depth=AnalysisDepth.BALANCED
                    )
                    
                    dashboard_data['hrm_enhancement'] = {
                        'confidence_score': insight.confidence_score,
                        'reasoning_summary': insight.summary,
                        'hierarchy_reasoning': insight.reasoning_path[:3],
                        'recommendations': insight.recommendations[:3]
                    }
                    
                except Exception as e:
                    logger.warning(f"Failed to enhance alignment dashboard with HRM: {e}")
                    dashboard_data['hrm_enhancement'] = {
                        'confidence_score': 0.5,
                        'reasoning_summary': "HRM analysis temporarily unavailable",
                        'hierarchy_reasoning': [],
                        'recommendations': ["Continue working on your current projects"]
                    }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error fetching alignment dashboard data: {e}")
            return {
                'rolling_weekly_score': 0,
                'monthly_score': 0,
                'monthly_goal': None,
                'progress_percentage': 0,
                'has_goal_set': False
            }

    async def get_weekly_score(self, user_id: str, use_hrm: bool = False) -> Dict:
        """
        Get weekly alignment score with optional HRM enhancement
        """
        try:
            rolling_weekly = await self.get_rolling_weekly_score(user_id)
            
            result = {
                'weekly_score': rolling_weekly,
                'period': 'last_7_days',
                'generated_at': datetime.now().isoformat()
            }
            
            # Optional HRM enhancement
            if use_hrm:
                try:
                    from hrm_service import HierarchicalReasoningModel, AnalysisDepth
                    hrm = HierarchicalReasoningModel(user_id)
                    
                    insight = await hrm.analyze_entity(
                        entity_type='weekly_alignment',
                        entity_id=None,
                        analysis_depth=AnalysisDepth.BALANCED
                    )
                    
                    result['hrm_enhancement'] = {
                        'confidence_score': insight.confidence_score,
                        'reasoning_summary': insight.summary,
                        'recommendations': insight.recommendations[:2]
                    }
                    
                except Exception as e:
                    logger.warning(f"Failed to enhance weekly score with HRM: {e}")
                    result['hrm_enhancement'] = {
                        'confidence_score': 0.5,
                        'reasoning_summary': "HRM analysis temporarily unavailable",
                        'recommendations': ["Continue working on your current projects"]
                    }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting weekly score: {e}")
            return {
                'weekly_score': 0,
                'period': 'last_7_days',
                'generated_at': datetime.now().isoformat()
            }

    async def get_monthly_score(self, user_id: str, use_hrm: bool = False) -> Dict:
        """
        Get monthly alignment score with optional HRM enhancement
        """
        try:
            monthly_score = await self.get_monthly_score(user_id)
            monthly_goal = await self.get_user_monthly_goal(user_id)
            
            # Calculate progress percentage
            progress_percentage = 0
            if monthly_goal and monthly_goal > 0:
                progress_percentage = min((monthly_score / monthly_goal) * 100, 100)
            
            result = {
                'monthly_score': monthly_score,
                'monthly_goal': monthly_goal,
                'progress_percentage': round(progress_percentage, 1),
                'period': 'current_month',
                'generated_at': datetime.now().isoformat()
            }
            
            # Optional HRM enhancement
            if use_hrm:
                try:
                    from hrm_service import HierarchicalReasoningModel, AnalysisDepth
                    hrm = HierarchicalReasoningModel(user_id)
                    
                    insight = await hrm.analyze_entity(
                        entity_type='monthly_alignment',
                        entity_id=None,
                        analysis_depth=AnalysisDepth.BALANCED
                    )
                    
                    result['hrm_enhancement'] = {
                        'confidence_score': insight.confidence_score,
                        'reasoning_summary': insight.summary,
                        'recommendations': insight.recommendations[:2]
                    }
                    
                except Exception as e:
                    logger.warning(f"Failed to enhance monthly score with HRM: {e}")
                    result['hrm_enhancement'] = {
                        'confidence_score': 0.5,
                        'reasoning_summary': "HRM analysis temporarily unavailable",
                        'recommendations': ["Continue working on your current projects"]
                    }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting monthly score: {e}")
            return {
                'monthly_score': 0,
                'monthly_goal': None,
                'progress_percentage': 0,
                'period': 'current_month',
                'generated_at': datetime.now().isoformat()
            }

    async def set_monthly_goal(self, user_id: str, goal: int) -> Dict:
        """
        Set monthly alignment goal and return confirmation
        """
        try:
            success = await self.set_user_monthly_goal(user_id, goal)
            
            if success:
                return {
                    'success': True,
                    'message': f'Monthly goal set to {goal} points',
                    'goal': goal,
                    'set_at': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'message': 'Failed to set monthly goal',
                    'goal': None,
                    'set_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error setting monthly goal: {e}")
            return {
                'success': False,
                'message': f'Error setting monthly goal: {str(e)}',
                'goal': None,
                'set_at': datetime.now().isoformat()
            }