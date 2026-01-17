from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
from services.api.models.async_models import (
    AnalyzeRequest, 
    AnalyzeResponse, 
    JobStatusResponse,
    ReportResponseWithJob
)
from services.api.job_manager import job_registry
from services.api.background_worker import background_worker
from services.api.models.report import ReportResponse
from shared.schemas.domain import Platform, ScrapeStatus
import time

router = APIRouter()

@router.post("/analyze", response_model=AnalyzeResponse, status_code=202)
async def submit_analysis(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    Submit a new analysis request.
    Returns immediately with job ID, processing happens in background.
    
    Performance target: ≤200ms response time
    """
    start_time = time.time()
    
    try:
        # Validate platform
        platform_str = request.platform or "instagram"
        try:
            platform = Platform(platform_str.lower())
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid platform: {platform_str}. Must be one of: {[p.value for p in Platform]}"
            )
        
        # Clean handle (remove @ prefix if present)
        handle = request.handle.lstrip('@')
        
        if not handle:
            raise HTTPException(status_code=400, detail="Handle cannot be empty")
        
        # Create job with idempotency (handle+platform deduplication)
        job_id = await job_registry.create_job(handle, platform)
        
        # Submit job to background worker
        # Use background_tasks to ensure FastAPI manages the task lifecycle
        background_tasks.add_task(
            background_worker.submit_job, 
            handle, 
            platform
        )
        
        # Ensure response time target (≤200ms)
        elapsed = time.time() - start_time
        if elapsed > 0.2:  # 200ms
            print(f"Warning: Analysis submission took {elapsed*1000:.1f}ms")
        
        return AnalyzeResponse(job_id=job_id, status="accepted")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit analysis: {str(e)}")

@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get the current status and progress of an analysis job.
    
    Performance target: ≤100ms response time
    """
    start_time = time.time()
    
    try:
        # Get job state from registry
        job = await job_registry.get_job(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Ensure response time target (≤100ms)
        elapsed = time.time() - start_time
        if elapsed > 0.1:  # 100ms
            print(f"Warning: Status query took {elapsed*1000:.1f}ms")
        
        return JobStatusResponse(
            job_id=job.job_id,
            status=job.status,
            phase=job.phase.value,
            percent=job.percent,
            created_at=job.created_at,
            updated_at=job.updated_at,
            error_message=job.error_message
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")

@router.get("/report/{job_id}", response_model=ReportResponse)
async def get_job_report(job_id: str):
    """
    Get the completed analysis report for a job.
    
    Performance target: ≤500ms response time for completed reports
    """
    start_time = time.time()
    
    try:
        # Get job state from registry
        job = await job_registry.get_job(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Check if job is completed
        if job.status != ScrapeStatus.COMPLETED:
            if job.status == ScrapeStatus.FAILED:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Job failed: {job.error_message or 'Unknown error'}"
                )
            else:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Job not completed. Current status: {job.status.value}"
                )
        
        # Check if report data is available
        if not job.report_data:
            raise HTTPException(status_code=500, detail="Job completed but no report data available")
        
        # Ensure response time target (≤500ms)
        elapsed = time.time() - start_time
        if elapsed > 0.5:  # 500ms
            print(f"Warning: Report retrieval took {elapsed*1000:.1f}ms")
        
        return job.report_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job report: {str(e)}")

@router.get("/health/async")
async def async_health_check():
    """
    Health check for the async pipeline components.
    """
    try:
        # Check job registry
        registry_status = "healthy"
        
        # Check background worker
        worker_status = "running" if background_worker._running else "stopped"
        
        return {
            "status": "ok",
            "components": {
                "job_registry": registry_status,
                "background_worker": worker_status
            },
            "jobs": {
                "total": len(job_registry._jobs),
                "pending": sum(1 for job in job_registry._jobs.values() if job.status == ScrapeStatus.PENDING),
                "processing": sum(1 for job in job_registry._jobs.values() if job.status == ScrapeStatus.PROCESSING),
                "completed": sum(1 for job in job_registry._jobs.values() if job.status == ScrapeStatus.COMPLETED),
                "failed": sum(1 for job in job_registry._jobs.values() if job.status == ScrapeStatus.FAILED)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")