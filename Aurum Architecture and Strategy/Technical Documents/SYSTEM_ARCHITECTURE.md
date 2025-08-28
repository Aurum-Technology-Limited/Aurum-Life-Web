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
User Action → React → FastAPI → HRM Service → Gemini API → Blackboard Storage → Response
                                      ↓
                                 Redis Cache
```

### 3. **Real-time Updates Flow**
```
Database Change → Supabase Realtime → WebSocket → React App → UI Update
```

### 4. **File Upload Flow**
```
User Upload → React (Chunked) → FastAPI → Supabase Storage → URL Reference in DB
```

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
├── services/           # Business logic
│   ├── task_service.py
│   ├── project_service.py
│   └── analytics_service.py
├── middleware/         # Custom middleware
│   ├── auth.py
│   └── rate_limit.py
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
│   └── hrm_feedback_log
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
- AI API quota approaching limit

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

- **API Response Time**: < 200ms (p95)
- **Page Load Time**: < 2 seconds
- **Time to Interactive**: < 3 seconds
- **AI Analysis Time**: < 3 seconds
- **Concurrent Users**: 10,000
- **Uptime**: 99.9%

---

This architecture is designed for scalability, maintainability, and performance while keeping infrastructure costs reasonable for a startup.