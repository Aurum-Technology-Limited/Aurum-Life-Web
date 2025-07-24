# Aurum Life - Personal Growth & Productivity Platform

A comprehensive personal growth application with task management, goal tracking, and AI-powered insights.

## 🚀 Quick Start

### 1. Environment Setup

**Important**: This application requires environment variables for security and API integrations.

```bash
# Copy example environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Then edit the `.env` files with your actual values. See [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) for detailed instructions.

### 2. Installation

```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies  
cd ../frontend
yarn install
```

### 3. Run the Application

```bash
# Start backend (from backend directory)
python server.py

# Start frontend (from frontend directory)
yarn start
```

## 🔐 Security Notes

- **Never commit `.env` files** - they contain sensitive credentials
- Use the provided `.env.example` files as templates
- See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment guidance
- Rotate secrets regularly in production

## 📚 Documentation

- [Environment Setup Guide](ENVIRONMENT_SETUP.md) - Detailed environment configuration
- [Deployment Guide](DEPLOYMENT.md) - Production deployment instructions

## 🏗️ Architecture

- **Frontend**: React with Tailwind CSS
- **Backend**: FastAPI with MongoDB
- **Authentication**: JWT + Google OAuth 2.0
- **Features**: Task management, goal tracking, insights, journaling

## 🔧 Development

The application supports both traditional email/password authentication and Google OAuth 2.0 sign-in.
