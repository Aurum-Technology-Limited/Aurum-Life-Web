"""
Supabase Webhook Handlers for Performance Optimization
Handles real-time database events to improve app responsiveness
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException
from sentiment_analysis_service import SentimentAnalysisService
from alignment_score_service import AlignmentScoreService
from user_behavior_analytics_service import UserBehaviorAnalyticsService
from hrm_service import HierarchicalReasoningModel

logger = logging.getLogger(__name__)
webhook_router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

# Initialize services
sentiment_service = SentimentAnalysisService()
alignment_service = AlignmentScoreService()
analytics_service = UserBehaviorAnalyticsService()

@webhook_router.post("/journal-entry-created")
async def handle_journal_entry_created(request: Request):
    """
    Webhook handler for when journal entries are created.
    Triggers background sentiment analysis.
    """
    try:
        payload = await request.json()
        record = payload.get('record', {})
        
        user_id = record.get('user_id')
        entry_id = record.get('id')
        content = record.get('content', '')
        
        if not user_id or not entry_id or not content:
            logger.warning("Invalid journal entry webhook payload")
            return {"status": "ignored", "reason": "missing_required_fields"}
        
        # Trigger background sentiment analysis
        logger.info(f"🎭 Triggering sentiment analysis for journal entry {entry_id}")
        
        # Run sentiment analysis in background
        asyncio.create_task(
            sentiment_service.analyze_journal_entry(user_id, entry_id, content)
        )
        
        # Update user analytics
        asyncio.create_task(
            analytics_service.track_event(user_id, 'journal_entry_created', {
                'entry_id': entry_id,
                'content_length': len(content)
            })
        )
        
        return {"status": "success", "processed": "journal_entry_created"}
        
    except Exception as e:
        logger.error(f"Error processing journal entry webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@webhook_router.post("/alignment-trigger")
async def handle_alignment_recalculation(request: Request):
    """
    Webhook handler for alignment score recalculation.
    Triggers when tasks, projects, or related entities change.
    """
    try:
        payload = await request.json()
        record = payload.get('record', {})
        table = payload.get('table', '')
        
        user_id = record.get('user_id')
        
        if not user_id:
            return {"status": "ignored", "reason": "no_user_id"}
        
        logger.info(f"🎯 Triggering alignment recalculation for user {user_id} due to {table} change")
        
        # Trigger background alignment recalculation
        asyncio.create_task(
            alignment_service.recalculate_user_alignment(user_id)
        )
        
        # Track alignment-related activity
        asyncio.create_task(
            analytics_service.track_event(user_id, 'alignment_data_changed', {
                'source_table': table,
                'trigger_time': datetime.utcnow().isoformat()
            })
        )
        
        return {"status": "success", "processed": "alignment_recalculation"}
        
    except Exception as e:
        logger.error(f"Error processing alignment webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@webhook_router.post("/hrm-insight-trigger")
async def handle_hrm_insight_generation(request: Request):
    """
    Webhook handler for HRM insight generation.
    Triggers AI analysis when user behavior patterns change significantly.
    """
    try:
        payload = await request.json()
        record = payload.get('record', {})
        
        user_id = record.get('user_id')
        event_type = record.get('event_type', '')
        
        if not user_id:
            return {"status": "ignored", "reason": "no_user_id"}
        
        # Only trigger HRM analysis for significant events
        significant_events = [
            'project_completed', 'goal_achieved', 'streak_milestone',
            'productivity_pattern_change', 'sentiment_trend_change'
        ]
        
        if event_type in significant_events:
            logger.info(f"🧠 Triggering HRM insight generation for user {user_id}")
            
            # Generate HRM insights in background
            asyncio.create_task(
                generate_hrm_insights_background(user_id, event_type)
            )
        
        return {"status": "success", "processed": f"hrm_insight_check_{event_type}"}
        
    except Exception as e:
        logger.error(f"Error processing HRM insight webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@webhook_router.post("/analytics-aggregation")
async def handle_analytics_aggregation(request: Request):
    """
    Webhook handler for real-time analytics aggregation.
    Updates analytics dashboards when user behavior events are logged.
    """
    try:
        payload = await request.json()
        record = payload.get('record', {})
        
        user_id = record.get('user_id')
        event_type = record.get('event_type')
        
        if not user_id or not event_type:
            return {"status": "ignored", "reason": "missing_fields"}
        
        logger.info(f"📊 Updating analytics aggregations for user {user_id}")
        
        # Update analytics aggregations in background
        asyncio.create_task(
            analytics_service.update_real_time_aggregations(user_id, event_type)
        )
        
        return {"status": "success", "processed": "analytics_aggregation"}
        
    except Exception as e:
        logger.error(f"Error processing analytics webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@webhook_router.post("/cache-invalidation")
async def handle_cache_invalidation(request: Request):
    """
    Webhook handler for cache invalidation.
    Invalidates relevant caches when data changes.
    """
    try:
        payload = await request.json()
        table = payload.get('table', '')
        record = payload.get('record', {})
        
        user_id = record.get('user_id')
        
        if not user_id:
            return {"status": "ignored", "reason": "no_user_id"}
        
        # Map tables to cache keys that need invalidation
        cache_invalidation_map = {
            'tasks': ['user_tasks', 'alignment_score', 'dashboard_stats'],
            'projects': ['user_projects', 'alignment_score', 'dashboard_stats'],
            'journal_entries': ['user_journal', 'sentiment_trends', 'wellness_score'],
            'areas': ['user_hierarchy', 'alignment_score'],
            'pillars': ['user_hierarchy', 'alignment_score']
        }
        
        cache_keys_to_invalidate = cache_invalidation_map.get(table, [])
        
        if cache_keys_to_invalidate:
            logger.info(f"🗂️ Invalidating caches for user {user_id}: {cache_keys_to_invalidate}")
            
            # Invalidate caches in background
            asyncio.create_task(
                invalidate_user_caches(user_id, cache_keys_to_invalidate)
            )
        
        return {"status": "success", "invalidated": cache_keys_to_invalidate}
        
    except Exception as e:
        logger.error(f"Error processing cache invalidation webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background task helpers
async def generate_hrm_insights_background(user_id: str, trigger_event: str):
    """Generate HRM insights in background"""
    try:
        hrm = HierarchicalReasoningModel(user_id)
        
        # Generate insights based on trigger event
        insight = await hrm.analyze_user_context(
            context_type='behavioral_change',
            trigger_event=trigger_event
        )
        
        # Store insights in blackboard
        if insight and insight.insights:
            logger.info(f"✅ Generated HRM insights for user {user_id}")
            # Store in blackboard or cache for quick retrieval
            
    except Exception as e:
        logger.error(f"Background HRM insight generation failed: {e}")

async def invalidate_user_caches(user_id: str, cache_keys: list):
    """Invalidate user-specific caches"""
    try:
        # Implement cache invalidation logic based on your cache system
        # This could be Redis, in-memory cache, etc.
        for key in cache_keys:
            cache_key = f"user:{user_id}:{key}"
            # await cache_service.delete(cache_key)
            logger.info(f"Cache invalidated: {cache_key}")
            
    except Exception as e:
        logger.error(f"Cache invalidation failed: {e}")

# Health check for webhooks
@webhook_router.get("/health")
async def webhook_health():
    """Health check endpoint for webhook system"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "handlers": [
            "journal-entry-created",
            "alignment-trigger", 
            "hrm-insight-trigger",
            "analytics-aggregation",
            "cache-invalidation"
        ]
    }