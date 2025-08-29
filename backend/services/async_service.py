"""
Async Processing Service

High-level service that integrates all async processing components including
task queues, background processing, caching, and performance optimization.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager

from async_processing.task_queue import TaskQueue, TaskManager, TaskPriority
from async_processing.background_processor import BackgroundProcessor
from async_processing.cache_manager import CacheManager
from async_processing.connection_pool import ConnectionPoolManager
from async_processing.memory_optimizer import MemoryOptimizer

logger = logging.getLogger(__name__)

class AsyncProcessingService:
    """High-level async processing service"""
    
    def __init__(self):
        # Core components
        self.task_queue = TaskQueue()
        self.task_manager = TaskManager(self.task_queue)
        self.background_processor = BackgroundProcessor(self.task_queue)
        self.cache_manager = CacheManager()
        self.connection_pool = ConnectionPoolManager()
        self.memory_optimizer = MemoryOptimizer()
        
        # Service state
        self.is_running = False
        self.start_time = None
        
        # Performance monitoring
        self.performance_stats = {
            'requests_processed': 0,
            'cache_hit_rate': 0.0,
            'average_response_time': 0.0,
            'error_rate': 0.0,
            'memory_usage_mb': 0.0
        }
    
    async def initialize(self):
        """Initialize all async processing components"""
        
        logger.info("Initializing async processing service...")
        
        try:
            # Initialize components in order
            await self.connection_pool.initialize()
            await self.cache_manager.initialize()
            
            # Register memory cleanup callbacks
            self.memory_optimizer.register_cleanup_callback(self._cleanup_cache)
            self.memory_optimizer.register_cleanup_callback(self._cleanup_completed_tasks)
            
            logger.info("Async processing service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize async processing service: {e}")
            raise
    
    async def start(self, num_workers: int = 4):
        """Start the async processing service"""
        
        if self.is_running:
            logger.warning("Async processing service is already running")
            return
        
        logger.info(f"Starting async processing service with {num_workers} workers...")
        
        try:
            # Start background processor
            await self.background_processor.start(num_workers)
            
            # Start performance monitoring
            asyncio.create_task(self._performance_monitoring_loop())
            
            self.is_running = True
            self.start_time = datetime.utcnow()
            
            logger.info("Async processing service started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start async processing service: {e}")
            raise
    
    async def stop(self):
        """Stop the async processing service"""
        
        if not self.is_running:
            return
        
        logger.info("Stopping async processing service...")
        
        try:
            # Stop background processor
            await self.background_processor.stop()
            
            # Close connections
            await self.cache_manager.close()
            await self.connection_pool.close()
            await self.memory_optimizer.close()
            
            self.is_running = False
            
            logger.info("Async processing service stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping async processing service: {e}")
    
    async def process_file_async(
        self,
        file_path: str,
        file_type: str,
        session_id: str,
        priority: TaskPriority = TaskPriority.NORMAL
    ) -> str:
        """Process file asynchronously and return task ID"""
        
        # Check cache first
        file_hash = self.cache_manager.create_cache_key(file_path, file_type)
        cached_result = await self.cache_manager.get_file_processing_result(file_hash)
        
        if cached_result:
            logger.info(f"File processing result found in cache: {file_path}")
            return cached_result
        
        # Submit task for background processing
        task_id = await self.task_manager.submit_file_processing_task(
            file_path=file_path,
            file_type=file_type,
            session_id=session_id,
            priority=priority
        )
        
        logger.info(f"File processing task submitted: {task_id}")
        return task_id
    
    async def analyze_resume_async(
        self,
        resume_text: str,
        job_description: str,
        session_id: str,
        analysis_options: Dict[str, Any] = None,
        priority: TaskPriority = TaskPriority.HIGH
    ) -> str:
        """Analyze resume asynchronously and return task ID"""
        
        # Check cache first
        resume_hash = self.cache_manager.create_cache_key(resume_text)
        job_hash = self.cache_manager.create_cache_key(job_description)
        cached_result = await self.cache_manager.get_analysis_result(resume_hash, job_hash)
        
        if cached_result:
            logger.info("Resume analysis result found in cache")
            return cached_result
        
        # Submit task for background processing
        task_id = await self.task_manager.submit_analysis_task(
            resume_text=resume_text,
            job_description=job_description,
            session_id=session_id,
            analysis_options=analysis_options or {},
            priority=priority
        )
        
        logger.info(f"Resume analysis task submitted: {task_id}")
        return task_id
    
    async def batch_analyze_resume_async(
        self,
        resume_text: str,
        job_descriptions: List[str],
        session_id: str,
        priority: TaskPriority = TaskPriority.NORMAL
    ) -> str:
        """Analyze resume against multiple job descriptions asynchronously"""
        
        task_id = await self.task_manager.submit_batch_analysis_task(
            resume_text=resume_text,
            job_descriptions=job_descriptions,
            session_id=session_id,
            priority=priority
        )
        
        logger.info(f"Batch analysis task submitted: {task_id} for {len(job_descriptions)} jobs")
        return task_id
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status and progress"""
        
        task_info = await self.task_queue.get_task_status(task_id)
        
        if not task_info:
            return None
        
        return {
            'task_id': task_info.task_id,
            'task_name': task_info.task_name,
            'status': task_info.status.value,
            'progress': task_info.progress,
            'created_at': task_info.created_at.isoformat(),
            'started_at': task_info.started_at.isoformat() if task_info.started_at else None,
            'completed_at': task_info.completed_at.isoformat() if task_info.completed_at else None,
            'result': task_info.result,
            'error': task_info.error,
            'retry_count': task_info.retry_count,
            'max_retries': task_info.max_retries
        }
    
    async def wait_for_task_completion(
        self,
        task_id: str,
        timeout: int = 300  # 5 minutes
    ) -> Optional[Dict[str, Any]]:
        """Wait for task completion and return result"""
        
        try:
            result = await self.task_manager.get_task_result(task_id, timeout)
            return result
        except TimeoutError:
            logger.warning(f"Task {task_id} timed out after {timeout} seconds")
            return None
        except Exception as e:
            logger.error(f"Error waiting for task {task_id}: {e}")
            return None
    
    async def subscribe_to_task_updates(self, task_id: str):
        """Subscribe to real-time task updates"""
        
        return await self.task_manager.subscribe_to_task_updates(task_id)
    
    async def cancel_task(self, task_id: str):
        """Cancel a pending or running task"""
        
        await self.task_queue.cancel_task(task_id)
        logger.info(f"Task {task_id} cancelled")
    
    async def get_queue_statistics(self) -> Dict[str, Any]:
        """Get comprehensive queue and processing statistics"""
        
        # Get queue stats
        queue_stats = await self.task_queue.get_queue_stats()
        
        # Get processor stats
        processor_stats = self.background_processor.get_stats()
        
        # Get cache stats
        cache_stats = await self.cache_manager.get_cache_stats()
        
        # Get connection pool stats
        pool_stats = await self.connection_pool.get_pool_stats()
        
        # Get memory stats
        memory_stats = self.memory_optimizer.get_memory_stats()
        
        return {
            'service': {
                'running': self.is_running,
                'uptime_seconds': (datetime.utcnow() - self.start_time).total_seconds() if self.start_time else 0,
                **self.performance_stats
            },
            'queue': queue_stats,
            'processor': processor_stats,
            'cache': cache_stats,
            'connections': pool_stats,
            'memory': memory_stats
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        
        health_status = {
            'service': self.is_running,
            'components': {},
            'overall': False
        }
        
        # Check connection pools
        pool_health = await self.connection_pool.health_check()
        health_status['components']['connections'] = pool_health['overall']
        
        # Check cache
        try:
            await self.cache_manager.set('health_check', 'ok', ttl=10)
            cache_result = await self.cache_manager.get('health_check')
            health_status['components']['cache'] = cache_result == 'ok'
        except Exception:
            health_status['components']['cache'] = False
        
        # Check memory usage
        memory_stats = self.memory_optimizer.get_memory_stats()
        memory_healthy = memory_stats['current_memory_mb'] < self.memory_optimizer.memory_thresholds['critical']
        health_status['components']['memory'] = memory_healthy
        
        # Check background processor
        health_status['components']['processor'] = self.background_processor.running
        
        # Overall health
        health_status['overall'] = all(health_status['components'].values())
        
        return health_status
    
    async def optimize_performance(self):
        """Perform comprehensive performance optimization"""
        
        logger.info("Starting performance optimization...")
        
        # Optimize memory
        memory_freed = await self.memory_optimizer.optimize()
        
        # Clean up cache
        await self.cache_manager.cleanup_expired()
        
        # Clean up completed tasks
        cleaned_tasks = await self.task_queue.cleanup_completed_tasks()
        
        # Optimize connection pools
        pool_optimizations = await self.connection_pool.optimize_pools()
        
        optimization_result = {
            'memory_freed_mb': memory_freed,
            'tasks_cleaned': cleaned_tasks,
            'pool_optimizations': pool_optimizations,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Performance optimization complete: {optimization_result}")
        return optimization_result
    
    async def _performance_monitoring_loop(self):
        """Background performance monitoring"""
        
        while self.is_running:
            try:
                # Update performance statistics
                await self._update_performance_stats()
                
                # Check for performance issues
                await self._check_performance_issues()
                
                # Sleep for monitoring interval
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(300)  # Back off on error
    
    async def _update_performance_stats(self):
        """Update performance statistics"""
        
        try:
            # Get cache stats
            cache_stats = await self.cache_manager.get_cache_stats()
            self.performance_stats['cache_hit_rate'] = cache_stats.get('hit_rate', 0.0)
            
            # Get memory stats
            memory_stats = self.memory_optimizer.get_memory_stats()
            self.performance_stats['memory_usage_mb'] = memory_stats.get('current_memory_mb', 0.0)
            
            # Get processor stats
            processor_stats = self.background_processor.get_stats()
            self.performance_stats['average_response_time'] = processor_stats.get('average_processing_time', 0.0)
            
            # Calculate error rate
            total_tasks = processor_stats.get('tasks_processed', 0) + processor_stats.get('tasks_failed', 0)
            if total_tasks > 0:
                self.performance_stats['error_rate'] = processor_stats.get('tasks_failed', 0) / total_tasks
            
        except Exception as e:
            logger.error(f"Failed to update performance stats: {e}")
    
    async def _check_performance_issues(self):
        """Check for performance issues and take corrective action"""
        
        # Check memory usage
        if self.performance_stats['memory_usage_mb'] > self.memory_optimizer.memory_thresholds['warning']:
            logger.warning("High memory usage detected, triggering optimization")
            await self.memory_optimizer.optimize()
        
        # Check cache hit rate
        if self.performance_stats['cache_hit_rate'] < 0.5:
            logger.warning("Low cache hit rate detected")
        
        # Check error rate
        if self.performance_stats['error_rate'] > 0.1:
            logger.warning(f"High error rate detected: {self.performance_stats['error_rate']:.2%}")
    
    async def _cleanup_cache(self):
        """Cleanup callback for memory optimization"""
        
        await self.cache_manager.cleanup_expired()
        logger.debug("Cache cleanup completed")
    
    async def _cleanup_completed_tasks(self):
        """Cleanup callback for completed tasks"""
        
        cleaned = await self.task_queue.cleanup_completed_tasks(timedelta(hours=1))
        if cleaned > 0:
            logger.debug(f"Cleaned up {cleaned} completed tasks")
    
    @asynccontextmanager
    async def get_db_session(self):
        """Get database session from connection pool"""
        
        async with self.connection_pool.get_db_session() as session:
            yield session
    
    @asynccontextmanager
    async def get_http_session(self):
        """Get HTTP session from connection pool"""
        
        async with self.connection_pool.get_http_session() as session:
            yield session
    
    @asynccontextmanager
    async def get_redis_client(self):
        """Get Redis client from connection pool"""
        
        async with self.connection_pool.get_redis_client() as client:
            yield client

# Global async processing service instance
async_service = AsyncProcessingService()