"""
Secure session management for API authentication and state tracking.

This module provides secure session management with expiration, validation,
and cleanup capabilities for maintaining user state across API requests.
"""

import os
import json
import time
import secrets
import hashlib
import logging
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import asyncio

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class Session:
    """Session data structure."""
    session_id: str
    created_at: datetime
    expires_at: datetime
    last_accessed: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    data: Dict[str, Any]
    access_count: int
    is_active: bool


class SessionManager:
    """
    Secure session manager for API authentication and state tracking.
    
    Provides secure session creation, validation, and cleanup with
    configurable expiration and security features.
    """
    
    def __init__(
        self,
        session_dir: Optional[str] = None,
        default_ttl_hours: int = 24,
        max_sessions_per_ip: int = 10,
        cleanup_interval_minutes: int = 60,
        enable_ip_validation: bool = True,
        enable_user_agent_validation: bool = False
    ):
        """
        Initialize session manager.
        
        Args:
            session_dir: Directory for session storage
            default_ttl_hours: Default session TTL in hours
            max_sessions_per_ip: Maximum sessions per IP address
            cleanup_interval_minutes: Cleanup interval in minutes
            enable_ip_validation: Whether to validate IP addresses
            enable_user_agent_validation: Whether to validate user agents
        """
        # Set up session directory
        if session_dir:
            self.session_dir = Path(session_dir)
        else:
            self.session_dir = Path.cwd() / "sessions"
        
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration
        self.default_ttl_hours = default_ttl_hours
        self.max_sessions_per_ip = max_sessions_per_ip
        self.cleanup_interval_minutes = cleanup_interval_minutes
        self.enable_ip_validation = enable_ip_validation
        self.enable_user_agent_validation = enable_user_agent_validation
        
        # Session storage
        self.sessions: Dict[str, Session] = {}
        self.ip_session_count: Dict[str, int] = {}
        
        # Session file
        self.session_file = self.session_dir / "sessions.json"
        
        # Load existing sessions
        self._load_sessions()
        
        # Cleanup task
        self.cleanup_task: Optional[asyncio.Task] = None
        
        logger.info(f"SessionManager initialized (TTL: {default_ttl_hours}h, max per IP: {max_sessions_per_ip})")
    
    def _load_sessions(self) -> None:
        """Load sessions from disk."""
        try:
            if self.session_file.exists():
                with open(self.session_file, 'r') as f:
                    session_data = json.load(f)
                
                # Convert back to Session objects
                for session_id, data in session_data.items():
                    data['created_at'] = datetime.fromisoformat(data['created_at'])
                    data['expires_at'] = datetime.fromisoformat(data['expires_at'])
                    data['last_accessed'] = datetime.fromisoformat(data['last_accessed'])
                    
                    session = Session(**data)
                    
                    # Only load non-expired sessions
                    if datetime.utcnow() <= session.expires_at:
                        self.sessions[session_id] = session
                        
                        # Update IP count
                        if session.ip_address:
                            self.ip_session_count[session.ip_address] = \
                                self.ip_session_count.get(session.ip_address, 0) + 1
                
                logger.info(f"Loaded {len(self.sessions)} active sessions")
        
        except Exception as e:
            logger.error(f"Failed to load sessions: {e}")
            self.sessions = {}
            self.ip_session_count = {}
    
    def _save_sessions(self) -> None:
        """Save sessions to disk."""
        try:
            # Convert Session objects to serializable format
            session_data = {}
            for session_id, session in self.sessions.items():
                data = asdict(session)
                data['created_at'] = session.created_at.isoformat()
                data['expires_at'] = session.expires_at.isoformat()
                data['last_accessed'] = session.last_accessed.isoformat()
                session_data[session_id] = data
            
            # Write to temporary file first, then rename for atomicity
            temp_file = self.session_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            
            temp_file.replace(self.session_file)
            
        except Exception as e:
            logger.error(f"Failed to save sessions: {e}")
    
    def create_session(
        self,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        ttl_hours: Optional[int] = None,
        initial_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new session.
        
        Args:
            ip_address: Client IP address
            user_agent: Client user agent
            ttl_hours: Session TTL in hours (uses default if None)
            initial_data: Initial session data
            
        Returns:
            Session ID
            
        Raises:
            ValueError: If session creation fails
        """
        # Check IP session limit
        if ip_address and self.ip_session_count.get(ip_address, 0) >= self.max_sessions_per_ip:
            raise ValueError(f"Maximum sessions per IP exceeded: {self.max_sessions_per_ip}")
        
        # Generate secure session ID
        session_id = self._generate_session_id()
        
        # Calculate expiration
        ttl = ttl_hours or self.default_ttl_hours
        expires_at = datetime.utcnow() + timedelta(hours=ttl)
        
        # Create session
        session = Session(
            session_id=session_id,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            last_accessed=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent,
            data=initial_data or {},
            access_count=0,
            is_active=True
        )
        
        # Store session
        self.sessions[session_id] = session
        
        # Update IP count
        if ip_address:
            self.ip_session_count[ip_address] = self.ip_session_count.get(ip_address, 0) + 1
        
        # Save to disk
        self._save_sessions()
        
        logger.info(f"Created session {session_id} (expires: {expires_at})")
        return session_id
    
    def get_session(
        self,
        session_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        update_access: bool = True
    ) -> Optional[Session]:
        """
        Get session by ID with validation.
        
        Args:
            session_id: Session ID
            ip_address: Client IP address for validation
            user_agent: Client user agent for validation
            update_access: Whether to update last access time
            
        Returns:
            Session object or None if not found/invalid
        """
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        # Check if session is expired
        if datetime.utcnow() > session.expires_at:
            logger.info(f"Session {session_id} expired, removing")
            self.delete_session(session_id)
            return None
        
        # Check if session is active
        if not session.is_active:
            return None
        
        # Validate IP address if enabled
        if self.enable_ip_validation and ip_address:
            if session.ip_address and session.ip_address != ip_address:
                logger.warning(f"IP mismatch for session {session_id}: {session.ip_address} vs {ip_address}")
                return None
        
        # Validate user agent if enabled
        if self.enable_user_agent_validation and user_agent:
            if session.user_agent and session.user_agent != user_agent:
                logger.warning(f"User agent mismatch for session {session_id}")
                return None
        
        # Update access information
        if update_access:
            session.last_accessed = datetime.utcnow()
            session.access_count += 1
            self._save_sessions()
        
        return session
    
    def update_session_data(self, session_id: str, data: Dict[str, Any]) -> bool:
        """
        Update session data.
        
        Args:
            session_id: Session ID
            data: Data to update
            
        Returns:
            True if updated successfully, False otherwise
        """
        session = self.get_session(session_id, update_access=False)
        if not session:
            return False
        
        session.data.update(data)
        session.last_accessed = datetime.utcnow()
        self._save_sessions()
        
        return True
    
    def extend_session(self, session_id: str, additional_hours: int = 0) -> bool:
        """
        Extend session expiration.
        
        Args:
            session_id: Session ID
            additional_hours: Hours to add (uses default TTL if None)
            
        Returns:
            True if extended successfully, False otherwise
        """
        session = self.get_session(session_id, update_access=False)
        if not session:
            return False
        hours = additional_hours if additional_hours else self.default_ttl_hours
        session.expires_at = datetime.utcnow() + timedelta(hours=hours)
        session.last_accessed = datetime.utcnow()
        self._save_sessions()
        logger.info(f"Extended session {session_id} by {hours} hours")
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if deleted successfully, False otherwise
        """
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        
        # Update IP count
        if session.ip_address:
            self.ip_session_count[session.ip_address] = \
                max(0, self.ip_session_count.get(session.ip_address, 0) - 1)
            
            if self.ip_session_count[session.ip_address] == 0:
                del self.ip_session_count[session.ip_address]
        
        # Remove session
        del self.sessions[session_id]
        self._save_sessions()
        
        logger.info(f"Deleted session {session_id}")
        return True
    
    def deactivate_session(self, session_id: str) -> bool:
        """
        Deactivate session without deleting.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if deactivated successfully, False otherwise
        """
        session = self.get_session(session_id, update_access=False)
        if not session:
            return False
        
        session.is_active = False
        self._save_sessions()
        
        logger.info(f"Deactivated session {session_id}")
        return True
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        current_time = datetime.utcnow()
        expired_sessions = []
        
        # Find expired sessions
        for session_id, session in self.sessions.items():
            if current_time > session.expires_at:
                expired_sessions.append(session_id)
        
        # Delete expired sessions
        for session_id in expired_sessions:
            self.delete_session(session_id)
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        
        return len(expired_sessions)
    
    def get_sessions_by_ip(self, ip_address: str) -> List[Session]:
        """Get all sessions for an IP address."""
        return [
            session for session in self.sessions.values()
            if session.ip_address == ip_address and session.is_active
        ]
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        current_time = datetime.utcnow()
        active_sessions = 0
        expired_sessions = 0
        total_accesses = 0
        
        for session in self.sessions.values():
            if current_time <= session.expires_at and session.is_active:
                active_sessions += 1
            else:
                expired_sessions += 1
            
            total_accesses += session.access_count
        
        return {
            'total_sessions': len(self.sessions),
            'active_sessions': active_sessions,
            'expired_sessions': expired_sessions,
            'unique_ips': len(self.ip_session_count),
            'total_accesses': total_accesses,
            'avg_accesses_per_session': total_accesses / len(self.sessions) if self.sessions else 0,
            'default_ttl_hours': self.default_ttl_hours,
            'max_sessions_per_ip': self.max_sessions_per_ip
        }
    
    def _generate_session_id(self) -> str:
        """Generate secure session ID."""
        # Generate random bytes
        random_bytes = secrets.token_bytes(32)
        
        # Add timestamp for uniqueness
        timestamp = str(int(time.time())).encode()
        
        # Create hash
        session_hash = hashlib.sha256(random_bytes + timestamp).hexdigest()
        
        return session_hash[:32]  # Use first 32 characters
    
    async def start_cleanup_task(self) -> None:
        """Start background cleanup task."""
        if self.cleanup_task and not self.cleanup_task.done():
            logger.warning("Cleanup task already running")
            return
        
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info(f"Started session cleanup task ({self.cleanup_interval_minutes}min interval)")
    
    async def stop_cleanup_task(self) -> None:
        """Stop background cleanup task."""
        if self.cleanup_task and not self.cleanup_task.done():
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
            logger.info("Stopped session cleanup task")
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval_minutes * 60)
                self.cleanup_expired_sessions()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in session cleanup loop: {e}")
    
    def __del__(self):
        """Cleanup on destruction."""
        try:
            if hasattr(self, 'cleanup_task') and self.cleanup_task and not self.cleanup_task.done():
                self.cleanup_task.cancel()
        except Exception:
            pass