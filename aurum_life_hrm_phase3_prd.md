# Product Requirements Document (PRD): Aurum Life - Phase 3 LLM-Augmented HRM Implementation

**Version:** 1.0  
**Date:** January 2025  
**Status:** Implementation Ready  

## Executive Summary

This PRD details the comprehensive transformation of Aurum Life from its current rule-based AI system to a sophisticated LLM-Augmented Hierarchical Reasoning Model (HRM). The implementation will provide Intentional Professionals with an AI system that understands and reasons about their life goals at every level of the PAPT hierarchy, delivering truly intelligent prioritization and insights.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Database Changes](#database-changes)
3. [Backend Modifications](#backend-modifications)
4. [Frontend Updates](#frontend-updates)
5. [API Changes](#api-changes)
6. [Migration Strategy](#migration-strategy)
7. [Testing Requirements](#testing-requirements)

---

## 1. Architecture Overview

### Current State
```
User → Frontend → FastAPI → Rule-based Scoring → Gemini (simple coaching) → Response
```

### Target State (Phase 3 HRM)
```
User → Frontend → FastAPI → HRM Service → Blackboard ← → Gemini LLM
                                ↓
                    Hierarchical Reasoning Engine
                    (Pillar → Area → Project → Task)
```

---

## 2. Database Changes

### 2.1 Tables to ADD

#### 2.1.1 `insights` Table (Core Blackboard)
```sql
CREATE TABLE public.insights (
    -- Primary Fields
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Entity Reference
    entity_type TEXT NOT NULL CHECK (entity_type IN ('pillar', 'area', 'project', 'task', 'global')),
    entity_id UUID, -- NULL for global insights
    
    -- Insight Details
    insight_type TEXT NOT NULL CHECK (insight_type IN (
        'priority_reasoning',      -- Why something is prioritized
        'alignment_analysis',      -- How entities align with goals
        'pattern_recognition',     -- Detected patterns
        'recommendation',          -- Action recommendations
        'goal_coherence',         -- Goal conflict/alignment analysis
        'time_allocation',        -- Time distribution insights
        'progress_prediction',    -- Future state predictions
        'obstacle_identification' -- Blocker analysis
    )),
    
    -- Core Content
    title TEXT NOT NULL,
    summary TEXT NOT NULL,        -- Human-readable summary
    detailed_reasoning JSONB NOT NULL, -- Full HRM reasoning trace
    
    -- HRM Specific Fields
    confidence_score DECIMAL(3,2) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
    impact_score DECIMAL(3,2) CHECK (impact_score >= 0 AND impact_score <= 1),
    
    -- Reasoning Path (shows hierarchical thinking)
    reasoning_path JSONB NOT NULL DEFAULT '[]'::JSONB,
    /* Example structure:
    [
        {
            "level": "pillar",
            "entity_id": "uuid",
            "entity_name": "Career",
            "reasoning": "Critical life domain with 85% time allocation",
            "confidence": 0.9
        },
        {
            "level": "area",
            "entity_id": "uuid",
            "entity_name": "Product Management",
            "reasoning": "High-importance area supporting career advancement",
            "confidence": 0.85
        }
    ]
    */
    
    -- LLM Context Preservation
    llm_session_id TEXT,
    llm_context JSONB, -- Preserved context for conversation continuity
    llm_model_used TEXT DEFAULT 'gemini-2.0-flash',
    
    -- User Interaction
    user_feedback TEXT CHECK (user_feedback IN ('accepted', 'rejected', 'modified', 'ignored')),
    feedback_details JSONB,
    application_count INTEGER DEFAULT 0, -- Times user applied this insight
    
    -- Metadata
    is_active BOOLEAN DEFAULT true,
    is_pinned BOOLEAN DEFAULT false, -- User can pin important insights
    expires_at TIMESTAMP WITH TIME ZONE, -- Auto-expire time-sensitive insights
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],
    
    -- Versioning
    version INTEGER DEFAULT 1,
    previous_version_id UUID REFERENCES public.insights(id),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for performance
CREATE INDEX idx_insights_user_entity ON insights(user_id, entity_type, entity_id);
CREATE INDEX idx_insights_active ON insights(user_id, is_active, created_at DESC);
CREATE INDEX idx_insights_type ON insights(user_id, insight_type, created_at DESC);
CREATE INDEX idx_insights_expiry ON insights(expires_at) WHERE expires_at IS NOT NULL;
```

#### 2.1.2 `hrm_rules` Table
```sql
CREATE TABLE public.hrm_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Rule Identity
    rule_code TEXT UNIQUE NOT NULL, -- e.g., 'PILLAR_ALIGNMENT_001'
    rule_name TEXT NOT NULL,
    description TEXT NOT NULL,
    
    -- Hierarchy Configuration
    hierarchy_level TEXT NOT NULL CHECK (hierarchy_level IN ('pillar', 'area', 'project', 'task', 'cross_level')),
    applies_to_entity_types TEXT[] NOT NULL, -- Which entities this rule evaluates
    
    -- Rule Logic
    rule_type TEXT NOT NULL CHECK (rule_type IN (
        'scoring',           -- Affects priority scores
        'filtering',         -- Filters entities
        'relationship',      -- Analyzes relationships
        'temporal',          -- Time-based rules
        'constraint',        -- Enforces constraints
        'pattern_matching'   -- Pattern detection
    )),
    
    -- Configuration
    rule_config JSONB NOT NULL,
    /* Example for temporal rule:
    {
        "conditions": {
            "due_date_proximity": "24h",
            "has_dependencies": false
        },
        "actions": {
            "priority_boost": 0.3,
            "add_tag": "urgent"
        },
        "llm_augmentation": {
            "analyze_context": true,
            "consider_energy_levels": true
        }
    }
    */
    
    -- Weights and Scoring
    base_weight DECIMAL(3,2) DEFAULT 0.5 CHECK (base_weight >= 0 AND base_weight <= 1),
    user_adjustable BOOLEAN DEFAULT false,
    
    -- LLM Integration
    requires_llm BOOLEAN DEFAULT false,
    llm_prompt_template TEXT,
    
    -- Management
    is_active BOOLEAN DEFAULT true,
    is_system_rule BOOLEAN DEFAULT true, -- System rules can't be deleted
    created_by TEXT DEFAULT 'system',
    
    -- Versioning
    version INTEGER DEFAULT 1,
    changelog JSONB DEFAULT '[]'::JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 2.1.3 `hrm_user_preferences` Table
```sql
CREATE TABLE public.hrm_user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Rule Customization
    rule_weight_overrides JSONB DEFAULT '{}'::JSONB,
    /* Example:
    {
        "PILLAR_ALIGNMENT_001": 0.8,
        "TEMPORAL_URGENCY_001": 0.6
    }
    */
    
    -- Reasoning Preferences
    explanation_detail_level TEXT DEFAULT 'balanced' CHECK (explanation_detail_level IN ('minimal', 'balanced', 'detailed')),
    show_confidence_scores BOOLEAN DEFAULT true,
    show_reasoning_path BOOLEAN DEFAULT true,
    
    -- AI Behavior
    ai_personality TEXT DEFAULT 'coach' CHECK (ai_personality IN ('coach', 'assistant', 'strategist', 'motivator')),
    ai_communication_style TEXT DEFAULT 'encouraging' CHECK (ai_communication_style IN ('direct', 'encouraging', 'analytical', 'socratic')),
    
    -- Focus Preferences
    primary_optimization TEXT DEFAULT 'balance' CHECK (primary_optimization IN (
        'balance',           -- Balance all pillars
        'focus',            -- Deep focus on priorities
        'exploration',      -- Encourage trying new things
        'efficiency',       -- Maximum productivity
        'wellbeing'        -- Wellness and sustainability
    )),
    
    -- Time Preferences
    preferred_work_hours JSONB DEFAULT '{"start": "09:00", "end": "17:00"}'::JSONB,
    energy_pattern TEXT DEFAULT 'steady' CHECK (energy_pattern IN ('morning_peak', 'afternoon_peak', 'evening_peak', 'steady')),
    
    -- Learning Settings
    enable_ai_learning BOOLEAN DEFAULT true,
    share_anonymous_insights BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 2.1.4 `hrm_feedback_log` Table
```sql
CREATE TABLE public.hrm_feedback_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    insight_id UUID REFERENCES public.insights(id) ON DELETE SET NULL,
    
    -- Feedback Details
    feedback_type TEXT NOT NULL CHECK (feedback_type IN (
        'insight_helpful',
        'insight_not_helpful',
        'priority_correct',
        'priority_incorrect',
        'reasoning_clear',
        'reasoning_unclear',
        'recommendation_followed',
        'recommendation_ignored'
    )),
    
    -- Context
    entity_type TEXT,
    entity_id UUID,
    original_score DECIMAL(5,2),
    user_adjusted_score DECIMAL(5,2),
    
    -- Detailed Feedback
    feedback_text TEXT,
    suggested_improvement TEXT,
    
    -- For learning
    applied_rules JSONB, -- Which rules were active
    reasoning_snapshot JSONB, -- State at time of feedback
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2.2 Tables to MODIFY

#### 2.2.1 Modify `tasks` Table
```sql
-- ADD these columns to existing tasks table
ALTER TABLE public.tasks ADD COLUMN IF NOT EXISTS hrm_priority_score DECIMAL(5,2);
ALTER TABLE public.tasks ADD COLUMN IF NOT EXISTS hrm_reasoning_summary TEXT;
ALTER TABLE public.tasks ADD COLUMN IF NOT EXISTS hrm_last_analyzed TIMESTAMP WITH TIME ZONE;
ALTER TABLE public.tasks ADD COLUMN IF NOT EXISTS ai_suggested_timeblock TEXT;
ALTER TABLE public.tasks ADD COLUMN IF NOT EXISTS obstacle_risk TEXT CHECK (obstacle_risk IN ('low', 'medium', 'high'));

-- ADD index for HRM queries
CREATE INDEX idx_tasks_hrm_priority ON tasks(user_id, completed, hrm_priority_score DESC) 
WHERE completed = false;
```

#### 2.2.2 Modify `projects` Table
```sql
-- ADD these columns
ALTER TABLE public.projects ADD COLUMN IF NOT EXISTS hrm_health_score DECIMAL(3,2);
ALTER TABLE public.projects ADD COLUMN IF NOT EXISTS hrm_predicted_completion DATE;
ALTER TABLE public.projects ADD COLUMN IF NOT EXISTS hrm_risk_factors JSONB DEFAULT '[]'::JSONB;
ALTER TABLE public.projects ADD COLUMN IF NOT EXISTS goal_coherence_score DECIMAL(3,2);
```

#### 2.2.3 Modify `areas` Table
```sql
-- ADD these columns
ALTER TABLE public.areas ADD COLUMN IF NOT EXISTS time_allocation_actual DECIMAL(5,2);
ALTER TABLE public.areas ADD COLUMN IF NOT EXISTS time_allocation_recommended DECIMAL(5,2);
ALTER TABLE public.areas ADD COLUMN IF NOT EXISTS balance_score DECIMAL(3,2);
```

#### 2.2.4 Modify `pillars` Table
```sql
-- ADD these columns
ALTER TABLE public.pillars ADD COLUMN IF NOT EXISTS vision_statement TEXT;
ALTER TABLE public.pillars ADD COLUMN IF NOT EXISTS success_metrics JSONB DEFAULT '[]'::JSONB;
ALTER TABLE public.pillars ADD COLUMN IF NOT EXISTS alignment_strength DECIMAL(3,2);
```

### 2.3 Tables to REMOVE

#### 2.3.1 Remove `ai_interactions` Table
```sql
-- Migrate useful data to insights table first
INSERT INTO public.insights (user_id, entity_type, insight_type, title, summary, detailed_reasoning, created_at)
SELECT 
    user_id,
    'global' as entity_type,
    'pattern_recognition' as insight_type,
    interaction_type as title,
    'Historical AI interaction' as summary,
    jsonb_build_object('type', interaction_type, 'context_size', context_size) as detailed_reasoning,
    created_at
FROM public.ai_interactions;

-- Then drop the table
DROP TABLE IF EXISTS public.ai_interactions CASCADE;
```

---

## 3. Backend Modifications

### 3.1 Files to ADD

#### 3.1.1 `backend/hrm_service.py`
```python
"""
Hierarchical Reasoning Model Service
Core implementation of LLM-Augmented HRM for Aurum Life
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from uuid import UUID
import logging
import asyncio
from decimal import Decimal

from emergentintegrations.llm.chat import LlmChat, UserMessage, SystemMessage
from pydantic import BaseModel
from supabase_client import get_supabase_client
from models import User

logger = logging.getLogger(__name__)

class ReasoningNode(BaseModel):
    """Represents a node in the hierarchical reasoning path"""
    level: str  # pillar, area, project, task
    entity_id: str
    entity_name: str
    reasoning: str
    confidence: float
    contributing_factors: List[Dict[str, Any]]

class HRMInsight(BaseModel):
    """Structured insight from HRM analysis"""
    entity_type: str
    entity_id: Optional[str]
    insight_type: str
    title: str
    summary: str
    detailed_reasoning: Dict[str, Any]
    confidence_score: float
    impact_score: float
    reasoning_path: List[ReasoningNode]
    recommendations: List[str]
    expires_at: Optional[datetime]

class HierarchicalReasoningModel:
    """
    LLM-Augmented Hierarchical Reasoning Model
    Provides intelligent reasoning across the PAPT hierarchy
    """
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.supabase = get_supabase_client()
        self.llm = self._initialize_llm()
        self._context_cache = {}
        
    def _initialize_llm(self) -> LlmChat:
        """Initialize Gemini with HRM-specific system prompt"""
        system_prompt = """You are the Hierarchical Reasoning Model (HRM) for Aurum Life, an advanced AI system that understands and reasons about personal productivity through the PAPT hierarchy (Pillars → Areas → Projects → Tasks).

Your role is to provide deep, multi-level reasoning that connects daily actions to life vision. You think hierarchically and understand how each level influences the others.

REASONING PRINCIPLES:
1. **Vertical Alignment**: Always trace connections from tasks up to pillars and from pillars down to tasks
2. **Contextual Intelligence**: Consider temporal, energy, and dependency factors
3. **Explainable Logic**: Provide clear reasoning paths that users can follow
4. **Confidence Scoring**: Be honest about uncertainty and provide confidence levels
5. **Actionable Insights**: Every insight should lead to clear next steps

HIERARCHY UNDERSTANDING:
- Pillars: Core life values and long-term vision (1-5 years)
- Areas: Major life domains and focus areas (quarterly)
- Projects: Specific outcomes and goals (monthly)
- Tasks: Daily actions and immediate steps (daily/weekly)

OUTPUT FORMAT:
Always structure your reasoning with:
1. Primary insight
2. Hierarchical connections
3. Confidence level and why
4. Specific recommendations
5. Potential obstacles or conflicts

Remember: You're not just prioritizing tasks, you're helping someone build their ideal life through intelligent system design."""
        
        import os
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
            
        return LlmChat(
            api_key=api_key,
            session_id=f"hrm-{self.user_id}",
            system_message=system_prompt
        ).with_model("gemini", "gemini-2.0-flash")
    
    async def analyze_entity(
        self, 
        entity_type: str, 
        entity_id: Optional[str] = None,
        analysis_depth: str = "balanced"
    ) -> HRMInsight:
        """
        Perform hierarchical reasoning on an entity
        
        Args:
            entity_type: One of 'pillar', 'area', 'project', 'task', 'global'
            entity_id: UUID of the entity (None for global analysis)
            analysis_depth: 'minimal', 'balanced', or 'detailed'
        """
        try:
            # Gather full hierarchical context
            context = await self._gather_hierarchical_context(entity_type, entity_id)
            
            # Build reasoning path bottom-up and top-down
            reasoning_path = await self._build_reasoning_path(context)
            
            # Apply HRM rules with LLM augmentation
            insight = await self._apply_hierarchical_reasoning(
                context, 
                reasoning_path, 
                analysis_depth
            )
            
            # Store in blackboard
            await self._store_insight(insight)
            
            return insight
            
        except Exception as e:
            logger.error(f"HRM analysis failed: {e}")
            raise
    
    async def _gather_hierarchical_context(
        self, 
        entity_type: str, 
        entity_id: Optional[str]
    ) -> Dict[str, Any]:
        """Gather complete context across all hierarchy levels"""
        
        context = {
            "user_id": self.user_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "timestamp": datetime.utcnow(),
            "hierarchy_data": {}
        }
        
        # Parallel fetch all hierarchy data
        pillars_task = self.supabase.table('pillars').select('*').eq('user_id', self.user_id).execute()
        areas_task = self.supabase.table('areas').select('*').eq('user_id', self.user_id).execute()
        projects_task = self.supabase.table('projects').select('*').eq('user_id', self.user_id).execute()
        tasks_task = self.supabase.table('tasks').select('*').eq('user_id', self.user_id).eq('completed', False).execute()
        
        # Get user preferences
        prefs_task = self.supabase.table('hrm_user_preferences').select('*').eq('user_id', self.user_id).single().execute()
        
        # Execute all queries
        results = await asyncio.gather(
            pillars_task, areas_task, projects_task, tasks_task, prefs_task,
            return_exceptions=True
        )
        
        context["hierarchy_data"] = {
            "pillars": results[0].data if not isinstance(results[0], Exception) else [],
            "areas": results[1].data if not isinstance(results[1], Exception) else [],
            "projects": results[2].data if not isinstance(results[2], Exception) else [],
            "tasks": results[3].data if not isinstance(results[3], Exception) else [],
        }
        
        context["user_preferences"] = results[4].data if not isinstance(results[4], Exception) else self._default_preferences()
        
        # Get specific entity details if provided
        if entity_id:
            entity_table = f"{entity_type}s"  # pluralize
            entity_data = await self.supabase.table(entity_table).select('*').eq('id', entity_id).single().execute()
            context["target_entity"] = entity_data.data
        
        # Get recent insights for learning
        recent_insights = await self.supabase.table('insights') \
            .select('*') \
            .eq('user_id', self.user_id) \
            .order('created_at', desc=True) \
            .limit(10) \
            .execute()
        context["recent_insights"] = recent_insights.data
        
        return context
    
    async def _build_reasoning_path(self, context: Dict[str, Any]) -> List[ReasoningNode]:
        """Build the hierarchical reasoning path"""
        reasoning_path = []
        
        # Implement bidirectional reasoning
        if context["entity_type"] == "task" and context.get("target_entity"):
            # Bottom-up: Task → Project → Area → Pillar
            task = context["target_entity"]
            
            # Get project
            project = next(
                (p for p in context["hierarchy_data"]["projects"] if p["id"] == task.get("project_id")),
                None
            )
            
            if project:
                # Get area
                area = next(
                    (a for a in context["hierarchy_data"]["areas"] if a["id"] == project.get("area_id")),
                    None
                )
                
                if area:
                    # Get pillar
                    pillar = next(
                        (p for p in context["hierarchy_data"]["pillars"] if p["id"] == area.get("pillar_id")),
                        None
                    )
                    
                    # Build path
                    if pillar:
                        reasoning_path.append(ReasoningNode(
                            level="pillar",
                            entity_id=pillar["id"],
                            entity_name=pillar["name"],
                            reasoning=f"Core life domain representing {pillar.get('vision_statement', 'fundamental values')}",
                            confidence=0.95,
                            contributing_factors=[
                                {"factor": "time_allocation", "value": pillar.get("time_allocation_percentage", 0)},
                                {"factor": "alignment_strength", "value": pillar.get("alignment_strength", 0)}
                            ]
                        ))
                    
                    # Add area reasoning
                    reasoning_path.append(ReasoningNode(
                        level="area",
                        entity_id=area["id"],
                        entity_name=area["name"],
                        reasoning=f"Focus area with importance level {area.get('importance', 3)}/5",
                        confidence=0.9,
                        contributing_factors=[
                            {"factor": "importance", "value": area.get("importance", 3)},
                            {"factor": "balance_score", "value": area.get("balance_score", 0)}
                        ]
                    ))
                
                # Add project reasoning
                reasoning_path.append(ReasoningNode(
                    level="project",
                    entity_id=project["id"],
                    entity_name=project["name"],
                    reasoning=f"Active project with {project.get('completion_percentage', 0)}% completion",
                    confidence=0.85,
                    contributing_factors=[
                        {"factor": "deadline_proximity", "value": self._calculate_deadline_proximity(project.get("deadline"))},
                        {"factor": "health_score", "value": project.get("hrm_health_score", 0)}
                    ]
                ))
        
        return reasoning_path
    
    async def _apply_hierarchical_reasoning(
        self,
        context: Dict[str, Any],
        reasoning_path: List[ReasoningNode],
        analysis_depth: str
    ) -> HRMInsight:
        """Apply HRM rules and LLM reasoning to generate insights"""
        
        # Load active HRM rules
        rules = await self._load_active_rules(context["entity_type"])
        
        # Apply rule-based scoring
        rule_results = await self._apply_rules(context, rules)
        
        # Prepare LLM prompt with full context
        llm_prompt = self._build_llm_prompt(context, reasoning_path, rule_results, analysis_depth)
        
        # Get LLM reasoning
        llm_response = await self.llm.send_message(UserMessage(text=llm_prompt))
        
        # Parse and structure the response
        insight = self._parse_llm_response(
            llm_response,
            context,
            reasoning_path,
            rule_results
        )
        
        return insight
    
    def _build_llm_prompt(
        self,
        context: Dict[str, Any],
        reasoning_path: List[ReasoningNode],
        rule_results: Dict[str, Any],
        analysis_depth: str
    ) -> str:
        """Build comprehensive prompt for LLM analysis"""
        
        entity_type = context["entity_type"]
        entity = context.get("target_entity", {})
        
        prompt = f"""Analyze this {entity_type} using Hierarchical Reasoning Model principles.

ENTITY DETAILS:
Type: {entity_type}
Name: {entity.get('name', 'N/A')}
Description: {entity.get('description', 'No description')}

HIERARCHICAL CONTEXT:
{self._format_reasoning_path(reasoning_path)}

RULE-BASED ANALYSIS:
{self._format_rule_results(rule_results)}

USER PREFERENCES:
- Primary optimization: {context['user_preferences'].get('primary_optimization', 'balance')}
- Energy pattern: {context['user_preferences'].get('energy_pattern', 'steady')}
- Work hours: {context['user_preferences'].get('preferred_work_hours', {})}

ANALYSIS DEPTH: {analysis_depth}

Provide:
1. Primary insight about this {entity_type}
2. How it connects to the hierarchy (both up and down)
3. Confidence score (0-1) with justification
4. 3-5 specific, actionable recommendations
5. Potential obstacles or conflicts to watch for

Format as JSON with keys: primary_insight, hierarchical_connections, confidence_score, confidence_reasoning, recommendations, obstacles"""
        
        return prompt
    
    async def _store_insight(self, insight: HRMInsight) -> None:
        """Store insight in the blackboard (insights table)"""
        
        insight_data = {
            "user_id": self.user_id,
            "entity_type": insight.entity_type,
            "entity_id": insight.entity_id,
            "insight_type": insight.insight_type,
            "title": insight.title,
            "summary": insight.summary,
            "detailed_reasoning": insight.detailed_reasoning,
            "confidence_score": float(insight.confidence_score),
            "impact_score": float(insight.impact_score),
            "reasoning_path": [node.dict() for node in insight.reasoning_path],
            "expires_at": insight.expires_at
        }
        
        await self.supabase.table('insights').insert(insight_data).execute()
    
    # Additional helper methods...
    def _calculate_deadline_proximity(self, deadline: Optional[str]) -> float:
        """Calculate how close a deadline is (0-1 scale)"""
        if not deadline:
            return 0.0
        
        try:
            deadline_date = datetime.fromisoformat(deadline.replace('Z', '+00:00'))
            days_until = (deadline_date - datetime.now(timezone.utc)).days
            
            if days_until <= 0:
                return 1.0
            elif days_until <= 7:
                return 0.8
            elif days_until <= 30:
                return 0.5
            else:
                return 0.2
        except:
            return 0.0
    
    def _default_preferences(self) -> Dict[str, Any]:
        """Default user preferences"""
        return {
            "primary_optimization": "balance",
            "explanation_detail_level": "balanced",
            "show_confidence_scores": True,
            "ai_personality": "coach",
            "energy_pattern": "steady",
            "preferred_work_hours": {"start": "09:00", "end": "17:00"}
        }
```

#### 3.1.2 `backend/blackboard_service.py`
```python
"""
Blackboard Service
Central data repository for HRM insights and shared intelligence
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from uuid import UUID
import logging
import asyncio
from supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

class BlackboardService:
    """
    Centralized insight repository with pub/sub capabilities
    Implements the Blackboard architectural pattern for AI systems
    """
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self._subscribers = {}
        self._cache = {}
        
    async def store_insight(
        self,
        user_id: str,
        insight: Dict[str, Any],
        notify_subscribers: bool = True
    ) -> str:
        """Store an insight and optionally notify subscribers"""
        
        try:
            # Store in database
            result = await self.supabase.table('insights').insert({
                **insight,
                'user_id': user_id,
                'created_at': datetime.utcnow().isoformat()
            }).execute()
            
            insight_id = result.data[0]['id']
            
            # Update cache
            cache_key = f"{user_id}:{insight['entity_type']}:{insight.get('entity_id', 'global')}"
            self._cache[cache_key] = insight
            
            # Notify subscribers if requested
            if notify_subscribers:
                await self._notify_subscribers(user_id, insight)
            
            return insight_id
            
        except Exception as e:
            logger.error(f"Failed to store insight: {e}")
            raise
    
    async def get_insights_for_entity(
        self,
        user_id: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        insight_types: Optional[List[str]] = None,
        active_only: bool = True,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve insights for a specific entity"""
        
        query = self.supabase.table('insights') \
            .select('*') \
            .eq('user_id', user_id) \
            .eq('entity_type', entity_type)
        
        if entity_id:
            query = query.eq('entity_id', entity_id)
        
        if insight_types:
            query = query.in_('insight_type', insight_types)
        
        if active_only:
            query = query.eq('is_active', True)
        
        result = await query.order('created_at', desc=True).limit(limit).execute()
        
        return result.data
    
    async def get_hierarchical_insights(
        self,
        user_id: str,
        task_id: str
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get all insights in the hierarchy for a specific task"""
        
        # First, get the task's hierarchy
        task = await self.supabase.table('tasks') \
            .select('*, project:projects!inner(*, area:areas!inner(*, pillar:pillars!inner(*)))') \
            .eq('id', task_id) \
            .single() \
            .execute()
        
        if not task.data:
            return {}
        
        task_data = task.data
        project = task_data.get('project', {})
        area = project.get('area', {})
        pillar = area.get('pillar', {})
        
        # Parallel fetch insights for all levels
        results = await asyncio.gather(
            self.get_insights_for_entity(user_id, 'pillar', pillar.get('id')),
            self.get_insights_for_entity(user_id, 'area', area.get('id')),
            self.get_insights_for_entity(user_id, 'project', project.get('id')),
            self.get_insights_for_entity(user_id, 'task', task_id),
            return_exceptions=True
        )
        
        return {
            'pillar': results[0] if not isinstance(results[0], Exception) else [],
            'area': results[1] if not isinstance(results[1], Exception) else [],
            'project': results[2] if not isinstance(results[2], Exception) else [],
            'task': results[3] if not isinstance(results[3], Exception) else []
        }
    
    async def mark_insight_feedback(
        self,
        user_id: str,
        insight_id: str,
        feedback: str,
        feedback_details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record user feedback on an insight"""
        
        # Update insight
        await self.supabase.table('insights') \
            .update({
                'user_feedback': feedback,
                'feedback_details': feedback_details,
                'updated_at': datetime.utcnow().isoformat()
            }) \
            .eq('id', insight_id) \
            .eq('user_id', user_id) \
            .execute()
        
        # Log feedback for learning
        await self.supabase.table('hrm_feedback_log').insert({
            'user_id': user_id,
            'insight_id': insight_id,
            'feedback_type': f'insight_{feedback}',
            'feedback_text': feedback_details.get('text') if feedback_details else None
        }).execute()
    
    async def expire_old_insights(self, user_id: str) -> int:
        """Mark expired insights as inactive"""
        
        result = await self.supabase.table('insights') \
            .update({'is_active': False}) \
            .eq('user_id', user_id) \
            .eq('is_active', True) \
            .lt('expires_at', datetime.utcnow().isoformat()) \
            .execute()
        
        return len(result.data)
    
    async def get_insight_patterns(
        self,
        user_id: str,
        lookback_days: int = 30
    ) -> Dict[str, Any]:
        """Analyze patterns in user's insights for meta-learning"""
        
        since_date = (datetime.utcnow() - timedelta(days=lookback_days)).isoformat()
        
        insights = await self.supabase.table('insights') \
            .select('*') \
            .eq('user_id', user_id) \
            .gte('created_at', since_date) \
            .execute()
        
        feedback = await self.supabase.table('hrm_feedback_log') \
            .select('*') \
            .eq('user_id', user_id) \
            .gte('created_at', since_date) \
            .execute()
        
        # Analyze patterns
        patterns = {
            'total_insights': len(insights.data),
            'insights_by_type': {},
            'average_confidence': 0,
            'feedback_summary': {},
            'most_helpful_types': [],
            'least_helpful_types': []
        }
        
        # Calculate statistics
        if insights.data:
            # Group by type
            for insight in insights.data:
                itype = insight['insight_type']
                patterns['insights_by_type'][itype] = patterns['insights_by_type'].get(itype, 0) + 1
            
            # Average confidence
            confidences = [i['confidence_score'] for i in insights.data if i.get('confidence_score')]
            if confidences:
                patterns['average_confidence'] = sum(confidences) / len(confidences)
        
        # Analyze feedback
        if feedback.data:
            for fb in feedback.data:
                ftype = fb['feedback_type']
                patterns['feedback_summary'][ftype] = patterns['feedback_summary'].get(ftype, 0) + 1
        
        return patterns
    
    # Pub/Sub functionality
    def subscribe(self, user_id: str, callback: callable) -> str:
        """Subscribe to insights for a user"""
        import uuid
        sub_id = str(uuid.uuid4())
        
        if user_id not in self._subscribers:
            self._subscribers[user_id] = {}
        
        self._subscribers[user_id][sub_id] = callback
        return sub_id
    
    def unsubscribe(self, user_id: str, subscription_id: str) -> None:
        """Unsubscribe from insights"""
        if user_id in self._subscribers:
            self._subscribers[user_id].pop(subscription_id, None)
    
    async def _notify_subscribers(self, user_id: str, insight: Dict[str, Any]) -> None:
        """Notify all subscribers of a new insight"""
        if user_id in self._subscribers:
            tasks = []
            for callback in self._subscribers[user_id].values():
                if asyncio.iscoroutinefunction(callback):
                    tasks.append(callback(insight))
                else:
                    tasks.append(asyncio.create_task(asyncio.to_thread(callback, insight)))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
```

#### 3.1.3 `backend/hrm_rules_engine.py`
```python
"""
HRM Rules Engine
Manages and executes hierarchical rules for the reasoning model
"""

from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from decimal import Decimal
import json
import logging
from abc import ABC, abstractmethod

from supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

class BaseRule(ABC):
    """Abstract base class for HRM rules"""
    
    def __init__(self, rule_config: Dict[str, Any]):
        self.rule_id = rule_config['id']
        self.rule_code = rule_config['rule_code']
        self.rule_name = rule_config['rule_name']
        self.config = rule_config['rule_config']
        self.weight = float(rule_config.get('base_weight', 0.5))
        
    @abstractmethod
    async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate the rule and return results"""
        pass
    
    def applies_to(self, entity_type: str) -> bool:
        """Check if rule applies to entity type"""
        return entity_type in self.config.get('applies_to_entity_types', [])

class TemporalUrgencyRule(BaseRule):
    """Rule for time-based urgency scoring"""
    
    async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        entity = context.get('target_entity', {})
        
        if not entity.get('due_date'):
            return {
                'score': 0,
                'confidence': 1.0,
                'reasoning': 'No due date set'
            }
        
        # Calculate urgency based on time remaining
        due_date = datetime.fromisoformat(entity['due_date'].replace('Z', '+00:00'))
        now = datetime.utcnow()
        hours_until_due = (due_date - now).total_seconds() / 3600
        
        if hours_until_due <= 0:
            score = 1.0
            reasoning = "Overdue task requires immediate attention"
        elif hours_until_due <= 24:
            score = 0.9
            reasoning = f"Due in {int(hours_until_due)} hours - critical urgency"
        elif hours_until_due <= 72:
            score = 0.7
            reasoning = f"Due in {int(hours_until_due/24)} days - high urgency"
        elif hours_until_due <= 168:  # 1 week
            score = 0.5
            reasoning = f"Due this week - moderate urgency"
        else:
            score = 0.2
            reasoning = f"Due in {int(hours_until_due/24)} days - low urgency"
        
        return {
            'score': score * self.weight,
            'confidence': 0.95,
            'reasoning': reasoning,
            'factors': {
                'hours_until_due': hours_until_due,
                'is_overdue': hours_until_due <= 0
            }
        }

class PillarAlignmentRule(BaseRule):
    """Rule for scoring based on pillar alignment and importance"""
    
    async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        entity = context.get('target_entity', {})
        hierarchy_data = context.get('hierarchy_data', {})
        
        # Trace entity to its pillar
        pillar = None
        alignment_path = []
        
        if context['entity_type'] == 'task':
            # Task -> Project -> Area -> Pillar
            project = next((p for p in hierarchy_data['projects'] if p['id'] == entity.get('project_id')), None)
            if project:
                alignment_path.append(f"Project: {project['name']}")
                area = next((a for a in hierarchy_data['areas'] if a['id'] == project.get('area_id')), None)
                if area:
                    alignment_path.append(f"Area: {area['name']}")
                    pillar = next((p for p in hierarchy_data['pillars'] if p['id'] == area.get('pillar_id')), None)
                    if pillar:
                        alignment_path.append(f"Pillar: {pillar['name']}")
        
        if not pillar:
            return {
                'score': 0.3,  # Base score for unaligned tasks
                'confidence': 0.8,
                'reasoning': 'Task not aligned to any pillar - consider organizing your hierarchy'
            }
        
        # Calculate alignment score based on pillar importance and time allocation
        time_allocation = pillar.get('time_allocation_percentage', 20) / 100
        alignment_strength = pillar.get('alignment_strength', 0.5)
        
        # Also consider area and project importance
        area_importance = next((a['importance'] for a in hierarchy_data['areas'] 
                               if any(p['id'] == alignment_path[1].split(': ')[1] for p in hierarchy_data['areas'])), 3) / 5
        
        project_importance = next((p['importance'] for p in hierarchy_data['projects']
                                  if p['name'] == alignment_path[0].split(': ')[1]), 3) / 5
        
        # Weighted score
        score = (
            time_allocation * 0.4 +
            alignment_strength * 0.3 +
            area_importance * 0.2 +
            project_importance * 0.1
        ) * self.weight
        
        reasoning = f"Aligned through: {' → '.join(alignment_path)}. "
        reasoning += f"Pillar allocation: {int(time_allocation*100)}%, "
        reasoning += f"Area importance: {int(area_importance*5)}/5"
        
        return {
            'score': score,
            'confidence': 0.9,
            'reasoning': reasoning,
            'factors': {
                'alignment_path': alignment_path,
                'time_allocation': time_allocation,
                'area_importance': area_importance,
                'project_importance': project_importance
            }
        }

class EnergyPatternRule(BaseRule):
    """Rule for matching tasks to user's energy patterns"""
    
    async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        entity = context.get('target_entity', {})
        user_prefs = context.get('user_preferences', {})
        
        current_hour = datetime.utcnow().hour
        energy_pattern = user_prefs.get('energy_pattern', 'steady')
        
        # Determine if task matches current energy level
        task_type = entity.get('category', 'general')
        is_deep_work = task_type in ['deep_work', 'creative', 'strategic']
        
        score = 0.5  # Default neutral score
        
        if energy_pattern == 'morning_peak' and 6 <= current_hour <= 12:
            score = 0.9 if is_deep_work else 0.4
            reasoning = "Morning peak hours - ideal for deep work"
        elif energy_pattern == 'afternoon_peak' and 13 <= current_hour <= 17:
            score = 0.9 if is_deep_work else 0.4
            reasoning = "Afternoon peak hours - ideal for focused tasks"
        elif energy_pattern == 'evening_peak' and 18 <= current_hour <= 22:
            score = 0.9 if is_deep_work else 0.4
            reasoning = "Evening peak hours - good for creative work"
        elif energy_pattern == 'steady':
            score = 0.6
            reasoning = "Steady energy pattern - consistent performance expected"
        else:
            score = 0.3 if is_deep_work else 0.7
            reasoning = f"Off-peak hours for {energy_pattern} pattern"
        
        return {
            'score': score * self.weight,
            'confidence': 0.75,
            'reasoning': reasoning,
            'factors': {
                'current_hour': current_hour,
                'energy_pattern': energy_pattern,
                'is_deep_work': is_deep_work
            }
        }

class DependencyRule(BaseRule):
    """Rule for handling task dependencies"""
    
    async def evaluate(self, context: Dict[str, Any]) -> Dict[str, Any]:
        entity = context.get('target_entity', {})
        hierarchy_data = context.get('hierarchy_data', {})
        
        dependency_ids = entity.get('dependency_task_ids', [])
        
        if not dependency_ids:
            return {
                'score': 0.5,
                'confidence': 1.0,
                'reasoning': 'No dependencies - can be started anytime'
            }
        
        # Check dependency status
        all_tasks = hierarchy_data.get('tasks', [])
        blocked_by = []
        ready_count = 0
        
        for dep_id in dependency_ids:
            dep_task = next((t for t in all_tasks if t['id'] == dep_id), None)
            if dep_task and not dep_task.get('completed', False):
                blocked_by.append(dep_task['name'])
            else:
                ready_count += 1
        
        if blocked_by:
            score = 0.1
            reasoning = f"Blocked by {len(blocked_by)} task(s): {', '.join(blocked_by[:2])}"
            if len(blocked_by) > 2:
                reasoning += f" and {len(blocked_by) - 2} more"
        else:
            score = 0.8
            reasoning = f"All {ready_count} dependencies completed - ready to start"
        
        return {
            'score': score * self.weight,
            'confidence': 0.95,
            'reasoning': reasoning,
            'factors': {
                'total_dependencies': len(dependency_ids),
                'blocked_by': blocked_by,
                'ready_count': ready_count
            }
        }

class HRMRulesEngine:
    """Main rules engine for HRM"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self._rule_registry: Dict[str, type] = {
            'TEMPORAL_URGENCY': TemporalUrgencyRule,
            'PILLAR_ALIGNMENT': PillarAlignmentRule,
            'ENERGY_PATTERN': EnergyPatternRule,
            'DEPENDENCY_CHECK': DependencyRule
        }
        self._rules_cache = {}
        
    async def load_rules_for_level(self, hierarchy_level: str) -> List[BaseRule]:
        """Load all active rules for a hierarchy level"""
        
        cache_key = f"rules_{hierarchy_level}"
        if cache_key in self._rules_cache:
            return self._rules_cache[cache_key]
        
        # Fetch rules from database
        result = await self.supabase.table('hrm_rules') \
            .select('*') \
            .eq('is_active', True) \
            .in_('hierarchy_level', [hierarchy_level, 'cross_level']) \
            .execute()
        
        rules = []
        for rule_data in result.data:
            rule_class = self._rule_registry.get(rule_data['rule_code'].split('_')[0] + '_' + rule_data['rule_code'].split('_')[1])
            if rule_class:
                rules.append(rule_class(rule_data))
            else:
                logger.warning(f"Unknown rule code: {rule_data['rule_code']}")
        
        self._rules_cache[cache_key] = rules
        return rules
    
    async def evaluate_entity(
        self,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate all applicable rules for an entity"""
        
        entity_type = context['entity_type']
        rules = await self.load_rules_for_level(entity_type)
        
        results = {
            'total_score': 0,
            'confidence': 0,
            'rule_results': [],
            'primary_factors': []
        }
        
        total_weight = 0
        confidence_sum = 0
        
        for rule in rules:
            if rule.applies_to(entity_type):
                try:
                    rule_result = await rule.evaluate(context)
                    
                    results['rule_results'].append({
                        'rule_name': rule.rule_name,
                        'score': rule_result['score'],
                        'confidence': rule_result['confidence'],
                        'reasoning': rule_result['reasoning'],
                        'factors': rule_result.get('factors', {})
                    })
                    
                    results['total_score'] += rule_result['score']
                    confidence_sum += rule_result['confidence'] * rule.weight
                    total_weight += rule.weight
                    
                except Exception as e:
                    logger.error(f"Rule {rule.rule_name} failed: {e}")
        
        # Normalize scores
        if total_weight > 0:
            results['total_score'] = min(1.0, results['total_score'] / total_weight)
            results['confidence'] = confidence_sum / total_weight
        
        # Identify primary factors
        results['rule_results'].sort(key=lambda x: x['score'], reverse=True)
        results['primary_factors'] = [
            r['reasoning'] for r in results['rule_results'][:3]
        ]
        
        return results
    
    async def get_user_rule_weights(self, user_id: str) -> Dict[str, float]:
        """Get user's customized rule weights"""
        
        result = await self.supabase.table('hrm_user_preferences') \
            .select('rule_weight_overrides') \
            .eq('user_id', user_id) \
            .single() \
            .execute()
        
        if result.data:
            return result.data.get('rule_weight_overrides', {})
        return {}
    
    def clear_cache(self):
        """Clear the rules cache"""
        self._rules_cache.clear()
```

### 3.2 Files to MODIFY

#### 3.2.1 Modify `backend/ai_coach_mvp_service.py`
```python
# REPLACE the entire get_today_priorities method with:

async def get_today_priorities(self, user_id: str, use_hrm: bool = True) -> Dict[str, Any]:
    """
    Get prioritized tasks for today using HRM or fallback to rule-based
    
    Args:
        user_id: User ID
        use_hrm: Whether to use the new HRM system (default: True)
    """
    if use_hrm:
        try:
            # Use the new HRM system
            from hrm_service import HierarchicalReasoningModel
            from blackboard_service import BlackboardService
            
            hrm = HierarchicalReasoningModel(user_id)
            blackboard = BlackboardService()
            
            # Get all active tasks
            tasks_resp = await self.supabase.table('tasks').select(
                'id, name, description, status, priority, due_date, project_id, completed, dependency_task_ids, hrm_priority_score'
            ).eq('user_id', user_id).eq('completed', False).execute()
            
            tasks = tasks_resp.data or []
            
            # Filter active statuses
            active_statuses = {'todo', 'in_progress', 'review'}
            tasks = [t for t in tasks if (t.get('status') in active_statuses or not t.get('status'))]
            
            if not tasks:
                return {'date': datetime.now().isoformat(), 'tasks': [], 'hrm_enabled': True}
            
            # Analyze each task with HRM
            analyzed_tasks = []
            
            for task in tasks[:10]:  # Limit to top 10 for performance
                # Check blackboard for recent insights
                recent_insights = await blackboard.get_insights_for_entity(
                    user_id, 'task', task['id'], 
                    insight_types=['priority_reasoning'],
                    limit=1
                )
                
                if recent_insights and (datetime.now() - datetime.fromisoformat(recent_insights[0]['created_at'])).hours < 6:
                    # Use cached insight
                    insight = recent_insights[0]
                    task['hrm_analysis'] = insight['detailed_reasoning']
                    task['hrm_priority_score'] = insight['confidence_score'] * 100
                    task['reasoning_summary'] = insight['summary']
                else:
                    # Get fresh HRM analysis
                    insight = await hrm.analyze_entity('task', task['id'], 'minimal')
                    
                    task['hrm_analysis'] = insight.detailed_reasoning
                    task['hrm_priority_score'] = insight.confidence_score * 100
                    task['reasoning_summary'] = insight.summary
                    
                    # Update task with HRM score
                    await self.supabase.table('tasks').update({
                        'hrm_priority_score': task['hrm_priority_score'],
                        'hrm_reasoning_summary': task['reasoning_summary'],
                        'hrm_last_analyzed': datetime.utcnow().isoformat()
                    }).eq('id', task['id']).execute()
                
                analyzed_tasks.append(task)
            
            # Sort by HRM priority score
            analyzed_tasks.sort(key=lambda x: x.get('hrm_priority_score', 0), reverse=True)
            
            # Get hierarchical insights for top 3 tasks
            top_tasks_with_insights = []
            for task in analyzed_tasks[:3]:
                hierarchical_insights = await blackboard.get_hierarchical_insights(user_id, task['id'])
                task['hierarchical_insights'] = hierarchical_insights
                top_tasks_with_insights.append(task)
            
            return {
                'date': datetime.now().isoformat(),
                'tasks': analyzed_tasks,
                'top_tasks_with_insights': top_tasks_with_insights,
                'hrm_enabled': True,
                'analysis_method': 'hierarchical_reasoning_model'
            }
            
        except Exception as e:
            logger.error(f"HRM analysis failed, falling back to rule-based: {e}")
            # Fall back to original implementation
            use_hrm = False
    
    if not use_hrm:
        # Original rule-based implementation
        # [Keep existing implementation as fallback]
        pass

# ADD new method for real-time HRM analysis:

async def analyze_entity_with_hrm(
    self, 
    user_id: str, 
    entity_type: str, 
    entity_id: str,
    analysis_depth: str = "balanced"
) -> Dict[str, Any]:
    """
    Analyze any entity (pillar, area, project, task) with HRM
    
    Args:
        user_id: User ID
        entity_type: One of 'pillar', 'area', 'project', 'task'
        entity_id: UUID of the entity
        analysis_depth: 'minimal', 'balanced', or 'detailed'
    
    Returns:
        Comprehensive HRM analysis with insights and recommendations
    """
    from hrm_service import HierarchicalReasoningModel
    
    hrm = HierarchicalReasoningModel(user_id)
    insight = await hrm.analyze_entity(entity_type, entity_id, analysis_depth)
    
    return {
        'entity_type': entity_type,
        'entity_id': entity_id,
        'analysis': {
            'title': insight.title,
            'summary': insight.summary,
            'confidence_score': insight.confidence_score,
            'impact_score': insight.impact_score,
            'reasoning_path': [
                {
                    'level': node.level,
                    'entity_name': node.entity_name,
                    'reasoning': node.reasoning,
                    'confidence': node.confidence
                }
                for node in insight.reasoning_path
            ],
            'recommendations': insight.recommendations,
            'detailed_reasoning': insight.detailed_reasoning
        },
        'generated_at': datetime.utcnow().isoformat()
    }
```

#### 3.2.2 Modify `backend/server.py`
```python
# ADD these imports at the top:
from hrm_service import HierarchicalReasoningModel
from blackboard_service import BlackboardService
from hrm_rules_engine import HRMRulesEngine

# ADD these service initializations after existing services:
blackboard_service = BlackboardService()
hrm_rules_engine = HRMRulesEngine()

# ADD these new endpoints:

@api_router.get("/insights/{entity_type}/{entity_id}")
async def get_entity_insights(
    entity_type: str,
    entity_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get HRM insights for any entity"""
    try:
        insights = await blackboard_service.get_insights_for_entity(
            str(current_user.id),
            entity_type,
            entity_id,
            active_only=True,
            limit=5
        )
        return {"insights": insights}
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to get insights")

@api_router.post("/insights/{entity_type}/{entity_id}/analyze")
async def analyze_entity(
    entity_type: str,
    entity_id: str,
    analysis_depth: str = Query("balanced", regex="^(minimal|balanced|detailed)$"),
    current_user: User = Depends(get_current_active_user)
):
    """Trigger HRM analysis for an entity"""
    try:
        result = await ai_coach_service.analyze_entity_with_hrm(
            str(current_user.id),
            entity_type,
            entity_id,
            analysis_depth
        )
        return result
    except Exception as e:
        logger.error(f"Error analyzing entity: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze entity")

@api_router.post("/insights/{insight_id}/feedback")
async def submit_insight_feedback(
    insight_id: str,
    feedback: str = Query(..., regex="^(accepted|rejected|modified|ignored)$"),
    feedback_details: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Submit feedback on an insight"""
    try:
        await blackboard_service.mark_insight_feedback(
            str(current_user.id),
            insight_id,
            feedback,
            feedback_details
        )
        return {"status": "feedback recorded"}
    except Exception as e:
        logger.error(f"Error recording feedback: {e}")
        raise HTTPException(status_code=500, detail="Failed to record feedback")

@api_router.get("/insights/patterns/me")
async def get_my_insight_patterns(
    lookback_days: int = Query(30, ge=7, le=90),
    current_user: User = Depends(get_current_active_user)
):
    """Get patterns from user's insights"""
    try:
        patterns = await blackboard_service.get_insight_patterns(
            str(current_user.id),
            lookback_days
        )
        return patterns
    except Exception as e:
        logger.error(f"Error getting patterns: {e}")
        raise HTTPException(status_code=500, detail="Failed to get patterns")

@api_router.get("/hrm/preferences")
async def get_hrm_preferences(current_user: User = Depends(get_current_active_user)):
    """Get user's HRM preferences"""
    try:
        result = await supabase_manager.client.table('hrm_user_preferences') \
            .select('*') \
            .eq('user_id', str(current_user.id)) \
            .single() \
            .execute()
        
        if result.data:
            return result.data
        else:
            # Return defaults
            return {
                "explanation_detail_level": "balanced",
                "show_confidence_scores": True,
                "show_reasoning_path": True,
                "ai_personality": "coach",
                "primary_optimization": "balance",
                "energy_pattern": "steady"
            }
    except Exception as e:
        logger.error(f"Error getting preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to get preferences")

@api_router.put("/hrm/preferences")
async def update_hrm_preferences(
    preferences: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
):
    """Update user's HRM preferences"""
    try:
        # Check if preferences exist
        existing = await supabase_manager.client.table('hrm_user_preferences') \
            .select('id') \
            .eq('user_id', str(current_user.id)) \
            .execute()
        
        if existing.data:
            # Update
            result = await supabase_manager.client.table('hrm_user_preferences') \
                .update(preferences) \
                .eq('user_id', str(current_user.id)) \
                .execute()
        else:
            # Insert
            result = await supabase_manager.client.table('hrm_user_preferences') \
                .insert({**preferences, 'user_id': str(current_user.id)}) \
                .execute()
        
        return result.data[0]
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        raise HTTPException(status_code=500, detail="Failed to update preferences")

# MODIFY the existing /today endpoint to use HRM:

@api_router.get("/today")
async def get_today_tasks(
    coaching_top_n: int = Query(3, ge=0, le=10),
    use_hrm: bool = Query(True, description="Use Hierarchical Reasoning Model"),
    current_user: User = Depends(get_current_active_user)
):
    """Get today's prioritized tasks with HRM analysis"""
    try:
        result = await ai_coach_service.get_today_priorities(
            str(current_user.id),
            use_hrm=use_hrm
        )
        return result
    except Exception as e:
        logger.error(f"Error getting today tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to get today tasks")
```

#### 3.2.3 Modify `backend/models.py`
```python
# ADD these new models after existing ones:

class HRMInsight(BaseModel):
    """Model for HRM-generated insights"""
    id: str
    user_id: str
    entity_type: str
    entity_id: Optional[str]
    insight_type: str
    title: str
    summary: str
    detailed_reasoning: Dict[str, Any]
    confidence_score: float
    impact_score: float
    reasoning_path: List[Dict[str, Any]]
    user_feedback: Optional[str]
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime]

class HRMPreferences(BaseModel):
    """User preferences for HRM behavior"""
    explanation_detail_level: str = "balanced"
    show_confidence_scores: bool = True
    show_reasoning_path: bool = True
    ai_personality: str = "coach"
    ai_communication_style: str = "encouraging"
    primary_optimization: str = "balance"
    energy_pattern: str = "steady"
    preferred_work_hours: Dict[str, str] = {"start": "09:00", "end": "17:00"}
    enable_ai_learning: bool = True

class HRMAnalysisRequest(BaseModel):
    """Request model for HRM analysis"""
    entity_type: str
    entity_id: str
    analysis_depth: str = "balanced"
    include_recommendations: bool = True
    include_obstacles: bool = True

class InsightFeedback(BaseModel):
    """Model for insight feedback"""
    insight_id: str
    feedback: str  # accepted, rejected, modified, ignored
    feedback_text: Optional[str]
    suggested_improvement: Optional[str]

# MODIFY existing Task model to include HRM fields:
class Task(BaseDocument):
    # ... existing fields ...
    
    # ADD these fields:
    hrm_priority_score: Optional[float] = None
    hrm_reasoning_summary: Optional[str] = None
    hrm_last_analyzed: Optional[datetime] = None
    ai_suggested_timeblock: Optional[str] = None
    obstacle_risk: Optional[str] = None  # low, medium, high

# MODIFY existing Project model:
class Project(BaseDocument):
    # ... existing fields ...
    
    # ADD these fields:
    hrm_health_score: Optional[float] = None
    hrm_predicted_completion: Optional[date] = None
    hrm_risk_factors: Optional[List[Dict[str, Any]]] = None
    goal_coherence_score: Optional[float] = None

# MODIFY existing Area model:
class Area(BaseDocument):
    # ... existing fields ...
    
    # ADD these fields:
    time_allocation_actual: Optional[float] = None
    time_allocation_recommended: Optional[float] = None
    balance_score: Optional[float] = None

# MODIFY existing Pillar model:
class Pillar(BaseDocument):
    # ... existing fields ...
    
    # ADD these fields:
    vision_statement: Optional[str] = None
    success_metrics: Optional[List[Dict[str, Any]]] = None
    alignment_strength: Optional[float] = None
```

### 3.3 Files to REMOVE

#### 3.3.1 Remove `backend/ai_interactions.py` (if exists)
- This functionality is now handled by the insights table and blackboard service

#### 3.3.2 Remove simple rule-based scoring methods
- Keep them as fallback but mark as deprecated

---

## 4. Frontend Updates

### 4.1 Components to ADD

#### 4.1.1 `frontend/src/components/HRMInsightCard.jsx`
```jsx
import React, { useState } from 'react';
import { ChevronDown, ChevronUp, ThumbsUp, ThumbsDown, Brain, TrendingUp, AlertTriangle } from 'lucide-react';
import { api } from '../services/api';

const HRMInsightCard = ({ insight, onFeedback }) => {
  const [expanded, setExpanded] = useState(false);
  const [showReasoningPath, setShowReasoningPath] = useState(false);

  const handleFeedback = async (feedbackType) => {
    try {
      await api.post(`/api/insights/${insight.id}/feedback?feedback=${feedbackType}`);
      if (onFeedback) {
        onFeedback(insight.id, feedbackType);
      }
    } catch (error) {
      console.error('Failed to submit feedback:', error);
    }
  };

  const getInsightIcon = () => {
    switch (insight.insight_type) {
      case 'priority_reasoning':
        return <TrendingUp className="w-5 h-5" />;
      case 'obstacle_identification':
        return <AlertTriangle className="w-5 h-5" />;
      default:
        return <Brain className="w-5 h-5" />;
    }
  };

  const getConfidenceColor = (score) => {
    if (score >= 0.8) return 'text-green-400';
    if (score >= 0.6) return 'text-yellow-400';
    return 'text-orange-400';
  };

  return (
    <div className="bg-gray-800 rounded-lg p-4 mb-3 border border-gray-700">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3 flex-1">
          <div className="text-blue-400 mt-1">
            {getInsightIcon()}
          </div>
          <div className="flex-1">
            <h4 className="text-white font-medium text-sm mb-1">
              {insight.title}
            </h4>
            <p className="text-gray-300 text-sm">
              {insight.summary}
            </p>
          </div>
        </div>
        
        {/* Confidence Score */}
        {insight.confidence_score && (
          <div className={`text-xs ${getConfidenceColor(insight.confidence_score)} ml-3`}>
            {Math.round(insight.confidence_score * 100)}% confident
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="flex items-center justify-between mt-3">
        <div className="flex items-center space-x-2">
          <button
            onClick={() => handleFeedback('accepted')}
            className="text-gray-400 hover:text-green-400 transition-colors"
            title="This was helpful"
          >
            <ThumbsUp className="w-4 h-4" />
          </button>
          <button
            onClick={() => handleFeedback('rejected')}
            className="text-gray-400 hover:text-red-400 transition-colors"
            title="Not helpful"
          >
            <ThumbsDown className="w-4 h-4" />
          </button>
        </div>
        
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-gray-400 hover:text-white transition-colors flex items-center text-xs"
        >
          {expanded ? 'Less' : 'More'} details
          {expanded ? <ChevronUp className="w-4 h-4 ml-1" /> : <ChevronDown className="w-4 h-4 ml-1" />}
        </button>
      </div>

      {/* Expanded Details */}
      {expanded && (
        <div className="mt-4 pt-4 border-t border-gray-700">
          {/* Reasoning Path */}
          {insight.reasoning_path && insight.reasoning_path.length > 0 && (
            <div className="mb-4">
              <button
                onClick={() => setShowReasoningPath(!showReasoningPath)}
                className="text-sm text-gray-400 hover:text-white mb-2 flex items-center"
              >
                Reasoning Path
                {showReasoningPath ? <ChevronUp className="w-4 h-4 ml-1" /> : <ChevronDown className="w-4 h-4 ml-1" />}
              </button>
              
              {showReasoningPath && (
                <div className="space-y-2">
                  {insight.reasoning_path.map((node, index) => (
                    <div key={index} className="flex items-start space-x-2 text-xs">
                      <div className="text-gray-500 uppercase w-16">{node.level}:</div>
                      <div className="flex-1">
                        <span className="text-white">{node.entity_name}</span>
                        <p className="text-gray-400 mt-1">{node.reasoning}</p>
                        <span className={`${getConfidenceColor(node.confidence)}`}>
                          {Math.round(node.confidence * 100)}% confidence
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Recommendations */}
          {insight.recommendations && insight.recommendations.length > 0 && (
            <div className="mb-4">
              <h5 className="text-sm font-medium text-gray-300 mb-2">Recommendations:</h5>
              <ul className="space-y-1">
                {insight.recommendations.map((rec, index) => (
                  <li key={index} className="text-sm text-gray-400 flex items-start">
                    <span className="text-blue-400 mr-2">•</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Impact Score */}
          {insight.impact_score && (
            <div className="text-xs text-gray-500">
              Impact Score: {Math.round(insight.impact_score * 100)}%
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default HRMInsightCard;
```

#### 4.1.2 `frontend/src/components/HRMDashboard.jsx`
```jsx
import React, { useState, useEffect } from 'react';
import { Brain, Settings, TrendingUp, Target, AlertCircle, RefreshCw } from 'lucide-react';
import { api } from '../services/api';
import HRMInsightCard from './HRMInsightCard';
import HRMPreferencesModal from './HRMPreferencesModal';

const HRMDashboard = () => {
  const [insights, setInsights] = useState([]);
  const [patterns, setPatterns] = useState(null);
  const [preferences, setPreferences] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showPreferences, setShowPreferences] = useState(false);
  const [selectedEntityType, setSelectedEntityType] = useState('all');

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [insightsRes, patternsRes, prefsRes] = await Promise.all([
        api.get('/api/insights/global/all'),
        api.get('/api/insights/patterns/me'),
        api.get('/api/hrm/preferences')
      ]);

      setInsights(insightsRes.data.insights || []);
      setPatterns(patternsRes.data);
      setPreferences(prefsRes.data);
    } catch (error) {
      console.error('Failed to load HRM dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInsightFeedback = (insightId, feedbackType) => {
    // Update local state to reflect feedback
    setInsights(prev => prev.map(insight => 
      insight.id === insightId 
        ? { ...insight, user_feedback: feedbackType }
        : insight
    ));
  };

  const triggerGlobalAnalysis = async () => {
    try {
      await api.post('/api/insights/global/analyze?analysis_depth=detailed');
      // Reload insights after analysis
      setTimeout(loadDashboardData, 2000);
    } catch (error) {
      console.error('Failed to trigger analysis:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Loading HRM insights...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Brain className="w-8 h-8 text-blue-400" />
          <div>
            <h2 className="text-2xl font-bold text-white">AI Intelligence Center</h2>
            <p className="text-gray-400 text-sm">Hierarchical Reasoning Model Insights</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={triggerGlobalAnalysis}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Analyze Now</span>
          </button>
          
          <button
            onClick={() => setShowPreferences(true)}
            className="p-2 text-gray-400 hover:text-white transition-colors"
          >
            <Settings className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Quick Stats */}
      {patterns && (
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="text-3xl font-bold text-white mb-1">
              {patterns.total_insights}
            </div>
            <div className="text-sm text-gray-400">Total Insights</div>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="text-3xl font-bold text-green-400 mb-1">
              {Math.round((patterns.average_confidence || 0) * 100)}%
            </div>
            <div className="text-sm text-gray-400">Avg Confidence</div>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="text-3xl font-bold text-blue-400 mb-1">
              {Object.keys(patterns.insights_by_type || {}).length}
            </div>
            <div className="text-sm text-gray-400">Insight Types</div>
          </div>
          
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="text-3xl font-bold text-purple-400 mb-1">
              {patterns.feedback_summary?.insight_accepted || 0}
            </div>
            <div className="text-sm text-gray-400">Accepted Insights</div>
          </div>
        </div>
      )}

      {/* Entity Type Filter */}
      <div className="flex items-center space-x-4">
        <span className="text-gray-400 text-sm">Filter by:</span>
        <div className="flex space-x-2">
          {['all', 'pillar', 'area', 'project', 'task'].map(type => (
            <button
              key={type}
              onClick={() => setSelectedEntityType(type)}
              className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                selectedEntityType === type
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:text-white'
              }`}
            >
              {type.charAt(0).toUpperCase() + type.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Insights List */}
      <div className="space-y-2">
        {insights
          .filter(insight => selectedEntityType === 'all' || insight.entity_type === selectedEntityType)
          .map(insight => (
            <HRMInsightCard
              key={insight.id}
              insight={insight}
              onFeedback={handleInsightFeedback}
            />
          ))}
          
        {insights.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <AlertCircle className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No insights available yet.</p>
            <p className="text-sm mt-2">Click "Analyze Now" to generate insights.</p>
          </div>
        )}
      </div>

      {/* Preferences Modal */}
      {showPreferences && (
        <HRMPreferencesModal
          preferences={preferences}
          onClose={() => setShowPreferences(false)}
          onSave={async (newPrefs) => {
            try {
              await api.put('/api/hrm/preferences', newPrefs);
              setPreferences(newPrefs);
              setShowPreferences(false);
            } catch (error) {
              console.error('Failed to save preferences:', error);
            }
          }}
        />
      )}
    </div>
  );
};

export default HRMDashboard;
```

### 4.2 Components to MODIFY

#### 4.2.1 Modify `frontend/src/components/Today.jsx`
```jsx
// ADD import at top:
import HRMInsightCard from './HRMInsightCard';

// ADD state for HRM insights:
const [hrmInsights, setHrmInsights] = useState({});
const [showHrmAnalysis, setShowHrmAnalysis] = useState(true);

// MODIFY the fetchTodayTasks function:
const fetchTodayTasks = async () => {
  try {
    setLoading(true);
    // Include HRM parameter
    const response = await todayAPI.getTodayTasks(3, true); // use_hrm = true
    
    if (response.data.hrm_enabled) {
      // Extract HRM insights from top tasks
      const insights = {};
      response.data.top_tasks_with_insights?.forEach(task => {
        if (task.hierarchical_insights) {
          insights[task.id] = task.hierarchical_insights;
        }
      });
      setHrmInsights(insights);
    }
    
    setTasks(response.data.tasks || []);
  } catch (err) {
    console.error('Failed to fetch today tasks:', err);
    setError(err.message);
  } finally {
    setLoading(false);
  }
};

// ADD toggle for HRM analysis display:
<div className="flex items-center justify-between mb-4">
  <h2 className="text-2xl font-bold text-white">Today's Priorities</h2>
  <button
    onClick={() => setShowHrmAnalysis(!showHrmAnalysis)}
    className="text-sm text-gray-400 hover:text-white flex items-center"
  >
    <Brain className="w-4 h-4 mr-1" />
    {showHrmAnalysis ? 'Hide' : 'Show'} AI Analysis
  </button>
</div>

// MODIFY task rendering to include HRM analysis:
{tasks.map((task, index) => (
  <div key={task.id} className="mb-4">
    {/* Existing task card */}
    <TaskCard task={task} />
    
    {/* HRM Analysis for top 3 tasks */}
    {showHrmAnalysis && index < 3 && task.hrm_analysis && (
      <div className="ml-4 mt-2">
        <HRMInsightCard
          insight={{
            id: `task-${task.id}-analysis`,
            title: 'Priority Analysis',
            summary: task.reasoning_summary,
            confidence_score: task.hrm_priority_score / 100,
            detailed_reasoning: task.hrm_analysis,
            reasoning_path: hrmInsights[task.id]?.task?.[0]?.reasoning_path
          }}
        />
      </div>
    )}
  </div>
))}
```

#### 4.2.2 Modify `frontend/src/components/Tasks.jsx`
```jsx
// ADD HRM analysis button to task actions:
const analyzeTaskWithHRM = async (taskId) => {
  try {
    const response = await api.post(`/api/insights/task/${taskId}/analyze?analysis_depth=balanced`);
    
    // Show analysis in a modal or side panel
    setSelectedTaskAnalysis(response.data.analysis);
    setShowAnalysisModal(true);
  } catch (error) {
    console.error('Failed to analyze task:', error);
  }
};

// ADD to task action buttons:
<button
  onClick={() => analyzeTaskWithHRM(task.id)}
  className="text-blue-400 hover:text-blue-300 transition-colors"
  title="AI Analysis"
>
  <Brain className="w-4 h-4" />
</button>
```

#### 4.2.3 Modify `frontend/src/App.js`
```jsx
// ADD import:
import HRMDashboard from './components/HRMDashboard';

// ADD route:
<Route 
  path="/intelligence" 
  element={
    <ProtectedRoute>
      <HRMDashboard />
    </ProtectedRoute>
  } 
/>

// ADD navigation item in sidebar:
{
  name: 'AI Intelligence',
  path: '/intelligence',
  icon: Brain,
  description: 'HRM insights and analysis'
}
```

### 4.3 Components to REMOVE

- Remove any references to `ai_interactions` tracking
- Remove simple priority scoring UI elements (keep as fallback)

---

## 5. API Changes

### 5.1 New Endpoints

```yaml
# HRM Analysis Endpoints
POST   /api/insights/{entity_type}/{entity_id}/analyze
GET    /api/insights/{entity_type}/{entity_id}
POST   /api/insights/{insight_id}/feedback
GET    /api/insights/patterns/me

# HRM Preferences
GET    /api/hrm/preferences
PUT    /api/hrm/preferences

# Enhanced Today with HRM
GET    /api/today?use_hrm=true
```

### 5.2 Modified Endpoints

```yaml
# Today endpoint now includes HRM analysis
GET    /api/today
Response includes:
  - hrm_enabled: boolean
  - top_tasks_with_insights: array
  - analysis_method: string

# Tasks include HRM scores
GET    /api/tasks
Response includes:
  - hrm_priority_score: number
  - hrm_reasoning_summary: string
  - hrm_last_analyzed: datetime
```

### 5.3 Deprecated Endpoints

```yaml
# These remain for backward compatibility but are deprecated
POST   /api/ai-interactions  # Replaced by insights
```

---

## 6. Migration Strategy

### 6.1 Database Migration Script

```sql
-- Run in this order:

-- 1. Create new tables
CREATE TABLE public.insights (...);
CREATE TABLE public.hrm_rules (...);
CREATE TABLE public.hrm_user_preferences (...);
CREATE TABLE public.hrm_feedback_log (...);

-- 2. Add columns to existing tables
ALTER TABLE public.tasks ADD COLUMN hrm_priority_score DECIMAL(5,2);
-- ... (other ALTER statements)

-- 3. Migrate ai_interactions data
INSERT INTO public.insights (...) SELECT ... FROM public.ai_interactions;

-- 4. Create initial HRM rules
INSERT INTO public.hrm_rules (rule_code, rule_name, ...) VALUES
  ('TEMPORAL_URGENCY_001', 'Task Deadline Urgency', ...),
  ('PILLAR_ALIGNMENT_001', 'Pillar Alignment Scoring', ...),
  ('ENERGY_PATTERN_001', 'Energy-Based Scheduling', ...),
  ('DEPENDENCY_CHECK_001', 'Task Dependency Analysis', ...);

-- 5. Create default preferences for existing users
INSERT INTO public.hrm_user_preferences (user_id)
SELECT id FROM auth.users
ON CONFLICT DO NOTHING;

-- 6. Drop deprecated table (after verification)
DROP TABLE public.ai_interactions;
```

### 6.2 Feature Flag Implementation

```python
# In backend/server.py
HRM_ENABLED = os.environ.get('HRM_ENABLED', 'true').lower() == 'true'

# Use throughout code:
if HRM_ENABLED:
    # Use HRM system
else:
    # Use legacy system
```

### 6.3 Rollout Plan

1. **Week 1**: Deploy database changes, keep HRM disabled
2. **Week 2**: Enable HRM for internal testing
3. **Week 3**: Enable for 10% of users
4. **Week 4**: Enable for 50% of users
5. **Week 5**: Enable for all users
6. **Week 6**: Remove legacy code

---

## 7. Testing Requirements

### 7.1 Unit Tests

```python
# backend/tests/test_hrm_service.py
class TestHierarchicalReasoningModel:
    async def test_analyze_task_entity(self):
        # Test task analysis with full hierarchy
        
    async def test_reasoning_path_construction(self):
        # Test reasoning path builds correctly
        
    async def test_confidence_scoring(self):
        # Test confidence calculations
        
    async def test_llm_prompt_generation(self):
        # Test prompt construction
```

### 7.2 Integration Tests

```python
# backend/tests/test_hrm_integration.py
class TestHRMIntegration:
    async def test_end_to_end_task_analysis(self):
        # Create full PAPT hierarchy
        # Analyze task
        # Verify insights stored
        # Check API responses
        
    async def test_blackboard_pub_sub(self):
        # Test insight notifications
        
    async def test_feedback_learning(self):
        # Submit feedback
        # Verify it affects future analyses
```

### 7.3 Performance Tests

```python
# backend/tests/test_hrm_performance.py
class TestHRMPerformance:
    async def test_bulk_analysis_performance(self):
        # Analyze 100 tasks
        # Verify < 30 seconds total
        
    async def test_caching_effectiveness(self):
        # Repeated analyses should use cache
        
    async def test_concurrent_analyses(self):
        # 10 concurrent users
        # Verify no deadlocks
```

### 7.4 UI/UX Tests

- Test insight card interactions
- Verify reasoning path display
- Test preference updates
- Validate mobile responsiveness

---

## Success Metrics

1. **User Engagement**
   - 80% of users view HRM insights daily
   - 60% provide feedback on insights
   - 40% customize HRM preferences

2. **System Performance**
   - < 2 second response time for analysis
   - 90% cache hit rate for recent insights
   - < 100ms blackboard write time

3. **Business Impact**
   - 25% increase in task completion rate
   - 30% improvement in user-reported alignment
   - 20% reduction in "analysis paralysis" support tickets

4. **AI Quality**
   - 85% positive feedback rate on insights
   - 90% confidence score accuracy
   - < 5% conflicting recommendations

---

## Risk Mitigation

1. **LLM API Failures**
   - Fallback to rule-based system
   - Cache recent analyses
   - Implement circuit breakers

2. **Performance Degradation**
   - Aggressive caching strategy
   - Background analysis jobs
   - Rate limiting per user

3. **User Confusion**
   - Gradual rollout with education
   - Clear explanation toggles
   - In-app guided tour

4. **Data Privacy**
   - All analysis done server-side
   - No PII in LLM prompts
   - User control over data retention

---

This PRD provides a complete blueprint for transforming Aurum Life's AI architecture from basic rule-based scoring to a sophisticated LLM-Augmented Hierarchical Reasoning Model. The implementation maintains backward compatibility while providing a clear path to advanced AI capabilities that truly understand and support the Intentional Professional's journey toward vertical alignment.