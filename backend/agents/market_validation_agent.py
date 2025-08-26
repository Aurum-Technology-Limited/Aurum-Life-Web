"""
Market & Customer Validation Agent
The relentless truth-seeker that validates hypotheses through empirical data
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from agent_base import BaseAgent, AgentMessage, AgentCapability, AgentState
from supabase_client import get_supabase_client
from models import User
import httpx
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

class MarketValidationAgent(BaseAgent):
    """
    Market validation agent that tests hypotheses and gathers empirical data
    Uses Lean Startup methodology for rapid validation cycles
    """
    
    def __init__(self):
        super().__init__(
            agent_id="market_validation_001",
            agent_type="MarketValidation"
        )
        self.supabase = None
        self.llm_chat = None
        self.validation_methods = {
            "competitive_analysis": self._competitive_analysis,
            "user_survey": self._create_user_survey,
            "interview_questions": self._generate_interview_questions,
            "ab_test_design": self._design_ab_test,
            "market_research": self._conduct_market_research
        }
        
    async def initialize(self) -> None:
        """Initialize connections and resources"""
        self.supabase = get_supabase_client()
        self.llm_chat = LlmChat(
            system_prompt="You are a market research expert specializing in hypothesis validation using lean startup methodology. Focus on empirical data and actionable insights."
        )
        
        # Register capabilities
        self.add_capability(AgentCapability(
            name="validate_hypothesis",
            description="Test a business hypothesis using appropriate validation methods",
            input_schema={
                "hypothesis": "string",
                "validation_method": "string (competitive_analysis|user_survey|interview_questions|ab_test_design|market_research)",
                "context": "object"
            },
            output_schema={
                "status": "string (validated|invalidated|needs_more_data)",
                "confidence": "number (0-100)",
                "evidence": "array",
                "insights": "array",
                "next_steps": "array"
            }
        ))
        
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process incoming validation requests"""
        try:
            if message.message_type == "validate_hypothesis":
                result = await self._validate_hypothesis(message.payload)
                
                return AgentMessage(
                    source_agent=self.agent_id,
                    target_agent=message.source_agent,
                    message_type="validation_result",
                    payload=result,
                    correlation_id=message.correlation_id
                )
                
            elif message.message_type == "batch_validation":
                results = await self._batch_validate(message.payload.get("hypotheses", []))
                
                return AgentMessage(
                    source_agent=self.agent_id,
                    target_agent=message.source_agent,
                    message_type="batch_validation_result",
                    payload={"results": results},
                    correlation_id=message.correlation_id
                )
                
            else:
                logger.warning(f"Unknown message type: {message.message_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return AgentMessage(
                source_agent=self.agent_id,
                target_agent=message.source_agent,
                message_type="error",
                payload={"error": str(e)},
                correlation_id=message.correlation_id
            )
            
    def get_capabilities(self) -> List[AgentCapability]:
        """Return agent capabilities"""
        return self.capabilities
        
    async def _validate_hypothesis(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a single hypothesis"""
        hypothesis = payload.get("hypothesis")
        method = payload.get("validation_method", "market_research")
        context = payload.get("context", {})
        
        # Break down hypothesis into testable components
        components = await self._analyze_hypothesis(hypothesis)
        
        # Execute validation method
        validation_func = self.validation_methods.get(method, self._conduct_market_research)
        validation_data = await validation_func(hypothesis, context)
        
        # Analyze results
        analysis = await self._analyze_validation_data(
            hypothesis, 
            components, 
            validation_data
        )
        
        # Store validation results in database
        await self._store_validation_results(hypothesis, analysis)
        
        return analysis
        
    async def _analyze_hypothesis(self, hypothesis: str) -> Dict[str, Any]:
        """Break down hypothesis into testable components"""
        prompt = f"""Analyze this hypothesis and break it down into testable components:

Hypothesis: {hypothesis}

Provide:
1. Key assumptions to test
2. Success metrics
3. Target audience
4. Time frame for validation
5. Risk factors"""

        response = await self.llm_chat.get_response(UserMessage(content=prompt))
        
        # Parse structured response
        # In production, this would use structured output parsing
        return {
            "assumptions": self._extract_list(response, "assumptions"),
            "metrics": self._extract_list(response, "metrics"),
            "audience": self._extract_text(response, "audience"),
            "timeframe": self._extract_text(response, "timeframe"),
            "risks": self._extract_list(response, "risks")
        }
        
    async def _competitive_analysis(self, hypothesis: str, context: Dict) -> Dict[str, Any]:
        """Conduct competitive analysis"""
        # In production, this would integrate with real data sources
        # For now, we'll use LLM to simulate competitive research
        
        prompt = f"""Conduct a competitive analysis for this hypothesis:

Hypothesis: {hypothesis}
Market: {context.get('market', 'general')}
Industry: {context.get('industry', 'technology')}

Analyze:
1. Direct competitors and their solutions
2. Market gaps and opportunities
3. Competitive advantages
4. Market size and growth potential
5. Entry barriers"""

        response = await self.llm_chat.get_response(UserMessage(content=prompt))
        
        return {
            "competitors": self._extract_list(response, "competitors"),
            "market_gaps": self._extract_list(response, "gaps"),
            "advantages": self._extract_list(response, "advantages"),
            "market_size": self._extract_text(response, "market size"),
            "barriers": self._extract_list(response, "barriers"),
            "raw_analysis": response.content
        }
        
    async def _create_user_survey(self, hypothesis: str, context: Dict) -> Dict[str, Any]:
        """Generate user survey questions"""
        prompt = f"""Create a targeted user survey to validate this hypothesis:

Hypothesis: {hypothesis}
Target Audience: {context.get('audience', 'general users')}

Generate:
1. 5-7 survey questions (mix of multiple choice and open-ended)
2. Expected response patterns that would validate the hypothesis
3. Red flags that would invalidate the hypothesis
4. Recommended sample size"""

        response = await self.llm_chat.get_response(UserMessage(content=prompt))
        
        return {
            "survey_questions": self._extract_list(response, "questions"),
            "validation_signals": self._extract_list(response, "validate"),
            "invalidation_signals": self._extract_list(response, "invalidate"),
            "sample_size": self._extract_text(response, "sample size"),
            "survey_design": response.content
        }
        
    async def _generate_interview_questions(self, hypothesis: str, context: Dict) -> Dict[str, Any]:
        """Generate customer interview questions"""
        prompt = f"""Design customer interview questions to validate this hypothesis:

Hypothesis: {hypothesis}
Interview Type: {context.get('interview_type', 'problem discovery')}

Create:
1. Open-ended questions that avoid leading the interviewee
2. Follow-up probes for deeper insights
3. Questions to uncover hidden pain points
4. Ways to measure problem severity"""

        response = await self.llm_chat.get_response(UserMessage(content=prompt))
        
        return {
            "primary_questions": self._extract_list(response, "questions"),
            "follow_up_probes": self._extract_list(response, "follow"),
            "pain_point_questions": self._extract_list(response, "pain"),
            "severity_measures": self._extract_list(response, "severity"),
            "interview_guide": response.content
        }
        
    async def _design_ab_test(self, hypothesis: str, context: Dict) -> Dict[str, Any]:
        """Design A/B test for hypothesis validation"""
        prompt = f"""Design an A/B test to validate this hypothesis:

Hypothesis: {hypothesis}
Test Duration: {context.get('duration', '2 weeks')}
Traffic Available: {context.get('traffic', 'unknown')}

Specify:
1. Control variant (A)
2. Test variant (B)
3. Primary success metric
4. Secondary metrics
5. Required sample size for statistical significance
6. Test implementation plan"""

        response = await self.llm_chat.get_response(UserMessage(content=prompt))
        
        return {
            "control_variant": self._extract_text(response, "control"),
            "test_variant": self._extract_text(response, "test variant"),
            "primary_metric": self._extract_text(response, "primary metric"),
            "secondary_metrics": self._extract_list(response, "secondary"),
            "sample_size": self._extract_text(response, "sample size"),
            "test_plan": response.content
        }
        
    async def _conduct_market_research(self, hypothesis: str, context: Dict) -> Dict[str, Any]:
        """Conduct general market research"""
        # This would integrate with real data sources in production
        # For now, we use LLM to simulate market research
        
        prompt = f"""Conduct market research to validate this hypothesis:

Hypothesis: {hypothesis}

Research:
1. Market trends supporting or refuting the hypothesis
2. Customer behavior patterns
3. Industry reports and statistics
4. Case studies of similar attempts
5. Expert opinions"""

        response = await self.llm_chat.get_response(UserMessage(content=prompt))
        
        return {
            "trends": self._extract_list(response, "trends"),
            "behavior_patterns": self._extract_list(response, "behavior"),
            "statistics": self._extract_list(response, "statistics"),
            "case_studies": self._extract_list(response, "case"),
            "expert_opinions": self._extract_list(response, "expert"),
            "research_summary": response.content
        }
        
    async def _analyze_validation_data(
        self, 
        hypothesis: str, 
        components: Dict[str, Any], 
        validation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze validation data and form conclusion"""
        
        # Use LLM to synthesize findings
        prompt = f"""Analyze the validation data and form a conclusion:

Hypothesis: {hypothesis}

Hypothesis Components:
{components}

Validation Data:
{validation_data}

Provide:
1. Clear conclusion: VALIDATED, INVALIDATED, or NEEDS MORE DATA
2. Confidence level (0-100%)
3. Key evidence points
4. Critical insights discovered
5. Recommended next steps"""

        response = await self.llm_chat.get_response(UserMessage(content=prompt))
        
        # Extract conclusion
        conclusion = "needs_more_data"
        if "VALIDATED" in response.content.upper():
            conclusion = "validated"
        elif "INVALIDATED" in response.content.upper():
            conclusion = "invalidated"
            
        # Extract confidence
        import re
        confidence_match = re.search(r'(\d+)%', response.content)
        confidence = int(confidence_match.group(1)) if confidence_match else 50
        
        return {
            "hypothesis": hypothesis,
            "status": conclusion,
            "confidence": confidence,
            "evidence": self._extract_list(response, "evidence"),
            "insights": self._extract_list(response, "insights"),
            "next_steps": self._extract_list(response, "next steps"),
            "validation_method": validation_data.get("method", "market_research"),
            "validation_date": datetime.utcnow().isoformat(),
            "full_analysis": response.content
        }
        
    async def _store_validation_results(self, hypothesis: str, analysis: Dict[str, Any]) -> None:
        """Store validation results in database"""
        try:
            # Store in a new validation_results table
            await self.supabase.table('validation_results').insert({
                'hypothesis': hypothesis,
                'status': analysis['status'],
                'confidence': analysis['confidence'],
                'evidence': analysis['evidence'],
                'insights': analysis['insights'],
                'next_steps': analysis['next_steps'],
                'validation_method': analysis['validation_method'],
                'full_analysis': analysis['full_analysis'],
                'created_at': datetime.utcnow().isoformat()
            }).execute()
        except Exception as e:
            logger.error(f"Failed to store validation results: {e}")
            
    async def _batch_validate(self, hypotheses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate multiple hypotheses in parallel"""
        tasks = []
        for hypothesis_data in hypotheses:
            task = self._validate_hypothesis(hypothesis_data)
            tasks.append(task)
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "hypothesis": hypotheses[i].get("hypothesis"),
                    "status": "error",
                    "error": str(result)
                })
            else:
                processed_results.append(result)
                
        return processed_results
        
    def _extract_list(self, response: Any, keyword: str) -> List[str]:
        """Extract list items from LLM response"""
        # Simple extraction - in production use structured parsing
        lines = response.content.split('\n')
        items = []
        capture = False
        
        for line in lines:
            if keyword.lower() in line.lower():
                capture = True
                continue
            if capture and line.strip().startswith(('-', '*', '•', '1', '2', '3')):
                items.append(line.strip().lstrip('-*•0123456789. '))
            elif capture and not line.strip():
                capture = False
                
        return items[:5]  # Limit to 5 items
        
    def _extract_text(self, response: Any, keyword: str) -> str:
        """Extract text value from LLM response"""
        lines = response.content.split('\n')
        for line in lines:
            if keyword.lower() in line.lower():
                # Extract value after colon or dash
                if ':' in line:
                    return line.split(':', 1)[1].strip()
                elif '-' in line:
                    return line.split('-', 1)[1].strip()
                    
        return "Not specified"