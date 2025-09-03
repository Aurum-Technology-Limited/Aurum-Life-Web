#!/usr/bin/env python3
"""
AI Quota Management Service
Tracks and manages AI interaction quotas for users
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from enum import Enum

from supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

class AIFeatureType(Enum):
    """Types of AI features that consume quota"""
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    HRM_ANALYSIS = "hrm_analysis"  
    TASK_WHY_STATEMENTS = "task_why_statements"
    FOCUS_SUGGESTIONS = "focus_suggestions"
    TODAY_PRIORITIES = "today_priorities"
    GOAL_COACHING = "goal_coaching"
    PROJECT_DECOMPOSITION = "project_decomposition"
    STRATEGIC_PLANNING = "strategic_planning"

class AIQuotaService:
    """Manages AI interaction quotas and usage tracking"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.monthly_quota_limits = {
            'free': 50,      # Free tier: 50 interactions/month
            'pro': 100,      # Pro tier: 100 interactions/month  
            'premium': 300,  # Premium tier: 300 interactions/month
            'enterprise': 1000  # Enterprise: 1000 interactions/month
        }
        self.default_quota_limit = self.monthly_quota_limits['pro']  # Default to pro tier
    
    async def get_user_quota(self, user_id: str, tier: str = 'pro') -> Dict[str, Any]:
        """Get user's current quota status with real usage tracking"""
        try:
            # Get quota limit for user's tier (default to pro for now)
            quota_limit = self.monthly_quota_limits.get(tier, self.default_quota_limit)
            
            # Get current month boundaries
            now = datetime.utcnow()
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Calculate next month start
            if now.month == 12:
                next_month = month_start.replace(year=month_start.year + 1, month=1)
            else:
                next_month = month_start.replace(month=month_start.month + 1)
            
            # Count actual AI interactions for this month
            response = self.supabase.table('ai_interactions').select('*', count='exact').eq(
                'user_id', user_id
            ).gte('created_at', month_start.isoformat()).execute()
            
            used_quota = response.count or 0
            remaining = max(0, quota_limit - used_quota)
            
            logger.info(f"📊 User {user_id} quota ({tier}): {used_quota}/{quota_limit} used, {remaining} remaining")
            
            return {
                'remaining': remaining,
                'total': quota_limit,
                'used': used_quota,
                'tier': tier,
                'resets_at': next_month.isoformat(),
                'period': 'monthly',
                'usage_breakdown': await self._get_usage_breakdown(user_id, month_start)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get quota for user {user_id}: {e}")
            # Return conservative quota on error
            return {
                'remaining': 5,
                'total': self.monthly_quota_limit,
                'used': 0,
                'resets_at': next_month.isoformat() if 'next_month' in locals() else None,
                'period': 'monthly'
            }
    
    async def check_quota_available(self, user_id: str, feature_type: AIFeatureType) -> tuple[bool, Dict[str, Any]]:
        """Check if user has quota available for AI interaction"""
        quota_info = await self.get_user_quota(user_id)
        
        has_quota = quota_info['remaining'] > 0
        
        if not has_quota:
            logger.warning(f"⚠️  User {user_id} has no remaining quota for {feature_type.value}")
        
        return has_quota, quota_info
    
    async def consume_quota(self, user_id: str, feature_type: AIFeatureType, 
                           feature_details: Dict[str, Any] = None,
                           cost_tokens: int = 0) -> bool:
        """Consume one AI interaction from user's quota"""
        try:
            # Check if quota is available first
            has_quota, quota_info = await self.check_quota_available(user_id, feature_type)
            
            if not has_quota:
                logger.warning(f"❌ Cannot consume quota - no interactions remaining for user {user_id}")
                return False
            
            # Record the AI interaction
            interaction_data = {
                'user_id': user_id,
                'feature_type': feature_type.value,
                'feature_details': feature_details or {},
                'tokens_used': cost_tokens,
                'success': True,
                'created_at': datetime.utcnow().isoformat()
            }
            
            response = self.supabase.table('ai_interactions').insert(interaction_data).execute()
            
            if response.data:
                new_quota = await self.get_user_quota(user_id)
                logger.info(f"✅ AI quota consumed: {feature_type.value} for user {user_id}. Remaining: {new_quota['remaining']}")
                return True
            else:
                logger.error(f"❌ Failed to record AI interaction: {response}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error consuming quota: {e}")
            return False
    
    async def log_ai_interaction(self, user_id: str, feature_type: AIFeatureType,
                               success: bool, error_message: str = None,
                               feature_details: Dict[str, Any] = None,
                               tokens_used: int = 0) -> bool:
        """Log an AI interaction attempt (regardless of success)"""
        try:
            interaction_data = {
                'user_id': user_id,
                'feature_type': feature_type.value,
                'feature_details': feature_details or {},
                'tokens_used': tokens_used,
                'success': success,
                'error_message': error_message,
                'created_at': datetime.utcnow().isoformat()
            }
            
            # Only consume quota if the interaction was successful
            if success:
                response = self.supabase.table('ai_interactions').insert(interaction_data).execute()
                if response.data:
                    logger.info(f"✅ AI interaction logged: {feature_type.value} (success={success})")
                    return True
            else:
                logger.warning(f"⚠️  AI interaction failed, not consuming quota: {feature_type.value} - {error_message}")
                
        except Exception as e:
            logger.error(f"❌ Error logging AI interaction: {e}")
            
        return False
    
    async def _get_usage_breakdown(self, user_id: str, month_start: datetime) -> Dict[str, int]:
        """Get breakdown of AI usage by feature type"""
        try:
            response = self.supabase.table('ai_interactions').select(
                'feature_type'
            ).eq('user_id', user_id).gte(
                'created_at', month_start.isoformat()
            ).eq('success', True).execute()
            
            interactions = response.data or []
            
            # Count by feature type
            breakdown = {}
            for interaction in interactions:
                feature = interaction.get('feature_type', 'unknown')
                breakdown[feature] = breakdown.get(feature, 0) + 1
            
            return breakdown
            
        except Exception as e:
            logger.error(f"❌ Error getting usage breakdown: {e}")
            return {}
    
    async def get_usage_analytics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get detailed usage analytics for a user"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            response = self.supabase.table('ai_interactions').select('*').eq(
                'user_id', user_id
            ).gte('created_at', cutoff_date.isoformat()).execute()
            
            interactions = response.data or []
            
            # Analyze usage patterns
            total_interactions = len(interactions)
            successful_interactions = len([i for i in interactions if i.get('success')])
            success_rate = successful_interactions / total_interactions if total_interactions > 0 else 0
            
            # Feature usage breakdown
            feature_usage = {}
            for interaction in interactions:
                feature = interaction.get('feature_type', 'unknown')
                if feature not in feature_usage:
                    feature_usage[feature] = {'count': 0, 'success': 0}
                feature_usage[feature]['count'] += 1
                if interaction.get('success'):
                    feature_usage[feature]['success'] += 1
            
            # Calculate success rates by feature
            for feature, stats in feature_usage.items():
                stats['success_rate'] = stats['success'] / stats['count'] if stats['count'] > 0 else 0
            
            return {
                'total_interactions': total_interactions,
                'successful_interactions': successful_interactions,
                'success_rate': success_rate,
                'feature_usage': feature_usage,
                'period_days': days,
                'most_used_feature': max(feature_usage.keys(), key=lambda k: feature_usage[k]['count']) if feature_usage else None
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting usage analytics: {e}")
            return {}

# Global service instance
ai_quota_service = AIQuotaService()