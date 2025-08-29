"""
API endpoints for Resume Curator application.

This module provides clean, focused REST API endpoints for:
- File upload and validation
- Resume analysis using AtlasCloud
- Health checks and monitoring

Designed for SDE1 portfolio demonstration with proper error handling,
validation, and security measures.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request, status, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from database import get_db
from models import Resume, AnalysisResult, ResumeUploadResponse, AnalysisRequest, AnalysisResponse, HealthResponse
from validation import (
    validate_file_upload, validate_job_description, check_rate_limit, 
    validate_and_raise, create_validation_error
)
from ai_analysis_service import analyze_resume, test_ai_service, get_ai_service
from resume_file_processor import extract_text_from_file

# Configure logging
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter()


# File upload endpoints
@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    request: Request,
    file: UploadFile = File(..., description="Resume file (PDF, DOC, DOCX)"),
    db: Session = Depends(get_db)
):
    """
    Upload and process a resume file.
    
    Args:
        request: HTTP request for rate limiting
        file: Uploaded resume file
        db: Database session
        
    Returns:
        ResumeUploadResponse with upload status and metadata
        
    Raises:
        HTTPException: If validation fails or processing errors occur
    """
    try:
        # Check rate limits
        check_rate_limit(request, 'upload')
        
        # Validate file upload
        validation_result = validate_file_upload(file)
        validate_and_raise(validation_result, "file")
        
        # Extract text from file
        try:
            extracted_text = await extract_text_from_file(file)
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            raise create_validation_error(
                "TEXT_EXTRACTION_ERROR",
                f"Could not extract text from file: {str(e)}",
                status_code=422
            )
        
        if not extracted_text or len(extracted_text.strip()) < 50:
            raise create_validation_error(
                "INSUFFICIENT_CONTENT",
                "Could not extract sufficient text content from file",
                status_code=422
            )
        
        # Create resume record
        resume = Resume(
            filename=validation_result.metadata['filename'],
            file_size=validation_result.metadata['file_size'],
            mime_type=validation_result.metadata.get('content_type', 'unknown'),
            extracted_text=extracted_text,
            status="completed"
        )
        
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        logger.info(f"Resume uploaded successfully: ID {resume.id}, filename {resume.filename}")
        
        return ResumeUploadResponse(
            id=resume.id,
            filename=resume.filename,
            file_size=resume.file_size,
            status=resume.status,
            upload_timestamp=resume.upload_timestamp
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )


@router.get("/resumes/{resume_id}")
async def get_resume(resume_id: int, db: Session = Depends(get_db)):
    """
    Get resume information by ID.
    
    Args:
        resume_id: Resume ID
        db: Database session
        
    Returns:
        Resume information dictionary
        
    Raises:
        HTTPException: If resume not found
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Get analysis count
    analysis_count = db.query(AnalysisResult).filter(AnalysisResult.resume_id == resume_id).count()
    
    return {
        "id": resume.id,
        "filename": resume.filename,
        "file_size": resume.file_size,
        "status": resume.status,
        "upload_timestamp": resume.upload_timestamp,
        "text_length": len(resume.extracted_text),
        "analysis_count": analysis_count
    }


# Analysis endpoints
@router.post("/analyze", response_model=AnalysisResponse)
async def create_analysis(
    request: Request,
    analysis_request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Create a new resume analysis.
    
    Args:
        request: HTTP request for rate limiting
        analysis_request: Analysis request data
        background_tasks: Background task manager
        db: Database session
        
    Returns:
        AnalysisResponse with analysis details
        
    Raises:
        HTTPException: If validation fails or resume not found
    """
    try:
        # Check rate limits
        check_rate_limit(request, 'analysis')
        
        # Validate job description
        job_validation = validate_job_description(analysis_request.job_description)
        validate_and_raise(job_validation, "job_description")
        
        # Get resume
        resume = db.query(Resume).filter(Resume.id == analysis_request.resume_id).first()
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        
        # Create analysis record
        analysis = AnalysisResult(
            resume_id=resume.id,
            job_description=job_validation.metadata['sanitized_content'],
            analysis_data={},  # Will be populated by background task
            processing_time_ms=None
        )
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        # Start background analysis
        background_tasks.add_task(
            perform_analysis_task,
            analysis.id,
            resume.extracted_text,
            analysis.job_description
        )
        
        logger.info(f"Analysis started: ID {analysis.id} for resume {resume.id}")
        
        return AnalysisResponse(
            id=analysis.id,
            resume_id=resume.id,
            job_description=analysis.job_description,
            analysis_data={"status": "processing"},
            compatibility_score=None,
            processing_time_ms=None,
            created_at=analysis.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis creation failed: {str(e)}"
        )


@router.get("/analysis/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: int, db: Session = Depends(get_db)):
    """
    Get analysis results by ID.
    
    Args:
        analysis_id: Analysis ID
        db: Database session
        
    Returns:
        AnalysisResponse with results
        
    Raises:
        HTTPException: If analysis not found
    """
    analysis = db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    return AnalysisResponse(
        id=analysis.id,
        resume_id=analysis.resume_id,
        job_description=analysis.job_description,
        analysis_data=analysis.analysis_data,
        compatibility_score=analysis.compatibility_score,
        processing_time_ms=analysis.processing_time_ms,
        created_at=analysis.created_at
    )


# Health check endpoint
@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    """
    Health check endpoint for monitoring.
    
    Args:
        request: HTTP request for rate limiting
        
    Returns:
        HealthResponse with system status
    """
    try:
        # Check rate limits (more lenient for health checks)
        check_rate_limit(request, 'health')
        
        # Test database connection
        from database import check_database_health
        db_result = check_database_health()
        db_healthy = db_result.get('status') == 'connected'
        
        # Test AI service
        ai_result = await test_ai_service()
        ai_healthy = ai_result.get('success', False)
        
        # Determine overall status
        if db_healthy and ai_healthy:
            status_text = "healthy"
        elif db_healthy or ai_healthy:
            status_text = "degraded"
        else:
            status_text = "unhealthy"
        
        return HealthResponse(
            status=status_text,
            database="connected" if db_healthy else "disconnected",
            atlascloud="available" if ai_healthy else "unavailable",
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            database="error",
            atlascloud="error"
        )


# Statistics endpoint
@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """
    Get application statistics.
    
    Args:
        db: Database session
        
    Returns:
        Statistics dictionary
    """
    try:
        # Get basic counts
        total_resumes = db.query(Resume).count()
        total_analyses = db.query(AnalysisResult).count()
        
        # Get recent activity (last 24 hours)
        from datetime import timedelta
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        recent_resumes = db.query(Resume).filter(Resume.upload_timestamp >= yesterday).count()
        recent_analyses = db.query(AnalysisResult).filter(AnalysisResult.created_at >= yesterday).count()
        
        # Get average processing time
        avg_processing_time = db.query(AnalysisResult.processing_time_ms).filter(
            AnalysisResult.processing_time_ms.isnot(None)
        ).all()
        
        avg_time = 0
        if avg_processing_time:
            times = [t[0] for t in avg_processing_time if t[0] is not None]
            avg_time = sum(times) / len(times) if times else 0
        
        return {
            "total_resumes": total_resumes,
            "total_analyses": total_analyses,
            "recent_resumes_24h": recent_resumes,
            "recent_analyses_24h": recent_analyses,
            "average_processing_time_ms": round(avg_time, 2),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stats retrieval failed: {str(e)}"
        )


# Background task for analysis
async def perform_analysis_task(analysis_id: int, resume_text: str, job_description: str):
    """
    Background task to perform resume analysis.
    
    Args:
        analysis_id: Analysis record ID
        resume_text: Resume text content
        job_description: Job description text
    """
    try:
        logger.info(f"Starting background analysis for ID {analysis_id}")
        start_time = datetime.utcnow()
        
        # Perform AI analysis
        result = await analyze_resume(resume_text, job_description)
        
        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Update database with results
        from database import SessionLocal
        db = SessionLocal()
        
        try:
            analysis = db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()
            if analysis:
                analysis.analysis_data = result.get('analysis_data', {})
                analysis.processing_time_ms = int(processing_time)
                
                # Extract compatibility score if available
                if result.get('success') and 'analysis_data' in result:
                    analysis_data = result['analysis_data']
                    if isinstance(analysis_data, dict):
                        analysis.compatibility_score = analysis_data.get('compatibility_score') or analysis_data.get('overall_score')
                
                db.commit()
                logger.info(f"Analysis completed for ID {analysis_id} in {processing_time:.1f}ms")
            else:
                logger.error(f"Analysis record not found: {analysis_id}")
                
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Background analysis failed for ID {analysis_id}: {e}")
        
        # Update database with error
        from database import SessionLocal
        db = SessionLocal()
        
        try:
            analysis = db.query(AnalysisResult).filter(AnalysisResult.id == analysis_id).first()
            if analysis:
                analysis.analysis_data = {
                    "error": str(e),
                    "status": "failed"
                }
                db.commit()
        except Exception as db_error:
            logger.error(f"Failed to update analysis error: {db_error}")
        finally:
            db.close()