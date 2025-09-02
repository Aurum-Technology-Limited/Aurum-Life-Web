from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends, status, Request, UploadFile, File, Form, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from pydantic import BaseModel
from pathlib import Path as PathlibPath
import os
import logging
from typing import List, Optional
from datetime import datetime
import uuid

# Import our models and services
from supabase_client import supabase_manager
from models import *
from user_behavior_analytics_service import UserBehaviorAnalyticsService
from optimized_services import (
    OptimizedPillarService, 
    OptimizedAreaService, 
    OptimizedProjectService,
    OptimizedStatsService
)
from performance_monitor import perf_monitor
from services import (
    UserService, TaskService, JournalService, 
    CourseService, RecurringTaskService, InsightsService, 
    ResourceService, StatsService, PillarService, AreaService, ProjectService,
    ProjectTemplateService, GoogleAuthService
)
from supabase_services import SupabasePillarService, SupabaseAreaService, SupabaseProjectService, SupabaseTaskService
from supabase_auth import get_current_active_user
from supabase_auth_endpoints import auth_router
from analytics_service import AnalyticsService
from user_behavior_analytics_service import UserBehaviorAnalyticsService
from sentiment_analysis_service import SentimentAnalysisService
from alignment_score_service import AlignmentScoreService
from ai_coach_mvp_service import AiCoachMvpService
from hrm_endpoints import hrm_router

ROOT_DIR = PathlibPath(__file__).parent
load_dotenv(ROOT_DIR / '.env')

app = FastAPI(title="Aurum Life API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@api_router.get("/")
async def root():
    return {"message": "Aurum Life API is running", "version": "1.0.0"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/")
async def root():
    return {"message": "Aurum Life API", "version": "1.0.0", "status": "running"}

@app.get("/favicon.ico")
async def favicon():
    return {"message": "No favicon configured"}

@api_router.get("/test-fast")
async def test_fast_endpoint():
    return {"status": "fast", "message": "Optimizations working", "timestamp": datetime.utcnow().isoformat()}

alignment_service = AlignmentScoreService()
ai_coach_service = AiCoachMvpService()
user_behavior_analytics_service = UserBehaviorAnalyticsService()
sentiment_analysis_service = SentimentAnalysisService()

# Upload endpoints omitted for brevity (unchanged)

# Essential API endpoints
@api_router.get("/pillars")
async def get_pillars(current_user: User = Depends(get_current_active_user)):
    try:
        service = SupabasePillarService()
        return await service.get_user_pillars(str(current_user.id))
    except Exception as e:
        logger.error(f"Error getting pillars: {e}")
        raise HTTPException(status_code=500, detail="Failed to get pillars")

@api_router.post("/pillars")
async def create_pillar(payload: PillarCreate, current_user: User = Depends(get_current_active_user)):
    try:
        result = await SupabasePillarService.create_pillar(str(current_user.id), payload)
        return result
    except Exception as e:
        logger.error(f"Error creating pillar: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/areas")
async def get_areas(current_user: User = Depends(get_current_active_user)):
    try:
        service = SupabaseAreaService()
        return await service.get_user_areas(str(current_user.id))
    except Exception as e:
        logger.error(f"Error getting areas: {e}")
        raise HTTPException(status_code=500, detail="Failed to get areas")

@api_router.post("/areas")
async def create_area(payload: AreaCreate, current_user: User = Depends(get_current_active_user)):
    try:
        result = await SupabaseAreaService.create_area(str(current_user.id), payload)
        return result
    except Exception as e:
        logger.error(f"Error creating area: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/projects")
async def get_projects(current_user: User = Depends(get_current_active_user)):
    try:
        service = SupabaseProjectService()
        return await service.get_user_projects(str(current_user.id))
    except Exception as e:
        logger.error(f"Error getting projects: {e}")
        raise HTTPException(status_code=500, detail="Failed to get projects")

@api_router.post("/projects")
async def create_project(payload: ProjectCreate, current_user: User = Depends(get_current_active_user)):
    try:
        result = await SupabaseProjectService.create_project(str(current_user.id), payload)
        return result
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/tasks")
async def get_tasks(
    project_id: Optional[str] = Query(default=None),
    q: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    priority: Optional[str] = Query(default=None),
    due_date: Optional[str] = Query(default=None),
    page: Optional[int] = Query(default=None, ge=1),
    limit: Optional[int] = Query(default=None, ge=1, le=200),
    return_meta: Optional[bool] = Query(default=False),
    current_user: User = Depends(get_current_active_user)
):
    try:
        task_service = TaskService()
        all_tasks = await task_service.get_user_tasks(
            str(current_user.id),
            project_id=project_id,
            q=q,
            status=status,
            priority=priority,
            due_date=due_date,
        )
        if not page or not limit:
            return all_tasks
        total = len(all_tasks)
        start = (page - 1) * limit
        end = start + limit
        page_items = all_tasks[start:end]
        if return_meta:
            return {"tasks": page_items, "total": total, "page": page, "limit": limit, "has_more": end < total}
        return page_items
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to get tasks")

@api_router.post("/tasks")
async def create_task(payload: TaskCreate, current_user: User = Depends(get_current_active_user)):
    try:
        result = await SupabaseTaskService.create_task(str(current_user.id), payload)
        return result
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@api_router.get("/insights")
async def get_insights(
    date_range: Optional[str] = Query(default='all_time'),
    area_id: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_active_user)
):
    try:
        insights_service = InsightsService()
        return await insights_service.get_user_insights(str(current_user.id), date_range=date_range, area_id=area_id)
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to get insights")

@api_router.get("/journal")
async def get_journal(current_user: User = Depends(get_current_active_user)):
    try:
        journal_service = JournalService()
        return await journal_service.get_user_entries(str(current_user.id))
    except Exception as e:
        logger.error(f"Error getting journal entries: {e}")
        raise HTTPException(status_code=500, detail="Failed to get journal entries")

# ================================
# AI COACH ENDPOINTS (HRM-Enhanced)
# ================================

@api_router.get("/ai/quota", tags=["AI Coach"])
async def get_ai_quota(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user's AI interaction quota for the current month
    
    Returns:
        dict: Quota information with remaining and total interactions
    """
    try:
        from calendar import monthrange
        from datetime import datetime, timedelta
        import calendar
        
        # Get current month boundaries
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate next month start
        if now.month == 12:
            next_month = month_start.replace(year=month_start.year + 1, month=1)
        else:
            next_month = month_start.replace(month=month_start.month + 1)
        
        # For MVP, we'll implement a simple quota system
        # In production, this would track actual AI usage from a quota table
        monthly_quota = 50  # 50 AI interactions per month
        
        # Count AI coach interactions for this month
        # This is a simplified implementation - in production you'd track this in a dedicated table
        used_quota = 0  # For new users, start with 0 used
        
        remaining = max(0, monthly_quota - used_quota)
        
        return {
            'remaining': remaining,
            'total': monthly_quota,
            'used': used_quota,
            'resets_at': next_month.isoformat(),
            'period': 'monthly'
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get AI quota: {e}")
        # Return default quota on error
        return {
            'remaining': 10,
            'total': 10,
            'used': 0,
            'resets_at': None,
            'period': 'monthly'
        }

@api_router.get("/ai/task-why-statements", response_model=TaskWhyStatementResponse, tags=["AI Coach"])
async def get_task_why_statements(
    task_ids: Optional[List[str]] = Query(None, description="Specific task IDs to analyze"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate contextual why statements for tasks with HRM-enhanced reasoning.
    
    This endpoint provides intelligent explanations for why tasks matter,
    connecting them to the user's broader goals and hierarchy.
    
    Enhanced with HRM:
    - Confidence scores for each explanation
    - Hierarchical reasoning paths
    - Personalized recommendations
    """
    try:
        # Get basic why statements from AI Coach service with HRM enhancement
        enhanced_response = await ai_coach_service.generate_task_why_statements(
            user_id=str(current_user.id),
            task_ids=task_ids,
            use_hrm=True
        )
        
        return enhanced_response
        
    except Exception as e:
        logger.error(f"Error generating task why statements: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate why statements")

@api_router.get("/ai/suggest-focus", tags=["AI Coach"])
async def suggest_focus_tasks(
    top_n: int = Query(5, ge=1, le=20, description="Number of tasks to suggest"),
    include_reasoning: bool = Query(True, description="Include HRM reasoning"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get AI-suggested focus tasks with HRM prioritization and detailed reasoning.
    
    This endpoint uses the Hierarchical Reasoning Model to intelligently
    prioritize tasks based on multiple factors and provides transparent reasoning.
    
    Enhanced with HRM:
    - Confidence scores for priority rankings
    - Detailed reasoning paths
    - Personalized recommendations
    - Alignment analysis
    """
    try:
        # Get today's priorities with HRM enhancement
        priorities = await ai_coach_service.get_today_priorities(
            user_id=str(current_user.id),
            coaching_top_n=top_n,
            use_hrm=include_reasoning
        )
        
        return priorities
        
    except Exception as e:
        logger.error(f"Error suggesting focus tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to suggest focus tasks")

@api_router.get("/alignment/dashboard", tags=["Alignment"])
async def get_alignment_dashboard(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get comprehensive alignment dashboard data with HRM insights.
    
    This endpoint provides alignment scores, progress tracking, and
    HRM-powered insights about the user's goal alignment.
    
    Enhanced with HRM:
    - Alignment analysis with confidence scores
    - Personalized recommendations for improvement
    - Trend analysis and predictions
    """
    try:
        # Get basic alignment data with HRM enhancement
        basic_data = await alignment_service.get_alignment_dashboard_data(
            user_id=str(current_user.id),
            use_hrm=True
        )
        
        return basic_data
        
    except Exception as e:
        logger.error(f"Error getting alignment dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to get alignment dashboard")

@api_router.get("/ai/today-priorities", tags=["AI Coach"])
async def get_today_priorities_enhanced(
    top_n: int = Query(5, ge=1, le=20, description="Number of top tasks to return"),
    include_hrm: bool = Query(True, description="Include HRM enhancements"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get today's prioritized tasks with enhanced HRM reasoning.
    
    This is an enhanced version of the today priorities endpoint that
    integrates HRM insights for better task prioritization and reasoning.
    
    Enhanced features:
    - HRM confidence scores
    - Detailed reasoning paths
    - Personalized recommendations
    - Coaching messages with AI insights
    """
    try:
        # Get basic priorities with HRM enhancement
        priorities = await ai_coach_service.get_today_priorities(
            user_id=str(current_user.id),
            coaching_top_n=top_n,
            use_hrm=include_hrm
        )
        
        return priorities
        
    except Exception as e:
        logger.error(f"Error getting today's priorities: {e}")
        raise HTTPException(status_code=500, detail="Failed to get today's priorities")

# ================================
# SEMANTIC SEARCH ENDPOINTS
# ================================

@api_router.get("/semantic/search", tags=["Semantic Search"])
async def semantic_search(
    query: str = Query(..., description="Search query text"),
    content_types: Optional[List[str]] = Query(default=["all"], description="Content types to search: journal_entry, task, project, daily_reflection, ai_insight, or all"),
    limit: int = Query(default=10, ge=1, le=50, description="Maximum number of results"),
    min_similarity: float = Query(default=0.3, ge=0.0, le=1.0, description="Minimum similarity threshold"),
    date_range_days: Optional[int] = Query(default=None, ge=1, le=365, description="Limit search to recent days"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Perform semantic search across user's content using pgvector RAG capabilities.
    
    This endpoint:
    1. Generates embeddings for the search query
    2. Uses pgvector similarity search across multiple content types
    3. Returns ranked results with confidence scores
    4. Supports filtering by content type and date range
    """
    try:
        from supabase_client import get_supabase_client
        import openai
        import os
        
        # Initialize OpenAI client for embeddings
        openai.api_key = os.getenv('OPENAI_API_KEY')
        if not openai.api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        # Generate embedding for search query
        try:
            embedding_response = openai.embeddings.create(
                model="text-embedding-3-small",
                input=query
            )
            query_embedding = embedding_response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise HTTPException(status_code=500, detail="Failed to generate search embedding")
        
        # Get Supabase client
        supabase = get_supabase_client()
        
        # Determine if we should search all content types
        search_all = "all" in content_types or len(content_types) == 0
        
        # Use the existing rag_search function for comprehensive search
        if search_all:
            # Call the rag_search function
            try:
                result = supabase.rpc('rag_search', {
                    'query_embedding': query_embedding,
                    'user_id_filter': str(current_user.id),
                    'match_count': limit,
                    'date_range_days': date_range_days
                }).execute()
                
                search_results = result.data or []
            except Exception as e:
                logger.error(f"RAG search failed: {e}")
                # Fallback to individual searches
                search_results = []
        else:
            # Search specific content types
            search_results = []
            
            # Search journal entries
            if "journal_entry" in content_types:
                try:
                    result = supabase.rpc('find_similar_journal_entries', {
                        'query_embedding': query_embedding,
                        'match_count': limit // len(content_types) + 1,
                        'user_id_filter': str(current_user.id)
                    }).execute()
                    
                    for item in result.data or []:
                        search_results.append({
                            'entity_type': 'journal_entry',
                            'entity_id': item['id'],
                            'title': item['title'],
                            'content': item['content'][:300] + '...' if len(item['content']) > 300 else item['content'],
                            'similarity': item['similarity'],
                            'created_at': item['created_at'],
                            'metadata': {}
                        })
                except Exception as e:
                    logger.warning(f"Journal search failed: {e}")
            
            # Search tasks
            if "task" in content_types:
                try:
                    result = supabase.rpc('find_similar_tasks', {
                        'query_embedding': query_embedding,
                        'match_count': limit // len(content_types) + 1,
                        'user_id_filter': str(current_user.id),
                        'include_completed': True
                    }).execute()
                    
                    for item in result.data or []:
                        search_results.append({
                            'entity_type': 'task',
                            'entity_id': item['id'],
                            'title': item['name'],
                            'content': item['description'] or '',
                            'similarity': item['similarity'],
                            'created_at': None,  # Tasks don't have created_at in the function
                            'metadata': {
                                'status': item['status'],
                                'project_name': item['project_name']
                            }
                        })
                except Exception as e:
                    logger.warning(f"Task search failed: {e}")
        
        # Filter by minimum similarity
        filtered_results = [
            result for result in search_results 
            if result['similarity'] >= min_similarity
        ]
        
        # Sort by similarity (descending)
        filtered_results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Limit results
        final_results = filtered_results[:limit]
        
        # Format response
        formatted_results = []
        for result in final_results:
            formatted_results.append({
                'id': result['entity_id'],
                'entity_type': result['entity_type'],
                'title': result['title'],
                'content_preview': result['content'][:200] + '...' if len(result['content']) > 200 else result['content'],
                'similarity_score': round(result['similarity'] * 100, 1),  # Convert to percentage
                'confidence_level': 'high' if result['similarity'] > 0.8 else 'medium' if result['similarity'] > 0.6 else 'low',
                'created_at': result['created_at'],
                'metadata': result.get('metadata', {}),
                'entity_icon': _get_entity_icon(result['entity_type']),
                'entity_display_name': _get_entity_display_name(result['entity_type'])
            })
        
        return {
            'query': query,
            'results': formatted_results,
            'total_results': len(formatted_results),
            'search_metadata': {
                'content_types_searched': content_types if not search_all else ['journal_entry', 'task', 'project', 'daily_reflection', 'ai_insight'],
                'min_similarity_threshold': min_similarity,
                'date_range_days': date_range_days,
                'embedding_model': 'text-embedding-3-small'
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Semantic search failed: {str(e)}")

@api_router.get("/semantic/similar/{entity_type}/{entity_id}", tags=["Semantic Search"])
async def find_similar_content(
    entity_type: str,
    entity_id: str,
    limit: int = Query(default=5, ge=1, le=20, description="Maximum number of similar items"),
    min_similarity: float = Query(default=0.4, ge=0.0, le=1.0, description="Minimum similarity threshold"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Find content similar to a specific entity (task, project, journal entry).
    
    This endpoint:
    1. Retrieves the embedding for the specified entity
    2. Searches for similar content across all types
    3. Returns ranked similar items with confidence scores
    """
    try:
        from supabase_client import get_supabase_client
        
        supabase = get_supabase_client()
        
        # Get the entity's embedding based on type
        entity_embedding = None
        entity_title = ""
        
        if entity_type == "journal_entry":
            result = supabase.table('journal_entries').select('content_embedding, title').eq('id', entity_id).eq('user_id', str(current_user.id)).single().execute()
            if result.data:
                entity_embedding = result.data['content_embedding']
                entity_title = result.data['title']
        elif entity_type == "task":
            result = supabase.table('tasks').select('description_embedding, name').eq('id', entity_id).eq('user_id', str(current_user.id)).single().execute()
            if result.data:
                entity_embedding = result.data['description_embedding']
                entity_title = result.data['name']
        elif entity_type == "project":
            result = supabase.table('projects').select('combined_embedding, name').eq('id', entity_id).eq('user_id', str(current_user.id)).single().execute()
            if result.data:
                entity_embedding = result.data['combined_embedding']
                entity_title = result.data['name']
        
        if not entity_embedding:
            raise HTTPException(status_code=404, detail=f"Entity not found or no embedding available for {entity_type}:{entity_id}")
        
        # Use RAG search to find similar content
        try:
            result = supabase.rpc('rag_search', {
                'query_embedding': entity_embedding,
                'user_id_filter': str(current_user.id),
                'match_count': limit + 1,  # +1 to account for the original entity
                'date_range_days': None
            }).execute()
            
            search_results = result.data or []
        except Exception as e:
            logger.error(f"Similar content search failed: {e}")
            raise HTTPException(status_code=500, detail="Failed to find similar content")
        
        # Filter out the original entity and apply similarity threshold
        filtered_results = [
            result for result in search_results 
            if result['entity_id'] != entity_id and result['similarity'] >= min_similarity
        ]
        
        # Limit results
        final_results = filtered_results[:limit]
        
        # Format response
        formatted_results = []
        for result in final_results:
            formatted_results.append({
                'id': result['entity_id'],
                'entity_type': result['entity_type'],
                'title': result['title'],
                'content_preview': result['content'][:200] + '...' if len(result['content']) > 200 else result['content'],
                'similarity_score': round(result['similarity'] * 100, 1),
                'confidence_level': 'high' if result['similarity'] > 0.8 else 'medium' if result['similarity'] > 0.6 else 'low',
                'created_at': result['created_at'],
                'metadata': result.get('metadata', {}),
                'entity_icon': _get_entity_icon(result['entity_type']),
                'entity_display_name': _get_entity_display_name(result['entity_type'])
            })
        
        return {
            'source_entity': {
                'id': entity_id,
                'type': entity_type,
                'title': entity_title
            },
            'similar_content': formatted_results,
            'total_results': len(formatted_results),
            'search_metadata': {
                'min_similarity_threshold': min_similarity,
                'embedding_model': 'text-embedding-3-small'
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Find similar content failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to find similar content: {str(e)}")

def _get_entity_icon(entity_type: str) -> str:
    """Get icon name for entity type"""
    icons = {
        'journal_entry': 'BookOpen',
        'task': 'CheckSquare',
        'project': 'Folder',
        'daily_reflection': 'Sun',
        'ai_insight': 'Brain'
    }
    return icons.get(entity_type, 'Circle')

def _get_entity_display_name(entity_type: str) -> str:
    """Get display name for entity type"""
    names = {
        'journal_entry': 'Journal Entry',
        'task': 'Task',
        'project': 'Project',
        'daily_reflection': 'Daily Reflection',
        'ai_insight': 'AI Insight'
    }
    return names.get(entity_type, entity_type.replace('_', ' ').title())

# ================================
# USER BEHAVIOR ANALYTICS ENDPOINTS
# ================================

@api_router.post("/analytics/track-event", tags=["Analytics"])
async def track_user_behavior_event(
    event: UserBehaviorEventCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Track a user behavior event for analytics
    
    This endpoint:
    1. Validates user consent for the event type
    2. Records the behavior event with privacy compliance
    3. Updates session counters if applicable
    4. Returns tracking confirmation
    """
    try:
        result = await user_behavior_analytics_service.track_event(str(current_user.id), event)
        return result
        
    except Exception as e:
        logger.error(f"Error tracking behavior event: {e}")
        raise HTTPException(status_code=500, detail="Failed to track behavior event")

@api_router.post("/analytics/start-session", tags=["Analytics"])
async def start_user_session(
    session: UserSessionCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Start a new user session for analytics tracking
    
    This endpoint:
    1. Creates a new user session record
    2. Initializes session counters
    3. Records device and browser information
    4. Returns session confirmation
    """
    try:
        result = await user_behavior_analytics_service.start_session(str(current_user.id), session)
        return result
        
    except Exception as e:
        logger.error(f"Error starting user session: {e}")
        raise HTTPException(status_code=500, detail="Failed to start user session")

@api_router.post("/analytics/end-session/{session_id}", tags=["Analytics"])
async def end_user_session(
    session_id: str,
    exit_page: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    End a user session and calculate final metrics
    
    This endpoint:
    1. Calculates session duration
    2. Records exit page if provided
    3. Marks session as inactive
    4. Returns session summary
    """
    try:
        result = await user_behavior_analytics_service.end_session(
            str(current_user.id), 
            session_id, 
            exit_page
        )
        return result
        
    except Exception as e:
        logger.error(f"Error ending user session: {e}")
        raise HTTPException(status_code=500, detail="Failed to end user session")

@api_router.get("/analytics/preferences", tags=["Analytics"])
async def get_analytics_preferences(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user's analytics preferences and consent settings
    
    Returns:
        User's current analytics preferences including consent settings,
        data retention preferences, and feature-specific tracking options
    """
    try:
        preferences = await user_behavior_analytics_service.get_user_analytics_preferences(
            str(current_user.id)
        )
        return preferences
        
    except Exception as e:
        logger.error(f"Error getting analytics preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics preferences")

@api_router.put("/analytics/preferences", tags=["Analytics"])
async def update_analytics_preferences(
    preferences: UserAnalyticsPreferencesUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update user's analytics preferences and consent settings
    
    This endpoint allows users to:
    1. Grant or revoke consent for different types of tracking
    2. Adjust data retention periods
    3. Enable/disable specific feature tracking
    4. Control anonymous data sharing
    """
    try:
        result = await user_behavior_analytics_service.update_user_analytics_preferences(
            str(current_user.id), 
            preferences
        )
        return result
        
    except Exception as e:
        logger.error(f"Error updating analytics preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to update analytics preferences")

@api_router.get("/analytics/dashboard", tags=["Analytics"])
async def get_analytics_dashboard(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to include in analytics"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get comprehensive analytics dashboard data
    
    This endpoint provides:
    1. User engagement metrics (sessions, time spent, interactions)
    2. AI feature usage statistics with success rates
    3. Daily usage trends and patterns
    4. Top used features and navigation patterns
    5. Privacy-compliant data aggregation
    """
    try:
        dashboard_data = await user_behavior_analytics_service.get_analytics_dashboard(
            str(current_user.id), 
            days
        )
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Error getting analytics dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics dashboard")

@api_router.get("/analytics/ai-features", tags=["Analytics"])
async def get_ai_feature_usage(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed AI feature usage analytics
    
    Returns:
        Detailed statistics for each AI feature including:
        - Total sessions and interactions
        - Time spent per feature
        - Success rates and error patterns
        - Usage trends over time
    """
    try:
        stats = await user_behavior_analytics_service.get_ai_feature_usage_stats(
            str(current_user.id), 
            days
        )
        return {"ai_features": stats, "period_days": days}
        
    except Exception as e:
        logger.error(f"Error getting AI feature usage: {e}")
        raise HTTPException(status_code=500, detail="Failed to get AI feature usage")

@api_router.get("/analytics/engagement", tags=["Analytics"])
async def get_user_engagement_metrics(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user engagement metrics
    
    Returns:
        Engagement metrics including session counts, duration,
        page views, bounce rate, and return user patterns
    """
    try:
        metrics = await user_behavior_analytics_service.get_user_engagement_metrics(
            str(current_user.id), 
            days
        )
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting engagement metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get engagement metrics")

@api_router.post("/analytics/anonymize", tags=["Analytics", "Privacy"])
async def anonymize_analytics_data(
    current_user: User = Depends(get_current_active_user)
):
    """
    Anonymize user's analytics data
    
    This endpoint:
    1. Removes personally identifiable information from analytics records
    2. Preserves aggregate statistics for product improvement
    3. Complies with privacy regulations (GDPR, CCPA)
    4. Cannot be reversed once executed
    """
    try:
        result = await user_behavior_analytics_service.anonymize_user_data(str(current_user.id))
        return result
        
    except Exception as e:
        logger.error(f"Error anonymizing analytics data: {e}")
        raise HTTPException(status_code=500, detail="Failed to anonymize analytics data")

@api_router.delete("/analytics/data", tags=["Analytics", "Privacy"])
async def delete_analytics_data(
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete all analytics data for the user
    
    This endpoint:
    1. Permanently deletes all user analytics data
    2. Removes behavior events, sessions, and preferences
    3. Cannot be reversed once executed
    4. Complies with "right to be forgotten" regulations
    """
    try:
        result = await user_behavior_analytics_service.delete_user_analytics_data(str(current_user.id))
        return result
        
    except Exception as e:
        logger.error(f"Error deleting analytics data: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete analytics data")

# ================================
# SENTIMENT ANALYSIS ENDPOINTS (EMOTIONAL OS)
# ================================

@api_router.post("/sentiment/analyze-entry/{entry_id}", tags=["Sentiment Analysis", "Emotional OS"])
async def analyze_entry_sentiment(
    entry_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Analyze sentiment for a specific journal entry using GPT-5 nano
    
    This endpoint:
    1. Retrieves the journal entry content
    2. Uses GPT-5 nano to perform sophisticated emotional analysis
    3. Updates the entry with sentiment data
    4. Returns comprehensive emotional insights
    """
    try:
        # Get the journal entry
        entry = await find_document("journal_entries", {"id": entry_id, "user_id": str(current_user.id)})
        if not entry:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        # Perform sentiment analysis
        sentiment_result = await sentiment_analysis_service.analyze_journal_entry(
            str(current_user.id),
            entry_id,
            entry.get('content', ''),
            entry.get('title', '')
        )
        
        return {
            "success": True,
            "entry_id": entry_id,
            "sentiment_analysis": sentiment_result.dict(),
            "sentiment_emoji": sentiment_analysis_service.get_sentiment_emoji(sentiment_result.sentiment_category),
            "sentiment_color": sentiment_analysis_service.get_sentiment_color(sentiment_result.sentiment_category)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing entry sentiment: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze entry sentiment")

@api_router.post("/sentiment/bulk-analyze", tags=["Sentiment Analysis", "Emotional OS"])
async def bulk_analyze_sentiment(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of entries to analyze"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Bulk analyze sentiment for existing journal entries that don't have sentiment scores
    
    This endpoint:
    1. Finds unanalyzed journal entries for the user
    2. Performs sentiment analysis on each entry using GPT-5 nano
    3. Updates entries with emotional intelligence data
    4. Returns analysis summary
    """
    try:
        result = await sentiment_analysis_service.bulk_analyze_existing_entries(
            str(current_user.id),
            limit
        )
        return result
        
    except Exception as e:
        logger.error(f"Error in bulk sentiment analysis: {e}")
        raise HTTPException(status_code=500, detail="Failed to perform bulk sentiment analysis")

@api_router.get("/sentiment/trends", tags=["Sentiment Analysis", "Emotional OS"])
async def get_sentiment_trends(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get emotional sentiment trends over time for insights dashboard
    
    This endpoint provides:
    1. Daily sentiment averages and patterns
    2. Emotional keyword trends
    3. Sentiment category distribution
    4. Emotional wellness indicators
    """
    try:
        trends = await sentiment_analysis_service.get_sentiment_trends(str(current_user.id), days)
        
        # Calculate summary statistics
        if trends:
            sentiment_scores = [t.average_sentiment for t in trends]
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            sentiment_trend_direction = "stable"
            
            if len(sentiment_scores) > 1:
                recent_avg = sum(sentiment_scores[-7:]) / min(7, len(sentiment_scores))  # Last week
                older_avg = sum(sentiment_scores[:-7]) / max(1, len(sentiment_scores) - 7)  # Before last week
                
                if recent_avg > older_avg + 0.1:
                    sentiment_trend_direction = "improving"
                elif recent_avg < older_avg - 0.1:
                    sentiment_trend_direction = "declining"
        else:
            avg_sentiment = 0.0
            sentiment_trend_direction = "no_data"
        
        return {
            "trends": [t.dict() for t in trends],
            "summary": {
                "period_days": days,
                "total_entries_analyzed": len(trends),
                "average_sentiment": avg_sentiment,
                "trend_direction": sentiment_trend_direction,
                "emoji_representation": sentiment_analysis_service.get_sentiment_emoji(
                    sentiment_analysis_service._score_to_category(avg_sentiment)
                )
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting sentiment trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to get sentiment trends")

@api_router.get("/sentiment/correlations", tags=["Sentiment Analysis", "Emotional OS"])
async def get_activity_sentiment_correlations(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get correlations between activities and emotional outcomes
    
    This endpoint analyzes:
    1. Which projects/tasks correlate with positive emotions
    2. Which activities may be emotionally draining
    3. Emotional impact patterns across different life areas
    4. Actionable insights for better emotional outcomes
    """
    try:
        correlations = await sentiment_analysis_service.analyze_activity_sentiment_correlation(
            str(current_user.id), 
            days
        )
        
        return {
            "correlations": [c.dict() for c in correlations],
            "analysis_period_days": days,
            "total_correlations": len(correlations),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting activity sentiment correlations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get activity sentiment correlations")

@api_router.get("/sentiment/insights", tags=["Sentiment Analysis", "Emotional OS"])
async def get_emotional_insights(
    days: int = Query(30, ge=1, le=365, description="Number of days for insight generation"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get AI-generated emotional insights based on sentiment patterns
    
    This endpoint provides:
    1. Trend analysis of emotional patterns
    2. Wellness alerts and recommendations
    3. Emotional growth indicators
    4. Personalized emotional intelligence insights
    """
    try:
        insights = await sentiment_analysis_service.generate_emotional_insights(
            str(current_user.id),
            days
        )
        
        return {
            "insights": [i.dict() for i in insights],
            "insight_count": len(insights),
            "analysis_period_days": days,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting emotional insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to get emotional insights")

@api_router.get("/sentiment/wellness-score", tags=["Sentiment Analysis", "Emotional OS"])
async def get_emotional_wellness_score(
    days: int = Query(30, ge=1, le=365, description="Number of days for wellness calculation"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get overall emotional wellness score (0-100)
    
    This endpoint calculates:
    1. Average sentiment over time period
    2. Emotional stability/consistency
    3. Journaling engagement level
    4. Overall emotional wellness indicator
    """
    try:
        wellness_score = await sentiment_analysis_service.get_emotional_wellness_score(
            str(current_user.id),
            days
        )
        
        # Determine wellness category
        if wellness_score >= 80:
            wellness_category = "excellent"
            wellness_emoji = "🌟"
        elif wellness_score >= 65:
            wellness_category = "good"
            wellness_emoji = "😊"
        elif wellness_score >= 50:
            wellness_category = "moderate"
            wellness_emoji = "😐"
        elif wellness_score >= 35:
            wellness_category = "concerning"
            wellness_emoji = "😟"
        else:
            wellness_category = "needs_attention"
            wellness_emoji = "😰"
        
        return {
            "wellness_score": wellness_score,
            "wellness_category": wellness_category,
            "wellness_emoji": wellness_emoji,
            "analysis_period_days": days,
            "generated_at": datetime.utcnow().isoformat(),
            "interpretation": f"Your emotional wellness score is {wellness_score:.1f}/100, indicating {wellness_category} emotional health."
        }
        
    except Exception as e:
        logger.error(f"Error getting emotional wellness score: {e}")
        raise HTTPException(status_code=500, detail="Failed to get emotional wellness score")

@api_router.post("/sentiment/analyze-text", tags=["Sentiment Analysis", "Emotional OS"])
async def analyze_text_sentiment(
    request: SentimentAnalysisRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Analyze sentiment for arbitrary text (for real-time analysis during writing)
    
    This endpoint:
    1. Performs real-time sentiment analysis on provided text
    2. Returns emotional insights without storing data
    3. Useful for live feedback during journal writing
    4. Provides immediate emotional awareness
    """
    try:
        # Create a temporary sentiment analysis (without storing)
        sentiment_result = await sentiment_analysis_service.analyze_journal_entry(
            str(current_user.id),
            "temp_analysis",  # Temporary ID
            request.text,
            ""  # No title
        )
        
        return {
            "sentiment_analysis": sentiment_result.dict(),
            "sentiment_emoji": sentiment_analysis_service.get_sentiment_emoji(sentiment_result.sentiment_category),
            "sentiment_color": sentiment_analysis_service.get_sentiment_color(sentiment_result.sentiment_category),
            "human_readable": f"{sentiment_result.sentiment_category.value.replace('_', ' ').title()}",
            "analyzed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing text sentiment: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze text sentiment")

# Include all routers after endpoints are defined
app.include_router(api_router)
app.include_router(auth_router, prefix="/api")
app.include_router(hrm_router)