-- HRM Phase 3: AI Conversation Memory for Context Preservation
-- Reference: RAG_IMPLEMENTATION_GUIDE.md

-- Store AI conversation history with embeddings
CREATE TABLE IF NOT EXISTS public.ai_conversation_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    conversation_date DATE NOT NULL DEFAULT CURRENT_DATE,
    message_role TEXT NOT NULL CHECK (message_role IN ('user', 'assistant', 'system')),
    message_content TEXT NOT NULL,
    message_embedding vector(1536),
    context_window JSONB DEFAULT '{}',
    tokens_used INTEGER DEFAULT 0,
    model_used TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for conversation retrieval and similarity search
CREATE INDEX IF NOT EXISTS idx_conversation_embedding 
ON ai_conversation_memory 
USING hnsw (message_embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

CREATE INDEX IF NOT EXISTS idx_conversation_user_date 
ON ai_conversation_memory (user_id, conversation_date DESC);

-- Row Level Security
ALTER TABLE ai_conversation_memory ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage their own AI conversations" 
ON ai_conversation_memory FOR ALL USING (auth.uid() = user_id);