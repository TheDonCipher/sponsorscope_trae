import math
from typing import List, Optional
from datetime import datetime
from collections import Counter
import statistics

def calculate_engagement_rate(likes: int, comments: int, followers: int) -> Optional[float]:
    """
    Computes raw engagement rate: (likes + (comments * 3)) / followers.
    Returns None if followers is 0.
    """
    if followers <= 0:
        return None
    return (likes + (comments * 3)) / followers

def calculate_entropy(texts: List[str]) -> Optional[float]:
    """
    Calculates Shannon entropy of the token distribution across all texts.
    Higher entropy = more diverse vocabulary.
    Returns None if no text is provided.
    """
    if not texts:
        return None
    
    # Simple tokenization: lowercase and split by whitespace
    tokens = []
    for text in texts:
        tokens.extend(text.lower().split())
    
    if not tokens:
        return 0.0
        
    total_tokens = len(tokens)
    counts = Counter(tokens)
    
    entropy = 0.0
    for count in counts.values():
        p = count / total_tokens
        entropy -= p * math.log2(p)
        
    return entropy

def calculate_uniqueness_ratio(author_ids: List[str]) -> Optional[float]:
    """
    Calculates ratio of unique commenters to total comments.
    1.0 = every comment is from a different person.
    Returns None if no authors provided.
    """
    if not author_ids:
        return None
        
    total = len(author_ids)
    unique = len(set(author_ids))
    
    return unique / total

def calculate_timing_variance(timestamps: List[datetime]) -> Optional[float]:
    """
    Calculates the variance of comment timestamps in seconds.
    Returns None if fewer than 2 timestamps.
    """
    if len(timestamps) < 2:
        return None
        
    # Convert to unix timestamps
    ts_seconds = [ts.timestamp() for ts in timestamps]
    
    try:
        return statistics.variance(ts_seconds)
    except statistics.StatisticsError:
        return 0.0
