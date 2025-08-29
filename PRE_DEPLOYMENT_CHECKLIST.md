# Pre-Deployment Checklist

Complete these tasks manually before deploying to production.

## 🔐 Security & Environment Setup

### 1. Update Environment Variables
- [x] **Backend `.env`**: ✅ Secure SECRET_KEY generated and applied
  ```bash
  # ✅ COMPLETED - Secure key generated: T0dM7MNi...
  SECRET_KEY=T0dM7MNiG0Q5cZksBuJM8gYKW_1LHW_PblaGIvSs9WY
  ```

- [ ] **AtlasCloud API Key**: Verify your API key is valid and test the connection
  ```bash
  ATLASCLOUD_API_KEY=apikey-fbdba7c40f58477ba0090a1f14e62346
  
  # Test the API key:
  cd backend
  python -c "from ai_analysis_service import test_ai_service; import asyncio; print(asyncio.run(test_ai_service()))"
  ```

- [ ] **Database URL**: Update for production database
  ```bash
  # Current: SQLite (development only)
  DATABASE_URL=sqlite:///./resume_curator.db
  
  # Production should use PostgreSQL:
  DATABASE_URL=postgresql://user:password@host:port/database
  ```

### 2. Create Production Environment Files
- [ ] Create `backend/.env.production` with production values
- [ ] Create `frontend/.env.production` with production API URL
- [ ] Ensure no sensitive data in `.env.example` files

## 🗄️ Database Setup

### 3. Database Migration
- [ ] **If using PostgreSQL**: Set up production database
- [ ] **If keeping SQLite**: Ensure database file is in persistent storage
- [ ] Test database connection with production credentials
- [ ] Run database initialization:
  ```bash
  cd backend
  python -c "from database import init_database; init_database()"
  ```

## 🧪 Testing & Validation

### 4. Test the Application
- [ ] **Backend API**: Test all endpoints work
  ```bash
  cd backend
  python development_server.py
  # Visit http://localhost:8000/docs to test API
  ```

- [ ] **Frontend**: Test the complete user flow
  ```bash
  cd frontend
  npm run dev
  # Test file upload, job description input, and analysis
  ```

- [ ] **Integration**: Test frontend → backend communication
- [ ] **AI Service**: Verify AtlasCloud integration works

### 5. Run Test Suites
- [ ] **Backend tests**:
  ```bash
  cd backend
  python run_test_suite.py
  ```

- [ ] **Frontend tests** (if any):
  ```bash
  cd frontend
  npm test
  ```

## 📦 Build & Dependencies

### 6. Verify Dependencies
- [ ] **Backend**: Check `requirements.txt` is up to date
  ```bash
  cd backend
  pip freeze > requirements.txt
  ```

- [ ] **Frontend**: Ensure `package.json` has correct dependencies
- [ ] Remove any unused dependencies

### 7. Build Testing
- [ ] **Frontend production build**:
  ```bash
  cd frontend
  npm run build
  # Check dist/ folder is created successfully
  ```

- [ ] **Docker builds** (if using Docker):
  ```bash
  docker-compose build
  docker-compose up -d
  # Test the containerized application
  ```

## 🚀 Deployment Configuration

### 8. Update Configuration Files
- [ ] **CORS Origins**: Update allowed origins in backend
  ```python
  # In backend/main.py or development_server.py
  allow_origins=[
      "https://your-production-domain.com",
      "https://www.your-production-domain.com"
  ]
  ```

- [ ] **API URL**: Update frontend API URL
  ```bash
  # In frontend/.env.production
  VITE_API_URL=https://api.your-domain.com
  ```

### 9. SSL/HTTPS Setup
- [ ] Obtain SSL certificates for production domain
- [ ] Configure HTTPS in your deployment platform
- [ ] Update all URLs to use HTTPS

## 🔍 Code Review

### 10. Clean Up Development Code
- [ ] Remove any `console.log()` statements from frontend
- [ ] Remove debug print statements from backend
- [ ] Remove any TODO comments or placeholder code
- [ ] Verify no hardcoded development URLs

### 11. Documentation
- [ ] Update `README.md` with deployment instructions
- [ ] Document environment variables needed
- [ ] Add API documentation links
- [ ] Update any outdated information

## 🌐 Platform-Specific Setup

### 12. Choose Deployment Platform
Select and configure one:

#### Option A: Vercel (Frontend) + Railway/Render (Backend)
- [ ] Connect GitHub repository to Vercel
- [ ] Set up backend on Railway or Render
- [ ] Configure environment variables on both platforms

#### Option B: Docker + Cloud Provider
- [ ] Test Docker Compose setup
- [ ] Configure cloud provider (AWS, GCP, Azure)
- [ ] Set up container registry

#### Option C: Traditional VPS
- [ ] Set up server with Node.js and Python
- [ ] Configure reverse proxy (Nginx)
- [ ] Set up process manager (PM2, systemd)

## 📊 Monitoring & Analytics

### 13. Set Up Monitoring
- [ ] Add error tracking (Sentry, LogRocket)
- [ ] Set up uptime monitoring
- [ ] Configure log aggregation
- [ ] Add performance monitoring

## 🔄 CI/CD Pipeline

### 14. Automated Deployment
- [ ] Set up GitHub Actions or similar CI/CD
- [ ] Configure automated testing
- [ ] Set up deployment triggers
- [ ] Test the deployment pipeline

## ✅ Final Checks

### 15. Pre-Launch Verification
- [ ] All environment variables are set correctly
- [ ] Database is accessible and initialized
- [ ] AI service (AtlasCloud) is working
- [ ] Frontend builds without errors
- [ ] Backend starts without errors
- [ ] All tests pass
- [ ] HTTPS is working
- [ ] Domain is configured correctly

### 16. Backup & Recovery
- [ ] Set up database backups
- [ ] Document recovery procedures
- [ ] Test backup restoration

## 🚨 Critical Security Items

### ⚠️ MUST DO BEFORE PRODUCTION:
1. **Change the SECRET_KEY** - Current one is a placeholder!
2. **Verify API keys** - Ensure they're valid and have proper permissions
3. **Use HTTPS** - Never deploy without SSL in production
4. **Database security** - Use proper authentication and encryption
5. **CORS configuration** - Only allow your production domains

## 📝 Deployment Commands Reference

```bash
# Backend (example for Railway/Render)
git push origin main  # Triggers deployment

# Frontend (example for Vercel)
npm run build  # Local test
git push origin main  # Triggers Vercel deployment

# Docker (example for cloud deployment)
docker-compose -f docker-compose.prod.yml up -d
```

---

**⚠️ Important**: Do not skip the security items marked as "MUST DO". They are critical for a safe production deployment.