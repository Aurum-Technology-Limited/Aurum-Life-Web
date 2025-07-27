# Product Requirements Document: Local Deployment of Aurum Life Application

## 🎯 Objective
Deploy the Aurum Life personal growth and productivity platform locally on a developer's machine with full functionality.

## 📋 Prerequisites Verification

Before beginning deployment, verify the following:

1. **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+ recommended)
2. **Python**: Version 3.8 or higher installed
3. **Node.js**: Version 16.x or higher with npm/yarn
4. **Git**: For cloning repository (if needed)
5. **Available Ports**: 3000 (frontend) and 8000 (backend) must be free

## 🔑 Required Credentials

The user has indicated they have credentials for all external dependencies. Confirm availability of:

### Essential Services:
- [ ] **Supabase**:
  - `SUPABASE_URL`
  - `SUPABASE_ANON_KEY`
  - `SUPABASE_SERVICE_ROLE_KEY`
  - `SUPABASE_JWT_SECRET`

- [ ] **Google OAuth**:
  - `GOOGLE_CLIENT_ID`
  - `GOOGLE_CLIENT_SECRET`

### Optional Services (confirm if available):
- [ ] **SendGrid**: `SENDGRID_API_KEY` and `SENDER_EMAIL`
- [ ] **Redis**: Connection URL and password (if using external Redis)
- [ ] **Gemini AI**: `GEMINI_API_KEY` (for AI Coach feature)
- [ ] **PostgreSQL**: Direct database URL (if not using Supabase's built-in Postgres)

## ❓ Clarifying Questions

Before proceeding, please confirm:

1. **Database Setup**: 
   - Are you using Supabase's built-in PostgreSQL, or do you have a separate PostgreSQL instance?
   - Do you need help setting up the Supabase project, or is it already configured?

2. **Redis Requirement**:
   - Do you want to run Redis locally for background tasks, or skip this for now?
   - If yes, should we use Docker for Redis or install it directly?

3. **Email Functionality**:
   - Is SendGrid configured and do you want email notifications active?
   - If no SendGrid, should we configure email to work in "development mode" (console output)?

4. **Environment**:
   - Are you on Windows, macOS, or Linux? (This affects some commands)
   - Do you prefer npm or yarn for frontend package management?

## 📝 Step-by-Step Deployment Instructions

### Phase 1: Environment Setup

1. **Clone/Navigate to Repository**
   ```bash
   cd /path/to/aurum-life
   # Verify you're in the correct directory
   ls -la  # Should show backend/, frontend/, supabase/ directories
   ```

2. **Create Python Virtual Environment**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   # venv\Scripts\activate
   
   # Verify activation (should show venv in prompt)
   which python  # Should point to venv/bin/python
   ```

3. **Install Backend Dependencies**
   ```bash
   cd backend
   pip install --upgrade pip
   pip install -r requirements.txt
   
   # Verify key packages installed
   pip show fastapi uvicorn supabase
   ```

### Phase 2: Configuration

4. **Configure Backend Environment**
   ```bash
   # Ensure you're in the backend directory
   cd backend  # if not already there
   
   # Create .env file if it doesn't exist
   cp .env.example .env 2>/dev/null || touch .env
   
   # Edit .env file with actual credentials
   ```

   **Required .env contents**:
   ```env
   # Core Settings
   ENVIRONMENT=development
   DEBUG=true
   SECRET_KEY=[generate-random-32-char-string]
   ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   
   # JWT Authentication
   JWT_SECRET_KEY=[your-actual-jwt-secret-key]
   
   # Supabase (REQUIRED - use your actual values)
   SUPABASE_URL=[your-supabase-project-url]
   SUPABASE_ANON_KEY=[your-supabase-anon-key]
   SUPABASE_SERVICE_ROLE_KEY=[your-supabase-service-role-key]
   SUPABASE_JWT_SECRET=[your-supabase-jwt-secret]
   
   # Database (if using direct PostgreSQL connection)
   DATABASE_URL=postgresql://[username]:[password]@[host]:[port]/[database]
   
   # Google OAuth (use your actual values)
   GOOGLE_CLIENT_ID=[your-google-client-id]
   GOOGLE_CLIENT_SECRET=[your-google-client-secret]
   
   # Optional Services
   SENDGRID_API_KEY=[your-sendgrid-key-or-leave-empty]
   SENDER_EMAIL=[your-sender-email-or-noreply@localhost]
   GEMINI_API_KEY=[your-gemini-key-or-leave-empty]
   
   # Redis (for local development, can use defaults)
   REDIS_URL=redis://localhost:6379
   REDIS_PASSWORD=
   
   # Server Settings
   HOST=127.0.0.1
   PORT=8000
   
   # API Configuration
   API_TIMEOUT_SECONDS=30
   RATE_LIMIT_PER_MINUTE=60
   LOG_LEVEL=INFO
   ```

5. **Configure Frontend Environment**
   ```bash
   cd ../frontend
   
   # Create .env file
   cp .env.example .env 2>/dev/null || touch .env
   ```

   **Required frontend .env contents**:
   ```env
   # Backend API
   REACT_APP_BACKEND_URL=http://localhost:8000
   
   # Supabase (use your actual values)
   REACT_APP_SUPABASE_URL=[your-supabase-project-url]
   REACT_APP_SUPABASE_ANON_KEY=[your-supabase-anon-key]
   
   # Google OAuth
   REACT_APP_GOOGLE_CLIENT_ID=[your-google-client-id]
   ```

### Phase 3: Database Setup

6. **Initialize Supabase Database**
   ```bash
   cd ../supabase
   
   # Option A: If Supabase CLI is installed
   supabase db push
   
   # Option B: Manual migration
   # Copy the contents of migrations/*.sql and run in Supabase SQL editor
   ```

7. **Verify Database Schema**
   - Log into Supabase Dashboard
   - Check that all required tables exist:
     - `users`, `profiles`, `tasks`, `projects`, `areas`, `pillars`
     - `achievements`, `notifications`, `journal_entries`, etc.

### Phase 4: Frontend Setup

8. **Install Frontend Dependencies**
   ```bash
   cd ../frontend
   
   # Using npm:
   npm install
   
   # OR using yarn:
   yarn install
   
   # Verify installation
   npm list react react-dom  # Should show installed versions
   ```

### Phase 5: Launch Application

9. **Start Backend Server**
   ```bash
   # Terminal 1
   cd backend
   source ../venv/bin/activate  # Ensure venv is active
   
   # Start server
   python server.py
   
   # Verify it's running:
   # Should see: "Uvicorn running on http://127.0.0.1:8000"
   ```

10. **Start Frontend Development Server**
    ```bash
    # Terminal 2 (new terminal window)
    cd frontend
    
    # Using npm:
    npm start
    
    # OR using yarn:
    yarn start
    
    # Should automatically open http://localhost:3000
    ```

### Phase 6: Verification

11. **Backend Health Check**
    ```bash
    # Terminal 3 (optional)
    curl http://localhost:8000/health
    # Should return: {"status":"healthy","timestamp":"..."}
    
    # Check API docs
    # Open browser: http://localhost:8000/docs
    ```

12. **Frontend Verification**
    - Open http://localhost:3000
    - You should see the Aurum Life login page
    - Check browser console for any errors (F12)

13. **Test Core Functionality**
    - [ ] Create a new account (sign up)
    - [ ] Log in with created account
    - [ ] Try Google OAuth login
    - [ ] Create a task
    - [ ] Create a project
    - [ ] Test navigation between sections

## 🚨 Troubleshooting Guide

### Common Issues and Solutions:

1. **Port Already in Use**
   ```bash
   # Find process using port
   lsof -i :8000  # or :3000 for frontend
   # Kill process if needed
   kill -9 [PID]
   ```

2. **Module Import Errors**
   - Ensure virtual environment is activated
   - Reinstall requirements: `pip install -r requirements.txt --force-reinstall`

3. **Supabase Connection Failed**
   - Verify Supabase project is active
   - Check credentials match exactly (no extra spaces)
   - Ensure Supabase project region is accessible

4. **Frontend Build Errors**
   - Clear npm cache: `npm cache clean --force`
   - Delete node_modules and reinstall: `rm -rf node_modules && npm install`

5. **CORS Errors**
   - Verify `ALLOWED_ORIGINS` in backend .env includes your frontend URL
   - Check both http://localhost:3000 and http://127.0.0.1:3000 are listed

## 📊 Success Criteria

The deployment is successful when:
- [ ] Backend API docs accessible at http://localhost:8000/docs
- [ ] Frontend loads without errors at http://localhost:3000
- [ ] User can create account and log in
- [ ] Basic CRUD operations work (create/read/update/delete tasks)
- [ ] No console errors in browser or terminal

## 🔄 Optional Enhancements

After basic deployment:

1. **Redis Setup** (for background tasks):
   ```bash
   # Using Docker:
   docker run -d -p 6379:6379 redis
   
   # Or install locally:
   # macOS: brew install redis
   # Ubuntu: sudo apt-get install redis-server
   ```

2. **Database Backups**:
   - Configure Supabase automatic backups
   - Set up local backup script

3. **Development Tools**:
   - Install Redux DevTools extension
   - Set up backend debugger configuration

## 📝 Notes for the Deploying Agent

- All commands assume a Unix-like environment. Adjust for Windows as needed.
- If any step fails, check the troubleshooting guide before proceeding.
- Keep terminal windows open to monitor logs from both backend and frontend.
- The application should be fully functional locally without any external API calls except to Supabase.

## 🎉 Deployment Complete

Once all steps are completed successfully, the Aurum Life application will be running locally with:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

The user can now use the application for personal productivity and growth tracking!