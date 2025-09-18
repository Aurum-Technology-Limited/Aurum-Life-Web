"""
HRM Phase 3: Hierarchical Reasoning Model Service
Provides intelligent reasoning across the PAPT hierarchy using LLM augmentation
Reference: aurum_life_hrm_phase3_prd.md - Section 3.1.1
"""

import uuid
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

from supabase_client import get_supabase_client
from models import User
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

@dataclass
class HRMInsight:
    """Structured insight from HRM analysis"""
    insight_id: str
    entity_type: str
    entity_id: Optional[str]
    insight_type: str
    title: str
    summary: str
    detailed_reasoning: Dict[str, Any]
    confidence_score: float
    impact_score: Optional[float]
    reasoning_path: List[Dict[str, Any]]
    recommendations: List[str]
    expires_at: Optional[datetime] = None

class AnalysisDepth(Enum):
    MINIMAL = "minimal"
    BALANCED = "balanced" 
    DETAILED = "detailed"

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
        self._rules_cache = None
        
    def _initialize_llm(self) -> LlmChat:
        """Initialize OpenAI GPT-5 nano with HRM-specific system prompt"""
        system_prompt = """You are the Aurum Life HRM (Hierarchical Reasoning Model), an advanced AI system that understands the relationships between life goals at every level.

Your role is to analyze the user's PAPT hierarchy (Pillars → Areas → Projects → Tasks) and provide intelligent insights about:
- Priority reasoning: Why certain items should be prioritized
- Alignment analysis: How well activities align with higher-level goals
- Pattern recognition: Detecting trends and behaviors
- Obstacle identification: Finding blockers and inefficiencies
- Goal coherence: Ensuring goals work together harmoniously

Always think hierarchically - consider how each level impacts and is impacted by others.
Be concise but thorough in your reasoning.
Provide actionable insights that help users make better decisions.
"""
        
        import os
        api_key = os.environ.get('OPENAI_API_KEY')
        model = os.environ.get('OPENAI_MODEL', 'gpt-5-nano')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
            
        return LlmChat(
            api_key=api_key,
            session_id=f"hrm-{self.user_id}",
            system_message=system_prompt
        ).with_model("openai", model)
    
    async def analyze_entity(
        self, 
        entity_type: str, 
        entity_id: Optional[str] = None, 
        analysis_depth: AnalysisDepth = AnalysisDepth.BALANCED,
        force_llm: bool = False
    ) -> HRMInsight:
        """
        Perform hierarchical reasoning on an entity
        
        Args:
            entity_type: Type of entity (pillar, area, project, task, global)
            entity_id: ID of specific entity (None for global analysis)
            analysis_depth: How deep to analyze (minimal, balanced, detailed)
            force_llm: Force LLM analysis even for simple cases
            
        Returns:
            HRMInsight with analysis results
        """
        try:
            # Get entity context
            entity_context = await self._get_entity_context(entity_type, entity_id)
            
            # Apply HRM rules
            rule_results = await self._apply_hrm_rules(entity_context, entity_type)
            
            # Determine if LLM analysis is needed
            needs_llm = force_llm or await self._should_use_llm_analysis(rule_results, analysis_depth)
            
            if needs_llm:
                # Get LLM insights
                llm_insights = await self._get_llm_insights(entity_context, rule_results, analysis_depth)
                combined_insights = await self._combine_rule_and_llm_insights(rule_results, llm_insights)
            else:
                combined_insights = rule_results
            
            # Create structured insight
            insight = await self._create_insight(
                entity_type=entity_type,
                entity_id=entity_id,
                analysis_results=combined_insights,
                depth=analysis_depth
            )
            
            # Store in blackboard
            await self._store_insight(insight)
            
            logger.info(f"✅ HRM analysis complete for {entity_type}:{entity_id} - Confidence: {insight.confidence_score:.2f}")
            return insight
            
        except Exception as e:
            logger.error(f"❌ HRM analysis failed for {entity_type}:{entity_id}: {e}")
            # Return fallback insight
            return HRMInsight(
                insight_id=str(uuid.uuid4()),
                entity_type=entity_type,
                entity_id=entity_id,
                insight_type='analysis_error',
                title='Analysis Error',
                summary=f'Unable to complete analysis: {str(e)}',
                detailed_reasoning={'error': str(e)},
                confidence_score=0.0,
                impact_score=0.0,
                reasoning_path=[],
                recommendations=['Please try again later or contact support']
            )
    
    async def _get_entity_context(self, entity_type: str, entity_id: Optional[str]) -> Dict[str, Any]:
        """Get full context for an entity including hierarchical relationships"""
        context = {
            'entity_type': entity_type,
            'entity_id': entity_id,
            'user_id': self.user_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if entity_type == 'global':
            # Global analysis - get overview of entire system
            context.update(await self._get_global_context())
        elif entity_type == 'task' and entity_id:
            context.update(await self._get_task_context(entity_id))
        elif entity_type == 'project' and entity_id:
            context.update(await self._get_project_context(entity_id))
        elif entity_type == 'area' and entity_id:
            context.update(await self._get_area_context(entity_id))
        elif entity_type == 'pillar' and entity_id:
            context.update(await self._get_pillar_context(entity_id))
        
        return context
    
    async def _get_task_context(self, task_id: str) -> Dict[str, Any]:
        """Get comprehensive context for a task"""
        # Get task with project/area/pillar chain
        task_query = """
        SELECT 
            t.*,
            p.name as project_name, p.importance as project_importance, p.status as project_status,
            a.name as area_name, a.importance as area_importance,
            pi.name as pillar_name, pi.time_allocation_percentage as pillar_time_allocation
        FROM tasks t
        LEFT JOIN projects p ON t.project_id = p.id
        LEFT JOIN areas a ON p.area_id = a.id
        LEFT JOIN pillars pi ON a.pillar_id = pi.id
        WHERE t.id = %s AND t.user_id = %s
        """
        
        # Query task with proper Supabase syntax (separate queries for relationships)
        task_resp = self.supabase.table('tasks').select(
            'id, name, description, status, priority, due_date, project_id'
        ).eq('id', task_id).eq('user_id', self.user_id).execute()
        
        if not task_resp.data:
            return {}
        
        task_data = task_resp.data[0]
        
        # Get project data if exists
        project_data = {}
        if task_data.get('project_id'):
            project_resp = self.supabase.table('projects').select(
                'id, name, description, area_id'
            ).eq('id', task_data['project_id']).execute()
            
            if project_resp.data:
                project_data = project_resp.data[0]
        
        # Get area data if exists
        area_data = {}
        if project_data.get('area_id'):
            area_resp = self.supabase.table('areas').select(
                'id, name, pillar_id'
            ).eq('id', project_data['area_id']).execute()
            
            if area_resp.data:
                area_data = area_resp.data[0]
        
        # Get pillar data if exists
        pillar_data = {}
        if area_data.get('pillar_id'):
            pillar_resp = self.supabase.table('pillars').select(
                'id, name'
            ).eq('id', area_data['pillar_id']).execute()
            
            if pillar_resp.data:
                pillar_data = pillar_resp.data[0]
        
        # Format the data for compatibility with original structure
        formatted_task = {
            'task_id': task_data['id'],
            'task_name': task_data['name'],
            'task_description': task_data.get('description', ''),
            'task_status': task_data.get('status', ''),
            'task_priority': task_data.get('priority', ''),
            'task_due_date': task_data.get('due_date'),
            'project_id': task_data.get('project_id'),
            'project_name': project_data.get('name'),
            'project_description': project_data.get('description'),
            'area_id': area_data.get('id'),
            'area_name': area_data.get('name'),
            'pillar_id': pillar_data.get('id'),
            'pillar_name': pillar_data.get('name')
        }
        
        task_data = formatted_task
        
        # Get dependencies if any
        dependencies = []
        if task_data.get('dependency_task_ids'):
            dep_resp = self.supabase.table('tasks').select('id, name, completed, status').in_(
                'id', task_data['dependency_task_ids']
            ).eq('user_id', self.user_id).execute()
            dependencies = dep_resp.data or []
        
        return {
            'task': task_data,
            'dependencies': dependencies,
            'hierarchy_depth': 4,
            'blocking_dependencies': [d for d in dependencies if not d.get('completed')]
        }
    
    async def _get_project_context(self, project_id: str) -> Dict[str, Any]:
        """Get comprehensive context for a project"""
        # Get project with tasks and parent hierarchy
        project_resp = self.supabase.table('projects').select(
            '*, areas(*, pillars(*))'
        ).eq('id', project_id).eq('user_id', self.user_id).execute()
        
        if not project_resp.data:
            return {}
        
        project_data = project_resp.data[0]
        
        # Get project tasks with status breakdown
        tasks_resp = self.supabase.table('tasks').select(
            'id, name, status, priority, completed, due_date, hrm_priority_score'
        ).eq('project_id', project_id).eq('user_id', self.user_id).execute()
        
        tasks = tasks_resp.data or []
        
        return {
            'project': project_data,
            'tasks': tasks,
            'task_stats': self._calculate_task_stats(tasks),
            'hierarchy_depth': 3
        }
    
    async def _apply_hrm_rules(self, context: Dict[str, Any], entity_type: str) -> Dict[str, Any]:
        """Apply all relevant HRM rules to the entity context"""
        if not self._rules_cache:
            await self._load_hrm_rules()
        
        applicable_rules = [
            rule for rule in self._rules_cache 
            if entity_type in rule.get('applies_to_entity_types', []) 
            and rule.get('is_active', True)
        ]
        
        rule_results = {
            'base_score': 0.0,
            'score_components': {},
            'applied_rules': [],
            'rule_reasoning': []
        }
        
        for rule in applicable_rules:
            try:
                rule_result = await self._apply_single_rule(rule, context)
                if rule_result:
                    rule_results['applied_rules'].append(rule['rule_code'])
                    rule_results['score_components'][rule['rule_code']] = rule_result['score_impact']
                    rule_results['rule_reasoning'].append(rule_result['reasoning'])
                    rule_results['base_score'] += rule_result['score_impact'] * rule.get('base_weight', 0.5)
            
            except Exception as e:
                logger.warning(f"Rule {rule['rule_code']} failed: {e}")
                continue
        
        return rule_results
    
    async def _should_use_llm_analysis(self, rule_results: Dict[str, Any], depth: AnalysisDepth) -> bool:
        """Determine if LLM analysis is needed based on rules and depth"""
        # Always use LLM for detailed analysis
        if depth == AnalysisDepth.DETAILED:
            return True
        
        # Use LLM if any rule requires it
        if any(rule.get('requires_llm') for rule in self._rules_cache 
               if rule['rule_code'] in rule_results.get('applied_rules', [])):
            return True
        
        # Use LLM if rule results are inconclusive (low confidence)
        confidence_indicators = [
            abs(score) for score in rule_results.get('score_components', {}).values()
        ]
        
        if confidence_indicators and max(confidence_indicators) < 0.3:
            return True
        
        return depth != AnalysisDepth.MINIMAL
    
    async def _get_llm_insights(
        self, 
        context: Dict[str, Any], 
        rule_results: Dict[str, Any], 
        depth: AnalysisDepth
    ) -> Dict[str, Any]:
        """Get insights from LLM analysis"""
        
        # Build comprehensive prompt based on context and rule results
        prompt = self._build_analysis_prompt(context, rule_results, depth)
        
        try:
            message = UserMessage(text=prompt)
            response = await self.llm.send_message(message)
            
            # Parse LLM response into structured format
            llm_insights = await self._parse_llm_response(response, context, depth)
            
            return llm_insights
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return {
                'llm_available': False,
                'fallback_reasoning': 'LLM analysis unavailable, using rule-based reasoning only',
                'confidence_penalty': -0.2
            }
    
    def _build_analysis_prompt(self, context: Dict[str, Any], rule_results: Dict[str, Any], depth: AnalysisDepth) -> str:
        """Build analysis prompt for LLM"""
        entity_type = context.get('entity_type')
        
        prompt_parts = [
            f"Analyze this {entity_type} in the context of the user's life goals hierarchy:",
            f"Context: {self._format_context_for_llm(context)}",
            f"Rule-based analysis results: {rule_results}",
        ]
        
        if depth == AnalysisDepth.DETAILED:
            prompt_parts.extend([
                "Provide detailed analysis including:",
                "1. Priority reasoning with specific factors",
                "2. Alignment analysis with higher-level goals", 
                "3. Pattern recognition and trends",
                "4. Obstacle identification and solutions",
                "5. Specific actionable recommendations"
            ])
        elif depth == AnalysisDepth.BALANCED:
            prompt_parts.extend([
                "Provide balanced analysis including:",
                "1. Key priority factors",
                "2. Goal alignment assessment",
                "3. Main recommendations (2-3)"
            ])
        else:  # MINIMAL
            prompt_parts.extend([
                "Provide minimal analysis:",
                "1. Primary priority factor",
                "2. One key recommendation"
            ])
        
        prompt_parts.append("Format your response as clear, actionable insights.")
        
        return "\n\n".join(prompt_parts)
    
    def _format_context_for_llm(self, context: Dict[str, Any]) -> str:
        """Format context data for LLM consumption"""
        entity_type = context.get('entity_type')
        formatted = []
        
        if entity_type == 'task':
            task = context.get('task', {})
            formatted.extend([
                f"Task: {task.get('name')}",
                f"Description: {task.get('description', 'No description')}",
                f"Status: {task.get('status')} | Priority: {task.get('priority')}",
                f"Due: {task.get('due_date', 'No due date')}",
                f"Project: {task.get('project_name', 'No project')} (Importance: {task.get('project_importance')})",
                f"Area: {task.get('area_name', 'No area')} (Importance: {task.get('area_importance')})",
                f"Pillar: {task.get('pillar_name', 'No pillar')} (Time Allocation: {task.get('pillar_time_allocation', 0)}%)"
            ])
            
            if context.get('blocking_dependencies'):
                formatted.append(f"Blocked by: {len(context['blocking_dependencies'])} incomplete dependencies")
        
        return " | ".join(formatted)
    
    async def _create_insight(
        self,
        entity_type: str,
        entity_id: Optional[str],
        analysis_results: Dict[str, Any],
        depth: AnalysisDepth
    ) -> HRMInsight:
        """Create structured insight from analysis results"""
        
        insight_id = str(uuid.uuid4())
        
        # Determine insight type based on analysis
        insight_type = self._determine_insight_type(analysis_results)
        
        # Generate title and summary
        title, summary = self._generate_title_and_summary(entity_type, analysis_results)
        
        # Calculate confidence score
        confidence = self._calculate_confidence_score(analysis_results)
        
        # Calculate impact score
        impact = self._calculate_impact_score(analysis_results, entity_type)
        
        # Build reasoning path
        reasoning_path = self._build_reasoning_path(analysis_results)
        
        # Generate recommendations
        recommendations = self._extract_recommendations(analysis_results)
        
        # Set expiration for time-sensitive insights
        expires_at = self._calculate_expiration(insight_type, entity_type)
        
        return HRMInsight(
            insight_id=insight_id,
            entity_type=entity_type,
            entity_id=entity_id,
            insight_type=insight_type,
            title=title,
            summary=summary,
            detailed_reasoning=analysis_results,
            confidence_score=confidence,
            impact_score=impact,
            reasoning_path=reasoning_path,
            recommendations=recommendations,
            expires_at=expires_at
        )
    
    async def _store_insight(self, insight: HRMInsight):
        """Store insight in blackboard system"""
        try:
            insight_data = {
                'id': insight.insight_id,
                'user_id': self.user_id,
                'entity_type': insight.entity_type,
                'entity_id': insight.entity_id,
                'insight_type': insight.insight_type,
                'title': insight.title,
                'summary': insight.summary,
                'detailed_reasoning': insight.detailed_reasoning,
                'confidence_score': insight.confidence_score,
                'impact_score': insight.impact_score,
                'reasoning_path': insight.reasoning_path,
                'expires_at': insight.expires_at.isoformat() if insight.expires_at else None,
                'tags': self._generate_insight_tags(insight),
                'created_at': datetime.utcnow().isoformat()
            }
            
            response = self.supabase.table('insights').insert(insight_data).execute()
            
            if response.data:
                logger.info(f"✅ Stored insight {insight.insight_id} in blackboard")
            else:
                logger.error(f"❌ Failed to store insight {insight.insight_id}")
                
        except Exception as e:
            logger.error(f"❌ Error storing insight: {e}")
    
    # Helper methods for rule processing, LLM parsing, scoring, etc.
    async def _load_hrm_rules(self):
        """Load HRM rules from database with caching"""
        try:
            resp = self.supabase.table('hrm_rules').select('*').eq('is_active', True).execute()
            self._rules_cache = resp.data or []
        except Exception as e:
            logger.warning(f"Failed to load HRM rules: {e}")
            # Use default rules if database is not available
            self._rules_cache = [
                {
                    'rule_code': 'priority_by_due_date',
                    'applies_to_entity_types': ['task'],
                    'is_active': True,
                    'base_weight': 0.7,
                    'requires_llm': False
                },
                {
                    'rule_code': 'alignment_with_pillar',
                    'applies_to_entity_types': ['task', 'project', 'area'],
                    'is_active': True,
                    'base_weight': 0.8,
                    'requires_llm': False
                }
            ]
    
    def _calculate_task_stats(self, tasks: List[Dict]) -> Dict[str, Any]:
        """Calculate task statistics for project context"""
        total = len(tasks)
        if total == 0:
            return {'total': 0, 'completed': 0, 'completion_rate': 0.0}
        
        completed = len([t for t in tasks if t.get('completed')])
        overdue = len([t for t in tasks if t.get('due_date') and datetime.fromisoformat(t['due_date'].replace('Z', '+00:00')) < datetime.utcnow()])
        
        return {
            'total': total,
            'completed': completed,
            'overdue': overdue,
            'completion_rate': completed / total,
            'overdue_rate': overdue / total
        }
    
    async def _get_global_context(self) -> Dict[str, Any]:
        """Get global context for user's entire system"""
        try:
            # Get high-level stats
            pillars_resp = self.supabase.table('pillars').select('id, name, time_allocation_percentage').eq('user_id', self.user_id).execute()
            areas_resp = self.supabase.table('areas').select('id, name, importance').eq('user_id', self.user_id).execute()
            projects_resp = self.supabase.table('projects').select('id, name, status, importance').eq('user_id', self.user_id).execute()
            tasks_resp = self.supabase.table('tasks').select('id, status, priority, completed, due_date').eq('user_id', self.user_id).execute()
            
            return {
                'pillars': pillars_resp.data or [],
                'areas': areas_resp.data or [],
                'projects': projects_resp.data or [],
                'tasks': tasks_resp.data or [],
                'task_stats': self._calculate_task_stats(tasks_resp.data or [])
            }
        except Exception as e:
            logger.error(f"Failed to get global context: {e}")
            return {}
    
    async def _get_area_context(self, area_id: str) -> Dict[str, Any]:
        """Get comprehensive context for an area"""
        try:
            area_resp = self.supabase.table('areas').select('*, pillars(*)').eq('id', area_id).eq('user_id', self.user_id).execute()
            if not area_resp.data:
                return {}
            
            area_data = area_resp.data[0]
            
            # Get projects in this area
            projects_resp = self.supabase.table('projects').select('id, name, status, importance').eq('area_id', area_id).eq('user_id', self.user_id).execute()
            projects = projects_resp.data or []
            
            return {
                'area': area_data,
                'projects': projects,
                'hierarchy_depth': 2
            }
        except Exception as e:
            logger.error(f"Failed to get area context: {e}")
            return {}
    
    async def _get_pillar_context(self, pillar_id: str) -> Dict[str, Any]:
        """Get comprehensive context for a pillar"""
        try:
            pillar_resp = self.supabase.table('pillars').select('*').eq('id', pillar_id).eq('user_id', self.user_id).execute()
            if not pillar_resp.data:
                return {}
            
            pillar_data = pillar_resp.data[0]
            
            # Get areas in this pillar
            areas_resp = self.supabase.table('areas').select('id, name, importance').eq('pillar_id', pillar_id).eq('user_id', self.user_id).execute()
            areas = areas_resp.data or []
            
            return {
                'pillar': pillar_data,
                'areas': areas,
                'hierarchy_depth': 1
            }
        except Exception as e:
            logger.error(f"Failed to get pillar context: {e}")
            return {}
    
    async def _apply_single_rule(self, rule: Dict[str, Any], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Apply a single HRM rule to context"""
        rule_code = rule.get('rule_code')
        
        try:
            if rule_code == 'priority_by_due_date':
                return await self._apply_due_date_rule(context)
            elif rule_code == 'alignment_with_pillar':
                return await self._apply_alignment_rule(context)
            else:
                logger.warning(f"Unknown rule code: {rule_code}")
                return None
        except Exception as e:
            logger.error(f"Error applying rule {rule_code}: {e}")
            return None
    
    async def _apply_due_date_rule(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply due date priority rule"""
        entity_type = context.get('entity_type')
        
        if entity_type == 'task':
            task = context.get('task', {})
            due_date_str = task.get('due_date')
            
            if not due_date_str:
                return {'score_impact': 0.0, 'reasoning': 'No due date set'}
            
            try:
                due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                days_until_due = (due_date - datetime.utcnow()).days
                
                if days_until_due < 0:
                    score_impact = 1.0  # Overdue - highest priority
                    reasoning = f"Task is {abs(days_until_due)} days overdue"
                elif days_until_due == 0:
                    score_impact = 0.9  # Due today
                    reasoning = "Task is due today"
                elif days_until_due <= 3:
                    score_impact = 0.7  # Due soon
                    reasoning = f"Task is due in {days_until_due} days"
                elif days_until_due <= 7:
                    score_impact = 0.4  # Due this week
                    reasoning = f"Task is due in {days_until_due} days"
                else:
                    score_impact = 0.1  # Due later
                    reasoning = f"Task is due in {days_until_due} days"
                
                return {
                    'score_impact': score_impact,
                    'reasoning': reasoning,
                    'rule_code': 'priority_by_due_date'
                }
            except Exception as e:
                return {'score_impact': 0.0, 'reasoning': f'Invalid due date format: {e}'}
        
        return {'score_impact': 0.0, 'reasoning': 'Rule not applicable to this entity type'}
    
    async def _apply_alignment_rule(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply alignment with pillar rule"""
        entity_type = context.get('entity_type')
        
        if entity_type in ['task', 'project', 'area']:
            # Check if entity has clear pillar connection
            pillar_name = None
            pillar_time_allocation = 0
            
            if entity_type == 'task':
                task = context.get('task', {})
                pillar_name = task.get('pillar_name')
                pillar_time_allocation = task.get('pillar_time_allocation', 0)
            
            if pillar_name and pillar_time_allocation:
                # Higher time allocation = higher alignment score
                score_impact = min(pillar_time_allocation / 100.0, 1.0)
                reasoning = f"Aligned with {pillar_name} pillar ({pillar_time_allocation}% time allocation)"
            else:
                score_impact = -0.2  # Penalty for poor alignment
                reasoning = "Poor alignment with pillar hierarchy"
            
            return {
                'score_impact': score_impact,
                'reasoning': reasoning,
                'rule_code': 'alignment_with_pillar'
            }
        
        return {'score_impact': 0.0, 'reasoning': 'Rule not applicable to this entity type'}
    
    async def _combine_rule_and_llm_insights(self, rule_results: Dict[str, Any], llm_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Combine rule-based and LLM insights"""
        combined = rule_results.copy()
        combined['llm_insights'] = llm_insights
        
        # Adjust confidence based on LLM availability
        if llm_insights.get('llm_available', True):
            combined['confidence_boost'] = 0.1
        else:
            combined['confidence_penalty'] = llm_insights.get('confidence_penalty', -0.1)
        
        return combined
    
    async def _parse_llm_response(self, response, context: Dict[str, Any], depth: AnalysisDepth) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        try:
            response_text = response.text if hasattr(response, 'text') else str(response)
            
            # Simple parsing - in production this would be more sophisticated
            insights = {
                'llm_available': True,
                'raw_response': response_text,
                'recommendations': [],
                'confidence_adjustment': 0.1
            }
            
            # Extract recommendations (simple pattern matching)
            lines = response_text.split('\n')
            for line in lines:
                if any(keyword in line.lower() for keyword in ['recommend', 'suggest', 'should', 'consider']):
                    insights['recommendations'].append(line.strip())
            
            # Limit recommendations
            insights['recommendations'] = insights['recommendations'][:3]
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return {
                'llm_available': False,
                'error': str(e),
                'confidence_penalty': -0.2
            }
    
    def _determine_insight_type(self, results: Dict[str, Any]) -> str:
        """Determine the primary insight type from analysis results"""
        if 'llm_insights' in results and results['llm_insights'].get('obstacle_identified'):
            return 'obstacle_identification'
        elif results.get('base_score', 0) > 0.8:
            return 'priority_reasoning'
        elif 'alignment_score' in results:
            return 'alignment_analysis'
        else:
            return 'recommendation'
    
    def _generate_title_and_summary(self, entity_type: str, results: Dict[str, Any]) -> tuple[str, str]:
        """Generate human-readable title and summary"""
        score = results.get('base_score', 0.0)
        
        if score > 0.8:
            title = f"High Priority {entity_type.title()}"
            summary = f"This {entity_type} scores highly on multiple factors and should be prioritized."
        elif score < -0.2:
            title = f"Low Priority {entity_type.title()}"  
            summary = f"This {entity_type} has several factors working against it and may be deprioritized."
        else:
            title = f"Balanced {entity_type.title()}"
            summary = f"This {entity_type} shows mixed signals and requires careful consideration."
        
        return title, summary
    
    def _calculate_confidence_score(self, results: Dict[str, Any]) -> float:
        """Calculate confidence score based on analysis quality"""
        base_confidence = 0.7
        
        # Boost confidence if LLM was used
        if results.get('llm_insights'):
            base_confidence += 0.1
        
        # Boost confidence based on number of applied rules
        rule_count = len(results.get('applied_rules', []))
        base_confidence += min(rule_count * 0.05, 0.2)
        
        # Reduce confidence if conflicting signals
        score_components = results.get('score_components', {}).values()
        if score_components:
            score_variance = max(score_components) - min(score_components)
            if score_variance > 1.0:
                base_confidence -= 0.1
        
        return min(max(base_confidence, 0.0), 1.0)
    
    def _calculate_impact_score(self, results: Dict[str, Any], entity_type: str) -> float:
        """Calculate potential impact of acting on this insight"""
        base_impact = 0.5
        
        # Higher impact for higher-level entities
        impact_multipliers = {
            'pillar': 0.9,
            'area': 0.7, 
            'project': 0.6,
            'task': 0.4,
            'global': 1.0
        }
        
        base_impact = impact_multipliers.get(entity_type, 0.5)
        
        # Adjust based on urgency indicators
        if abs(results.get('base_score', 0)) > 0.8:
            base_impact += 0.2
        
        return min(max(base_impact, 0.0), 1.0)
    
    def _build_reasoning_path(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build hierarchical reasoning path"""
        path = []
        
        for rule_code in results.get('applied_rules', []):
            rule_reasoning = next(
                (r for r in results.get('rule_reasoning', []) if r.get('rule_code') == rule_code),
                None
            )
            if rule_reasoning:
                path.append(rule_reasoning)
        
        return path
    
    def _extract_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Extract actionable recommendations from analysis"""
        recommendations = []
        
        # Add rule-based recommendations
        for reasoning in results.get('rule_reasoning', []):
            if 'recommendation' in reasoning:
                recommendations.append(reasoning['recommendation'])
        
        # Add LLM recommendations if available
        if results.get('llm_insights', {}).get('recommendations'):
            recommendations.extend(results['llm_insights']['recommendations'])
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _calculate_expiration(self, insight_type: str, entity_type: str) -> Optional[datetime]:
        """Calculate when this insight should expire"""
        expiration_rules = {
            'priority_reasoning': timedelta(hours=6),  # Priorities change quickly
            'obstacle_identification': timedelta(days=1),  # Obstacles need prompt attention
            'pattern_recognition': timedelta(days=7),  # Patterns are more stable
            'alignment_analysis': timedelta(days=3),  # Alignment needs periodic review
            'recommendation': timedelta(days=1)  # Recommendations should be acted on quickly
        }
        
        if insight_type in expiration_rules:
            return datetime.utcnow() + expiration_rules[insight_type]
        
        return None  # No expiration
    
    def _generate_insight_tags(self, insight: HRMInsight) -> List[str]:
        """Generate tags for insight categorization"""
        tags = [insight.entity_type, insight.insight_type]
        
        if insight.confidence_score > 0.8:
            tags.append('high_confidence')
        if insight.impact_score and insight.impact_score > 0.8:
            tags.append('high_impact')
        
        return tags

# Additional helper methods would be implemented here...
# This is a comprehensive foundation for the HRM service