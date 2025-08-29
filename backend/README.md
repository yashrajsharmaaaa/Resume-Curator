# Resume Curator Backend

FastAPI backend for the Resume Curator application.

## Setup

1. Create and activate virtual environment:
```bash
py -m venv venv
venv\Scripts\activate.ps1  # Windows PowerShell
# or
venv\Scripts\activate.bat  # Windows CMD
```

2. Install dependencies:
pip install -r requirements.txt
```

3. Copy environment configuration:
Or directly with uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
## API Documentation

Once running, visit:
- API docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc