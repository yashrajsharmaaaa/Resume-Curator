# 🚀 Resume Curator - Quick Start Guide

Get your Resume Curator application running in minutes!

## 📋 Prerequisites

- **Docker Desktop** (recommended) OR
- **Python 3.8+** and **Node.js 16+** (for manual setup)
- **AtlasCloud API Key** (free at https://atlascloud.ai)

## 🐳 Option 1: Docker Deployment (Recommended)

### Windows Users
```cmd
# 1. Clone the repository
git clone <your-repo-url>
cd resume-curator

# 2. Run the deployment script
deploy-local.bat
```

### macOS/Linux Users
```bash
# 1. Clone the repository
git clone <your-repo-url>
cd resume-curator

# 2. Make script executable and run
chmod +x deploy-local.sh
./deploy-local.sh
```

### Manual Docker Steps
```bash
# 1. Create environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# 2. Edit backend/.env and add your AtlasCloud API key
# ATLASCLOUD_API_KEY=your_api_key_here

# 3. Start all services
docker-compose up --build -d

# 4. Access the application
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

## 💻 Option 2: Manual Setup

### Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your AtlasCloud API key
python main.py
```

### Frontend Setup (New Terminal)
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## 🌐 Cloud Deployment

### Deploy Frontend (GitHub Pages)
```bash
cd frontend
npm install --save-dev gh-pages
npm run deploy
```

### Deploy Backend (Render)
1. Push code to GitHub
2. Connect repository to Render
3. Create Web Service from `backend` folder
4. Add environment variables in Render dashboard
5. Deploy automatically

## 🔧 Configuration

### Required Environment Variables

**Backend (.env)**
```env
ATLASCLOUD_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./resume_curator.db
```

**Frontend (.env)**
```env
VITE_API_URL=http://localhost:8000
```

## ✅ Verify Deployment

1. **Health Check**: Visit http://localhost:8000/health
2. **Frontend**: Visit http://localhost:3000
3. **API Docs**: Visit http://localhost:8000/docs
4. **Upload Test**: Try uploading a resume file

## 🚨 Troubleshooting

### Common Issues

**Docker not starting?**
- Ensure Docker Desktop is running
- Check if ports 3000, 8000, 5432 are available

**Backend errors?**
- Verify AtlasCloud API key is correct
- Check backend logs: `docker-compose logs backend`

**Frontend not loading?**
- Check if backend is running first
- Verify API URL in frontend/.env

**File upload failing?**
- Ensure file is PDF or DOCX format
- Check file size is under 10MB

### Get Help
```bash
# View all service logs
docker-compose logs -f

# Check specific service
docker-compose logs backend
docker-compose logs frontend

# Restart services
docker-compose restart

# Stop everything
docker-compose down
```

## 🎯 Next Steps

1. **Customize**: Update branding and colors
2. **Deploy**: Push to production (Render + GitHub Pages)
3. **Monitor**: Set up logging and analytics
4. **Scale**: Add more features and optimizations

## 📚 Additional Resources

- [Full Deployment Guide](DEPLOYMENT_GUIDE.md)
- [API Documentation](http://localhost:8000/docs)
- [AtlasCloud API Docs](https://docs.atlascloud.ai)
- [Docker Documentation](https://docs.docker.com)

---

**Need help?** Check the troubleshooting section or review the logs for specific error messages.