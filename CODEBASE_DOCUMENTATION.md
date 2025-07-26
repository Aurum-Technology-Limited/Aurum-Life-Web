# Aurum Life - Comprehensive Codebase Documentation

## Table of Contents
1. [Overview](#overview)
2. [Backend Documentation (FastAPI)](#backend-documentation-fastapi)
3. [Frontend Documentation (React)](#frontend-documentation-react)
4. [System Architecture](#system-architecture)
5. [Development Workflow](#development-workflow)

## Overview

Aurum Life is a full-stack personal growth and productivity platform built with FastAPI (backend) and React (frontend). The application implements a hierarchical task management system based on the concept of a "Personal OS" with Pillars → Areas → Projects → Tasks structure.

**Tech Stack:**
- **Backend**: FastAPI, MongoDB (Motor), JWT Authentication, SendGrid (Email), Google OAuth
- **Frontend**: React 19, Tailwind CSS, React DnD, Radix UI components
- **Database**: MongoDB with async Motor driver
- **Authentication**: JWT + Google OAuth 2.0
- **Email**: SendGrid integration for notifications and password reset

---

## Backend Documentation (FastAPI)

### Project Setup

#### Environment Setup
1. **Copy environment template:**
   ```bash
   cp backend/.env.example backend/.env
   ```

2. **Required environment variables** (edit `backend/.env`):
   ```env
   # Database
   MONGO_URL=mongodb://localhost:27017/
   DB_NAME=aurum_life
   
   # Authentication
   JWT_SECRET_KEY=your-strong-secret-key-here
   
   # Email (SendGrid)
   SENDGRID_API_KEY=your-sendgrid-api-key
   SENDER_EMAIL=noreply@yourapp.com
   RESET_TOKEN_EXPIRY_HOURS=24
   
   # Google OAuth
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   
   # AI Coach (Optional)
   GEMINI_API_KEY=your-gemini-api-key
   ```

#### Installation & Startup
```bash
cd backend
pip install -r requirements.txt
python server.py
```

**Server starts on:** `http://localhost:8000`  
**API Docs:** `http://localhost:8000/docs`

### Database Models (`/models.py`)

The application uses a hierarchical structure with the following core entities:

#### User Model
```python
class User(BaseDocument):
    email: str
    username: str
    password_hash: Optional[str] = None  # Optional for Google OAuth users
    first_name: str
    last_name: str
    google_id: Optional[str] = None
    profile_picture: Optional[str] = None
    is_active: bool = True
    level: int = 1
    total_points: int = 0
    current_streak: int = 0
```

#### Hierarchy Models

**Pillar** (Top Level - Life Domains)
```python
class Pillar(BaseDocument):
    user_id: str
    name: str                                    # e.g., "Health", "Career"
    description: str = ""
    icon: str = "🎯"
    color: str = "#F4B400"
    time_allocation_percentage: Optional[float] = None
    archived: bool = False
    sort_order: int = 0
```

**Area** (Focus Areas within Pillars)
```python
class Area(BaseDocument):
    user_id: str
    pillar_id: Optional[str] = None             # Parent pillar
    name: str                                   # e.g., "Fitness", "Nutrition"
    description: str = ""
    icon: str = "🎯"
    color: str = "#F4B400"
    importance: ImportanceEnum = ImportanceEnum.medium  # 1-5 scale
    archived: bool = False
    sort_order: int = 0
```

**Project** (Goals/Initiatives within Areas)
```python
class Project(BaseDocument):
    user_id: str
    area_id: str                                # Parent area
    name: str                                   # e.g., "Marathon Training"
    description: str = ""
    icon: str = "🚀"
    deadline: Optional[datetime] = None
    status: ProjectStatusEnum = ProjectStatusEnum.not_started
    priority: PriorityEnum = PriorityEnum.medium
    importance: ImportanceEnum = ImportanceEnum.medium
    completion_percentage: float = 0.0
    archived: bool = False
    sort_order: int = 0
```

**Task** (Individual Actions within Projects)
```python
class Task(BaseDocument):
    user_id: str
    project_id: str                             # Parent project
    parent_task_id: Optional[str] = None        # For sub-tasks
    name: str                                   # e.g., "Run 5K"
    description: str = ""
    status: TaskStatusEnum = TaskStatusEnum.todo
    priority: PriorityEnum = PriorityEnum.medium
    due_date: Optional[datetime] = None
    due_time: Optional[str] = None              # HH:MM format
    reminder_date: Optional[datetime] = None
    completed: bool = False
    completed_at: Optional[datetime] = None
    dependency_task_ids: List[str] = []         # Prerequisites
    kanban_column: str = "to_do"                # to_do, in_progress, review, done
    sort_order: int = 0
    estimated_duration: Optional[int] = None    # minutes
    sub_task_completion_required: bool = False
```

### API Endpoint Reference

#### Authentication Endpoints

**POST `/api/auth/register`**
- **Description**: Register a new user with email/password
- **Request Body**: 
  ```json
  {
    "username": "string",
    "email": "user@example.com", 
    "first_name": "string",
    "last_name": "string",
    "password": "string"
  }
  ```
- **Response**: `UserResponse` object
- **cURL Example**:
  ```bash
  curl -X POST "http://localhost:8000/api/auth/register" \
    -H "Content-Type: application/json" \
    -d '{"username":"john_doe","email":"john@example.com","first_name":"John","last_name":"Doe","password":"password123"}'
  ```

**POST `/api/auth/login`**
- **Description**: Login with email/password, returns JWT token
- **Request Body**: 
  ```json
  {
    "email": "user@example.com",
    "password": "string"
  }
  ```
- **Response**: 
  ```json
  {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer"
  }
  ```

**POST `/api/auth/google`**
- **Description**: Authenticate with Google OAuth token
- **Request Body**: 
  ```json
  {
    "token": "google-id-token"
  }
  ```
- **Response**: `GoogleAuthResponse` with JWT token and user data

**GET `/api/auth/me`**
- **Description**: Get current authenticated user information
- **Headers**: `Authorization: Bearer <jwt-token>`
- **Response**: `UserResponse` object

#### Pillar Management

**GET `/api/pillars`**
- **Description**: Get all pillars for authenticated user
- **Headers**: `Authorization: Bearer <jwt-token>`
- **Query Parameters**: 
  - `include_areas` (bool): Include nested areas
  - `include_archived` (bool): Include archived pillars
- **Response**: `List[PillarResponse]`

**POST `/api/pillars`**
- **Description**: Create a new pillar
- **Request Body**: 
  ```json
  {
    "name": "Health & Fitness",
    "description": "Physical and mental well-being",
    "icon": "💪",
    "color": "#10B981",
    "time_allocation_percentage": 25.0
  }
  ```

**PUT `/api/pillars/{pillar_id}`**
- **Description**: Update an existing pillar
- **Path Parameters**: `pillar_id` (string)
- **Request Body**: `PillarUpdate` object (partial updates)

#### Area Management

**GET `/api/areas`**
- **Description**: Get all areas for authenticated user
- **Query Parameters**:
  - `include_projects` (bool): Include nested projects
  - `include_archived` (bool): Include archived areas
- **Response**: `List[AreaResponse]`

**POST `/api/areas`**
- **Description**: Create a new area
- **Request Body**: 
  ```json
  {
    "pillar_id": "pillar-uuid",
    "name": "Cardio Training",
    "description": "Cardiovascular fitness improvement",
    "icon": "🏃",
    "importance": 4
  }
  ```

#### Project Management

**GET `/api/projects`**
- **Description**: Get all projects for authenticated user
- **Query Parameters**:
  - `include_tasks` (bool): Include nested tasks
  - `include_archived` (bool): Include archived projects
- **Response**: `List[ProjectResponse]`

**POST `/api/projects`**
- **Description**: Create a new project
- **Request Body**: 
  ```json
  {
    "area_id": "area-uuid",
    "name": "Marathon Training Plan",
    "description": "16-week marathon preparation",
    "icon": "🏃‍♂️",
    "deadline": "2024-06-01T00:00:00Z",
    "priority": "high",
    "importance": 5
  }
  ```

**GET `/api/projects/{project_id}/tasks`**
- **Description**: Get all tasks for a specific project
- **Response**: `List[TaskResponse]`

**GET `/api/projects/{project_id}/kanban`**
- **Description**: Get project tasks organized in Kanban board format
- **Response**: 
  ```json
  {
    "project_id": "string",
    "columns": {
      "to_do": [{"task": "TaskResponse", "position": 0}],
      "in_progress": [{"task": "TaskResponse", "position": 0}],
      "review": [{"task": "TaskResponse", "position": 0}],
      "done": [{"task": "TaskResponse", "position": 0}]
    }
  }
  ```

#### Task Management

**GET `/api/tasks`**
- **Description**: Get all tasks for authenticated user
- **Query Parameters**:
  - `include_subtasks` (bool): Include sub-tasks
  - `completed` (bool): Filter by completion status
- **Response**: `List[TaskResponse]`

**POST `/api/tasks`**
- **Description**: Create a new task
- **Request Body**: 
  ```json
  {
    "project_id": "project-uuid",
    "name": "Morning 5K run",
    "description": "Daily cardio exercise",
    "priority": "medium",
    "due_date": "2024-03-15T00:00:00Z",
    "due_time": "07:00",
    "estimated_duration": 30
  }
  ```

**PUT `/api/tasks/{task_id}`**
- **Description**: Update an existing task
- **Request Body**: `TaskUpdate` object (partial updates)

**PUT `/api/tasks/{task_id}/column`**
- **Description**: Move task to different Kanban column
- **Request Body**: 
  ```json
  {
    "column": "in_progress",
    "position": 0
  }
  ```

#### Today View & AI Coach

**GET `/api/today`**
- **Description**: Get AI-prioritized tasks for today with coaching insights
- **Response**: 
  ```json
  {
    "priorities": [
      {
        "task_id": "task-uuid",
        "task_name": "Task name",
        "coaching_message": "AI-generated advice",
        "score": 85,
        "reasons": ["Due today", "High importance"]
      }
    ],
    "daily_tasks": ["List of selected daily tasks"],
    "insights": "Overall daily guidance"
  }
  ```

**POST `/api/today/tasks/{task_id}`**
- **Description**: Add task to today's focus list
- **Path Parameters**: `task_id` (string)

**PUT `/api/today/reorder`**
- **Description**: Reorder today's task priorities
- **Request Body**: 
  ```json
  {
    "task_ids": ["task-1-uuid", "task-2-uuid", "task-3-uuid"]
  }
  ```

#### File Attachments

**POST `/api/resources`**
- **Description**: Upload file and create resource
- **Request Body**: FormData with file and metadata
- **Response**: `ResourceResponse`

**POST `/api/resources/{resource_id}/attach`**
- **Description**: Attach uploaded resource to entity (project/task)
- **Request Body**: 
  ```json
  {
    "entity_type": "project",
    "entity_id": "project-uuid"
  }
  ```

**GET `/api/resources/entity/{entity_type}/{entity_id}`**
- **Description**: Get all files attached to specific entity
- **Response**: `List[ResourceResponse]`

### Core Services (`/services.py`)

#### UserService
```python
class UserService:
    @staticmethod
    async def create_user(user_data: UserCreate) -> User
    
    @staticmethod 
    async def authenticate_user(email: str, password: str) -> Optional[User]
    
    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]
    
    @staticmethod
    async def create_password_reset_token(email: str) -> Optional[str]
    
    @staticmethod
    async def reset_password(token: str, new_password: str) -> bool
```

#### PillarService
```python
class PillarService:
    @staticmethod
    async def create_pillar(user_id: str, pillar_data: PillarCreate) -> Pillar
    
    @staticmethod
    async def get_pillars(user_id: str, include_areas: bool = False) -> List[Pillar]
    
    @staticmethod
    async def update_pillar(user_id: str, pillar_id: str, pillar_data: PillarUpdate) -> bool
    
    @staticmethod
    async def archive_pillar(user_id: str, pillar_id: str) -> bool
```

#### TaskService  
```python
class TaskService:
    @staticmethod
    async def create_task(user_id: str, task_data: TaskCreate) -> Task
    
    @staticmethod
    async def get_tasks(user_id: str, **filters) -> List[Task]
    
    @staticmethod
    async def update_task(user_id: str, task_id: str, task_data: TaskUpdate) -> bool
    
    @staticmethod
    async def complete_task(user_id: str, task_id: str) -> bool
    
    @staticmethod
    async def get_task_dependencies(user_id: str, task_id: str) -> Dict
```

#### AICoachService
```python
class AiCoachService:
    @staticmethod
    async def get_todays_priorities(user_id: str, limit: int = 3) -> List[Dict]
    # Uses Gemini 2.0-flash for intelligent task prioritization
    # Combines urgency/importance matrix with user context
    # Returns AI-generated coaching messages for each priority
```

---

## Frontend Documentation (React)

### Project Setup

#### Environment Setup
1. **Copy environment template:**
   ```bash
   cp frontend/.env.example frontend/.env
   ```

2. **Required environment variables** (edit `frontend/.env`):
   ```env
   REACT_APP_BACKEND_URL=http://localhost:8000
   WDS_SOCKET_PORT=443
   ```

#### Installation & Startup
```bash
cd frontend
yarn install
yarn start
```

**Application starts on:** `http://localhost:3000`

### Component Library (`/src/components/`)

#### Core Layout Components

**Layout.jsx**
- **Purpose**: Main application shell with navigation sidebar
- **Props**: 
  ```jsx
  {
    activeSection: string,      // Current active section
    onSectionChange: function   // Navigation handler
  }
  ```
- **Example Usage**:
  ```jsx
  <Layout activeSection="dashboard" onSectionChange={handleSectionChange}>
    <Dashboard />
  </Layout>
  ```

**Dashboard.jsx**
- **Purpose**: Main overview page with user statistics and quick actions
- **Props**: 
  ```jsx
  {
    onSectionChange: function   // Navigation to other sections
  }
  ```
- **Features**: 
  - User statistics cards (completion rates, streaks, points)
  - AI Coach recommendations widget
  - Quick access to Today view and recent activities

#### Hierarchy Management Components

**Pillars.jsx**
- **Purpose**: Manage top-level life domains (Pillars)
- **Props**: 
  ```jsx
  {
    onSectionChange: function   // Navigate to areas/projects
  }
  ```
- **Features**:
  - CRUD operations for pillars
  - Drag-and-drop reordering
  - Time allocation percentage tracking
  - Color and icon customization

**Areas.jsx**
- **Purpose**: Manage focus areas within pillars
- **Props**: Same as Pillars
- **Features**:
  - Nested view showing pillar → area relationships
  - Importance level setting (1-5 scale)
  - Project count and progress indicators

**Projects.jsx**
- **Purpose**: Comprehensive project management interface
- **Props**: 
  ```jsx
  {
    onSectionChange: function,
    filterAreaId?: string       // Optional filter for specific area
  }
  ```
- **Features**:
  - List and grid view modes
  - Project status tracking (not_started, in_progress, completed)
  - Deadline management with overdue indicators
  - Task progress visualization
  - File attachment management
  - Archive/unarchive functionality

**Tasks.jsx**
- **Purpose**: Task management with multiple view options
- **Features**:
  - List view with sorting and filtering
  - Kanban board integration
  - Sub-task support with hierarchical display
  - Due date/time management
  - Priority and status indicators
  - Batch operations (complete multiple, reorder)

#### Specialized Components

**Today.jsx**
- **Purpose**: AI-powered daily task prioritization interface
- **Features**:
  - AI Coach priority recommendations with explanations
  - Drag-and-drop task reordering
  - Quick task completion toggles
  - Pomodoro timer integration
  - Focus session tracking

**KanbanBoard.jsx**
- **Purpose**: Kanban-style task visualization for projects
- **Props**: 
  ```jsx
  {
    projectId: string,
    tasks: Array,
    onTaskUpdate: function,
    onTaskMove: function
  }
  ```
- **Features**:
  - Four-column layout (To Do, In Progress, Review, Done)
  - Drag-and-drop between columns
  - Task details on hover/click
  - Progress indicators per column

**AICoach.jsx**
- **Purpose**: Conversational AI interface for personal coaching
- **Features**:
  - Chat-based interaction with AI coach
  - Context-aware responses based on user data
  - Goal-setting assistance
  - Progress insights and recommendations

**FileManager.jsx**
- **Purpose**: File attachment system for projects and tasks
- **Props**:
  ```jsx
  {
    entityType: 'project' | 'task',
    entityId: string,
    entityName?: string,
    showUpload?: boolean
  }
  ```
- **Features**:
  - Drag-and-drop file upload
  - Supported file types: images, PDFs, documents
  - File preview and download
  - Contextual organization by entity

#### UI Components (`/src/components/ui/`)

**Button, Input, Modal, etc.**
- **Purpose**: Reusable UI primitives built with Radix UI and Tailwind
- **Features**: Consistent styling, accessibility, and theming

### State Management (`/src/contexts/`)

#### AuthContext.js
- **Purpose**: Authentication state and user session management
- **State Variables**:
  ```javascript
  {
    user: User | null,              // Current user object
    token: string | null,           // JWT authentication token
    loading: boolean,               // Auth state loading
    isAuthenticated: boolean        // Computed auth status
  }
  ```
- **Functions**:
  ```javascript
  {
    login: (email, password) => Promise<{success: boolean, error?: string}>,
    register: (userData) => Promise<{success: boolean, error?: string}>,
    updateProfile: (profileData) => Promise<{success: boolean, error?: string}>,
    logout: () => void
  }
  ```

#### DataContext.js
- **Purpose**: Data invalidation and refresh coordination
- **Functions**:
  ```javascript
  {
    onDataMutation: (entity, operation, data) => void    // Trigger data refresh
  }
  ```

#### NotificationContext.js
- **Purpose**: In-app notification system management
- **State Variables**:
  ```javascript
  {
    notifications: Array,           // Current notifications
    unreadCount: number,           // Unread notification count
    preferences: Object            // User notification preferences
  }
  ```

### API Service (`/src/services/api.js`)

#### Authentication Functions
```javascript
// Configured axios instance with automatic token handling
const apiClient = axios.create({
  baseURL: process.env.REACT_APP_BACKEND_URL + '/api',
  timeout: 10000
});

// Request interceptor adds JWT token to headers
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

#### Core API Functions
```javascript
// Pillars API
export const pillarsAPI = {
  getPillars: (includeAreas = false) => apiClient.get('/pillars', {params: {include_areas: includeAreas}}),
  createPillar: (data) => apiClient.post('/pillars', data),
  updatePillar: (id, data) => apiClient.put(`/pillars/${id}`, data),
  deletePillar: (id) => apiClient.delete(`/pillars/${id}`)
};

// Projects API
export const projectsAPI = {
  getProjects: (includeTasks = false) => apiClient.get('/projects', {params: {include_tasks: includeTasks}}),
  createProject: (data) => apiClient.post('/projects', data),
  getProjectKanban: (projectId) => apiClient.get(`/projects/${projectId}/kanban`)
};

// Tasks API
export const tasksAPI = {
  getTasks: (filters = {}) => apiClient.get('/tasks', {params: filters}),
  createTask: (data) => apiClient.post('/tasks', data),
  updateTask: (id, data) => apiClient.put(`/tasks/${id}`, data),
  moveTaskColumn: (id, column, position) => apiClient.put(`/tasks/${id}/column`, {column, position})
};

// Today/AI Coach API
export const todayAPI = {
  getTodayView: () => apiClient.get('/today'),
  addTaskToToday: (taskId) => apiClient.post(`/today/tasks/${taskId}`),
  reorderTodayTasks: (taskIds) => apiClient.put('/today/reorder', {task_ids: taskIds})
};
```

---

## System Architecture

### Authentication Flow
1. **Registration**: Email/password → password hashing → user creation → auto-login
2. **Login**: Credential validation → JWT token generation → token storage
3. **Google OAuth**: Google token verification → user lookup/creation → JWT generation
4. **Request Authentication**: JWT token validation → user context injection
5. **Password Reset**: Email verification → secure token generation → SendGrid email → token validation

### Data Hierarchy & Relationships
```
User
├── Pillars (Life Domains)
│   ├── Areas (Focus Areas)
│   │   ├── Projects (Goals/Initiatives)  
│   │   │   ├── Tasks (Individual Actions)
│   │   │   │   └── Sub-tasks (Task breakdown)
│   │   │   └── File Attachments
│   │   └── Project Templates
│   └── Recurring Task Templates
├── Journal Entries
├── Achievements & Points
└── Notification Preferences
```

### AI Coach Integration
- **Rule-Based Engine**: Urgency/Importance matrix scoring
- **Gemini 2.0-flash**: Contextual coaching messages and insights
- **Scoring Algorithm**: 
  - Overdue tasks: +100 points
  - Due today: +80 points  
  - High priority: +30 points
  - High importance (project/area): +50/+25 points
  - Dependencies cleared: +60 points

### File Management System
- **Upload Process**: File validation → cloud storage → resource record creation → entity attachment
- **Supported Types**: Images (PNG, JPEG, GIF), Documents (PDF, DOC, DOCX), Text files
- **Storage**: Cloud-based with secure URL generation
- **Organization**: Contextual attachments linked to projects/tasks

---

## Development Workflow

### Code Organization
- **Backend**: Service layer pattern with clear separation of concerns
- **Frontend**: Component-based architecture with context for state management
- **Database**: Document-based MongoDB with structured schemas
- **API**: RESTful endpoints with comprehensive OpenAPI documentation

### Key Development Commands
```bash
# Backend development
cd backend
python server.py                    # Start development server
python -m pytest tests/            # Run tests

# Frontend development  
cd frontend
yarn start                         # Start development server
yarn build                         # Production build
yarn test                          # Run tests

# Database operations
python backend/seed_data.py         # Seed sample data
python backend/migrate_*.py         # Run specific migrations
```

### Environment Configuration
- **Development**: Local MongoDB, test API keys, HTTP endpoints
- **Production**: Cloud MongoDB, production API keys, HTTPS endpoints, security headers
- **Security**: JWT secrets, API keys, and sensitive data via environment variables only

This documentation provides a comprehensive technical overview enabling new developers to understand, contribute to, and extend the Aurum Life codebase effectively.