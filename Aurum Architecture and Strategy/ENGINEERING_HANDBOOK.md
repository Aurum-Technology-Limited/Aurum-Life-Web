# Aurum Life Engineering Handbook

**Last Updated:** January 2025  
**Document Type:** Engineering Process & Standards  
**Audience:** Current and Future Engineers

---

## 🎯 Engineering Philosophy

### Core Principles
1. **User Value First**: Every line of code should improve user experience
2. **Simplicity**: Prefer simple solutions that work over complex ones that might
3. **Quality**: Better to ship less features with high quality than more with bugs
4. **Learning**: Mistakes are learning opportunities, not failures
5. **Collaboration**: Code reviews are conversations, not critiques

### Technical Values
- **Performance**: Every millisecond counts
- **Security**: Privacy and security by design
- **Accessibility**: Build for everyone
- **Maintainability**: Write code for the next developer
- **Innovation**: Experiment safely with feature flags

---

## 🏗️ Development Process

### 1. **Development Workflow**

```mermaid
Feature Request → Design Review → Technical Spec → Implementation → Code Review → Testing → Deployment
```

#### Branch Strategy (Git Flow)
```
main
  ├── develop
  │   ├── feature/add-hrm-insights
  │   ├── feature/improve-task-ui
  │   └── feature/api-v2
  ├── release/v1.2.0
  └── hotfix/critical-auth-bug
```

#### Branch Naming Convention
- `feature/` - New features
- `bugfix/` - Non-critical bug fixes  
- `hotfix/` - Critical production fixes
- `chore/` - Maintenance tasks
- `docs/` - Documentation only

#### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Example:**
```
feat(hrm): add confidence scoring to task analysis

- Implement confidence calculation based on data completeness
- Add visual indicators for confidence levels
- Update API to return confidence scores

Closes #123
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (formatting, semicolons)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding tests
- `chore`: Maintenance tasks

### 2. **Code Review Process**

#### PR Requirements
- [ ] Clear description of changes
- [ ] Link to relevant issue/ticket
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No console.logs or debug code
- [ ] Performance impact considered

#### Review Checklist
1. **Functionality**: Does it work as intended?
2. **Code Quality**: Is it readable and maintainable?
3. **Performance**: Any potential bottlenecks?
4. **Security**: Any vulnerabilities introduced?
5. **Tests**: Adequate test coverage?
6. **Documentation**: Is it clear how to use?

#### Review Etiquette
- Start with positive feedback
- Suggest, don't demand
- Explain the "why" behind suggestions
- Use "we" instead of "you"
- Approve with comments if minor issues

---

## 💻 Coding Standards

### 1. **TypeScript/JavaScript (Frontend)**

#### Style Guide
```typescript
// ✅ Good: Clear, self-documenting
interface TaskPriority {
  score: number;
  confidence: number;
  reasoning: string;
}

async function calculateTaskPriority(
  task: Task,
  context: UserContext
): Promise<TaskPriority> {
  // Implementation
}

// ❌ Bad: Unclear naming, any types
async function calc(t: any, c: any): Promise<any> {
  // Implementation
}
```

#### React Best Practices
```jsx
// ✅ Good: Functional component with proper types
interface TaskCardProps {
  task: Task;
  onComplete: (taskId: string) => void;
  className?: string;
}

const TaskCard: React.FC<TaskCardProps> = ({ 
  task, 
  onComplete, 
  className = '' 
}) => {
  const handleComplete = useCallback(() => {
    onComplete(task.id);
  }, [task.id, onComplete]);

  return (
    <div className={`task-card ${className}`}>
      {/* Component content */}
    </div>
  );
};

// ❌ Bad: Class component, no types, inline functions
class TaskCard extends React.Component {
  render() {
    return (
      <div onClick={() => this.props.onComplete(this.props.task.id)}>
        {/* Component content */}
      </div>
    );
  }
}
```

#### State Management
```typescript
// ✅ Good: Using React Query for server state
const { data: tasks, isLoading, error } = useQuery({
  queryKey: ['tasks', projectId],
  queryFn: () => fetchTasks(projectId),
  staleTime: 5 * 60 * 1000, // 5 minutes
});

// ✅ Good: Using context for client state
const ThemeContext = createContext<ThemeContextType | null>(null);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};
```

### 2. **Python (Backend)**

#### Style Guide (PEP 8 + Type Hints)
```python
# ✅ Good: Clear types, docstrings, error handling
from typing import List, Optional, Dict, Any
from datetime import datetime
from models import Task, User, HRMInsight

async def analyze_task_priority(
    task: Task,
    user: User,
    depth: str = "balanced"
) -> HRMInsight:
    """
    Analyze task priority using Hierarchical Reasoning Model.
    
    Args:
        task: Task to analyze
        user: User context for personalization
        depth: Analysis depth - minimal, balanced, or detailed
        
    Returns:
        HRMInsight containing priority analysis
        
    Raises:
        ValueError: If depth is invalid
        HRMException: If analysis fails
    """
    if depth not in ["minimal", "balanced", "detailed"]:
        raise ValueError(f"Invalid depth: {depth}")
        
    try:
        # Implementation
        pass
    except Exception as e:
        logger.error(f"HRM analysis failed for task {task.id}: {e}")
        raise HRMException("Analysis failed") from e

# ❌ Bad: No types, poor naming, no error handling
def analyze(t, u, d="balanced"):
    # Implementation
    pass
```

#### FastAPI Best Practices
```python
# ✅ Good: Proper dependency injection, error handling
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    project_id: Optional[str] = None,
    completed: Optional[bool] = None,
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[TaskResponse]:
    """Get tasks with optional filtering."""
    try:
        tasks = await TaskService.get_user_tasks(
            user_id=current_user.id,
            project_id=project_id,
            completed=completed,
            limit=limit,
            db=db
        )
        return tasks
    except Exception as e:
        logger.error(f"Failed to fetch tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch tasks"
        )
```

### 3. **SQL/Database**

#### Query Guidelines
```sql
-- ✅ Good: Indexed, limited, explicit columns
SELECT 
    t.id,
    t.name,
    t.due_date,
    p.name as project_name,
    a.name as area_name
FROM tasks t
INNER JOIN projects p ON t.project_id = p.id
INNER JOIN areas a ON p.area_id = a.id
WHERE 
    t.user_id = $1
    AND t.completed = false
    AND t.due_date <= NOW() + INTERVAL '7 days'
ORDER BY t.due_date ASC
LIMIT 100;

-- ❌ Bad: SELECT *, no indexes, no limits
SELECT * 
FROM tasks 
WHERE user_id = $1 
ORDER BY created_at;
```

#### Migration Best Practices
```sql
-- ✅ Good: Transactional, reversible, commented
BEGIN;

-- Add HRM fields to tasks table
-- Purpose: Support AI-powered prioritization
ALTER TABLE tasks 
ADD COLUMN IF NOT EXISTS hrm_priority_score DECIMAL(5,2),
ADD COLUMN IF NOT EXISTS hrm_reasoning_summary TEXT;

-- Add index for performance
CREATE INDEX IF NOT EXISTS idx_tasks_hrm_priority 
ON tasks(user_id, completed, hrm_priority_score DESC) 
WHERE completed = false;

-- Add comment for documentation
COMMENT ON COLUMN tasks.hrm_priority_score IS 
'AI-calculated priority score (0-100) from Hierarchical Reasoning Model';

COMMIT;

-- Rollback script
-- ALTER TABLE tasks 
-- DROP COLUMN IF EXISTS hrm_priority_score,
-- DROP COLUMN IF EXISTS hrm_reasoning_summary;
-- DROP INDEX IF EXISTS idx_tasks_hrm_priority;
```

---

## 🧪 Testing Standards

### 1. **Test Types & Coverage**

#### Coverage Requirements
- Unit Tests: 80% minimum
- Integration Tests: Critical paths
- E2E Tests: User journeys
- Performance Tests: API endpoints

#### Test Structure
```typescript
// ✅ Good: Descriptive, isolated, comprehensive
describe('TaskPriorityService', () => {
  let service: TaskPriorityService;
  let mockHRMClient: jest.Mocked<HRMClient>;

  beforeEach(() => {
    mockHRMClient = createMockHRMClient();
    service = new TaskPriorityService(mockHRMClient);
  });

  describe('calculatePriority', () => {
    it('should return high priority for overdue tasks', async () => {
      // Arrange
      const overdueTask = createTask({
        dueDate: subDays(new Date(), 1),
        status: 'in_progress'
      });

      // Act
      const result = await service.calculatePriority(overdueTask);

      // Assert
      expect(result.score).toBeGreaterThan(80);
      expect(result.reasoning).toContain('overdue');
    });

    it('should handle HRM service errors gracefully', async () => {
      // Arrange
      mockHRMClient.analyze.mockRejectedValue(new Error('Service unavailable'));

      // Act & Assert
      await expect(service.calculatePriority(createTask()))
        .resolves.toMatchObject({
          score: 50, // Fallback score
          confidence: 0.5,
          reasoning: 'Using fallback calculation'
        });
    });
  });
});
```

### 2. **Frontend Testing**

```jsx
// ✅ Good: Testing user interactions and edge cases
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

describe('TaskCard', () => {
  it('should show HRM insights when available', async () => {
    const task = createTask({
      hrmAnalysis: {
        priority: 85,
        reasoning: 'Critical for project deadline'
      }
    });

    render(<TaskCard task={task} />);

    // Check insight is displayed
    expect(screen.getByText('Priority: 85')).toBeInTheDocument();
    expect(screen.getByText(/Critical for project deadline/)).toBeInTheDocument();
  });

  it('should handle loading state gracefully', () => {
    render(<TaskCard task={createTask()} loading />);
    
    expect(screen.getByTestId('skeleton-loader')).toBeInTheDocument();
    expect(screen.queryByText('Priority:')).not.toBeInTheDocument();
  });
});
```

### 3. **Backend Testing**

```python
# ✅ Good: Async test with proper fixtures
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_get_task_priorities(
    async_client: AsyncClient,
    async_session: AsyncSession,
    test_user: User
):
    # Arrange
    tasks = await create_test_tasks(async_session, test_user, count=5)
    
    # Act
    response = await async_client.get(
        "/api/today",
        headers={"Authorization": f"Bearer {test_user.token}"}
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data["tasks"]) == 5
    assert all(task["hrm_priority_score"] is not None for task in data["tasks"])
    assert data["hrm_enabled"] is True
```

---

## 🚀 Deployment Process

### 1. **CI/CD Pipeline**

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          npm test -- --coverage
          python -m pytest --cov=backend

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Build Docker images
        run: |
          docker build -t aurumlife/frontend:${{ github.sha }} ./frontend
          docker build -t aurumlife/backend:${{ github.sha }} ./backend

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/frontend frontend=aurumlife/frontend:${{ github.sha }}
          kubectl set image deployment/backend backend=aurumlife/backend:${{ github.sha }}
          kubectl rollout status deployment/frontend
          kubectl rollout status deployment/backend
```

### 2. **Deployment Checklist**

#### Pre-Deployment
- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Database migrations tested
- [ ] Performance impact assessed
- [ ] Feature flags configured
- [ ] Rollback plan documented

#### Deployment Steps
1. **Announce in #deployments Slack**
2. **Run database migrations**
3. **Deploy backend services**
4. **Deploy frontend**
5. **Verify health checks**
6. **Run smoke tests**
7. **Monitor error rates**

#### Post-Deployment
- [ ] Verify key metrics stable
- [ ] Check error tracking (Sentry)
- [ ] Test critical user paths
- [ ] Update status page
- [ ] Document any issues

### 3. **Rollback Procedure**

```bash
# Quick rollback to previous version
kubectl rollout undo deployment/frontend
kubectl rollout undo deployment/backend

# Rollback to specific version
kubectl rollout undo deployment/frontend --to-revision=3
kubectl rollout undo deployment/backend --to-revision=3

# Verify rollback
kubectl rollout status deployment/frontend
kubectl rollout status deployment/backend
```

---

## 📊 Monitoring & Debugging

### 1. **Logging Standards**

```python
# ✅ Good: Structured logging with context
logger.info(
    "Task analysis completed",
    extra={
        "user_id": user.id,
        "task_id": task.id,
        "duration_ms": duration,
        "confidence_score": result.confidence,
        "cache_hit": cache_hit
    }
)

# ❌ Bad: Unstructured, missing context
print(f"Done analyzing task")
```

### 2. **Error Handling**

```typescript
// ✅ Good: Graceful degradation with monitoring
try {
  const insights = await hrmService.analyzeTask(taskId);
  return { success: true, insights };
} catch (error) {
  // Log to monitoring service
  Sentry.captureException(error, {
    tags: {
      feature: 'hrm_analysis',
      taskId
    }
  });
  
  // Fallback to basic analysis
  const fallbackInsights = calculateBasicPriority(task);
  return { 
    success: true, 
    insights: fallbackInsights,
    degraded: true 
  };
}
```

### 3. **Performance Monitoring**

```python
# ✅ Good: Track performance metrics
from functools import wraps
import time

def track_performance(metric_name: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                # Send to monitoring
                metrics.histogram(
                    f"{metric_name}.duration",
                    duration,
                    tags={"status": "success"}
                )
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                metrics.histogram(
                    f"{metric_name}.duration",
                    duration,
                    tags={"status": "error", "error_type": type(e).__name__}
                )
                raise
        return wrapper
    return decorator

@track_performance("hrm.task_analysis")
async def analyze_task(task_id: str) -> HRMInsight:
    # Implementation
    pass
```

---

## 🔒 Security Best Practices

### 1. **Input Validation**

```python
# ✅ Good: Comprehensive validation
from pydantic import BaseModel, validator, constr

class TaskCreate(BaseModel):
    name: constr(min_length=1, max_length=255, strip_whitespace=True)
    description: Optional[constr(max_length=5000)]
    due_date: Optional[datetime]
    project_id: UUID
    
    @validator('due_date')
    def due_date_not_in_past(cls, v):
        if v and v < datetime.now():
            raise ValueError('Due date cannot be in the past')
        return v
    
    @validator('name')
    def sanitize_name(cls, v):
        # Remove any potential XSS attempts
        return bleach.clean(v, tags=[], strip=True)
```

### 2. **Authentication & Authorization**

```python
# ✅ Good: Proper permission checking
async def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Task:
    task = await db.get(Task, task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Verify user owns the task
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return task
```

### 3. **Sensitive Data Handling**

```typescript
// ✅ Good: Never log sensitive data
const sanitizedUser = {
  id: user.id,
  email: user.email.replace(/(.{2})(.*)(@.*)/, '$1***$3'),
  name: user.name
};

logger.info('User login successful', { user: sanitizedUser });

// ❌ Bad: Logging sensitive data
logger.info('User login', { user, password: req.body.password });
```

---

## 🎓 Learning Resources

### Internal Resources
- **Onboarding Guide**: `/docs/onboarding.md`
- **Architecture Decisions**: `/docs/adr/`
- **API Documentation**: `/docs/api/`
- **Troubleshooting Guide**: `/docs/troubleshooting.md`

### Recommended Learning
- **TypeScript**: TypeScript Deep Dive
- **React**: React Beta Docs
- **Python**: Effective Python by Brett Slatkin
- **System Design**: Designing Data-Intensive Applications
- **AI/ML**: Fast.ai Practical Deep Learning

### Team Practices
- **Pair Programming**: Every Friday afternoon
- **Tech Talks**: Bi-weekly presentations
- **Book Club**: Monthly technical book
- **Conference Budget**: $1,500/year per engineer

---

## 🤝 Team Rituals

### Daily
- **Standup**: 10:00 AM (15 min max)
- **PR Reviews**: Before lunch and EOD

### Weekly
- **Planning**: Monday 2:00 PM
- **Retrospective**: Friday 4:00 PM
- **Tech Debt Friday**: 20% time for improvements

### Monthly
- **All Hands**: First Tuesday
- **Hackathon**: Last Friday
- **1-on-1s**: Scheduled individually

---

This handbook is a living document. Every team member is encouraged to contribute improvements through pull requests.