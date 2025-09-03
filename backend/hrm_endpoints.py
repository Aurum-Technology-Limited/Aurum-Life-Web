"""
HRM Phase 3: API Endpoints for Hierarchical Reasoning Model
Reference: aurum_life_hrm_phase3_prd.md - Section 4.1
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from typing import List, Dict, Optional, Any
import logging

from supabase_auth import get_current_active_user
from models import User
from hrm_service import HierarchicalReasoningModel, AnalysisDepth
from blackboard_service import blackboard, InsightPriority
from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Create router for HRM endpoints
hrm_router = APIRouter(prefix="/api/hrm", tags=["HRM"])

# Request/Response Models
class AnalyzeEntityRequest(BaseModel):
    entity_type: str  # pillar, area, project, task, global
    entity_id: Optional[str] = None
    analysis_depth: str = "balanced"  # minimal, balanced, detailed
    force_llm: bool = False

class InsightFeedbackRequest(BaseModel):
    feedback: str  # accepted, rejected, modified, ignored
    feedback_details: Optional[Dict[str, Any]] = None

class GetInsightsRequest(BaseModel):
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    insight_type: Optional[str] = None
    is_active: Optional[bool] = True
    is_pinned: Optional[bool] = None
    min_confidence: Optional[float] = None
    tags: Optional[List[str]] = None
    limit: int = 50
    include_expired: bool = False

@hrm_router.post("/analyze")
async def analyze_entity(
    request: AnalyzeEntityRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    """
    Perform HRM analysis on any entity with quota tracking.
    CONSUMES: 1 AI interaction per analysis
    """
    try:
        # Check quota before proceeding
        from ai_quota_service import ai_quota_service, AIFeatureType
        has_quota, quota_info = await ai_quota_service.check_quota_available(
            str(current_user.id), AIFeatureType.HRM_ANALYSIS
        )
        
        if not has_quota:
            raise HTTPException(
                status_code=429,
                detail=f"AI quota exceeded. You have {quota_info['remaining']} interactions remaining this month."
            )
        
        start_time = datetime.utcnow()
        
        # Initialize HRM for user
        hrm = HierarchicalReasoningModel(str(current_user.id))
        
        # Convert analysis depth
        depth_map = {
            'minimal': AnalysisDepth.MINIMAL,
            'balanced': AnalysisDepth.BALANCED,
            'detailed': AnalysisDepth.DETAILED
        }
        depth = depth_map.get(request.analysis_depth, AnalysisDepth.BALANCED)
        
        # Perform analysis
        insight = await hrm.analyze_entity(
            entity_type=request.entity_type,
            entity_id=request.entity_id,
            analysis_depth=depth,
            force_llm=request.force_llm
        )
        
        # Record successful AI interaction
        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        await ai_quota_service.log_ai_interaction(
            str(current_user.id),
            AIFeatureType.HRM_ANALYSIS,
            success=True,
            feature_details={
                'entity_type': request.entity_type,
                'entity_id': request.entity_id,
                'analysis_depth': request.analysis_depth,
                'force_llm': request.force_llm
            },
            tokens_used=processing_time
        )
        
        logger.info(f"✅ AI quota consumed: hrm_analysis for user {current_user.id}")
        
        # Return insight data
        response = {
            'insight_id': insight.insight_id,
            'entity_type': insight.entity_type,
            'entity_id': insight.entity_id,
            'insight_type': insight.insight_type,
            'title': insight.title,
            'summary': insight.summary,
            'confidence_score': insight.confidence_score,
            'impact_score': insight.impact_score,
            'reasoning_path': insight.reasoning_path,
            'recommendations': insight.recommendations,
            'expires_at': insight.expires_at.isoformat() if insight.expires_at else None,
            'analysis_depth': request.analysis_depth,
            'used_llm': 'llm_insights' in insight.detailed_reasoning
        }
        
        logger.info(f"✅ HRM analysis completed for {request.entity_type}:{request.entity_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ HRM analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@hrm_router.get("/insights")
async def get_insights(
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[str] = Query(None),
    insight_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(True),
    is_pinned: Optional[bool] = Query(None),
    min_confidence: Optional[float] = Query(None),
    tags: Optional[str] = Query(None),  # Comma-separated tags
    limit: int = Query(50, ge=1, le=200),
    include_expired: bool = Query(False),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get insights from the blackboard with filtering options
    
    Supports filtering by:
    - entity_type: pillar, area, project, task, global
    - entity_id: specific entity ID
    - insight_type: priority_reasoning, alignment_analysis, etc.
    - is_active: active insights only
    - is_pinned: pinned insights only
    - min_confidence: minimum confidence score
    - tags: comma-separated list of tags to match
    """
    try:
        # Build filters
        filters = {}
        if entity_type:
            filters['entity_type'] = entity_type
        if entity_id:
            filters['entity_id'] = entity_id
        if insight_type:
            filters['insight_type'] = insight_type
        if is_active is not None:
            filters['is_active'] = is_active
        if is_pinned is not None:
            filters['is_pinned'] = is_pinned
        if min_confidence is not None:
            filters['min_confidence'] = min_confidence
        if tags:
            filters['tags'] = tags.split(',')
        
        # Get insights from blackboard
        insights = await blackboard.get_insights(
            user_id=str(current_user.id),
            filters=filters,
            limit=limit,
            include_expired=include_expired
        )
        
        return {
            'insights': insights,
            'total': len(insights),
            'filters_applied': filters
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get insights: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve insights: {str(e)}")

@hrm_router.get("/insights/{insight_id}")
async def get_insight_by_id(
    insight_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get specific insight by ID"""
    try:
        insight = await blackboard.get_insight_by_id(str(current_user.id), insight_id)
        
        if not insight:
            raise HTTPException(status_code=404, detail="Insight not found")
        
        return insight
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get insight {insight_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@hrm_router.post("/insights/{insight_id}/feedback")
async def provide_insight_feedback(
    insight_id: str,
    request: InsightFeedbackRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Provide feedback on an insight for model improvement
    
    Feedback types:
    - accepted: User found the insight helpful and acted on it
    - rejected: User disagreed with the insight
    - modified: User agreed partially but made modifications
    - ignored: User saw the insight but didn't act on it
    """
    try:
        success = await blackboard.update_insight_feedback(
            user_id=str(current_user.id),
            insight_id=insight_id,
            feedback=request.feedback,
            feedback_details=request.feedback_details
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Insight not found or update failed")
        
        return {
            'success': True,
            'message': 'Feedback recorded successfully',
            'insight_id': insight_id,
            'feedback': request.feedback
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to record feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@hrm_router.post("/insights/{insight_id}/pin")
async def pin_insight(
    insight_id: str,
    pinned: bool = True,
    current_user: User = Depends(get_current_active_user)
):
    """Pin or unpin an insight"""
    try:
        success = await blackboard.pin_insight(
            user_id=str(current_user.id),
            insight_id=insight_id,
            pinned=pinned
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Insight not found")
        
        return {
            'success': True,
            'message': f'Insight {"pinned" if pinned else "unpinned"} successfully',
            'insight_id': insight_id,
            'pinned': pinned
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to pin insight: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@hrm_router.delete("/insights/{insight_id}")
async def deactivate_insight(
    insight_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Deactivate an insight (soft delete)"""
    try:
        success = await blackboard.deactivate_insight(
            user_id=str(current_user.id),
            insight_id=insight_id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Insight not found")
        
        return {
            'success': True,
            'message': 'Insight deactivated successfully',
            'insight_id': insight_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to deactivate insight: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@hrm_router.get("/statistics")
async def get_insight_statistics(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get insight statistics for dashboard
    
    Returns statistics including:
    - Total insights generated
    - Average confidence score
    - User feedback rates
    - Insights by type breakdown
    - Confidence trend over time
    """
    try:
        stats = await blackboard.get_insight_statistics(
            user_id=str(current_user.id),
            days=days
        )
        
        return {
            'statistics': stats,
            'period_days': days,
            'generated_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get insight statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@hrm_router.post("/prioritize-today")
async def get_today_priorities(
    top_n: int = Query(5, ge=1, le=20),
    include_reasoning: bool = Query(True),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get AI-prioritized tasks for today with HRM reasoning
    
    This endpoint:
    1. Gets all active tasks for the user
    2. Applies HRM analysis for priority scoring  
    3. Returns top N tasks with reasoning
    4. Includes coaching messages when available
    """
    try:
        # Initialize HRM for user
        hrm = HierarchicalReasoningModel(str(current_user.id))
        
        # Get today's priorities using the existing AI coach service method
        # but enhanced with full HRM reasoning
        from ai_coach_mvp_service import AiCoachMvpService
        ai_coach = AiCoachMvpService()
        
        # Get prioritized tasks
        priorities = await ai_coach.get_today_priorities(
            user_id=str(current_user.id),
            coaching_top_n=top_n
        )
        
        # Enhance with HRM insights if requested
        if include_reasoning and priorities.get('tasks'):
            enhanced_tasks = []
            for task in priorities['tasks']:
                # Get detailed HRM analysis for high-priority tasks
                if task.get('score', 0) > 50:  # Only for high-scoring tasks
                    try:
                        insight = await hrm.analyze_entity(
                            entity_type='task',
                            entity_id=task['id'],
                            analysis_depth=AnalysisDepth.BALANCED
                        )
                        task['hrm_insight'] = {
                            'confidence_score': insight.confidence_score,
                            'recommendations': insight.recommendations[:2],  # Top 2 recommendations
                            'insight_summary': insight.summary
                        }
                    except Exception as e:
                        logger.warning(f"Failed to get HRM insight for task {task['id']}: {e}")
                
                enhanced_tasks.append(task)
            
            priorities['tasks'] = enhanced_tasks
        
        return priorities
        
    except Exception as e:
        logger.error(f"❌ Failed to get today's priorities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@hrm_router.get("/preferences")
async def get_hrm_preferences(
    current_user: User = Depends(get_current_active_user)
):
    """Get user's HRM preferences"""
    try:
        from supabase_client import get_supabase_client
        supabase = get_supabase_client()
        
        response = supabase.table('hrm_user_preferences').select('*').eq(
            'user_id', str(current_user.id)
        ).execute()
        
        if response.data:
            preferences = response.data[0]
        else:
            # Return default preferences
            preferences = {
                'explanation_detail_level': 'balanced',
                'show_confidence_scores': True,
                'show_reasoning_path': True,
                'ai_personality': 'coach',
                'ai_communication_style': 'encouraging',
                'primary_optimization': 'balance',
                'preferred_work_hours': {'start': '09:00', 'end': '17:00'},
                'energy_pattern': 'steady',
                'enable_ai_learning': True,
                'share_anonymous_insights': False
            }
        
        return preferences
        
    except Exception as e:
        logger.error(f"❌ Failed to get HRM preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class HRMPreferencesUpdate(BaseModel):
    explanation_detail_level: Optional[str] = None
    show_confidence_scores: Optional[bool] = None
    show_reasoning_path: Optional[bool] = None
    ai_personality: Optional[str] = None
    ai_communication_style: Optional[str] = None
    primary_optimization: Optional[str] = None
    preferred_work_hours: Optional[Dict[str, str]] = None
    energy_pattern: Optional[str] = None
    enable_ai_learning: Optional[bool] = None
    share_anonymous_insights: Optional[bool] = None

@hrm_router.put("/preferences")
async def update_hrm_preferences(
    preferences: HRMPreferencesUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update user's HRM preferences"""
    try:
        from supabase_client import get_supabase_client
        from datetime import datetime
        
        supabase = get_supabase_client()
        
        # Filter out None values
        update_data = {
            k: v for k, v in preferences.dict().items() 
            if v is not None
        }
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No preferences to update")
        
        update_data['updated_at'] = datetime.utcnow().isoformat()
        
        # Upsert preferences with proper conflict resolution
        response = supabase.table('hrm_user_preferences').upsert({
            'user_id': str(current_user.id),
            **update_data
        }, on_conflict='user_id').execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to update preferences")
        
        return {
            'success': True,
            'message': 'Preferences updated successfully',
            'preferences': response.data[0]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to update HRM preferences: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background task endpoints
@hrm_router.post("/batch-analyze")
async def batch_analyze_entities(
    background_tasks: BackgroundTasks,
    entity_types: List[str] = Query(..., description="List of entity types to analyze"),
    analysis_depth: str = Query("balanced"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Trigger batch analysis of multiple entity types
    This runs in the background and stores results in the blackboard
    """
    try:
        def run_batch_analysis():
            """Background task function"""
            import asyncio
            asyncio.run(_batch_analyze_impl(str(current_user.id), entity_types, analysis_depth))
        
        background_tasks.add_task(run_batch_analysis)
        
        return {
            'success': True,
            'message': f'Batch analysis started for {len(entity_types)} entity types',
            'entity_types': entity_types,
            'analysis_depth': analysis_depth
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to start batch analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def _batch_analyze_impl(user_id: str, entity_types: List[str], analysis_depth: str):
    """Implementation of batch analysis"""
    try:
        hrm = HierarchicalReasoningModel(user_id)
        depth_map = {
            'minimal': AnalysisDepth.MINIMAL,
            'balanced': AnalysisDepth.BALANCED,
            'detailed': AnalysisDepth.DETAILED
        }
        depth = depth_map.get(analysis_depth, AnalysisDepth.BALANCED)
        
        for entity_type in entity_types:
            try:
                # Analyze each entity type globally
                await hrm.analyze_entity(
                    entity_type=entity_type,
                    entity_id=None,  # Global analysis
                    analysis_depth=depth
                )
                logger.info(f"✅ Completed batch analysis for {entity_type}")
                
            except Exception as e:
                logger.error(f"❌ Batch analysis failed for {entity_type}: {e}")
                continue
        
        logger.info(f"✅ Completed batch analysis for user {user_id}")
        
    except Exception as e:
        logger.error(f"❌ Batch analysis implementation failed: {e}")

# Import datetime for statistics endpoint
from datetime import datetime