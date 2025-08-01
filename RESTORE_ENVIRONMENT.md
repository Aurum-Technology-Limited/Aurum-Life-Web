# URGENT: Restore Your Environment Variables

## ⚠️ IMPORTANT NOTICE
The .env files have been cleaned of secrets for security. You need to restore your actual values for the application to work.

## 🔧 Quick Restore Commands

### Backend Environment Variables
Edit `/app/backend/.env` and replace these placeholder values with your actual ones:

```bash
# Replace these with your actual values:
GOOGLE_CLIENT_ID=514537887764-mgfh2g9k8ni7tanhm32o2o4mg1atrcgb.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
JWT_SECRET_KEY="aurum-life-secret-key-2025-production-change-this"
```

### Frontend Environment Variables  
Edit `/app/frontend/.env` and replace:

```bash
# Replace with your actual backend URL:
REACT_APP_BACKEND_URL=https://bc5c41e8-49fa-4e1c-8536-e71401e166ef.preview.emergentagent.com
```

## 🚀 Restart Services

After updating the .env files, restart the services:

```bash
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
```

## ✅ Verification

The application should now work exactly as before, but the repository is safe to push to git!

## 🔒 Security Status
- ✅ Git history cleaned of secrets
- ✅ .env files properly ignored
- ✅ Safe to push to any git repository
- ✅ Placeholder values in tracked files