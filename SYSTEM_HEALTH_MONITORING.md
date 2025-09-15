# System Health Monitoring Guide
**Aurum Life RAG + Behavioral Analytics Monitoring**

## 🎯 **MONITORING OVERVIEW**

This guide provides comprehensive monitoring procedures for the Aurum Life RAG + Behavioral Analytics system, ensuring optimal performance, data integrity, and user experience.

---

## 📊 **KEY PERFORMANCE INDICATORS (KPIs)**

### **Core System Health Metrics:**

#### **1. Embedding Generation Performance**
```sql
-- Success rate monitoring (should be >95%)
SELECT 
  DATE(triggered_at) as date,
  COUNT(*) as total_requests,
  COUNT(*) FILTER (WHERE status = 'completed') as successful,
  COUNT(*) FILTER (WHERE status = 'error') as failed,
  ROUND(COUNT(*) FILTER (WHERE status = 'completed') * 100.0 / COUNT(*), 2) as success_rate
FROM webhook_logs 
WHERE webhook_type = 'metadata_embedding_queued'
  AND triggered_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE(triggered_at)
ORDER BY date DESC;
```

#### **2. Vector Search Performance**
```sql
-- Query performance analysis (should be <100ms)
EXPLAIN (ANALYZE, BUFFERS, TIMING) 
SELECT domain_tag, text_snippet, 1 - (embedding <=> $1) as similarity
FROM user_metadata_embeddings 
WHERE user_id = $2 
ORDER BY embedding <=> $1 
LIMIT 10;
```

#### **3. Behavioral Analytics Freshness**
```sql
-- Materialized view refresh status
SELECT 
  schemaname,
  matviewname,
  ispopulated,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||matviewname)) as size
FROM pg_matviews 
WHERE schemaname = 'public'
ORDER BY matviewname;

-- Last refresh timing
SELECT 
  webhook_type,
  MAX(processed_at) as last_refresh,
  EXTRACT(EPOCH FROM (NOW() - MAX(processed_at))) / 3600 as hours_since_refresh
FROM webhook_logs 
WHERE webhook_type = 'materialized_views_refresh'
GROUP BY webhook_type;
```

---

## 🚨 **ALERT THRESHOLDS**

### **Critical Alerts (Immediate Action Required):**

#### **Embedding Generation Failure Rate >5%**
```sql
-- Check recent embedding failures
SELECT 
  COUNT(*) FILTER (WHERE status = 'error') as failures,
  COUNT(*) as total_attempts,
  ROUND(COUNT(*) FILTER (WHERE status = 'error') * 100.0 / COUNT(*), 2) as failure_rate
FROM webhook_logs 
WHERE webhook_type = 'metadata_embedding_queued'
  AND triggered_at >= NOW() - INTERVAL '1 hour';
```

#### **Vector Search Performance >200ms**
```sql
-- Monitor slow queries (setup via pg_stat_statements)
SELECT 
  query,
  calls,
  total_time,
  mean_time,
  stddev_time
FROM pg_stat_statements 
WHERE query LIKE '%user_metadata_embeddings%'
  AND mean_time > 200
ORDER BY mean_time DESC;
```

#### **Materialized View Refresh Failure**
```sql
-- Check view refresh failures
SELECT * FROM webhook_logs 
WHERE webhook_type = 'materialized_views_refresh'
  AND status = 'error'
  AND triggered_at >= NOW() - INTERVAL '24 hours';
```

### **Warning Alerts (Monitor Closely):**

#### **Edge Function Response Time >5 seconds**
```sql
-- Monitor Edge Function processing delays
SELECT 
  table_name,
  AVG(EXTRACT(EPOCH FROM (processed_at - triggered_at))) as avg_processing_seconds,
  MAX(EXTRACT(EPOCH FROM (processed_at - triggered_at))) as max_processing_seconds,
  COUNT(*) as processed_count
FROM webhook_logs 
WHERE webhook_type = 'metadata_embedding_queued'
  AND status = 'completed'
  AND triggered_at >= NOW() - INTERVAL '24 hours'
GROUP BY table_name;
```

#### **OpenAI API Error Rate >2%**
```sql
-- Monitor OpenAI integration health
SELECT 
  COUNT(*) FILTER (WHERE error_message LIKE '%OpenAI%') as openai_errors,
  COUNT(*) as total_processed,
  ROUND(COUNT(*) FILTER (WHERE error_message LIKE '%OpenAI%') * 100.0 / COUNT(*), 2) as error_rate
FROM webhook_logs 
WHERE webhook_type = 'metadata_embedding_queued'
  AND status = 'error'
  AND triggered_at >= NOW() - INTERVAL '24 hours';
```

---

## 📈 **PERFORMANCE MONITORING**

### **Database Performance:**

#### **Connection Monitoring:**
```sql
-- Active connections
SELECT 
  state,
  COUNT(*) as connection_count,
  AVG(EXTRACT(EPOCH FROM (NOW() - state_change))) as avg_duration_seconds
FROM pg_stat_activity 
WHERE datname = current_database()
GROUP BY state;

-- Long-running queries
SELECT 
  pid,
  user_name,
  state,
  query_start,
  EXTRACT(EPOCH FROM (NOW() - query_start)) as duration_seconds,
  LEFT(query, 100) as query_preview
FROM pg_stat_activity 
WHERE state = 'active' 
  AND query_start < NOW() - INTERVAL '30 seconds'
ORDER BY query_start;
```

#### **Index Efficiency:**
```sql
-- HNSW vector index usage
SELECT 
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE indexname LIKE '%hnsw%' OR indexname LIKE '%embedding%';

-- JSONB index efficiency  
SELECT 
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read
FROM pg_stat_user_indexes 
WHERE indexname LIKE '%behavior_metrics%';
```

### **Storage Monitoring:**

#### **Table Growth Analysis:**
```sql
-- Monitor table size growth
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
  pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as index_size
FROM pg_tables 
WHERE schemaname = 'public'
  AND tablename IN ('user_metadata_embeddings', 'user_behavior_events', 'webhook_logs', 'pillars', 'areas', 'projects', 'tasks')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

#### **Embedding Storage Efficiency:**
```sql
-- Embedding distribution and storage analysis
SELECT 
  domain_tag,
  COUNT(*) as embedding_count,
  AVG(LENGTH(text_snippet)) as avg_snippet_length,
  MIN(created_at) as first_created,
  MAX(created_at) as last_created,
  EXTRACT(EPOCH FROM (MAX(created_at) - MIN(created_at))) / 86400 as days_span
FROM user_metadata_embeddings 
GROUP BY domain_tag
ORDER BY embedding_count DESC;
```

---

## 🔍 **DATA QUALITY MONITORING**

### **Behavioral Metrics Quality:**

#### **Data Completeness:**
```sql
-- Check behavioral metrics data quality
SELECT 
  'pillars' as entity_type,
  COUNT(*) as total_entities,
  COUNT(*) FILTER (WHERE behavior_metrics != '[]'::jsonb) as entities_with_metrics,
  ROUND(COUNT(*) FILTER (WHERE behavior_metrics != '[]'::jsonb) * 100.0 / COUNT(*), 2) as coverage_percentage
FROM pillars
UNION ALL
SELECT 
  'areas',
  COUNT(*),
  COUNT(*) FILTER (WHERE behavior_metrics != '[]'::jsonb),
  ROUND(COUNT(*) FILTER (WHERE behavior_metrics != '[]'::jsonb) * 100.0 / COUNT(*), 2)
FROM areas;

-- Metrics data distribution
SELECT 
  domain_tag,
  jsonb_array_length(behavior_metrics) as metric_points,
  COUNT(*) as entity_count
FROM (
  SELECT 'pillars' as domain_tag, behavior_metrics FROM pillars WHERE behavior_metrics != '[]'::jsonb
  UNION ALL
  SELECT 'areas', behavior_metrics FROM areas WHERE behavior_metrics != '[]'::jsonb
) metrics_data
GROUP BY domain_tag, jsonb_array_length(behavior_metrics)
ORDER BY domain_tag, metric_points;
```

#### **Analytics View Integrity:**
```sql
-- Verify materialized view data integrity
SELECT 
  'weekly_pillar_alignment' as view_name,
  COUNT(*) as row_count,
  COUNT(DISTINCT user_id) as unique_users,
  MIN(week_start) as earliest_week,
  MAX(week_start) as latest_week
FROM weekly_pillar_alignment
UNION ALL
SELECT 
  'area_habit_metrics',
  COUNT(*),
  COUNT(DISTINCT user_id),
  MIN(calculated_date),
  MAX(calculated_date)
FROM area_habit_metrics;
```

---

## 🔄 **AUTOMATED HEALTH CHECKS**

### **Scheduled Health Monitoring:**
```sql
-- Create comprehensive health check function
CREATE OR REPLACE FUNCTION system_health_check()
RETURNS JSON AS $$
DECLARE
  health_report JSON;
  embedding_success_rate NUMERIC;
  recent_errors INTEGER;
  search_performance TEXT;
  view_freshness INTERVAL;
BEGIN
  -- Calculate embedding success rate (last 24 hours)
  SELECT 
    COALESCE(
      COUNT(*) FILTER (WHERE status = 'completed') * 100.0 / NULLIF(COUNT(*), 0),
      100
    )
  INTO embedding_success_rate
  FROM webhook_logs 
  WHERE webhook_type = 'metadata_embedding_queued'
    AND triggered_at >= NOW() - INTERVAL '24 hours';
  
  -- Count recent errors
  SELECT COUNT(*) INTO recent_errors
  FROM webhook_logs 
  WHERE status = 'error' 
    AND triggered_at >= NOW() - INTERVAL '1 hour';
  
  -- Check view freshness
  SELECT NOW() - MAX(processed_at) INTO view_freshness
  FROM webhook_logs 
  WHERE webhook_type = 'materialized_views_refresh';
  
  -- Determine search performance status
  search_performance := CASE 
    WHEN embedding_success_rate >= 95 THEN 'excellent'
    WHEN embedding_success_rate >= 90 THEN 'good'
    WHEN embedding_success_rate >= 80 THEN 'degraded'
    ELSE 'critical'
  END;
  
  -- Build health report
  health_report := json_build_object(
    'overall_status', CASE 
      WHEN embedding_success_rate >= 95 AND recent_errors = 0 THEN 'healthy'
      WHEN embedding_success_rate >= 90 AND recent_errors <= 5 THEN 'warning'
      ELSE 'critical'
    END,
    'embedding_system', json_build_object(
      'success_rate', embedding_success_rate,
      'status', search_performance,
      'recent_errors', recent_errors
    ),
    'analytics_system', json_build_object(
      'view_freshness_hours', EXTRACT(EPOCH FROM view_freshness) / 3600,
      'status', CASE WHEN view_freshness < INTERVAL '25 hours' THEN 'fresh' ELSE 'stale' END
    ),
    'storage_metrics', json_build_object(
      'total_embeddings', (SELECT COUNT(*) FROM user_metadata_embeddings),
      'total_users_with_rag', (SELECT COUNT(DISTINCT user_id) FROM user_metadata_embeddings)
    ),
    'generated_at', NOW()
  );
  
  RETURN health_report;
END;
$$ LANGUAGE plpgsql;

-- Schedule health checks
SELECT cron.schedule(
  'system-health-check',
  '*/15 * * * *', -- Every 15 minutes
  'SELECT system_health_check();'
);
```

### **Critical Error Detection:**
```sql
-- Function to detect and alert on critical issues
CREATE OR REPLACE FUNCTION detect_critical_issues()
RETURNS TEXT AS $$
DECLARE
  issues TEXT[] := ARRAY[]::TEXT[];
  embedding_failures INTEGER;
  search_errors INTEGER;
  view_staleness INTERVAL;
BEGIN
  -- Check embedding failures
  SELECT COUNT(*) INTO embedding_failures
  FROM webhook_logs 
  WHERE webhook_type = 'metadata_embedding_queued'
    AND status = 'error'
    AND triggered_at >= NOW() - INTERVAL '1 hour';
  
  IF embedding_failures > 10 THEN
    issues := array_append(issues, 'High embedding failure rate: ' || embedding_failures || ' failures in last hour');
  END IF;
  
  -- Check view staleness
  SELECT NOW() - MAX(processed_at) INTO view_staleness
  FROM webhook_logs 
  WHERE webhook_type = 'materialized_views_refresh';
  
  IF view_staleness > INTERVAL '25 hours' THEN
    issues := array_append(issues, 'Materialized views stale: ' || view_staleness::TEXT);
  END IF;
  
  -- Return consolidated issues
  IF array_length(issues, 1) > 0 THEN
    RETURN array_to_string(issues, '; ');
  ELSE
    RETURN 'No critical issues detected';
  END IF;
END;
$$ LANGUAGE plpgsql;
```

---

## 🔍 **OPERATIONAL MONITORING QUERIES**

### **Daily Operations Dashboard:**

#### **System Overview:**
```sql
-- Daily system status summary
WITH daily_stats AS (
  SELECT 
    DATE(NOW()) as check_date,
    (SELECT COUNT(*) FROM user_metadata_embeddings) as total_embeddings,
    (SELECT COUNT(DISTINCT user_id) FROM user_metadata_embeddings) as users_with_rag,
    (SELECT COUNT(*) FROM webhook_logs WHERE triggered_at >= NOW() - INTERVAL '24 hours') as daily_webhooks,
    (SELECT COUNT(*) FROM webhook_logs WHERE status = 'completed' AND triggered_at >= NOW() - INTERVAL '24 hours') as successful_webhooks
)
SELECT 
  *,
  ROUND(successful_webhooks * 100.0 / NULLIF(daily_webhooks, 0), 2) as daily_success_rate
FROM daily_stats;
```

#### **User Engagement Metrics:**
```sql
-- User activity and RAG usage
SELECT 
  COUNT(DISTINCT user_id) as active_users_with_rag,
  AVG(embedding_count) as avg_embeddings_per_user,
  SUM(CASE WHEN last_activity >= NOW() - INTERVAL '7 days' THEN 1 ELSE 0 END) as recently_active_users
FROM (
  SELECT 
    user_id,
    COUNT(*) as embedding_count,
    MAX(created_at) as last_activity
  FROM user_metadata_embeddings
  GROUP BY user_id
) user_activity;
```

### **Performance Monitoring:**

#### **Resource Utilization:**
```sql
-- Database resource monitoring
SELECT 
  'Database Size' as metric,
  pg_size_pretty(pg_database_size(current_database())) as value
UNION ALL
SELECT 
  'Embedding Table Size',
  pg_size_pretty(pg_total_relation_size('user_metadata_embeddings'))
UNION ALL
SELECT 
  'Behavior Events Size', 
  pg_size_pretty(pg_total_relation_size('user_behavior_events'))
UNION ALL
SELECT 
  'Active Connections',
  COUNT(*)::TEXT
FROM pg_stat_activity WHERE state = 'active';
```

#### **Query Performance Trends:**
```sql
-- Top queries by execution time (requires pg_stat_statements)
SELECT 
  LEFT(query, 100) as query_preview,
  calls,
  total_time,
  mean_time,
  stddev_time,
  rows
FROM pg_stat_statements 
WHERE query LIKE '%user_metadata_embeddings%' 
   OR query LIKE '%behavior_metrics%'
ORDER BY mean_time DESC 
LIMIT 10;
```

---

## 🧠 **AI SYSTEM MONITORING**

### **OpenAI Integration Health:**

#### **API Usage Tracking:**
```sql
-- OpenAI API usage analysis
SELECT 
  DATE(triggered_at) as date,
  COUNT(*) as embedding_requests,
  COUNT(*) FILTER (WHERE error_message LIKE '%OpenAI%') as api_errors,
  COUNT(*) FILTER (WHERE error_message LIKE '%rate limit%') as rate_limit_hits,
  AVG(EXTRACT(EPOCH FROM (processed_at - triggered_at))) as avg_processing_seconds
FROM webhook_logs 
WHERE webhook_type = 'metadata_embedding_queued'
  AND triggered_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE(triggered_at)
ORDER BY date DESC;
```

#### **Embedding Quality Metrics:**
```sql
-- Embedding content quality analysis
SELECT 
  domain_tag,
  COUNT(*) as total_embeddings,
  AVG(LENGTH(text_snippet)) as avg_snippet_length,
  MIN(LENGTH(text_snippet)) as min_snippet_length,
  MAX(LENGTH(text_snippet)) as max_snippet_length,
  COUNT(*) FILTER (WHERE LENGTH(text_snippet) < 20) as very_short_snippets
FROM user_metadata_embeddings 
GROUP BY domain_tag
ORDER BY avg_snippet_length DESC;
```

### **RAG Search Analytics:**

#### **Search Pattern Analysis:**
```sql
-- Query cache analysis (if implemented)
SELECT 
  COUNT(*) as cached_queries,
  COUNT(DISTINCT user_id) as users_with_cached_queries,
  AVG(LENGTH(query_text)) as avg_query_length,
  COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '1 hour') as recent_queries
FROM query_cache 
WHERE created_at >= NOW() - INTERVAL '24 hours';
```

---

## 📊 **BUSINESS METRICS MONITORING**

### **User Adoption Metrics:**

#### **RAG Feature Usage:**
```sql
-- RAG adoption and usage patterns
WITH user_rag_adoption AS (
  SELECT 
    user_id,
    COUNT(*) as total_embeddings,
    COUNT(DISTINCT domain_tag) as domains_used,
    MAX(created_at) as last_rag_activity,
    MIN(created_at) as first_rag_activity
  FROM user_metadata_embeddings
  GROUP BY user_id
)
SELECT 
  COUNT(*) as total_rag_users,
  AVG(total_embeddings) as avg_embeddings_per_user,
  AVG(domains_used) as avg_domains_per_user,
  COUNT(*) FILTER (WHERE last_rag_activity >= NOW() - INTERVAL '7 days') as active_rag_users,
  COUNT(*) FILTER (WHERE domains_used >= 4) as power_users
FROM user_rag_adoption;
```

#### **Behavioral Analytics Engagement:**
```sql
-- Behavioral analytics usage
SELECT 
  COUNT(DISTINCT user_id) as users_with_behavioral_data,
  SUM(jsonb_array_length(behavior_metrics)) as total_behavioral_data_points,
  AVG(jsonb_array_length(behavior_metrics)) as avg_data_points_per_pillar
FROM pillars 
WHERE behavior_metrics != '[]'::jsonb;
```

### **Feature Impact Analysis:**
```sql
-- Productivity improvement correlation
SELECT 
  user_id,
  COUNT(*) FILTER (WHERE (metrics->>'alignment_score')::numeric >= 0.8) as high_alignment_days,
  COUNT(*) as total_measured_days,
  ROUND(COUNT(*) FILTER (WHERE (metrics->>'alignment_score')::numeric >= 0.8) * 100.0 / COUNT(*), 2) as high_performance_percentage
FROM (
  SELECT 
    user_id,
    jsonb_array_elements(behavior_metrics) as metrics
  FROM pillars 
  WHERE behavior_metrics != '[]'::jsonb
) behavioral_data
GROUP BY user_id
HAVING COUNT(*) >= 7 -- Users with at least 1 week of data
ORDER BY high_performance_percentage DESC;
```

---

## 🚨 **INCIDENT RESPONSE PROCEDURES**

### **Critical Issue Response:**

#### **Embedding Generation System Down:**
```sql
-- Emergency diagnostic queries
SELECT 
  'Recent Webhook Errors' as issue_type,
  COUNT(*) as count,
  string_agg(DISTINCT error_message, '; ') as error_messages
FROM webhook_logs 
WHERE status = 'error' 
  AND triggered_at >= NOW() - INTERVAL '1 hour'
UNION ALL
SELECT 
  'Edge Function Health',
  CASE WHEN COUNT(*) > 0 THEN 1 ELSE 0 END,
  'Check Edge Function logs in Supabase dashboard'
FROM webhook_logs 
WHERE webhook_type = 'metadata_embedding_queued'
  AND triggered_at >= NOW() - INTERVAL '5 minutes';
```

**Resolution Steps:**
1. Check Edge Function logs in Supabase dashboard
2. Verify OpenAI API key and quota
3. Check PostgreSQL notification system
4. Restart Edge Function if necessary
5. Manual processing via batch API if critical

#### **Vector Search Performance Degradation:**
```sql
-- Index health check
SELECT 
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes 
WHERE indexname LIKE '%embedding%';

-- VACUUM and ANALYZE if needed
VACUUM ANALYZE user_metadata_embeddings;
```

#### **Materialized View Refresh Failure:**
```sql
-- Manual view refresh with error handling
SELECT refresh_behavior_views();

-- Check specific view status
SELECT 
  schemaname,
  matviewname,
  ispopulated
FROM pg_matviews 
WHERE schemaname = 'public';
```

---

## 📋 **MAINTENANCE PROCEDURES**

### **Weekly Maintenance:**
```sql
-- Execute every Sunday
SELECT cleanup_old_embeddings(180); -- Remove embeddings older than 6 months
SELECT cleanup_query_cache();       -- Clean query cache
VACUUM ANALYZE user_metadata_embeddings; -- Optimize vector storage
VACUUM ANALYZE user_behavior_events;     -- Optimize behavioral data
```

### **Monthly Maintenance:**
```sql
-- Performance optimization
REINDEX INDEX idx_metadata_embeddings_hnsw; -- Rebuild vector index
UPDATE pg_stat_statements_reset();           -- Reset query statistics

-- Storage analysis
SELECT get_embedding_stats(); -- Comprehensive storage analysis
```

### **Quarterly Review:**
- **Performance benchmarking**: Compare query times against baselines
- **Storage optimization**: Analyze growth patterns and optimize retention
- **Feature usage analysis**: Review adoption metrics and optimization opportunities
- **Security audit**: Review RLS policies and access patterns

---

## 🔧 **TROUBLESHOOTING GUIDE**

### **Common Issues & Solutions:**

#### **Embeddings Not Generating:**
1. Check user analytics preferences: `record_rag_snippets = true`
2. Verify Edge Function deployment and OpenAI API key
3. Check webhook_logs for error messages
4. Test manual processing via API

#### **Slow Vector Search:**
1. Check HNSW index status: `SELECT * FROM pg_indexes WHERE indexname LIKE '%hnsw%';`
2. Analyze query plans: `EXPLAIN ANALYZE` on search queries
3. Consider index rebuilding: `REINDEX INDEX idx_metadata_embeddings_hnsw;`
4. Review similarity thresholds and result limits

#### **Behavioral Analytics Missing:**
1. Verify materialized views are refreshed: Check `refresh_behavior_views()` logs
2. Check behavioral metrics data: Ensure `behavior_metrics != '[]'`
3. Validate analytics preferences: User consent for `track_pillar_metrics`
4. Review cron job status: `SELECT * FROM cron.job_run_details;`

---

## 📞 **ESCALATION PROCEDURES**

### **Severity Levels:**

#### **Critical (Immediate Response):**
- RAG system completely down (>50% failure rate)
- Database connectivity issues
- Data corruption or loss
- Security breach indicators

#### **High (4-hour Response):**
- Performance degradation >200ms
- Edge Function processing delays >1 minute
- Materialized view refresh failures
- OpenAI API integration issues

#### **Medium (24-hour Response):**
- Individual embedding generation failures
- Minor performance issues <200ms
- User consent preference issues
- Documentation updates needed

#### **Low (Weekly Review):**
- Optimization opportunities
- Feature usage analysis
- Storage growth planning
- Performance tuning suggestions

---

This monitoring guide ensures the RAG + Behavioral Analytics system operates at peak performance with proactive issue detection and rapid incident response capabilities.