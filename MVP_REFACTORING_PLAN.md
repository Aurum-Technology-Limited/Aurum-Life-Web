# Aurum Life MVP v1.1 Refactoring Plan

## Executive Summary
This document outlines the technical refactoring plan to transform the existing Aurum Life web application into a lean, performant MVP focused on validating the core vertical alignment concept (Pillar → Area → Project → Task).

## Current State Analysis

### Technology Stack
- **Backend**: FastAPI, MongoDB, Celery/Redis, Supabase Auth
- **Frontend**: React 19, TanStack Query, Tailwind CSS, shadcn/ui components
- **Infrastructure**: Multiple test files indicate Supabase migration in progress

### Key Findings
1. **Over-engineered Features**: AI Coach, achievements, templates, insights, journal, etc.
2. **Multiple Auth Systems**: Legacy JWT + Supabase Auth (hybrid mode)
3. **Database**: MongoDB with some Supabase integration attempts
4. **Performance**: No clear optimization or benchmarking in place
5. **UI Complexity**: 30+ components including features outside MVP scope

## MVP Refactoring Strategy

### Phase 1: Backend Optimization & Simplification (Week 1-2)

#### 1.1 Database Performance
```
Priority: CRITICAL
Goal: P95 API response time < 150ms
```

**Tasks:**
- [ ] Add MongoDB indexes for hierarchy queries
  - `pillars`: user_id, sort_order
  - `areas`: user_id, pillar_id, sort_order
  - `projects`: user_id, area_id, sort_order, status
  - `tasks`: user_id, project_id, due_date, current_score, status
- [ ] Implement connection pooling
- [ ] Add query performance monitoring
- [ ] Remove N+1 queries in hierarchy fetching

#### 1.2 Simplify Scoring Engine
```
Priority: HIGH
Goal: Deterministic, fast task scoring
```

**Current Formula (to implement):**
```python
current_score = (user_priority * 0.6) + (urgency_score * 0.4)
urgency_score = max(0, 100 - days_until_due * 10)
```

**Tasks:**
- [ ] Simplify scoring_engine.py to basic formula
- [ ] Remove AI/ML dependencies
- [ ] Add background Celery task for score updates
- [ ] Index `current_score` field in tasks collection

#### 1.3 API Security Hardening
```
Priority: CRITICAL
Goal: Secure, authenticated API
```

**Tasks:**
- [ ] Consolidate to Supabase Auth only (remove legacy JWT)
- [ ] Add input validation middleware
- [ ] Implement rate limiting
- [ ] Enforce HTTPS redirect
- [ ] Add CORS configuration for production domain

#### 1.4 Remove Non-MVP Features
```
Priority: HIGH
Goal: Clean, focused codebase
```

**Backend files/features to remove:**
- [ ] ai_coach_service.py
- [ ] notification_service.py (keep minimal task reminders)
- [ ] All achievement/badge related code
- [ ] Course/learning functionality
- [ ] Journal features
- [ ] File storage features
- [ ] Templates (except basic CRUD)

### Phase 2: Frontend Simplification (Week 2-3)

#### 2.1 Component Reduction
```
Priority: HIGH
Goal: Minimal, fast UI
```

**Components to KEEP (and simplify):**
- [ ] Login.jsx (Supabase auth only)
- [ ] Layout.jsx (simplified navigation)
- [ ] Pillars.jsx
- [ ] Areas.jsx
- [ ] Projects.jsx
- [ ] Tasks.jsx (basic CRUD only)
- [ ] Today.jsx (primary view)
- [ ] UserMenu.jsx (profile/logout only)

**Components to REMOVE:**
- [ ] AICoach.jsx
- [ ] Achievements.jsx
- [ ] Journal.jsx
- [ ] Learning.jsx
- [ ] Insights.jsx
- [ ] KanbanBoard.jsx
- [ ] NotificationCenter.jsx
- [ ] ProjectTemplates.jsx
- [ ] RecurringTasks.jsx
- [ ] PomodoroTimer.jsx
- [ ] FileManager.jsx
- [ ] Feedback.jsx

#### 2.2 Today View Optimization
```
Priority: CRITICAL
Goal: Instant load, clear focus
```

**New Today View Features:**
- [ ] Single optimized query for today's tasks
- [ ] Simple task list with checkboxes
- [ ] Show parent Project/Area for context
- [ ] Morning Intention text field
- [ ] Evening Reflection text field
- [ ] No automation, just manual fields

#### 2.3 UI Performance
```
Priority: HIGH
Goal: < 3s initial load time
```

**Tasks:**
- [ ] Implement code splitting
- [ ] Add React.memo to list components
- [ ] Optimize TanStack Query caching
- [ ] Remove unused CSS/components
- [ ] Implement virtual scrolling for long lists

### Phase 3: Testing & Deployment (Week 3-4)

#### 3.1 Performance Testing
```
Priority: CRITICAL
Goal: Validate performance metrics
```

**Tests to implement:**
- [ ] API response time benchmarks
- [ ] Database query performance tests
- [ ] Frontend load time tests
- [ ] Concurrent user stress tests

#### 3.2 Data Migration
```
Priority: HIGH
Goal: Clean production data
```

**Tasks:**
- [ ] Archive removed features' data
- [ ] Migrate users to Supabase Auth
- [ ] Clean up orphaned records
- [ ] Backup production database

#### 3.3 Deployment
```
Priority: HIGH
Goal: Zero-downtime deployment
```

**Tasks:**
- [ ] Set up staging environment
- [ ] Create deployment scripts
- [ ] Configure monitoring/alerts
- [ ] Plan rollback strategy

## Success Metrics Implementation

### Technical Metrics
```python
# API Performance Monitor
@app.middleware("http")
async def monitor_performance(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Log if > 150ms (P95 target)
    if process_time > 0.15:
        logger.warning(f"Slow API: {request.url.path} took {process_time}s")
    
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### User Metrics Tracking
```javascript
// Track core loop completion
const trackOnboarding = {
  pillarCreated: false,
  areaCreated: false,
  projectCreated: false,
  taskCreated: false,
  
  checkCompletion: () => {
    if (all true) {
      analytics.track('core_loop_completed');
    }
  }
};
```

## Development Timeline

### Week 1: Backend Foundation
- Days 1-2: Database optimization & indexes
- Days 3-4: Simplify scoring engine
- Days 5: Security hardening

### Week 2: Backend Cleanup & Frontend Start
- Days 1-2: Remove non-MVP backend features
- Days 3-5: Frontend component reduction

### Week 3: Frontend Optimization
- Days 1-2: Today view implementation
- Days 3-4: Performance optimization
- Day 5: Integration testing

### Week 4: Launch Preparation
- Days 1-2: Performance testing
- Days 3-4: Staging deployment
- Day 5: Production deployment

## Risk Mitigation

### Technical Risks
1. **Data Loss**: Full backup before any changes
2. **Performance Regression**: Benchmark before/after each change
3. **Auth Migration Issues**: Maintain hybrid auth temporarily
4. **User Disruption**: Gradual feature removal with notices

### Rollback Plan
1. Git tags at each major milestone
2. Database backups before migrations
3. Feature flags for gradual rollout
4. Monitoring alerts for immediate detection

## Next Steps

1. **Immediate Actions**:
   - Create feature branch: `mvp-v1.1-refactor`
   - Set up performance monitoring
   - Begin database index creation

2. **Team Alignment**:
   - Review plan with engineering team
   - Assign ownership for each phase
   - Set up daily standups

3. **Communication**:
   - Notify users of upcoming changes
   - Prepare MVP feature documentation
   - Create migration guide

## Conclusion

This refactoring plan strips Aurum Life down to its essential value proposition: helping users connect daily tasks to life goals through vertical alignment. By removing complexity and focusing on performance, we can validate our core hypothesis with real users and gather critical feedback for future iterations.

The key is ruthless prioritization - if a feature isn't directly supporting the Pillar → Area → Project → Task hierarchy, it doesn't belong in the MVP.