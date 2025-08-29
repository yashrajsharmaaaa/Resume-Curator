# Resume Curator

> AI-powered resume analysis and job compatibility assessment platform

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/react-18+-blue.svg)](https://reactjs.org)

## Overview

Resume Curator is an **SDE1 portfolio project** demonstrating full-stack development skills with AI integration, clean architecture, and modern deployment practices.

### Key Features
- **AI-Powered Analysis**: Resume analysis using AtlasCloud GPT models
- **Job Matching**: Compare resumes against job descriptions with compatibility scoring
- **Full-Stack Architecture**: FastAPI backend + React frontend + PostgreSQL
- **Docker Containerization**: Complete Docker setup for easy deployment
- **Testing Suite**: Comprehensive pytest testing framework
- **Input Validation**: File type validation, rate limiting, and security
- **Modern UI**: Responsive React interface with professional design

## Quick Start (Docker - Recommended)

### Prerequisites
- Docker & Docker Compose
- AtlasCloud API key

### 1. Clone & Setup
```bash
git clone <repository-url>
cd resume-curator
cp backend/.env.example backend/.env
# Add your ATLASCLOUD_API_KEY to backend/.env
```

### 2. Start with Docker
```bash
docker-compose up --build
```

### 3. Access Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Manual Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/resume-curator.git
cd resume-curator
```

### 2. Setup AI Provider

**AtlasCloud AI Setup**
```bash
# Get API key from AtlasCloud
# Edit backend/.env:
ATLASCLOUD_API_KEY=your_api_key_here
AI_PROVIDER=atlascloud
```

### 3. Database Setup
```bash
python setup_postgresql.py
```

### 4. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### 5. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` to access the application.

## 🤖 AI Providers

### AtlasCloud (Cloud-based)
- **Cost**: Low-cost alternative to OpenAI
- **Models**: Access to GPT and other models
- **Setup**: Get API key from AtlasCloud
- **Privacy**: Medium (cloud-based)

### Simple Setup
The application uses AtlasCloud for AI analysis, providing reliable cloud-based AI processing.

## ⚙️ Configuration

### Environment Variables (.env)

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/resume_curator

# AtlasCloud AI
ATLASCLOUD_API_KEY=your_api_key_here
ATLASCLOUD_MODEL=openai/gpt-oss-20b

# AI Provider Selection
AI_PROVIDER=atlascloud

# Security
SECRET_KEY=your_secret_key_here
```

## 🧪 Testing

### Test AtlasCloud Integration
```bash
python test_atlascloud.py
```

### Test Database Connection
```bash
python test_db_connection.py
```

### Run Backend Tests
```bash
cd backend
pytest
```

## 📚 Documentation

- **[AtlasCloud Setup](ATLASCLOUD_SETUP.md)**: Complete AtlasCloud integration guide
- **[PostgreSQL Setup](POSTGRESQL_SETUP.md)**: Database setup guide
- **[Deployment Guide](DEPLOYMENT.md)**: Production deployment instructions

## 🏗️ Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **PostgreSQL**: Robust database with async support
- **SQLModel**: Modern ORM with Pydantic integration

- **AtlasCloud**: Cloud-based AI models for enhanced analysis
- **NLTK**: Natural language processing toolkit

### Frontend
- **React 18**: Modern React with hooks and context
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Smooth animations and transitions
- **Lucide React**: Beautiful icon library

## 📁 Project Structure

```
resume-curator/
├── backend/                 # FastAPI backend
│   ├── ai_analysis/        # AI integration (AtlasCloud)
│   ├── api/                # API endpoints
│   ├── database/           # Database models and migrations
│   ├── services/           # Business logic
│   └── validation/         # Input validation and security
├── frontend/               # React frontend
│   ├── src/components/     # React components
│   ├── src/services/       # API services
│   └── src/styles/         # CSS and styling
└── docs/                   # Documentation
```

## 🔒 Security Features

- File upload validation and sanitization
- Rate limiting and request throttling
- Secure session management
- Input validation and SQL injection protection
- CORS configuration
- Security headers and middleware

## 🚀 Deployment

### Docker Deployment
```bash
docker-compose up -d
```

### Manual Deployment
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: Report bugs on GitHub Issues
- **Documentation**: Check the setup guides above
- **AI Integration**: See AtlasCloud setup guide

---

🚀 **Ready to analyze resumes with AI!** Choose your preferred AI provider and start optimizing resumes today.

## 🎯 Portfolio Project

This is a portfolio project showcasing full-stack development skills for job applications.

### Live Demo
- **Frontend**: https://yashrajsharmaaaa.github.io/resume-curator
- **Backend API**: https://resume-curator-api.onrender.com
- **Source Code**: https://github.com/yashrajsharmaaaa/resume-curator

### Skills Demonstrated
- **Frontend**: React, Vite, Tailwind CSS, Responsive Design
- **Backend**: FastAPI, Python, RESTful APIs
- **Database**: SQLite/PostgreSQL, Data Modeling
- **AI Integration**: AtlasCloud API, Natural Language Processing
- **DevOps**: GitHub Actions, CI/CD, Deployment
- **Tools**: Git, npm, pip, Environment Management

### Features for Recruiters
- Upload resume files (PDF, DOC, DOCX)
- AI-powered resume analysis and feedback
- Job description matching and scoring
- Responsive design for all devices
- Professional UI/UX design

### Technical Highlights
- Clean, maintainable code architecture
- Proper error handling and validation
- Automated testing and deployment
- Security best practices
- Modern development workflow

---

*This project was built to demonstrate my capabilities as a full-stack developer and my ability to integrate modern AI services into web applications.*