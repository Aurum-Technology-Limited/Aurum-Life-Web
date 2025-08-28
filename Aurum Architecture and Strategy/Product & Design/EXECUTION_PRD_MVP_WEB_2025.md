# Aurum Life MVP Web App - Execution PRD for AI-Enhanced Architecture

**Version:** 1.0  
**Date:** January 2025  
**Document Type:** Execution Requirements for Development Agent  
**Target:** MVP Web Application with Enhanced AI Architecture  

---

## 📋 Executive Summary

This document provides comprehensive execution requirements for implementing Aurum Life's enhanced AI architecture as an MVP web application. The implementation will transform the existing rule-based system into a sophisticated LLM-Augmented Hierarchical Reasoning Model (HRM) while maintaining all current functionality.

**Key Documents Referenced:**
- `/workspace/Aurum Architecture and Strategy/aurum_life_hrm_phase3_prd.md` - Complete HRM technical specifications
- `/workspace/Aurum Architecture and Strategy/aurum_life_hrm_ui_epics_user_stories.md` - UI/UX requirements
- `/workspace/Aurum Architecture and Strategy/aurum_life_new_screens_specification.md` - New screen designs
- `/workspace/Aurum Architecture and Strategy/aurum_life_wireframes_web.md` - Web wireframes
- `/workspace/Aurum Architecture and Strategy/aurum_life_wireframes_mobile.md` - Mobile wireframes

---

## 🎯 Implementation Scope

### Core Objectives
1. **Implement HRM Architecture** - Transform from rule-based to LLM-augmented reasoning
2. **Create Blackboard System** - Centralized insights repository with pub/sub capabilities
3. **Build New UI Components** - AI-powered interfaces for insights and interaction
4. **Maintain Existing Features** - Ensure backward compatibility with current functionality
5. **Optimize Performance** - Implement caching and efficient data patterns

### Out of Scope for MVP
- Mobile native app (web-responsive only)
- Voice assistant integration
- AR features
- Third-party calendar sync
- Team collaboration features

---

## 🏗️ Technical Architecture Requirements

### 1. Database Schema Updates

**Location:** Create migration files in `/workspace/backend/migrations/`

#### 1.1 New Tables Required

```sql
-- File: 001_create_insights_table.sql
-- Reference: aurum_life_hrm_phase3_prd.md - Section 2.1.1
CREATE TABLE public.insights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    entity_type TEXT NOT NULL CHECK (entity_type IN ('pillar', 'area', 'project', 'task', 'global')),
    entity_id UUID,
    insight_type TEXT NOT NULL CHECK (insight_type IN (
        'priority_reasoning', 'alignment_analysis', 'pattern_recognition',
        'recommendation', 'goal_coherence', 'time_allocation',
        'progress_prediction', 'obstacle_identification'
    )),
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    detailed_reasoning JSONB NOT NULL,
    confidence_score DECIMAL(3,2) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
    impact_score DECIMAL(3,2) CHECK (impact_score >= 0 AND impact_score <= 1),
    reasoning_path JSONB NOT NULL DEFAULT '[]'::JSONB,
    llm_session_id TEXT,
    llm_context JSONB,
    llm_model_used TEXT DEFAULT 'gemini-2.0-flash',
    user_feedback TEXT CHECK (user_feedback IN ('accepted', 'rejected', 'modified', 'ignored')),
    feedback_details JSONB,
    application_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    is_pinned BOOLEAN DEFAULT false,
    expires_at TIMESTAMP WITH TIME ZONE,
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],
    version INTEGER DEFAULT 1,
    previous_version_id UUID REFERENCES public.insights(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for performance
CREATE INDEX idx_insights_user_entity ON insights(user_id, entity_type, entity_id);
CREATE INDEX idx_insights_active ON insights(user_id, is_active, created_at DESC);
CREATE INDEX idx_insights_type ON insights(user_id, insight_type, created_at DESC);
CREATE INDEX idx_insights_expiry ON insights(expires_at) WHERE expires_at IS NOT NULL;
```

```sql
-- File: 002_create_hrm_rules_table.sql
-- Reference: aurum_life_hrm_phase3_prd.md - Section 2.1.2
CREATE TABLE public.hrm_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_code TEXT UNIQUE NOT NULL,
    rule_name TEXT NOT NULL,
    description TEXT NOT NULL,
    hierarchy_level TEXT NOT NULL CHECK (hierarchy_level IN ('pillar', 'area', 'project', 'task', 'cross_level')),
    applies_to_entity_types TEXT[] NOT NULL,
    rule_type TEXT NOT NULL CHECK (rule_type IN (
        'scoring', 'filtering', 'relationship',
        'temporal', 'constraint', 'pattern_matching'
    )),
    rule_config JSONB NOT NULL,
    base_weight DECIMAL(3,2) DEFAULT 0.5 CHECK (base_weight >= 0 AND base_weight <= 1),
    user_adjustable BOOLEAN DEFAULT false,
    requires_llm BOOLEAN DEFAULT false,
    llm_prompt_template TEXT,
    is_active BOOLEAN DEFAULT true,
    is_system_rule BOOLEAN DEFAULT true,
    created_by TEXT DEFAULT 'system',
    version INTEGER DEFAULT 1,
    changelog JSONB DEFAULT '[]'::JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

```sql
-- File: 003_create_hrm_preferences_table.sql
-- Reference: aurum_life_hrm_phase3_prd.md - Section 2.1.3
CREATE TABLE public.hrm_user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    rule_weight_overrides JSONB DEFAULT '{}'::JSONB,
    explanation_detail_level TEXT DEFAULT 'balanced' CHECK (explanation_detail_level IN ('minimal', 'balanced', 'detailed')),
    show_confidence_scores BOOLEAN DEFAULT true,
    show_reasoning_path BOOLEAN DEFAULT true,
    ai_personality TEXT DEFAULT 'coach' CHECK (ai_personality IN ('coach', 'assistant', 'strategist', 'motivator')),
    ai_communication_style TEXT DEFAULT 'encouraging' CHECK (ai_communication_style IN ('direct', 'encouraging', 'analytical', 'socratic')),
    primary_optimization TEXT DEFAULT 'balance' CHECK (primary_optimization IN (
        'balance', 'focus', 'exploration', 'efficiency', 'wellbeing'
    )),
    preferred_work_hours JSONB DEFAULT '{"start": "09:00", "end": "17:00"}'::JSONB,
    energy_pattern TEXT DEFAULT 'steady' CHECK (energy_pattern IN ('morning_peak', 'afternoon_peak', 'evening_peak', 'steady')),
    enable_ai_learning BOOLEAN DEFAULT true,
    share_anonymous_insights BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

```sql
-- File: 004_create_feedback_log_table.sql
-- Reference: aurum_life_hrm_phase3_prd.md - Section 2.1.4
CREATE TABLE public.hrm_feedback_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    insight_id UUID REFERENCES public.insights(id) ON DELETE SET NULL,
    feedback_type TEXT NOT NULL CHECK (feedback_type IN (
        'insight_helpful', 'insight_not_helpful',
        'priority_correct', 'priority_incorrect',
        'reasoning_clear', 'reasoning_unclear',
        'recommendation_followed', 'recommendation_ignored'
    )),
    entity_type TEXT,
    entity_id UUID,
    original_score DECIMAL(5,2),
    user_adjusted_score DECIMAL(5,2),
    feedback_text TEXT,
    suggested_improvement TEXT,
    applied_rules JSONB,
    reasoning_snapshot JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 1.2 Existing Table Modifications

```sql
-- File: 005_modify_existing_tables.sql
-- Reference: aurum_life_hrm_phase3_prd.md - Section 2.2
-- Add HRM fields to tasks table
ALTER TABLE public.tasks ADD COLUMN IF NOT EXISTS hrm_priority_score DECIMAL(5,2);
ALTER TABLE public.tasks ADD COLUMN IF NOT EXISTS hrm_reasoning_summary TEXT;
ALTER TABLE public.tasks ADD COLUMN IF NOT EXISTS hrm_last_analyzed TIMESTAMP WITH TIME ZONE;
ALTER TABLE public.tasks ADD COLUMN IF NOT EXISTS ai_suggested_timeblock TEXT;
ALTER TABLE public.tasks ADD COLUMN IF NOT EXISTS obstacle_risk TEXT CHECK (obstacle_risk IN ('low', 'medium', 'high'));
CREATE INDEX idx_tasks_hrm_priority ON tasks(user_id, completed, hrm_priority_score DESC) WHERE completed = false;

-- Add HRM fields to projects table
ALTER TABLE public.projects ADD COLUMN IF NOT EXISTS hrm_health_score DECIMAL(3,2);
ALTER TABLE public.projects ADD COLUMN IF NOT EXISTS hrm_predicted_completion DATE;
ALTER TABLE public.projects ADD COLUMN IF NOT EXISTS hrm_risk_factors JSONB DEFAULT '[]'::JSONB;
ALTER TABLE public.projects ADD COLUMN IF NOT EXISTS goal_coherence_score DECIMAL(3,2);

-- Add HRM fields to areas table
ALTER TABLE public.areas ADD COLUMN IF NOT EXISTS time_allocation_actual DECIMAL(5,2);
ALTER TABLE public.areas ADD COLUMN IF NOT EXISTS time_allocation_recommended DECIMAL(5,2);
ALTER TABLE public.areas ADD COLUMN IF NOT EXISTS balance_score DECIMAL(3,2);

-- Add HRM fields to pillars table
ALTER TABLE public.pillars ADD COLUMN IF NOT EXISTS vision_statement TEXT;
ALTER TABLE public.pillars ADD COLUMN IF NOT EXISTS success_metrics JSONB DEFAULT '[]'::JSONB;
ALTER TABLE public.pillars ADD COLUMN IF NOT EXISTS alignment_strength DECIMAL(3,2);
```

#### 1.3 Data Migration

```sql
-- File: 006_migrate_ai_interactions.sql
-- Reference: aurum_life_hrm_phase3_prd.md - Section 2.3
-- Migrate existing ai_interactions data to insights table
INSERT INTO public.insights (
    user_id, entity_type, insight_type, title, summary, 
    detailed_reasoning, confidence_score, created_at
)
SELECT 
    user_id,
    'global' as entity_type,
    'pattern_recognition' as insight_type,
    interaction_type as title,
    'Historical AI interaction' as summary,
    jsonb_build_object('type', interaction_type, 'context_size', context_size) as detailed_reasoning,
    0.75 as confidence_score,
    created_at
FROM public.ai_interactions
WHERE EXISTS (SELECT 1 FROM public.ai_interactions LIMIT 1);

-- Drop the old table after verification
-- DROP TABLE IF EXISTS public.ai_interactions CASCADE;
```

```sql
-- File: 007_seed_hrm_rules.sql
-- Reference: aurum_life_hrm_phase3_prd.md - Section 6.1
INSERT INTO public.hrm_rules (rule_code, rule_name, description, hierarchy_level, applies_to_entity_types, rule_type, rule_config, base_weight, requires_llm) VALUES
('TEMPORAL_URGENCY_001', 'Task Deadline Urgency', 'Scores tasks based on deadline proximity', 'task', ARRAY['task'], 'temporal', 
 '{"conditions": {"due_date_proximity": "24h", "has_dependencies": false}, "actions": {"priority_boost": 0.3, "add_tag": "urgent"}}'::jsonb, 
 0.7, false),
 
('PILLAR_ALIGNMENT_001', 'Pillar Alignment Scoring', 'Scores entities based on pillar importance and time allocation', 'cross_level', ARRAY['task', 'project', 'area'], 'scoring',
 '{"factors": ["pillar_time_allocation", "area_importance", "project_priority"], "aggregation": "weighted_average"}'::jsonb,
 0.8, false),
 
('ENERGY_PATTERN_001', 'Energy-Based Task Matching', 'Matches tasks to user energy patterns', 'task', ARRAY['task'], 'temporal',
 '{"energy_mapping": {"deep_work": ["morning_peak"], "admin": ["afternoon"], "creative": ["evening_peak"]}}'::jsonb,
 0.5, true),
 
('DEPENDENCY_CHECK_001', 'Task Dependency Analysis', 'Analyzes and scores based on dependency status', 'task', ARRAY['task'], 'constraint',
 '{"blocking_penalty": 0.8, "ready_boost": 0.2}'::jsonb,
 0.6, false);
```

### 2. Backend Service Implementation

#### 2.1 Core HRM Service

**File:** `/workspace/backend/hrm_service.py`
**Reference:** `aurum_life_hrm_phase3_prd.md` - Section 3.1.1

```python
# Implementation structure based on PRD specifications
# Full implementation details in aurum_life_hrm_phase3_prd.md - Section 3.1.1

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
        
    async def analyze_entity(self, entity_type: str, entity_id: Optional[str] = None, analysis_depth: str = "balanced") -> HRMInsight:
        """
        Perform hierarchical reasoning on an entity
        Reference: aurum_life_hrm_phase3_prd.md - analyze_entity method
        """
        # Implementation as specified in PRD
        pass
```

#### 2.2 Blackboard Service

**File:** `/workspace/backend/blackboard_service.py`
**Reference:** `aurum_life_hrm_phase3_prd.md` - Section 3.1.2

```python
# Implementation structure based on PRD specifications
# Full implementation details in aurum_life_hrm_phase3_prd.md - Section 3.1.2

class BlackboardService:
    """
    Centralized insight repository with pub/sub capabilities
    Implements the Blackboard architectural pattern for AI systems
    """
    
    async def store_insight(self, user_id: str, insight: Dict[str, Any], notify_subscribers: bool = True) -> str:
        """
        Store an insight and optionally notify subscribers
        Reference: aurum_life_hrm_phase3_prd.md - store_insight method
        """
        # Implementation as specified in PRD
        pass
```

#### 2.3 Rules Engine

**File:** `/workspace/backend/hrm_rules_engine.py`
**Reference:** `aurum_life_hrm_phase3_prd.md` - Section 3.1.3

```python
# Implementation structure based on PRD specifications
# Full implementation details in aurum_life_hrm_phase3_prd.md - Section 3.1.3

class HRMRulesEngine:
    """
    Main rules engine for HRM
    Manages and executes hierarchical rules for the reasoning model
    """
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self._rule_registry = {
            'TEMPORAL_URGENCY': TemporalUrgencyRule,
            'PILLAR_ALIGNMENT': PillarAlignmentRule,
            'ENERGY_PATTERN': EnergyPatternRule,
            'DEPENDENCY_CHECK': DependencyRule
        }
        self._rules_cache = {}
```

#### 2.4 API Endpoint Updates

**File:** `/workspace/backend/server.py`
**Reference:** `aurum_life_hrm_phase3_prd.md` - Section 3.2.2

Add these new endpoints:

```python
# New imports
from hrm_service import HierarchicalReasoningModel
from blackboard_service import BlackboardService
from hrm_rules_engine import HRMRulesEngine

# Service initialization
blackboard_service = BlackboardService()
hrm_rules_engine = HRMRulesEngine()

# New endpoints as specified in PRD Section 5.1
@api_router.get("/insights/{entity_type}/{entity_id}")
async def get_entity_insights(
    entity_type: str,
    entity_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get HRM insights for any entity"""
    # Implementation as specified in PRD
    pass

@api_router.post("/insights/{entity_type}/{entity_id}/analyze")
async def analyze_entity(
    entity_type: str,
    entity_id: str,
    analysis_depth: str = Query("balanced", regex="^(minimal|balanced|detailed)$"),
    current_user: User = Depends(get_current_active_user)
):
    """Trigger HRM analysis for an entity"""
    # Implementation as specified in PRD
    pass
```

### 3. Frontend Implementation

#### 3.1 New Components Required

**Reference:** `aurum_life_wireframes_web.md` for detailed specifications

##### 3.1.1 AI Command Center Component

**File:** `/workspace/frontend/src/components/AICommandCenter.jsx`
**Reference:** `aurum_life_wireframes_web.md` - Section 1

```jsx
import React, { useState, useEffect, useRef } from 'react';
import { Command } from 'lucide-react';
import { useHotkeys } from 'react-hotkeys-hook';

const AICommandCenter = () => {
  // Implementation based on wireframe specifications
  // Styling: Background #1F2937, Border #374151, etc.
  return (
    <div className="fixed inset-0 z-50 bg-black/70">
      {/* Implementation as per wireframe */}
    </div>
  );
};
```

##### 3.1.2 HRM Insight Card Component

**File:** `/workspace/frontend/src/components/HRMInsightCard.jsx`
**Reference:** `aurum_life_hrm_ui_epics_user_stories.md` - Section "New Components Needed"

```jsx
import React, { useState } from 'react';
import { ChevronDown, ChevronUp, ThumbsUp, ThumbsDown, Brain, TrendingUp, AlertTriangle } from 'lucide-react';

const HRMInsightCard = ({ insight, onFeedback }) => {
  // Implementation based on UI specifications
  return (
    <div className="bg-gray-800 rounded-lg p-4 mb-3 border border-gray-700">
      {/* Implementation as specified in user stories */}
    </div>
  );
};
```

##### 3.1.3 AI Insights Dashboard

**File:** `/workspace/frontend/src/components/AIInsightsDashboard.jsx`
**Reference:** `aurum_life_wireframes_web.md` - Section 2

```jsx
import React, { useState, useEffect } from 'react';
import { Brain, Settings, RefreshCw } from 'lucide-react';
import HRMInsightCard from './HRMInsightCard';
import { api } from '../services/api';

const AIInsightsDashboard = () => {
  // Implementation based on wireframe specifications
  // Stats cards, filter system, insights list
  return (
    <div className="p-6 bg-[#0B0D14]">
      {/* Implementation as per wireframe */}
    </div>
  );
};
```

##### 3.1.4 Focus Mode Component

**File:** `/workspace/frontend/src/components/FocusMode.jsx`
**Reference:** `aurum_life_wireframes_web.md` - Section 3

```jsx
import React, { useState, useEffect } from 'react';
import { Pause, Check, X } from 'lucide-react';

const FocusMode = ({ task, onComplete, onExit }) => {
  // Implementation based on wireframe specifications
  // Timer, progress ring, AI coaching
  return (
    <div className="fixed inset-0 bg-[#0B0D14] flex items-center justify-center">
      {/* Implementation as per wireframe */}
    </div>
  );
};
```

##### 3.1.5 Daily Planning Ritual

**File:** `/workspace/frontend/src/components/DailyPlanningRitual.jsx`
**Reference:** `aurum_life_wireframes_web.md` - Section 4

```jsx
import React, { useState } from 'react';
import { Sun } from 'lucide-react';

const DailyPlanningRitual = ({ onComplete, onSkip }) => {
  const [energy, setEnergy] = useState(null);
  const [schedule, setSchedule] = useState([]);
  
  // Implementation based on wireframe specifications
  return (
    <div className="max-w-4xl mx-auto p-8">
      {/* Implementation as per wireframe */}
    </div>
  );
};
```

#### 3.2 Component Integration

##### 3.2.1 Update App.js

**File:** `/workspace/frontend/src/App.js`

Add new routes and lazy imports:

```jsx
// Add to lazy imports section
const AIInsightsDashboard = lazy(() => import('./components/AIInsightsDashboard'));
const FocusMode = lazy(() => import('./components/FocusMode'));

// Add to navigation cases in renderActiveSection()
case 'ai-insights':
  return <AIInsightsDashboard {...props} />;
case 'focus':
  return <FocusMode {...props} />;
```

##### 3.2.2 Update Navigation

**File:** `/workspace/frontend/src/components/SimpleLayout.jsx`

Add new navigation items:

```jsx
const navigation = useMemo(() => [
  // ... existing items ...
  { name: 'AI Insights', key: 'ai-insights', icon: Brain },
  // ... rest of items ...
], []);
```

##### 3.2.3 Update Today Component

**File:** `/workspace/frontend/src/components/Today.jsx`
**Reference:** `aurum_life_hrm_ui_epics_user_stories.md` - Story 2.1

Modify to include HRM analysis:

```jsx
// Add HRM insight display to task cards
import HRMInsightCard from './HRMInsightCard';

// In the task rendering section:
{showHrmAnalysis && task.hrm_analysis && (
  <div className="ml-4 mt-2">
    <HRMInsightCard
      insight={{
        id: `task-${task.id}-analysis`,
        title: 'Priority Analysis',
        summary: task.hrm_reasoning_summary,
        confidence_score: task.hrm_priority_score / 100,
        detailed_reasoning: task.hrm_analysis
      }}
    />
  </div>
)}
```

### 4. API Integration Updates

#### 4.1 Update API Service

**File:** `/workspace/frontend/src/services/api.js`

Add new API endpoints:

```javascript
// HRM Insights API
export const insightsAPI = {
  getInsights: (entityType, entityId) => 
    api.get(`/api/insights/${entityType}/${entityId}`),
    
  analyzeEntity: (entityType, entityId, depth = 'balanced') =>
    api.post(`/api/insights/${entityType}/${entityId}/analyze?analysis_depth=${depth}`),
    
  submitFeedback: (insightId, feedback, details = null) =>
    api.post(`/api/insights/${insightId}/feedback?feedback=${feedback}`, details),
    
  getPatterns: (lookbackDays = 30) =>
    api.get(`/api/insights/patterns/me?lookback_days=${lookbackDays}`)
};

// HRM Preferences API
export const hrmAPI = {
  getPreferences: () => api.get('/api/hrm/preferences'),
  updatePreferences: (preferences) => api.put('/api/hrm/preferences', preferences)
};

// Update Today API to include HRM parameter
export const todayAPI = {
  getTodayTasks: (coachingTopN = 3, useHrm = true) => 
    api.get(`/api/today?coaching_top_n=${coachingTopN}&use_hrm=${useHrm}`),
  // ... rest of methods
};
```

### 5. Design System Updates

#### 5.1 Add AI-Specific Styles

**File:** `/workspace/frontend/src/index.css`

Add new design tokens:

```css
/* AI-specific colors */
:root {
  --ai-primary: #3B82F6;
  --ai-secondary: #8B5CF6;
  --ai-success: #10B981;
  --ai-warning: #F59E0B;
  --ai-danger: #EF4444;
  --ai-surface: #1E293B;
  --ai-surface-light: #334155;
}

/* AI-specific utilities */
@layer utilities {
  .ai-glow {
    box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
  }
  
  .ai-border {
    border-color: var(--ai-primary);
  }
  
  .confidence-high {
    color: var(--ai-success);
  }
  
  .confidence-medium {
    color: var(--ai-warning);
  }
  
  .confidence-low {
    color: var(--ai-danger);
  }
}
```

### 6. Performance Optimizations

#### 6.1 Caching Strategy

**File:** `/workspace/backend/cache_service.py`

Add HRM-specific caching:

```python
def cache_hrm_insight(user_id: str, entity_type: str, entity_id: str, ttl: int = 21600):
    """Cache HRM insights for 6 hours by default"""
    cache_key = f"hrm_insight:{user_id}:{entity_type}:{entity_id}"
    return cache_result(cache_key, ttl_seconds=ttl)

def cache_reasoning_path(user_id: str, task_id: str, ttl: int = 3600):
    """Cache reasoning paths for 1 hour"""
    cache_key = f"reasoning_path:{user_id}:{task_id}"
    return cache_result(cache_key, ttl_seconds=ttl)
```

#### 6.2 Query Optimization

**Reference:** `aurum_life_hrm_phase3_prd.md` - Performance sections

- Implement parallel fetching for hierarchy data
- Use database views for complex reasoning paths
- Batch API calls where possible
- Implement progressive loading for insights

### 7. Testing Requirements

#### 7.1 Backend Tests

**Directory:** `/workspace/backend/tests/`

Create test files:

1. `test_hrm_service.py` - Test HRM analysis functionality
2. `test_blackboard_service.py` - Test insight storage and retrieval
3. `test_hrm_rules_engine.py` - Test rule execution
4. `test_hrm_endpoints.py` - Test new API endpoints

#### 7.2 Frontend Tests

**Directory:** `/workspace/frontend/src/__tests__/`

Create test files:

1. `AICommandCenter.test.jsx` - Test command parsing and suggestions
2. `HRMInsightCard.test.jsx` - Test insight display and feedback
3. `AIInsightsDashboard.test.jsx` - Test dashboard functionality
4. `FocusMode.test.jsx` - Test timer and controls

### 8. Deployment Checklist

#### 8.1 Environment Variables

Add to `.env`:

```bash
# Existing variables remain unchanged
# Add HRM-specific configuration
HRM_ENABLED=true
HRM_DEFAULT_ANALYSIS_DEPTH=balanced
HRM_CACHE_TTL=21600
HRM_MAX_INSIGHTS_PER_USER=1000
```

#### 8.2 Database Migrations

1. Run all migration scripts in order (001-007)
2. Verify data migration from ai_interactions table
3. Create database backup before migrations
4. Test rollback procedures

#### 8.3 Feature Flags

Implement feature flag for gradual rollout:

```python
# In backend/server.py
HRM_ENABLED = os.environ.get('HRM_ENABLED', 'true').lower() == 'true'

# Use throughout code
if HRM_ENABLED:
    # Use HRM system
else:
    # Use legacy system
```

### 9. MVP Success Criteria

1. **Functional Requirements**
   - [ ] HRM analyzes tasks with reasoning paths
   - [ ] Insights are stored and retrievable
   - [ ] Users can provide feedback on insights
   - [ ] AI Command Center is accessible via Cmd+K
   - [ ] Daily planning ritual generates schedules
   - [ ] Focus mode tracks time with AI coaching

2. **Performance Requirements**
   - [ ] Insight generation < 3 seconds
   - [ ] Command center response < 500ms
   - [ ] Page load times < 2 seconds
   - [ ] Smooth animations at 60fps

3. **Quality Requirements**
   - [ ] 90% test coverage for new code
   - [ ] No regression in existing features
   - [ ] Accessibility compliance (WCAG 2.1 AA)
   - [ ] Mobile responsive design

### 10. Implementation Order

**Week 1: Foundation**
1. Database migrations and schema updates
2. Backend HRM service implementation
3. Blackboard service implementation
4. Basic API endpoints

**Week 2: Core Features**
1. AI Command Center component
2. HRM Insight Card component  
3. Update Today view with HRM
4. Implement caching layer

**Week 3: Advanced Features**
1. AI Insights Dashboard
2. Focus Mode implementation
3. Daily Planning Ritual
4. Rules engine completion

**Week 4: Polish & Testing**
1. Performance optimization
2. Comprehensive testing
3. Bug fixes and refinements
4. Documentation updates

---

## 📚 Additional References

- **Technical Architecture:** Review existing codebase structure in `/workspace/backend/` and `/workspace/frontend/`
- **Design System:** Maintain consistency with current dark theme (#0B0D14 background, #F59E0B primary)
- **AI Integration:** Leverage existing Gemini integration in `ai_coach_service.py`
- **Performance:** Follow patterns in `ultra_performance_services.py`

## 🚨 Important Notes

1. **Backward Compatibility:** All existing features must continue working during implementation
2. **Data Integrity:** Implement comprehensive data validation and error handling
3. **Security:** Follow existing authentication patterns and add rate limiting for AI endpoints
4. **Monitoring:** Add logging for all HRM decisions for debugging and improvement

This PRD provides a complete blueprint for implementing the enhanced AI architecture. Reference the linked documents for detailed specifications, wireframes, and user stories.