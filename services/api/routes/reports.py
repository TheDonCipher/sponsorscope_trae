from fastapi import APIRouter, HTTPException, Depends, Request
from services.api.models.report import ReportResponse
from services.api.assembler import ReportAssembler
from services.governance.core.enhanced_killswitch import enhanced_killswitch
from services.governance.core.proxy import GovernanceProxy
from services.scraper.adapters.instagram import InstagramScraper
from services.analyzer.heuristics.engagement import compute_true_engagement
from services.analyzer.heuristics.authenticity import compute_audience_authenticity
from shared.schemas.domain import DataCompleteness, Platform
from services.governance.core.engine import GovernanceEngine
from services.governance.models.request import IssueType
from pydantic import BaseModel
from types import SimpleNamespace

router = APIRouter()

# Instantiate Governance Engine (Singleton-ish)
governance = GovernanceEngine(db_client=None)

class CorrectionInput(BaseModel):
    handle: str
    issue_type: IssueType
    explanation: str = None
    report_id: str = "unknown"

@router.get("/report/{handle}", response_model=ReportResponse)
async def get_report(handle: str):
    """
    Get or trigger a report for a specific handle.
    """
    # 0. Kill Switch Check (Read)
    if not await enhanced_killswitch.is_read_enabled():
        raise HTTPException(status_code=503, detail=enhanced_killswitch.get_maintenance_message())

    # 0. Kill Switch Check (Scan)
    if not await enhanced_killswitch.is_scan_enabled():
        raise HTTPException(status_code=503, detail=enhanced_killswitch.get_maintenance_message())

    # 1. Initialize Scraper (Default to Instagram for MVP)
    # TODO: Detect platform from handle or add query param
    scraper = InstagramScraper()
    gp = GovernanceProxy()
    platform = "instagram"
    session = gp.start_session(handle, Platform.INSTAGRAM)  # type: ignore
    if not gp.can_start(Platform.INSTAGRAM):
        gp.end_session(session, success=False, failure_reason="budget_exhausted")
        raise HTTPException(status_code=429, detail="Scan budget reached for platform")
    
    # 2. Run Scan
    # This fetches "mock" data from the adapter, but using the real interface structure
    await gp.pacer.await_pacing(handle, 0)
    scan_result = await scraper.run_scan(handle)
    
    if scan_result.data_completeness == DataCompleteness.UNAVAILABLE:
        raise HTTPException(status_code=404, detail=f"Handle @{handle} not found on Instagram.")
        
    if scan_result.data_completeness == DataCompleteness.FAILED:
        raise HTTPException(status_code=500, detail="Failed to scrape data.")

    # 3. Run Analysis
    # These compute real scores based on the (currently mocked) raw data
    engagement_result = compute_true_engagement(
        scan_result.profile, 
        scan_result.posts, 
        scan_result.comments
    )
    
    authenticity_result = compute_audience_authenticity(
        scan_result.profile, 
        scan_result.posts, 
        scan_result.comments
    )
    
    # 4. Assemble Report
    report = ReportAssembler.assemble(
        handle=handle,
        platform=platform,
        heuristic_results={
            "engagement": engagement_result,
            "authenticity": authenticity_result
        },
        llm_results={}, # No LLM integration yet
        raw_evidence=[]
    )
    gp.end_session(session, success=scan_result.data_completeness != DataCompleteness.FAILED, failure_reason=";".join(scan_result.errors) if scan_result.errors else None)
    
    # Add governance banners
    governance_banners = gp.compute_banners(scan_result, session)
    system_notices = await enhanced_killswitch.get_system_notices()
    
    # Combine all banners
    report.warning_banners = report.warning_banners + governance_banners + system_notices
    
    return report

@router.get("/evidence/{evidence_id}")
async def get_evidence(evidence_id: str):
    """
    Retrieve specific raw evidence (screenshot/json).
    """
    raise HTTPException(status_code=501, detail="Not implemented")

@router.post("/correction")
async def submit_correction(input: CorrectionInput, request: Request):
    """
    Submit a correction request for a report.
    """
    # Create a mock report object sufficient for GovernanceEngine check
    # We default to PARTIAL_NO_COMMENTS to allow the request to proceed in most cases,
    # unless the issue implies otherwise.
    # In a real system, we would fetch the report from DB.
    mock_report = SimpleNamespace(
        id=input.report_id,
        data_completeness=DataCompleteness.PARTIAL_NO_COMMENTS
    )
    
    result = governance.submit_request(
        handle=input.handle,
        report=mock_report, # type: ignore
        issue_type=input.issue_type,
        ip_address=request.client.host if request.client else "unknown",
        explanation=input.explanation
    )
    
    return result
