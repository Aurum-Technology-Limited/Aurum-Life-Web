# Aurum Life - Personal Growth Companion

A comprehensive personal development platform built with React, Supabase, and modern web technologies. Aurum Life helps users manage their goals, track progress, and maintain consistency in their personal growth journey.

## 🚀 Live Application

**Production URL:** https://aurum-life-web.vercel.app

## ✨ Features

### Core Functionality
- **Task Management** - Organize and track daily tasks with priority levels
- **Project Planning** - Break down large goals into manageable projects
- **Area Management** - Categorize life areas (Health, Career, Relationships, etc.)
- **Journaling** - Daily reflection and progress tracking
- **AI Coach** - Intelligent insights and recommendations
- **Progress Tracking** - Visual dashboards and analytics
- **Goal Setting** - SMART goal framework with milestone tracking

### Technical Features
- **Real-time Updates** - Live data synchronization
- **Responsive Design** - Mobile-first approach
- **Dark Theme** - Modern, eye-friendly interface
- **Drag & Drop** - Intuitive task organization
- **Search & Filter** - Quick content discovery
- **Data Export** - Backup and analysis capabilities

## 🏗️ Architecture

### Frontend
- **Framework:** React 18 with hooks
- **Styling:** Tailwind CSS
- **State Management:** React Context + TanStack Query
- **Authentication:** Supabase Auth
- **Deployment:** Vercel

### Backend
- **Database:** Supabase PostgreSQL
- **API:** Supabase Edge Functions (Deno)
- **Authentication:** Supabase Auth with JWT
- **Real-time:** Supabase Realtime
- **Storage:** Supabase Storage

### Key Technologies
- **Frontend:** React, TypeScript, Tailwind CSS, Apollo Client
- **Backend:** Supabase, PostgreSQL, Deno
- **Deployment:** Vercel, Supabase Cloud
- **Analytics:** PostHog (with ad-blocker resilience)

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Supabase account

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/Aurum-Technology-Limited/Aurum-Life-Web.git
   cd Aurum-Life-Web
   ```

2. **Install dependencies**
   ```bash
   # Frontend
   cd frontend
   npm install
   
   # Backend (if running locally)
   cd ../backend
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Frontend (.env.local)
   REACT_APP_SUPABASE_URL=https://sftppbnqlsumjlrgyzgo.supabase.co
   REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key
   REACT_APP_BACKEND_URL=https://sftppbnqlsumjlrgyzgo.supabase.co/functions/v1
   REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id
   ```

4. **Start development servers**
   ```bash
   # Frontend (Terminal 1)
   cd frontend
   npm start
   
   # Backend (Terminal 2, optional for local development)
   cd backend
   python server_supabase.py
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8001 (if running locally)

## 🔧 Configuration

### Environment Variables

#### Frontend (Vercel/Production)
- `REACT_APP_SUPABASE_URL` - Supabase project URL
- `REACT_APP_SUPABASE_ANON_KEY` - Supabase anonymous key
- `REACT_APP_BACKEND_URL` - Backend API URL
- `REACT_APP_GOOGLE_CLIENT_ID` - Google OAuth client ID

#### Backend (Supabase Edge Functions)
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_ANON_KEY` - Supabase anonymous key
- `SUPABASE_SERVICE_ROLE_KEY` - Supabase service role key
- `OPENAI_API_KEY` - OpenAI API key for AI features
- `JWT_SECRET_KEY` - JWT signing secret

### Database Setup

The application uses Supabase PostgreSQL with the following key tables:
- `user_profiles` - User account information
- `tasks` - Task management
- `projects` - Project organization
- `areas` - Life area categorization
- `pillars` - Core life pillars
- `journal_entries` - Daily journaling
- `alignment_scores` - Progress tracking

## 📱 Usage

### Getting Started
1. **Sign Up** - Create an account with email/password or Google OAuth
2. **Onboarding** - Complete the guided setup process
3. **Set Goals** - Define your life areas and initial goals
4. **Start Tracking** - Begin logging tasks and journal entries

### Key Workflows
- **Daily Planning** - Use the Today view to plan your day
- **Project Management** - Break down large goals into projects
- **Progress Review** - Regular check-ins and adjustments
- **Journaling** - Daily reflection and learning

## 🛠️ Development

### Project Structure
```
frontend/
├── src/
│   ├── components/     # React components
│   ├── contexts/       # React contexts
│   ├── services/       # API services
│   ├── hooks/          # Custom hooks
│   └── utils/          # Utility functions
backend/
├── server_supabase.py  # Local development server
└── requirements.txt    # Python dependencies
supabase/
├── functions/          # Edge Functions
└── config.toml        # Supabase configuration
```

### Key Commands
```bash
# Frontend development
npm start              # Start development server
npm run build         # Build for production
npm test              # Run tests

# Backend development
python server_supabase.py  # Start local server

# Database
npx supabase db reset  # Reset local database
npx supabase db push   # Push schema changes
```

## 🚀 Deployment

### Production Deployment
The application is automatically deployed to:
- **Frontend:** Vercel (https://aurum-life-web.vercel.app)
- **Backend:** Supabase Edge Functions
- **Database:** Supabase Cloud

### Manual Deployment
1. **Frontend:** Push to main branch triggers Vercel deployment
2. **Backend:** Deploy Edge Functions via Supabase CLI or Dashboard
3. **Database:** Schema changes via Supabase migrations

## 🔒 Security

### Authentication
- Supabase Auth with JWT tokens
- Email/password and Google OAuth
- Secure session management
- User data isolation

### Data Protection
- Row-level security (RLS) in PostgreSQL
- Encrypted data transmission
- Secure API endpoints
- Privacy-focused analytics

## 📊 Performance

### Optimizations
- Code splitting and lazy loading
- Image optimization
- Database query optimization
- Caching strategies
- CDN delivery

### Monitoring
- Vercel Analytics
- Supabase monitoring
- Error tracking
- Performance metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the documentation in the `/docs` folder
- Review the troubleshooting guide

## 🔄 Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## 🎯 Roadmap

- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Team collaboration features
- [ ] Integration with external tools
- [ ] AI-powered insights
- [ ] Habit tracking
- [ ] Goal templates

---

**Built with ❤️ by Aurum Technology Limited**