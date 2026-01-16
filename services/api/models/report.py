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
    score: float
    grade: Optional[str] = None
    confidence: float
    flags: List[str]
    evidence_links: List[str]  # List of evidence_ids
    
class ReportResponse(BaseModel):
    id: str
    handle: str
    platform: str
    generated_at: str
    methodology_version: str
    data_completeness: str  # enum value
    
    # Pillars
    true_engagement: PillarScoreResponse
    audience_authenticity: PillarScoreResponse
    brand_safety: PillarScoreResponse
    
    # Evidence Vault
    evidence_vault: List[Evidence]
    
    # Meta
    is_archival: bool = False
    warning_banners: List[str] = []
