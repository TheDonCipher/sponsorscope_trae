import uuid
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from services.api.models.report import ReportResponse
from shared.schemas.domain import ScrapeStatus, Platform

class JobPhase(str, Enum):
    """Processing phases for async job execution."""
    PENDING = "Pending"
    SCRAPING = "Scraping"
    ANALYSIS = "Analysis"
    FINALIZING = "Finalizing"
    COMPLETED = "Completed"
    FAILED = "Failed"

@dataclass
class JobState:
    """Represents the state of an async analysis job."""
    job_id: str
    handle: str
    platform: Platform
    status: ScrapeStatus
    phase: JobPhase
    percent: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    report_data: Optional[ReportResponse] = None
    retry_count: int = 0
    last_retry_at: Optional[datetime] = None

class JobRegistry:
    """
    In-memory job registry with TTL-based cleanup for async analysis jobs.
    Provides idempotent job creation and thread-safe state management.
    """
    
    def __init__(self, ttl_hours: int = 24, cleanup_interval_minutes: int = 5):
        self._jobs: Dict[str, JobState] = {}
        self._handle_index: Dict[str, str] = {}  # handle:platform -> job_id mapping
        self._ttl = timedelta(hours=ttl_hours)
        self._cleanup_interval = timedelta(minutes=cleanup_interval_minutes)
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def start_cleanup_task(self):
        """Start the background cleanup task."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
    
    async def stop_cleanup_task(self):
        """Stop the background cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
    
    async def create_job(self, handle: str, platform: Platform) -> str:
        """
        Create a new job or return existing job ID for the same handle+platform.
        Ensures idempotency by checking handle:platform composite key.
        """
        handle_key = f"{handle}:{platform}"
        
        async with self._lock:
            # Check if job already exists for this handle+platform
            if handle_key in self._handle_index:
                existing_job_id = self._handle_index[handle_key]
                if existing_job_id in self._jobs:
                    return existing_job_id
            
            # Create new job
            job_id = str(uuid.uuid4())
            job_state = JobState(
                job_id=job_id,
                handle=handle,
                platform=platform,
                status=ScrapeStatus.PENDING,
                phase=JobPhase.PENDING
            )
            
            self._jobs[job_id] = job_state
            self._handle_index[handle_key] = job_id
            
            return job_id
    
    async def get_job(self, job_id: str) -> Optional[JobState]:
        """Get job state by ID."""
        async with self._lock:
            return self._jobs.get(job_id)
    
    async def update_job_status(
        self, 
        job_id: str, 
        status: ScrapeStatus, 
        phase: JobPhase,
        percent: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """Update job status and progress."""
        async with self._lock:
            if job_id not in self._jobs:
                return False
            
            job = self._jobs[job_id]
            job.status = status
            job.phase = phase
            job.percent = percent
            job.error_message = error_message
            job.updated_at = datetime.utcnow()
            
            if status in [ScrapeStatus.COMPLETED, ScrapeStatus.FAILED]:
                job.completed_at = datetime.utcnow()
            
            return True
    
    async def set_job_report(self, job_id: str, report: ReportResponse) -> bool:
        """Set the completed report data for a job."""
        async with self._lock:
            if job_id not in self._jobs:
                return False
            
            job = self._jobs[job_id]
            job.report_data = report
            job.status = ScrapeStatus.COMPLETED
            job.phase = JobPhase.COMPLETED
            job.percent = 100
            job.completed_at = datetime.utcnow()
            job.updated_at = datetime.utcnow()
            
            return True
    
    async def increment_retry(self, job_id: str) -> bool:
        """Increment retry count for failed job."""
        async with self._lock:
            if job_id not in self._jobs:
                return False
            
            job = self._jobs[job_id]
            job.retry_count += 1
            job.last_retry_at = datetime.utcnow()
            job.updated_at = datetime.utcnow()
            
            return True
    
    async def _periodic_cleanup(self):
        """Background task to clean up expired jobs."""
        while True:
            try:
                await asyncio.sleep(self._cleanup_interval.total_seconds())
                await self._cleanup_expired_jobs()
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log error but continue cleanup task
                print(f"Error in cleanup task: {e}")
    
    async def _cleanup_expired_jobs(self):
        """Remove jobs that have exceeded their TTL."""
        async with self._lock:
            now = datetime.utcnow()
            expired_jobs = []
            
            for job_id, job in self._jobs.items():
                if job.completed_at and (now - job.completed_at) > self._ttl:
                    expired_jobs.append(job_id)
            
            # Remove expired jobs and their handle index entries
            for job_id in expired_jobs:
                job = self._jobs[job_id]
                handle_key = f"{job.handle}:{job.platform}"
                if handle_key in self._handle_index and self._handle_index[handle_key] == job_id:
                    del self._handle_index[handle_key]
                del self._jobs[job_id]

# Global job registry instance
job_registry = JobRegistry()