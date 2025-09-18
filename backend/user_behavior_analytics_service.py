"""
User Behavior Analytics Service for Aurum Life
Tracks user interactions with AI features and provides insights
"""

import asyncio
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date, timedelta
from supabase_client import get_supabase_client
from models import (
    UserBehaviorEventCreate, 
    UserSessionCreate,
    UserAnalyticsPreferencesCreate,
    UserAnalyticsPreferencesUpdate,
    AIFeatureTypeEnum,
    UserActionTypeEnum,
    AIFeatureUsageStats,
    UserEngagementMetrics,
    DailyUsageStats,
    AnalyticsDashboardResponse
)
import logging
import json
from collections import defaultdict

logger = logging.getLogger(__name__)

class UserBehaviorAnalyticsService:
    """Service for tracking and analyzing user behavior"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    async def track_event(self, user_id: str, event: UserBehaviorEventCreate) -> Dict[str, any]:
        """
        Track a user behavior event
        
        Args:
            user_id: User ID
            event: Event data to track
            
        Returns:
            Dict with tracking result
        """
        try:
            # Check user consent first
            consent_check = await self.check_user_consent(user_id, event.action_type)
            if not consent_check:
                return {"success": False, "message": "User has not consented to this type of tracking"}
            
            # Prepare event data
            event_data = {
                "user_id": user_id,
                "session_id": event.session_id,
                "action_type": event.action_type,
                "feature_name": event.feature_name,
                "ai_feature_type": event.ai_feature_type,
                "event_data": event.event_data or {},
                "duration_ms": event.duration_ms,
                "success": event.success,
                "error_message": event.error_message,
                "page_url": event.page_url,
                "referrer_url": event.referrer_url,
                "user_agent": event.user_agent,
                "screen_resolution": event.screen_resolution,
                "timezone": event.timezone,
                "client_timestamp": event.client_timestamp.isoformat() if event.client_timestamp else None,
                "consent_given": True,
                "is_anonymized": False,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Insert event
            result = self.supabase.table('user_behavior_events').insert(event_data).execute()
            
            # Update session if it exists
            if event.session_id:
                await self.update_session_counters(user_id, event.session_id, event.action_type)
            
            return {"success": True, "event_id": result.data[0]['id'] if result.data else None}
            
        except Exception as e:
            logger.error(f"Error tracking event: {e}")
            return {"success": False, "error": str(e)}
    
    async def start_session(self, user_id: str, session_data: UserSessionCreate) -> Dict[str, any]:
        """
        Start a new user session
        
        Args:
            user_id: User ID
            session_data: Session creation data
            
        Returns:
            Dict with session result
        """
        try:
            # Check if session already exists
            existing_session = self.supabase.table('user_sessions')\
                .select('*')\
                .eq('user_id', user_id)\
                .eq('session_id', session_data.session_id)\
                .eq('is_active', True)\
                .execute()
            
            if existing_session.data:
                return {"success": True, "message": "Session already exists", "session_id": session_data.session_id}
            
            # Create new session
            session_record = {
                "user_id": user_id,
                "session_id": session_data.session_id,
                "entry_page": session_data.entry_page,
                "user_agent": session_data.user_agent,
                "screen_resolution": session_data.screen_resolution,
                "timezone": session_data.timezone,
                "device_type": session_data.device_type,
                "start_time": datetime.utcnow().isoformat(),
                "is_active": True,
                "consent_given": True,
                "page_views": 0,
                "ai_interactions": 0,
                "feature_usages": 0
            }
            
            result = self.supabase.table('user_sessions').insert(session_record).execute()
            
            return {"success": True, "session_id": session_data.session_id}
            
        except Exception as e:
            logger.error(f"Error starting session: {e}")
            return {"success": False, "error": str(e)}
    
    async def end_session(self, user_id: str, session_id: str, exit_page: Optional[str] = None) -> Dict[str, any]:
        """
        End a user session
        
        Args:
            user_id: User ID
            session_id: Session ID to end
            exit_page: Final page visited
            
        Returns:
            Dict with result
        """
        try:
            # Get session start time
            session = self.supabase.table('user_sessions')\
                .select('start_time')\
                .eq('user_id', user_id)\
                .eq('session_id', session_id)\
                .eq('is_active', True)\
                .single()\
                .execute()
            
            if not session.data:
                return {"success": False, "message": "Session not found"}
            
            # Calculate duration
            start_time = datetime.fromisoformat(session.data['start_time'].replace('Z', '+00:00'))
            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Update session
            update_data = {
                "end_time": end_time.isoformat(),
                "duration_ms": duration_ms,
                "is_active": False
            }
            
            if exit_page:
                update_data["exit_page"] = exit_page
            
            self.supabase.table('user_sessions')\
                .update(update_data)\
                .eq('user_id', user_id)\
                .eq('session_id', session_id)\
                .execute()
            
            return {"success": True, "duration_ms": duration_ms}
            
        except Exception as e:
            logger.error(f"Error ending session: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_session_counters(self, user_id: str, session_id: str, action_type: UserActionTypeEnum) -> None:
        """Update session counters based on action type"""
        try:
            increment_field = None
            
            if action_type == UserActionTypeEnum.page_view:
                increment_field = "page_views"
            elif action_type == UserActionTypeEnum.ai_interaction:
                increment_field = "ai_interactions"
            elif action_type == UserActionTypeEnum.feature_usage:
                increment_field = "feature_usages"
            
            if increment_field:
                # Use PostgreSQL's native increment
                self.supabase.rpc('increment_session_counter', {
                    'p_user_id': user_id,
                    'p_session_id': session_id,
                    'p_field': increment_field
                }).execute()
                
        except Exception as e:
            logger.warning(f"Error updating session counters: {e}")
    
    async def check_user_consent(self, user_id: str, action_type: UserActionTypeEnum) -> bool:
        """
        Check if user has consented to tracking for specific action type
        
        Args:
            user_id: User ID
            action_type: Type of action being tracked
            
        Returns:
            Boolean indicating consent status
        """
        try:
            prefs = self.supabase.table('user_analytics_preferences')\
                .select('*')\
                .eq('user_id', user_id)\
                .single()\
                .execute()
            
            if not prefs.data:
                # Default to consent if no preferences set
                return True
            
            preferences = prefs.data
            
            # Check general analytics consent
            if not preferences.get('analytics_consent', True):
                return False
            
            # Check specific action type consent
            if action_type == UserActionTypeEnum.ai_interaction:
                return preferences.get('ai_behavior_tracking', True)
            elif action_type == UserActionTypeEnum.search:
                return preferences.get('track_search_queries', False)
            elif action_type == UserActionTypeEnum.navigation:
                return preferences.get('track_navigation_patterns', True)
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking user consent: {e}")
            return True  # Default to consent on error
    
    async def get_user_analytics_preferences(self, user_id: str) -> Dict[str, any]:
        """Get user analytics preferences"""
        try:
            result = self.supabase.table('user_analytics_preferences')\
                .select('*')\
                .eq('user_id', user_id)\
                .single()\
                .execute()
            
            if result.data:
                return result.data
            else:
                # Create default preferences if none exist
                return await self.create_default_analytics_preferences(user_id)
                
        except Exception as e:
            logger.error(f"Error getting analytics preferences: {e}")
            return await self.create_default_analytics_preferences(user_id)
    
    async def update_user_analytics_preferences(self, user_id: str, preferences: UserAnalyticsPreferencesUpdate) -> Dict[str, any]:
        """Update user analytics preferences"""
        try:
            # Prepare update data, excluding None values
            update_data = {}
            for key, value in preferences.dict().items():
                if value is not None:
                    update_data[key] = value
            
            if not update_data:
                return {"success": False, "message": "No data to update"}
            
            result = self.supabase.table('user_analytics_preferences')\
                .update(update_data)\
                .eq('user_id', user_id)\
                .execute()
            
            return {"success": True, "data": result.data[0] if result.data else None}
            
        except Exception as e:
            logger.error(f"Error updating analytics preferences: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_default_analytics_preferences(self, user_id: str) -> Dict[str, any]:
        """Create default analytics preferences for user"""
        try:
            default_prefs = {
                "user_id": user_id,
                "analytics_consent": True,
                "ai_behavior_tracking": True,
                "performance_tracking": True,
                "error_reporting": True,
                "data_retention_days": 365,
                "anonymize_after_days": 90,
                "track_ai_insights_usage": True,
                "track_ai_actions_usage": True,
                "track_goal_planner_usage": True,
                "track_navigation_patterns": True,
                "track_search_queries": False,
                "share_anonymous_stats": True
            }
            
            result = self.supabase.table('user_analytics_preferences')\
                .insert(default_prefs)\
                .execute()
            
            return result.data[0] if result.data else default_prefs
            
        except Exception as e:
            logger.error(f"Error creating default preferences: {e}")
            return {}
    
    async def get_ai_feature_usage_stats(self, user_id: str, days: int = 30) -> List[AIFeatureUsageStats]:
        """Get AI feature usage statistics for user"""
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Query the optimized view
            result = self.supabase.table('user_ai_feature_usage')\
                .select('*')\
                .eq('user_id', user_id)\
                .gte('usage_date', start_date.date())\
                .execute()
            
            if not result.data:
                return []
            
            # Aggregate data by feature type
            feature_stats = defaultdict(lambda: {
                'total_sessions': 0,
                'total_time_spent_ms': 0,
                'total_interactions': 0,
                'success_rates': [],
                'last_used': None
            })
            
            for row in result.data:
                feature_type = row['ai_feature_type']
                feature_name = row['feature_name']
                key = f"{feature_type}:{feature_name}"
                
                feature_stats[key]['total_sessions'] += row['unique_sessions']
                feature_stats[key]['total_time_spent_ms'] += row['total_time_spent_ms'] or 0
                feature_stats[key]['total_interactions'] += row['total_interactions']
                feature_stats[key]['success_rates'].append(row['success_rate'])
                
                if not feature_stats[key]['last_used'] or row['last_used'] > feature_stats[key]['last_used']:
                    feature_stats[key]['last_used'] = row['last_used']
            
            # Convert to response format
            stats_list = []
            for key, stats in feature_stats.items():
                feature_type, feature_name = key.split(':', 1)
                
                avg_duration = (
                    stats['total_time_spent_ms'] / stats['total_interactions']
                    if stats['total_interactions'] > 0 else 0.0
                )
                
                avg_success_rate = (
                    sum(stats['success_rates']) / len(stats['success_rates'])
                    if stats['success_rates'] else 1.0
                )
                
                stats_list.append(AIFeatureUsageStats(
                    feature_type=AIFeatureTypeEnum(feature_type),
                    feature_name=feature_name,
                    total_sessions=stats['total_sessions'],
                    total_time_spent_ms=stats['total_time_spent_ms'],
                    average_session_duration_ms=avg_duration,
                    total_interactions=stats['total_interactions'],
                    success_rate=avg_success_rate,
                    last_used=stats['last_used']
                ))
            
            return sorted(stats_list, key=lambda x: x.total_interactions, reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting AI feature usage stats: {e}")
            return []
    
    async def get_user_engagement_metrics(self, user_id: str, days: int = 30) -> UserEngagementMetrics:
        """Get user engagement metrics"""
        try:
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get daily analytics data
            daily_data = self.supabase.table('daily_user_analytics')\
                .select('*')\
                .eq('user_id', user_id)\
                .gte('analytics_date', start_date.date())\
                .execute()
            
            if not daily_data.data:
                return UserEngagementMetrics()
            
            # Aggregate metrics
            total_sessions = sum(row['unique_sessions'] for row in daily_data.data)
            total_time_spent_ms = sum(row['total_time_spent_ms'] or 0 for row in daily_data.data)
            total_page_views = sum(row['page_views'] for row in daily_data.data)
            total_ai_interactions = sum(row['ai_interactions'] for row in daily_data.data)
            
            # Calculate average session duration
            avg_session_duration_ms = (
                total_time_spent_ms / total_sessions
                if total_sessions > 0 else 0.0
            )
            
            # Calculate bounce rate (sessions with only 1 page view)
            single_page_sessions = sum(
                1 for row in daily_data.data 
                if row['page_views'] <= 1 and row['unique_sessions'] > 0
            )
            bounce_rate = (
                single_page_sessions / total_sessions
                if total_sessions > 0 else 0.0
            )
            
            # Calculate return user rate (users who visited on multiple days)
            unique_days = len(set(row['analytics_date'] for row in daily_data.data))
            return_user_rate = unique_days / days if days > 0 else 0.0
            
            return UserEngagementMetrics(
                total_sessions=total_sessions,
                total_time_spent_ms=total_time_spent_ms,
                average_session_duration_ms=avg_session_duration_ms,
                total_page_views=total_page_views,
                total_ai_interactions=total_ai_interactions,
                bounce_rate=bounce_rate,
                return_user_rate=return_user_rate
            )
            
        except Exception as e:
            logger.error(f"Error getting user engagement metrics: {e}")
            return UserEngagementMetrics()
    
    async def get_analytics_dashboard(self, user_id: str, days: int = 30) -> AnalyticsDashboardResponse:
        """Get complete analytics dashboard data"""
        try:
            # Execute all queries concurrently
            engagement_task = asyncio.create_task(
                self.get_user_engagement_metrics(user_id, days)
            )
            ai_features_task = asyncio.create_task(
                self.get_ai_feature_usage_stats(user_id, days)
            )
            daily_stats_task = asyncio.create_task(
                self.get_daily_usage_stats(user_id, days)
            )
            top_features_task = asyncio.create_task(
                self.get_top_features(user_id, days)
            )
            
            # Wait for all tasks to complete
            engagement, ai_features, daily_stats, top_features = await asyncio.gather(
                engagement_task,
                ai_features_task,
                daily_stats_task,
                top_features_task
            )
            
            return AnalyticsDashboardResponse(
                user_engagement=engagement,
                ai_feature_usage=ai_features,
                daily_stats=daily_stats,
                top_features=top_features,
                user_journey_patterns=[]  # TODO: Implement journey pattern analysis
            )
            
        except Exception as e:
            logger.error(f"Error getting analytics dashboard: {e}")
            return AnalyticsDashboardResponse(
                user_engagement=UserEngagementMetrics(),
                ai_feature_usage=[],
                daily_stats=[],
                top_features=[]
            )
    
    async def get_daily_usage_stats(self, user_id: str, days: int = 30) -> List[DailyUsageStats]:
        """Get daily usage statistics"""
        try:
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=days)
            
            result = self.supabase.table('daily_user_analytics')\
                .select('*')\
                .eq('user_id', user_id)\
                .gte('analytics_date', start_date)\
                .order('analytics_date')\
                .execute()
            
            daily_stats = []
            for row in result.data:
                daily_stats.append(DailyUsageStats(
                    date=row['analytics_date'],
                    sessions=row['unique_sessions'],
                    unique_users=1,  # Single user context
                    total_time_spent_ms=row['total_time_spent_ms'] or 0,
                    page_views=row['page_views'],
                    ai_interactions=row['ai_interactions']
                ))
            
            return daily_stats
            
        except Exception as e:
            logger.error(f"Error getting daily usage stats: {e}")
            return []
    
    async def get_top_features(self, user_id: str, days: int = 30) -> List[Dict[str, any]]:
        """Get top used features"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            result = self.supabase.table('user_behavior_events')\
                .select('feature_name, action_type, ai_feature_type')\
                .eq('user_id', user_id)\
                .gte('timestamp', start_date.isoformat())\
                .execute()
            
            if not result.data:
                return []
            
            # Count feature usage
            feature_counts = defaultdict(int)
            for row in result.data:
                feature_key = f"{row['feature_name']}:{row['action_type']}"
                feature_counts[feature_key] += 1
            
            # Sort and format
            top_features = []
            for feature_key, count in sorted(feature_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                feature_name, action_type = feature_key.split(':', 1)
                top_features.append({
                    'feature_name': feature_name,
                    'action_type': action_type,
                    'usage_count': count
                })
            
            return top_features
            
        except Exception as e:
            logger.error(f"Error getting top features: {e}")
            return []
    
    async def anonymize_user_data(self, user_id: str) -> Dict[str, any]:
        """Anonymize user's analytics data"""
        try:
            # Call the PostgreSQL function
            result = self.supabase.rpc('anonymize_user_behavior_data', {
                'p_user_id': user_id
            }).execute()
            
            return {"success": True, "message": "User data anonymized successfully"}
            
        except Exception as e:
            logger.error(f"Error anonymizing user data: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete_user_analytics_data(self, user_id: str) -> Dict[str, any]:
        """Delete all analytics data for a user"""
        try:
            # Delete in order due to foreign key constraints
            self.supabase.table('user_behavior_events')\
                .delete()\
                .eq('user_id', user_id)\
                .execute()
            
            self.supabase.table('user_sessions')\
                .delete()\
                .eq('user_id', user_id)\
                .execute()
            
            self.supabase.table('user_analytics_preferences')\
                .delete()\
                .eq('user_id', user_id)\
                .execute()
            
            return {"success": True, "message": "All analytics data deleted"}
            
        except Exception as e:
            logger.error(f"Error deleting user analytics data: {e}")
            return {"success": False, "error": str(e)}