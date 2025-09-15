"""
RAG (Retrieval Augmented Generation) Service
Handles semantic search across user's PAPT hierarchy and conversation memory
Reference: aurum-life-impl-plan.md
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import json
import uuid
from supabase import create_client, Client
from dotenv import load_dotenv
import openai
from pathlib import Path

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

logger = logging.getLogger(__name__)

class SupabaseRAGService:
    """RAG service for semantic search across user's personal data"""
    
    def __init__(self):
        self.supabase_url = os.environ.get('SUPABASE_URL')
        self.supabase_service_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        
        if not all([self.supabase_url, self.supabase_service_key, self.openai_api_key]):
            raise ValueError("Missing required environment variables for RAG service")
        
        self.supabase: Client = create_client(self.supabase_url, self.supabase_service_key)
        openai.api_key = self.openai_api_key
    
    async def get_relevant_context(self, user_id: str, query: str, 
                                 domain_filters: List[str] = None, 
                                 max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Get relevant context from user's PAPT hierarchy and conversation history
        using semantic similarity search
        
        Args:
            user_id: User identifier
            query: The search query to find relevant context for
            domain_filters: Optional list of domain tags to filter by ['pillar', 'area', 'project', 'task', 'journal_entry']
            max_results: Maximum number of results to return
            
        Returns:
            List of relevant context items with similarity scores
        """
        try:
            # Generate embedding for the query
            query_embedding = await self._generate_embedding(query)
            if not query_embedding:
                logger.error("Failed to generate embedding for query")
                return []
            
            # Search user metadata embeddings
            metadata_results = await self._search_metadata_embeddings(
                user_id, query_embedding, domain_filters, max_results // 2
            )
            
            # Search conversation memory
            conversation_results = await self._search_conversation_memory(
                user_id, query_embedding, max_results // 2
            )
            
            # Combine and rank results
            combined_results = self._combine_and_rank_results(
                metadata_results, conversation_results, max_results
            )
            
            logger.info(f"Retrieved {len(combined_results)} relevant context items for user {user_id}")
            return combined_results
            
        except Exception as e:
            logger.error(f"Error retrieving relevant context: {e}")
            return []
    
    async def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate OpenAI embedding for text"""
        try:
            response = await openai.Embedding.acreate(
                model="text-embedding-ada-002",
                input=text
            )
            return response['data'][0]['embedding']
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    async def _search_metadata_embeddings(self, user_id: str, query_embedding: List[float], 
                                        domain_filters: List[str] = None, 
                                        limit: int = 5) -> List[Dict[str, Any]]:
        """Search user's metadata embeddings using vector similarity"""
        try:
            # Build the RPC call for vector similarity search
            rpc_params = {
                'query_embedding': query_embedding,
                'p_user_id': user_id,
                'match_count': limit
            }
            
            if domain_filters:
                rpc_params['domain_tags'] = domain_filters
            
            # Use RPC function for efficient vector search
            response = self.supabase.rpc('search_metadata_embeddings', rpc_params).execute()
            
            results = []
            if response.data:
                for item in response.data:
                    results.append({
                        'type': 'metadata',
                        'domain_tag': item['domain_tag'],
                        'entity_id': item['entity_id'],
                        'text_snippet': item['text_snippet'],
                        'similarity_score': item['similarity'],
                        'created_at': item['created_at']
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching metadata embeddings: {e}")
            return []
    
    async def _search_conversation_memory(self, user_id: str, query_embedding: List[float], 
                                        limit: int = 5) -> List[Dict[str, Any]]:
        """Search conversation memory using vector similarity"""
        try:
            # Search recent conversation history (last 30 days)
            cutoff_date = datetime.now() - timedelta(days=30)
            
            response = self.supabase.rpc('search_conversation_memory', {
                'query_embedding': query_embedding,
                'p_user_id': user_id,
                'match_count': limit,
                'cutoff_date': cutoff_date.isoformat()
            }).execute()
            
            results = []
            if response.data:
                for item in response.data:
                    results.append({
                        'type': 'conversation',
                        'message_role': item['message_role'],
                        'message_content': item['message_content'],
                        'similarity_score': item['similarity'],
                        'conversation_date': item['conversation_date'],
                        'created_at': item['created_at']
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching conversation memory: {e}")
            return []
    
    def _combine_and_rank_results(self, metadata_results: List[Dict], 
                                conversation_results: List[Dict], 
                                max_results: int) -> List[Dict[str, Any]]:
        """Combine and rank results from different sources"""
        try:
            # Combine results
            all_results = metadata_results + conversation_results
            
            # Sort by similarity score (descending)
            all_results.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # Take top results
            top_results = all_results[:max_results]
            
            # Add ranking information
            for i, result in enumerate(top_results):
                result['rank'] = i + 1
                result['source'] = result['type']  # metadata or conversation
            
            return top_results
            
        except Exception as e:
            logger.error(f"Error combining and ranking results: {e}")
            return []
    
    async def store_conversation_context(self, user_id: str, role: str, content: str, 
                                       context_window: Dict = None) -> bool:
        """Store conversation context with embedding for future retrieval"""
        try:
            # Check user consent
            if not await self._check_user_consent(user_id, 'store_behavioral_embeddings'):
                logger.info(f"User {user_id} has not consented to behavioral embedding storage")
                return False
            
            # Generate embedding for the content
            embedding = await self._generate_embedding(content)
            if not embedding:
                return False
            
            # Store in conversation memory
            conversation_data = {
                'user_id': user_id,
                'conversation_date': datetime.now().date().isoformat(),
                'message_role': role,
                'message_content': content,
                'message_embedding': embedding,
                'context_window': context_window or {},
                'model_used': 'text-embedding-ada-002'
            }
            
            response = self.supabase.table('ai_conversation_memory').insert(conversation_data).execute()
            
            if response.data:
                logger.info(f"Stored conversation context for user {user_id}")
                return True
            else:
                logger.error("Failed to store conversation context")
                return False
            
        except Exception as e:
            logger.error(f"Error storing conversation context: {e}")
            return False
    
    async def get_behavioral_insights(self, user_id: str, 
                                    time_range: str = '30d') -> Dict[str, Any]:
        """Get behavioral insights from materialized views"""
        try:
            insights = {
                'pillar_alignment': await self._get_pillar_alignment(user_id, time_range),
                'area_habits': await self._get_area_habits(user_id),
                'flow_patterns': await self._get_flow_patterns(user_id, time_range),
                'task_completion': await self._get_task_completion_patterns(user_id)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting behavioral insights: {e}")
            return {}
    
    async def _get_pillar_alignment(self, user_id: str, time_range: str) -> List[Dict]:
        """Get pillar alignment data from materialized view"""
        try:
            days = int(time_range.replace('d', ''))
            cutoff_date = datetime.now() - timedelta(days=days)
            
            response = self.supabase.table('weekly_pillar_alignment').select('*').eq(
                'user_id', user_id
            ).gte('week_start', cutoff_date.date()).order('week_start', desc=True).execute()
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Error getting pillar alignment: {e}")
            return []
    
    async def _get_area_habits(self, user_id: str) -> List[Dict]:
        """Get area habit metrics from materialized view"""
        try:
            response = self.supabase.table('area_habit_metrics').select('*').eq(
                'user_id', user_id
            ).order('avg_alignment', desc=True).execute()
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Error getting area habits: {e}")
            return []
    
    async def _get_flow_patterns(self, user_id: str, time_range: str) -> List[Dict]:
        """Get flow state patterns from materialized view"""
        try:
            days = int(time_range.replace('d', ''))
            cutoff_date = datetime.now() - timedelta(days=days)
            
            response = self.supabase.table('daily_flow_metrics').select('*').eq(
                'user_id', user_id
            ).gte('flow_date', cutoff_date.date()).order('flow_date', desc=True).execute()
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Error getting flow patterns: {e}")
            return []
    
    async def _get_task_completion_patterns(self, user_id: str) -> List[Dict]:
        """Get task completion patterns from materialized view"""
        try:
            response = self.supabase.table('task_completion_patterns').select('*').eq(
                'user_id', user_id
            ).order('completion_rate', desc=True).limit(20).execute()
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Error getting task completion patterns: {e}")
            return []
    
    async def _check_user_consent(self, user_id: str, preference_name: str) -> bool:
        """Check if user has consented to specific data collection"""
        try:
            response = self.supabase.table('user_analytics_preferences').select(
                preference_name
            ).eq('user_id', user_id).single().execute()
            
            if response.data:
                return response.data.get(preference_name, True)  # Default to True
            return True  # Default to True if no preferences set
            
        except Exception as e:
            logger.error(f"Error checking user consent: {e}")
            return True  # Default to allowing if error occurs
    
    async def update_behavioral_metrics(self, user_id: str, entity_type: str, 
                                      entity_id: str, metrics: Dict[str, Any]) -> bool:
        """Update behavioral metrics for pillars/areas"""
        try:
            # Check user consent
            if not await self._check_user_consent(user_id, 'track_pillar_metrics'):
                return False
            
            if entity_type not in ['pillars', 'areas']:
                logger.error(f"Invalid entity type for behavioral metrics: {entity_type}")
                return False
            
            # Add timestamp to metrics
            timestamped_metrics = {
                **metrics,
                'timestamp': datetime.now().isoformat()
            }
            
            # Get current metrics
            response = self.supabase.table(entity_type).select(
                'behavior_metrics'
            ).eq('id', entity_id).eq('user_id', user_id).single().execute()
            
            if not response.data:
                logger.error(f"Entity not found: {entity_type}:{entity_id}")
                return False
            
            current_metrics = response.data.get('behavior_metrics', [])
            
            # Append new metrics (keep last 90 entries)
            current_metrics.append(timestamped_metrics)
            current_metrics = current_metrics[-90:]  # Keep last 90 entries
            
            # Update the entity
            update_response = self.supabase.table(entity_type).update({
                'behavior_metrics': current_metrics
            }).eq('id', entity_id).eq('user_id', user_id).execute()
            
            if update_response.data:
                logger.info(f"Updated behavioral metrics for {entity_type}:{entity_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating behavioral metrics: {e}")
            return False

# Global instance
rag_service = SupabaseRAGService()