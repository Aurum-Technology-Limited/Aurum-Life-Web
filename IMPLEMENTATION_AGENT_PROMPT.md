# Implementation Agent Prompt: Aurum Life AI Architecture Enhancement

## 🎯 Mission
You are tasked with implementing the comprehensive AI architecture enhancement for Aurum Life, transforming it from a rule-based task management system into an intelligent life operating system powered by an LLM-Augmented Hierarchical Reasoning Model (HRM).

## 📚 Required Reading Order
Read these documents in the following sequence to understand the full scope:

### 1. Strategic Overview
- `/workspace/Aurum Architecture and Strategy/README.md` - Start here for overall structure
- `/workspace/Aurum Architecture and Strategy/Product & Design/EXECUTION_PRD_MVP_WEB_2025.md` - Main execution guide

### 2. Technical Architecture
- `/workspace/Aurum Architecture and Strategy/Technical Documents/SYSTEM_ARCHITECTURE.md` - System design
- `/workspace/Aurum Architecture and Strategy/Technical Documents/aurum_life_hrm_phase3_prd.md` - Detailed HRM specifications
- `/workspace/Aurum Architecture and Strategy/Technical Documents/DATABASE_CHANGES_REQUIRED.md` - Database migrations needed
- `/workspace/Aurum Architecture and Strategy/Technical Documents/DATABASE_MIGRATION_PLAN.md` - Migration strategy

### 3. Product & Design Requirements
- `/workspace/Aurum Architecture and Strategy/Product & Design/aurum_life_hrm_ui_epics_user_stories.md` - UI/UX requirements
- `/workspace/Aurum Architecture and Strategy/Product & Design/aurum_life_new_screens_specification.md` - New screen designs
- `/workspace/Aurum Architecture and Strategy/Product & Design/aurum_life_wireframes_web.md` - Web wireframes
- `/workspace/Aurum Architecture and Strategy/Product & Design/aurum_life_wireframes_mobile.md` - Mobile wireframes

### 4. Engineering Standards
- `/workspace/Aurum Architecture and Strategy/Technical Documents/ENGINEERING_HANDBOOK.md` - Development standards
- `/workspace/Aurum Architecture and Strategy/Technical Documents/API_DOCUMENTATION_TEMPLATE.md` - API specifications
- `/workspace/Aurum Architecture and Strategy/Technical Documents/CODE_REFACTORING_GUIDE.md` - Refactoring guidelines

### 5. AI Implementation
- `/workspace/Aurum Architecture and Strategy/Technical Documents/RAG_IMPLEMENTATION_GUIDE.md` - RAG system setup
- `/workspace/Aurum Architecture and Strategy/Legal & Compliance/AI_ETHICS_GUIDELINES.md` - AI ethics to follow

## 🏗️ Implementation Phases

### Phase 1: Database Foundation (Priority: CRITICAL)
1. **Create Database Migrations**
   - Location: `/workspace/backend/migrations/`
   - Create numbered SQL files for each table (001_create_insights_table.sql, etc.)
   - Tables to create:
     - `public.insights` - Core blackboard for AI insights
     - `public.hrm_rules` - Hierarchical reasoning rules
     - `public.hrm_user_preferences` - User AI preferences
     - `public.hrm_feedback_log` - Feedback tracking
     - `public.blackboard_subscribers` - Pub/sub for insights
     - `public.reasoning_cache` - Performance optimization
     - `public.hierarchy_snapshots` - Historical tracking

2. **Update Existing Tables**
   - Add columns to existing tables as specified in DATABASE_CHANGES_REQUIRED.md
   - Create indexes for performance optimization
   - Set up foreign key relationships

3. **pgvector Setup**
   - Enable pgvector extension
   - Create vector columns for semantic search
   - Implement embedding tables as per RAG_IMPLEMENTATION_GUIDE.md

### Phase 2: Backend Services (Priority: HIGH)
1. **HRM Service Implementation**
   - Location: `/workspace/backend/hrm_service.py`
   - Implement the Hierarchical Reasoning Model
   - Create rule engine for PAPT hierarchy
   - Integrate with Gemini 2.0-flash API

2. **Blackboard System**
   - Location: `/workspace/backend/blackboard_service.py`
   - Implement pub/sub pattern for insights
   - Create insight generation and storage logic
   - Build caching layer for performance

3. **API Endpoints**
   - Update `/workspace/backend/server.py` with new endpoints:
     - `/api/insights/*` - Insight management
     - `/api/hrm/*` - HRM configuration
     - `/api/ai-coach/*` - Enhanced AI coach
     - `/api/feedback/*` - Feedback collection

4. **Integration Services**
   - Update existing services to use HRM
   - Modify scoring_engine.py to incorporate AI reasoning
   - Enhance ai_coach_service.py with HRM capabilities

### Phase 3: Frontend Implementation (Priority: HIGH)
1. **New Components**
   - Location: `/workspace/frontend/src/components/`
   - Create components as specified in wireframes:
     - `InsightCard` - Display AI insights
     - `ReasoningPath` - Show hierarchical reasoning
     - `AICoachChat` - Enhanced chat interface
     - `FeedbackDialog` - Collect user feedback
     - `ConfidenceIndicator` - Show AI confidence

2. **New Screens**
   - Implement screens from `aurum_life_new_screens_specification.md`:
     - Insights Dashboard
     - AI Coach Enhanced View
     - HRM Preferences
     - Feedback & Learning Center

3. **State Management**
   - Update React Query hooks for new endpoints
   - Implement real-time updates via Supabase Realtime
   - Add caching for insights and reasoning

4. **UI/UX Enhancements**
   - Apply Aurum Life design system (gold gradient theme)
   - Implement responsive layouts from wireframes
   - Add animations for insight updates

### Phase 4: Integration & Testing (Priority: MEDIUM)
1. **Integration Testing**
   - Test HRM reasoning across all hierarchy levels
   - Verify insight generation and storage
   - Test user feedback loop

2. **Performance Optimization**
   - Implement caching strategies
   - Optimize database queries
   - Add monitoring for AI response times

3. **Migration Scripts**
   - Create data migration scripts
   - Test migration on staging environment
   - Prepare rollback procedures

## 🛠️ Technical Stack & Tools

### Current Stack (Maintain Compatibility)
- **Frontend**: React 19.0.0, Tailwind CSS, TanStack Query
- **Backend**: FastAPI, Python 3.11+, Supabase
- **Database**: PostgreSQL with pgvector
- **AI**: Gemini 2.0-flash via emergentintegrations
- **Auth**: Supabase Auth with JWT

### New Integrations
- **Caching**: Redis for insight caching
- **Queue**: Celery for async AI processing
- **Monitoring**: Performance tracking for AI operations

## 📋 Implementation Checklist

### Database Layer
- [ ] Create all migration files in `/workspace/backend/migrations/`
- [ ] Test migrations on local Supabase instance
- [ ] Create indexes for performance
- [ ] Set up pgvector for semantic search
- [ ] Implement RLS policies for new tables

### Backend Layer
- [ ] Implement HRM service with rule engine
- [ ] Create blackboard service with pub/sub
- [ ] Add new API endpoints to server.py
- [ ] Update existing services for HRM integration
- [ ] Implement caching layer
- [ ] Add error handling and logging
- [ ] Create background jobs for async processing

### Frontend Layer
- [ ] Create all new React components
- [ ] Implement new screens and routes
- [ ] Update state management for HRM
- [ ] Add real-time insight updates
- [ ] Implement responsive designs
- [ ] Add loading states and error handling
- [ ] Create feedback collection flows

### Testing & Deployment
- [ ] Write unit tests for HRM logic
- [ ] Create integration tests for API
- [ ] Test UI components and flows
- [ ] Performance test AI operations
- [ ] Create deployment scripts
- [ ] Document API changes
- [ ] Update user documentation

## 🚨 Critical Requirements

1. **Backward Compatibility**: All existing features must continue working
2. **Performance**: AI responses must be under 3 seconds
3. **Data Integrity**: No data loss during migration
4. **Security**: Maintain RLS policies and auth requirements
5. **Scalability**: Design for 10,000+ concurrent users

## 📝 Development Guidelines

1. **Code Style**: Follow ENGINEERING_HANDBOOK.md standards
2. **Git Workflow**: Create feature branches for each component
3. **Documentation**: Update API docs as you build
4. **Testing**: Write tests alongside implementation
5. **Reviews**: Self-review against wireframes and PRDs

## 🎯 Success Criteria

1. **Functional Requirements**
   - HRM provides reasoning for all PAPT levels
   - Insights are generated and stored correctly
   - User feedback is collected and processed
   - AI coach uses hierarchical reasoning
   - All new screens match wireframe specifications

2. **Performance Requirements**
   - AI response time < 3 seconds
   - Page load time < 2 seconds
   - Database queries optimized with indexes
   - Caching reduces redundant AI calls

3. **Quality Requirements**
   - 90%+ test coverage for new code
   - No regression in existing features
   - Responsive design works on all devices
   - Accessibility standards met

## 🔄 Implementation Order

1. **First**: Database migrations and schema updates
2. **Second**: Backend HRM and blackboard services
3. **Third**: API endpoints and service integration
4. **Fourth**: Frontend components and screens
5. **Fifth**: Integration, testing, and optimization
6. **Finally**: Deployment preparation and documentation

## 📞 Resources & Support

- Architecture questions: Refer to SYSTEM_ARCHITECTURE.md
- UI/UX questions: Check wireframes and design specs
- API questions: See API_DOCUMENTATION_TEMPLATE.md
- Database questions: Review DATABASE_MIGRATION_PLAN.md
- AI implementation: Follow RAG_IMPLEMENTATION_GUIDE.md

## 🚀 Getting Started

1. Set up your local development environment
2. Review all documents in the order specified above
3. Create a development branch: `feature/hrm-implementation`
4. Start with database migrations (Phase 1)
5. Test each component as you build
6. Commit frequently with descriptive messages

## 🗄️ Supabase Database Tasks - IMPORTANT

Since you cannot directly execute SQL queries on the Supabase instance, you must:

1. **Generate SQL Queries**: For each database change, provide the complete SQL query that needs to be executed
2. **Ask for Confirmation**: Before proceeding with dependent tasks, ask the user to confirm that they have executed the SQL queries
3. **Provide Step-by-Step Instructions**: For each Supabase task, provide:
   - The exact SQL query to execute
   - Where to execute it (Supabase SQL Editor)
   - What to verify after execution
   - Any RLS policies or permissions that need to be set

### Example Interaction Pattern:

```
Agent: "I need to create the insights table in Supabase. Please execute the following SQL query in your Supabase SQL Editor:

[SQL QUERY HERE]

After execution, please confirm:
1. The table was created successfully
2. Any errors encountered
3. If you need me to generate the RLS policies for this table

Once confirmed, I'll proceed with the next migration."
```

### Key Supabase Tasks Requiring User Execution:

1. **Database Migrations**
   - Creating new tables
   - Adding columns to existing tables
   - Creating indexes
   - Setting up foreign key relationships

2. **pgvector Setup**
   - Enabling the pgvector extension
   - Creating vector columns
   - Setting up embedding tables

3. **RLS (Row Level Security) Policies**
   - Creating security policies for new tables
   - Updating policies for modified tables

4. **Database Functions & Triggers**
   - Creating stored procedures
   - Setting up triggers for automated tasks

5. **Permissions & Roles**
   - Granting permissions to service roles
   - Setting up API access controls

Always provide complete, tested SQL queries and wait for user confirmation before assuming the database changes are in place.

Remember: The goal is to transform Aurum Life into an intelligent system that truly understands and reasons about users' life goals. Every implementation decision should support this vision.

---

**Note**: This is a living document. Update it as you discover new requirements or make architectural decisions during implementation.