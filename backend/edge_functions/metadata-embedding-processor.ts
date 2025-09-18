"""
Supabase Edge Function: Metadata Embedding Processor
Listens to PostgreSQL notifications and generates embeddings for user metadata
Reference: aurum-life-impl-plan.md
"""

import { createClient } from '@supabase/supabase-js'
import OpenAI from 'openai'

const supabase = createClient(
  Deno.env.get('SUPABASE_URL')!,
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
)

const openai = new OpenAI({
  apiKey: Deno.env.get('OPENAI_API_KEY')!
})

interface EmbeddingPayload {
  table: string
  id: string
  user_id: string
  timestamp: string
}

interface EntityRecord {
  id: string
  user_id: string
  name: string
  description?: string
  title?: string
  content?: string
  [key: string]: any
}

Deno.serve(async (req) => {
  try {
    // Set up real-time listener for embedding queue
    const changes = supabase
      .channel('metadata_embedding_processor')
      .on('postgres_changes', 
          { event: '*', schema: 'public' }, 
          async (payload: any) => {
            console.log('Received embedding request:', payload)
            await processEmbeddingRequest(payload.new)
          })
      .subscribe()

    // Also handle direct HTTP requests for manual processing
    if (req.method === 'POST') {
      const payload = await req.json()
      await processEmbeddingRequest(payload)
      return new Response('Processing complete', { status: 200 })
    }

    return new Response('Embedding processor listening...', { status: 200 })
  } catch (error) {
    console.error('Edge function error:', error)
    return new Response(`Error: ${error.message}`, { status: 500 })
  }
})

async function processEmbeddingRequest(payload: EmbeddingPayload) {
  const { table, id, user_id, timestamp } = payload
  
  try {
    console.log(`Processing embedding for ${table}:${id}`)
    
    // Check user consent
    const { data: preferences } = await supabase
      .from('user_analytics_preferences')
      .select('record_rag_snippets')
      .eq('user_id', user_id)
      .single()
    
    if (preferences && !preferences.record_rag_snippets) {
      console.log(`User ${user_id} has not consented to RAG snippet recording`)
      await updateWebhookLog(user_id, table, 'skipped_no_consent')
      return
    }
    
    // Fetch the record from the appropriate table
    const record = await fetchEntityRecord(table, id)
    if (!record) {
      console.error(`Record not found: ${table}:${id}`)
      await updateWebhookLog(user_id, table, 'error', 'Record not found')
      return
    }
    
    // Generate text snippet based on table type
    const snippet = generateTextSnippet(table, record)
    if (!snippet || snippet.trim().length === 0) {
      console.warn(`No meaningful content for embedding: ${table}:${id}`)
      await updateWebhookLog(user_id, table, 'skipped_no_content')
      return
    }
    
    // Generate embedding using OpenAI
    console.log(`Generating embedding for snippet: "${snippet.substring(0, 100)}..."`)
    const embeddingResponse = await openai.embeddings.create({
      model: 'text-embedding-ada-002',
      input: snippet
    })
    
    if (!embeddingResponse.data?.[0]?.embedding) {
      throw new Error('No embedding returned from OpenAI')
    }
    
    const embedding = embeddingResponse.data[0].embedding
    
    // Check if embedding already exists for this entity
    const { data: existingEmbedding } = await supabase
      .from('user_metadata_embeddings')
      .select('id')
      .eq('user_id', user_id)
      .eq('domain_tag', table)
      .eq('entity_id', id)
      .single()
    
    if (existingEmbedding) {
      // Update existing embedding
      const { error: updateError } = await supabase
        .from('user_metadata_embeddings')
        .update({
          text_snippet: snippet,
          embedding: embedding,
          created_at: new Date().toISOString()
        })
        .eq('id', existingEmbedding.id)
      
      if (updateError) throw updateError
      console.log(`Updated existing embedding for ${table}:${id}`)
    } else {
      // Insert new embedding
      const { error: insertError } = await supabase
        .from('user_metadata_embeddings')
        .insert({
          user_id,
          domain_tag: table,
          entity_id: id,
          text_snippet: snippet,
          embedding: embedding
        })
      
      if (insertError) throw insertError
      console.log(`Created new embedding for ${table}:${id}`)
    }
    
    // Update webhook log with success
    await updateWebhookLog(user_id, table, 'completed')
    
  } catch (error) {
    console.error(`Error processing embedding for ${table}:${id}:`, error)
    await updateWebhookLog(user_id, table, 'error', error.message)
  }
}

async function fetchEntityRecord(table: string, id: string): Promise<EntityRecord | null> {
  const { data, error } = await supabase
    .from(table)
    .select('*')
    .eq('id', id)
    .single()
  
  if (error) {
    console.error(`Error fetching ${table}:${id}:`, error)
    return null
  }
  
  return data as EntityRecord
}

function generateTextSnippet(table: string, record: EntityRecord): string {
  let snippet = ''
  
  switch (table) {
    case 'pillars':
      snippet = `Pillar: ${record.name}`
      if (record.description) snippet += ` - ${record.description}`
      if (record.time_allocation_percentage) {
        snippet += ` (${record.time_allocation_percentage}% time allocation)`
      }
      break
      
    case 'areas':
      snippet = `Area: ${record.name}`
      if (record.description) snippet += ` - ${record.description}`
      if (record.importance) snippet += ` (Importance: ${record.importance}/5)`
      break
      
    case 'projects':
      snippet = `Project: ${record.name}`
      if (record.description) snippet += ` - ${record.description}`
      if (record.status) snippet += ` (Status: ${record.status})`
      if (record.priority) snippet += ` (Priority: ${record.priority})`
      break
      
    case 'tasks':
      snippet = `Task: ${record.name}`
      if (record.description) snippet += ` - ${record.description}`
      if (record.priority) snippet += ` (Priority: ${record.priority})`
      if (record.status) snippet += ` (Status: ${record.status})`
      if (record.due_date) {
        const dueDate = new Date(record.due_date).toLocaleDateString()
        snippet += ` (Due: ${dueDate})`
      }
      break
      
    case 'journal_entries':
      snippet = `Journal: ${record.title}`
      if (record.content) {
        // Limit content to first 500 characters for embedding
        const content = record.content.substring(0, 500)
        snippet += ` - ${content}${record.content.length > 500 ? '...' : ''}`
      }
      if (record.mood) snippet += ` (Mood: ${record.mood})`
      if (record.tags?.length > 0) snippet += ` (Tags: ${record.tags.join(', ')})`
      break
      
    default:
      console.warn(`Unknown table for snippet generation: ${table}`)
      if (record.name || record.title) {
        snippet = `${record.name || record.title}`
        if (record.description || record.content) {
          snippet += ` - ${(record.description || record.content).substring(0, 200)}`
        }
      }
  }
  
  return snippet.trim()
}

async function updateWebhookLog(userId: string, tableName: string, status: string, errorMessage?: string) {
  try {
    await supabase
      .from('webhook_logs')
      .update({
        status,
        error_message: errorMessage || null,
        processed_at: new Date().toISOString()
      })
      .eq('user_id', userId)
      .eq('table_name', tableName)
      .eq('webhook_type', 'metadata_embedding_queued')
      .eq('status', 'queued')
      .order('triggered_at', { ascending: false })
      .limit(1)
  } catch (error) {
    console.error('Error updating webhook log:', error)
  }
}