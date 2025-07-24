# Environment Configuration Guide

This guide explains how to set up the required environment variables for Aurum Life.

## Quick Setup

1. Copy the example files:
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```

2. Fill in your actual values in the `.env` files (see sections below)

## Backend Configuration (`backend/.env`)

### Database
- `MONGO_URL`: MongoDB connection string
- `DB_NAME`: Database name (default: `aurum_life`)

### Authentication
- `JWT_SECRET_KEY`: Secret key for JWT token signing (use a strong, random string)

### Email (SendGrid)
- `SENDGRID_API_KEY`: Your SendGrid API key for sending emails
- `SENDER_EMAIL`: Email address used as sender for system emails
- `RESET_TOKEN_EXPIRY_HOURS`: Password reset token expiry (default: 24)

### Google OAuth 2.0
- `GOOGLE_CLIENT_ID`: Google OAuth Client ID from Google Cloud Console
- `GOOGLE_CLIENT_SECRET`: Google OAuth Client Secret from Google Cloud Console

#### Setting up Google OAuth:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Sign-In API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
5. Set authorized origins and redirect URIs for your domain

## Frontend Configuration (`frontend/.env`)

### API Connection
- `REACT_APP_BACKEND_URL`: Full URL to your backend API
- `WDS_SOCKET_PORT`: WebSocket port for development (default: 443)

## Security Notes

⚠️ **Important**: 
- Never commit `.env` files to version control
- Use strong, unique values for production
- Rotate secrets regularly
- Use different values for development/staging/production

## Development vs Production

### Development
- Use `http://localhost` URLs
- Use test/demo API keys where possible
- JWT secret can be simpler

### Production
- Use HTTPS URLs
- Use production API keys
- Use strong, random JWT secret (64+ characters)
- Enable additional security measures