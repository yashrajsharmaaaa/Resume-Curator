

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Resume, AnalysisResult, AnalysisRequest, AnalysisResponse
from simple_ai_service import analyze_resume_simple

router = APIRouter()

@router.post("/analyze", response_model=AnalysisResponse)
async def create_analysis_simple(
    request: AnalysisRequest,
    db: Session = Depends(get_db)
):
    try:
        resume = db.query(Resume).filter(Resume.id == request.resume_id).first()
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # Direct AI processing (no background tasks)
        ai_result = await analyze_resume_simple(
            resume.extracted_text, 
            request.job_description
        )
        
        if not ai_result.get('success'):
            raise HTTPException(
                status_code=500, 
                detail=f"AI analysis failed: {ai_result.get('error', 'Unknown error')}"
            )
        
        analysis_data = ai_result.get('analysis', {})
        score = analysis_data.get('compatibility_score') or analysis_data.get('overall_score')
        
        analysis = AnalysisResult(
            resume_id=request.resume_id,
            job_description=request.job_description,
            analysis_data=analysis_data,
            compatibility_score=score
        )
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        return AnalysisResponse(
            id=analysis.id,
            resume_id=analysis.resume_id,
            job_description=analysis.job_description,
            analysis_data=analysis.analysis_data,
            compatibility_score=analysis.compatibility_score,
            processing_time_ms=None,
            created_at=analysis.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.get("/health-simple")
async def simple_health_check():
    from simple_ai_service import get_ai_service
    
    try:
        service = await get_ai_service()
        ai_test = await service.test_connection()
        
        return {
            "status": "healthy" if ai_test.get('success') else "unhealthy",
            "ai_service": "available" if ai_test.get('success') else "unavailable"
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}