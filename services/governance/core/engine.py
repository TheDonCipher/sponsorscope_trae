from datetime import datetime, timedelta
from typing import Dict, Optional
from services.governance.models.request import CorrectionRequest, IssueType, RequestStatus
from shared.schemas.models import Report
from shared.schemas.domain import DataCompleteness

class GovernanceEngine:
    """
    Manages the lifecycle of correction requests.
    Enforces rules on rescan eligibility and rate limits.
    """
    
    def __init__(self, db_client=None):
        self.db = db_client # Mock for now
        # Simple in-memory storage for MVP testing
        self._requests: Dict[str, CorrectionRequest] = {}
        self._last_rescan: Dict[str, datetime] = {} # handle -> timestamp
        
    def submit_request(
        self, 
        handle: str, 
        report: Report, 
        issue_type: IssueType, 
        ip_address: str, 
        explanation: str = None
    ) -> CorrectionRequest:
        
        # 1. Abuse Prevention (Rate Limit by IP)
        # TODO: Implement Redis rate limiter here.
        
        # 2. Rescan Eligibility Check
        if not self._is_eligible_for_rescan(handle, report, issue_type):
            return self._create_denied_request(
                handle, report.id, issue_type, ip_address, 
                reason="Rescan not eligible: Limit 1 per 30 days or Data is already FULL."
            )
            
        # 3. Create Request
        req_id = f"req_{len(self._requests) + 1}"
        request = CorrectionRequest(
            request_id=req_id,
            handle=handle,
            previous_report_id=report.id,
            issue_type=issue_type,
            explanation=explanation,
            requester_ip=ip_address,
            status=RequestStatus.PENDING_REVIEW
        )
        
        self._requests[req_id] = request
        
        # 4. Auto-Approve Logic (for MVP)
        # If eligibility passed, we schedule rescan immediately
        self._approve_rescan(request)
        
        return request
    
    def _is_eligible_for_rescan(self, handle: str, report: Report, issue_type: IssueType) -> bool:
        # Rule: 1 rescan per 30 days
        last = self._last_rescan.get(handle)
        if last and (datetime.utcnow() - last) < timedelta(days=30):
            return False
            
        # Rule: Only if data incomplete OR platform error
        # Exception: "Context Missing" allows submission but maybe manual review
        if issue_type == IssueType.CONTEXT_MISSING:
            return True # Allowed but might not trigger auto-rescan
            
        if report.data_completeness == DataCompleteness.FULL and issue_type != IssueType.PLATFORM_ERROR:
            return False
            
        return True
        
    def _approve_rescan(self, request: CorrectionRequest):
        request.status = RequestStatus.RESCAN_SCHEDULED
        self._last_rescan[request.handle] = datetime.utcnow()
        # Trigger async scan task here
        
    def _create_denied_request(self, handle, report_id, issue, ip, reason) -> CorrectionRequest:
        return CorrectionRequest(
            request_id="denied",
            handle=handle,
            previous_report_id=report_id,
            issue_type=issue,
            requester_ip=ip,
            status=RequestStatus.DENIED,
            denial_reason=reason
        )
