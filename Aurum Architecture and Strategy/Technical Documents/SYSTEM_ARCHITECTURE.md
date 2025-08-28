# Aurum Life System Architecture

**Last Updated:** January 2025  
**Document Type:** Technical Architecture Documentation

---

## 🏗️ High-Level Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                   CLIENT LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐         │
│  │   Web Browser   │     │  Mobile Browser │     │   Future: iOS   │         │
│  │   (React SPA)   │     │ (Responsive PWA)│     │   Future: Android│         │
│  └────────┬────────┘     └────────┬────────┘     └────────┬────────┘         │
│           │                       │                         │                   │
│           └───────────────────────┴─────────────────────────┘                  │
│                                   │                                             │
├───────────────────────────────────┼─────────────────────────────────────────────┤
│                                   ▼                                             │
│                           LOAD BALANCER                                         │
│                        (Nginx/Cloudflare)                                       │
│                                   │                                             │
├───────────────────────────────────┼─────────────────────────────────────────────┤
│                          APPLICATION LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                   │                                             │
│  ┌────────────────────────────────┴────────────────────────────────┐          │
│  │                        KUBERNETES CLUSTER                         │          │
│  │                                                                  │          │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │          │
│  │  │  Frontend Pod   │  │  Frontend Pod   │  │  Frontend Pod   │ │          │
│  │  │  (React Build)  │  │  (React Build)  │  │  (React Build)  │ │          │
│  │  │   Port: 3000    │  │   Port: 3000    │  │   Port: 3000    │ │          │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘ │          │
│  │                                                                  │          │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │          │
│  │  │  Backend Pod    │  │  Backend Pod    │  │  Backend Pod    │ │          │
│  │  │   (FastAPI)     │  │   (FastAPI)     │  │   (FastAPI)     │ │          │
│  │  │   Port: 8001    │  │   Port: 8001    │  │   Port: 8001    │ │          │
│  │  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │          │
│  │           │                    │                    │            │          │
│  │           └────────────────────┴────────────────────┘            │          │
│  │                                │                                 │          │
│  └────────────────────────────────┼─────────────────────────────────┘          │
│                                   │                                             │
├───────────────────────────────────┼─────────────────────────────────────────────┤
│                            SERVICE LAYER                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                   │                                             │
│      ┌────────────────────────────┴────────────────────────────┐              │
│      │                                                         │              │
│      ▼                              ▼                          ▼              │
│  ┌─────────────┐            ┌──────────────┐          ┌──────────────┐       │
│  │   Redis     │            │   Celery     │          │   HRM/AI     │       │
│  │   Cache     │            │   Workers    │          │   Service    │       │
│  │  Port: 6379 │            │  (Async Jobs)│          │  (Internal)  │       │
│  └─────────────┘            └──────┬───────┘          └──────┬───────┘       │
│                                    │                          │               │
├────────────────────────────────────┼──────────────────────────┼────────────────┤
│                              DATA LAYER                        │               │
├────────────────────────────────────────────────────────────────┼────────────────┤
│                                    │                           │               │
│  ┌─────────────────────────────────▼───────────────────────────▼─────┐        │
│  │                         SUPABASE PLATFORM                          │        │
│  │                                                                   │        │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │        │
│  │  │  PostgreSQL  │  │   Realtime   │  │   Storage    │         │        │
│  │  │   Database   │  │  WebSockets  │  │   (Files)    │         │        │
│  │  │              │  │              │  │              │         │        │
│  │  │  - users     │  │ - Live updates│  │ - Avatars    │         │        │
│  │  │  - pillars   │  │ - Presence   │  │ - Attachments│         │        │
│  │  │  - areas     │  │              │  │              │         │        │
│  │  │  - projects  │  │              │  │              │         │        │
│  │  │  - tasks     │  │              │  │              │         │        │
│  │  │  - insights  │  │              │  │              │         │        │
│  │  │  - hrm_rules │  │              │  │              │         │        │
│  │  └──────────────┘  └──────────────┘  └──────────────┘         │        │
│  │                                                                   │        │
│  │  ┌──────────────────────────────────────────────────┐           │        │
│  │  │                 AUTH SERVICE                      │           │        │
│  │  │         (Supabase Auth / JWT Tokens)            │           │        │
│  │  └──────────────────────────────────────────────────┘           │        │
│  └───────────────────────────────────────────────────────────────────┘        │
│                                                                                │
├────────────────────────────────────────────────────────────────────────────────┤
│                           EXTERNAL SERVICES                                    │
├────────────────────────────────────────────────────────────────────────────────┤
│                                                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Google      │  │   SendGrid   │  │   Gemini     │  │   AWS S3     │    │
│  │  OAuth 2.0   │  │    Email     │  │   AI API     │  │  (Backup)    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                                                │
└────────────────────────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow Patterns

### 1. **User Authentication Flow**
```
User → React App → FastAPI → Supabase Auth → JWT Token → Authenticated Session
```

### 2. **AI Analysis Request Flow**
```
User Action → React → FastAPI → AI Router → Model Selection → Response
                         ↓          ↓              ↓
                    Redis Cache  HRM Service   ┌─ Strategic: GPT-4 Turbo
                                              └─ Execution: Gemini 1.5 Flash
```

### 3. **Real-time Updates Flow**
```
Database Change → Supabase Realtime → WebSocket → React App → UI Update
```

### 4. **File Upload Flow**
```
User Upload → React (Chunked) → FastAPI → Supabase Storage → URL Reference in DB
```

### 5. **Voice Conversation Flow**
```
User Speech → Whisper STT → AI Router → LLM Response → OpenAI TTS → Audio Output
                  ↓                ↓                        ↓
            Transcription    Model Selection         Voice Selection
                           (Complex/Simple)         (Standard/Premium)
```

## 🤖 AI Architecture

### Multi-Model Strategy

Aurum AI employs a sophisticated multi-model architecture to optimize both performance and cost:

```
┌─────────────────────────────────────────────────────────────────┐
│                        AI Request Router                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Request Classification:                                         │
│  ├─ Complexity Analysis                                          │
│  ├─ Task Type Detection                                          │
│  └─ Cost Optimization                                            │
│                                                                  │
├──────────────────────┬──────────────────────────────────────────┤
│                      ▼                                           │
│  ┌─────────────────────────────┐  ┌──────────────────────────┐ │
│  │   Strategic Planning Model   │  │   Execution Model        │ │
│  ├─────────────────────────────┤  ├──────────────────────────┤ │
│  │                             │  │                          │ │
│  │  Provider: OpenAI           │  │  Provider: Google        │ │
│  │  Model: GPT-4 Turbo         │  │  Model: Gemini 1.5 Flash │ │
│  │                             │  │                          │ │
│  │  Use Cases:                 │  │  Use Cases:              │ │
│  │  • Strategic alignment      │  │  • CRUD operations       │ │
│  │  • Complex planning         │  │  • Data validation       │ │
│  │  • Multi-step reasoning     │  │  • Simple queries        │ │
│  │  • Cross-functional analysis│  │  • Routine updates       │ │
│  │                             │  │                          │ │
│  │  Cost: ~$0.01/1K tokens     │  │  Cost: ~$0.0001/1K tokens│ │
│  └─────────────────────────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### AI Model Selection Criteria

The AI Router uses these criteria to select the appropriate model:

1. **Task Complexity Score (0-10)**
   - 0-3: Simple CRUD, direct queries → Gemini Flash
   - 4-7: Moderate analysis, planning → Gemini Flash or GPT-4 based on load
   - 8-10: Complex reasoning, strategy → GPT-4 Turbo

2. **Request Type Patterns**
   - Contains "analyze", "strategy", "plan" → Strategic Model
   - Contains "create", "update", "list", "fetch" → Execution Model
   - Multi-entity operations → Strategic Model
   - Single entity operations → Execution Model

3. **Cost Optimization Rules**
   - Budget tracking per user/organization
   - Automatic downgrade to cheaper models when quota approached
   - Premium tier users get priority access to advanced models

### Speech API Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Voice Conversation Pipeline                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Speech-to-Text (STT)                                        │
│  ┌─────────────────────────────┐                               │
│  │   Provider: OpenAI           │                               │
│  │   Service: Whisper API       │                               │
│  │   Languages: 99+             │                               │
│  │   Cost: $0.006/minute        │                               │
│  │   Features:                  │                               │
│  │   • Streaming transcription  │                               │
│  │   • Accent robustness        │                               │
│  │   • Noise cancellation       │                               │
│  └──────────────┬──────────────┘                               │
│                 ▼                                               │
│  2. Language Model Processing                                   │
│  ┌─────────────────────────────┐                               │
│  │   (Uses existing AI Router) │                               │
│  └──────────────┬──────────────┘                               │
│                 ▼                                               │
│  3. Text-to-Speech (TTS)                                        │
│  ┌─────────────────────────────┐  ┌──────────────────────────┐ │
│  │   Standard Voice            │  │   Premium Voice          │ │
│  ├─────────────────────────────┤  ├──────────────────────────┤ │
│  │   Provider: OpenAI          │  │   Provider: ElevenLabs   │ │
│  │   Cost: $0.015/1K chars     │  │   Cost: $0.18/1K chars   │ │
│  │   Latency: ~400ms           │  │   Latency: ~300ms        │ │
│  │   Quality: Natural          │  │   Quality: Ultra-realistic│ │
│  │   Voices: 6 options         │  │   Voices: Customizable   │ │
│  └─────────────────────────────┘  └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### AI Service Implementation

```python
# AI Router Implementation Pattern
class AIRouter:
    def __init__(self):
        self.strategic_model = OpenAIClient(model="gpt-4-turbo")
        self.execution_model = GeminiClient(model="gemini-1.5-flash")
        self.complexity_analyzer = ComplexityAnalyzer()
    
    async def route_request(self, request: AIRequest) -> AIResponse:
        complexity_score = await self.complexity_analyzer.analyze(request)
        
        if complexity_score > 7 or request.requires_reasoning:
            return await self.strategic_model.process(request)
        else:
            return await self.execution_model.process(request)

# Speech Service Implementation
class SpeechService:
    def __init__(self):
        self.stt = WhisperAPI()
        self.tts_standard = OpenAITTS()
        self.tts_premium = ElevenLabsTTS()
    
    async def process_voice(self, audio_stream, user_tier):
        # Speech to Text
        transcript = await self.stt.transcribe(audio_stream)
        
        # Process with AI
        ai_response = await self.ai_router.route_request(transcript)
        
        # Text to Speech
        if user_tier == "premium":
            audio_response = await self.tts_premium.synthesize(ai_response)
        else:
            audio_response = await self.tts_standard.synthesize(ai_response)
        
        return audio_response
```

### Cost Optimization Strategies

1. **Request Batching**
   - Combine multiple small requests into single API calls
   - Implement request queuing with 100ms wait time

2. **Intelligent Caching**
   - Cache common queries and responses
   - User-specific cache for personalized responses
   - TTL based on data volatility

3. **Model Fallback Chain**
   ```
   Primary: Gemini Flash → Fallback: GPT-3.5 → Emergency: Cached/Template
   ```

4. **Usage Monitoring**
   - Real-time cost tracking per user
   - Automatic alerts at 80% budget consumption
   - Monthly usage reports and optimization suggestions

## 🏛️ Component Architecture

### Frontend Architecture (React)
```
src/
├── components/           # UI Components
│   ├── ai/              # AI-specific components
│   │   ├── AICommandCenter.jsx
│   │   ├── HRMInsightCard.jsx
│   │   └── AIInsightsDashboard.jsx
│   ├── core/            # Core PAPT components
│   │   ├── Pillars.jsx
│   │   ├── Areas.jsx
│   │   ├── Projects.jsx
│   │   └── Tasks.jsx
│   └── shared/          # Shared components
├── services/            # API Services
│   ├── api.js          # Base API configuration
│   ├── auth.js         # Authentication
│   └── insights.js     # HRM/AI services
├── contexts/           # React Contexts
│   ├── AuthContext.js
│   └── DataContext.js
└── hooks/              # Custom React Hooks
```

### Backend Architecture (FastAPI)
```
backend/
├── models.py           # Pydantic models
├── server.py           # Main FastAPI app
├── hrm_service.py      # HRM implementation
├── blackboard_service.py # Insights storage
├── hrm_rules_engine.py # Rules execution
├── ai/                 # AI Services
│   ├── router.py       # AI model router
│   ├── complexity_analyzer.py
│   ├── openai_client.py
│   ├── gemini_client.py
│   └── speech_service.py
├── services/           # Business logic
│   ├── task_service.py
│   ├── project_service.py
│   └── analytics_service.py
├── middleware/         # Custom middleware
│   ├── auth.py
│   ├── rate_limit.py
│   └── ai_usage_tracker.py
└── utils/             # Utilities
```

### Database Schema Architecture
```
public schema
├── Authentication
│   ├── auth.users (Supabase managed)
│   └── user_profiles
├── PAPT Hierarchy
│   ├── pillars
│   ├── areas
│   ├── projects
│   └── tasks
├── AI/HRM System
│   ├── insights
│   ├── hrm_rules
│   ├── hrm_user_preferences
│   ├── hrm_feedback_log
│   ├── ai_interactions
│   ├── ai_model_usage_logs
│   └── speech_transcripts
├── Supporting
│   ├── journal_entries
│   ├── journal_templates
│   ├── notifications
│   └── resources
└── Indexes & Triggers
```

## 🔐 Security Architecture

### Authentication & Authorization
- **JWT Tokens**: Stateless authentication
- **Row Level Security (RLS)**: Database-level access control
- **API Key Management**: For external service integration
- **CORS Configuration**: Restrictive cross-origin policies

### Data Protection
- **Encryption at Rest**: Supabase managed
- **Encryption in Transit**: HTTPS/TLS 1.3
- **PII Handling**: Minimal collection, secure storage
- **Audit Logging**: All data modifications tracked

## 🚀 Deployment Architecture

### Container Strategy
```yaml
Frontend Container:
  - Base: node:18-alpine
  - Build: React production build
  - Serve: Nginx
  - Health checks: /health

Backend Container:
  - Base: python:3.11-slim
  - Framework: FastAPI + Uvicorn
  - Process Manager: Supervisor
  - Health checks: /api/health

AI Service Container (Optional Microservice):
  - Base: python:3.11-slim
  - Framework: FastAPI + Uvicorn
  - Features:
    - Model router with complexity analyzer
    - Speech processing pipeline
    - Cost tracking middleware
  - Health checks: /api/ai/health
  - Auto-scaling: Based on request queue length
```

### Scaling Strategy
- **Horizontal Scaling**: Pod autoscaling based on CPU/Memory
- **Load Balancing**: Round-robin with health checks
- **Database Pooling**: Connection pooling for PostgreSQL
- **Cache Strategy**: Redis for session and API response caching

## 📊 Monitoring & Observability

### Metrics Collection
- **Application Metrics**: Response times, error rates
- **Infrastructure Metrics**: CPU, memory, disk usage
- **Business Metrics**: User activity, feature adoption

### Logging Strategy
```
Application Logs → Structured JSON → Log Aggregator → Monitoring Dashboard
```

### Alert Conditions
- API response time > 2 seconds
- Error rate > 5%
- Database connection pool exhaustion
- AI API quota approaching limit (80% threshold)
- AI cost per user > $0.50/month
- Model routing failures > 1%
- Voice transcription failures > 5%
- Strategic model usage > 30% (cost alert)

## 🔄 Backup & Recovery

### Backup Strategy
- **Database**: Daily automated backups (30-day retention)
- **File Storage**: Replicated across regions
- **Configuration**: Version controlled in Git

### Disaster Recovery
- **RTO (Recovery Time Objective)**: 4 hours
- **RPO (Recovery Point Objective)**: 24 hours
- **Failover**: Manual promotion of read replica

## 🔧 Development & CI/CD

### Development Flow
```
Local Development → Git Push → CI Pipeline → Staging → Production
```

### CI/CD Pipeline
1. **Code Quality**: Linting, formatting checks
2. **Testing**: Unit, integration, E2E tests
3. **Security Scan**: Dependency vulnerabilities
4. **Build**: Docker images
5. **Deploy**: Rolling update to Kubernetes

## 📈 Performance Targets

### Application Performance
- **API Response Time**: < 200ms (p95)
- **Page Load Time**: < 2 seconds
- **Time to Interactive**: < 3 seconds
- **Concurrent Users**: 10,000
- **Uptime**: 99.9%

### AI Performance
- **Strategic Model Response**: < 3 seconds
- **Execution Model Response**: < 500ms
- **Model Router Decision**: < 50ms
- **AI Cost per User**: < $0.50/month (average)

### Voice Interaction Performance
- **Speech-to-Text Latency**: < 500ms (streaming)
- **Text-to-Speech Latency**: < 400ms (standard), < 300ms (premium)
- **End-to-End Voice Response**: < 2 seconds
- **Voice Recognition Accuracy**: > 95%

## 💰 AI Cost Analysis & Projections

### Cost Breakdown per 1,000 Users/Month

#### Text-Based AI Usage
- **Strategic Tasks** (20% of requests): ~$50
  - Average 100 requests/user × 0.2 × $0.025/request
- **Execution Tasks** (80% of requests): ~$8
  - Average 100 requests/user × 0.8 × $0.001/request
- **Total Text AI**: ~$58/month

#### Voice Interaction Usage (if 30% adoption)
- **Speech-to-Text**: ~$54
  - 300 users × 10 min/month × $0.006/min
- **Text-to-Speech (Standard)**: ~$45
  - 300 users × 10K chars/month × $0.015/1K
- **Text-to-Speech (Premium - 10% users)**: ~$54
  - 30 users × 10K chars/month × $0.18/1K
- **Total Voice**: ~$153/month

#### Total AI Costs
- **Per 1,000 users**: ~$211/month
- **Per user average**: ~$0.21/month
- **With 50% margin**: ~$0.42/user/month pricing

### Cost Optimization Achieved
- **Single Model Approach**: ~$250/1K users (GPT-4 only)
- **Multi-Model Approach**: ~$58/1K users (78% savings)
- **With Caching**: Additional 20-30% reduction possible

### Scaling Projections
| Users | Monthly AI Cost | Cost per User |
|-------|-----------------|---------------|
| 1K    | $211           | $0.21         |
| 10K   | $1,900         | $0.19         |
| 100K  | $17,000        | $0.17         |
| 1M    | $150,000       | $0.15         |

*Note: Costs decrease per user due to better caching and volume discounts*

---

This architecture is designed for scalability, maintainability, and performance while keeping infrastructure costs reasonable for a startup.