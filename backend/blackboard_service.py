"""
HRM Phase 3: Blackboard Service for Centralized AI Insights
Implements the Blackboard architectural pattern for AI systems
Reference: aurum_life_hrm_phase3_prd.md - Section 3.1.2
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum

from supabase_client import get_supabase_client
from hrm_service import HRMInsight

logger = logging.getLogger(__name__)

@dataclass
class InsightSubscription:
    """Subscription to insight notifications"""
    subscriber_id: str
    callback: Callable
    filters: Dict[str, Any]
    created_at: datetime

class InsightPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class BlackboardService:
    """
    Centralized insight repository with pub/sub capabilities
    Implements the Blackboard architectural pattern for AI systems
    """
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self._subscribers: Dict[str, InsightSubscription] = {}
        self._insight_cache: Dict[str, Dict[str, Any]] = {}
        self._processing_queue = asyncio.Queue()
        self._background_tasks = set()
        
    async def start_background_processing(self):
        """Start background insight processing"""
        task = asyncio.create_task(self._process_insight_queue())
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)
        
        cleanup_task = asyncio.create_task(self._cleanup_expired_insights())
        self._background_tasks.add(cleanup_task)
        cleanup_task.add_done_callback(self._background_tasks.discard)
    
    async def store_insight(
        self, 
        user_id: str, 
        insight: HRMInsight, 
        priority: InsightPriority = InsightPriority.MEDIUM,
        notify_subscribers: bool = True
    ) -> str:
        """
        Store insight in blackboard and notify subscribers
        
        Args:
            user_id: User ID
            insight: HRM insight to store
            priority: Priority level for processing
            notify_subscribers: Whether to notify subscribers
            
        Returns:
            Insight ID
        """
        try:
            # Prepare insight data for storage
            insight_data = {
                'id': insight.insight_id,
                'user_id': user_id,
                'entity_type': insight.entity_type,
                'entity_id': insight.entity_id,
                'insight_type': insight.insight_type,
                'title': insight.title,
                'summary': insight.summary,
                'detailed_reasoning': insight.detailed_reasoning,
                'confidence_score': insight.confidence_score,
                'impact_score': insight.impact_score,
                'reasoning_path': insight.reasoning_path,
                'expires_at': insight.expires_at.isoformat() if insight.expires_at else None,
                'tags': self._generate_insight_tags(insight),
                'is_active': True,
                'is_pinned': False,
                'application_count': 0,
                'version': 1,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Store in database
            response = self.supabase.table('insights').upsert(insight_data).execute()
            
            if not response.data:
                raise Exception("Failed to store insight in database")
            
            stored_insight = response.data[0]
            
            # Update cache
            cache_key = f"{user_id}:{insight.entity_type}:{insight.entity_id or 'global'}"
            if cache_key not in self._insight_cache:
                self._insight_cache[cache_key] = {}
            self._insight_cache[cache_key][insight.insight_id] = stored_insight
            
            # Add to processing queue for notifications
            if notify_subscribers:
                await self._processing_queue.put({
                    'action': 'notify_subscribers',
                    'user_id': user_id,
                    'insight': stored_insight,
                    'priority': priority
                })
            
            # Check for insight relationships and patterns
            await self._processing_queue.put({
                'action': 'analyze_relationships',
                'user_id': user_id,
                'insight_id': insight.insight_id
            })
            
            logger.info(f"✅ Stored insight {insight.insight_id} in blackboard for user {user_id}")
            return insight.insight_id
            
        except Exception as e:
            logger.error(f"❌ Failed to store insight: {e}")
            raise
    
    async def get_insights(
        self,
        user_id: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 50,
        include_expired: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Retrieve insights from blackboard with filtering
        
        Args:
            user_id: User ID
            filters: Optional filters (entity_type, insight_type, tags, etc.)
            limit: Maximum number of insights to return
            include_expired: Whether to include expired insights
            
        Returns:
            List of insights
        """
        try:
            query = self.supabase.table('insights').select('*').eq('user_id', user_id)
            
            # Apply filters
            if filters:
                if 'entity_type' in filters:
                    query = query.eq('entity_type', filters['entity_type'])
                if 'entity_id' in filters:
                    query = query.eq('entity_id', filters['entity_id'])
                if 'insight_type' in filters:
                    query = query.eq('insight_type', filters['insight_type'])
                if 'is_active' in filters:
                    query = query.eq('is_active', filters['is_active'])
                if 'is_pinned' in filters:
                    query = query.eq('is_pinned', filters['is_pinned'])
                if 'min_confidence' in filters:
                    query = query.gte('confidence_score', filters['min_confidence'])
                if 'tags' in filters and filters['tags']:
                    query = query.overlaps('tags', filters['tags'])
            
            # Handle expiration
            if not include_expired:
                query = query.or_('expires_at.is.null,expires_at.gt.' + datetime.utcnow().isoformat())
            
            # Order and limit
            query = query.order('created_at', desc=True).limit(limit)
            
            response = query.execute()
            insights = response.data or []
            
            # Update last_accessed_at for retrieved insights
            if insights:
                insight_ids = [insight['id'] for insight in insights]
                self.supabase.table('insights').update({
                    'last_accessed_at': datetime.utcnow().isoformat()
                }).in_('id', insight_ids).execute()
            
            logger.info(f"✅ Retrieved {len(insights)} insights for user {user_id}")
            return insights
            
        except Exception as e:
            logger.error(f"❌ Failed to get insights: {e}")
            return []
    
    async def get_insight_by_id(self, user_id: str, insight_id: str) -> Optional[Dict[str, Any]]:
        """Get specific insight by ID"""
        try:
            response = self.supabase.table('insights').select('*').eq(
                'id', insight_id
            ).eq('user_id', user_id).execute()
            
            if response.data:
                insight = response.data[0]
                
                # Update access time
                self.supabase.table('insights').update({
                    'last_accessed_at': datetime.utcnow().isoformat()
                }).eq('id', insight_id).execute()
                
                return insight
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get insight {insight_id}: {e}")
            return None
    
    async def update_insight_feedback(
        self,
        user_id: str,
        insight_id: str,
        feedback: str,
        feedback_details: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update insight with user feedback
        
        Args:
            user_id: User ID
            insight_id: Insight ID
            feedback: accepted, rejected, modified, ignored
            feedback_details: Additional feedback details
            
        Returns:
            True if successful
        """
        try:
            update_data = {
                'user_feedback': feedback,
                'feedback_details': feedback_details or {},
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Increment application count for positive feedback
            if feedback == 'accepted':
                # Get current application count
                current = await self.get_insight_by_id(user_id, insight_id)
                if current:
                    update_data['application_count'] = (current.get('application_count', 0) or 0) + 1
            
            response = self.supabase.table('insights').update(update_data).eq(
                'id', insight_id
            ).eq('user_id', user_id).execute()
            
            if response.data:
                # Log feedback for model improvement
                await self._log_feedback(user_id, insight_id, feedback, feedback_details)
                
                # Invalidate cache
                self._invalidate_cache_for_user(user_id)
                
                logger.info(f"✅ Updated insight {insight_id} with feedback: {feedback}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to update insight feedback: {e}")
            return False
    
    async def pin_insight(self, user_id: str, insight_id: str, pinned: bool = True) -> bool:
        """Pin or unpin an insight"""
        try:
            response = self.supabase.table('insights').update({
                'is_pinned': pinned,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', insight_id).eq('user_id', user_id).execute()
            
            return bool(response.data)
            
        except Exception as e:
            logger.error(f"❌ Failed to {'pin' if pinned else 'unpin'} insight: {e}")
            return False
    
    async def deactivate_insight(self, user_id: str, insight_id: str) -> bool:
        """Deactivate an insight"""
        try:
            response = self.supabase.table('insights').update({
                'is_active': False,
                'updated_at': datetime.utcnow().isoformat()
            }).eq('id', insight_id).eq('user_id', user_id).execute()
            
            if response.data:
                self._invalidate_cache_for_user(user_id)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to deactivate insight: {e}")
            return False
    
    async def subscribe_to_insights(
        self,
        subscriber_id: str,
        callback: Callable,
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Subscribe to insight notifications
        
        Args:
            subscriber_id: Unique subscriber identifier
            callback: Callback function for notifications
            filters: Optional filters for subscription
            
        Returns:
            Subscription ID
        """
        subscription = InsightSubscription(
            subscriber_id=subscriber_id,
            callback=callback,
            filters=filters or {},
            created_at=datetime.utcnow()
        )
        
        self._subscribers[subscriber_id] = subscription
        
        logger.info(f"✅ Created insight subscription: {subscriber_id}")
        return subscriber_id
    
    async def unsubscribe(self, subscriber_id: str) -> bool:
        """Remove insight subscription"""
        if subscriber_id in self._subscribers:
            del self._subscribers[subscriber_id]
            logger.info(f"✅ Removed insight subscription: {subscriber_id}")
            return True
        return False
    
    async def get_insight_statistics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get insight statistics for dashboard"""
        try:
            since_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            # Get basic counts
            insights_resp = self.supabase.table('insights').select(
                'insight_type, confidence_score, user_feedback, created_at'
            ).eq('user_id', user_id).gte('created_at', since_date).execute()
            
            insights = insights_resp.data or []
            
            if not insights:
                return {
                    'total_insights': 0,
                    'avg_confidence': 0.0,
                    'feedback_rate': 0.0,
                    'acceptance_rate': 0.0,
                    'insights_by_type': {},
                    'confidence_trend': []
                }
            
            # Calculate statistics
            total_insights = len(insights)
            avg_confidence = sum(i.get('confidence_score', 0) for i in insights) / total_insights
            
            # Feedback statistics
            with_feedback = [i for i in insights if i.get('user_feedback')]
            feedback_rate = len(with_feedback) / total_insights if total_insights > 0 else 0
            
            accepted = [i for i in with_feedback if i.get('user_feedback') == 'accepted']
            acceptance_rate = len(accepted) / len(with_feedback) if with_feedback else 0
            
            # Insights by type
            insights_by_type = {}
            for insight in insights:
                insight_type = insight.get('insight_type', 'unknown')
                insights_by_type[insight_type] = insights_by_type.get(insight_type, 0) + 1
            
            # Confidence trend (weekly averages)
            confidence_trend = self._calculate_confidence_trend(insights)
            
            return {
                'total_insights': total_insights,
                'avg_confidence': round(avg_confidence, 3),
                'feedback_rate': round(feedback_rate, 3),
                'acceptance_rate': round(acceptance_rate, 3),
                'insights_by_type': insights_by_type,
                'confidence_trend': confidence_trend
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get insight statistics: {e}")
            return {}
    
    # Background processing methods
    async def _process_insight_queue(self):
        """Background task to process insight queue"""
        while True:
            try:
                # Wait for items in queue
                item = await self._processing_queue.get()
                
                action = item.get('action')
                if action == 'notify_subscribers':
                    await self._notify_subscribers(item)
                elif action == 'analyze_relationships':
                    await self._analyze_insight_relationships(item)
                
                self._processing_queue.task_done()
                
            except Exception as e:
                logger.error(f"❌ Error processing insight queue item: {e}")
                await asyncio.sleep(1)  # Brief pause before continuing
    
    async def _cleanup_expired_insights(self):
        """Background task to clean up expired insights"""
        while True:
            try:
                # Clean up every hour
                await asyncio.sleep(3600)
                
                # Deactivate expired insights
                expired_cutoff = datetime.utcnow().isoformat()
                self.supabase.table('insights').update({
                    'is_active': False,
                    'updated_at': datetime.utcnow().isoformat()
                }).lt('expires_at', expired_cutoff).eq('is_active', True).execute()
                
                # Clear old cache entries
                self._insight_cache.clear()
                
                logger.info("✅ Cleaned up expired insights")
                
            except Exception as e:
                logger.error(f"❌ Error in insight cleanup: {e}")
    
    async def _notify_subscribers(self, item: Dict[str, Any]):
        """Notify subscribers of new insights"""
        user_id = item.get('user_id')
        insight = item.get('insight')
        priority = item.get('priority', InsightPriority.MEDIUM)
        
        # Find matching subscribers
        matching_subscribers = []
        for subscriber_id, subscription in self._subscribers.items():
            if self._matches_subscription_filters(insight, subscription.filters):
                matching_subscribers.append(subscription)
        
        # Notify subscribers
        for subscription in matching_subscribers:
            try:
                await subscription.callback(insight, priority)
            except Exception as e:
                logger.error(f"❌ Subscriber callback failed for {subscription.subscriber_id}: {e}")
    
    async def _analyze_insight_relationships(self, item: Dict[str, Any]):
        """Analyze relationships between insights"""
        user_id = item.get('user_id')
        insight_id = item.get('insight_id')
        
        # Get recent insights for pattern analysis
        recent_insights = await self.get_insights(
            user_id=user_id,
            filters={'is_active': True},
            limit=20
        )
        
        if len(recent_insights) < 3:
            return  # Not enough data for pattern analysis
        
        # Look for patterns (this would be expanded with more sophisticated analysis)
        patterns = self._detect_insight_patterns(recent_insights)
        
        if patterns:
            # Create meta-insight about detected patterns
            from hrm_service import HRMInsight
            import uuid
            
            pattern_insight = HRMInsight(
                insight_id=str(uuid.uuid4()),
                entity_type='global',
                entity_id=None,
                insight_type='pattern_recognition',
                title='Pattern Detected in Recent Insights',
                summary=f"Detected {len(patterns)} patterns in your recent insights",
                detailed_reasoning={'patterns': patterns},
                confidence_score=0.75,
                impact_score=0.6,
                reasoning_path=[{
                    'level': 'global',
                    'reasoning': 'Analysis of insight relationships and patterns',
                    'confidence': 0.75
                }],
                recommendations=[f"Consider: {pattern['recommendation']}" for pattern in patterns[:3]]
            )
            
            # Store pattern insight
            await self.store_insight(user_id, pattern_insight, notify_subscribers=False)
    
    # Helper methods
    def _generate_insight_tags(self, insight: HRMInsight) -> List[str]:
        """Generate tags for insight categorization"""
        tags = [insight.entity_type, insight.insight_type]
        
        if insight.confidence_score > 0.8:
            tags.append('high_confidence')
        if insight.impact_score and insight.impact_score > 0.8:
            tags.append('high_impact')
        if insight.expires_at and insight.expires_at < datetime.utcnow() + timedelta(hours=6):
            tags.append('urgent')
        
        return tags
    
    def _matches_subscription_filters(self, insight: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if insight matches subscription filters"""
        if not filters:
            return True
        
        for filter_key, filter_value in filters.items():
            insight_value = insight.get(filter_key)
            
            if filter_key == 'min_confidence' and insight_value < filter_value:
                return False
            elif filter_key == 'tags' and not set(filter_value).intersection(insight.get('tags', [])):
                return False
            elif filter_key in insight and insight_value != filter_value:
                return False
        
        return True
    
    def _calculate_confidence_trend(self, insights: List[Dict[str, Any]]) -> List[Dict[str, float]]:
        """Calculate weekly confidence trend"""
        # Group by week and calculate averages
        from collections import defaultdict
        weekly_confidence = defaultdict(list)
        
        for insight in insights:
            created_at = datetime.fromisoformat(insight['created_at'].replace('Z', '+00:00'))
            week_key = created_at.strftime('%Y-W%U')
            weekly_confidence[week_key].append(insight.get('confidence_score', 0))
        
        trend = []
        for week, confidences in sorted(weekly_confidence.items()):
            avg_confidence = sum(confidences) / len(confidences)
            trend.append({
                'week': week,
                'avg_confidence': round(avg_confidence, 3)
            })
        
        return trend[-4:]  # Last 4 weeks
    
    def _detect_insight_patterns(self, insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect patterns in insights"""
        patterns = []
        
        # Pattern 1: Repeated low confidence in same entity type
        entity_types = {}
        for insight in insights:
            entity_type = insight.get('entity_type')
            if entity_type:
                if entity_type not in entity_types:
                    entity_types[entity_type] = []
                entity_types[entity_type].append(insight.get('confidence_score', 0))
        
        for entity_type, scores in entity_types.items():
            if len(scores) >= 3 and sum(scores) / len(scores) < 0.6:
                patterns.append({
                    'type': 'low_confidence_pattern',
                    'entity_type': entity_type,
                    'description': f'Consistently low confidence scores for {entity_type} insights',
                    'recommendation': f'Review and refine {entity_type} analysis approach'
                })
        
        return patterns
    
    def _invalidate_cache_for_user(self, user_id: str):
        """Invalidate cache entries for a user"""
        keys_to_remove = [key for key in self._insight_cache.keys() if key.startswith(f"{user_id}:")]
        for key in keys_to_remove:
            del self._insight_cache[key]
    
    async def _log_feedback(
        self,
        user_id: str,
        insight_id: str,
        feedback: str,
        feedback_details: Optional[Dict[str, Any]]
    ):
        """Log feedback for model improvement"""
        try:
            feedback_data = {
                'user_id': user_id,
                'insight_id': insight_id,
                'feedback_type': f'insight_{feedback}',
                'feedback_text': feedback_details.get('text') if feedback_details else None,
                'suggested_improvement': feedback_details.get('improvement') if feedback_details else None,
                'created_at': datetime.utcnow().isoformat()
            }
            
            self.supabase.table('hrm_feedback_log').insert(feedback_data).execute()
            
        except Exception as e:
            logger.error(f"❌ Failed to log feedback: {e}")

# Global blackboard instance
blackboard = BlackboardService()