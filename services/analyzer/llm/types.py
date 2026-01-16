from typing import List, Optional
from pydantic import BaseModel, Field

class LLMRefinementResult(BaseModel):
    """
    Structured output from the LLM Refinement Layer.
    Ensures strict adherence to output contract.
    """
    refined_score: float = Field(..., description="Final score after bounded refinement")
    adjustment: int = Field(..., description="Adjustment value (e.g. -5, +10), limited to +/- 15")
    explanation: str = Field(..., description="Rationale for the adjustment")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Calibrated confidence score")
    flags: List[str] = Field(default_factory=list, description="Risk flags identified by LLM")
    
class BrandSafetyResult(BaseModel):
    grade: str = Field(..., pattern="^[A-F][+-]?$")
    risk_score: float = Field(..., ge=0.0, le=100.0)
    flags: List[str]
    confidence: float
    explanation: str
    fallback_mode: Optional[str] = None
