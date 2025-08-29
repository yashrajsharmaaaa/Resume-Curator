"""
Database models for Resume Curator application.

This module contains simplified SQLAlchemy models for PostgreSQL:
- Resume: Stores uploaded resume metadata
- AnalysisResult: Stores AI analysis results from AtlasCloud

Models are designed for SDE1 portfolio demonstration with clean architecture
and proper relationships.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
import uuid

Base = declarative_base()


class Resume(Base):
    """
    Model for storing resume metadata and file information.
    
    Stores basic information about uploaded resumes with automatic
    timestamp tracking and unique identification.
    """
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    extracted_text = Column(Text, nullable=False)
    upload_timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to analysis results
    analysis_results = relationship("AnalysisResult", back_populates="resume")


class AnalysisResult(Base):
    """
    Model for storing AI analysis results from AtlasCloud.
    
    Stores the complete analysis output including compatibility scores,
    recommendations, and processing metadata.
    """
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    job_description = Column(Text, nullable=False)
    analysis_data = Column(JSON, nullable=False)  # Complete AtlasCloud response
    compatibility_score = Column(Float, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to resume
    resume = relationship("Resume", back_populates="analysis_results")


# Pydantic models for API requests and responses

class ResumeUploadRequest(BaseModel):
    """Request model for resume upload (handled by FastAPI's UploadFile)."""
    pass


class ResumeUploadResponse(BaseModel):
    """Response model for successful resume upload."""
    id: int
    filename: str
    file_size: int
    status: str
    upload_timestamp: datetime
    
    class Config:
        from_attributes = True


class AnalysisRequest(BaseModel):
    """Request model for analysis creation."""
    resume_id: int
    job_description: str = Field(..., min_length=10, max_length=10000)


class AnalysisResponse(BaseModel):
    """Response model for analysis results."""
    id: int
    resume_id: int
    job_description: str
    analysis_data: Dict[str, Any]
    compatibility_score: Optional[float]
    processing_time_ms: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ResumeListResponse(BaseModel):
    """Response model for listing resumes."""
    id: int
    filename: str
    status: str
    upload_timestamp: datetime
    analysis_count: int = 0
    
    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: Dict[str, Any] = Field(
        ...,
        example={
            "code": "VALIDATION_ERROR",
            "message": "File size exceeds 10MB limit",
            "details": {
                "field": "file",
                "received_size": 15728640,
                "max_size": 10485760
            }
        }
    )


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    database: str = "connected"
    atlascloud: str = "available"