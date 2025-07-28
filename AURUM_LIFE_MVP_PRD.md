# Aurum Life MVP - Product Requirements Document (PRD)

## Executive Summary

Aurum Life is a personal growth and productivity platform built on the concept of **vertical alignment** - organizing life from high-level pillars down to daily tasks. This PRD defines the Minimum Viable Product (MVP) focusing on core features that deliver immediate value while maintaining simplicity.

**Core Value Proposition**: Help users align their daily actions with their life goals through a hierarchical task management system that provides clarity, focus, and measurable progress.

## Product Vision

Create a streamlined productivity tool that helps users:
- Organize their life into meaningful pillars (major life areas)
- Break down pillars into actionable areas, projects, and tasks
- Focus on what matters most through intelligent prioritization
- Track progress and maintain momentum with visual feedback

## MVP Scope

### ✅ INCLUDED in MVP

#### 1. **Authentication & User Management**
- **Email/Password Authentication**
  - User registration with email verification
  - Secure login/logout
  - Password reset via email
- **Google OAuth Integration**
  - One-click Google sign-in
  - Profile synchronization
- **User Profile Management**
  - Basic profile information (name, email)
  - Profile picture support
  - Account settings

#### 2. **Hierarchical Task Organization**
- **Four-Level Hierarchy**:
  1. **Pillars** - Major life categories (e.g., Career, Health, Relationships)
     - Custom icons and colors
     - Description and purpose
     - Time allocation percentage
  2. **Areas** - Subcategories within pillars
     - Link to parent pillar
     - Importance levels (Low/Medium/High)
     - Custom icons and colors
  3. **Projects** - Specific initiatives within areas
     - Status tracking (Not Started/In Progress/Completed/On Hold)
     - Priority levels (Low/Medium/High/Critical)
     - Deadlines and progress tracking
     - Project icons
  4. **Tasks** - Actionable items within projects
     - Status (Todo/In Progress/Review/Completed)
     - Priority levels
     - Due dates and times
     - Estimated duration
     - Task dependencies
     - Sub-task support

#### 3. **Today View (Primary Interface)**
- **Smart Task Aggregation**
  - All tasks due today across all projects
  - Overdue tasks highlighted
  - Tasks sorted by calculated score (priority × importance × urgency)
- **Quick Actions**
  - Mark tasks complete/incomplete
  - Snooze to tomorrow
  - Quick edit priority
- **Progress Tracking**
  - Daily completion percentage
  - Tasks completed counter
  - Visual progress indicators

#### 4. **Core Task Management**
- **Task CRUD Operations**
  - Create, read, update, delete tasks
  - Bulk operations support
- **Task Features**
  - Rich text descriptions
  - Categories for grouping
  - Completion tracking with timestamps
- **Dependency Management**
  - Set task dependencies
  - Prevent completion of blocked tasks
  - Visual dependency indicators

#### 5. **Basic Scoring System**
- **Automatic Score Calculation**
  - Score = Priority × Importance × Urgency × Completion Factor
  - Updates daily via background job
  - Used for intelligent task sorting
- **Scoring Factors**:
  - Task priority (1-4 scale)
  - Project importance (inherited)
  - Time urgency (based on due date)
  - Completion bonus for maintaining momentum

#### 6. **Essential UI Components**
- **Navigation**
  - Sidebar with hierarchy navigation
  - Breadcrumb navigation
  - Quick search functionality
- **Responsive Design**
  - Mobile-friendly interfaces
  - Touch-optimized interactions
  - Consistent design system
- **Data Tables**
  - Sortable columns
  - Inline editing
  - Pagination for large datasets

#### 7. **Performance Optimizations**
- **Database Indexes** on frequently queried fields
- **Connection Pooling** for database efficiency
- **Caching** for static data
- **Lazy Loading** for improved initial load times
- **Optimized Queries** with projection and aggregation

#### 8. **Basic Email Notifications**
- **Password Reset Emails**
- **Welcome Email on Registration**
- **Email Verification**

### ❌ NOT INCLUDED in MVP

#### 1. **Advanced Features**
- ❌ **AI Coach** - No AI-powered suggestions or insights
- ❌ **Achievements/Gamification** - No badges, levels, or rewards
- ❌ **Journal/Reflection** - No journaling or mood tracking
- ❌ **Learning Courses** - No educational content
- ❌ **Advanced Analytics** - No detailed insights or reports
- ❌ **Kanban Board** - No drag-and-drop task management
- ❌ **Pomodoro Timer** - No time tracking features
- ❌ **File Attachments** - No document upload/management
- ❌ **Resource Library** - No knowledge base features

#### 2. **Complex Task Features**
- ❌ **Recurring Tasks** - No task recurrence patterns
- ❌ **Task Templates** - No reusable task templates
- ❌ **Project Templates** - No project scaffolding
- ❌ **Time Tracking** - No actual time spent tracking
- ❌ **Task Comments** - No collaboration features
- ❌ **Task History** - No audit trail

#### 3. **Advanced Notifications**
- ❌ **Push Notifications** - No browser/mobile push
- ❌ **In-App Notifications** - No notification center
- ❌ **SMS Notifications** - No text message alerts
- ❌ **Custom Notification Rules** - No configurable alerts
- ❌ **Reminder Scheduling** - No advanced reminder options

#### 4. **Collaboration Features**
- ❌ **Team Workspaces** - Single user only
- ❌ **Sharing** - No project/task sharing
- ❌ **Comments/Chat** - No communication features
- ❌ **Activity Feed** - No team activity tracking

#### 5. **Advanced Integrations**
- ❌ **Calendar Sync** - No Google/Outlook calendar integration
- ❌ **Third-party Apps** - No Slack, Trello, etc. integrations
- ❌ **API Access** - No public API for developers
- ❌ **Webhooks** - No event notifications
- ❌ **Import/Export** - No data portability features

#### 6. **Premium Features**
- ❌ **Multiple Workspaces** - One workspace per user
- ❌ **Advanced Permissions** - No role-based access
- ❌ **White Labeling** - No customization options
- ❌ **Priority Support** - Standard support only

## Technical Architecture

### Frontend
- **Framework**: React 18.x
- **Styling**: Tailwind CSS
- **State Management**: TanStack Query (React Query)
- **Routing**: React Router
- **HTTP Client**: Axios
- **Build Tool**: Create React App

### Backend
- **Framework**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth + JWT
- **Task Queue**: Celery with Redis
- **Email Service**: SendGrid
- **File Storage**: Supabase Storage (minimal use)

### Infrastructure
- **Hosting**: To be determined (Cloud provider)
- **CDN**: CloudFlare (for static assets)
- **Monitoring**: Basic health checks
- **Analytics**: Google Analytics (basic)

## User Flows

### 1. **Onboarding Flow**
1. User lands on login page
2. Choose sign-up method (Email or Google)
3. Complete registration
4. Redirect to empty dashboard
5. Prompt to create first pillar
6. Guide through creating area → project → task

### 2. **Daily Usage Flow**
1. User logs in
2. Lands on Today view
3. Reviews tasks for the day
4. Completes tasks throughout the day
5. Uses quick actions for task management
6. Checks progress at end of day

### 3. **Planning Flow**
1. Navigate to Pillars section
2. Create/Edit pillar structure
3. Add areas within pillars
4. Create projects in areas
5. Break down projects into tasks
6. Set priorities and deadlines

## Success Metrics

### Primary KPIs
- **Onboarding Completion Rate**: Target 60%+
- **Daily Active Users (DAU)**: Growth of 10% month-over-month
- **Task Completion Rate**: Average 70%+ of daily tasks completed
- **User Retention**: 40%+ users active after 30 days

### Performance Metrics
- **Page Load Time**: < 3 seconds
- **API Response Time**: P95 < 150ms
- **Uptime**: 99.9% availability
- **Error Rate**: < 0.1% of requests

### User Satisfaction
- **Net Promoter Score (NPS)**: Target 40+
- **Support Ticket Volume**: < 5% of MAU
- **Feature Adoption**: 80%+ using hierarchy features

## MVP Timeline

### Phase 1: Foundation (Weeks 1-2)
- Set up infrastructure
- Implement authentication
- Create basic data models
- Deploy development environment

### Phase 2: Core Features (Weeks 3-6)
- Build hierarchy CRUD operations
- Implement Today view
- Add task management
- Create scoring system

### Phase 3: Polish (Weeks 7-8)
- UI/UX refinements
- Performance optimization
- Bug fixes
- User testing

### Phase 4: Launch Preparation (Week 9)
- Production deployment
- Monitoring setup
- Documentation
- Marketing website

## Risk Mitigation

### Technical Risks
- **Database Performance**: Mitigated with proper indexing and caching
- **Scalability**: Start with vertical scaling, plan for horizontal
- **Security**: Regular security audits, proper authentication

### Product Risks
- **Feature Creep**: Strict adherence to MVP scope
- **User Adoption**: Focus on core value proposition
- **Competition**: Differentiate with vertical alignment concept

## Post-MVP Roadmap

### Version 1.1 (Month 2-3)
- Recurring tasks
- Basic project templates
- Enhanced notifications

### Version 1.2 (Month 4-5)
- Kanban board view
- Time tracking
- Basic analytics

### Version 2.0 (Month 6+)
- AI-powered insights
- Team collaboration
- Mobile apps
- Advanced integrations

## Conclusion

This MVP focuses on delivering a simple, fast, and effective task management system built on the unique vertical alignment concept. By explicitly excluding complex features, we can launch quickly, gather user feedback, and iterate based on real usage data.

The key to success is maintaining laser focus on the core value proposition: helping users align their daily actions with their life goals through an intuitive hierarchical system.