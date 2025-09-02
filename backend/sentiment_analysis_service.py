"""
Sentiment Analysis Service for Aurum Life Emotional OS
Uses OpenAI GPT-5 nano for sophisticated emotional intelligence analysis
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta, date
from openai import OpenAI
from models import (
    SentimentAnalysisResult, 
    SentimentCategoryEnum, 
    SentimentTrendData,
    ActivitySentimentCorrelation,
    EmotionalInsight,
    EmotionalInsightTypeEnum
)
from supabase_client import get_supabase_client, find_documents, update_document
import asyncio

logger = logging.getLogger(__name__)

class SentimentAnalysisService:
    """GPT-5 nano powered sentiment analysis for emotional intelligence"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.supabase = get_supabase_client()
        self.model = "gpt-5-nano"
        
    async def analyze_journal_entry(self, user_id: str, entry_id: str, text: str, title: str = "") -> SentimentAnalysisResult:
        """
        Analyze sentiment of a journal entry using GPT-5 nano
        
        Args:
            user_id: User ID for context
            entry_id: Journal entry ID
            text: Journal entry content
            title: Journal entry title (optional)
            
        Returns:
            SentimentAnalysisResult with comprehensive emotional analysis
        """
        try:
            logger.info(f"🧠 Analyzing sentiment for entry {entry_id[:8]}...")
            
            # Construct analysis prompt
            analysis_prompt = self._build_sentiment_prompt(text, title)
            
            # Call GPT-5 nano for analysis
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_completion_tokens=400,  # GPT-5 nano uses max_completion_tokens
                response_format={"type": "json_object"}
            )
            
            # Parse response
            raw_content = response.choices[0].message.content
            logger.info(f"🔍 Raw GPT response: {raw_content}")
            
            try:
                analysis_data = json.loads(raw_content)
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON parsing failed: {e}")
                logger.error(f"Raw content: {raw_content}")
                # Fallback to neutral sentiment
                analysis_data = {
                    'sentiment_score': 0.0,
                    'confidence_score': 0.5,
                    'emotional_keywords': [],
                    'emotional_themes': [],
                    'dominant_emotions': [],
                    'emotional_intensity': 0.5,
                    'reasoning': f'JSON parsing failed: {str(e)}'
                }
            
            # Create sentiment result
            sentiment_result = SentimentAnalysisResult(
                sentiment_score=float(analysis_data.get('sentiment_score', 0.0)),
                sentiment_category=self._score_to_category(analysis_data.get('sentiment_score', 0.0)),
                confidence_score=float(analysis_data.get('confidence_score', 0.8)),
                emotional_keywords=analysis_data.get('emotional_keywords', []),
                emotional_themes=analysis_data.get('emotional_themes', []),
                reasoning=analysis_data.get('reasoning', ''),
                dominant_emotions=analysis_data.get('dominant_emotions', []),
                emotional_intensity=float(analysis_data.get('emotional_intensity', 0.5))
            )
            
            # Update journal entry with sentiment data
            await self._update_entry_sentiment(entry_id, sentiment_result)
            
            logger.info(f"✅ Sentiment analysis complete: {sentiment_result.sentiment_category} ({sentiment_result.sentiment_score:.2f})")
            return sentiment_result
            
        except Exception as e:
            logger.error(f"❌ Sentiment analysis failed for entry {entry_id}: {e}")
            # Return neutral sentiment on error
            return SentimentAnalysisResult(
                sentiment_score=0.0,
                sentiment_category=SentimentCategoryEnum.neutral,
                confidence_score=0.0,
                reasoning=f"Analysis failed: {str(e)}"
            )
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for sentiment analysis"""
        return """You are an expert emotional intelligence analyst for a personal growth application called Aurum Life. 

Your role is to analyze journal entries and personal reflections to provide deep emotional insights that help users understand their emotional patterns and achieve better life alignment.

ANALYSIS FRAMEWORK:
1. Sentiment Score: Rate emotional tone from -1.0 (very negative) to +1.0 (very positive)
2. Emotional Keywords: Extract 3-7 key emotional words/phrases
3. Emotional Themes: Identify 2-4 major emotional themes
4. Dominant Emotions: List 1-3 primary emotions expressed
5. Emotional Intensity: Rate intensity of emotional expression (0.0-1.0)
6. Reasoning: Explain your analysis in 1-2 sentences

RESPONSE FORMAT: Always respond with valid JSON containing:
{
  "sentiment_score": number (-1.0 to 1.0),
  "confidence_score": number (0.0 to 1.0),
  "emotional_keywords": ["word1", "word2", ...],
  "emotional_themes": ["theme1", "theme2", ...],
  "dominant_emotions": ["emotion1", "emotion2", ...],
  "emotional_intensity": number (0.0 to 1.0),
  "reasoning": "brief explanation"
}

EMOTIONAL INTELLIGENCE FOCUS:
- Look beyond surface-level positive/negative
- Identify complex emotional states (e.g., "hopeful anxiety", "grateful melancholy")
- Consider context of personal growth and life goals
- Detect emotional patterns that impact productivity and well-being
- Recognize emotional resilience and growth indicators"""

    def _build_sentiment_prompt(self, text: str, title: str = "") -> str:
        """Build the analysis prompt for GPT-5 nano"""
        prompt = f"""Analyze the emotional sentiment and psychological state expressed in this personal journal entry:

TITLE: {title}

CONTENT:
{text}

Provide a comprehensive emotional analysis focusing on:
1. Overall emotional tone and sentiment
2. Emotional complexity and nuance
3. Psychological indicators (stress, contentment, motivation, anxiety, etc.)
4. Personal growth signals (reflection, learning, goal alignment)
5. Emotional intensity and authenticity

Remember: This is personal reflective writing, so look for subtle emotional cues, internal conflicts, growth patterns, and authentic self-expression rather than just surface-level sentiment."""

        return prompt
    
    def _score_to_category(self, score: float) -> SentimentCategoryEnum:
        """Convert sentiment score to category"""
        if score >= 0.6:
            return SentimentCategoryEnum.very_positive
        elif score >= 0.2:
            return SentimentCategoryEnum.positive
        elif score >= -0.2:
            return SentimentCategoryEnum.neutral
        elif score >= -0.6:
            return SentimentCategoryEnum.negative
        else:
            return SentimentCategoryEnum.very_negative
    
    async def _update_entry_sentiment(self, entry_id: str, sentiment: SentimentAnalysisResult) -> bool:
        """Update journal entry with sentiment analysis results"""
        try:
            update_data = {
                'sentiment_score': sentiment.sentiment_score,
                'sentiment_category': sentiment.sentiment_category.value,
                'sentiment_confidence': sentiment.confidence_score,
                'emotional_keywords': sentiment.emotional_keywords,
                'emotional_themes': sentiment.emotional_themes,
                'dominant_emotions': sentiment.dominant_emotions,
                'emotional_intensity': sentiment.emotional_intensity,
                'sentiment_analysis_date': datetime.utcnow().isoformat(),
                'sentiment_analysis_version': '1.0'
            }
            
            result = self.supabase.table('journal_entries').update(update_data).eq('id', entry_id).execute()
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Failed to update entry sentiment: {e}")
            return False
    
    async def get_sentiment_trends(self, user_id: str, days: int = 30) -> List[SentimentTrendData]:
        """Get sentiment trends over time for insights dashboard"""
        try:
            # Calculate date range
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=days)
            
            # Get journal entries with sentiment data
            entries = self.supabase.table('journal_entries')\
                .select('*')\
                .eq('user_id', user_id)\
                .gte('created_at', start_date.isoformat())\
                .not_.is_('sentiment_score', 'null')\
                .execute()
            
            if not entries.data:
                return []
            
            # Group by date and calculate daily averages
            daily_sentiments = {}
            for entry in entries.data:
                entry_date = datetime.fromisoformat(entry['created_at'].replace('Z', '+00:00')).date()
                
                if entry_date not in daily_sentiments:
                    daily_sentiments[entry_date] = {
                        'scores': [],
                        'categories': [],
                        'keywords': []
                    }
                
                daily_sentiments[entry_date]['scores'].append(entry.get('sentiment_score', 0.0))
                daily_sentiments[entry_date]['categories'].append(entry.get('sentiment_category', 'neutral'))
                daily_sentiments[entry_date]['keywords'].extend(entry.get('emotional_keywords', []))
            
            # Convert to trend data
            trend_data = []
            for date_key, data in daily_sentiments.items():
                avg_sentiment = sum(data['scores']) / len(data['scores']) if data['scores'] else 0.0
                
                # Find most common category
                category_counts = {}
                for cat in data['categories']:
                    category_counts[cat] = category_counts.get(cat, 0) + 1
                dominant_category = max(category_counts, key=category_counts.get) if category_counts else 'neutral'
                
                # Get unique keywords
                unique_keywords = list(set(data['keywords']))[:5]  # Top 5 unique keywords
                
                trend_data.append(SentimentTrendData(
                    date=date_key,
                    average_sentiment=avg_sentiment,
                    entry_count=len(data['scores']),
                    dominant_category=SentimentCategoryEnum(dominant_category),
                    emotional_keywords=unique_keywords
                ))
            
            # Sort by date
            trend_data.sort(key=lambda x: x.date)
            return trend_data
            
        except Exception as e:
            logger.error(f"Failed to get sentiment trends: {e}")
            return []
    
    async def analyze_activity_sentiment_correlation(self, user_id: str, days: int = 30) -> List[ActivitySentimentCorrelation]:
        """Analyze correlation between activities (pillars/areas/projects) and emotional outcomes"""
        try:
            logger.info(f"📊 Analyzing activity-sentiment correlations for user {user_id[:8]}...")
            
            # Get sentiment data and activity data
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=days)
            
            # Get journal entries with sentiment scores
            entries = self.supabase.table('journal_entries')\
                .select('*')\
                .eq('user_id', user_id)\
                .gte('created_at', start_date.isoformat())\
                .not_.is_('sentiment_score', 'null')\
                .execute()
            
            # Get completed tasks in the same period
            tasks = self.supabase.table('tasks')\
                .select('*, projects(*)')\
                .eq('user_id', user_id)\
                .eq('completed', True)\
                .gte('completed_at', start_date.isoformat())\
                .execute()
            
            if not entries.data or not tasks.data:
                return []
            
            # Build correlation analysis using GPT-5 nano
            correlation_prompt = self._build_correlation_prompt(entries.data, tasks.data)
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_correlation_system_prompt()},
                    {"role": "user", "content": correlation_prompt}
                ],
                max_completion_tokens=600,  # GPT-5 nano uses max_completion_tokens
                response_format={"type": "json_object"}
            )
            
            # Parse correlation results
            correlations_data = json.loads(response.choices[0].message.content)
            
            # Convert to ActivitySentimentCorrelation objects
            correlations = []
            for item in correlations_data.get('correlations', []):
                correlations.append(ActivitySentimentCorrelation(
                    activity_type=item.get('activity_type', 'project'),
                    activity_id=item.get('activity_id', ''),
                    activity_name=item.get('activity_name', ''),
                    average_sentiment=float(item.get('average_sentiment', 0.0)),
                    entry_count=int(item.get('entry_count', 0)),
                    sentiment_trend=item.get('sentiment_trend', []),
                    emotional_impact_score=float(item.get('emotional_impact_score', 0.5)),
                    insights=item.get('insights', [])
                ))
            
            logger.info(f"✅ Found {len(correlations)} activity-sentiment correlations")
            return correlations
            
        except Exception as e:
            logger.error(f"Failed to analyze activity-sentiment correlation: {e}")
            return []
    
    def _get_correlation_system_prompt(self) -> str:
        """System prompt for activity-sentiment correlation analysis"""
        return """You are an expert at analyzing correlations between activities and emotional outcomes for personal growth insights.

Your task is to identify patterns between completed tasks/projects and emotional states expressed in journal entries.

CORRELATION ANALYSIS FOCUS:
1. Identify which activities (projects, tasks) correlate with positive/negative emotional outcomes
2. Look for patterns in emotional responses to different types of work
3. Detect activities that consistently boost or drain emotional energy
4. Provide actionable insights about emotional impact of activities

RESPONSE FORMAT: Always respond with valid JSON:
{
  "correlations": [
    {
      "activity_type": "project|area|pillar",
      "activity_id": "id",
      "activity_name": "name",
      "average_sentiment": number (-1.0 to 1.0),
      "entry_count": number,
      "sentiment_trend": [recent scores],
      "emotional_impact_score": number (0.0 to 1.0),
      "insights": ["insight1", "insight2"]
    }
  ]
}"""

    def _build_correlation_prompt(self, entries: List[Dict], tasks: List[Dict]) -> str:
        """Build prompt for activity-sentiment correlation analysis"""
        entries_summary = []
        for entry in entries[:10]:  # Limit to recent entries
            entries_summary.append({
                'date': entry.get('created_at', '')[:10],
                'sentiment_score': entry.get('sentiment_score', 0.0),
                'emotional_keywords': entry.get('emotional_keywords', []),
                'title': entry.get('title', '')
            })
        
        tasks_summary = []
        for task in tasks[:20]:  # Limit to recent tasks
            project_name = task.get('projects', {}).get('name', 'Unknown') if task.get('projects') else 'Unknown'
            tasks_summary.append({
                'task_name': task.get('name', ''),
                'project_name': project_name,
                'completed_at': task.get('completed_at', '')[:10] if task.get('completed_at') else '',
                'priority': task.get('priority', 'medium')
            })
        
        return f"""Analyze the correlation between completed activities and emotional outcomes:

RECENT JOURNAL ENTRIES WITH SENTIMENT:
{json.dumps(entries_summary, indent=2)}

COMPLETED TASKS/PROJECTS:
{json.dumps(tasks_summary, indent=2)}

Identify patterns between:
1. Which projects/tasks correlate with positive emotional states
2. Which activities may be emotionally draining
3. Emotional impact of different types of work
4. Actionable insights for better emotional outcomes

Focus on finding meaningful correlations that can guide the user toward emotionally fulfilling activities."""

    async def generate_emotional_insights(self, user_id: str, days: int = 30) -> List[EmotionalInsight]:
        """Generate AI-powered emotional insights based on sentiment patterns"""
        try:
            logger.info(f"🔮 Generating emotional insights for user {user_id[:8]}...")
            
            # Get recent sentiment trends
            trends = await self.get_sentiment_trends(user_id, days)
            
            if not trends:
                return []
            
            # Build insights prompt
            insights_prompt = self._build_insights_prompt(trends)
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_insights_system_prompt()},
                    {"role": "user", "content": insights_prompt}
                ],
                max_completion_tokens=500,  # GPT-5 nano uses max_completion_tokens
                response_format={"type": "json_object"}
            )
            
            insights_data = json.loads(response.choices[0].message.content)
            
            # Convert to EmotionalInsight objects
            insights = []
            for insight_item in insights_data.get('insights', []):
                insight = EmotionalInsight(
                    user_id=user_id,
                    insight_type=EmotionalInsightTypeEnum(insight_item.get('type', 'emotional_pattern')),
                    title=insight_item.get('title', ''),
                    description=insight_item.get('description', ''),
                    insight_data=insight_item.get('data', {}),
                    confidence_score=float(insight_item.get('confidence', 0.8)),
                    date_range_start=datetime.utcnow() - timedelta(days=days),
                    date_range_end=datetime.utcnow(),
                    actionable_suggestions=insight_item.get('suggestions', [])
                )
                insights.append(insight)
            
            logger.info(f"✅ Generated {len(insights)} emotional insights")
            return insights
            
        except Exception as e:
            logger.error(f"Failed to generate emotional insights: {e}")
            return []
    
    def _get_insights_system_prompt(self) -> str:
        """System prompt for emotional insights generation"""
        return """You are an empathetic AI coach specializing in emotional intelligence and personal growth insights.

Analyze emotional patterns from journal sentiment data to provide actionable insights that help users:
1. Understand their emotional patterns
2. Identify triggers for positive/negative emotions  
3. Optimize activities for better emotional outcomes
4. Build emotional resilience and awareness

INSIGHT TYPES:
- trend_analysis: Emotional trends over time
- activity_correlation: Connection between activities and emotions
- emotional_pattern: Recurring emotional patterns
- mood_prediction: Predictive insights about mood
- wellness_alert: Emotional wellness concerns

RESPONSE FORMAT: Always respond with valid JSON:
{
  "insights": [
    {
      "type": "insight_type",
      "title": "Brief insight title",
      "description": "Detailed insight description",
      "confidence": number (0.0 to 1.0),
      "data": {"key": "value"},
      "suggestions": ["actionable suggestion 1", "suggestion 2"]
    }
  ]
}"""

    def _build_insights_prompt(self, trends: List[SentimentTrendData]) -> str:
        """Build prompt for emotional insights generation"""
        trends_data = []
        for trend in trends:
            trends_data.append({
                'date': trend.date.isoformat(),
                'sentiment': trend.average_sentiment,
                'category': trend.dominant_category.value,
                'entries': trend.entry_count,
                'keywords': trend.emotional_keywords
            })
        
        return f"""Analyze these emotional trends and provide personalized insights:

SENTIMENT TRENDS (Last {len(trends)} days):
{json.dumps(trends_data, indent=2)}

Generate 2-4 meaningful insights about:
1. Emotional patterns and trends
2. Potential triggers or correlations
3. Emotional wellness observations
4. Actionable suggestions for emotional growth

Focus on patterns that can help the user improve their emotional well-being and life alignment."""

    async def get_emotional_wellness_score(self, user_id: str, days: int = 30) -> float:
        """Calculate overall emotional wellness score (0-100)"""
        try:
            trends = await self.get_sentiment_trends(user_id, days)
            
            if not trends:
                return 50.0  # Neutral baseline
            
            # Calculate wellness based on multiple factors
            sentiment_scores = [t.average_sentiment for t in trends]
            consistency_scores = []
            
            # Calculate consistency (less volatility = better wellness)
            if len(sentiment_scores) > 1:
                volatility = sum(abs(sentiment_scores[i] - sentiment_scores[i-1]) 
                               for i in range(1, len(sentiment_scores))) / (len(sentiment_scores) - 1)
                consistency_score = max(0, 1 - volatility)  # Lower volatility = higher consistency
            else:
                consistency_score = 1.0
            
            # Calculate average sentiment (normalized to 0-1)
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
            normalized_sentiment = (avg_sentiment + 1) / 2  # Convert -1,1 to 0,1
            
            # Calculate frequency score (more entries = better engagement)
            frequency_score = min(1.0, len(trends) / (days * 0.5))  # Target: entry every 2 days
            
            # Weighted wellness score
            wellness_score = (
                normalized_sentiment * 0.5 +      # 50% weight on average sentiment
                consistency_score * 0.3 +         # 30% weight on emotional stability  
                frequency_score * 0.2             # 20% weight on engagement
            ) * 100
            
            return min(100.0, max(0.0, wellness_score))
            
        except Exception as e:
            logger.error(f"Failed to calculate wellness score: {e}")
            return 50.0
    
    @staticmethod
    def get_sentiment_emoji(category: SentimentCategoryEnum) -> str:
        """Get emoji representation for sentiment category"""
        emoji_map = {
            SentimentCategoryEnum.very_positive: "😄",
            SentimentCategoryEnum.positive: "😊", 
            SentimentCategoryEnum.neutral: "😐",
            SentimentCategoryEnum.negative: "😞",
            SentimentCategoryEnum.very_negative: "😢"
        }
        return emoji_map.get(category, "😐")
    
    @staticmethod
    def get_sentiment_color(category: SentimentCategoryEnum) -> str:
        """Get color representation for sentiment category"""
        color_map = {
            SentimentCategoryEnum.very_positive: "#10B981",  # Green
            SentimentCategoryEnum.positive: "#34D399",       # Light green
            SentimentCategoryEnum.neutral: "#6B7280",        # Gray
            SentimentCategoryEnum.negative: "#F59E0B",       # Orange
            SentimentCategoryEnum.very_negative: "#EF4444"   # Red
        }
        return color_map.get(category, "#6B7280")
    
    async def bulk_analyze_existing_entries(self, user_id: str, limit: int = 50) -> Dict[str, Any]:
        """Analyze sentiment for existing journal entries that don't have sentiment scores"""
        try:
            logger.info(f"🔄 Starting bulk sentiment analysis for user {user_id[:8]}...")
            
            # Get unanalyzed entries
            entries = self.supabase.table('journal_entries')\
                .select('*')\
                .eq('user_id', user_id)\
                .is_('sentiment_score', 'null')\
                .order('created_at', desc=True)\
                .limit(limit)\
                .execute()
            
            if not entries.data:
                return {"analyzed": 0, "message": "No entries need analysis"}
            
            analyzed_count = 0
            failed_count = 0
            
            # Analyze each entry (with rate limiting)
            for entry in entries.data:
                try:
                    await self.analyze_journal_entry(
                        user_id, 
                        entry['id'], 
                        entry['content'], 
                        entry.get('title', '')
                    )
                    analyzed_count += 1
                    
                    # Rate limiting - small delay between requests
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.warning(f"Failed to analyze entry {entry['id']}: {e}")
                    failed_count += 1
            
            logger.info(f"✅ Bulk analysis complete: {analyzed_count} analyzed, {failed_count} failed")
            
            return {
                "analyzed": analyzed_count,
                "failed": failed_count,
                "total": len(entries.data),
                "message": f"Successfully analyzed {analyzed_count} entries"
            }
            
        except Exception as e:
            logger.error(f"Bulk sentiment analysis failed: {e}")
            return {"analyzed": 0, "failed": 0, "error": str(e)}