#!/bin/bash

# Aurum Life - Supabase Deployment Script
# This script deploys the frontend and backend to Supabase

set -e

echo "🚀 Starting Aurum Life Supabase Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Supabase CLI is installed
if ! command -v supabase &> /dev/null; then
    echo -e "${RED}❌ Supabase CLI is not installed. Please install it first:${NC}"
    echo "npm install -g supabase"
    exit 1
fi

# Check if Vercel CLI is installed (for frontend deployment)
if ! command -v vercel &> /dev/null; then
    echo -e "${YELLOW}⚠️  Vercel CLI is not installed. Installing...${NC}"
    npm install -g vercel
fi

echo -e "${BLUE}📦 Building frontend for production...${NC}"
cd frontend

# Build frontend with production environment variables
REACT_APP_BACKEND_URL=https://sftppbnqlsumjlrgyzgo.supabase.co/functions/v1 \
REACT_APP_SUPABASE_URL=https://sftppbnqlsumjlrgyzgo.supabase.co \
REACT_APP_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNmdHBwYm5xbHN1bWpscmd5emdvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDgzNjI3OTUsImV4cCI6MjAyMzk3ODc5NX0.PzL5W-OcWZwwFGj_YIAjGDCdtqvgM8mPQy1Yl-xW-S8 \
REACT_APP_GOOGLE_CLIENT_ID=266791319799-m9kd1n5t3pdh4oicijppk06sva56asj6.apps.googleusercontent.com \
yarn build

echo -e "${GREEN}✅ Frontend build completed!${NC}"

echo -e "${BLUE}🚀 Deploying frontend to Vercel...${NC}"
vercel --prod --yes

echo -e "${BLUE}🔧 Deploying backend to Supabase Edge Functions...${NC}"
cd ../supabase

# Deploy Edge Function
supabase functions deploy aurum-api

echo -e "${GREEN}✅ Backend deployed to Supabase Edge Functions!${NC}"

echo -e "${BLUE}📊 Setting up database schema...${NC}"
# Run database migrations
supabase db push

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Next steps:${NC}"
echo "1. Update your Vercel environment variables:"
echo "   - REACT_APP_BACKEND_URL=https://sftppbnqlsumjlrgyzgo.supabase.co/functions/v1"
echo "   - REACT_APP_SUPABASE_URL=https://sftppbnqlsumjlrgyzgo.supabase.co"
echo "   - REACT_APP_SUPABASE_ANON_KEY=your_anon_key"
echo "   - REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id"
echo ""
echo "2. Set up Supabase Edge Function environment variables:"
echo "   - SUPABASE_URL=https://sftppbnqlsumjlrgyzgo.supabase.co"
echo "   - SUPABASE_ANON_KEY=your_anon_key"
echo "   - OPENAI_API_KEY=your_openai_key"
echo ""
echo "3. Configure CORS in Supabase Dashboard if needed"
echo "4. Test your deployed application!"
echo ""
echo -e "${GREEN}🚀 Your Aurum Life app is now live on Supabase!${NC}"
