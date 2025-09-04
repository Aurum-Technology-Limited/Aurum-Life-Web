"""
GraphQL Resolvers
Efficient data fetching with batching and caching
"""

import strawberry
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import logging
from functools import lru_cache
import asyncio
from collections import defaultdict

from graphql_schema import (
    User, Pillar, Area, Project, Task, JournalEntry, AlignmentScore,
    DailyReflection, Insight, UserStats, TaskStats, ProjectStats,
    DashboardData, TaskConnection, ProjectConnection, JournalEntryConnection,
    CreateTaskInput, UpdateTaskInput, CreateProjectInput, UpdateProjectInput,
    CreateJournalEntryInput, TaskMutationResponse, ProjectMutationResponse,
    JournalMutationResponse, PaginationInput, TaskFilterInput, ProjectFilterInput,
    TaskStatus, Priority, ProjectStatus, JournalInsights, SentimentTrend,
    WellnessScore, EmotionalInsight, ActivityCorrelation, AnalyticsDashboard,
    UserEngagement, AIFeatureUsage, DailyStats, FeatureAdoption, ErrorTracking,
    AnalyticsPreferences
)
from supabase_client import supabase_manager
from cache_service import cache_service
from models import User as UserModel

logger = logging.getLogger(__name__)

# DataLoader pattern for efficient batching
class DataLoader:
    """Simple DataLoader implementation for batching database queries"""
    
    def __init__(self, batch_fn, max_batch_size=100):
        self.batch_fn = batch_fn
        self.max_batch_size = max_batch_size
        self._queue = []
        self._cache = {}
        self._promise = None
    
    async def load(self, key):
        if key in self._cache:
            return self._cache[key]
        
        self._queue.append(key)
        
        if not self._promise:
            self._promise = asyncio.create_task(self._dispatch())
        
        result = await self._promise
        return result.get(key)
    
    async def _dispatch(self):
        keys = self._queue[:self.max_batch_size]
        self._queue = self._queue[self.max_batch_size:]
        
        results = await self.batch_fn(keys)
        
        # Cache results
        for key, value in results.items():
            self._cache[key] = value
        
        if self._queue:
            self._promise = asyncio.create_task(self._dispatch())
        else:
            self._promise = None
        
        return results

# Batch loading functions
async def batch_load_areas_by_pillar(pillar_ids: List[str]) -> Dict[str, List[Area]]:
    """Batch load areas for multiple pillars"""
    try:
        response = await supabase_manager.client.table('areas')\
            .select('*')\
            .in_('pillar_id', pillar_ids)\
            .eq('archived', False)\
            .order('sort_order')\
            .execute()
        
        # Group by pillar_id
        areas_by_pillar = defaultdict(list)
        for area_data in response.data:
            area = Area(**area_data)
            areas_by_pillar[area_data['pillar_id']].append(area)
        
        return dict(areas_by_pillar)
    except Exception as e:
        logger.error(f"Error batch loading areas: {e}")
        return {}

async def batch_load_projects_by_area(area_ids: List[str]) -> Dict[str, List[Project]]:
    """Batch load projects for multiple areas"""
    try:
        response = await supabase_manager.client.table('projects')\
            .select('*')\
            .in_('area_id', area_ids)\
            .eq('archived', False)\
            .order('sort_order')\
            .execute()
        
        # Group by area_id
        projects_by_area = defaultdict(list)
        for project_data in response.data:
            project = Project(**project_data)
            projects_by_area[project_data['area_id']].append(project)
        
        return dict(projects_by_area)
    except Exception as e:
        logger.error(f"Error batch loading projects: {e}")
        return {}

async def batch_load_tasks_by_project(project_ids: List[str]) -> Dict[str, List[Task]]:
    """Batch load tasks for multiple projects"""
    try:
        response = await supabase_manager.client.table('tasks')\
            .select('*')\
            .in_('project_id', project_ids)\
            .order('sort_order')\
            .execute()
        
        # Group by project_id
        tasks_by_project = defaultdict(list)
        for task_data in response.data:
            task = Task(**task_data)
            tasks_by_project[task_data['project_id']].append(task)
        
        return dict(tasks_by_project)
    except Exception as e:
        logger.error(f"Error batch loading tasks: {e}")
        return {}

# Create DataLoaders
area_loader = DataLoader(batch_load_areas_by_pillar)
project_loader = DataLoader(batch_load_projects_by_area)
task_loader = DataLoader(batch_load_tasks_by_project)

# Query Resolvers
@strawberry.type
class Query:
    @strawberry.field
    async def me(self, info) -> Optional[User]:
        """Get current user"""
        user = info.context["user"]
        if not user:
            return None
        
        return User(
            id=str(user.id),
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            profile_picture=user.profile_picture,
            is_active=user.is_active,
            created_at=user.created_at
        )
    
    @strawberry.field
    async def pillars(self, info, archived: bool = False) -> List[Pillar]:
        """Get all pillars for current user"""
        user = info.context["user"]
        
        # Try cache first
        cache_key = f"graphql:pillars:{user.id}:{archived}"
        cached = await cache_service.get(cache_key)
        if cached:
            return [Pillar(**p) for p in cached]
        
        response = await supabase_manager.client.table('pillars')\
            .select('*')\
            .eq('user_id', str(user.id))\
            .eq('archived', archived)\
            .order('sort_order')\
            .execute()
        
        pillars = [Pillar(**pillar) for pillar in response.data]
        
        # Cache for 5 minutes
        await cache_service.set(cache_key, response.data, ttl_seconds=300)
        
        return pillars
    
    @strawberry.field
    async def areas(
        self, 
        info, 
        pillar_id: Optional[strawberry.ID] = None,
        archived: bool = False
    ) -> List[Area]:
        """Get areas, optionally filtered by pillar"""
        user = info.context["user"]
        
        query = supabase_manager.client.table('areas')\
            .select('*')\
            .eq('user_id', str(user.id))\
            .eq('archived', archived)
        
        if pillar_id:
            query = query.eq('pillar_id', pillar_id)
        
        response = await query.order('sort_order').execute()
        
        return [Area(**area) for area in response.data]
    
    @strawberry.field
    async def projects(
        self,
        info,
        filter: Optional[ProjectFilterInput] = None,
        pagination: Optional[PaginationInput] = None
    ) -> ProjectConnection:
        """Get projects with filtering and pagination"""
        user = info.context["user"]
        pagination = pagination or PaginationInput()
        
        query = supabase_manager.client.table('projects')\
            .select('*', count='exact')\
            .eq('user_id', str(user.id))
        
        # Apply filters
        if filter:
            if filter.status:
                query = query.eq('status', filter.status.value)
            if filter.priority:
                query = query.eq('priority', filter.priority.value)
            if filter.area_id:
                query = query.eq('area_id', filter.area_id)
            if filter.archived is not None:
                query = query.eq('archived', filter.archived)
        
        # Apply pagination
        query = query.range(
            pagination.offset, 
            pagination.offset + pagination.limit - 1
        )
        
        response = await query.order('created_at', desc=True).execute()
        
        projects = [Project(**project) for project in response.data]
        total_count = response.count or 0
        
        return ProjectConnection(
            projects=projects,
            total_count=total_count,
            has_next_page=(pagination.offset + pagination.limit) < total_count
        )
    
    @strawberry.field
    async def tasks(
        self,
        info,
        filter: Optional[TaskFilterInput] = None,
        pagination: Optional[PaginationInput] = None
    ) -> TaskConnection:
        """Get tasks with filtering and pagination"""
        user = info.context["user"]
        pagination = pagination or PaginationInput()
        
        query = supabase_manager.client.table('tasks')\
            .select('*', count='exact')\
            .eq('user_id', str(user.id))
        
        # Apply filters
        if filter:
            if filter.status:
                query = query.eq('status', filter.status.value)
            if filter.priority:
                query = query.eq('priority', filter.priority.value)
            if filter.project_id:
                query = query.eq('project_id', filter.project_id)
            if filter.completed is not None:
                query = query.eq('completed', filter.completed)
            if filter.has_due_date:
                if filter.has_due_date:
                    query = query.not_.is_('due_date', 'null')
                else:
                    query = query.is_('due_date', 'null')
        
        # Apply pagination
        query = query.range(
            pagination.offset,
            pagination.offset + pagination.limit - 1
        )
        
        response = await query.order('created_at', desc=True).execute()
        
        tasks = [Task(**task) for task in response.data]
        total_count = response.count or 0
        
        return TaskConnection(
            tasks=tasks,
            total_count=total_count,
            has_next_page=(pagination.offset + pagination.limit) < total_count
        )
    
    @strawberry.field
    async def task(self, info, id: strawberry.ID) -> Optional[Task]:
        """Get single task by ID"""
        user = info.context["user"]
        
        response = await supabase_manager.client.table('tasks')\
            .select('*')\
            .eq('id', id)\
            .eq('user_id', str(user.id))\
            .single()\
            .execute()
        
        if response.data:
            return Task(**response.data)
        return None
    
    @strawberry.field
    async def project(self, info, id: strawberry.ID) -> Optional[Project]:
        """Get single project by ID"""
        user = info.context["user"]
        
        response = await supabase_manager.client.table('projects')\
            .select('*')\
            .eq('id', id)\
            .eq('user_id', str(user.id))\
            .single()\
            .execute()
        
        if response.data:
            return Project(**response.data)
        return None
    
    @strawberry.field(name="journalEntries")
    async def journal_entries(
        self,
        info,
        skip: Optional[int] = 0,
        limit: Optional[int] = 20,
        mood_filter: Optional[str] = None,
        tag_filter: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> List[JournalEntry]:
        """Get journal entries with filters"""
        user = info.context["user"]
        
        query = supabase_manager.client.table('journal_entries')\
            .select('*')\
            .eq('user_id', str(user.id))\
            .eq('deleted', False)
        
        # Apply mood filter
        if mood_filter:
            query = query.eq('mood', mood_filter)
        
        # Apply tag filter
        if tag_filter:
            query = query.contains('tags', [tag_filter])
        
        # Apply date filters
        if date_from:
            query = query.gte('created_at', date_from)
        if date_to:
            query = query.lte('created_at', date_to)
        
        # Apply pagination
        query = query.range(skip, skip + limit - 1)
        
        response = await query.order('created_at', desc=True).execute()
        
        entries = [JournalEntry(
            id=str(entry['id']),
            user_id=str(entry['user_id']),
            title=entry['title'],
            content=entry['content'],
            mood=entry.get('mood'),
            energy_level=entry.get('energy_level'),
            tags=entry.get('tags', []),
            word_count=entry.get('word_count', 0),
            created_at=datetime.fromisoformat(entry['created_at'].replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(entry['updated_at'].replace('Z', '+00:00')),
            sentiment_score=entry.get('sentiment_score'),
            sentiment_category=entry.get('sentiment_category'),
            emotional_keywords=entry.get('emotional_keywords', []),
            dominant_emotions=entry.get('dominant_emotions', [])
        ) for entry in (response.data or [])]
        
        return entries
    
    @strawberry.field(name="journalInsights")
    async def journal_insights(self, info, time_range: int = 30) -> JournalInsights:
        """Get journal insights and analytics"""
        user = info.context["user"]
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=time_range)
        
        # Fetch journal entries in time range
        entries_response = await supabase_manager.client.table('journal_entries')\
            .select('*')\
            .eq('user_id', str(user.id))\
            .gte('created_at', start_date.isoformat())\
            .lte('created_at', end_date.isoformat())\
            .execute()
        
        entries = entries_response.data or []
        
        # Calculate sentiment trends
        sentiment_by_date = {}
        for entry in entries:
            date_key = entry['created_at'][:10]  # YYYY-MM-DD
            if date_key not in sentiment_by_date:
                sentiment_by_date[date_key] = []
            if entry.get('sentiment_score') is not None:
                sentiment_by_date[date_key].append({
                    'score': entry['sentiment_score'],
                    'category': entry.get('sentiment_category', 'neutral')
                })
        
        sentiment_trends = []
        for date, sentiments in sorted(sentiment_by_date.items()):
            if sentiments:
                avg_score = sum(s['score'] for s in sentiments) / len(sentiments)
                # Determine overall category
                if avg_score > 0.6:
                    category = 'very_positive'
                elif avg_score > 0.2:
                    category = 'positive'
                elif avg_score > -0.2:
                    category = 'neutral'
                elif avg_score > -0.6:
                    category = 'negative'
                else:
                    category = 'very_negative'
                
                sentiment_trends.append(SentimentTrend(
                    date=date,
                    score=avg_score,
                    category=category
                ))
        
        # Calculate wellness scores
        total_entries = len(entries)
        positive_entries = len([e for e in entries if e.get('sentiment_score', 0) > 0.2])
        high_energy_entries = len([e for e in entries if e.get('energy_level') in ['high', 'very_high']])
        
        wellness_score = WellnessScore(
            overall=0.7 if total_entries > 0 else 0.5,
            emotional=positive_entries / total_entries if total_entries > 0 else 0.5,
            productivity=0.65,  # Would calculate from task completion
            balance=high_energy_entries / total_entries if total_entries > 0 else 0.5
        )
        
        # Generate emotional insights
        emotional_insights = []
        if total_entries > 5:
            if positive_entries / total_entries > 0.7:
                emotional_insights.append(EmotionalInsight(
                    type='positive_trend',
                    message='Your emotional state has been predominantly positive!',
                    confidence=0.85
                ))
            elif positive_entries / total_entries < 0.3:
                emotional_insights.append(EmotionalInsight(
                    type='support_needed',
                    message='Consider focusing on self-care and activities that bring you joy.',
                    confidence=0.8
                ))
        
        # Activity correlations (simplified)
        activity_correlations = [
            ActivityCorrelation(
                activity='journaling',
                sentiment_impact=0.15,
                frequency=total_entries
            )
        ]
        
        return JournalInsights(
            sentiment_trends=sentiment_trends,
            wellness_score=wellness_score,
            emotional_insights=emotional_insights,
            activity_correlations=activity_correlations
        )
    
    @strawberry.field
    async def dashboard(self, info) -> DashboardData:
        """Get dashboard data with all stats"""
        user = info.context["user"]
        
        # Parallel fetch all data
        tasks_future = supabase_manager.client.table('tasks')\
            .select('*')\
            .eq('user_id', str(user.id))\
            .execute()
        
        projects_future = supabase_manager.client.table('projects')\
            .select('*')\
            .eq('user_id', str(user.id))\
            .execute()
        
        user_stats_future = supabase_manager.client.table('user_stats')\
            .select('*')\
            .eq('user_id', str(user.id))\
            .single()\
            .execute()
        
        insights_future = supabase_manager.client.table('insights')\
            .select('*')\
            .eq('user_id', str(user.id))\
            .eq('is_active', True)\
            .order('created_at', desc=True)\
            .limit(5)\
            .execute()
        
        # Wait for all futures
        tasks_response = await tasks_future
        projects_response = await projects_future
        user_stats_response = await user_stats_future
        insights_response = await insights_future
        
        # Process tasks
        tasks = tasks_response.data
        now = datetime.utcnow()
        
        task_stats = TaskStats(
            total=len(tasks),
            completed=len([t for t in tasks if t['completed']]),
            in_progress=len([t for t in tasks if t['status'] == 'in_progress']),
            overdue=len([t for t in tasks if t['due_date'] and 
                        datetime.fromisoformat(t['due_date'].replace('Z', '+00:00')) < now and 
                        not t['completed']]),
            completion_rate=len([t for t in tasks if t['completed']]) / len(tasks) if tasks else 0
        )
        
        # Process projects
        projects = projects_response.data
        
        project_stats = ProjectStats(
            total=len(projects),
            completed=len([p for p in projects if p['status'] == 'Completed']),
            in_progress=len([p for p in projects if p['status'] == 'In Progress']),
            on_hold=len([p for p in projects if p['status'] == 'On Hold']),
            average_completion=sum(p.get('completion_percentage', 0) for p in projects) / len(projects) if projects else 0
        )
        
        # User stats
        stats_data = user_stats_response.data or {}
        
        user_stats = UserStats(
            task_stats=task_stats,
            project_stats=project_stats,
            total_journal_entries=stats_data.get('total_journal_entries', 0),
            total_areas=stats_data.get('total_areas', 0),
            total_pillars=stats_data.get('total_pillars', 0),
            current_streak=stats_data.get('daily_streak', 0),
            total_points=stats_data.get('total_points', 0)
        )
        
        # Recent tasks
        recent_tasks = sorted(
            [Task(**t) for t in tasks if not t['completed']],
            key=lambda t: t.created_at,
            reverse=True
        )[:10]
        
        # Upcoming deadlines
        upcoming_deadlines = sorted(
            [Task(**t) for t in tasks if t['due_date'] and not t['completed']],
            key=lambda t: t.due_date
        )[:10]
        
        # Recent insights
        recent_insights = [Insight(**i) for i in insights_response.data]
        
        return DashboardData(
            user_stats=user_stats,
            recent_tasks=recent_tasks,
            upcoming_deadlines=upcoming_deadlines,
            recent_insights=recent_insights,
            alignment_trend=[]  # TODO: Implement alignment trend
        )
    
    @strawberry.field(name="analyticsDashboard")
    async def analytics_dashboard(self, info, days: int = 30) -> AnalyticsDashboard:
        """Get analytics dashboard data"""
        user = info.context["user"]
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Fetch user behavior events
        events_response = await supabase_manager.client.table('user_behavior_events')\
            .select('*')\
            .eq('user_id', str(user.id))\
            .gte('timestamp', start_date.isoformat())\
            .lte('timestamp', end_date.isoformat())\
            .execute()
        
        events = events_response.data or []
        
        # Fetch sessions
        sessions_response = await supabase_manager.client.table('user_sessions')\
            .select('*')\
            .eq('user_id', str(user.id))\
            .gte('start_time', start_date.isoformat())\
            .execute()
        
        sessions = sessions_response.data or []
        
        # Calculate user engagement metrics
        total_sessions = len(sessions)
        total_ai_interactions = len([e for e in events if e['action_type'] == 'ai_interaction'])
        total_time_spent_ms = sum(s.get('duration_ms', 0) for s in sessions if s.get('duration_ms'))
        avg_session_duration = total_time_spent_ms // total_sessions if total_sessions > 0 else 0
        unique_features = len(set(e['feature_name'] for e in events))
        engagement_score = min(1.0, (total_sessions * 0.3 + total_ai_interactions * 0.5 + unique_features * 0.2) / 100)
        
        user_engagement = UserEngagement(
            total_sessions=total_sessions,
            total_ai_interactions=total_ai_interactions,
            total_time_spent_ms=total_time_spent_ms,
            average_session_duration_ms=avg_session_duration,
            unique_features_used=unique_features,
            engagement_score=engagement_score
        )
        
        # Calculate AI feature usage
        ai_feature_usage = []
        ai_events = [e for e in events if e['action_type'] == 'ai_interaction']
        feature_groups = defaultdict(list)
        for event in ai_events:
            feature_groups[event.get('ai_feature_type', 'unknown')].append(event)
        
        for feature_name, feature_events in feature_groups.items():
            success_count = len([e for e in feature_events if e.get('success', True)])
            total_count = len(feature_events)
            success_rate = success_count / total_count if total_count > 0 else 0
            
            # Calculate average response time
            response_times = [e.get('duration_ms', 0) for e in feature_events if e.get('duration_ms')]
            avg_response_time = sum(response_times) // len(response_times) if response_times else 0
            
            # Get last used timestamp
            last_used = max((datetime.fromisoformat(e['timestamp'].replace('Z', '+00:00')) 
                           for e in feature_events), default=None)
            
            ai_feature_usage.append(AIFeatureUsage(
                feature_name=feature_name,
                total_interactions=total_count,
                success_rate=success_rate,
                average_response_time_ms=avg_response_time,
                last_used=last_used
            ))
        
        # Calculate daily stats
        daily_stats = []
        events_by_date = defaultdict(list)
        sessions_by_date = defaultdict(list)
        
        for event in events:
            date_key = event['timestamp'][:10]  # YYYY-MM-DD
            events_by_date[date_key].append(event)
        
        for session in sessions:
            date_key = session['start_time'][:10]
            sessions_by_date[date_key].append(session)
        
        # Get tasks completed by date
        tasks_response = await supabase_manager.client.table('tasks')\
            .select('completed_at')\
            .eq('user_id', str(user.id))\
            .eq('completed', True)\
            .gte('completed_at', start_date.isoformat())\
            .lte('completed_at', end_date.isoformat())\
            .execute()
        
        tasks_by_date = defaultdict(int)
        for task in (tasks_response.data or []):
            if task.get('completed_at'):
                date_key = task['completed_at'][:10]
                tasks_by_date[date_key] += 1
        
        # Build daily stats
        current_date = start_date
        while current_date <= end_date:
            date_key = current_date.strftime('%Y-%m-%d')
            day_events = events_by_date.get(date_key, [])
            day_sessions = sessions_by_date.get(date_key, [])
            
            daily_stats.append(DailyStats(
                date=date_key,
                sessions=len(day_sessions),
                ai_interactions=len([e for e in day_events if e['action_type'] == 'ai_interaction']),
                features_used=len(set(e['feature_name'] for e in day_events)),
                tasks_completed=tasks_by_date.get(date_key, 0),
                time_spent_ms=sum(s.get('duration_ms', 0) for s in day_sessions if s.get('duration_ms'))
            ))
            
            current_date += timedelta(days=1)
        
        # Calculate feature adoption (simplified)
        feature_adoption = []
        all_features = ['my_ai_insights', 'ai_quick_actions', 'goal_planner', 'semantic_search']
        
        for feature in all_features:
            feature_count = len([e for e in events if e.get('ai_feature_type') == feature])
            adoption_rate = min(1.0, feature_count / max(total_sessions, 1))
            
            if feature_count > 20:
                frequency = 'high'
            elif feature_count > 5:
                frequency = 'medium'
            else:
                frequency = 'low'
            
            feature_adoption.append(FeatureAdoption(
                feature_name=feature,
                adoption_rate=adoption_rate,
                usage_frequency=frequency,
                user_satisfaction=None  # Would need feedback data
            ))
        
        # Error tracking (simplified)
        error_events = [e for e in events if not e.get('success', True)]
        error_groups = defaultdict(list)
        for error in error_events:
            error_type = error.get('error_message', 'Unknown error')[:50]  # Truncate
            error_groups[error_type].append(error)
        
        error_tracking = []
        for error_type, errors in list(error_groups.items())[:10]:  # Top 10 errors
            last_error = max(errors, key=lambda e: e['timestamp'])
            error_tracking.append(ErrorTracking(
                error_type=error_type,
                occurrences=len(errors),
                affected_users=1,  # Current user only
                last_occurred=datetime.fromisoformat(last_error['timestamp'].replace('Z', '+00:00')),
                severity='medium'  # Would need proper classification
            ))
        
        # Top pages and features
        page_counts = defaultdict(int)
        feature_counts = defaultdict(int)
        
        for event in events:
            if event['action_type'] == 'page_view':
                page_counts[event.get('page_url', '/')] += 1
            feature_counts[event.get('feature_name', 'unknown')] += 1
        
        top_pages = [{'url': url, 'views': count} for url, count in 
                     sorted(page_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
        top_features = [{'name': name, 'uses': count} for name, count in 
                       sorted(feature_counts.items(), key=lambda x: x[1], reverse=True)[:5]]
        
        return AnalyticsDashboard(
            user_engagement=user_engagement,
            ai_feature_usage=ai_feature_usage,
            daily_stats=daily_stats,
            feature_adoption=feature_adoption,
            error_tracking=error_tracking,
            top_pages=top_pages,
            top_features=top_features
        )
    
    @strawberry.field(name="analyticsPreferences")
    async def analytics_preferences(self, info) -> Optional[AnalyticsPreferences]:
        """Get user's analytics preferences"""
        user = info.context["user"]
        
        response = await supabase_manager.client.table('user_analytics_preferences')\
            .select('*')\
            .eq('user_id', str(user.id))\
            .single()\
            .execute()
        
        if response.data:
            prefs = response.data
            return AnalyticsPreferences(
                analytics_consent=prefs.get('analytics_consent', True),
                ai_behavior_tracking=prefs.get('ai_behavior_tracking', True),
                performance_tracking=prefs.get('performance_tracking', True),
                error_reporting=prefs.get('error_reporting', True),
                data_retention_days=prefs.get('data_retention_days', 365),
                anonymize_after_days=prefs.get('anonymize_after_days', 90),
                share_anonymous_stats=prefs.get('share_anonymous_stats', True)
            )
        
        # Return defaults if no preferences found
        return AnalyticsPreferences(
            analytics_consent=True,
            ai_behavior_tracking=True,
            performance_tracking=True,
            error_reporting=True,
            data_retention_days=365,
            anonymize_after_days=90,
            share_anonymous_stats=True
        )

# Field Resolvers for related data
@strawberry.type
class Pillar:
    # ... existing fields ...
    
    @strawberry.field
    async def areas(self, info) -> List[Area]:
        """Resolve areas for this pillar"""
        return await area_loader.load(self.id)

@strawberry.type
class Area:
    # ... existing fields ...
    
    @strawberry.field
    async def projects(self, info) -> List[Project]:
        """Resolve projects for this area"""
        return await project_loader.load(self.id)

@strawberry.type
class Project:
    # ... existing fields ...
    
    @strawberry.field
    async def tasks(self, info) -> List[Task]:
        """Resolve tasks for this project"""
        return await task_loader.load(self.id)