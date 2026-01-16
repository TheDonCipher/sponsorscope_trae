from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class Evidence(BaseModel):
    """
    Traceable evidence linking a score to its source.
    """
    evidence_id: str
    type: Literal["post", "comment", "statistic"]
    source_url: str
    screenshot_path: Optional[str] = None
    excerpt: str
    timestamp: str  # ISO8601
    
class PillarScoreResponse(BaseModel):
    signal_strength: float = Field(..., description="Formerly 'score'. 0-100 credibility index.")
    grade: Optional[str] = None
    confidence: float
    flags: List[str]
    evidence_links: List[str]  # List of evidence_ids
    
from services.api.models.epistemic import EpistemicState

class ReportResponse(BaseModel):
    id: str
    handle: str
    platform: str
    generated_at: str
    methodology_version: str
    data_completeness: str  # enum value
    epistemic_state: EpistemicState
    
    # Pillars
    true_engagement: PillarScoreResponse
    audience_authenticity: PillarScoreResponse
    brand_safety: PillarScoreResponse
    
    # Evidence Vault
    evidence_vault: List[Evidence]
    
    # Meta
    is_archival: bool = False
    warning_banners: List[str] = []
    known_limitations: List[str] = [
        "Advanced AI-generated comments may evade detection.",
        "Signals reflect probabilistic patterns, not individual intent."
    ]
