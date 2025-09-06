# Environment Setup Guide - Aurum Life

This guide explains how to set up the required environment variables for Aurum Life in both development and production environments.

## 🚀 Quick Setup

### Development Environment

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
   
   # Backend (optional for local development)
   cd ../backend
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create frontend environment file
   cp frontend/.env.example frontend/.env.local
   
   # Create backend environment file (if running locally)
   cp backend/.env.example backend/.env
   ```

## 🔧 Environment Variables

### Frontend Configuration (`frontend/.env.local`)

```bash
# Supabase Configuration
REACT_APP_SUPABASE_URL=https://sftppbnqlsumjlrgyzgo.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNmdHBwYm5xbHN1bWpscmd5emdvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM1MTYwOTksImV4cCI6MjA2OTA5MjA5OX0.EE8EW1fr2GyUo_exh7Sj_kA2mXGWwffxU4aEHXPWjrQ

# Backend API
REACT_APP_BACKEND_URL=https://sftppbnqlsumjlrgyzgo.supabase.co/functions/v1

# Google OAuth
REACT_APP_GOOGLE_CLIENT_ID=266791319799-m9kd1n5t3pdh4oicijppk06sva56asj6.apps.googleusercontent.com

# Development Settings
WDS_SOCKET_PORT=443
```

### Backend Configuration (`backend/.env`)

```bash
# Supabase Configuration
SUPABASE_URL=https://sftppbnqlsumjlrgyzgo.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNmdHBwYm5xbHN1bWpscmd5emdvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM1MTYwOTksImV4cCI6MjA2OTA5MjA5OX0.EE8EW1fr2GyUo_exh7Sj_kA2mXGWwffxU4aEHXPWjrQ
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNmdHBwYm5xbHN1bWpscmd5emdvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzUxNjA5OSwiZXhwIjoyMDY5MDkyMDk5fQ.yG2lyX7WEnbRc8u3z8n3JQSQ72EqmO7hn4Or64NvKGo

# AI Services
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash-lite

# Email Services
SENDGRID_API_KEY=your_sendgrid_api_key_here
SENDER_EMAIL=your_sender_email_here

# JWT Configuration
JWT_SECRET_KEY=aurum-life-secret-key-2025-production-change-this

# Google OAuth
GOOGLE_CLIENT_ID=266791319799-m9kd1n5t3pdh4oicijppk06sva56asj6.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
```

## 🌐 Production Environment

### Vercel Configuration

Environment variables are configured in the Vercel dashboard:

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project: `aurum-life-web`
3. Go to **Settings** → **Environment Variables**
4. Add the following variables:

```bash
REACT_APP_SUPABASE_URL=https://sftppbnqlsumjlrgyzgo.supabase.co
REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNmdHBwYm5xbHN1bWpscmd5emdvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM1MTYwOTksImV4cCI6MjA2OTA5MjA5OX0.EE8EW1fr2GyUo_exh7Sj_kA2mXGWwffxU4aEHXPWjrQ
REACT_APP_BACKEND_URL=https://sftppbnqlsumjlrgyzgo.supabase.co/functions/v1
REACT_APP_GOOGLE_CLIENT_ID=266791319799-m9kd1n5t3pdh4oicijppk06sva56asj6.apps.googleusercontent.com
```

### Supabase Configuration

Environment variables are configured in the Supabase dashboard:

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project: `sftppbnqlsumjlrgyzgo`
3. Go to **Settings** → **Edge Functions**
4. Add the following variables:

```bash
SUPABASE_URL=https://sftppbnqlsumjlrgyzgo.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNmdHBwYm5xbHN1bWpscmd5emdvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM1MTYwOTksImV4cCI6MjA2OTA5MjA5OX0.EE8EW1fr2GyUo_exh7Sj_kA2mXGWwffxU4aEHXPWjrQ
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNmdHBwYm5xbHN1bWpscmd5emdvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MzUxNjA5OSwiZXhwIjoyMDY5MDkyMDk5fQ.yG2lyX7WEnbRc8u3z8n3JQSQ72EqmO7hn4Or64NvKGo
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
SENDGRID_API_KEY=your_sendgrid_api_key_here
SENDER_EMAIL=your_sender_email_here
JWT_SECRET_KEY=aurum-life-secret-key-2025-production-change-this
```

## 🔑 API Keys Setup

### Supabase Keys

1. **Get Supabase Keys**
   - Go to [Supabase Dashboard](https://supabase.com/dashboard)
   - Select your project
   - Go to **Settings** → **API**
   - Copy the **Project URL** and **anon public** key

2. **Service Role Key**
   - In the same API settings page
   - Copy the **service_role** key (keep this secret!)

### Google OAuth Setup

1. **Create Google OAuth Credentials**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable Google Sign-In API
   - Go to **Credentials** → **Create Credentials** → **OAuth 2.0 Client IDs**

2. **Configure OAuth Settings**
   - **Authorized JavaScript origins:**
     - `http://localhost:3000` (development)
     - `https://aurum-life-web.vercel.app` (production)
   - **Authorized redirect URIs:**
     - `http://localhost:3000` (development)
     - `https://aurum-life-web.vercel.app` (production)

### OpenAI API Setup

1. **Get OpenAI API Key**
   - Go to [OpenAI Platform](https://platform.openai.com/)
   - Create an account or sign in
   - Go to **API Keys** section
   - Create a new secret key

2. **Set Usage Limits**
   - Set monthly spending limits
   - Monitor usage in the dashboard

### SendGrid Setup

1. **Create SendGrid Account**
   - Go to [SendGrid](https://sendgrid.com/)
   - Create an account
   - Verify your sender email

2. **Get API Key**
   - Go to **Settings** → **API Keys**
   - Create a new API key with full access

## 🛠️ Development Commands

### Frontend Development

```bash
# Start development server
cd frontend
npm start

# Build for production
npm run build

# Run tests
npm test
```

### Backend Development

```bash
# Start local server
cd backend
python server_supabase.py

# Install dependencies
pip install -r requirements.txt
```

### Database Development

```bash
# Start Supabase locally
npx supabase start

# Apply migrations
npx supabase db push

# Reset database
npx supabase db reset
```

## 🔒 Security Best Practices

### Environment Variables

- ✅ **Never commit** `.env` files to version control
- ✅ **Use strong, unique** values for production
- ✅ **Rotate keys** regularly
- ✅ **Use different** credentials for each environment
- ✅ **Restrict access** to production keys

### API Security

- ✅ **Enable RLS** (Row Level Security) in Supabase
- ✅ **Use HTTPS** for all production endpoints
- ✅ **Validate inputs** on both frontend and backend
- ✅ **Implement rate limiting** where appropriate
- ✅ **Monitor access** logs regularly

## 🐛 Troubleshooting

### Common Issues

1. **"Missing Supabase environment variables"**
   - Check that all required variables are set
   - Verify variable names match exactly
   - Restart development server after changes

2. **"Invalid API key" errors**
   - Verify Supabase keys are current
   - Check that keys match your project
   - Ensure no extra spaces or characters

3. **Authentication failures**
   - Verify Google OAuth configuration
   - Check redirect URIs match exactly
   - Ensure client ID is correct

4. **Database connection issues**
   - Verify Supabase URL and keys
   - Check RLS policies are correct
   - Ensure user has proper permissions

### Debug Commands

```bash
# Check environment variables
echo $REACT_APP_SUPABASE_URL

# Test Supabase connection
npx supabase status

# Verify Vercel environment
vercel env ls

# Check build logs
vercel logs
```

## 📋 Environment Checklist

### Development Setup
- [ ] Repository cloned
- [ ] Dependencies installed
- [ ] Environment files created
- [ ] Supabase keys configured
- [ ] Google OAuth setup
- [ ] Development server running

### Production Setup
- [ ] Vercel environment variables set
- [ ] Supabase environment variables set
- [ ] Domain configured
- [ ] SSL certificates active
- [ ] Monitoring enabled
- [ ] Backup procedures in place

---

**Last Updated:** January 2025  
**Environment Status:** ✅ Production Ready  
**Next Review:** February 2025