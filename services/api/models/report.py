from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from services.api.models.epistemic import EpistemicState

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
    history: List[float] = [] # Historical data for sparklines
    benchmark_delta: float = 0.0 # Percentage difference from niche average

class Metric(BaseModel):
    name: str
    value: str
    delta: str
    stability: float # 0.0 to 1.0

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
    niche_credibility: Optional[PillarScoreResponse] = None # Added for V2 dashboard
    
    # Detailed Stats
    profile_metrics: List[Metric] = []
    
    # Evidence Vault
    evidence_vault: List[Evidence]
    
    # Meta
    is_archival: bool = False
    warning_banners: List[str] = []
    known_limitations: List[str] = [
        "Advanced AI-generated comments may evade detection.",
        "Signals reflect probabilistic patterns, not individual intent."
    ]
