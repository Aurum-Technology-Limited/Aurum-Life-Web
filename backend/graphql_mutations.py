"""
GraphQL Mutations
Handle create, update, delete operations
"""

import strawberry
from typing import Optional
from datetime import datetime
import logging

from graphql_schema import (
    Task, Project, JournalEntry, Area, Pillar,
    CreateTaskInput, UpdateTaskInput, CreateProjectInput, UpdateProjectInput,
    CreateJournalEntryInput, UpdateJournalEntryInput, CreateAreaInput, UpdateAreaInput,
    CreatePillarInput, UpdatePillarInput, TaskMutationResponse, ProjectMutationResponse,
    JournalMutationResponse, AreaMutationResponse, PillarMutationResponse, DeleteResponse
)
from supabase_client import supabase_manager
from cache_service import cache_service
from sentiment_analysis import analyze_journal_sentiment

logger = logging.getLogger(__name__)

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_task(self, info, input: CreateTaskInput) -> TaskMutationResponse:
        """Create a new task"""
        user = info.context["user"]
        
        try:
            # Prepare task data
            task_data = {
                'user_id': str(user.id),
                'project_id': input.project_id,
                'name': input.name,
                'description': input.description,
                'priority': input.priority.value,
                'due_date': input.due_date.isoformat() if input.due_date else None,
                'estimated_duration': input.estimated_duration,
                'status': 'todo',
                'completed': False
            }
            
            # Create task
            response = await supabase_manager.client.table('tasks')\
                .insert(task_data)\
                .execute()
            
            if response.data:
                task = Task(**response.data[0])
                
                # Invalidate cache
                await cache_service.delete(f"tasks:{user.id}")
                
                return TaskMutationResponse(
                    success=True,
                    message="Task created successfully",
                    task=task
                )
            
            return TaskMutationResponse(
                success=False,
                message="Failed to create task"
            )
            
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return TaskMutationResponse(
                success=False,
                message=f"Error: {str(e)}"
            )
    
    @strawberry.mutation
    async def update_task(self, info, input: UpdateTaskInput) -> TaskMutationResponse:
        """Update an existing task"""
        user = info.context["user"]
        
        try:
            # Build update data
            update_data = {}
            if input.name is not None:
                update_data['name'] = input.name
            if input.description is not None:
                update_data['description'] = input.description
            if input.status is not None:
                update_data['status'] = input.status.value
            if input.priority is not None:
                update_data['priority'] = input.priority.value
            if input.due_date is not None:
                update_data['due_date'] = input.due_date.isoformat()
            if input.completed is not None:
                update_data['completed'] = input.completed
                if input.completed:
                    update_data['completed_at'] = datetime.utcnow().isoformat()
            
            update_data['updated_at'] = datetime.utcnow().isoformat()
            
            # Update task
            response = await supabase_manager.client.table('tasks')\
                .update(update_data)\
                .eq('id', input.id)\
                .eq('user_id', str(user.id))\
                .execute()
            
            if response.data:
                task = Task(**response.data[0])
                
                # Invalidate cache
                await cache_service.delete(f"tasks:{user.id}")
                
                # Update alignment score if task completed
                if input.completed:
                    await self._update_alignment_score(user.id, input.id)
                
                return TaskMutationResponse(
                    success=True,
                    message="Task updated successfully",
                    task=task
                )
            
            return TaskMutationResponse(
                success=False,
                message="Task not found or unauthorized"
            )
            
        except Exception as e:
            logger.error(f"Error updating task: {e}")
            return TaskMutationResponse(
                success=False,
                message=f"Error: {str(e)}"
            )
    
    @strawberry.mutation
    async def delete_task(self, info, id: strawberry.ID) -> TaskMutationResponse:
        """Delete a task"""
        user = info.context["user"]
        
        try:
            response = await supabase_manager.client.table('tasks')\
                .delete()\
                .eq('id', id)\
                .eq('user_id', str(user.id))\
                .execute()
            
            if response.data:
                # Invalidate cache
                await cache_service.delete(f"tasks:{user.id}")
                
                return TaskMutationResponse(
                    success=True,
                    message="Task deleted successfully"
                )
            
            return TaskMutationResponse(
                success=False,
                message="Task not found or unauthorized"
            )
            
        except Exception as e:
            logger.error(f"Error deleting task: {e}")
            return TaskMutationResponse(
                success=False,
                message=f"Error: {str(e)}"
            )
    
    @strawberry.mutation
    async def create_project(self, info, input: CreateProjectInput) -> ProjectMutationResponse:
        """Create a new project"""
        user = info.context["user"]
        
        try:
            # Prepare project data
            project_data = {
                'user_id': str(user.id),
                'area_id': input.area_id,
                'name': input.name,
                'description': input.description,
                'icon': input.icon,
                'deadline': input.deadline.isoformat() if input.deadline else None,
                'priority': input.priority.value,
                'importance': input.importance,
                'status': 'Not Started',
                'completion_percentage': 0.0,
                'archived': False
            }
            
            # Create project
            response = await supabase_manager.client.table('projects')\
                .insert(project_data)\
                .execute()
            
            if response.data:
                project = Project(**response.data[0])
                
                # Invalidate cache
                await cache_service.delete(f"projects:{user.id}")
                
                return ProjectMutationResponse(
                    success=True,
                    message="Project created successfully",
                    project=project
                )
            
            return ProjectMutationResponse(
                success=False,
                message="Failed to create project"
            )
            
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return ProjectMutationResponse(
                success=False,
                message=f"Error: {str(e)}"
            )
    
    @strawberry.mutation
    async def update_project(self, info, input: UpdateProjectInput) -> ProjectMutationResponse:
        """Update an existing project"""
        user = info.context["user"]
        
        try:
            # Build update data
            update_data = {}
            if input.name is not None:
                update_data['name'] = input.name
            if input.description is not None:
                update_data['description'] = input.description
            if input.status is not None:
                update_data['status'] = input.status.value
            if input.priority is not None:
                update_data['priority'] = input.priority.value
            if input.deadline is not None:
                update_data['deadline'] = input.deadline.isoformat()
            if input.completion_percentage is not None:
                update_data['completion_percentage'] = input.completion_percentage
            
            update_data['updated_at'] = datetime.utcnow().isoformat()
            
            # Update project
            response = await supabase_manager.client.table('projects')\
                .update(update_data)\
                .eq('id', input.id)\
                .eq('user_id', str(user.id))\
                .execute()
            
            if response.data:
                project = Project(**response.data[0])
                
                # Invalidate cache
                await cache_service.delete(f"projects:{user.id}")
                
                return ProjectMutationResponse(
                    success=True,
                    message="Project updated successfully",
                    project=project
                )
            
            return ProjectMutationResponse(
                success=False,
                message="Project not found or unauthorized"
            )
            
        except Exception as e:
            logger.error(f"Error updating project: {e}")
            return ProjectMutationResponse(
                success=False,
                message=f"Error: {str(e)}"
            )
    
    @strawberry.mutation
    async def create_journal_entry(self, info, input: CreateJournalEntryInput) -> JournalMutationResponse:
        """Create a new journal entry"""
        user = info.context["user"]
        
        try:
            # Prepare entry data
            entry_data = {
                'user_id': str(user.id),
                'title': input.title,
                'content': input.content,
                'mood': input.mood,
                'energy_level': input.energy_level,
                'tags': input.tags,
                'word_count': len(input.content.split()),
                'deleted': False
            }
            
            # Create entry
            response = await supabase_manager.client.table('journal_entries')\
                .insert(entry_data)\
                .execute()
            
            if response.data:
                entry = JournalEntry(**response.data[0])
                
                # Analyze sentiment asynchronously
                asyncio.create_task(
                    analyze_journal_sentiment(entry.id, entry.content)
                )
                
                # Invalidate cache
                await cache_service.delete(f"journal:{user.id}")
                
                return JournalMutationResponse(
                    success=True,
                    message="Journal entry created successfully",
                    entry=entry
                )
            
            return JournalMutationResponse(
                success=False,
                message="Failed to create journal entry"
            )
            
        except Exception as e:
            logger.error(f"Error creating journal entry: {e}")
            return JournalMutationResponse(
                success=False,
                message=f"Error: {str(e)}"
            )
    
    @strawberry.mutation
    async def toggle_task_completion(self, info, id: strawberry.ID) -> TaskMutationResponse:
        """Quick toggle task completion status"""
        user = info.context["user"]
        
        try:
            # Get current task
            get_response = await supabase_manager.client.table('tasks')\
                .select('completed')\
                .eq('id', id)\
                .eq('user_id', str(user.id))\
                .single()\
                .execute()
            
            if not get_response.data:
                return TaskMutationResponse(
                    success=False,
                    message="Task not found"
                )
            
            # Toggle completion
            new_completed = not get_response.data['completed']
            update_data = {
                'completed': new_completed,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            if new_completed:
                update_data['completed_at'] = datetime.utcnow().isoformat()
                update_data['status'] = 'completed'
            else:
                update_data['completed_at'] = None
                update_data['status'] = 'todo'
            
            # Update task
            response = await supabase_manager.client.table('tasks')\
                .update(update_data)\
                .eq('id', id)\
                .eq('user_id', str(user.id))\
                .execute()
            
            if response.data:
                task = Task(**response.data[0])
                
                # Invalidate cache
                await cache_service.delete(f"tasks:{user.id}")
                
                # Update alignment score if completed
                if new_completed:
                    await self._update_alignment_score(user.id, id)
                
                return TaskMutationResponse(
                    success=True,
                    message=f"Task {'completed' if new_completed else 'reopened'} successfully",
                    task=task
                )
            
            return TaskMutationResponse(
                success=False,
                message="Failed to update task"
            )
            
        except Exception as e:
            logger.error(f"Error toggling task completion: {e}")
            return TaskMutationResponse(
                success=False,
                message=f"Error: {str(e)}"
            )
    
    async def _update_alignment_score(self, user_id: str, task_id: str):
        """Update alignment score when task is completed"""
        try:
            # Get task details
            task_response = await supabase_manager.client.table('tasks')\
                .select('*, project:projects(*, area:areas(*))')\
                .eq('id', task_id)\
                .single()\
                .execute()
            
            if task_response.data:
                task = task_response.data
                project = task.get('project', {})
                area = project.get('area', {})
                
                # Calculate points based on priority and importance
                base_points = 10
                priority_multiplier = {'high': 3, 'medium': 2, 'low': 1}.get(task.get('priority', 'medium'), 2)
                importance_multiplier = area.get('importance', 3) / 3
                
                points = int(base_points * priority_multiplier * importance_multiplier)
                
                # Create alignment score entry
                score_data = {
                    'user_id': user_id,
                    'task_id': task_id,
                    'points_earned': points,
                    'task_priority': task.get('priority'),
                    'project_priority': project.get('priority'),
                    'area_importance': area.get('importance')
                }
                
                await supabase_manager.client.table('alignment_scores')\
                    .insert(score_data)\
                    .execute()
                
                logger.info(f"Alignment score updated for task {task_id}: {points} points")
                
        except Exception as e:
            logger.error(f"Error updating alignment score: {e}")
    
    # Area Mutations
    @strawberry.mutation
    async def create_area(self, info, area: CreateAreaInput) -> AreaMutationResponse:
        """Create a new area"""
        user = info.context["user"]
        
        try:
            area_data = {
                'user_id': str(user.id),
                'name': area.name,
                'description': area.description or '',
                'icon': area.icon or '🎯',
                'color': area.color or '#F4B400',
                'importance': area.importance or 3,
                'pillar_id': area.pillar_id if area.pillar_id else None
            }
            
            response = await supabase_manager.client.table('areas')\
                .insert(area_data)\
                .execute()
            
            if response.data:
                created_area = Area(**response.data[0])
                return AreaMutationResponse(
                    success=True,
                    message="Area created successfully",
                    area=created_area
                )
            
            return AreaMutationResponse(
                success=False,
                message="Failed to create area"
            )
            
        except Exception as e:
            logger.error(f"Error creating area: {e}")
            return AreaMutationResponse(
                success=False,
                message=str(e)
            )
    
    @strawberry.mutation
    async def update_area(self, info, id: strawberry.ID, area: UpdateAreaInput) -> AreaMutationResponse:
        """Update an area"""
        user = info.context["user"]
        
        try:
            update_data = {}
            if area.name is not None:
                update_data['name'] = area.name
            if area.description is not None:
                update_data['description'] = area.description
            if area.icon is not None:
                update_data['icon'] = area.icon
            if area.color is not None:
                update_data['color'] = area.color
            if area.importance is not None:
                update_data['importance'] = area.importance
            if area.archived is not None:
                update_data['archived'] = area.archived
            
            update_data['updated_at'] = datetime.utcnow().isoformat()
            
            response = await supabase_manager.client.table('areas')\
                .update(update_data)\
                .eq('id', id)\
                .eq('user_id', str(user.id))\
                .execute()
            
            if response.data:
                updated_area = Area(**response.data[0])
                return AreaMutationResponse(
                    success=True,
                    message="Area updated successfully",
                    area=updated_area
                )
            
            return AreaMutationResponse(
                success=False,
                message="Area not found"
            )
            
        except Exception as e:
            logger.error(f"Error updating area: {e}")
            return AreaMutationResponse(
                success=False,
                message=str(e)
            )
    
    @strawberry.mutation
    async def delete_area(self, info, id: strawberry.ID) -> DeleteResponse:
        """Delete an area"""
        user = info.context["user"]
        
        try:
            response = await supabase_manager.client.table('areas')\
                .delete()\
                .eq('id', id)\
                .eq('user_id', str(user.id))\
                .execute()
            
            return DeleteResponse(
                success=True,
                message="Area deleted successfully"
            )
            
        except Exception as e:
            logger.error(f"Error deleting area: {e}")
            return DeleteResponse(
                success=False,
                message=str(e)
            )
    
    # Pillar Mutations
    @strawberry.mutation
    async def create_pillar(self, info, pillar: CreatePillarInput) -> PillarMutationResponse:
        """Create a new pillar"""
        user = info.context["user"]
        
        try:
            pillar_data = {
                'user_id': str(user.id),
                'name': pillar.name,
                'description': pillar.description or '',
                'icon': pillar.icon or '🏔️',
                'color': pillar.color or '#7C3AED'
            }
            
            response = await supabase_manager.client.table('pillars')\
                .insert(pillar_data)\
                .execute()
            
            if response.data:
                created_pillar = Pillar(**response.data[0])
                return PillarMutationResponse(
                    success=True,
                    message="Pillar created successfully",
                    pillar=created_pillar
                )
            
            return PillarMutationResponse(
                success=False,
                message="Failed to create pillar"
            )
            
        except Exception as e:
            logger.error(f"Error creating pillar: {e}")
            return PillarMutationResponse(
                success=False,
                message=str(e)
            )
    
    @strawberry.mutation
    async def update_pillar(self, info, id: strawberry.ID, pillar: UpdatePillarInput) -> PillarMutationResponse:
        """Update a pillar"""
        user = info.context["user"]
        
        try:
            update_data = {}
            if pillar.name is not None:
                update_data['name'] = pillar.name
            if pillar.description is not None:
                update_data['description'] = pillar.description
            if pillar.icon is not None:
                update_data['icon'] = pillar.icon
            if pillar.color is not None:
                update_data['color'] = pillar.color
            if pillar.archived is not None:
                update_data['archived'] = pillar.archived
            
            update_data['updated_at'] = datetime.utcnow().isoformat()
            
            response = await supabase_manager.client.table('pillars')\
                .update(update_data)\
                .eq('id', id)\
                .eq('user_id', str(user.id))\
                .execute()
            
            if response.data:
                updated_pillar = Pillar(**response.data[0])
                return PillarMutationResponse(
                    success=True,
                    message="Pillar updated successfully",
                    pillar=updated_pillar
                )
            
            return PillarMutationResponse(
                success=False,
                message="Pillar not found"
            )
            
        except Exception as e:
            logger.error(f"Error updating pillar: {e}")
            return PillarMutationResponse(
                success=False,
                message=str(e)
            )
    
    @strawberry.mutation
    async def delete_pillar(self, info, id: strawberry.ID) -> DeleteResponse:
        """Delete a pillar"""
        user = info.context["user"]
        
        try:
            response = await supabase_manager.client.table('pillars')\
                .delete()\
                .eq('id', id)\
                .eq('user_id', str(user.id))\
                .execute()
            
            return DeleteResponse(
                success=True,
                message="Pillar deleted successfully"
            )
            
        except Exception as e:
            logger.error(f"Error deleting pillar: {e}")
            return DeleteResponse(
                success=False,
                message=str(e)
            )