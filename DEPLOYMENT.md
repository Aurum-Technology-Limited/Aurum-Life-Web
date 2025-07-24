# Deployment Configuration Template

## Environment-Specific Configurations

### Development Environment
```bash
# Backend
MONGO_URL=mongodb://localhost:27017
REACT_APP_BACKEND_URL=http://localhost:8001
GOOGLE_CLIENT_ID=your-dev-google-client-id
GOOGLE_CLIENT_SECRET=your-dev-google-client-secret
JWT_SECRET_KEY="dev-jwt-secret-key"
```

### Staging Environment
```bash
# Backend
MONGO_URL=mongodb://staging-db-url:27017/aurum_staging
REACT_APP_BACKEND_URL=https://staging-api.yourapp.com
GOOGLE_CLIENT_ID=your-staging-google-client-id
GOOGLE_CLIENT_SECRET=your-staging-google-client-secret
JWT_SECRET_KEY="staging-jwt-secret-key-64-chars-minimum"
```

### Production Environment
```bash
# Backend
MONGO_URL=mongodb://prod-db-cluster:27017/aurum_production
REACT_APP_BACKEND_URL=https://api.yourapp.com  
GOOGLE_CLIENT_ID=your-prod-google-client-id
GOOGLE_CLIENT_SECRET=your-prod-google-client-secret
JWT_SECRET_KEY="production-jwt-secret-key-must-be-very-secure-64-chars-minimum"
```

## Deployment Checklist

### Before Deployment:
- [ ] Copy `.env.example` files to `.env`
- [ ] Fill in environment-specific values
- [ ] Verify all required environment variables are set
- [ ] Test with development values first
- [ ] Rotate secrets for production

### Security Best Practices:
- [ ] Use different credentials for each environment
- [ ] Use strong, random JWT secrets (64+ characters)
- [ ] Restrict Google OAuth domains in production
- [ ] Use environment variable injection in CI/CD
- [ ] Never commit actual `.env` files

### Monitoring:
- [ ] Set up logging for authentication events
- [ ] Monitor for failed login attempts
- [ ] Set up alerts for security issues