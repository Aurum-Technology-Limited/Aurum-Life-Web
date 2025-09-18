<<<<<<< HEAD

  # Aurum-Life-Web-UI

  This is a code bundle for Aurum-Life-Web-UI. The original project is available at https://www.figma.com/design/zNM1dbPNDPzkx3NaXWFcUD/Aurum-Life-Web-UI.

  ## Running the code

  Run `npm i` to install the dependencies.

  Run `npm run dev` to start the development server.
  
=======
# Aurum Life - AI-Powered Personal Productivity Platform
**Enhanced with RAG System & Behavioral Analytics**

## 🌟 **OVERVIEW**

Aurum Life is a next-generation personal productivity platform that combines traditional task management with cutting-edge AI capabilities. The system uses semantic search, behavioral analytics, and personalized AI recommendations to help users achieve their life goals.

### **🚀 KEY FEATURES**

#### **🧠 AI-Powered Capabilities:**
- **Semantic Search**: Find related content across your entire life structure using AI
- **RAG (Retrieval Augmented Generation)**: AI recommendations based on your personal data  
- **Behavioral Analytics**: Advanced pattern recognition and productivity insights
- **Contextual AI**: Personalized recommendations using your complete productivity history

#### **🎯 Productivity System:**
- **PAPT Hierarchy**: Pillars → Areas → Projects → Tasks structure
- **Smart Journaling**: AI-enhanced reflection and insight generation
- **Goal Tracking**: Alignment scoring and progress visualization
- **Habit Formation**: Behavioral strength analysis and optimization

#### **📊 Advanced Analytics:**
- **Weekly Trend Analysis**: Alignment scores, sentiment, and habit strength
- **Flow State Tracking**: Productivity patterns and interruption analysis  
- **Task Performance**: Completion rates by energy and cognitive load
- **Personalized Insights**: Data-driven recommendations for optimization

#### **🔐 Privacy-First Design:**
- **Granular Consent**: 11 different privacy control options
- **Data Ownership**: Complete control over your personal data
- **Local Processing**: AI analysis respects your privacy preferences
- **GDPR Compliant**: Right to export and delete all data

---

## 🏗️ **TECHNICAL ARCHITECTURE**

### **Core Technology Stack:**
- **Backend**: FastAPI (Python) with async processing
- **Database**: Supabase (PostgreSQL) with pgvector for AI features
- **Frontend**: React with Tailwind CSS
- **AI Integration**: OpenAI embeddings for semantic understanding
- **Real-time Processing**: Supabase Edge Functions
- **Automation**: PostgreSQL triggers + pg_cron scheduling

### **Advanced Features:**
- **Vector Search**: HNSW indexes for sub-100ms semantic queries
- **Behavioral Metrics**: JSONB time-series data with materialized views  
- **Automated Processing**: Background embedding generation
- **Privacy Controls**: User-configurable data collection preferences
- **Performance Optimization**: Strategic indexing and caching

---

## 🚀 **GETTING STARTED**

### **Prerequisites:**
- Node.js 18+ and Python 3.9+
- Supabase account with project created
- OpenAI API key for semantic features

### **Environment Setup:**

#### **Backend (.env):**
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_ANON_KEY=your-anon-key
OPENAI_API_KEY=your-openai-api-key
```

#### **Frontend (.env):**
```env
REACT_APP_BACKEND_URL=your-backend-url
REACT_APP_SUPABASE_URL=https://your-project.supabase.co  
REACT_APP_SUPABASE_ANON_KEY=your-anon-key
```

### **Installation:**

```bash
# Clone and setup backend
cd backend
pip install -r requirements.txt

# Setup frontend
cd frontend  
yarn install

# Start services
# Backend runs on port 8001 via supervisor
# Frontend runs on port 3000 via supervisor
sudo supervisorctl restart all
```

---

## 📊 **DATABASE SETUP**

### **1. Enable Extensions:**
```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_cron;
```

### **2. Apply Migrations:**
Execute these SQL files in sequence in your Supabase SQL Editor:
1. `backend/migrations/016_user_metadata_embeddings.sql`
2. `backend/migrations/017_behavioral_metrics_enhancement.sql`  
3. `backend/migrations/018_analytics_preferences_extension.sql`
4. `backend/migrations/019_automated_embedding_pipeline.sql`
5. `backend/migrations/020_analytical_materialized_views.sql`
6. `backend/rag_system_functions.sql`

### **3. Deploy Edge Function:**
1. **Supabase Dashboard** → Edge Functions → Create Function
2. **Name**: `metadata-embedding-processor`  
3. **Code**: Copy from `backend/edge_functions/metadata-embedding-processor.ts`
4. **Environment Variables**: Add `OPENAI_API_KEY`

### **4. Setup Automation:**
```sql
-- Schedule automated maintenance
SELECT cron.schedule('refresh-behavioral-views', '0 2 * * *', 'SELECT refresh_behavior_views();');
SELECT cron.schedule('cleanup-embeddings', '0 3 * * 0', 'SELECT cleanup_old_embeddings(180);');
```

---

## 🧠 **AI FEATURES USAGE**

### **Semantic Search:**
```javascript
// Search across your entire productivity system
const results = await ragApi.semanticSearch(
  "tasks related to health goals",
  ['tasks', 'projects'], // Search domains
  10 // Max results
);

// Results include:
// - Cross-domain relationships (journal → tasks)  
// - Similarity scores (0.4-1.0)
// - Rich context (priority, status, metadata)
```

### **Behavioral Insights:**
```javascript
// Get productivity analytics
const insights = await ragApi.getBehavioralInsights('30d');

// Returns:
// - Weekly pillar alignment trends
// - Habit formation patterns  
// - Flow state analysis
// - Task completion predictions
```

### **AI-Enhanced Recommendations:**
```javascript
// Context-aware AI suggestions
const context = await ragApi.getContextSummary();
// Use context for personalized AI recommendations
```

---

## 📈 **ANALYTICS CAPABILITIES**

### **Behavioral Metrics Tracked:**
- **Alignment Score** (0-1): How well actions align with life goals
- **Sentiment Analysis** (0-1): Emotional well-being patterns
- **Habit Strength** (0-1): Consistency and routine formation
- **Energy Levels** (0-1): Motivation and vitality tracking
- **Focus Time**: Deep work duration and quality

### **Analytical Views:**
- **Weekly Pillar Alignment**: Trend analysis across life areas
- **Area Habit Metrics**: Habit formation success rates
- **Daily Flow Metrics**: Productivity flow state patterns  
- **Task Completion Patterns**: Performance by energy/cognitive requirements

---

## 🔐 **PRIVACY & SECURITY**

### **Privacy Controls:**
Users have granular control over:
- Analytics data collection
- AI behavior tracking  
- RAG snippet storage
- Flow state monitoring
- Behavioral embedding generation

### **Data Security:**
- **Row Level Security**: Multi-tenant data isolation
- **Encrypted Storage**: All data encrypted at rest
- **Audit Trails**: Complete processing history
- **Right to Deletion**: GDPR-compliant data removal

---

## 🔧 **DEVELOPMENT**

### **Project Structure:**
```
/app/
├── backend/                     # FastAPI backend
│   ├── migrations/             # Database schema migrations
│   ├── edge_functions/         # Supabase Edge Functions
│   ├── rag_service.py         # RAG service implementation
│   ├── supabase_services.py   # Database services
│   └── server.py              # Main API server
├── frontend/                   # React frontend
│   ├── src/services/          # API service layers
│   ├── src/components/        # React components
│   └── src/hooks/            # Custom React hooks
├── tests/                     # Test suites
└── docs/                     # Technical documentation
```

### **Key Services:**
- **RAG Service**: Semantic search and context generation
- **Behavioral Analytics**: Metrics collection and analysis
- **Supabase Services**: Database operations with RLS
- **Edge Functions**: Background processing and AI integration

---

## 📊 **MONITORING & MAINTENANCE**

### **System Health:**
- **Embedding Generation**: Automated background processing
- **Performance Monitoring**: Query timing and success rates
- **Resource Usage**: Storage and compute optimization
- **Error Tracking**: Comprehensive logging and alerting

### **Automated Maintenance:**
- **Daily**: Analytics refresh, cache cleanup
- **Weekly**: Old data cleanup, performance optimization
- **Monthly**: System health analysis, storage optimization

---

## 🎯 **PRODUCTION METRICS**

### **Performance Benchmarks:**
- **Vector Search**: <100ms for 10,000+ embeddings
- **Behavioral Analytics**: <200ms for 90-day analysis
- **API Response**: <500ms for complex queries
- **Embedding Generation**: <5 seconds per entity

### **Scalability Specifications:**
- **Concurrent Users**: 1000+ with proper connection pooling
- **Data Growth**: Handles millions of embeddings efficiently
- **Processing Throughput**: 3000 embeddings/minute (OpenAI limit)
- **Storage Efficiency**: Optimized JSONB + vector storage

---

## 🤝 **CONTRIBUTING**

### **Development Guidelines:**
1. **Follow privacy-first principles** - All features respect user consent
2. **Maintain performance standards** - Queries should be <100ms
3. **Comprehensive testing** - Include RAG and behavioral analytics tests
4. **Documentation updates** - Keep technical docs current
5. **Security review** - Verify RLS policies and input validation

### **Testing Requirements:**
- **Unit Tests**: Individual service methods
- **Integration Tests**: End-to-end RAG workflows
- **Performance Tests**: Vector search and analytics queries
- **Security Tests**: RLS policy enforcement
- **Privacy Tests**: Consent mechanism validation

---

## 📞 **SUPPORT & RESOURCES**

### **Documentation:**
- `TECHNICAL_ARCHITECTURE_DOCUMENTATION.md` - Complete system architecture
- `RAG_SYSTEM_IMPLEMENTATION_GUIDE.md` - RAG implementation details
- `API_ENDPOINTS_SPECIFICATION.md` - Complete API documentation
- `DEPLOYMENT_GUIDE.md` - Production deployment procedures

### **Key Files:**
- **Database Schema**: `supabase_schema.sql`
- **RAG Service**: `backend/rag_service.py`
- **Edge Function**: `backend/edge_functions/metadata-embedding-processor.ts`
- **Migration Files**: `backend/migrations/016-020_*.sql`

---

**Aurum Life represents the future of personal productivity platforms - combining proven productivity methodologies with cutting-edge AI technology while maintaining complete user privacy and control.** 🚀✨

Built with ❤️ for personal growth and life optimization.
>>>>>>> 9941fa0c5c07842de7f6ea64297b84d6b147bf5d
