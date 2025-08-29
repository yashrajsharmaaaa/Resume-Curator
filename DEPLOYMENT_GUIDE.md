# 🚀 Deployment Guide: Vercel + Railway

This guide walks you through deploying Resume Curator using Vercel (frontend) and Railway (backend).

## 📋 Prerequisites

- [x] GitHub repository with your code
- [x] Vercel account (free)
- [x] Railway account (free)
- [x] AtlasCloud API key

## 🎯 Deployment Strategy

**Frontend (React/Vite)** → **Vercel**
**Backend (FastAPI)** → **Railway**
**Database** → **Railway PostgreSQL**

---

## 🚂 Step 1: Deploy Backend to Railway

### 1.1 Create Railway Project
1. Go to [railway.app](https://railway.app)
2. Sign up/login with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your `resume-curator` repository

### 1.2 Configure Railway Environment
In Railway dashboard, go to Variables and add:

```env
# Required Environment Variables
SECRET_KEY=T0dM7MNiG0Q5cZksBuJM8gYKW_1LHW_PblaGIvSs9WY
ATLASCLOUD_API_KEY=apikey-fbdba7c40f58477ba0090a1f14e62346
AI_PROVIDER=atlascloud
ATLASCLOUD_MODEL=openai/gpt-oss-20b
ATLASCLOUD_BASE_URL=https://api.atlascloud.ai/v1
ATLASCLOUD_TEMPERATURE=0.7
ATLASCLOUD_MAX_TOKENS=1024

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false
RELOAD=false

# File Upload
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=[".pdf", ".doc", ".docx"]

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=30

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=detailed
ENVIRONMENT=production
```

### 1.3 Add PostgreSQL Database
1. In Railway dashboard, click "New Service"
2. Select "PostgreSQL"
3. Railway will automatically set `DATABASE_URL`

### 1.4 Update CORS Origins
After deployment, Railway will give you a URL like `https://your-app.railway.app`

Add this to your Railway environment variables:
```env
CORS_ORIGINS=["https://your-frontend-domain.vercel.app", "https://your-app.railway.app"]
```

---

## 🌐 Step 2: Deploy Frontend to Vercel

### 2.1 Create Vercel Project
1. Go to [vercel.com](https://vercel.com)
2. Sign up/login with GitHub
3. Click "New Project"
4. Import your `resume-curator` repository

### 2.2 Configure Build Settings
Vercel should auto-detect, but verify:
- **Framework Preset**: Vite
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`

### 2.3 Set Environment Variables
In Vercel dashboard, go to Settings → Environment Variables:

```env
VITE_API_URL=https://your-backend.railway.app/api
VITE_API_TIMEOUT=30000
VITE_NODE_ENV=production
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_ERROR_REPORTING=true
```

### 2.4 Deploy
Click "Deploy" - Vercel will build and deploy your frontend.

---

## 🔧 Step 3: Final Configuration

### 3.1 Update CORS in Railway
Once you have your Vercel URL (e.g., `https://resume-curator.vercel.app`), update Railway environment:

```env
CORS_ORIGINS=["https://resume-curator.vercel.app", "https://www.resume-curator.vercel.app"]
```

### 3.2 Test the Deployment
1. Visit your Vercel frontend URL
2. Try uploading a resume
3. Check if AI analysis works
4. Verify all features function correctly

---

## 🎉 Success Checklist

- [ ] Backend deployed to Railway
- [ ] PostgreSQL database connected
- [ ] Frontend deployed to Vercel
- [ ] Environment variables configured
- [ ] CORS properly set up
- [ ] AI analysis working
- [ ] File upload working
- [ ] All features tested

---

## 🔍 Troubleshooting

### Backend Issues
- Check Railway logs in dashboard
- Verify environment variables are set
- Test `/health` endpoint: `https://your-backend.railway.app/health`

### Frontend Issues
- Check Vercel build logs
- Verify `VITE_API_URL` points to Railway backend
- Check browser console for CORS errors

### Database Issues
- Verify `DATABASE_URL` is automatically set by Railway
- Check if database initialization ran successfully

---

## 💰 Cost Estimate

**Railway (Backend + Database)**
- Free tier: $5/month credit
- Typical usage: $0-5/month

**Vercel (Frontend)**
- Free tier: 100GB bandwidth
- Typical usage: $0/month

**Total: $0-5/month** for a production-ready deployment!

---

## 🚀 Next Steps

1. **Custom Domain**: Add your own domain in Vercel settings
2. **SSL**: Automatic with both Vercel and Railway
3. **Monitoring**: Set up error tracking (Sentry)
4. **Analytics**: Add usage analytics
5. **CI/CD**: Automatic deployments on git push (already configured)

Your Resume Curator is now production-ready! 🎉