# Aurum Architecture and Strategy Documentation

This folder contains all architectural, strategic, and business documentation for Aurum Life's enhanced AI-powered personal operating system.

## 📁 Document Structure

### 🎯 Core Execution Documents

1. **[EXECUTION_PRD_MVP_WEB_2025.md](./EXECUTION_PRD_MVP_WEB_2025.md)**
   - **Purpose**: Main execution document for development agents
   - **Content**: Complete implementation requirements for MVP web app with enhanced AI architecture
   - **Status**: Active - Use this for implementation

### 🏗️ Technical Architecture

2. **[aurum_life_hrm_phase3_prd.md](./aurum_life_hrm_phase3_prd.md)**
   - **Purpose**: Detailed technical specifications for Hierarchical Reasoning Model
   - **Content**: Database schemas, backend services, API specifications
   - **Key Sections**: HRM implementation, Blackboard architecture, Rules engine

### 🎨 UI/UX Design Documents

3. **[aurum_life_hrm_ui_epics_user_stories.md](./aurum_life_hrm_ui_epics_user_stories.md)**
   - **Purpose**: Complete UI/UX requirements as epics and user stories
   - **Content**: 8 major epics with 40+ detailed user stories
   - **Key Features**: AI Intelligence Dashboard, Contextual AI Analysis, Feedback Loop

4. **[aurum_life_new_screens_specification.md](./aurum_life_new_screens_specification.md)**
   - **Purpose**: Specifications for all new screens in the enhanced architecture
   - **Content**: Layout, features, and purpose for 10 new screens
   - **Platforms**: Both web and mobile specifications

5. **[aurum_life_wireframes_web.md](./aurum_life_wireframes_web.md)**
   - **Purpose**: Detailed web wireframes with exact styling specifications
   - **Content**: Pixel-perfect layouts with color codes, spacing, typography
   - **Design System**: Maintains Aurum Life's dark theme with AI accent colors

6. **[aurum_life_wireframes_mobile.md](./aurum_life_wireframes_mobile.md)**
   - **Purpose**: Mobile-specific wireframes optimized for touch
   - **Content**: Touch targets, gestures, bottom sheets, mobile patterns
   - **Considerations**: Device safe areas, thumb reach, one-handed use

### 📂 Archive Folder

Contains previous versions of PRDs and documentation for historical reference:
- PRD_AurumLife_v2.md
- PRD_AurumLife_v3_CurrentState.md
- AURUM_LIFE_PRD.md
- COMPREHENSIVE_PRD_2025.md

## 🚀 Implementation Guide

### For Development Agents:

1. **Start with**: `EXECUTION_PRD_MVP_WEB_2025.md` - This is your main guide
2. **Reference**: Technical details in `aurum_life_hrm_phase3_prd.md`
3. **Build UI from**: Wireframes and specifications documents
4. **Follow user stories in**: `aurum_life_hrm_ui_epics_user_stories.md`

### Key Implementation Order:

**Week 1**: Database setup and core HRM services
**Week 2**: Essential UI components and API integration  
**Week 3**: Advanced features and AI interactions
**Week 4**: Testing, optimization, and polish

## 🎯 Project Vision

Transform Aurum Life from a task management system into an intelligent life operating system that:
- Understands the hierarchical relationships between life goals and daily tasks
- Provides AI-powered reasoning for every prioritization decision
- Learns from user feedback to improve recommendations
- Offers proactive guidance through natural language interaction

## 🔧 Technical Stack

- **Frontend**: React 19.0.0, Tailwind CSS, TanStack Query
- **Backend**: FastAPI, Python, Supabase (PostgreSQL)
- **AI**: Gemini 2.0-flash via emergentintegrations
- **Architecture**: Hierarchical Reasoning Model with Blackboard pattern

## 📊 Success Metrics

- Task completion rate improvement: 25%
- User engagement with AI insights: 80% daily
- Feedback submission rate: 40%
- Response time for AI analysis: <3 seconds

## 🤝 Contributing

When adding new documentation to this folder:
1. Use clear, descriptive filenames
2. Include a header with purpose and last updated date
3. Reference related documents where applicable
4. Update this README with the new document

---

**Last Updated**: January 2025  
**Maintained by**: Aurum Life Development Team