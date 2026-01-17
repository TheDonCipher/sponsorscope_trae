from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from shared.schemas.domain import ScrapeStatus, Platform
from services.api.models.report import ReportResponse

class AnalyzeRequest(BaseModel):
    """Request model for analysis submission."""
    handle: str = Field(..., description="Social media handle to analyze")
    platform: Optional[str] = Field("instagram", description="Platform (instagram/tiktok/youtube)")

class AnalyzeResponse(BaseModel):
    """Response model for analysis submission."""
    job_id: str = Field(..., description="Unique identifier for the analysis job")
    status: str = Field("accepted", description="Job submission status")

class JobStatusResponse(BaseModel):
    """Response model for job status check."""
    job_id: str = Field(..., description="Job identifier")
    status: ScrapeStatus = Field(..., description="Job status (pending/processing/completed/failed)")
    phase: str = Field(..., description="Current processing phase")
    percent: Optional[int] = Field(None, description="Completion percentage (0-100)")
    created_at: datetime = Field(..., description="ISO timestamp of job creation")
    updated_at: datetime = Field(..., description="ISO timestamp of last status update")
    error_message: Optional[str] = Field(None, description="Error message if job failed")

class ReportResponseWithJob(BaseModel):
    """Response model for report retrieval with job metadata."""
    job_id: str = Field(..., description="Job identifier")
    report: ReportResponse = Field(..., description="Complete analysis report")
    completed_at: datetime = Field(..., description="ISO timestamp when job was completed")