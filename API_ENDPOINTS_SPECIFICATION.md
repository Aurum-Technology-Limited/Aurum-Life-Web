# API Endpoints Specification - RAG & Behavioral Analytics
**Aurum Life Enhanced Backend API**

## 🚀 **RAG SYSTEM ENDPOINTS**

### **`GET /api/rag/search`**
Semantic search across user's complete PAPT hierarchy and journal entries.

**Parameters:**
- `query` (string, required): Search query text
- `domain_filters` (array, optional): Filter by entity types ['pillars', 'areas', 'projects', 'tasks', 'journal_entries']  
- `max_results` (integer, optional, default: 10): Maximum results to return
- `min_similarity` (float, optional, default: 0.7): Minimum similarity threshold

**Response:**
```json
{
  "results": [
    {
      "type": "metadata",
      "domain_tag": "tasks",
      "entity_id": "uuid",
      "text_snippet": "Task: Complete project proposal - Detailed task description...",
      "similarity_score": 0.892,
      "created_at": "2025-09-15T12:00:00Z"
    }
  ],
  "query": "project planning",
  "total_results": 5,
  "processing_time_ms": 45
}
```

### **`GET /api/rag/context-summary`**
Get user's context summary for AI prompt enhancement.

**Parameters:**
- `include_recent_activity` (boolean, optional, default: true)
- `activity_days` (integer, optional, default: 7)

**Response:**
```json
{
  "user_id": "uuid",
  "hierarchy_summary": {
    "pillars": 6,
    "areas": 12,
    "active_projects": 8,
    "pending_tasks": 23
  },
  "recent_activity": {
    "journal_entries_last_7_days": 5,
    "activity_period": "7 days"
  },
  "behavioral_patterns": {
    "avg_alignment_score": 0.85,
    "primary_focus_times": ["09:00-11:00", "14:00-16:00"],
    "most_productive_day": "Tuesday"
  },
  "generated_at": "2025-09-15T12:00:00Z"
}
```

---

## 📊 **BEHAVIORAL ANALYTICS ENDPOINTS**

### **`GET /api/analytics/behavioral-insights`**
Get comprehensive behavioral insights from materialized views.

**Parameters:**
- `time_range` (string, optional, default: "30d"): Time range for analysis
- `include_predictions` (boolean, optional, default: false): Include predictive insights

**Response:**
```json
{
  "pillar_alignment": [
    {
      "pillar_id": "uuid",
      "pillar_name": "Health & Fitness",
      "week_start": "2025-09-09",
      "avg_alignment": 0.87,
      "avg_sentiment": 0.74,
      "avg_habit_strength": 0.91,
      "data_points": 12,
      "trend": "improving"
    }
  ],
  "area_habits": [
    {
      "area_id": "uuid", 
      "area_name": "Exercise Routine",
      "strong_habits": 5,
      "moderate_habits": 2,
      "avg_alignment": 0.89,
      "avg_focus_time": 95
    }
  ],
  "flow_patterns": [
    {
      "flow_date": "2025-09-15",
      "flow_sessions": 3,
      "total_flow_minutes": 180,
      "procrastination_events": 2,
      "context_switches": 8
    }
  ],
  "task_completion": [
    {
      "energy_requirement": "high",
      "cognitive_load": "complex", 
      "completion_rate": 0.78,
      "avg_completion_hours": 2.4
    }
  ],
  "generated_at": "2025-09-15T12:00:00Z"
}
```

### **`POST /api/analytics/update-behavioral-metrics`**
Update behavioral metrics for pillars or areas.

**Request Body:**
```json
{
  "entity_type": "pillars", // or "areas"
  "entity_id": "uuid",
  "metrics": {
    "alignment_score": 0.85,
    "sentiment": 0.72,
    "habit_strength": 0.91,
    "energy_level": 0.68,
    "focus_time_minutes": 120
  }
}
```

**Response:**
```json
{
  "success": true,
  "updated_entity": "pillars",
  "entity_id": "uuid",
  "metrics_count": 15,
  "updated_at": "2025-09-15T12:00:00Z"
}
```

---

## 🧠 **AI INTEGRATION ENDPOINTS**

### **`POST /api/ai/rag-enhanced-chat`**
AI chat with RAG context integration.

**Request Body:**
```json
{
  "message": "Help me prioritize my tasks for tomorrow",
  "include_context": true,
  "context_domains": ["tasks", "projects", "journal_entries"],
  "max_context_items": 8
}
```

**Response:**
```json
{
  "response": "Based on your recent journal reflection about feeling overwhelmed, I recommend...",
  "context_used": [
    {
      "domain": "journal_entries", 
      "content": "Journal entry about workload...",
      "relevance": 0.89
    },
    {
      "domain": "tasks",
      "content": "High priority presentation task...", 
      "relevance": 0.84
    }
  ],
  "tokens_used": 1250,
  "processing_time_ms": 890
}
```

### **`GET /api/ai/recommendations`**
Get AI-powered recommendations based on RAG context.

**Parameters:**
- `recommendation_type` (string): 'task_prioritization', 'goal_alignment', 'habit_formation'
- `context_days` (integer, optional, default: 14): Days of context to analyze

**Response:**
```json
{
  "recommendations": [
    {
      "type": "task_prioritization",
      "entity_id": "uuid",
      "entity_type": "tasks",
      "title": "Complete project proposal",
      "reasoning": "Based on your journal entries about deadline stress and current pillar focus on career advancement",
      "confidence": 0.91,
      "supporting_context": [
        "Recent journal entry mentions project anxiety",
        "Career pillar has 85% alignment score", 
        "Task has high priority and approaching deadline"
      ]
    }
  ],
  "context_summary": {
    "entities_analyzed": 45,
    "behavioral_patterns": 12,
    "confidence_avg": 0.87
  }
}
```

---

## 🔍 **SYSTEM MONITORING ENDPOINTS**

### **`GET /api/system/rag-health`**
Monitor RAG system health and performance.

**Response:**
```json
{
  "system_status": "healthy",
  "embedding_stats": {
    "total_embeddings": 1247,
    "embeddings_by_domain": {
      "pillars": 24,
      "areas": 58, 
      "projects": 127,
      "tasks": 892,
      "journal_entries": 146
    },
    "last_generated": "2025-09-15T11:45:23Z"
  },
  "processing_stats": {
    "successful_webhooks": 1189,
    "failed_webhooks": 12,
    "success_rate": 0.989,
    "avg_processing_time_ms": 1250
  },
  "performance_metrics": {
    "avg_search_time_ms": 67,
    "cache_hit_rate": 0.34,
    "openai_api_health": "operational"
  }
}
```

### **`GET /api/system/behavioral-analytics-health`**
Monitor behavioral analytics system.

**Response:**
```json
{
  "analytics_status": "operational",
  "materialized_views": {
    "weekly_pillar_alignment": {
      "last_refresh": "2025-09-15T02:00:00Z",
      "row_count": 245,
      "refresh_duration_ms": 1890
    },
    "daily_flow_metrics": {
      "last_refresh": "2025-09-15T02:00:00Z", 
      "row_count": 89,
      "refresh_duration_ms": 567
    }
  },
  "behavioral_data_quality": {
    "users_with_metrics": 45,
    "avg_data_points_per_user": 23,
    "data_freshness_hours": 6
  }
}
```

---

## 🔧 **MAINTENANCE ENDPOINTS**

### **`POST /api/admin/refresh-analytics`** 
Manual refresh of materialized views (admin only).

### **`POST /api/admin/backfill-embeddings`**
Trigger embedding generation for entities without embeddings (admin only).

### **`GET /api/admin/system-stats`**
Comprehensive system statistics (admin only).

---

## 🔐 **AUTHENTICATION & PERMISSIONS**

### **Standard User Endpoints:**
- All RAG and behavioral analytics endpoints require valid JWT token
- User can only access their own data (RLS enforced)
- Privacy preferences respected automatically

### **Admin Endpoints:**
- Require admin token authentication
- Bypass RLS for system maintenance
- Full system monitoring and control capabilities

### **Privacy Controls:**
- User consent checked for all RAG operations
- Behavioral metrics respects analytics preferences
- Data retention policies automatically enforced
- Export/deletion endpoints for GDPR compliance

---

## ⚡ **PERFORMANCE SPECIFICATIONS**

### **Response Time Targets:**
- **RAG Search**: <100ms for semantic similarity
- **Behavioral Insights**: <200ms for 90-day analysis
- **Context Summary**: <50ms for user hierarchy
- **Analytics Refresh**: <5 minutes for complete views

### **Throughput Capacity:**
- **Embedding Generation**: 3000/minute (OpenAI limit)
- **Concurrent Users**: 1000+ with proper connection pooling
- **Vector Search**: 10,000+ embeddings without performance degradation
- **Analytics Queries**: Real-time response on materialized views

---

This API specification supports a complete RAG-enhanced personal productivity platform with enterprise-grade performance, security, and privacy controls.