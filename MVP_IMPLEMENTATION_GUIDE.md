# Aurum Life MVP v1.1 Implementation Guide

## Overview
This guide provides step-by-step instructions for refactoring the existing Aurum Life application into a lean MVP focused on the core vertical alignment concept.

## Pre-Implementation Checklist

- [ ] Create feature branch: `git checkout -b mvp-v1.1-refactor`
- [ ] Full database backup
- [ ] Document current performance baseline
- [ ] Notify team of refactoring start
- [ ] Set up staging environment

## Phase 1: Backend Optimization (Days 1-5)

### Day 1-2: Database Performance

1. **Run Database Optimizer**
   ```bash
   cd backend
   python database_optimizer.py
   ```
   This will:
   - Create all necessary indexes
   - Add `current_score` field to tasks
   - Create materialized views
   - Analyze current performance

2. **Verify Indexes**
   ```bash
   # Connect to MongoDB
   mongo mongodb://localhost:27017/aurum_life
   
   # Check indexes
   db.tasks.getIndexes()
   db.projects.getIndexes()
   db.areas.getIndexes()
   db.pillars.getIndexes()
   ```

3. **Update Connection Pooling**
   Update `backend/database.py`:
   ```python
   # Add connection pool settings
   client = AsyncIOMotorClient(
       mongo_url,
       maxPoolSize=50,
       minPoolSize=10,
       maxIdleTimeMS=45000
   )
   ```

### Day 3-4: Simplify Scoring Engine

1. **Replace Scoring System**
   ```bash
   # Backup current scoring engine
   mv backend/scoring_engine.py backend/scoring_engine_old.py
   
   # Use new MVP scoring engine
   cp backend/mvp_scoring_engine.py backend/scoring_engine.py
   ```

2. **Update Celery Tasks**
   ```bash
   # Restart Celery workers
   celery -A celery_app worker --loglevel=info
   
   # Start Celery beat for scheduled tasks
   celery -A celery_app beat --loglevel=info
   ```

3. **Initial Score Calculation**
   ```python
   # Run in Python shell
   from mvp_scoring_engine import daily_score_update
   daily_score_update.delay()
   ```

### Day 5: Security & Performance Monitoring

1. **Add Performance Middleware**
   Update `backend/server.py`:
   ```python
   from mvp_performance_monitor import performance_middleware, perf_router
   
   # Add middleware
   app.add_middleware(performance_middleware)
   
   # Add performance routes
   app.include_router(perf_router)
   ```

2. **Security Updates**
   - Remove legacy JWT code
   - Ensure all endpoints use Supabase auth
   - Add rate limiting:
   ```python
   from slowapi import Limiter
   from slowapi.util import get_remote_address
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   ```

## Phase 2: Feature Removal (Days 6-7)

### Remove Non-MVP Features

1. **Run Feature Removal Script**
   ```bash
   cd backend
   python remove_non_mvp_features.py
   ```

2. **Update Imports**
   Replace in affected files:
   ```python
   # Old
   from notification_service import notification_service
   
   # New
   from notification_service_mvp import notification_service
   ```

3. **Clean Frontend Components**
   Remove these files:
   ```bash
   cd frontend/src/components
   rm AICoach.jsx Achievements.jsx Journal.jsx Learning.jsx
   rm Insights.jsx KanbanBoard.jsx NotificationCenter.jsx
   rm ProjectTemplates.jsx RecurringTasks.jsx PomodoroTimer.jsx
   rm FileManager.jsx Feedback.jsx
   ```

## Phase 3: Frontend Optimization (Days 8-10)

### Day 8: Implement New Today View

1. **Replace Today Component**
   ```bash
   cd frontend/src/components
   mv Today.jsx Today_old.jsx
   cp TodayMVP.jsx Today.jsx
   ```

2. **Update API Service**
   Create `frontend/src/services/todayService.js`:
   ```javascript
   export const todayService = {
     getTodayTasks: async () => {
       const response = await api.get('/api/today/tasks');
       return response.data;
     },
     
     updateTask: async (taskId, data) => {
       const response = await api.patch(`/api/today/tasks/${taskId}`, data);
       return response.data;
     }
   };
   ```

### Day 9-10: Performance Optimization

1. **Code Splitting**
   Update `frontend/src/App.js`:
   ```javascript
   import { lazy, Suspense } from 'react';
   
   const Pillars = lazy(() => import('./components/Pillars'));
   const Areas = lazy(() => import('./components/Areas'));
   const Projects = lazy(() => import('./components/Projects'));
   const Tasks = lazy(() => import('./components/Tasks'));
   ```

2. **Optimize Queries**
   Update TanStack Query settings:
   ```javascript
   const queryClient = new QueryClient({
     defaultOptions: {
       queries: {
         staleTime: 5 * 60 * 1000, // 5 minutes
         cacheTime: 10 * 60 * 1000, // 10 minutes
         refetchOnWindowFocus: false,
       },
     },
   });
   ```

3. **Remove Unused Dependencies**
   ```bash
   cd frontend
   npm uninstall [unused-packages]
   npm audit fix
   ```

## Phase 4: Testing & Deployment (Days 11-14)

### Performance Testing

1. **API Load Testing**
   ```bash
   # Install artillery
   npm install -g artillery
   
   # Create test script
   artillery quick --count 100 --num 10 http://localhost:8000/api/today/tasks
   ```

2. **Monitor P95 Response Times**
   ```bash
   # Check performance endpoint
   curl http://localhost:8000/api/performance/summary
   ```

3. **Frontend Performance**
   - Use Chrome DevTools Lighthouse
   - Target: < 3s initial load
   - Target: > 90 performance score

### Deployment Steps

1. **Staging Deployment**
   ```bash
   # Build frontend
   cd frontend
   npm run build
   
   # Deploy backend
   cd ../backend
   # Update environment variables
   # Deploy to staging server
   ```

2. **Production Checklist**
   - [ ] All tests passing
   - [ ] P95 < 150ms verified
   - [ ] Database indexes verified
   - [ ] Backups completed
   - [ ] Rollback plan ready

3. **Go Live**
   - [ ] Deploy during low-traffic window
   - [ ] Monitor performance metrics
   - [ ] Check error logs
   - [ ] Verify core functionality

## Post-Deployment

### Monitoring

1. **Set Up Alerts**
   ```python
   # Add to performance monitor
   if p95_response_time > 0.15:
       send_alert("P95 exceeds 150ms")
   ```

2. **Track Success Metrics**
   - Onboarding completion rate
   - Daily active users
   - Task completion rate
   - User feedback

### Rollback Plan

If issues arise:
1. `git checkout main`
2. Restore from backup: `backend_backup_[timestamp]`
3. Redeploy previous version
4. Investigate issues on staging

## Common Issues & Solutions

### Issue: Slow Today View
**Solution**: Check if indexes are being used
```javascript
db.tasks.explain("executionStats").find({
  user_id: "xxx",
  completed: false
}).sort({current_score: -1})
```

### Issue: Score Not Updating
**Solution**: Check Celery workers
```bash
celery -A celery_app status
celery -A celery_app inspect active
```

### Issue: Auth Failures
**Solution**: Verify Supabase configuration
```bash
# Check environment variables
echo $SUPABASE_URL
echo $SUPABASE_ANON_KEY
```

## Success Criteria

- [ ] P95 API response time < 150ms
- [ ] Zero critical bugs in production
- [ ] 60%+ onboarding completion
- [ ] Positive user feedback on core concept

## Support

For questions during implementation:
- Slack: #mvp-refactor
- Wiki: Internal MVP docs
- Lead: [Engineering Lead Name]

Remember: The goal is ruthless simplification while maintaining the core value proposition of vertical alignment.