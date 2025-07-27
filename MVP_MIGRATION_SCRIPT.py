#!/usr/bin/env python3
"""
Aurum Life MVP v1.2 Migration Script
Performs complete migration to production-ready MVP
Handles file replacements, branch cleanup, and documentation updates
"""

import os
import shutil
import subprocess
import sys
from datetime import datetime
import json
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mvp_migration.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MVPMigration:
    def __init__(self):
        self.backup_dir = f"pre_mvp_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.errors = []
        self.warnings = []
        
    def run_migration(self):
        """Execute the complete migration process"""
        logger.info("Starting Aurum Life MVP v1.2 Migration")
        
        try:
            # Step 1: Create backup
            self.create_backup()
            
            # Step 2: Clean up branches
            self.cleanup_branches()
            
            # Step 3: Replace backend files
            self.replace_backend_files()
            
            # Step 4: Replace frontend files
            self.replace_frontend_files()
            
            # Step 5: Remove non-MVP files
            self.remove_non_mvp_files()
            
            # Step 6: Clean up test files
            self.cleanup_test_files()
            
            # Step 7: Update documentation
            self.update_documentation()
            
            # Step 8: Create new documentation
            self.create_new_documentation()
            
            # Step 9: Verify migration
            self.verify_migration()
            
            # Step 10: Generate report
            self.generate_migration_report()
            
            logger.info("✅ Migration completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            self.rollback()
            raise
    
    def create_backup(self):
        """Create full backup of current state"""
        logger.info("Creating backup...")
        
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
            
            # Backup critical directories
            dirs_to_backup = ['backend', 'frontend/src/components', 'tests']
            
            for dir_path in dirs_to_backup:
                if os.path.exists(dir_path):
                    dest = os.path.join(self.backup_dir, dir_path)
                    shutil.copytree(dir_path, dest)
                    logger.info(f"Backed up {dir_path}")
                    
            # Save current git state
            git_info = {
                'branch': subprocess.check_output(['git', 'branch', '--show-current']).decode().strip(),
                'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip(),
                'status': subprocess.check_output(['git', 'status', '--porcelain']).decode()
            }
            
            with open(os.path.join(self.backup_dir, 'git_state.json'), 'w') as f:
                json.dump(git_info, f, indent=2)
                
        except Exception as e:
            self.errors.append(f"Backup failed: {e}")
            raise
    
    def cleanup_branches(self):
        """Clean up unnecessary branches"""
        logger.info("Cleaning up branches...")
        
        try:
            # Get current branch
            current_branch = subprocess.check_output(
                ['git', 'branch', '--show-current']
            ).decode().strip()
            
            # List all branches
            branches = subprocess.check_output(
                ['git', 'branch', '-a']
            ).decode().strip().split('\n')
            
            # Branches to keep
            keep_branches = ['main', 'master', 'develop', 'staging', current_branch]
            
            # Delete merged branches
            for branch in branches:
                branch = branch.strip().replace('*', '').strip()
                if branch and branch not in keep_branches and not branch.startswith('remotes/'):
                    try:
                        # Check if branch is merged
                        subprocess.run(
                            ['git', 'branch', '-d', branch],
                            check=True,
                            capture_output=True
                        )
                        logger.info(f"Deleted merged branch: {branch}")
                    except subprocess.CalledProcessError:
                        self.warnings.append(f"Could not delete branch {branch} (unmerged changes)")
                        
        except Exception as e:
            self.warnings.append(f"Branch cleanup warning: {e}")
    
    def replace_backend_files(self):
        """Replace backend files with MVP versions"""
        logger.info("Replacing backend files...")
        
        replacements = [
            ('backend/server_secure.py', 'backend/server.py'),
            ('backend/supabase_auth_secure.py', 'backend/supabase_auth.py'),
            ('backend/models_validated.py', 'backend/models.py'),
            ('backend/mvp_scoring_engine.py', 'backend/scoring_engine.py'),
            ('backend/mvp_performance_monitor.py', 'backend/performance_monitor.py'),
            ('backend/celery_config.py', 'backend/celery_app.py'),
            ('backend/mvp_today_service.py', 'backend/today_service.py'),
        ]
        
        for src, dst in replacements:
            try:
                if os.path.exists(src):
                    # Backup original if exists
                    if os.path.exists(dst):
                        shutil.move(dst, f"{dst}.old")
                    
                    # Move new file
                    shutil.move(src, dst)
                    logger.info(f"Replaced {dst}")
                else:
                    self.warnings.append(f"Source file not found: {src}")
                    
            except Exception as e:
                self.errors.append(f"Failed to replace {dst}: {e}")
    
    def replace_frontend_files(self):
        """Replace frontend files with MVP versions"""
        logger.info("Replacing frontend files...")
        
        try:
            # Replace Today component
            today_mvp = 'frontend/src/components/TodayMVP.jsx'
            today_main = 'frontend/src/components/Today.jsx'
            
            if os.path.exists(today_mvp):
                if os.path.exists(today_main):
                    shutil.move(today_main, f"{today_main}.old")
                shutil.move(today_mvp, today_main)
                logger.info("Replaced Today component")
                
            # Create new component structure if TaskList was created
            if os.path.exists('frontend/src/components/tasks/TaskList.jsx'):
                logger.info("New component structure already in place")
                
        except Exception as e:
            self.errors.append(f"Failed to replace frontend files: {e}")
    
    def remove_non_mvp_files(self):
        """Remove files not needed for MVP"""
        logger.info("Removing non-MVP files...")
        
        # Backend files to remove
        backend_remove = [
            'backend/ai_coach_service.py',
            'backend/notification_service.py',
            'backend/email_service.py',
        ]
        
        # Frontend components to remove
        frontend_remove = [
            'frontend/src/components/AICoach.jsx',
            'frontend/src/components/Achievements.jsx',
            'frontend/src/components/Journal.jsx',
            'frontend/src/components/Learning.jsx',
            'frontend/src/components/Insights.jsx',
            'frontend/src/components/KanbanBoard.jsx',
            'frontend/src/components/NotificationCenter.jsx',
            'frontend/src/components/ProjectTemplates.jsx',
            'frontend/src/components/RecurringTasks.jsx',
            'frontend/src/components/PomodoroTimer.jsx',
            'frontend/src/components/FileManager.jsx',
            'frontend/src/components/Feedback.jsx',
        ]
        
        # Test files in root to remove
        root_test_patterns = [
            '*_test.py',
            'test_*.py',
            '*.png',
            'debug_*.py',
            'check_*.py',
        ]
        
        all_files = backend_remove + frontend_remove
        
        for file_path in all_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"Removed {file_path}")
            except Exception as e:
                self.warnings.append(f"Could not remove {file_path}: {e}")
        
        # Clean root directory
        import glob
        for pattern in root_test_patterns:
            for file_path in glob.glob(pattern):
                try:
                    if os.path.isfile(file_path):
                        dest = os.path.join(self.backup_dir, 'root_files', file_path)
                        os.makedirs(os.path.dirname(dest), exist_ok=True)
                        shutil.move(file_path, dest)
                        logger.info(f"Archived {file_path}")
                except Exception as e:
                    self.warnings.append(f"Could not archive {file_path}: {e}")
    
    def cleanup_test_files(self):
        """Run test cleanup script if it exists"""
        logger.info("Cleaning up test files...")
        
        try:
            if os.path.exists('cleanup_tests.py'):
                subprocess.run([sys.executable, 'cleanup_tests.py'], check=True)
                logger.info("Test cleanup completed")
            else:
                logger.warning("cleanup_tests.py not found, skipping test cleanup")
        except Exception as e:
            self.warnings.append(f"Test cleanup warning: {e}")
    
    def update_documentation(self):
        """Remove old documentation files"""
        logger.info("Updating documentation...")
        
        old_docs = [
            'DEPLOYMENT.md',
            'ENVIRONMENT_SETUP.md',
            'RESTORE_ENVIRONMENT.md',
        ]
        
        for doc in old_docs:
            if os.path.exists(doc):
                dest = os.path.join(self.backup_dir, 'old_docs', doc)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.move(doc, dest)
                logger.info(f"Archived old documentation: {doc}")
    
    def create_new_documentation(self):
        """Create new documentation for MVP"""
        logger.info("Creating new documentation...")
        
        # Create main README
        readme_content = """# Aurum Life MVP v1.2

A production-ready personal productivity platform built on the principle of vertical alignment: Pillar → Area → Project → Task.

## Technology Stack

- **Frontend**: React 19, TanStack Query, Tailwind CSS
- **Backend**: Python 3.x, FastAPI, Uvicorn
- **Database**: PostgreSQL (via Supabase)
- **Authentication**: Supabase Auth with RLS
- **Task Queue**: Celery with Redis
- **Infrastructure**: Docker/Kubernetes ready

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL (or Supabase account)
- Redis

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
uvicorn server:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env
# Edit .env with your configuration
npm start
```

### Running Tests
```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test
```

## Architecture

### Security Features
- Supabase Authentication (no legacy JWT)
- Row Level Security (RLS) for complete data isolation
- Input validation on all endpoints
- Environment-based configuration

### Performance
- Optimized PostgreSQL queries with proper indexing
- Target: <150ms P95 API response time
- Single-query patterns for hierarchy fetching
- Background task processing with Celery

### Core Features
- **Pillars**: Life categories (Health, Career, etc.)
- **Areas**: Focus areas within pillars
- **Projects**: Specific goals with deadlines
- **Tasks**: Actionable items with smart prioritization
- **Today View**: Optimized daily task management
- **Morning Intentions & Evening Reflections**: Manual journaling

## API Documentation

### Authentication
All API endpoints require authentication via Bearer token:
```
Authorization: Bearer <supabase_jwt_token>
```

### Core Endpoints
- `GET /api/today/tasks` - Get prioritized tasks for today
- `GET /api/hierarchy` - Get complete user hierarchy
- `POST /api/pillars` - Create a new pillar
- `POST /api/areas` - Create a new area
- `POST /api/projects` - Create a new project
- `POST /api/tasks` - Create a new task

## Deployment

### Environment Variables
Required environment variables:
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_ANON_KEY` - Supabase anonymous key
- `SUPABASE_SERVICE_KEY` - Supabase service key (production only)
- `SUPABASE_JWT_SECRET` - JWT secret for token verification
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - Application secret key (min 32 chars)
- `ENVIRONMENT` - development/staging/production

### Production Checklist
- [ ] All environment variables set
- [ ] RLS policies applied in Supabase
- [ ] Database indexes created
- [ ] Redis configured for Celery
- [ ] HTTPS enabled
- [ ] CORS origins configured
- [ ] Performance monitoring enabled

## Monitoring

Access performance metrics at `/api/performance/summary` (requires authentication).

## Support

For issues or questions, please create an issue in the repository.
"""
        
        with open('README.md', 'w') as f:
            f.write(readme_content)
        logger.info("Created new README.md")
        
        # Create API documentation
        api_docs = """# Aurum Life API Documentation

## Authentication

All endpoints require Supabase JWT authentication.

### Headers
```
Authorization: Bearer <token>
Content-Type: application/json
```

## Endpoints

### Pillars

#### Create Pillar
```
POST /api/pillars
{
  "name": "Health & Wellness",
  "description": "Physical and mental health",
  "icon": "💪",
  "color": "#4CAF50"
}
```

#### Get User Pillars
```
GET /api/pillars
```

#### Update Pillar
```
PATCH /api/pillars/{pillar_id}
{
  "name": "Updated Name"
}
```

#### Delete Pillar (Archive)
```
DELETE /api/pillars/{pillar_id}
```

### Areas

#### Create Area
```
POST /api/areas
{
  "pillar_id": "uuid",
  "name": "Exercise",
  "description": "Regular physical activity",
  "icon": "🏃",
  "color": "#2196F3"
}
```

### Projects

#### Create Project
```
POST /api/projects
{
  "area_id": "uuid",
  "name": "30-Day Challenge",
  "description": "Complete workout program",
  "deadline": "2025-12-31T00:00:00Z",
  "priority": "high",
  "status": "in_progress"
}
```

### Tasks

#### Create Task
```
POST /api/tasks
{
  "project_id": "uuid",
  "name": "Morning workout",
  "description": "20 min cardio",
  "priority": "high",
  "due_date": "2025-07-28T09:00:00Z",
  "estimated_duration": 20
}
```

#### Complete Task
```
PATCH /api/tasks/{task_id}
{
  "completed": true
}
```

### Today View

#### Get Today's Tasks
```
GET /api/today/tasks
```

Response:
```json
{
  "tasks": [
    {
      "id": "uuid",
      "name": "Morning workout",
      "priority": "high",
      "due_date": "2025-07-28T09:00:00Z",
      "current_score": 85.5,
      "project_name": "30-Day Challenge",
      "area_name": "Exercise",
      "pillar_name": "Health & Wellness"
    }
  ],
  "stats": {
    "total_today": 5,
    "completed_today": 2,
    "completion_rate": 40.0
  }
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "An internal error occurred"
}
```
"""
        
        with open('API_DOCUMENTATION.md', 'w') as f:
            f.write(api_docs)
        logger.info("Created API_DOCUMENTATION.md")
        
        # Create troubleshooting guide
        troubleshooting = """# Troubleshooting Guide

## Common Issues and Solutions

### Authentication Issues

#### "Could not validate credentials"
**Cause**: Invalid or expired token
**Solution**: 
1. Ensure token is included in Authorization header
2. Check token hasn't expired (1 hour lifetime)
3. Verify Supabase JWT secret is correct

#### "User account is deactivated"
**Cause**: User account has been disabled
**Solution**: Check user status in Supabase Auth dashboard

### Database Issues

#### "Failed to create pillar"
**Possible Causes**:
1. RLS policies not applied
2. User ID mismatch
3. Database connection issue

**Solutions**:
1. Run RLS migration: `supabase/migrations/20250727_rls_policies.sql`
2. Verify user authentication
3. Check DATABASE_URL environment variable

#### Slow API responses (>150ms)
**Causes**:
1. Missing database indexes
2. N+1 query patterns
3. Large data sets

**Solutions**:
1. Run index creation script
2. Use optimized query patterns
3. Implement pagination

### Celery/Task Queue Issues

#### Tasks not executing
**Causes**:
1. Celery worker not running
2. Redis connection failed
3. Task routing misconfigured

**Solutions**:
```bash
# Start Celery worker
celery -A celery_app worker --loglevel=info

# Start Celery beat (for scheduled tasks)
celery -A celery_app beat --loglevel=info

# Check Redis connection
redis-cli ping
```

### Frontend Issues

#### "Network Error" on API calls
**Causes**:
1. Backend not running
2. CORS misconfiguration
3. Wrong API URL

**Solutions**:
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check ALLOWED_ORIGINS in backend .env
3. Verify REACT_APP_API_URL in frontend .env

#### Components not rendering
**Causes**:
1. Missing dependencies
2. Import errors
3. State management issues

**Solutions**:
1. Run `npm install`
2. Check browser console for errors
3. Verify TanStack Query setup

## Error Codes Reference

### Backend Errors

| Code | Description | Action |
|------|-------------|--------|
| AUTH001 | Invalid token format | Check Authorization header |
| AUTH002 | Token expired | Refresh token |
| AUTH003 | User not found | Verify user exists |
| DB001 | Database connection failed | Check DATABASE_URL |
| DB002 | Query timeout | Check indexes, optimize query |
| VAL001 | Validation failed | Check request payload |
| RLS001 | Access denied by RLS | Verify ownership |

### Frontend Errors

| Code | Description | Action |
|------|-------------|--------|
| API001 | Network request failed | Check backend status |
| API002 | Timeout | Increase timeout, check backend |
| STATE001 | Invalid state update | Check React hooks usage |
| ROUTE001 | Route not found | Verify route configuration |

## Performance Debugging

### Checking API Performance
```bash
# Check performance endpoint
curl -H "Authorization: Bearer <token>" \\
  http://localhost:8000/api/performance/summary
```

### Database Query Analysis
```sql
-- Check slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE mean_exec_time > 150
ORDER BY mean_exec_time DESC;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan;
```

### Monitoring Celery Tasks
```bash
# Check active tasks
celery -A celery_app inspect active

# Check task queue length
celery -A celery_app inspect reserved

# View task failures
celery -A celery_app events
```

## Getting Help

1. Check logs: `backend/mvp_migration.log`
2. Enable debug mode (development only)
3. Check Supabase dashboard for auth/database issues
4. Review test cases in `tests/` directory
"""
        
        with open('TROUBLESHOOTING.md', 'w') as f:
            f.write(troubleshooting)
        logger.info("Created TROUBLESHOOTING.md")
        
        # Create test cases documentation
        test_cases = """# Test Cases for MVP v1.2

## Unit Tests

### Authentication Tests
```python
def test_valid_token_authentication():
    # Test successful authentication with valid Supabase token
    
def test_expired_token_rejection():
    # Test that expired tokens are rejected
    
def test_malformed_token_rejection():
    # Test that malformed tokens are rejected
```

### Validation Tests
```python
def test_pillar_name_required():
    # Test that pillar creation requires name
    
def test_sql_injection_prevention():
    # Test that SQL injection attempts are blocked
    
def test_xss_prevention():
    # Test that XSS attempts are sanitized
```

### Service Layer Tests
```python
def test_create_pillar_success():
    # Test successful pillar creation
    
def test_update_pillar_ownership():
    # Test users can only update their own pillars
    
def test_cascade_delete_prevention():
    # Test that deleting pillar doesn't delete children
```

## Integration Tests

### Hierarchy Tests
```python
async def test_complete_hierarchy_creation():
    # Test creating Pillar -> Area -> Project -> Task
    
async def test_hierarchy_statistics():
    # Test that statistics are calculated correctly
    
async def test_hierarchy_performance():
    # Test that hierarchy query completes in <150ms
```

### RLS Tests
```python
async def test_user_data_isolation():
    # Test User A cannot see User B's data
    
async def test_cross_user_update_prevention():
    # Test User A cannot update User B's data
    
async def test_cross_user_delete_prevention():
    # Test User A cannot delete User B's data
```

## End-to-End Tests

### Core User Journey
```python
async def test_registration_to_task_completion():
    # 1. Register user
    # 2. Create pillar
    # 3. Create area
    # 4. Create project  
    # 5. Create task
    # 6. View in Today
    # 7. Complete task
    # 8. Verify progress
```

### Performance Tests
```python
async def test_api_response_times():
    # Test all critical endpoints meet <150ms requirement
    
async def test_concurrent_users():
    # Test system handles 100 concurrent users
    
async def test_large_dataset_performance():
    # Test performance with 1000+ tasks
```

## Error Scenarios

### Database Errors
```python
def test_database_connection_failure():
    # Test graceful handling of database outage
    
def test_transaction_rollback():
    # Test that failed operations rollback properly
```

### Validation Errors
```python
def test_invalid_email_format():
    # Test email validation
    
def test_weak_password_rejection():
    # Test password strength requirements
    
def test_invalid_uuid_format():
    # Test UUID validation
```

### Edge Cases
```python
def test_empty_hierarchy():
    # Test system handles users with no data
    
def test_circular_dependencies():
    # Test prevention of circular task dependencies
    
def test_timezone_handling():
    # Test correct handling of different timezones
```

## Load Testing

### Locust Test Script
```python
from locust import HttpUser, task, between

class AurumLifeUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login and store token
        response = self.client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "Test123!@#"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def view_today(self):
        self.client.get("/api/today/tasks", headers=self.headers)
    
    @task(2)
    def view_hierarchy(self):
        self.client.get("/api/hierarchy", headers=self.headers)
    
    @task(1)
    def create_task(self):
        self.client.post("/api/tasks", headers=self.headers, json={
            "project_id": "test-project-id",
            "name": f"Load test task",
            "priority": "medium"
        })
```

## Security Tests

### OWASP Top 10
1. **Injection**: Test SQL injection prevention
2. **Broken Authentication**: Test token validation
3. **Sensitive Data Exposure**: Test HTTPS enforcement
4. **XML External Entities**: N/A (JSON only)
5. **Broken Access Control**: Test RLS policies
6. **Security Misconfiguration**: Test env validation
7. **XSS**: Test input sanitization
8. **Insecure Deserialization**: Test JSON validation
9. **Vulnerable Components**: Test dependency scanning
10. **Insufficient Logging**: Test audit trails

## Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test category
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run with coverage
pytest tests/ --cov=backend --cov-report=html

# Run security tests only
pytest tests/security/ -v

# Run performance tests
pytest tests/performance/ -v --benchmark-only
```
"""
        
        with open('TEST_CASES.md', 'w') as f:
            f.write(test_cases)
        logger.info("Created TEST_CASES.md")
    
    def verify_migration(self):
        """Verify migration was successful"""
        logger.info("Verifying migration...")
        
        required_files = [
            'backend/server.py',
            'backend/supabase_auth.py',
            'backend/models.py',
            'backend/scoring_engine.py',
            'backend/performance_monitor.py',
            'backend/celery_app.py',
            'backend/config.py',
            'backend/optimized_queries.py',
            'frontend/src/components/Today.jsx',
        ]
        
        removed_files = [
            'backend/ai_coach_service.py',
            'frontend/src/components/AICoach.jsx',
            'frontend/src/components/Achievements.jsx',
        ]
        
        # Check required files exist
        for file_path in required_files:
            if not os.path.exists(file_path):
                self.errors.append(f"Required file missing: {file_path}")
        
        # Check removed files don't exist
        for file_path in removed_files:
            if os.path.exists(file_path):
                self.warnings.append(f"File should be removed: {file_path}")
        
        # Check no test files in root
        import glob
        root_tests = glob.glob('*_test.py') + glob.glob('test_*.py')
        if root_tests:
            self.warnings.append(f"Test files still in root: {root_tests}")
    
    def generate_migration_report(self):
        """Generate final migration report"""
        logger.info("Generating migration report...")
        
        report = f"""# MVP v1.2 Migration Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Migration Summary
- Backup created: {self.backup_dir}
- Errors: {len(self.errors)}
- Warnings: {len(self.warnings)}

## Files Replaced
- backend/server.py (secure version)
- backend/supabase_auth.py (hardened auth)
- backend/models.py (validated models)
- backend/scoring_engine.py (simplified)
- backend/performance_monitor.py (monitoring)
- backend/celery_app.py (robust config)
- frontend/src/components/Today.jsx (optimized)

## Files Added
- backend/config.py (configuration management)
- backend/optimized_queries.py (query optimization)
- API_DOCUMENTATION.md
- TROUBLESHOOTING.md
- TEST_CASES.md

## Files Removed
- All AI Coach components
- Achievement system
- Journal functionality
- Learning modules
- Insights/Analytics
- File management
- Complex notifications
- Test files from root

## Errors
{chr(10).join(self.errors) if self.errors else 'None'}

## Warnings
{chr(10).join(self.warnings) if self.warnings else 'None'}

## Next Steps
1. Run database migrations in Supabase
2. Update environment variables
3. Run tests: pytest tests/
4. Deploy to staging
5. Performance testing
6. Deploy to production

## Rollback Instructions
If you need to rollback:
1. Restore from backup: {self.backup_dir}
2. Reset git: git reset --hard <commit>
3. Restore database from backup
"""
        
        with open('MIGRATION_REPORT.md', 'w') as f:
            f.write(report)
        logger.info("Created MIGRATION_REPORT.md")
        
        # Also log summary
        logger.info(f"Migration complete - Errors: {len(self.errors)}, Warnings: {len(self.warnings)}")
    
    def rollback(self):
        """Rollback migration in case of failure"""
        logger.error("Rolling back migration...")
        
        try:
            # Restore from backup
            if os.path.exists(self.backup_dir):
                for item in os.listdir(self.backup_dir):
                    src = os.path.join(self.backup_dir, item)
                    dst = item
                    
                    if os.path.isdir(src) and item not in ['old_docs', 'root_files']:
                        if os.path.exists(dst):
                            shutil.rmtree(dst)
                        shutil.copytree(src, dst)
                        logger.info(f"Restored {dst}")
                        
            logger.info("Rollback completed")
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            logger.error("Manual intervention required!")

def main():
    """Main entry point"""
    print("""
╔══════════════════════════════════════════════════════╗
║          Aurum Life MVP v1.2 Migration               ║
║                                                      ║
║  This script will:                                   ║
║  - Replace files with production versions            ║
║  - Remove non-MVP features                           ║
║  - Clean up branches and tests                      ║
║  - Update documentation                              ║
║                                                      ║
║  A backup will be created before any changes.        ║
╚══════════════════════════════════════════════════════╝
    """)
    
    response = input("Do you want to proceed? (yes/no): ")
    if response.lower() != 'yes':
        print("Migration cancelled.")
        return
    
    migration = MVPMigration()
    
    try:
        migration.run_migration()
        print("\n✅ Migration completed successfully!")
        print(f"📁 Backup saved to: {migration.backup_dir}")
        print("📄 See MIGRATION_REPORT.md for details")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("Check mvp_migration.log for details")
        sys.exit(1)

if __name__ == "__main__":
    main()