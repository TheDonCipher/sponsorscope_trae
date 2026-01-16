from typing import List, Tuple
from pydantic import BaseModel, Field

class CalibratedScoreEnvelope(BaseModel):
    """
    Final output of the calibration layer.
    Integrates base scores with graph signals and safety bands.
    """
    base_score: float = Field(..., description="Original Phase 1 score")
    adjusted_score: float = Field(..., description="Score after penalties (if any)")
    uncertainty_band: Tuple[float, float] = Field(..., description="(low, high) range")
    confidence: float = Field(..., ge=0.0, le=1.0)
    applied_adjustments: List[str] = Field(default_factory=list, description="List of signals that caused a penalty")
    suppressed_signals: List[str] = Field(default_factory=list, description="Signals ignored due to safety rules")
    calibration_version: str = "v2.3"
