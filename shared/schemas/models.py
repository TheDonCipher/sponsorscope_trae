from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from pydantic import BaseModel, Field
from .domain import DataCompleteness, Platform

class ConfidenceInterval(BaseModel):
    lower: float
    upper: float
    confidence_score: float = Field(..., description="0-1.0 score based on data volume and AI consistency")

class ScoreEvidence(BaseModel):
    """Links to source data for a specific score."""
    source_post_ids: List[str] = Field(default_factory=list)
    snippet: Optional[str] = None
    explanation: Optional[str] = None

class PillarScore(BaseModel):
    score: float  # 0-100 or specific range
    grade: Optional[str] = None # A-F for Brand Safety
    confidence_interval: Optional[ConfidenceInterval] = None
    is_heuristic: bool = True
    llm_refined: bool = False
    fallback_mode: Optional[str] = None # e.g., "text_only"
    evidence: Optional[ScoreEvidence] = None

class MethodologyMetadata(BaseModel):
    version: str
    calibrated_region: str = "Botswana"
    heuristics_version: str
    llm_model: str = "gemini-1.5-flash"

class InfluencerProfile(BaseModel):
    handle: str
    platform: Platform
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    verification_status: bool = False

class Report(BaseModel):
    id: str
    handle: str
    platform: Platform
    
    # Metadata
    methodology_version: str
    methodology_metadata: MethodologyMetadata
    data_completeness: DataCompleteness
    
    # Scoring
    overall_score: float
    overall_confidence_interval: Tuple[float, float]
    
    # Pillars
    true_engagement: PillarScore
    audience_authenticity: PillarScore
    brand_safety: PillarScore
    niche_credibility: PillarScore
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    
    # Audit
    request_id: str
