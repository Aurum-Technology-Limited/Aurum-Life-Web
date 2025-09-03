#!/usr/bin/env python3
"""
Generate Real AI Insights Based on User Data
This script creates meaningful insights from actual user activities
"""
import os
import sys
sys.path.append('/app/backend')

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid
import random

from supabase_client import get_supabase_client
from blackboard_service import BlackboardService
from hrm_service import HierarchicalReasoningModel, AnalysisDepth

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealInsightGenerator:
    """Generate insights based on real user data patterns"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.blackboard = BlackboardService()
        
    async def get_user_data_summary(self, user_id: str) -> Dict[str, Any]:
        """Analyze user's actual data to create insights"""
        try:
            # Get user's tasks
            tasks_response = self.supabase.table('tasks').select('*').eq('user_id', user_id).execute()
            tasks = tasks_response.data or []
            
            # Get user's projects  
            projects_response = self.supabase.table('projects').select('*').eq('user_id', user_id).execute()
            projects = projects_response.data or []
            
            # Get user's journal entries
            journal_response = self.supabase.table('journal_entries').select('*').eq('user_id', user_id).execute()
            journal_entries = journal_response.data or []
            
            # Get user's pillars
            pillars_response = self.supabase.table('pillars').select('*').eq('user_id', user_id).execute()
            pillars = pillars_response.data or []
            
            # Get user's areas
            areas_response = self.supabase.table('areas').select('*').eq('user_id', user_id).execute()
            areas = areas_response.data or []
            
            return {
                'tasks': tasks,
                'projects': projects,
                'journal_entries': journal_entries,
                'pillars': pillars,
                'areas': areas,
                'total_tasks': len(tasks),
                'total_projects': len(projects),
                'total_journals': len(journal_entries),
                'total_pillars': len(pillars),
                'total_areas': len(areas)
            }
            
        except Exception as e:
            logger.error(f"Error getting user data: {e}")
            return {}
    
    def analyze_task_patterns(self, tasks: List[Dict]) -> List[Dict[str, Any]]:
        """Analyze user's task patterns to generate insights"""
        insights = []
        
        if not tasks:
            return [{
                'title': 'Getting Started',
                'summary': 'You haven\'t created any tasks yet. Start by adding some tasks to track your progress and get personalized insights.',
                'insight_type': 'recommendation',
                'confidence_score': 0.9,
                'impact_score': 0.8,
                'priority': 'high',
                'recommendations': [
                    'Create your first task to get started',
                    'Break down large goals into smaller, manageable tasks',
                    'Set realistic deadlines for better productivity'
                ]
            }]
        
        # Analyze completion rates
        completed_tasks = [t for t in tasks if t.get('status') == 'completed']
        completion_rate = len(completed_tasks) / len(tasks) if tasks else 0
        
        if completion_rate > 0.8:
            insights.append({
                'title': 'High Task Completion Rate',
                'summary': f'Excellent! You\'ve completed {len(completed_tasks)} out of {len(tasks)} tasks ({completion_rate:.1%} completion rate). You\'re demonstrating great follow-through.',
                'insight_type': 'pattern_recognition',
                'confidence_score': 0.95,
                'impact_score': 0.7,
                'priority': 'medium',
                'recommendations': [
                    'Continue this excellent momentum',
                    'Consider taking on more challenging tasks',
                    'Share your productivity strategies with others'
                ]
            })
        elif completion_rate < 0.3:
            insights.append({
                'title': 'Task Completion Opportunity',
                'summary': f'You have {len(tasks) - len(completed_tasks)} pending tasks out of {len(tasks)} total. This presents an opportunity to boost your productivity.',
                'insight_type': 'obstacle_identification', 
                'confidence_score': 0.85,
                'impact_score': 0.9,
                'priority': 'high',
                'recommendations': [
                    'Break down large tasks into smaller steps',
                    'Set specific deadlines for each task',
                    'Focus on completing 2-3 tasks this week',
                    'Review and remove tasks that are no longer relevant'
                ]
            })
        
        # Analyze overdue tasks
        overdue_tasks = []
        for task in tasks:
            due_date = task.get('due_date')
            if due_date and task.get('status') != 'completed':
                try:
                    due_datetime = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    if due_datetime < datetime.now():
                        overdue_tasks.append(task)
                except:
                    pass
        
        if overdue_tasks:
            insights.append({
                'title': 'Overdue Tasks Need Attention',
                'summary': f'You have {len(overdue_tasks)} overdue tasks that need immediate attention to prevent further delays.',
                'insight_type': 'priority_reasoning',
                'confidence_score': 1.0,
                'impact_score': 0.95,
                'priority': 'critical',
                'recommendations': [
                    'Review overdue tasks and prioritize the most important ones',
                    'Reschedule unrealistic deadlines',
                    'Consider delegating or removing tasks that are no longer relevant',
                    'Set up reminders for upcoming deadlines'
                ]
            })
        
        return insights
    
    def analyze_project_patterns(self, projects: List[Dict], tasks: List[Dict]) -> List[Dict[str, Any]]:
        """Analyze project patterns and relationships with tasks"""
        insights = []
        
        if not projects:
            return [{
                'title': 'Project Organization Opportunity',
                'summary': 'Consider organizing your tasks into projects for better structure and tracking of larger initiatives.',
                'insight_type': 'recommendation',
                'confidence_score': 0.8,
                'impact_score': 0.7,
                'priority': 'medium',
                'recommendations': [
                    'Group related tasks into projects',
                    'Set clear project goals and deadlines',
                    'Track progress at the project level'
                ]
            }]
        
        # Analyze project-task distribution
        project_tasks = {}
        for task in tasks:
            project_id = task.get('project_id')
            if project_id:
                if project_id not in project_tasks:
                    project_tasks[project_id] = []
                project_tasks[project_id].append(task)
        
        # Find projects with no tasks
        empty_projects = [p for p in projects if p.get('id') not in project_tasks]
        if empty_projects:
            insights.append({
                'title': 'Projects Need Tasks',
                'summary': f'{len(empty_projects)} projects don\'t have any tasks assigned. Add specific action items to move these projects forward.',
                'insight_type': 'alignment_analysis',
                'confidence_score': 0.9,
                'impact_score': 0.8,
                'priority': 'high',
                'recommendations': [
                    'Review empty projects and add specific tasks',
                    'Break down project goals into actionable steps',
                    'Consider archiving projects that are no longer active'
                ]
            })
        
        # Find most active project
        if project_tasks:
            most_active_project_id = max(project_tasks.keys(), key=lambda k: len(project_tasks[k]))
            most_active_project = next(p for p in projects if p.get('id') == most_active_project_id)
            task_count = len(project_tasks[most_active_project_id])
            
            insights.append({
                'title': f'Most Active Project: {most_active_project.get("name", "Unnamed Project")}',
                'summary': f'This project has {task_count} tasks and represents your primary focus area. Great concentration of effort!',
                'insight_type': 'pattern_recognition',
                'confidence_score': 0.9,
                'impact_score': 0.6,
                'priority': 'medium',
                'recommendations': [
                    'Continue focusing on this high-priority project',
                    'Set milestones to track progress',
                    'Consider if other projects need more attention'
                ]
            })
        
        return insights
    
    def analyze_journal_patterns(self, journal_entries: List[Dict]) -> List[Dict[str, Any]]:
        """Analyze journaling patterns for insights"""
        insights = []
        
        if not journal_entries:
            return [{
                'title': 'Start Your Reflection Journey',
                'summary': 'Journaling is a powerful tool for self-reflection and growth. Start with just a few minutes daily to capture your thoughts and experiences.',
                'insight_type': 'recommendation',
                'confidence_score': 0.85,
                'impact_score': 0.9,
                'priority': 'high',
                'recommendations': [
                    'Write your first journal entry today',
                    'Set a daily reminder for reflection time',
                    'Start with simple prompts like "What went well today?"',
                    'Focus on gratitude and learning experiences'
                ]
            }]
        
        # Analyze recent journaling activity
        recent_entries = []
        week_ago = datetime.now() - timedelta(days=7)
        for entry in journal_entries:
            created_at = entry.get('created_at')
            if created_at:
                try:
                    entry_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    if entry_date > week_ago:
                        recent_entries.append(entry)
                except:
                    pass
        
        if recent_entries:
            insights.append({
                'title': 'Active Reflection Practice',
                'summary': f'You\'ve written {len(recent_entries)} journal entries this week. This consistent reflection practice is excellent for personal growth.',
                'insight_type': 'pattern_recognition',
                'confidence_score': 0.9,
                'impact_score': 0.7,
                'priority': 'medium',
                'recommendations': [
                    'Continue this excellent journaling habit',
                    'Try reviewing past entries to identify patterns',
                    'Consider setting specific themes for different days',
                    'Share insights with trusted friends or mentors'
                ]
            })
        elif len(journal_entries) > 0:
            insights.append({
                'title': 'Reconnect With Reflection',
                'summary': f'You have {len(journal_entries)} journal entries but haven\'t written recently. Returning to regular reflection can boost self-awareness.',
                'insight_type': 'recommendation',
                'confidence_score': 0.8,
                'impact_score': 0.8,
                'priority': 'medium',
                'recommendations': [
                    'Set aside 10 minutes today for journaling',
                    'Reflect on recent experiences and learnings',
                    'Consider what barriers prevent regular journaling',
                    'Set up a recurring reminder for reflection time'
                ]
            })
        
        return insights
    
    def analyze_goal_alignment(self, user_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze overall goal alignment across all user data"""
        insights = []
        
        pillars = user_data.get('pillars', [])
        areas = user_data.get('areas', [])
        projects = user_data.get('projects', [])
        tasks = user_data.get('tasks', [])
        
        # Check for hierarchical structure
        if not pillars:
            insights.append({
                'title': 'Define Your Core Pillars',
                'summary': 'Pillars represent the fundamental areas of your life (like Health, Career, Relationships). Defining these creates a strong foundation for all your goals.',
                'insight_type': 'alignment_analysis',
                'confidence_score': 0.95,
                'impact_score': 1.0,
                'priority': 'critical',
                'recommendations': [
                    'Identify 3-5 core life pillars that matter most to you',
                    'Examples: Health & Fitness, Career Growth, Relationships, Learning',
                    'Make sure each pillar reflects your values and long-term vision',
                    'Use pillars to guide all other goal-setting decisions'
                ]
            })
        
        if pillars and not areas:
            insights.append({
                'title': 'Break Down Your Pillars Into Areas',
                'summary': f'You have {len(pillars)} pillars defined. Now create specific focus areas within each pillar to organize your efforts more effectively.',
                'insight_type': 'goal_coherence',
                'confidence_score': 0.9,
                'impact_score': 0.9,
                'priority': 'high',
                'recommendations': [
                    'Create 2-3 areas for each pillar',
                    'Areas should be specific focus zones within each pillar',
                    'Example: "Health" pillar might have "Exercise", "Nutrition", "Mental Health" areas',
                    'This creates better organization and clearer focus'
                ]
            })
        
        # Analyze distribution across pillars
        if pillars and tasks:
            pillar_task_counts = {}
            for pillar in pillars:
                pillar_task_counts[pillar.get('name', 'Unnamed')] = 0
            
            # Count tasks per pillar (through areas and projects)
            for task in tasks:
                project_id = task.get('project_id')
                if project_id:
                    project = next((p for p in projects if p.get('id') == project_id), None)
                    if project:
                        area_id = project.get('area_id')
                        if area_id:
                            area = next((a for a in areas if a.get('id') == area_id), None)
                            if area:
                                pillar_id = area.get('pillar_id')
                                if pillar_id:
                                    pillar = next((p for p in pillars if p.get('id') == pillar_id), None)
                                    if pillar:
                                        pillar_name = pillar.get('name', 'Unnamed')
                                        pillar_task_counts[pillar_name] += 1
            
            # Find imbalanced pillars
            total_tasks = sum(pillar_task_counts.values())
            if total_tasks > 0:
                neglected_pillars = [name for name, count in pillar_task_counts.items() if count == 0]
                if neglected_pillars:
                    insights.append({
                        'title': 'Some Life Pillars Need Attention',
                        'summary': f'Your {", ".join(neglected_pillars)} pillar(s) don\'t have active tasks. Consider if these areas need more focus for a balanced life.',
                        'insight_type': 'alignment_analysis',
                        'confidence_score': 0.85,
                        'impact_score': 0.8,
                        'priority': 'high',
                        'recommendations': [
                            'Review neglected pillars and assess their importance',
                            'Add at least one project or task for each important pillar',
                            'Consider if some pillars should be merged or redefined',
                            'Aim for balanced attention across your core life areas'
                        ]
                    })
        
        return insights
    
    async def generate_insights_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Generate comprehensive insights for a user"""
        logger.info(f"Generating insights for user {user_id}")
        
        # Get user data
        user_data = await self.get_user_data_summary(user_id)
        all_insights = []
        
        # Generate different types of insights
        task_insights = self.analyze_task_patterns(user_data.get('tasks', []))
        project_insights = self.analyze_project_patterns(
            user_data.get('projects', []), 
            user_data.get('tasks', [])
        )
        journal_insights = self.analyze_journal_patterns(user_data.get('journal_entries', []))
        alignment_insights = self.analyze_goal_alignment(user_data)
        
        all_insights.extend(task_insights)
        all_insights.extend(project_insights) 
        all_insights.extend(journal_insights)
        all_insights.extend(alignment_insights)
        
        # Limit to top 10 most important insights
        all_insights.sort(key=lambda x: (
            {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}[x.get('priority', 'low')],
            x.get('confidence_score', 0),
            x.get('impact_score', 0)
        ), reverse=True)
        
        return all_insights[:10]
    
    async def store_insight_in_blackboard(self, user_id: str, insight_data: Dict[str, Any]) -> str:
        """Store insight in the blackboard/database"""
        try:
            insight_id = str(uuid.uuid4())
            
            # Prepare insight data for database
            db_insight = {
                'id': insight_id,
                'user_id': user_id,
                'entity_type': 'global',  # Most insights are global
                'entity_id': None,
                'insight_type': insight_data.get('insight_type', 'recommendation'),
                'title': insight_data.get('title', 'Insight'),
                'summary': insight_data.get('summary', ''),
                'reasoning_path': insight_data.get('recommendations', []),
                'confidence_score': insight_data.get('confidence_score', 0.5),
                'impact_score': insight_data.get('impact_score', 0.5),
                'tags': [],
                'metadata': {
                    'priority': insight_data.get('priority', 'medium'),
                    'recommendations': insight_data.get('recommendations', [])
                },
                'is_active': True,
                'is_pinned': insight_data.get('priority') == 'critical',
                'expires_at': None,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'last_accessed_at': None
            }
            
            # Insert into database
            response = self.supabase.table('insights').insert(db_insight).execute()
            
            if response.data:
                logger.info(f"✅ Stored insight: {insight_data.get('title')}")
                return insight_id
            else:
                logger.error(f"❌ Failed to store insight: {response}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error storing insight: {e}")
            return None
    
    async def clear_old_generic_insights(self, user_id: str):
        """Remove old generic/test insights"""
        try:
            # Delete insights with generic titles like "Balanced Global"
            response = self.supabase.table('insights').delete().eq('user_id', user_id).ilike('title', '%Balanced Global%').execute()
            logger.info(f"✅ Cleared old generic insights for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error clearing old insights: {e}")
    
    async def generate_and_store_insights(self, user_id: str):
        """Main method to generate and store insights for a user"""
        try:
            logger.info(f"Starting insight generation for user {user_id}")
            
            # Clear old generic insights first
            await self.clear_old_generic_insights(user_id)
            logger.info("Cleared old generic insights")
            
            # Generate new insights
            insights = await self.generate_insights_for_user(user_id)
            logger.info(f"Generated {len(insights)} insights")
            
            if not insights:
                logger.warning("No insights generated - this may indicate no user data or errors")
                return 0
            
            stored_count = 0
            for i, insight in enumerate(insights):
                logger.info(f"Storing insight {i+1}: {insight.get('title', 'No title')}")
                insight_id = await self.store_insight_in_blackboard(user_id, insight)
                if insight_id:
                    stored_count += 1
                else:
                    logger.error(f"Failed to store insight: {insight.get('title')}")
            
            logger.info(f"✅ Generated and stored {stored_count} insights for user {user_id}")
            return stored_count
            
        except Exception as e:
            logger.error(f"❌ Error generating insights: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return 0

async def main():
    """Main function to generate insights for test user"""
    generator = RealInsightGenerator()
    
    # Use the actual user ID found in the database
    test_user_id = 'f9ed7066-5954-46e2-8de3-92d38a28832f'
    logger.info(f"🎯 Generating insights for user ID: {test_user_id}")
    
    try:
        # Generate insights
        count = await generator.generate_and_store_insights(str(test_user_id))
        
        if count > 0:
            print(f"\n🎉 SUCCESS: Generated {count} real insights based on user data!")
        else:
            print(f"\n⚠️  Generated {count} insights - there may have been errors. Check the logs above.")
        print("The 'My AI Insights' page should now show meaningful, personalized insights.")
        
    except Exception as e:
        logger.error(f"❌ Error in main: {e}")
        print(f"\n💥 FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(main())