# 🤖 Aurum Life AI Quota System - Complete Guide

**Version:** 3.0.0  
**Last Updated:** September 3, 2025  
**Status:** ✅ Production-Ready with Real Usage Tracking

---

## 📊 **REAL AI QUOTA SYSTEM NOW IMPLEMENTED**

### **✅ What Changed:**
- **Before**: Hardcoded 250/250 (fake tracking)
- **After**: Real usage tracking with database-backed quota system
- **Result**: Accurate AI interaction consumption and cost control

---

## 🎯 **EXACTLY HOW AI INTERACTIONS ARE CONSUMED**

### **💛 SENTIMENT ANALYSIS (1 interaction per analysis)**

#### **When Triggered:**
```javascript
// When you write a journal entry:
1. You type in the Journal and save entry
2. Database trigger automatically calls sentiment analysis
3. GPT-4o-mini analyzes your text
4. CONSUMES: 1 AI interaction automatically

// When you manually test sentiment:
1. You use the sentiment analysis endpoint
2. GPT-4o-mini processes your text  
3. CONSUMES: 1 AI interaction per test
```

#### **Backend Implementation:**
```python
# sentiment_analysis_service.py
async def analyze_text(text, title, user_id):
    # 1. Check if user has quota available
    has_quota, quota_info = await ai_quota_service.check_quota_available(user_id)
    
    # 2. If no quota, return error message
    if not has_quota:
        return {"error": "AI quota exceeded"}
    
    # 3. Make OpenAI API call
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "Analyze sentiment..."}]
    )
    
    # 4. Log successful interaction (decrements quota by 1)
    await ai_quota_service.log_ai_interaction(
        user_id, AIFeatureType.SENTIMENT_ANALYSIS, success=True
    )
```

#### **Quota Impact:**
- **Each Journal Entry**: -1 AI interaction (automatic)
- **Manual Sentiment Test**: -1 AI interaction per test
- **Cost Per Analysis**: ~$0.002 (GPT-4o-mini pricing)

---

### **🎯 GOAL PLANNER AI COACHING (1-3 interactions per session)**

#### **When Triggered:**
```javascript
// Goal Planner features that consume quota:
1. Goal Decomposition: "Break down this goal into projects" → 1 interaction
2. Obstacle Analysis: "Identify potential obstacles" → 1 interaction  
3. Strategic Planning: "Create action plan" → 1 interaction
4. Weekly Reviews: AI-powered strategic guidance → 1 interaction
```

#### **Backend Implementation:**
```python
# ai_coach_mvp_service.py (Goal Planner backend)
async def goal_coaching_session(user_id, goal_data):
    # Check quota for coaching session
    has_quota = await ai_quota_service.check_quota_available(user_id)
    
    if not has_quota:
        return {"error": "AI quota exceeded"}
    
    # Make LLM call for goal coaching
    llm = LlmChat().with_model("openai", "gpt-5-nano")
    response = await llm.send_message(goal_prompt)
    
    # Log interaction
    await ai_quota_service.log_ai_interaction(
        user_id, AIFeatureType.GOAL_COACHING, success=True
    )
```

#### **Quota Impact:**
- **Basic Goal Setup**: -1 AI interaction
- **Advanced Goal Session**: -2-3 AI interactions (multiple AI calls)
- **Cost Per Session**: ~$0.003-0.010 depending on complexity

---

### **⚡ AI QUICK ACTIONS (1 interaction per feature)**

#### **When Triggered:**
```javascript
// AI Quick Actions features:
1. "AI Focus Suggestions" → 1 interaction (analyzes all tasks)
2. "Today's Priorities" → 1 interaction (AI coaching for top tasks)  
3. "Task Why Statements" → 1 interaction (explains why tasks matter)
4. "Quick Goal Setup" → 1 interaction (rapid goal creation with AI)
```

#### **Backend Implementation:**
```python
# server.py - AI Quick Actions endpoints
@app.get("/ai/suggest-focus")
async def suggest_focus_tasks(user_id):
    # Check quota
    has_quota = await ai_quota_service.check_quota_available(user_id)
    
    if not has_quota:
        raise HTTPException(429, "AI quota exceeded")
    
    # Get AI-powered focus suggestions
    priorities = await ai_coach_service.get_today_priorities(user_id, use_ai=True)
    
    # Log interaction  
    await ai_quota_service.log_ai_interaction(
        user_id, AIFeatureType.FOCUS_SUGGESTIONS, success=True
    )
```

#### **Quota Impact:**
- **Each AI Quick Action**: -1 AI interaction per feature
- **Multiple Actions**: Each feature consumes separately
- **Cost Per Action**: ~$0.002-0.005 per feature

---

### **🧠 HRM ANALYSIS (1 interaction per analysis)**

#### **When Triggered:**
```javascript
// When you click "Analyze with AI" buttons:
1. On Tasks: "Why does this task matter?" → 1 interaction
2. On Projects: "How does this project align with goals?" → 1 interaction
3. On Areas: "What's the strategic importance?" → 1 interaction
4. On Pillars: "How balanced is this life domain?" → 1 interaction
5. Global Analysis: "Overall life analysis" → 1 interaction
```

#### **Backend Implementation:**
```python
# hrm_service.py - Hierarchical Reasoning Model
async def analyze_entity(entity_type, entity_id, user_id):
    # Check quota
    has_quota = await ai_quota_service.check_quota_available(user_id)
    
    # Make LLM call for hierarchical reasoning
    llm = LlmChat().with_model("openai", "gpt-5-nano")
    response = await llm.send_message(analysis_prompt)
    
    # Log interaction
    await ai_quota_service.log_ai_interaction(
        user_id, AIFeatureType.HRM_ANALYSIS, success=True
    )
```

#### **Quota Impact:**
- **Each "Analyze with AI"**: -1 AI interaction
- **Multiple Entities**: Each analysis consumes separately
- **Cost Per Analysis**: ~$0.002 per analysis

---

### **❌ WHAT DOESN'T CONSUME QUOTA:**

#### **Free Features (No AI Calls):**
```javascript
✅ Rule-based Insights: Pattern recognition without OpenAI calls (FREE)
✅ Dashboard Analytics: Statistics and charts (FREE)
✅ Navigation: All UI navigation and screen switching (FREE)  
✅ Semantic Search: Vector similarity using pgvector (FREE)
✅ Task/Project CRUD: Creating, editing, deleting items (FREE)
✅ Calendar & Planning: Date management and scheduling (FREE)
✅ Authentication: Login, profile management (FREE)
✅ Data Export: Exporting your data (FREE)
```

---

## 📈 **QUOTA TRACKING IMPLEMENTATION**

### **🗄️ Database Schema:**
```sql
CREATE TABLE ai_interactions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  feature_type VARCHAR(100),  -- 'sentiment_analysis', 'goal_coaching', etc.
  feature_details JSONB,     -- Additional context about the interaction
  tokens_used INTEGER,       -- Approximate OpenAI token usage
  success BOOLEAN,           -- Whether the AI call succeeded
  error_message TEXT,        -- Error details if failed
  processing_time_ms INTEGER, -- How long the AI call took
  created_at TIMESTAMPTZ     -- When the interaction occurred
);
```

### **⚡ Real-Time Quota Tracking:**
```python
class AIQuotaService:
    async def get_user_quota(user_id):
        """Returns REAL usage data from database"""
        # Counts actual ai_interactions records for current month
        # Returns {remaining: X, used: Y, total: 250}
        
    async def consume_quota(user_id, feature_type):
        """Logs AI interaction and decrements available quota"""
        # Inserts record into ai_interactions table
        # Real-time quota calculation
```

### **📊 Usage Analytics:**
```python
# Real usage breakdown by feature:
{
  "sentiment_analysis": 15,     # 15 journal entries analyzed
  "goal_coaching": 8,           # 8 goal planning sessions
  "focus_suggestions": 12,      # 12 focus suggestion requests
  "hrm_analysis": 5,            # 5 "Analyze with AI" clicks
  "task_why_statements": 3      # 3 task explanation requests
}
```

---

## 🎯 **TESTING THE QUOTA SYSTEM**

### **Real-Time Quota Testing:**

#### **Test 1: Check Current Usage**
```bash
# Login credentials: marc.alleyne@aurumtechnologyltd.com / password123
Current quota: 0/250 used, 250 remaining ✅
```

#### **Test 2: Consume AI Interactions**
```javascript
// Try these features and watch quota decrease:
1. Write a journal entry → Watch quota: 249 remaining
2. Use "AI Focus Suggestions" → Watch quota: 248 remaining  
3. Click "Analyze with AI" on a task → Watch quota: 247 remaining
4. Use Goal Planner coaching → Watch quota: 245-246 remaining
```

#### **Test 3: Quota Exceeded Behavior**
```python
# When quota reaches 0:
HTTP 429: "AI quota exceeded. You have 0 interactions remaining this month."

# Graceful degradation:
- Sentiment analysis: Returns neutral sentiment with upgrade message
- AI coaching: Skipped with explanation
- HRM analysis: Basic analysis without AI enhancement
```

---

## ⚙️ **QUOTA MANAGEMENT FEATURES**

### **📊 Real-Time Monitoring:**
- **Quota Warnings**: Notifications at 80% (200/250) and 95% (238/250) usage
- **Usage Breakdown**: Track which AI features you use most
- **Processing Time**: Monitor AI response performance
- **Success Rate**: Track AI interaction reliability

### **🔄 Monthly Reset:**
- **Auto Reset**: Quota automatically resets on the 1st of each month
- **Pro Rata**: New users get full quota regardless of signup date
- **Rollover**: No rollover - unused quota expires monthly

### **📱 User Experience:**
- **Real-Time Updates**: Quota display updates immediately after AI usage
- **Graceful Degradation**: Features work with limitations when quota exceeded
- **Upgrade Prompts**: Clear messaging about premium tier benefits

---

## 💰 **COST ANALYSIS**

### **OpenAI Cost per Interaction:**
```
📝 Sentiment Analysis (GPT-4o-mini): ~$0.002 per journal entry
🎯 Goal Coaching (GPT-5-nano): ~$0.003-0.005 per session
⚡ Focus Suggestions (GPT-5-nano): ~$0.002-0.004 per request
🧠 HRM Analysis (GPT-5-nano): ~$0.002 per analysis
📊 Task Why Statements (GPT-5-nano): ~$0.001-0.003 per request

Monthly OpenAI costs for 250 interactions: ~$0.50-1.25
```

### **Revenue vs Cost Analysis:**
```
💛 Free Tier (10 interactions): $0.02-0.05 cost → Sustainable loss leader
🚀 Pro Tier ($19/month, 250 interactions): $0.50-1.25 cost → 95%+ margin
⭐ Premium Tier ($39/month, unlimited): $2-10 cost → 75%+ margin
```

---

## 🎮 **HOW TO USE THE ENHANCED QUOTA SYSTEM**

### **For Users:**

#### **Monitor Your Usage:**
1. **Check Quota**: AI Quota widget shows real usage (e.g., "23/250 used")
2. **View Breakdown**: See which features you use most
3. **Track Patterns**: Understand your AI usage habits

#### **Optimize Usage:**
1. **Journal Regularly**: Each entry uses 1 interaction for sentiment analysis
2. **Batch AI Actions**: Use AI Quick Actions efficiently  
3. **Strategic HRM**: Use "Analyze with AI" for important decisions
4. **Goal Planning**: Use Goal Planner for high-impact strategic sessions

#### **When Quota is Low:**
1. **Priority Features**: Focus on highest-value AI interactions
2. **Manual Alternatives**: Use rule-based insights when quota is low
3. **Next Month**: Quota resets automatically on the 1st
4. **Upgrade**: Consider Pro tier for unlimited interactions

### **For Developers:**

#### **Adding New AI Features:**
```python
# Template for quota-aware AI endpoint:
@app.post("/api/new-ai-feature")
async def new_ai_feature(user: User = Depends(get_current_active_user)):
    # 1. Check quota
    has_quota, quota_info = await ai_quota_service.check_quota_available(
        str(user.id), AIFeatureType.NEW_FEATURE
    )
    
    # 2. Return quota exceeded error if needed
    if not has_quota:
        raise HTTPException(429, "AI quota exceeded")
    
    # 3. Make AI API call
    result = await openai_client.chat.completions.create(...)
    
    # 4. Log successful interaction
    await ai_quota_service.log_ai_interaction(
        str(user.id), AIFeatureType.NEW_FEATURE, success=True
    )
    
    return result
```

---

## 📊 **QUOTA ANALYTICS & MONITORING**

### **Usage Analytics Available:**
```python
# Database views and functions:
daily_ai_usage                    # Daily usage patterns by feature
get_user_ai_usage_current_month() # Current month detailed breakdown
check_ai_quota_available()        # Real-time quota checking
```

### **Business Intelligence:**
```sql
-- Most used AI features
SELECT feature_type, COUNT(*) as usage_count
FROM ai_interactions 
WHERE success = true AND created_at >= date_trunc('month', NOW())
GROUP BY feature_type
ORDER BY usage_count DESC;

-- User engagement with AI features
SELECT 
  user_id,
  COUNT(*) as total_interactions,
  COUNT(DISTINCT feature_type) as features_used,
  AVG(processing_time_ms) as avg_response_time
FROM ai_interactions
WHERE success = true
GROUP BY user_id;
```

---

## 🔧 **IMPLEMENTATION DETAILS**

### **AI Feature Types Tracked:**
```python
class AIFeatureType(Enum):
    SENTIMENT_ANALYSIS = "sentiment_analysis"      # Journal emotion analysis
    HRM_ANALYSIS = "hrm_analysis"                  # "Analyze with AI" buttons
    TASK_WHY_STATEMENTS = "task_why_statements"    # Task importance explanations
    FOCUS_SUGGESTIONS = "focus_suggestions"        # AI-powered task prioritization
    TODAY_PRIORITIES = "today_priorities"          # Daily AI coaching
    GOAL_COACHING = "goal_coaching"                # Strategic goal planning
    PROJECT_DECOMPOSITION = "project_decomposition" # Project breakdown with AI
    STRATEGIC_PLANNING = "strategic_planning"      # Long-term planning sessions
```

### **Quota Thresholds & Warnings:**
```python
# Automatic warnings:
200/250 (80%): "You've used 80% of your AI interactions"
238/250 (95%): "Only 12 AI interactions remaining this month"
250/250 (100%): "AI quota exceeded - upgrade for unlimited access"

# Webhook notifications:
pg_notify('quota_warning', {...})  # Real-time notifications
pg_notify('quota_limit', {...})    # Limit reached alerts
```

---

## 🎯 **SPECIFIC FEATURE CONSUMPTION GUIDE**

### **📝 JOURNAL & EMOTIONAL INTELLIGENCE**
- **Writing Entry**: 1 interaction (automatic sentiment analysis)
- **Manual Sentiment Test**: 1 interaction per test
- **Emotional Dashboard**: FREE (uses stored sentiment data)
- **Trend Analysis**: FREE (uses historical sentiment data)

### **🎯 GOAL PLANNER (Strategic AI Coaching)**
- **Basic Goal Setup**: 1 interaction (AI goal decomposition)
- **Advanced Planning Session**: 2-3 interactions (multiple AI analyses)
- **Weekly Strategic Review**: 1 interaction (comprehensive AI guidance)
- **Obstacle Analysis**: 1 interaction (AI-powered obstacle identification)

### **⚡ AI QUICK ACTIONS**
- **"AI Focus Suggestions"**: 1 interaction (analyzes all tasks for priority)
- **"Task Why Statements"**: 1 interaction (explains importance of multiple tasks)
- **"Quick Goal Setup"**: 1 interaction (rapid AI-assisted goal creation)
- **"Today's Priorities"**: 1 interaction (AI coaching for daily tasks)

### **🧠 HIERARCHICAL REASONING (HRM)**
- **"Analyze with AI" (Task)**: 1 interaction per task analysis
- **"Analyze with AI" (Project)**: 1 interaction per project analysis
- **"Analyze with AI" (Area)**: 1 interaction per area analysis
- **"Analyze with AI" (Pillar)**: 1 interaction per pillar analysis
- **Global Analysis**: 1 interaction for comprehensive life analysis

---

## 💡 **OPTIMIZATION STRATEGIES**

### **For Users:**
```
🎯 High-Value Interactions:
1. Use Goal Planner for major life decisions (high ROI)
2. Use HRM Analysis for important projects (strategic value)
3. Write journal entries regularly (compound emotional intelligence)
4. Use AI Quick Actions for daily optimization (efficiency boost)

⚡ Efficiency Tips:
1. Batch AI interactions when possible
2. Use free features (analytics, semantic search) extensively  
3. Save AI interactions for high-impact decisions
4. Plan AI usage around monthly reset cycle
```

### **For Businesses:**
```
📊 Cost Optimization:
1. Monitor which AI features provide most user value
2. Optimize prompts to reduce token usage
3. Implement smart caching for repeated AI requests
4. Use tiered pricing to manage AI costs vs revenue

🎯 User Value:
1. Track correlation between AI usage and user retention
2. Monitor which AI features drive subscription upgrades
3. Analyze optimal quota levels for each tier
4. Implement usage-based upselling opportunities
```

---

## 🎉 **SUCCESS: COMPLETE AI QUOTA SYSTEM**

### **✅ IMPLEMENTED FEATURES:**
- **✅ Real Usage Tracking**: Database-backed quota system
- **✅ All AI Endpoints**: Quota consumption integrated across all OpenAI calls
- **✅ Graceful Degradation**: Smooth experience when quota exceeded
- **✅ Usage Analytics**: Comprehensive tracking and business intelligence
- **✅ Threshold Monitoring**: Automated warnings and notifications
- **✅ Cost Control**: Accurate tracking for business optimization

### **🎯 CURRENT STATUS:**
- **Your Current Quota**: 0/250 used (fresh start with real tracking)
- **Next AI Interaction**: Will decrement to 249/250 remaining
- **Features Ready**: All AI features now consume quota properly
- **Monitoring Active**: Real-time usage tracking and analytics

### **💛 RESULT:**
**Aurum Life now has enterprise-grade AI quota management with accurate usage tracking, cost control, and optimal user experience!** 🚀

---

**AI Quota System Implementation By**: Strategic Orchestrator  
**Testing Status**: ✅ Verified and Operational  
**Business Impact**: Enhanced cost control and user value optimization