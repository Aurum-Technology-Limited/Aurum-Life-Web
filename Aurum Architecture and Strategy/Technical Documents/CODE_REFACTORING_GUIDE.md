# Aurum Life Code Refactoring Guide

**Last Updated:** January 2025  
**Purpose:** Guide for implementation agents to understand the codebase structure and recent improvements

---

## 🎯 Overview

This guide documents the comprehensive code refactoring and organization completed for Aurum Life. The codebase is now well-structured, documented, and ready for the HRM Phase 3 implementation.

---

## 📁 Repository Structure

### **Root Directory (Clean)**
The root directory has been cleaned of all test files. Key remaining files:
- `supabase_schema.sql` - Database schema
- `CHANGELOG.md` - Version history
- Configuration files (package.json, etc.)

### **Backend (`/backend`)**
```
backend/
├── server.py                    # Main FastAPI application
├── models.py                    # Pydantic data models
├── supabase_client.py          # Database connection manager
├── supabase_auth.py            # Authentication utilities
├── ai_coach_mvp_service.py     # AI prioritization service
├── services/                    # Business logic services
│   ├── optimized_services.py   # Performance-optimized CRUD
│   └── supabase_services.py    # Direct DB operations
└── requirements.txt            # Python dependencies
```

### **Frontend (`/frontend`)**
```
frontend/
├── src/
│   ├── App.js                  # Main application component
│   ├── components/             # React components
│   │   ├── Today.jsx          # AI-powered today view
│   │   ├── AICoach.jsx        # AI coaching interface
│   │   └── [PAPT components]  # Pillars, Areas, Projects, Tasks
│   ├── contexts/              # React context providers
│   ├── services/              # API integration
│   └── utils/                 # Helper functions
└── package.json               # Node dependencies
```

### **Tests (`/tests`)**
All 287 test files have been organized into:
```
tests/
├── backend/        # Backend-specific tests
├── integration/    # Integration tests
├── frontend/       # Frontend tests
├── performance/    # Performance benchmarks
├── migration/      # Database migration scripts
├── cleanup/        # Cleanup utilities
└── helpers/        # Test helper functions
```

### **Documentation (`/Aurum Architecture and Strategy`)**
```
Aurum Architecture and Strategy/
├── Business Documents/
│   ├── BUSINESS_MODEL_CANVAS.md
│   ├── GO_TO_MARKET_STRATEGY.md
│   └── AURUM_LIFE_BUSINESS_PLAN.md
├── Technical Documents/
│   ├── SYSTEM_ARCHITECTURE.md
│   ├── API_DOCUMENTATION_TEMPLATE.md
│   ├── ENGINEERING_HANDBOOK.md
│   └── aurum_life_hrm_phase3_prd.md
├── Legal & Compliance/
│   ├── TERMS_OF_SERVICE.md
│   ├── SECURITY_PRIVACY_POLICY.md
│   └── AI_ETHICS_GUIDELINES.md
├── Product & Design/
│   ├── EXECUTION_PRD_MVP_WEB_2025.md
│   ├── aurum_life_hrm_ui_epics_user_stories.md
│   ├── aurum_life_new_screens_specification.md
│   ├── aurum_life_wireframes_web.md
│   └── aurum_life_wireframes_mobile.md
└── Archive/
    └── [Old PRD versions]
```

---

## 🔧 Refactored Components

### **1. Backend Server (`server_refactored.py`)**

**Key Improvements:**
- Comprehensive documentation for every endpoint
- Clear separation of concerns
- Performance monitoring integration
- Detailed error handling
- Security best practices

**Important Endpoints:**
```python
# AI Coach - Today View (Most Important)
GET /api/today
- Returns AI-prioritized tasks
- Includes coaching messages
- Performance optimized

# PAPT Hierarchy Management
GET/POST/PUT/DELETE /api/pillars
GET/POST/PUT/DELETE /api/areas  
GET/POST/PUT/DELETE /api/projects
GET/POST/PUT/DELETE /api/tasks

# AI Features
POST /api/tasks/{task_id}/ai-coach
GET /api/insights
GET /api/alignment-score
```

### **2. AI Coach Service (`ai_coach_mvp_service_refactored.py`)**

**Key Features Documented:**
1. **Today Prioritization Algorithm**
   - Scoring factors explained
   - Performance optimizations
   - Gemini AI integration

2. **Contextual Why Statements**
   - Vertical alignment explanations
   - Motivation generation

3. **Project Decomposition**
   - Template-based task suggestions
   - Overcomes blank slate problem

4. **Daily Reflections**
   - Streak tracking
   - Progress monitoring

**Scoring Algorithm:**
```
Overdue: +100 points
Due Today: +80 points  
High Priority: +30 points
Important Project: +50 points
Important Area: +25 points
Dependencies Met: +60 points
```

### **3. Frontend App (`App_refactored.js`)**

**Architecture Highlights:**
- Lazy loading for performance
- Context-based state management
- Section-based navigation
- Comprehensive error boundaries
- React Query configuration

**Provider Hierarchy:**
```
ErrorBoundary
└── GoogleOAuthProvider
    └── QueryClientProvider
        └── AuthProvider
            └── DataProvider
                └── NotificationProvider
                    └── DndProvider
                        └── App Content
```

---

## 🚀 Implementation Guidelines

### **For Backend Development:**

1. **Adding New Endpoints:**
   - Follow RESTful conventions
   - Add to `api_router` in server.py
   - Include comprehensive docstrings
   - Implement proper error handling
   - Add performance monitoring

2. **Database Operations:**
   - Use optimized services when available
   - Batch queries for related data
   - Implement proper indexes
   - Follow the models.py schemas

3. **AI Integration:**
   - Gemini API key in environment
   - Graceful fallbacks if AI fails
   - Cache AI responses when appropriate
   - Monitor API usage

### **For Frontend Development:**

1. **Component Structure:**
   - Functional components with hooks
   - Proper TypeScript types (when added)
   - React Query for data fetching
   - Context for global state

2. **State Management:**
   - AuthContext for authentication
   - DataContext for shared data
   - Local state for component-specific
   - React Query for server state

3. **Performance:**
   - Lazy load heavy components
   - Memoize expensive computations
   - Use React.memo for pure components
   - Implement virtual scrolling for lists

### **Database Schema Updates:**

When implementing HRM Phase 3, add these tables:
```sql
-- Insights table for AI-generated insights
CREATE TABLE insights (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    type VARCHAR(50),
    content JSONB,
    created_at TIMESTAMP
);

-- HRM rules configuration
CREATE TABLE hrm_rules (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    condition JSONB,
    action JSONB,
    priority INTEGER
);

-- HRM user preferences
CREATE TABLE hrm_user_preferences (
    user_id UUID PRIMARY KEY,
    preferences JSONB,
    updated_at TIMESTAMP
);
```

---

## 📝 Code Style Guidelines

### **Python (Backend):**
```python
# Use type hints
async def get_task(task_id: str, user_id: str) -> Optional[Task]:
    """Get a task by ID, ensuring user ownership."""
    pass

# Comprehensive error handling
try:
    result = await risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise HTTPException(status_code=400, detail=str(e))
```

### **JavaScript/React (Frontend):**
```jsx
// Functional components with clear props
const TaskCard = ({ task, onComplete, isHighlighted = false }) => {
  // Hook usage at top
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  
  // Event handlers
  const handleComplete = useCallback(async () => {
    setIsLoading(true);
    try {
      await completeTask(task.id);
      onComplete(task.id);
    } catch (error) {
      console.error('Failed to complete task:', error);
    } finally {
      setIsLoading(false);
    }
  }, [task.id, onComplete]);
  
  // Clear render logic
  return (
    <div className={`task-card ${isHighlighted ? 'highlighted' : ''}`}>
      {/* Component content */}
    </div>
  );
};
```

---

## 🔄 Git Workflow

1. **Branch Naming:**
   - `feature/hrm-insights-dashboard`
   - `fix/ai-coach-performance`
   - `chore/update-dependencies`

2. **Commit Messages:**
   ```
   feat(hrm): add insights generation service
   fix(ai-coach): resolve timezone calculation bug
   docs: update API documentation for new endpoints
   ```

3. **Pull Request Template:**
   - Clear description of changes
   - Link to relevant issues
   - Test coverage confirmation
   - Performance impact assessment

---

## ⚡ Performance Considerations

1. **Backend Optimizations:**
   - Use `OptimizedPillarService` etc. for CRUD
   - Batch database queries
   - Implement caching where appropriate
   - Monitor with `perf_monitor`

2. **Frontend Optimizations:**
   - React Query caching (5 min stale time)
   - Lazy loading for code splitting
   - Memoization for expensive operations
   - Virtual scrolling for long lists

3. **Database Optimizations:**
   - Proper indexes on foreign keys
   - Composite indexes for common queries
   - JSONB indexes for JSON fields
   - Regular VACUUM operations

---

## 🐛 Common Issues & Solutions

### **Issue: Slow Today View**
**Solution:** Check if Gemini API is responding slowly. The view should still work without AI coaching.

### **Issue: Authentication Errors**
**Solution:** Verify Supabase JWT is valid and SUPABASE_JWT_SECRET is set correctly.

### **Issue: CORS Errors**
**Solution:** Check that frontend URL is in backend CORS allowed origins.

### **Issue: Task Dependencies Not Working**
**Solution:** Ensure `dependency_task_ids` is properly stored as array in database.

---

## 📚 Additional Resources

- **Main Execution PRD:** `/Aurum Architecture and Strategy/Product & Design/EXECUTION_PRD_MVP_WEB_2025.md`
- **API Documentation:** `/Aurum Architecture and Strategy/Technical Documents/API_DOCUMENTATION_TEMPLATE.md`
- **System Architecture:** `/Aurum Architecture and Strategy/Technical Documents/SYSTEM_ARCHITECTURE.md`
- **Engineering Handbook:** `/Aurum Architecture and Strategy/Technical Documents/ENGINEERING_HANDBOOK.md`

---

## ✅ Checklist for Implementation Agent

- [ ] Review all documents in Aurum Architecture and Strategy folder
- [ ] Understand the PAPT hierarchy (Pillar → Area → Project → Task)
- [ ] Set up environment variables (especially GEMINI_API_KEY)
- [ ] Review refactored code examples
- [ ] Understand AI scoring algorithm
- [ ] Check database schema matches code models
- [ ] Test existing endpoints before adding new features
- [ ] Follow established patterns for consistency

---

This codebase is now clean, well-organized, and ready for the exciting HRM Phase 3 implementation. The foundation is solid - build amazing things on top of it! 🚀