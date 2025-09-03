

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request, status
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

logger = logging.getLogger(__name__)
router = APIRouter()
@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    try:
        check_rate_limit(request, 'upload')
        
        validation_result = validate_file_upload(file)
        validate_and_raise(validation_result, "file")
        
        try:
            extracted_text = await extract_text_from_file(file)
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            raise create_validation_error(
                "TEXT_EXTRACTION_ERROR",
                f"Could not extract text from file: {str(e)}",
                status_code=422
            )
        
        # Ensure minimum content quality for analysis
        if not extracted_text or len(extracted_text.strip()) < 50:
            raise create_validation_error(
                "INSUFFICIENT_CONTENT",
                "Could not extract sufficient text content from file",
                status_code=422
            )
        
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


@router.get("/resumes")
async def list_resumes(db: Session = Depends(get_db)):
    try:
        resumes = db.query(Resume).order_by(Resume.upload_timestamp.desc()).all()
        
        result = []
        for resume in resumes:
            analysis_count = db.query(AnalysisResult).filter(
                AnalysisResult.resume_id == resume.id
            ).count()
            
            result.append({
                "id": resume.id,
                "filename": resume.filename,
                "file_size": resume.file_size,
                "status": resume.status,
                "upload_timestamp": resume.upload_timestamp,
                "analysis_count": analysis_count
            })
        
        return {"resumes": result, "total": len(result)}
        
    except Exception as e:
        logger.error(f"Resume list retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resume list retrieval failed: {str(e)}"
        )


@router.get("/resumes/{resume_id}")
async def get_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
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


@router.post("/analyze", response_model=AnalysisResponse)
async def create_analysis(
    request: Request,
    analysis_request: AnalysisRequest,
    db: Session = Depends(get_db)
):
    try:
        check_rate_limit(request, 'analysis')
        
        job_validation = validate_job_description(analysis_request.job_description)
        validate_and_raise(job_validation, "job_description")
        
        resume = db.query(Resume).filter(Resume.id == analysis_request.resume_id).first()
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        
        # Process analysis directly (no background tasks)
        result = await analyze_resume(
            resume.extracted_text, 
            job_validation.metadata['sanitized_content']
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI analysis failed: {result.get('error', 'Unknown error')}"
            )
        
        analysis_data = result.get('analysis_data', {})
        score = analysis_data.get('compatibility_score') or analysis_data.get('overall_score')
        
        analysis = AnalysisResult(
            resume_id=resume.id,
            job_description=job_validation.metadata['sanitized_content'],
            analysis_data=analysis_data,
            compatibility_score=score
        )
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        logger.info(f"Analysis completed: ID {analysis.id} for resume {resume.id}")
        
        return AnalysisResponse(
            id=analysis.id,
            resume_id=resume.id,
            job_description=analysis.job_description,
            analysis_data=analysis.analysis_data,
            compatibility_score=analysis.compatibility_score,
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


@router.get("/health", response_model=HealthResponse)
async def health_check():
    try:
        # Test external AI service dependency
        ai_result = await test_ai_service()
        ai_healthy = ai_result.get('success', False)
        
        return HealthResponse(
            status="healthy" if ai_healthy else "unhealthy",
            database="connected",
            atlascloud="available" if ai_healthy else "unavailable",
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            database="error",
            atlascloud="error",
            timestamp=datetime.utcnow()
        )


@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    try:
        total_resumes = db.query(Resume).count()
        total_analyses = db.query(AnalysisResult).count()
        
        from datetime import timedelta
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        recent_resumes = db.query(Resume).filter(Resume.upload_timestamp >= yesterday).count()
        recent_analyses = db.query(AnalysisResult).filter(AnalysisResult.created_at >= yesterday).count()
        
        return {
            "total_resumes": total_resumes,
            "total_analyses": total_analyses,
            "recent_resumes_24h": recent_resumes,
            "recent_analyses_24h": recent_analyses,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stats retrieval failed: {str(e)}"
        )


