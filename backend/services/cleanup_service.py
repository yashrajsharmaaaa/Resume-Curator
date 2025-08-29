"""
Data cleanup service for Resume Curator application.

This service handles automatic and manual cleanup of expired data
as required by Requirements 8.2, 8.3 for data protection and privacy.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlmodel import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from models import ResumeSession, AnalysisResult

# Configure logging
logger = logging.getLogger(__name__)


class CleanupService:
    """
    Service for managing data cleanup operations.
    
    Provides automatic and manual cleanup of expired resume sessions
    and analysis results to ensure data privacy and storage efficiency.
    """
    
    def __init__(self):
        self.is_running = False
        self.cleanup_task: Optional[asyncio.Task] = None
    
    async def cleanup_expired_sessions(self, session: AsyncSession) -> Dict[str, int]:
        """
        Clean up expired resume sessions and their associated data.
        
        Args:
            session: Database session
            
        Returns:
            Dictionary with cleanup statistics
        """
        try:
            current_time = datetime.utcnow()
            
            # Find expired sessions
            expired_sessions_query = select(ResumeSession).where(
                ResumeSession.expires_at <= current_time
            )
            result = await session.execute(expired_sessions_query)
            expired_sessions = result.scalars().all()
            
            if not expired_sessions:
                logger.info("No expired sessions found")
                return {
                    "expired_sessions": 0,
                    "deleted_analyses": 0,
                    "total_cleaned": 0
                }
            
            expired_session_ids = [s.session_id for s in expired_sessions]
            logger.info(f"Found {len(expired_sessions)} expired sessions")
            
            # Delete associated analysis results first (foreign key constraint)
            analysis_delete_query = delete(AnalysisResult).where(
                AnalysisResult.session_id.in_(expired_session_ids)
            )
            analysis_result = await session.execute(analysis_delete_query)
            deleted_analyses = analysis_result.rowcount
            
            # Delete expired sessions
            session_delete_query = delete(ResumeSession).where(
                ResumeSession.session_id.in_(expired_session_ids)
            )
            session_result = await session.execute(session_delete_query)
            deleted_sessions = session_result.rowcount
            
            await session.commit()
            
            cleanup_stats = {
                "expired_sessions": deleted_sessions,
                "deleted_analyses": deleted_analyses,
                "total_cleaned": deleted_sessions + deleted_analyses
            }
            
            logger.info(f"Cleanup completed: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error during cleanup: {e}")
            raise
    
    async def cleanup_sessions_older_than(
        self, 
        session: AsyncSession, 
        hours: int = 24
    ) -> Dict[str, int]:
        """
        Clean up sessions older than specified hours.
        
        Args:
            session: Database session
            hours: Number of hours to look back
            
        Returns:
            Dictionary with cleanup statistics
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Find old sessions
            old_sessions_query = select(ResumeSession).where(
                ResumeSession.created_at <= cutoff_time
            )
            result = await session.execute(old_sessions_query)
            old_sessions = result.scalars().all()
            
            if not old_sessions:
                logger.info(f"No sessions older than {hours} hours found")
                return {
                    "old_sessions": 0,
                    "deleted_analyses": 0,
                    "total_cleaned": 0
                }
            
            old_session_ids = [s.session_id for s in old_sessions]
            logger.info(f"Found {len(old_sessions)} sessions older than {hours} hours")
            
            # Delete associated analysis results first
            analysis_delete_query = delete(AnalysisResult).where(
                AnalysisResult.session_id.in_(old_session_ids)
            )
            analysis_result = await session.execute(analysis_delete_query)
            deleted_analyses = analysis_result.rowcount
            
            # Delete old sessions
            session_delete_query = delete(ResumeSession).where(
                ResumeSession.session_id.in_(old_session_ids)
            )
            session_result = await session.execute(session_delete_query)
            deleted_sessions = session_result.rowcount
            
            await session.commit()
            
            cleanup_stats = {
                "old_sessions": deleted_sessions,
                "deleted_analyses": deleted_analyses,
                "total_cleaned": deleted_sessions + deleted_analyses
            }
            
            logger.info(f"Age-based cleanup completed: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error during age-based cleanup: {e}")
            raise
    
    async def get_cleanup_statistics(self, session: AsyncSession) -> Dict[str, int]:
        """
        Get statistics about data that needs cleanup.
        
        Args:
            session: Database session
            
        Returns:
            Dictionary with cleanup statistics
        """
        try:
            current_time = datetime.utcnow()
            
            # Count total sessions
            total_sessions_query = select(ResumeSession)
            total_result = await session.execute(total_sessions_query)
            total_sessions = len(total_result.scalars().all())
            
            # Count expired sessions
            expired_query = select(ResumeSession).where(
                ResumeSession.expires_at <= current_time
            )
            expired_result = await session.execute(expired_query)
            expired_sessions = len(expired_result.scalars().all())
            
            # Count total analyses
            total_analyses_query = select(AnalysisResult)
            analyses_result = await session.execute(total_analyses_query)
            total_analyses = len(analyses_result.scalars().all())
            
            # Count sessions older than 24 hours
            cutoff_time = current_time - timedelta(hours=24)
            old_query = select(ResumeSession).where(
                ResumeSession.created_at <= cutoff_time
            )
            old_result = await session.execute(old_query)
            old_sessions = len(old_result.scalars().all())
            
            return {
                "total_sessions": total_sessions,
                "expired_sessions": expired_sessions,
                "total_analyses": total_analyses,
                "sessions_older_than_24h": old_sessions,
                "active_sessions": total_sessions - expired_sessions
            }
            
        except Exception as e:
            logger.error(f"Error getting cleanup statistics: {e}")
            raise
    
    async def manual_cleanup(self) -> Dict[str, int]:
        """
        Perform manual cleanup of expired data.
        
        Returns:
            Dictionary with cleanup results
        """
        try:
            async with get_async_session() as session:
                return await self.cleanup_expired_sessions(session)
        except Exception as e:
            logger.error(f"Manual cleanup failed: {e}")
            raise
    
    async def scheduled_cleanup_task(self, interval_hours: int = 1):
        """
        Background task for scheduled cleanup operations.
        
        Args:
            interval_hours: Hours between cleanup runs
        """
        logger.info(f"Starting scheduled cleanup task (interval: {interval_hours}h)")
        
        while self.is_running:
            try:
                async with get_async_session() as session:
                    stats = await self.cleanup_expired_sessions(session)
                    if stats["total_cleaned"] > 0:
                        logger.info(f"Scheduled cleanup completed: {stats}")
                
                # Wait for next cleanup cycle
                await asyncio.sleep(interval_hours * 3600)  # Convert hours to seconds
                
            except asyncio.CancelledError:
                logger.info("Scheduled cleanup task cancelled")
                break
            except Exception as e:
                logger.error(f"Error in scheduled cleanup task: {e}")
                # Wait before retrying
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    async def start_scheduled_cleanup(self, interval_hours: int = 1):
        """
        Start the scheduled cleanup background task.
        
        Args:
            interval_hours: Hours between cleanup runs
        """
        if self.is_running:
            logger.warning("Scheduled cleanup is already running")
            return
        
        self.is_running = True
        self.cleanup_task = asyncio.create_task(
            self.scheduled_cleanup_task(interval_hours)
        )
        logger.info("Scheduled cleanup started")
    
    async def stop_scheduled_cleanup(self):
        """Stop the scheduled cleanup background task."""
        if not self.is_running:
            logger.warning("Scheduled cleanup is not running")
            return
        
        self.is_running = False
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
            self.cleanup_task = None
        
        logger.info("Scheduled cleanup stopped")
    
    async def force_cleanup_all(self, confirm: bool = False) -> Dict[str, int]:
        """
        Force cleanup of all data (use with extreme caution).
        
        Args:
            confirm: Must be True to actually perform the cleanup
            
        Returns:
            Dictionary with cleanup results
        """
        if not confirm:
            raise ValueError("Force cleanup requires explicit confirmation")
        
        try:
            async with get_async_session() as session:
                # Delete all analysis results
                analysis_delete = delete(AnalysisResult)
                analysis_result = await session.execute(analysis_delete)
                deleted_analyses = analysis_result.rowcount
                
                # Delete all sessions
                session_delete = delete(ResumeSession)
                session_result = await session.execute(session_delete)
                deleted_sessions = session_result.rowcount
                
                await session.commit()
                
                cleanup_stats = {
                    "deleted_sessions": deleted_sessions,
                    "deleted_analyses": deleted_analyses,
                    "total_cleaned": deleted_sessions + deleted_analyses
                }
                
                logger.warning(f"Force cleanup completed: {cleanup_stats}")
                return cleanup_stats
                
        except Exception as e:
            logger.error(f"Force cleanup failed: {e}")
            raise


# Global cleanup service instance
cleanup_service = CleanupService()