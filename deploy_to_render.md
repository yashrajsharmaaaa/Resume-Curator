# Deploy Backend to Render

## Quick Deployment Steps

### 1. Create Render Account
- Go to [render.com](https://render.com)
- Sign up with your GitHub account

### 2. Create Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository: `Resume-Curator`
3. Configure the service:

**Basic Settings:**
- **Name**: `resume-curator-api`
- **Region**: `Oregon (US West)`
- **Branch**: `main`
- **Root Directory**: `backend`
- **Runtime**: `Python 3`

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python main.py`

**Environment Variables:**
```
SECRET_KEY=T0dM7MNiG0Q5cZksBuJM8gYKW_1LHW_PblaGIvSs9WY
DATABASE_URL=sqlite:///./resume_curator.db
ATLASCLOUD_API_KEY=apikey-fbdba7c40f58477ba0090a1f14e62346
ATLASCLOUD_MODEL=openai/gpt-oss-20b
AI_PROVIDER=atlascloud
HOST=0.0.0.0
PORT=10000
CORS_ORIGINS=["https://yashrajsharmaaaa.github.io"]
ENVIRONMENT=production
```

### 3. Deploy
- Click "Create Web Service"
- Wait for deployment (5-10 minutes)
- Your API will be available at: `https://resume-curator-api.onrender.com`

### 4. Test Deployment
Visit: `https://resume-curator-api.onrender.com/health`

## Current Status

✅ **Frontend**: Auto-deploys to GitHub Pages on every push
✅ **Backend Config**: Ready for Render deployment  
✅ **API Key**: Updated and configured
✅ **CORS**: Configured for GitHub Pages

## Next Steps

1. Deploy backend to Render using steps above
2. Test the full application at: https://yashrajsharmaaaa.github.io/resume-curator
3. Verify API connectivity between frontend and backend

## Troubleshooting

If deployment fails:
- Check Render logs for errors
- Verify all environment variables are set
- Ensure `requirements.txt` includes all dependencies
- Check that `main.py` starts the server correctly