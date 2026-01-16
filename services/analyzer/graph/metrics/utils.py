import math
import statistics
from datetime import datetime
from typing import List
from shared.schemas.raw import RawComment

def calculate_timing_concentration(timestamps: List[datetime]) -> float:
    """
    Calculates 0-1 concentration score based on timestamp entropy.
    1.0 = All at same second (High Concentration)
    0.0 = Perfectly uniform
    """
    if len(timestamps) < 2:
        return 0.0
        
    # Convert to timestamps
    ts_vals = [t.timestamp() for t in timestamps]
    
    # 1. Burst Detection: Fraction of comments within 300s of median
    # This is a simple clustering check
    median_ts = statistics.median(ts_vals)
    burst_count = sum(1 for t in ts_vals if abs(t - median_ts) <= 300)
    burst_ratio = burst_count / len(ts_vals)
    
    # 2. Variance Penalty
    # Low variance = High concentration
    try:
        variance = statistics.variance(ts_vals)
        # Normalize variance. 1 hour variance (3600^2) is "normal" for a viral post?
        # Actually, let's stick to entropy or burst ratio for robustness.
        # Entropy of "minute buckets" is standard.
        pass
    except:
        pass
        
    return burst_ratio

def calculate_jaccard_similarity(set_a: set, set_b: set) -> float:
    """
    Jaccard Similarity = (A intersect B) / (A union B)
    """
    if not set_a and not set_b:
        return 0.0
    
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    
    if union == 0:
        return 0.0
        
    return intersection / union
