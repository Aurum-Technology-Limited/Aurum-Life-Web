# Aurum Life - Technical Documentation

**Version:** 2.0.0 (Refactored Architecture)  
**Last Updated:** August 2025  

---

## 🏗️ **ARCHITECTURE OVERVIEW**

### **System Architecture:**
```
Frontend (React) ←→ Backend (FastAPI) ←→ Database (Supabase)
     ↓                    ↓                    ↓
- React Query         - Service Classes    - PostgreSQL
- Context API         - Pydantic Models    - Real-time sync
- Tailwind CSS        - Auth middleware    - Row Level Security
```

### **Deployment Architecture:**
```
Kubernetes Cluster
├── Frontend Service (Port 3000)
├── Backend Service (Port 8001) 
└── Supervisor Process Manager
```

---

## 📁 **PROJECT STRUCTURE**

### **Frontend Structure:**
```
frontend/src/
├── components/           # React components
│   ├── auth/            # Authentication components
│   ├── dashboard/       # Dashboard and main views
│   ├── ui/              # Reusable UI components
│   └── forms/           # Form components
├── contexts/            # React contexts for state management
├── services/            # API services and utilities
├── hooks/               # Custom React hooks
├── utils/               # Utility functions
└── data/                # Static data and templates
```

### **Backend Structure:**
```
backend/
├── supabase_auth_endpoints.py    # Authentication endpoints
├── supabase_client.py            # Database client
├── services.py                   # Business logic services
├── models.py                     # Pydantic data models
├── server.py                     # FastAPI application
└── optimized_services.py         # Performance-optimized services
```

---

## 🔗 **API REFERENCE**

### **Authentication Endpoints:**

#### **POST /api/auth/register**
Register a new user account.
```json
Request:
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe",
  "username": "johndoe"
}

Response:
{
  "id": "uuid",
  "username": "johndoe",
  "email": "user@example.com", 
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "has_completed_onboarding": false,
  "created_at": "2025-08-25T00:00:00"
}
```

#### **POST /api/auth/login**
Authenticate user and return tokens.
```json
Request:
{
  "email": "user@example.com",
  "password": "SecurePass123"
}

Response:
{
  "access_token": "jwt_token_here",
  "refresh_token": "refresh_token_here", 
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### **POST /api/auth/forgot-password**
Initiate password reset flow.
```json
Request:
{
  "email": "user@example.com"
}

Response:
{
  "success": true,
  "message": "If an account exists, a password reset email has been sent."
}
```

### **Core Data Endpoints:**

#### **GET /api/tasks**
Retrieve tasks with filtering and pagination.
```json
Query Parameters:
- project_id: string (optional)
- q: string (search query, optional)
- status: string (todo|in_progress|review|completed, optional) 
- priority: string (low|medium|high, optional)
- due_date: string (overdue|today|week|YYYY-MM-DD, optional)
- page: integer (pagination, optional)
- limit: integer (page size, optional)
- return_meta: boolean (include metadata, optional)

Response (without metadata):
[
  {
    "id": "task_uuid",
    "title": "Task Title",
    "description": "Task description",
    "status": "todo",
    "priority": "high",
    "due_date": "2025-08-30",
    "project_id": "project_uuid",
    "created_at": "2025-08-25T00:00:00"
  }
]

Response (with metadata):
{
  "tasks": [...],
  "total": 150,
  "page": 1, 
  "limit": 20,
  "has_more": true
}
```

#### **GET /api/insights**
Retrieve analytics and insights data.
```json
Query Parameters:
- date_range: string (all_time|week|month, default: all_time)
- area_id: string (optional)

Response:
{
  "eisenhower_matrix": {
    "Q1": {"count": 5, "tasks": [...]},
    "Q2": {"count": 8, "tasks": [...]}, 
    "Q3": {"count": 3, "tasks": [...]},
    "Q4": {"count": 2, "tasks": [...]}
  },
  "alignment_snapshot": {
    "pillar_alignment": [...]
  },
  "area_distribution": [...],
  "generated_at": "2025-08-25T12:00:00"
}
```

---

## 🔐 **AUTHENTICATION FLOW**

### **Login Flow:**
1. User submits credentials to `/api/auth/login`
2. Backend validates with Supabase Auth
3. Returns access_token and refresh_token
4. Frontend stores tokens in localStorage
5. Automatic token refresh before expiry
6. User profile loaded from `/api/auth/me`

### **Password Reset Flow:**
1. User requests reset via `/api/auth/forgot-password`
2. Backend sends email via Microsoft 365 SMTP
3. User clicks email link → redirected to `/reset-password`
4. Frontend extracts token from URL parameters
5. User submits new password to `/api/auth/update-password`
6. Backend validates token and updates password
7. User redirected to login page

### **Token Management:**
- **Access Token:** 3600 seconds (1 hour) expiry
- **Refresh Token:** Automatic refresh 1 minute before expiry
- **Storage:** localStorage with expiry tracking
- **Security:** Bearer token authentication, automatic cleanup

---

## 🔄 **DATA FLOW PATTERNS**

### **Hierarchical Data Flow:**
```
User creates Pillar
    ↓
Pillar contains Areas
    ↓  
Area contains Projects
    ↓
Project contains Tasks
```

### **State Management Flow:**
```
API Call → TanStack Query Cache → React Context → Component State → UI Update
```

### **Authentication State Flow:**
```
Login → Token Storage → User Profile Fetch → App State Update → Route Protection
```

---

## 🧪 **TESTING STRATEGY**

### **Backend Testing:**
- **Unit Tests** - Individual service and endpoint testing
- **Integration Tests** - Cross-service communication validation
- **Security Tests** - Input validation and injection protection
- **Performance Tests** - Load testing and optimization validation

### **Frontend Testing:**
- **Component Tests** - Individual component behavior testing
- **Integration Tests** - Component interaction and API integration
- **E2E Tests** - Complete user workflow validation
- **Performance Tests** - Render optimization and load time testing

### **Test Credentials:**
- **Primary:** marc.alleyne@aurumtechnologyltd.com
- **Fallback:** smoketest_e0742f61@aurumtechnologyltd.com
- **Password:** password123 (or user-reset password)

---

## 🔧 **CONFIGURATION MANAGEMENT**

### **Environment Variables:**

#### **Frontend (.env):**
```bash
REACT_APP_BACKEND_URL=https://smart-life-os.preview.emergentagent.com
REACT_APP_GOOGLE_CLIENT_ID=514537887764-mgfh2g9k8ni7tanhm32o2o4mg1atrcgb.apps.googleusercontent.com
REACT_APP_SUPABASE_URL=https://sftppbnqlsumjlrgyzgo.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
DANGEROUSLY_DISABLE_HOST_CHECK=true
```

#### **Backend (.env):**
```bash
SUPABASE_URL=https://sftppbnqlsumjlrgyzgo.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
GOOGLE_CLIENT_ID=266791319799-m9kd1n5t3pdh4oicijppk06sva56asj6.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
SENDGRID_API_KEY=SG.wBB6585OSeqa0S5EwMNhEw...
SENDER_EMAIL=marc.alleyne@aurumtechnologyltd.com
JWT_SECRET_KEY=aurum-life-secret-key-2025-production-change-this
GEMINI_API_KEY=AIzaSyCs3D7Etbics6QV17oBpgAfHk9S86NNftc
```

---

## 🔄 **DEPLOYMENT PROCEDURES**

### **Service Management:**
```bash
# Restart all services
sudo supervisorctl restart all

# Restart specific services  
sudo supervisorctl restart frontend
sudo supervisorctl restart backend

# Check service status
sudo supervisorctl status
```

### **Dependency Management:**
```bash
# Frontend (use yarn, not npm)
yarn install
yarn add package-name

# Backend
pip install -r requirements.txt
pip install package-name
# Add to requirements.txt
```

### **Database Operations:**
- **Supabase Dashboard** - Web interface for database management
- **Real-time Sync** - Automatic data synchronization
- **Backup Strategy** - Automated Supabase backups
- **Migration Support** - Schema evolution capabilities

---

## 🔍 **MONITORING & DEBUGGING**

### **Logging:**
```bash
# Backend logs
tail -f /var/log/supervisor/backend.*.log

# Frontend logs (browser console)
# Enhanced debugging in development mode
```

### **Performance Monitoring:**
- **Load Times** - Page load performance tracking
- **API Response Times** - Backend performance monitoring  
- **Error Rates** - Application stability monitoring
- **User Analytics** - Feature usage and engagement tracking

### **Debug Endpoints:**
- **GET /api/health** - Backend health check
- **GET /api/auth/debug-supabase-config** - Configuration validation
- **Frontend Debug Tools** - URL resolution debugging

---

## 🛡️ **SECURITY CONSIDERATIONS**

### **Authentication Security:**
- **Password Requirements** - 8+ characters, uppercase, number
- **Token Security** - JWT with secure storage and automatic refresh
- **Session Management** - Proper timeout and cleanup
- **Error Masking** - Prevent information leakage

### **Input Validation:**
- **Server-Side Validation** - Pydantic models with custom validators
- **SQL Injection Protection** - Parameterized queries and ORM usage
- **XSS Protection** - Input sanitization and output encoding
- **CORS Configuration** - Proper cross-origin request handling

### **Data Protection:**
- **Encryption** - Data encrypted in transit and at rest
- **Access Control** - User-based data isolation
- **Audit Logging** - Comprehensive operation logging
- **Backup Security** - Encrypted backup storage

---

## 📞 **SUPPORT & MAINTENANCE**

### **Common Issues & Solutions:**

#### **Authentication Issues:**
- **Problem:** 401 Unauthorized errors
- **Solution:** Check token validity, refresh tokens, verify Supabase configuration

#### **Performance Issues:**
- **Problem:** Slow load times
- **Solution:** Check TanStack Query cache, verify API response times, monitor bundle size

#### **Database Issues:**
- **Problem:** Data sync problems
- **Solution:** Verify Supabase connection, check real-time subscriptions, validate RLS policies

### **Maintenance Tasks:**
- **Weekly:** Monitor performance metrics and error rates
- **Monthly:** Review user feedback and feature usage analytics
- **Quarterly:** Security audit and dependency updates
- **Annually:** Architecture review and optimization planning

---

**For technical support and development questions, refer to the main PRD document and this technical guide.**