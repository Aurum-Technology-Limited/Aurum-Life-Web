# RAG Implementation Guide for Aurum AI

## Overview

This guide details the implementation of Retrieval-Augmented Generation (RAG) using pgvector in Supabase for Aurum AI. RAG will enable contextual, personalized AI responses by retrieving relevant historical user data.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     RAG Pipeline Architecture                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. User Query → 2. Generate Embedding → 3. Vector Search       │
│                                              ↓                   │
│  6. AI Response ← 5. Generate Answer ← 4. Retrieve Context      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Key Benefits

1. **Contextual Understanding**: AI understands user's history, patterns, and preferences
2. **Semantic Search**: Find conceptually related content, not just keyword matches
3. **Memory Continuity**: AI remembers past conversations and insights
4. **Cross-Entity Intelligence**: Discover connections across pillars, areas, projects, and tasks

## Data Models for Vector Embeddings

### 1. **Journal Entries** (Highest Priority)
- **Why**: Rich, reflective content about user's thoughts, challenges, and progress
- **Embeddings**: Both title and content
- **Use Cases**: 
  - Finding similar past experiences
  - Understanding emotional patterns
  - Providing contextual advice

### 2. **Daily Reflections**
- **Why**: Tracks daily progress, mood, and accomplishments
- **Embeddings**: Reflection text, accomplishments, challenges
- **Use Cases**:
  - Pattern recognition over time
  - Mood-based recommendations
  - Progress tracking insights

### 3. **Tasks with Descriptions**
- **Why**: Contains approach strategies and implementation details
- **Embeddings**: Task names and descriptions
- **Use Cases**:
  - Finding similar tasks across projects
  - Suggesting proven approaches
  - Time estimation based on similar tasks

### 4. **Projects**
- **Why**: Strategic initiatives with goals and context
- **Embeddings**: Combined name + description
- **Use Cases**:
  - Strategic alignment analysis
  - Cross-project synergies
  - Resource allocation insights

### 5. **AI Conversation Memory** (New)
- **Why**: Maintains conversation continuity
- **Embeddings**: User messages and AI responses
- **Use Cases**:
  - Context-aware responses
  - Follow-up on previous discussions
  - Long-term relationship building

### 6. **AI Insights** (New)
- **Why**: Stores discovered patterns and recommendations
- **Embeddings**: Insight content
- **Use Cases**:
  - Surfacing relevant past insights
  - Building on previous discoveries
  - Tracking insight effectiveness

## Implementation Steps

### Phase 1: Infrastructure Setup

```sql
-- 1. Enable pgvector extension in Supabase
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Run the pgvector_rag_schema.sql script
-- This adds vector columns and indexes to existing tables
```

### Phase 2: Embedding Generation Service

```python
# backend/ai/embedding_service.py

import openai
from typing import List, Dict
import asyncio
from supabase import create_client

class EmbeddingService:
    def __init__(self):
        self.model = "text-embedding-3-small"  # 1536 dimensions, cost-effective
        self.batch_size = 100
        
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        response = await openai.Embedding.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding
    
    async def batch_generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts efficiently"""
        embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            response = await openai.Embedding.create(
                model=self.model,
                input=batch
            )
            embeddings.extend([e.embedding for e in response.data])
        return embeddings
    
    async def update_journal_embeddings(self, user_id: str):
        """Update embeddings for user's journal entries"""
        # Fetch journal entries without embeddings
        entries = await self.db.from_('journal_entries')\
            .select('id, title, content')\
            .eq('user_id', user_id)\
            .is_('content_embedding', None)\
            .execute()
        
        if not entries.data:
            return
        
        # Generate embeddings
        contents = [f"{e['title']}\n\n{e['content']}" for e in entries.data]
        embeddings = await self.batch_generate_embeddings(contents)
        
        # Update database
        for entry, embedding in zip(entries.data, embeddings):
            await self.db.from_('journal_entries')\
                .update({
                    'content_embedding': embedding,
                    'embedding_model': self.model,
                    'embedding_updated_at': 'now()'
                })\
                .eq('id', entry['id'])\
                .execute()
```

### Phase 3: RAG Query Service

```python
# backend/ai/rag_service.py

class RAGService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.context_window = 5  # Number of relevant documents to retrieve
        
    async def retrieve_context(self, query: str, user_id: str) -> Dict:
        """Retrieve relevant context for a query"""
        # Generate query embedding
        query_embedding = await self.embedding_service.generate_embedding(query)
        
        # Search across multiple tables using rag_search function
        results = await self.db.rpc('rag_search', {
            'query_embedding': query_embedding,
            'user_id_filter': user_id,
            'match_count': self.context_window,
            'date_range_days': 90  # Focus on recent 3 months
        }).execute()
        
        # Format context for LLM
        context = self._format_context(results.data)
        return {
            'context': context,
            'sources': results.data
        }
    
    def _format_context(self, results: List[Dict]) -> str:
        """Format retrieved documents for LLM context"""
        context_parts = []
        
        for doc in results:
            if doc['entity_type'] == 'journal_entry':
                context_parts.append(
                    f"Journal Entry ({doc['created_at'][:10]}): "
                    f"{doc['title']}\n{doc['content'][:200]}..."
                )
            elif doc['entity_type'] == 'task':
                context_parts.append(
                    f"Task: {doc['title']} "
                    f"(Status: {doc['metadata']['status']}, "
                    f"Priority: {doc['metadata']['priority']})\n"
                    f"{doc['content']}"
                )
            # Add other entity types...
        
        return "\n\n---\n\n".join(context_parts)
```

### Phase 4: Integration with AI Router

```python
# backend/ai/router.py (updated)

class AIRouter:
    def __init__(self):
        self.rag_service = RAGService()
        # ... existing initialization
    
    async def route_request(self, request: AIRequest) -> AIResponse:
        # Retrieve relevant context if needed
        if request.use_rag:
            rag_result = await self.rag_service.retrieve_context(
                query=request.content,
                user_id=request.user_id
            )
            
            # Enhance prompt with context
            enhanced_prompt = f"""
            Based on the following context from the user's history:
            
            {rag_result['context']}
            
            User's current question: {request.content}
            
            Please provide a personalized response that takes into account their history and patterns.
            """
            
            request.content = enhanced_prompt
            request.metadata['rag_sources'] = rag_result['sources']
        
        # Continue with existing routing logic
        complexity_score = await self.complexity_analyzer.analyze(request)
        # ...
```

## Best Practices

### 1. **Embedding Generation**
- Generate embeddings asynchronously in batches
- Use background jobs for bulk updates
- Cache embeddings for frequently accessed content

### 2. **Vector Search Optimization**
- Use HNSW indexes for faster similarity search
- Limit search scope with filters (date ranges, entity types)
- Pre-filter by user_id for security and performance

### 3. **Context Window Management**
- Retrieve 5-10 most relevant documents
- Prioritize recent content (last 90 days)
- Balance context size with token limits

### 4. **Privacy & Security**
- Always filter by user_id in vector searches
- Use RLS policies on all tables
- Don't mix embeddings across users

### 5. **Cost Optimization**
- Use `text-embedding-3-small` model (5x cheaper than ada-002)
- Batch embedding requests
- Only embed content-rich fields
- Set up embedding update schedules (not real-time)

## Monitoring & Metrics

### Key Metrics to Track
1. **Embedding Coverage**: % of content with embeddings
2. **Search Relevance**: User feedback on RAG results
3. **Query Performance**: Vector search latency
4. **Cost Metrics**: Embeddings API usage per user

### Implementation Timeline

**Week 1-2**: 
- Set up pgvector extension
- Implement embedding service
- Start with journal entries

**Week 3-4**:
- Add RAG search functionality
- Integrate with AI router
- Implement conversation memory

**Week 5-6**:
- Expand to all content types
- Optimize performance
- Add monitoring

## Expected Outcomes

1. **80% More Relevant Responses**: AI answers informed by user's history
2. **3x Better Task Suggestions**: Based on similar past tasks
3. **Improved User Retention**: AI "remembers" user journey
4. **Cross-Entity Insights**: Discover hidden patterns

## Cost Analysis

### Embedding Costs (OpenAI text-embedding-3-small)
- **Initial Backfill**: ~$0.02 per user (1000 items)
- **Ongoing**: ~$0.002 per user/month
- **Total RAG Cost**: < $0.05 per user/month

### Storage Costs (Supabase)
- **Vector Storage**: ~1MB per 1000 embeddings
- **Index Storage**: ~2MB per 1000 embeddings
- **Negligible for most use cases**

## Next Steps

1. Review and approve the schema changes
2. Deploy pgvector extension in Supabase
3. Implement embedding service
4. Start with journal entries as pilot
5. Gradually expand to other content types

---

This RAG implementation will transform Aurum AI from a stateless assistant to an intelligent companion that truly understands each user's journey.