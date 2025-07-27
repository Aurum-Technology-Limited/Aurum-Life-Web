"""
Script to remove/disable non-MVP features from Aurum Life
This safely comments out or removes features not needed for MVP v1.1
"""

import os
import shutil
from datetime import datetime

# Create backup directory
backup_dir = f"backend_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
os.makedirs(backup_dir, exist_ok=True)

# Files to remove/archive
files_to_archive = [
    "ai_coach_service.py",
    "notification_service.py",  # Will create minimal version
    "email_service.py",  # Keep minimal for auth
]

# Features to disable in server.py
features_to_disable = [
    # AI Coach endpoints
    ("@api_router.post(\"/ai-coach/chat\")", "@api_router.post(\"/ai-coach/generate-goals\")"),
    
    # Achievement endpoints  
    ("@api_router.get(\"/achievements\")", "@api_router.post(\"/achievements/check\")"),
    
    # Journal endpoints
    ("@api_router.get(\"/journal\")", "@api_router.delete(\"/journal/{entry_id}\")"),
    
    # Learning/Course endpoints
    ("@api_router.get(\"/courses\")", "@api_router.post(\"/courses/{course_id}/complete-lesson\")"),
    
    # Insights endpoints
    ("@api_router.get(\"/insights/dashboard\")", "@api_router.get(\"/insights/analytics\")"),
    
    # Template endpoints (keep basic CRUD)
    ("@api_router.get(\"/project-templates\")", "@api_router.post(\"/projects/{project_id}/apply-template\")"),
    
    # Recurring task endpoints
    ("@api_router.get(\"/recurring-tasks\")", "@api_router.post(\"/recurring-tasks/{template_id}/skip-instance\")"),
    
    # File management
    ("@api_router.post(\"/files/upload\")", "@api_router.delete(\"/files/{file_id}\")"),
]

def archive_file(filename):
    """Archive a file to backup directory"""
    src = f"backend/{filename}"
    dst = f"{backup_dir}/{filename}"
    
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"Archived {filename}")
        
        # Create minimal stub
        with open(src, 'w') as f:
            f.write(f'"""\n{filename} - Disabled for MVP\nOriginal backed up to {backup_dir}\n"""\n\n')
            f.write("# This feature is disabled in MVP v1.1\n")
            f.write("# See MVP_REFACTORING_PLAN.md for details\n")
        
        print(f"Created stub for {filename}")

def create_minimal_notification_service():
    """Create minimal notification service for task reminders only"""
    content = '''"""
Minimal Notification Service for MVP v1.1
Only supports basic task reminders
"""

from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class MinimalNotificationService:
    """Stripped down notification service for MVP"""
    
    async def create_task_reminder(self, user_id: str, task_id: str, reminder_time: datetime):
        """Create a simple task reminder"""
        # In MVP, just log it - no actual notifications
        logger.info(f"Task reminder scheduled for user {user_id}, task {task_id} at {reminder_time}")
        return True
    
    async def cancel_task_reminder(self, user_id: str, task_id: str):
        """Cancel a task reminder"""
        logger.info(f"Task reminder cancelled for user {user_id}, task {task_id}")
        return True

# Global instance
notification_service = MinimalNotificationService()
'''
    
    with open('backend/notification_service_mvp.py', 'w') as f:
        f.write(content)
    
    print("Created minimal notification service")

def disable_features_in_server():
    """Comment out non-MVP endpoints in server.py"""
    
    # Read server.py
    with open('backend/server.py', 'r') as f:
        content = f.read()
    
    # Backup original
    with open(f'{backup_dir}/server.py', 'w') as f:
        f.write(content)
    
    # Create list of endpoints to disable
    disabled_endpoints = []
    
    # This is a simplified approach - in production you'd use AST parsing
    lines = content.split('\n')
    new_lines = []
    skip_until = None
    
    for i, line in enumerate(lines):
        if skip_until and i < skip_until:
            new_lines.append(f"# MVP_DISABLED: {line}")
            continue
            
        # Check if this line starts a feature to disable
        should_disable = False
        for feature_start, _ in features_to_disable:
            if feature_start in line:
                should_disable = True
                # Find the end of this function (simplified - looks for next @)
                for j in range(i+1, len(lines)):
                    if lines[j].strip().startswith('@') or lines[j].strip().startswith('def '):
                        skip_until = j
                        break
                break
        
        if should_disable:
            new_lines.append(f"# MVP_DISABLED: {line}")
            disabled_endpoints.append(line.strip())
        else:
            new_lines.append(line)
    
    # Write modified server.py
    with open('backend/server_mvp.py', 'w') as f:
        f.write('\n'.join(new_lines))
    
    print(f"Disabled {len(disabled_endpoints)} endpoints in server.py")
    return disabled_endpoints

def create_migration_report():
    """Create a report of all changes made"""
    report = f"""
# MVP v1.1 Migration Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Backup Location
All original files backed up to: {backup_dir}

## Files Archived
{chr(10).join('- ' + f for f in files_to_archive)}

## Features Disabled
The following endpoint groups were disabled in server.py:
- AI Coach endpoints
- Achievement/Badge endpoints  
- Journal endpoints
- Learning/Course endpoints
- Insights/Analytics endpoints
- Advanced Template endpoints
- Recurring Task endpoints
- File Management endpoints

## New MVP Files Created
- notification_service_mvp.py (minimal version)
- server_mvp.py (with disabled endpoints)

## Next Steps
1. Replace server.py with server_mvp.py
2. Replace notification_service.py with notification_service_mvp.py
3. Update imports in other files as needed
4. Run tests to ensure core functionality works

## Rollback Instructions
To rollback these changes:
1. Copy all files from {backup_dir} back to backend/
2. Restart the application
"""
    
    with open('MVP_MIGRATION_REPORT.md', 'w') as f:
        f.write(report)
    
    print("Created migration report: MVP_MIGRATION_REPORT.md")

if __name__ == "__main__":
    print("Starting MVP feature removal...")
    
    # Archive non-MVP files
    for file in files_to_archive:
        archive_file(file)
    
    # Create minimal versions
    create_minimal_notification_service()
    
    # Disable features in server.py
    disabled = disable_features_in_server()
    
    # Create report
    create_migration_report()
    
    print("\nMVP feature removal complete!")
    print(f"Check {backup_dir} for backups")
    print("Review MVP_MIGRATION_REPORT.md for details")