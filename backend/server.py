from fastapi import FastAPI, APIRouter, HTTPException, Query, Depends, status, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from pydantic import BaseModel
from pathlib import Path
import os
import logging
from typing import List, Optional
from datetime import datetime
import uuid

# Import our models and services
from supabase_client import supabase_manager
from models import *
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
from alignment_score_service import AlignmentScoreService
from ai_coach_mvp_service import AiCoachMvpService
from hrm_endpoints import hrm_router

ROOT_DIR = Path(__file__).parent
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
        # Get basic why statements from AI Coach service
        basic_response = await ai_coach_service.generate_task_why_statements(
            user_id=str(current_user.id),
            task_ids=task_ids
        )
        
        # Enhance with HRM insights
        from hrm_service import HierarchicalReasoningModel
        hrm = HierarchicalReasoningModel(str(current_user.id))
        
        enhanced_statements = []
        for statement in basic_response.why_statements:
            try:
                # Get HRM analysis for this task
                insight = await hrm.analyze_entity(
                    entity_type='task',
                    entity_id=statement.task_id,
                    analysis_depth=hrm.AnalysisDepth.BALANCED
                )
                
                # Create enhanced statement with HRM data
                enhanced_statement = statement.dict()
                enhanced_statement['hrm_enhancement'] = {
                    'confidence_score': insight.confidence_score,
                    'reasoning_summary': insight.summary,
                    'hierarchy_reasoning': insight.reasoning_path[:2],  # Top 2 reasoning steps
                    'recommendations': insight.recommendations[:2]  # Top 2 recommendations
                }
                enhanced_statements.append(enhanced_statement)
                
            except Exception as e:
                logger.warning(f"Failed to enhance task {statement.task_id} with HRM: {e}")
                # Fall back to basic statement
                enhanced_statements.append(statement.dict())
        
        # Return enhanced response
        return TaskWhyStatementResponse(
            why_statements=[TaskWhyStatement(**stmt) if isinstance(stmt, dict) else stmt for stmt in enhanced_statements],
            tasks_analyzed=basic_response.tasks_analyzed,
            vertical_alignment={
                **basic_response.vertical_alignment,
                'hrm_enhanced': True,
                'enhancement_success_rate': len([s for s in enhanced_statements if 'hrm_enhancement' in s]) / len(enhanced_statements) if enhanced_statements else 0
            }
        )
        
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
            coaching_top_n=top_n
        )
        
        if include_reasoning and priorities.get('tasks'):
            from hrm_service import HierarchicalReasoningModel, AnalysisDepth
            hrm = HierarchicalReasoningModel(str(current_user.id))
            
            enhanced_tasks = []
            for task in priorities['tasks']:
                try:
                    # Get HRM analysis for high-priority tasks
                    if task.get('score', 0) > 50:  # Only for high-scoring tasks to optimize performance
                        insight = await hrm.analyze_entity(
                            entity_type='task',
                            entity_id=task['id'],
                            analysis_depth=AnalysisDepth.BALANCED
                        )
                        
                        task['hrm_enhancement'] = {
                            'confidence_score': insight.confidence_score,
                            'reasoning_summary': insight.summary,
                            'hierarchy_reasoning': insight.reasoning_path[:3],
                            'recommendations': insight.recommendations[:3]
                        }
                    
                    enhanced_tasks.append(task)
                    
                except Exception as e:
                    logger.warning(f"Failed to enhance task {task.get('id')} with HRM: {e}")
                    enhanced_tasks.append(task)
            
            priorities['tasks'] = enhanced_tasks
            priorities['hrm_enhanced'] = True
        
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
        # Get basic alignment data
        basic_data = await alignment_service.get_alignment_dashboard_data(str(current_user.id))
        
        # Enhance with HRM insights
        from hrm_service import HierarchicalReasoningModel, AnalysisDepth
        hrm = HierarchicalReasoningModel(str(current_user.id))
        
        try:
            # Get global alignment analysis
            alignment_insight = await hrm.analyze_entity(
                entity_type='global',
                entity_id=None,
                analysis_depth=AnalysisDepth.BALANCED
            )
            
            basic_data['hrm_enhancement'] = {
                'confidence_score': alignment_insight.confidence_score,
                'reasoning_summary': alignment_insight.summary,
                'hierarchy_reasoning': alignment_insight.reasoning_path[:3],
                'recommendations': alignment_insight.recommendations[:5]
            }
            
        except Exception as e:
            logger.warning(f"Failed to enhance alignment dashboard with HRM: {e}")
            basic_data['hrm_enhancement'] = {
                'confidence_score': 0.5,
                'reasoning_summary': "HRM analysis temporarily unavailable",
                'hierarchy_reasoning': [],
                'recommendations': ["Continue working on your current projects", "Review your goal alignment regularly"]
            }
        
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
        # Get basic priorities
        priorities = await ai_coach_service.get_today_priorities(
            user_id=str(current_user.id),
            coaching_top_n=top_n
        )
        
        if include_hrm and priorities.get('tasks'):
            from hrm_service import HierarchicalReasoningModel, AnalysisDepth
            hrm = HierarchicalReasoningModel(str(current_user.id))
            
            enhanced_tasks = []
            for task in priorities['tasks']:
                try:
                    # Get HRM analysis for each task
                    insight = await hrm.analyze_entity(
                        entity_type='task',
                        entity_id=task['id'],
                        analysis_depth=AnalysisDepth.MINIMAL  # Use minimal for performance
                    )
                    
                    task['hrm_enhancement'] = {
                        'confidence_score': insight.confidence_score,
                        'reasoning_summary': insight.summary,
                        'recommendations': insight.recommendations[:2]
                    }
                    
                except Exception as e:
                    logger.warning(f"Failed to enhance task {task.get('id')} with HRM: {e}")
                
                enhanced_tasks.append(task)
            
            priorities['tasks'] = enhanced_tasks
            priorities['hrm_enhanced'] = True
        
        return priorities
        
    except Exception as e:
        logger.error(f"Error getting today's priorities: {e}")
        raise HTTPException(status_code=500, detail="Failed to get today's priorities")

app.include_router(api_router)
app.include_router(auth_router, prefix="/api")
app.include_router(hrm_router)