from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class CoordinationSignals(BaseModel):
    """
    Statistical signals indicating potential coordinated behavior.
    Non-accusatory, purely observational.
    """
    timing_concentration: float = Field(..., ge=0.0, le=1.0, description="Entropy-based burst detection (0=Random, 1=Concentrated)")
    commenter_overlap: float = Field(..., ge=0.0, le=1.0, description="Jaccard similarity across posts (0=Unique, 1=Identical)")
    edge_reuse_ratio: float = Field(..., ge=0.0, le=1.0, description="Repeated interactions ratio")
    reciprocity_score: float = Field(..., ge=0.0, le=1.0, description="Creator response rate to commenters")
    sample_size: int = Field(..., description="Number of interactions analyzed")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Statistical confidence in these signals")
    notes: List[str] = Field(default_factory=list, description="Neutral, explanatory context")
    signal_version: str = "v1.0"
    generated_at: datetime = Field(default_factory=datetime.utcnow)
