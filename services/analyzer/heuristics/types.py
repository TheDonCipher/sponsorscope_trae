from typing import Dict, Optional, Union
from pydantic import BaseModel, Field
from shared.schemas.domain import DataCompleteness

class HeuristicResult(BaseModel):
    """
    Standard output for all heuristic scoring functions.
    Contains the normalized score, raw computed value, confidence, and metadata.
    """
    score: float = Field(..., description="Normalized score (0-100) or probability (0-1.0)")
    raw_value: Optional[float] = Field(None, description="Raw computed metric (e.g., raw engagement rate)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the result based on data availability")
    data_completeness: DataCompleteness
    signals: Dict[str, Union[float, str, int, None]] = Field(default_factory=dict, description="Intermediate signals used for calculation")
