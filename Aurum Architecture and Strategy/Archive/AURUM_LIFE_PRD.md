# Aurum Life - Product Requirements Document (PRD)
**Version:** 2.0  
**Last Updated:** January 2025  
**Status:** Production Ready

---

## Executive Summary

Aurum Life is a comprehensive personal growth and productivity web application designed for hierarchical task management, reflective journaling, and continuous learning. Built with a modern tech stack (React.js, FastAPI, Supabase), it provides users with structured goal-setting frameworks, AI-powered coaching features, and data-driven insights to support their personal development journey.

---

## Product Overview

### Vision
To create the ultimate personal growth companion that transforms scattered goals into structured, actionable journeys with intelligent guidance and meaningful progress tracking.

### Mission
Enable individuals to build lasting habits, achieve meaningful goals, and gain deep insights into their personal growth through structured hierarchical organization and AI-powered coaching.

### Target Users
- **Primary:** Goal-oriented professionals and students seeking structured personal development
- **Secondary:** Life coaches, productivity enthusiasts, and individuals transitioning between major life phases

---

## Core Features & Functionality

### 1. **Hierarchical Life Organization System**

#### 1.1 **Pillars** 🏛️
- **Purpose:** Top-level life domains that define core focus areas
- **Features:**
  - Create/Edit/Delete pillars with custom icons and colors
  - Time allocation percentage tracking
  - Visual statistics (areas, projects, tasks count)
  - Progress visualization with completion percentages
  - Archive/restore functionality
- **Data Fields:** Name, description, icon, color, time allocation %, sort order, creation date
- **Navigation:** Click-through to filtered Areas view

#### 1.2 **Areas** 🎯
- **Purpose:** Specific life domains within pillars (e.g., "Health & Fitness" under "Personal Growth")
- **Features:**
  - Pillar association with visual hierarchy
  - Importance levels (1-5 scale: Low to Critical)
  - Project tracking and progress visualization
  - Archive/restore functionality
  - Color-coded organization
  - Advanced filtering (by pillar, archived status)
- **Data Fields:** Name, description, icon, color, pillar link, importance level, archive status
- **Visual Elements:** Progress bars, completion statistics, project counts

#### 1.3 **Projects** 📁
- **Purpose:** Concrete initiatives within areas with defined outcomes
- **Features:**
  - Area association for hierarchical structure
  - Status tracking (Not Started, In Progress, Completed, On Hold)
  - Priority levels (Low, Medium, High)
  - Importance scoring (1-5 scale)
  - Deadline management
  - Progress percentage calculation
  - Task relationship management
- **Data Fields:** Name, description, icon, area link, deadline, status, priority, importance, completion %
- **AI Integration:** Project decomposition assistance

#### 1.4 **Tasks** ✅
- **Purpose:** Actionable items that drive project completion
- **Features:**
  - Project and parent task relationships
  - Status workflow (Todo, In Progress, Review, Completed)
  - Priority and due date management
  - Time tracking (estimated vs. actual duration)
  - Dependency management
  - Kanban board organization
  - Sub-task support with completion requirements
- **Data Fields:** Name, description, project link, parent task, status, priority, due date/time, category, dependencies
- **Advanced Features:** Recurring tasks, smart reminders, dependency blocking

### 2. **AI Coach MVP Features** 🤖

#### 2.1 **Contextual "Why" Statements**
- **Purpose:** Provide motivational context by connecting tasks to higher-level goals
- **Features:**
  - Automatic analysis of task-to-pillar relationships
  - Personalized motivation statements
  - Vertical alignment explanations
  - Task prioritization insights
- **API Endpoint:** `GET /api/ai/task-why-statements`
- **Integration:** Embedded in Today view and Tasks management

#### 2.2 **Project Decomposition Assistant**
- **Purpose:** Overcome "blank slate" problem when starting new projects
- **Features:**
  - Template-based task suggestions (Learning, Health, Career, Work, General)
  - Intelligent task generation with priorities and duration estimates
  - Customizable suggestions based on project context
  - One-click task creation from suggestions
- **API Endpoint:** `POST /api/ai/decompose-project`
- **Integration:** Built into project creation workflow

#### 2.3 **Daily Reflection & Streak System**
- **Purpose:** Build consistent self-reflection habits and track personal growth
- **Features:**
  - Daily reflection prompts with structured questions
  - Completion scoring (1-10 scale)
  - Mood tracking with preset options
  - Accomplishment and challenge documentation
  - Daily streak counter with milestone recognition
  - Historical reflection browsing
- **Data Fields:** Reflection text, completion score, mood, accomplishments, challenges, tomorrow focus
- **API Endpoints:** 
  - `POST /api/ai/daily-reflection`
  - `GET /api/ai/daily-reflections`
  - `GET /api/ai/daily-streak`

### 3. **Today View** 📅
- **Purpose:** Focused daily task management and prioritization
- **Features:**
  - Curated daily task list
  - Available task selection from broader project pool
  - AI-powered task recommendations
  - Progress tracking (completed vs. total)
  - Contextual "why" statements for motivation
  - Time-blocked scheduling integration
- **Smart Features:** Intelligent task prioritization, dependency-aware suggestions

### 4. **Journaling System** 📖
- **Purpose:** Reflective writing and personal documentation
- **Features:**
  - Rich text journal entries
  - Date-based organization
  - Mood and category tagging
  - Search and filtering capabilities
  - File attachment support
  - "On This Day" memories feature
- **Analytics:** Writing stats, entry frequency, mood patterns

### 5. **Insights & Analytics** 📊
- **Purpose:** Data-driven personal growth insights
- **Features:**
  - Progress visualization across all hierarchy levels
  - Completion rate tracking
  - Time allocation analysis
  - Productivity pattern identification
  - Goal achievement metrics
  - Trend analysis with historical data
- **Visual Elements:** Interactive charts, progress bars, statistical summaries

### 6. **Dashboard** 🏠
- **Purpose:** Central hub with personalized overview
- **Features:**
  - Welcome messaging with user context
  - Key statistics cards (streaks, habits, learning, achievements)
  - AI Coach recommendations
  - Daily streak tracker with reflection prompt
  - Quick navigation to all major sections
- **Performance:** Optimized loading with <3 second target

### 7. **File Management & Attachments** 📎
- **Purpose:** Contextual file organization and resource management
- **Features:**
  - Direct parent-child file relationships
  - Drag-and-drop upload interface
  - Progress indicators for uploads
  - File preview and management
  - Multiple file type support (documents, images, archives)
  - Chunked upload for large files
- **Integration:** Embedded in Projects and Tasks workflows

### 8. **Authentication System** 🔐
- **Purpose:** Secure user access and data protection
- **Features:**
  - Google OAuth 2.0 integration
  - Traditional email/password authentication
  - JWT token-based session management
  - Hybrid authentication support
  - User profile management
  - Password reset functionality
- **Security:** Token validation, session expiration, secure endpoints

### 9. **Notification System** 🔔
- **Purpose:** Timely reminders and engagement
- **Features:**
  - Browser push notifications
  - Task due date reminders
  - Customizable notification preferences
  - Quiet hours configuration
  - Multiple notification channels
- **Types:** Task due, overdue, deadlines, achievements, dependency updates

### 10. **Project Templates** 📋
- **Purpose:** Rapid project setup with proven structures
- **Features:**
  - Pre-built project templates
  - Template customization
  - Usage tracking
  - Template sharing capabilities
- **Categories:** Learning, Health, Career, Personal, Work

---

## Technical Architecture

### Frontend Stack
- **Framework:** React.js with hooks and functional components
- **State Management:** TanStack Query for server state, Context API for local state
- **Styling:** Tailwind CSS with custom design system
- **Performance:** Code splitting with React.lazy(), memoization with React.memo
- **UI Components:** Custom component library with shadcn/ui integration

### Backend Stack
- **Framework:** FastAPI (Python)
- **Database:** Supabase (PostgreSQL)
- **Authentication:** Hybrid system (Supabase Auth + Google OAuth 2.0)
- **API Design:** RESTful with Pydantic models
- **Performance:** Response time targets <200ms (P95)

### Infrastructure
- **Deployment:** Kubernetes cluster
- **Development:** Hot reload enabled for both frontend and backend
- **Environment:** Docker containerization
- **Performance Monitoring:** Built-in logging and performance tracking

---

## User Experience Features

### Design System
- **Theme:** Dark mode with yellow accent (#F4B400)
- **Typography:** Responsive sizing with dynamic text scaling
- **Icons:** Comprehensive icon picker with emoji support
- **Colors:** Customizable color palettes for organization
- **Layout:** Responsive design with mobile-first approach

### Navigation
- **Structure:** Sidebar navigation with clear section organization
- **Breadcrumbs:** Hierarchical navigation with context awareness
- **Search:** Quick access to content across all sections
- **Shortcuts:** Keyboard shortcuts for power users

### Performance
- **Loading:** <3 second page load targets
- **Caching:** Intelligent data caching with automatic invalidation
- **Optimization:** Lazy loading, code splitting, memoization
- **Error Handling:** Graceful degradation with retry mechanisms

---

## Data Model

### Core Entities
1. **User:** Profile, preferences, authentication
2. **Pillar:** Top-level life domains
3. **Area:** Mid-level organization within pillars
4. **Project:** Concrete initiatives with defined outcomes
5. **Task:** Actionable items with status and dependencies
6. **Journal Entry:** Reflective writing with metadata
7. **Daily Reflection:** Structured self-assessment
8. **Resource:** File attachments with contextual relationships

### Relationships
- Pillar → Areas (one-to-many)
- Area → Projects (one-to-many)  
- Project → Tasks (one-to-many)
- Task → Sub-tasks (one-to-many)
- All entities → Resources (many-to-many attachments)

---

## Security & Privacy

### Data Protection
- JWT token-based authentication
- Secure API endpoints with proper validation
- User data isolation
- HTTPS encryption in production

### Privacy
- User-specific data access controls
- Optional data sharing for AI features
- GDPR compliance considerations
- Local data storage where appropriate

---

## Performance Metrics

### Current Benchmarks
- **Dashboard Load:** <2 seconds
- **API Response Times:** Average <600ms
- **Areas API:** 437ms (85% improvement achieved)
- **Backend Optimization:** 78% improvement in core endpoints
- **Cache Hit Rate:** >90% for frequently accessed data

### Targets
- **P95 Response Time:** <200ms for core APIs
- **Page Load:** <3 seconds for all sections
- **Database Queries:** Optimized with minimal N+1 issues
- **Memory Usage:** Efficient with proper cleanup

---

## Future Roadmap

### Phase 1 (Completed)
- ✅ Core hierarchical system (Pillars → Areas → Projects → Tasks)
- ✅ Basic CRUD operations
- ✅ Authentication system
- ✅ AI Coach MVP features
- ✅ Performance optimizations

### Phase 2 (In Progress)
- 🔄 Advanced Code Splitting implementation
- 🔄 Context Usage optimization
- 🔄 Frontend test coverage improvements
- 🔄 Areas API performance optimization

### Phase 3 (Planned)
- ⏳ Intelligent Today View with smart prioritization
- ⏳ Smart Recurring Tasks
- ⏳ Advanced Task Dependencies
- ⏳ Enhanced reporting and analytics
- ⏳ Mobile application

---

## Success Metrics

### User Engagement
- Daily active users
- Session duration
- Feature adoption rates
- Task completion rates
- Reflection streak maintenance

### Product Performance
- API response times
- Error rates
- User satisfaction scores
- Feature usage analytics
- Performance benchmark achievement

### Business Impact
- User retention rates
- Goal achievement rates
- User feedback sentiment
- Feature request volume
- Technical debt reduction

---

## Conclusion

Aurum Life represents a comprehensive personal development platform that successfully combines structured goal management with intelligent AI assistance. The hierarchical organization system provides clear structure, while AI coaching features add personalized guidance. With strong technical foundations and user-centric design, the product is well-positioned for continued growth and enhancement.

The current production-ready state demonstrates successful achievement of core objectives, with clear pathways for future development and scalability.