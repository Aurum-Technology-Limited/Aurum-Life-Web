# Aurum Life System Architecture - Current Production

**Last Updated:** January 2025  
**Document Type:** Technical Architecture Documentation  
**Status:** ✅ Production Ready

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
│  │   Vercel CDN    │     │   Vercel CDN    │     │   Future: React  │         │
│  └────────┬────────┘     └────────┬────────┘     └────────┬────────┘         │
│           │                       │                         │                   │
│           └───────────────────────┴─────────────────────────┘                  │
│                                   │                                             │
├───────────────────────────────────┼─────────────────────────────────────────────┤
│                                   ▼                                             │
│                           VERCEL EDGE NETWORK                                   │
│                        (Global CDN + Edge Functions)                           │
│                                   │                                             │
├───────────────────────────────────┼─────────────────────────────────────────────┤
│                          APPLICATION LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                   │                                             │
│  ┌────────────────────────────────┴────────────────────────────────┐          │
│  │                        VERCEL PLATFORM                          │          │
│  │                                                                  │          │
│  │  ┌─────────────────────────────────────────────────────────────┐ │          │
│  │  │                FRONTEND (React SPA)                         │ │          │
│  │  │                                                             │ │          │
│  │  │  • React 18 with Hooks & Context                          │ │          │
│  │  │  • Tailwind CSS for Styling                               │ │          │
│  │  │  • Apollo Client for GraphQL                              │ │          │
│  │  │  • TanStack Query for Data Management                     │ │          │
│  │  │  • Supabase Auth for Authentication                      │ │          │
│  │  │  • PostHog for Analytics (Ad-blocker Resistant)          │ │          │
│  │  └─────────────────────────────────────────────────────────────┘ │          │
│  └─────────────────────────────────────────────────────────────────┘          │
│                                   │                                             │
├───────────────────────────────────┼─────────────────────────────────────────────┤
│                                   ▼                                             │
│                          SUPABASE CLOUD PLATFORM                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                   │                                             │
│  ┌────────────────────────────────┴────────────────────────────────┐          │
│  │                    SUPABASE SERVICES                            │          │
│  │                                                                  │          │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │          │
│  │  │   AUTH SERVICE  │  │  EDGE FUNCTIONS │  │   REALTIME      │ │          │
│  │  │                 │  │                 │  │   SERVICE       │ │          │
│  │  │ • JWT Tokens    │  │ • Deno Runtime  │  │ • WebSockets    │ │          │
│  │  │ • OAuth (Google)│  │ • TypeScript    │  │ • Live Updates  │ │          │
│  │  │ • Email/Password│  │ • REST API      │  │ • Subscriptions │ │          │
│  │  │ • Session Mgmt  │  │ • CORS Config   │  │ • Real-time Sync│ │          │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘ │          │
│  │                                                                  │          │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │          │
│  │  │   DATABASE      │  │    STORAGE      │  │   MONITORING    │ │          │
│  │  │   (PostgreSQL)  │  │   (S3 Compatible)│  │   & ANALYTICS   │ │          │
│  │  │                 │  │                 │  │                 │ │          │
│  │  │ • Row Level Sec │  │ • File Uploads  │  │ • Performance   │ │          │
│  │  │ • ACID Compliant│  │ • CDN Delivery  │  │ • Error Tracking│ │          │
│  │  │ • Full-text Search│ │ • Image Resize │  │ • Usage Metrics │ │          │
│  │  │ • Extensions    │  │ • Secure Access │  │ • Health Checks │ │          │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘ │          │
│  └─────────────────────────────────────────────────────────────────┘          │
│                                   │                                             │
├───────────────────────────────────┼─────────────────────────────────────────────┤
│                                   ▼                                             │
│                          EXTERNAL SERVICES                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                 │
│  │   OPENAI API    │  │   GEMINI API    │  │   SENDGRID      │                 │
│  │                 │  │                 │  │                 │                 │
│  │ • GPT-4o-mini   │  │ • Gemini 2.5    │  │ • Email Service │                 │
│  │ • AI Insights   │  │ • Flash Lite    │  │ • Notifications │                 │
│  │ • Smart Features│  │ • Fast Responses│  │ • Templates     │                 │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                 │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Technology Stack

### Frontend Technologies
- **Framework:** React 18 with Hooks and Context API
- **Styling:** Tailwind CSS with custom design system
- **State Management:** React Context + TanStack Query
- **Data Fetching:** Apollo Client (GraphQL) + Axios (REST)
- **Authentication:** Supabase Auth with JWT tokens
- **Build Tool:** Create React App with CRACO
- **Deployment:** Vercel with automatic CI/CD

### Backend Technologies
- **Runtime:** Deno (Supabase Edge Functions)
- **Language:** TypeScript
- **API:** RESTful API with JWT authentication
- **Database:** PostgreSQL with Row Level Security
- **Authentication:** Supabase Auth
- **Real-time:** Supabase Realtime
- **Storage:** Supabase Storage (S3 compatible)

### Infrastructure
- **Frontend Hosting:** Vercel (Global CDN)
- **Backend Hosting:** Supabase Cloud (Edge Functions)
- **Database:** Supabase PostgreSQL
- **CDN:** Vercel Edge Network
- **Monitoring:** Vercel Analytics + Supabase Monitoring
- **Domain:** Custom domain support

---

## 🔐 Security Architecture

### Authentication Flow
```
1. User Login Request
   ↓
2. Supabase Auth Service
   ↓
3. JWT Token Generation
   ↓
4. Token Storage (HttpOnly Cookie)
   ↓
5. API Request with JWT
   ↓
6. Token Validation
   ↓
7. User Data Access (RLS)
```

### Data Protection
- **Row Level Security (RLS):** All database tables have RLS policies
- **JWT Tokens:** Secure token-based authentication
- **HTTPS Everywhere:** All communications encrypted
- **CORS Configuration:** Properly configured for production
- **API Security:** All endpoints require authentication
- **Data Isolation:** Users can only access their own data

---

## 📊 Data Architecture

### Database Schema
```sql
-- Core Tables
user_profiles          -- User account information
tasks                  -- Task management
projects               -- Project organization
areas                  -- Life area categorization
pillars                -- Core life pillars
journal_entries        -- Daily journaling
alignment_scores       -- Progress tracking

-- Supporting Tables
ai_interactions        -- AI feature usage
daily_reflections      -- Daily check-ins
sleep_reflections      -- Sleep tracking
feedback               -- User feedback
username_change_records -- Username history
```

---

## 🚀 Deployment Architecture

### Production Deployment
- **Frontend:** Vercel (https://aurum-life-web.vercel.app)
- **Backend:** Supabase Edge Functions
- **Database:** Supabase PostgreSQL
- **CDN:** Vercel Edge Network (Global)
- **Domain:** Custom domain support

### CI/CD Pipeline
```
GitHub Push (main branch)
    ↓
Vercel Build Trigger
    ↓
Environment Variable Injection
    ↓
React Build Process
    ↓
Static Asset Generation
    ↓
Global CDN Deployment
    ↓
Health Check & Monitoring
```

---

## 📈 Performance Architecture

### Frontend Performance
- **Code Splitting:** Lazy loading of components
- **Image Optimization:** Automatic image optimization
- **Caching:** Browser and CDN caching
- **Bundle Size:** Tree shaking and minification
- **Core Web Vitals:** Optimized for Google metrics

### Backend Performance
- **Edge Functions:** Global distribution
- **Database Indexing:** Optimized queries
- **Connection Pooling:** Managed by Supabase
- **Caching:** Built-in caching layers
- **CDN:** Global content delivery

---

## 🎯 Key Architecture Decisions

### Why Vercel + Supabase?
1. **Developer Experience:** Excellent DX with modern tools
2. **Performance:** Global CDN and edge functions
3. **Scalability:** Automatic scaling and optimization
4. **Security:** Built-in security features
5. **Cost Efficiency:** Pay-as-you-scale pricing
6. **Maintenance:** Minimal operational overhead

### Why React + TypeScript?
1. **Type Safety:** Compile-time error detection
2. **Developer Productivity:** Rich IDE support
3. **Maintainability:** Easier code maintenance
4. **Ecosystem:** Large community and libraries
5. **Performance:** Optimized rendering
6. **Future-Proof:** Modern web standards

---

**Document Status:** ✅ Current  
**Last Review:** January 2025  
**Next Review:** February 2025  
**Maintainer:** Development Team
