# Aurum Life - Deployment Guide

## 🚀 Production Deployment Status

**Current Status:** ✅ **LIVE AND OPERATIONAL**

- **Frontend:** https://aurum-life-web.vercel.app
- **Backend:** Supabase Edge Functions
- **Database:** Supabase PostgreSQL
- **Authentication:** Supabase Auth

## 🏗️ Architecture Overview

### Frontend (Vercel)
- **Platform:** Vercel
- **Framework:** React 18
- **Build Tool:** Create React App with CRACO
- **Styling:** Tailwind CSS
- **Deployment:** Automatic on git push to main

### Backend (Supabase)
- **Platform:** Supabase Cloud
- **Runtime:** Deno (Edge Functions)
- **Database:** PostgreSQL with Row Level Security
- **Authentication:** Supabase Auth
- **Real-time:** Supabase Realtime

## 🔧 Environment Configuration

### Frontend Environment Variables (Vercel)

```bash
# Supabase Configuration
REACT_APP_SUPABASE_URL=https://sftppbnqlsumjlrgyzgo.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNmdHBwYm5xbHN1bWpscmd5emdvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM1MTYwOTksImV4cCI6MjA2OTA5MjA5OX0.EE8EW1fr2GyUo_exh7Sj_kA2mXGWwffxU4aEHXPWjrQ

# Backend API
REACT_APP_BACKEND_URL=https://sftppbnqlsumjlrgyzgo.supabase.co/functions/v1

# Google OAuth
REACT_APP_GOOGLE_CLIENT_ID=266791319799-m9kd1n5t3pdh4oicijppk06sva56asj6.apps.googleusercontent.com
```

### Backend Environment Variables (Supabase)

```bash
# Supabase Configuration
SUPABASE_URL=https://sftppbnqlsumjlrgyzgo.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNmdHBwYm5xbHN1bWpscmd5emdvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM1MTYwOTksImV4cCI6MjA2OTA5MjA5OX0.EE8EW1fr2GyUo_exh7Sj_kA2mXGWwffxU4aEHXPWjrQ
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNmdHBwYm5xbHN1bWpscmd5emdvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzUxNjA5OSwiZXhwIjoyMDY5MDkyMDk5fQ.yG2lyX7WEnbRc8u3z8n3JQSQ72EqmO7hn4Or64NvKGo

# AI Services
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Email Services
SENDGRID_API_KEY=your_sendgrid_api_key_here
SENDER_EMAIL=your_sender_email_here

# JWT Configuration
JWT_SECRET_KEY=aurum-life-secret-key-2025-production-change-this
```

## 🚀 Deployment Process

### Frontend Deployment (Vercel)

1. **Automatic Deployment**
   - Push to `main` branch triggers deployment
   - Vercel builds and deploys automatically
   - Environment variables configured in Vercel dashboard

2. **Manual Deployment**
   ```bash
   # Install Vercel CLI
   npm i -g vercel
   
   # Deploy
   vercel --prod
   ```

3. **Build Configuration**
   - **Build Command:** `yarn build`
   - **Output Directory:** `build`
   - **Install Command:** `yarn install`

### Backend Deployment (Supabase Edge Functions)

1. **Deploy Edge Function**
   ```bash
   # Install Supabase CLI
   npm install -g supabase
   
   # Deploy function
   supabase functions deploy aurum-api
   ```

2. **Manual Deployment via Dashboard**
   - Go to Supabase Dashboard → Edge Functions
   - Create new function: `aurum-api`
   - Copy code from `supabase/functions/aurum-api/index.ts`
   - Deploy

### Database Setup

1. **Schema Migration**
   ```bash
   # Apply migrations
   supabase db push
   ```

2. **Row Level Security**
   - All tables have RLS enabled
   - Users can only access their own data
   - Service role has full access

## 🔒 Security Configuration

### Authentication
- **Provider:** Supabase Auth
- **Methods:** Email/Password, Google OAuth
- **Session Management:** JWT tokens
- **Security:** Row Level Security (RLS)

### API Security
- **Authentication Required:** All endpoints require valid JWT
- **CORS:** Configured for production domain
- **Rate Limiting:** Supabase built-in limits
- **Data Isolation:** User-scoped data access

### Environment Security
- **Secrets Management:** Vercel environment variables
- **Key Rotation:** Regular key updates
- **Access Control:** Team-based access in Vercel

## 📊 Monitoring & Analytics

### Performance Monitoring
- **Vercel Analytics:** Frontend performance
- **Supabase Monitoring:** Database and API metrics
- **Error Tracking:** Built-in error handling

### User Analytics
- **PostHog:** User behavior analytics
- **Ad-blocker Resistant:** Graceful degradation
- **Privacy Focused:** Minimal data collection

## 🔄 CI/CD Pipeline

### Automated Workflows
1. **Code Push** → GitHub
2. **Vercel Build** → Frontend deployment
3. **Supabase Sync** → Database updates
4. **Health Check** → Automated testing

### Manual Processes
- **Edge Function Updates** → Supabase Dashboard
- **Database Migrations** → Supabase CLI
- **Environment Updates** → Vercel Dashboard

## 🛠️ Troubleshooting

### Common Issues

1. **Authentication Errors (401)**
   - Check Supabase anon key validity
   - Verify environment variables in Vercel
   - Ensure user exists in Supabase Auth

2. **Build Failures**
   - Check Node.js version compatibility
   - Verify all dependencies are installed
   - Review build logs in Vercel

3. **Database Connection Issues**
   - Verify Supabase URL and keys
   - Check RLS policies
   - Review database permissions

### Debug Commands
```bash
# Check Supabase connection
npx supabase status

# Test Edge Function locally
supabase functions serve

# Verify environment variables
vercel env ls
```

## 📈 Performance Optimization

### Frontend Optimizations
- **Code Splitting:** Lazy loading of components
- **Image Optimization:** Vercel automatic optimization
- **Caching:** Browser and CDN caching
- **Bundle Size:** Tree shaking and minification

### Backend Optimizations
- **Database Indexing:** Optimized queries
- **Connection Pooling:** Supabase managed
- **Edge Functions:** Global distribution
- **Caching:** Supabase built-in caching

## 🔄 Rollback Procedures

### Frontend Rollback
1. Go to Vercel Dashboard
2. Select deployment to rollback to
3. Click "Promote to Production"

### Backend Rollback
1. Go to Supabase Dashboard
2. Edge Functions → aurum-api
3. Deploy previous version

### Database Rollback
1. Use Supabase migrations
2. Apply previous schema version
3. Verify data integrity

## 📋 Maintenance Checklist

### Daily
- [ ] Monitor application health
- [ ] Check error logs
- [ ] Verify user authentication

### Weekly
- [ ] Review performance metrics
- [ ] Update dependencies
- [ ] Backup critical data

### Monthly
- [ ] Security audit
- [ ] Performance optimization
- [ ] Feature updates

## 🆘 Support & Recovery

### Emergency Contacts
- **Vercel Support:** Dashboard support
- **Supabase Support:** Community + Enterprise
- **Development Team:** GitHub issues

### Recovery Procedures
1. **Identify Issue** → Check logs and metrics
2. **Assess Impact** → User and system impact
3. **Implement Fix** → Code or configuration change
4. **Deploy Solution** → Automated or manual deployment
5. **Verify Resolution** → Testing and monitoring

---

**Last Updated:** January 2025  
**Deployment Status:** ✅ Production Ready  
**Next Review:** February 2025