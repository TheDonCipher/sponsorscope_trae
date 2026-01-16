from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class IssueType(str, Enum):
    DATA_INCOMPLETE = "data_incomplete"
    COMMENTS_DISABLED = "comments_disabled"
    PRIVATE_ACCOUNT = "private_account"
    PLATFORM_ERROR = "platform_error"
    CONTEXT_MISSING = "context_missing"

class RequestStatus(str, Enum):
    PENDING_REVIEW = "pending_review"
    RESCAN_SCHEDULED = "rescan_scheduled"
    RESCAN_COMPLETED = "rescan_completed"
    DENIED = "denied"

class CorrectionRequest(BaseModel):
    request_id: str
    handle: str
    previous_report_id: str
    issue_type: IssueType
    explanation: Optional[str] = Field(None, max_length=500)
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    requester_ip: str # For rate limiting
    status: RequestStatus = RequestStatus.PENDING_REVIEW
    denial_reason: Optional[str] = None
    rescan_report_id: Optional[str] = None
