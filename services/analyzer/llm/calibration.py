from shared.schemas.domain import DataCompleteness

def calibrate_confidence(
    heuristic_confidence: float,
    llm_consistency_score: float, # 0.0 to 1.0 (1.0 = LLM agrees with Heuristics)
    data_completeness: DataCompleteness
) -> float:
    """
    Calibrates the final confidence score based on data availability and AI agreement.
    
    Rules:
    1. Final confidence <= Heuristic confidence.
    2. Partial data reduces confidence significantly.
    3. Low LLM consistency reduces confidence.
    """
    
    base_confidence = heuristic_confidence
    
    # Penalty for Partial Data
    if data_completeness == DataCompleteness.PARTIAL_NO_COMMENTS:
        base_confidence *= 0.7
    elif data_completeness == DataCompleteness.PARTIAL_NO_IMAGES:
        base_confidence *= 0.8
    elif data_completeness == DataCompleteness.TEXT_ONLY:
        base_confidence *= 0.6
    elif data_completeness == DataCompleteness.ARCHIVAL:
        base_confidence *= 0.9
        
    # Penalty for AI Disagreement
    # If LLM wanted to move score by +15 but was capped, consistency is low.
    # For now, we assume llm_consistency_score is derived from adjustment magnitude.
    # Large adjustment = Lower consistency/Higher uncertainty about the baseline.
    
    # If adjustment is small (high consistency), confidence stays high.
    # If adjustment is large (low consistency), confidence drops.
    
    # Let's say llm_consistency is passed in. 
    # If LLM agrees (adjustment ~0), consistency ~1.0.
    # If LLM disagrees max (adjustment 15), consistency ~0.5.
    
    final_confidence = base_confidence * llm_consistency_score
    
    return round(min(final_confidence, heuristic_confidence), 2)
