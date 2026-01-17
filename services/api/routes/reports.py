from fastapi import APIRouter, HTTPException, Depends, Request
from services.api.models.report import ReportResponse
from services.api.assembler import ReportAssembler
from services.governance.core.killswitch import KillSwitch
from services.scraper.adapters.instagram import InstagramScraper
from services.analyzer.heuristics.engagement import compute_true_engagement
from services.analyzer.heuristics.authenticity import compute_audience_authenticity
from shared.schemas.domain import DataCompleteness
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
    if not KillSwitch.is_read_enabled():
        raise HTTPException(status_code=503, detail=KillSwitch.get_maintenance_message())

    # 1. Initialize Scraper (Default to Instagram for MVP)
    # TODO: Detect platform from handle or add query param
    scraper = InstagramScraper()
    
    # 2. Run Scan
    # This fetches "mock" data from the adapter, but using the real interface structure
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
        platform="instagram",
        heuristic_results={
            "engagement": engagement_result,
            "authenticity": authenticity_result
        },
        llm_results={}, # No LLM integration yet
        raw_evidence=[]
    )
    
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
