from enum import Enum
from pydantic import BaseModel, Field

class EpistemicStatus(str, Enum):
    ROBUST = "ROBUST"   # High confidence, full data, corroboration
    PARTIAL = "PARTIAL" # Missing data, or conflicting signals
    FRAGILE = "FRAGILE" # Low sample size, or significant anomalies

class EpistemicState(BaseModel):
    """
    Meta-signal about the reliability of the report itself.
    """
    status: EpistemicStatus
    reason: str = Field(..., description="Plain language explanation of why reliability is limited")
    data_points_analyzed: int = 0
