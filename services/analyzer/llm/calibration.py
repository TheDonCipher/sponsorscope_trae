from shared.schemas.domain import DataCompleteness
from typing import Optional

def calibrate_confidence(
    heuristic_confidence: float,
    llm_consistency_score: float, # 0.0 to 1.0 (1.0 = LLM agrees with Heuristics)
    data_completeness: DataCompleteness,
    monotonic_safety_applied: bool = False,
    llm_error_occurred: bool = False
) -> float:
    """
    Calibrates the final confidence score based on data availability, AI agreement, and safety rules.
    
    Enhanced calibration that accounts for:
    - Data completeness penalties
    - LLM consistency (agreement with heuristics)
    - Monotonic safety rule application
    - LLM errors and timeouts
    
    Rules:
    1. Final confidence <= Heuristic confidence.
    2. Partial data reduces confidence significantly.
    3. Low LLM consistency reduces confidence.
    4. Monotonic safety application slightly reduces confidence.
    5. LLM errors significantly reduce confidence.
    
    Args:
        heuristic_confidence: Base confidence from heuristic analysis
        llm_consistency_score: How much LLM agrees with heuristics (0.0-1.0)
        data_completeness: Level of data availability
        monotonic_safety_applied: Whether monotonic safety rules were triggered
        llm_error_occurred: Whether LLM encountered errors
        
    Returns:
        Calibrated confidence score (0.0-1.0)
    """
    
    base_confidence = heuristic_confidence
    
    # Penalty for Partial Data (monotonic safety factor)
    if data_completeness == DataCompleteness.PARTIAL_NO_COMMENTS:
        base_confidence *= 0.7
    elif data_completeness == DataCompleteness.PARTIAL_NO_IMAGES:
        base_confidence *= 0.8
    elif data_completeness == DataCompleteness.TEXT_ONLY:
        base_confidence *= 0.6
    elif data_completeness == DataCompleteness.ARCHIVAL:
        base_confidence *= 0.9
    elif data_completeness == DataCompleteness.FULL:
        base_confidence *= 1.0
        
    # Penalty for LLM Disagreement/Consistency
    # Large adjustments indicate lower consistency/higher uncertainty
    final_confidence = base_confidence * llm_consistency_score
    
    # Additional penalty for monotonic safety application
    # This indicates the LLM wanted to adjust but was constrained
    if monotonic_safety_applied:
        final_confidence *= 0.9  # 10% penalty for safety rule activation
        
    # Severe penalty for LLM errors
    if llm_error_occurred:
        final_confidence *= 0.5  # 50% penalty for LLM failures
        
    return round(min(final_confidence, heuristic_confidence), 2)
