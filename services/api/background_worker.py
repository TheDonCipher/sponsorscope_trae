import asyncio
from datetime import datetime
from typing import Optional
from services.api.job_manager import job_registry, JobPhase, JobState
from services.api.models.report import ReportResponse
from services.api.assembler import ReportAssembler
from services.api.retry_handler import (
    RetryHandler, SCRAPING_RETRY_CONFIG, ANALYSIS_RETRY_CONFIG, ASSEMBLY_RETRY_CONFIG,
    is_network_error, is_rate_limit_error
)
from services.governance.core.killswitch import KillSwitch
from services.governance.core.proxy import GovernanceProxy
from services.scraper.adapters.instagram import InstagramScraper
from services.analyzer.heuristics.engagement import compute_true_engagement
from services.analyzer.heuristics.authenticity import compute_audience_authenticity
from shared.schemas.domain import DataCompleteness, Platform, ScrapeStatus

class BackgroundWorker:
    """
    Background worker that processes async analysis jobs.
    Handles the complete pipeline from scraping to report generation.
    """
    
    def __init__(self):
        self._running = False
        self._worker_task: Optional[asyncio.Task] = None
        self._semaphore = asyncio.Semaphore(3)  # Max 3 concurrent jobs
        
        # Initialize retry handlers for different phases
        self._scraping_retry_handler = RetryHandler(SCRAPING_RETRY_CONFIG)
        self._analysis_retry_handler = RetryHandler(ANALYSIS_RETRY_CONFIG)
        self._assembly_retry_handler = RetryHandler(ASSEMBLY_RETRY_CONFIG)
    
    async def start(self):
        """Start the background worker."""
        if not self._running:
            self._running = True
            self._worker_task = asyncio.create_task(self._process_jobs())
    
    async def stop(self):
        """Stop the background worker."""
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
    
    async def _process_jobs(self):
        """Main worker loop that processes pending jobs."""
        while self._running:
            try:
                # Get pending jobs
                pending_jobs = await self._get_pending_jobs()
                
                # Process jobs concurrently (limited by semaphore)
                if pending_jobs:
                    tasks = [
                        asyncio.create_task(self._process_single_job(job))
                        for job in pending_jobs
                    ]
                    await asyncio.gather(*tasks, return_exceptions=True)
                
                # Wait before next check
                await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in background worker: {e}")
                await asyncio.sleep(5)  # Wait longer on error
    
    async def _get_pending_jobs(self) -> list[JobState]:
        """Get all pending jobs that need processing."""
        # This is a simplified implementation - in production you'd query the registry
        # For now, we'll check all jobs and return those that are pending
        pending = []
        # Note: In a real implementation, this would be a proper query
        # For this demo, we'll return empty list and rely on external job submission
        return pending
    
    async def _process_single_job(self, job: JobState):
        """Process a single analysis job."""
        async with self._semaphore:
            try:
                await self._execute_job_pipeline(job)
            except Exception as e:
                await self._handle_job_failure(job, str(e))
    
    async def _execute_job_pipeline(self, job: JobState):
        """Execute the complete analysis pipeline for a job."""
        job_id = job.job_id
        handle = job.handle
        platform = job.platform
        
        # Update status to processing
        await job_registry.update_job_status(
            job_id, 
            ScrapeStatus.PROCESSING, 
            JobPhase.SCRAPING,
            percent=0
        )
        
        try:
            # Kill Switch Checks
            if not KillSwitch.is_read_enabled():
                raise Exception("Read operations are disabled by kill switch")
            
            if not KillSwitch.is_scan_enabled():
                raise Exception("Scan operations are disabled by kill switch")
            
            # Phase 1: Scraping (30% of progress)
            await self._scraping_phase(job, handle, platform)
            
            # Phase 2: Analysis (60% of progress)
            await self._analysis_phase(job, handle, platform)
            
            # Phase 3: Finalizing (10% of progress)
            await self._finalizing_phase(job, handle, platform)
            
        except Exception as e:
            await self._handle_job_failure(job, str(e))
    
    async def _scraping_phase(self, job: JobState, handle: str, platform: Platform):
        """Execute the scraping phase with retry logic."""
        await job_registry.update_job_status(
            job.job_id,
            ScrapeStatus.PROCESSING,
            JobPhase.SCRAPING,
            percent=10
        )
        
        # Define scraping function with retry logic
        async def _scraping_operation():
            # Initialize scraper (currently only Instagram supported)
            scraper = InstagramScraper()
            gp = GovernanceProxy()
            
            # Check governance constraints
            session = gp.start_session(handle, platform)
            if not gp.can_start(platform):
                gp.end_session(session, success=False, failure_reason="budget_exhausted")
                raise Exception("Scan budget reached for platform")
            
            # Apply pacing
            await gp.pacer.await_pacing(handle, 0)
            
            # Update progress
            await job_registry.update_job_status(
                job.job_id,
                ScrapeStatus.PROCESSING,
                JobPhase.SCRAPING,
                percent=20
            )
            
            # Run scan
            scan_result = await scraper.run_scan(handle)
            
            # Check scan results
            if scan_result.data_completeness == DataCompleteness.UNAVAILABLE:
                gp.end_session(session, success=False, failure_reason="handle_not_found")
                raise Exception(f"Handle @{handle} not found on {platform}")
            
            if scan_result.data_completeness == DataCompleteness.FAILED:
                gp.end_session(session, success=False, failure_reason="scrape_failed")
                raise Exception("Failed to scrape data")
            
            return scan_result, session, gp
        
        # Execute with retry logic
        try:
            scan_result, session, gp = await self._scraping_retry_handler.execute_with_conditional_retry(
                _scraping_operation,
                should_retry=lambda e: is_network_error(e) or is_rate_limit_error(e)
            )
            
            # Store scan result for next phase
            job._scan_result = scan_result
            job._session = session
            job._gp = gp
            
            # Update progress
            await job_registry.update_job_status(
                job.job_id,
                ScrapeStatus.PROCESSING,
                JobPhase.SCRAPING,
                percent=30
            )
            
        except Exception as e:
            # If scraping fails after retries, re-raise the exception
            raise Exception(f"Scraping failed after retries: {str(e)}")
    
    async def _analysis_phase(self, job: JobState, handle: str, platform: Platform):
        """Execute the analysis phase with retry logic."""
        await job_registry.update_job_status(
            job.job_id,
            ScrapeStatus.PROCESSING,
            JobPhase.ANALYSIS,
            percent=35
        )
        
        scan_result = job._scan_result
        
        # Define analysis function with retry logic
        async def _analysis_operation():
            # Run engagement analysis
            engagement_result = compute_true_engagement(
                scan_result.profile,
                scan_result.posts,
                scan_result.comments
            )
            
            await job_registry.update_job_status(
                job.job_id,
                ScrapeStatus.PROCESSING,
                JobPhase.ANALYSIS,
                percent=60
            )
            
            # Run authenticity analysis
            authenticity_result = compute_audience_authenticity(
                scan_result.profile,
                scan_result.posts,
                scan_result.comments
            )
            
            return engagement_result, authenticity_result
        
        # Execute with retry logic
        try:
            engagement_result, authenticity_result = await self._analysis_retry_handler.execute_with_retry(
                _analysis_operation
            )
            
            # Store analysis results
            job._engagement_result = engagement_result
            job._authenticity_result = authenticity_result
            
            await job_registry.update_job_status(
                job.job_id,
                ScrapeStatus.PROCESSING,
                JobPhase.ANALYSIS,
                percent=85
            )
            
        except Exception as e:
            # If analysis fails after retries, re-raise the exception
            raise Exception(f"Analysis failed after retries: {str(e)}")
    
    async def _finalizing_phase(self, job: JobState, handle: str, platform: Platform):
        """Execute the finalizing phase and generate report with retry logic."""
        await job_registry.update_job_status(
            job.job_id,
            ScrapeStatus.PROCESSING,
            JobPhase.FINALIZING,
            percent=90
        )
        
        scan_result = job._scan_result
        session = job._session
        gp = job._gp
        
        # Define finalizing function with retry logic
        async def _finalizing_operation():
            # Assemble final report
            report = ReportAssembler.assemble(
                handle=handle,
                platform=platform.value,
                heuristic_results={
                    "engagement": job._engagement_result,
                    "authenticity": job._authenticity_result
                },
                llm_results={},  # No LLM integration yet
                raw_evidence=[]
            )
            
            # Add governance banners
            gp.end_session(
                session, 
                success=scan_result.data_completeness != DataCompleteness.FAILED,
                failure_reason=";".join(scan_result.errors) if scan_result.errors else None
            )
            report.warning_banners = report.warning_banners + gp.compute_banners(scan_result, session)
            
            return report
        
        # Execute with retry logic
        try:
            report = await self._assembly_retry_handler.execute_with_retry(_finalizing_operation)
            
            # Store completed report
            await job_registry.set_job_report(job.job_id, report)
            
            await job_registry.update_job_status(
                job.job_id,
                ScrapeStatus.COMPLETED,
                JobPhase.COMPLETED,
                percent=100
            )
            
        except Exception as e:
            # If finalizing fails after retries, re-raise the exception
            raise Exception(f"Finalizing failed after retries: {str(e)}")
    
    async def _handle_job_failure(self, job: JobState, error_message: str):
        """Handle job failure with retry logic."""
        # Increment retry count
        await job_registry.increment_retry(job.job_id)
        
        # Update job status to failed
        await job_registry.update_job_status(
            job.job_id,
            ScrapeStatus.FAILED,
            JobPhase.FAILED,
            error_message=error_message
        )
        
        print(f"Job {job.job_id} failed: {error_message}")
    
    async def submit_job(self, handle: str, platform: Platform) -> str:
        """
        Submit a new job for processing.
        This method creates the job and immediately returns the job ID.
        The actual processing happens in the background worker loop.
        """
        # Create job in registry
        job_id = await job_registry.create_job(handle, platform)
        
        # Get the job state
        job = await job_registry.get_job(job_id)
        if not job:
            raise Exception("Failed to create job")
        
        # Immediately process this job (for demo purposes)
        # In production, this would be queued for background processing
        asyncio.create_task(self._process_single_job(job))
        
        return job_id

# Global background worker instance
background_worker = BackgroundWorker()