# Resume Curator - Deployment Guide

## 🚀 **Ready for Hosting!**

This guide covers deploying Resume Curator in both development and production environments.

---

## 📋 **Pre-Deployment Checklist**

### ✅ **Completed Setup**
- [x] Fixed corrupted requirements.txt
- [x] Multi-stage Docker builds (dev/prod)
- [x] Environment configuration
- [x] Production optimizations
- [x] Database configuration
- [x] AtlasCloud AI integration

### ⚠️ **Requirements**
- Docker Desktop installed and running
- AtlasCloud API key (for AI features)
- 2GB+ available RAM
- 10GB+ available disk space

---

## 🏃‍♂️ **Quick Start (Development)**

### 1. Start Docker Desktop
Ensure Docker Desktop is running on your system.

### 2. Clone & Configure
```bash
cd resume-curator
cp backend/.env.example backend/.env
# Edit backend/.env and add your ATLASCLOUD_API_KEY
```

### 3. Launch Application
```bash
# Development mode (with hot reload)
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 4. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: localhost:5432

---

## 🏭 **Production Deployment**

### 1. Environment Setup
```bash
# Copy production environment
cp backend/.env.production backend/.env

# Edit and configure:
# - ATLASCLOUD_API_KEY (required)
# - SECRET_KEY (change from default)
# - CORS_ORIGINS (add your domain)
```

### 2. Production Build & Deploy
```bash
# Build and start production containers
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d
```

### 3. Production Access
- **Frontend**: http://localhost (port 80)
- **Backend API**: http://localhost:8000
- **Database**: Internal Docker network

---

## 🔧 **Configuration Options**

### Backend Environment Variables
```env
# Required
ATLASCLOUD_API_KEY=your-api-key-here

# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/resume_curator

# Security (CHANGE IN PRODUCTION!)
SECRET_KEY=your-strong-secret-key-here

# CORS (Update for your domain)
CORS_ORIGINS=["https://yourdomain.com"]

# File Upload
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=[".pdf", ".doc", ".docx"]
```

### AtlasCloud Configuration
Get your API key from [AtlasCloud](https://api.atlascloud.ai/):
1. Sign up for AtlasCloud account
2. Generate API key
3. Add to `ATLASCLOUD_API_KEY` in `.env`

---

## 🧪 **Testing & Verification**

### 1. Health Checks
```bash
# Check all services
docker-compose ps

# Test backend health
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000
```

### 2. API Testing
```bash
# Test API endpoints
curl http://localhost:8000/api/health
curl http://localhost:8000/docs  # Interactive API docs
```

### 3. Run Backend Tests
```bash
# Run test suite
docker-compose exec backend pytest
```

---

## 📊 **Monitoring & Logs**

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs postgres
```

### Monitor Resources
```bash
# Docker stats
docker stats

# Service status
docker-compose ps
```

---

## 🔒 **Security Considerations**

### Production Security
1. **Change default credentials**:
   - Database password
   - Secret key
   - AtlasCloud API key

2. **Update CORS origins**:
   - Remove localhost from production
   - Add your actual domain

3. **File upload security**:
   - Validate file types
   - Scan uploaded files
   - Limit file sizes

### Network Security
- Use HTTPS in production
- Configure firewall rules
- Regular security updates

---

## 🌐 **Cloud Hosting Options**

### Docker-friendly Hosting
1. **Digital Ocean App Platform**
2. **AWS ECS/Fargate**
3. **Google Cloud Run**
4. **Azure Container Instances**
5. **Railway**
6. **Heroku** (with Docker)

### Traditional VPS
1. **DigitalOcean Droplets**
2. **AWS EC2**
3. **Google Compute Engine**
4. **Linode**

---

## 🐛 **Troubleshooting**

### Common Issues

#### Docker Build Fails
```bash
# Clear Docker cache
docker system prune -a
docker-compose build --no-cache
```

#### Database Connection Issues
- Check PostgreSQL is running: `docker-compose ps postgres`
- Verify DATABASE_URL in .env
- Check network connectivity

#### AtlasCloud API Errors
- Verify API key is correct
- Check internet connectivity
- Review API rate limits

#### Frontend Build Issues
- Clear node_modules: `docker-compose exec frontend rm -rf node_modules`
- Rebuild: `docker-compose build frontend --no-cache`

---

## 📈 **Performance Optimization**

### Production Optimizations
1. **Enable gzip compression** (nginx)
2. **Use CDN** for static assets
3. **Database connection pooling**
4. **Redis caching** (optional)
5. **Load balancing** (multiple instances)

### Resource Allocation
- **Backend**: 512MB RAM minimum
- **Frontend**: 256MB RAM minimum  
- **Database**: 1GB RAM minimum
- **Total**: ~2GB RAM recommended

---

## 🔄 **Updates & Maintenance**

### Regular Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild containers
docker-compose build --no-cache

# Restart services
docker-compose up -d
```

### Database Backups
```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres resume_curator > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres resume_curator < backup.sql
```

---

## ✅ **Deployment Checklist**

### Pre-deployment
- [ ] Docker Desktop running
- [ ] AtlasCloud API key configured
- [ ] Environment variables set
- [ ] Secret key changed (production)
- [ ] CORS origins updated (production)

### Deployment
- [ ] Docker containers build successfully
- [ ] All services start and show healthy
- [ ] Frontend accessible
- [ ] Backend API responding
- [ ] Database connection working
- [ ] File upload functional
- [ ] AI analysis working

### Post-deployment
- [ ] Run test suite
- [ ] Check logs for errors
- [ ] Monitor resource usage
- [ ] Verify security settings
- [ ] Document any custom configurations

---

## 🎯 **Success Metrics**

Your deployment is successful when:
- ✅ All containers start without errors
- ✅ Health checks pass for all services
- ✅ Frontend loads and is responsive
- ✅ File upload works end-to-end
- ✅ AI analysis generates results
- ✅ No critical errors in logs

---

**🚀 Ready to deploy! Your Resume Curator is production-ready!**