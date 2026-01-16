from typing import List
from shared.schemas.raw import RawPost, RawProfile, RawComment
from shared.schemas.domain import DataCompleteness
from .types import HeuristicResult
from .utils import calculate_entropy, calculate_uniqueness_ratio, calculate_timing_variance

def compute_audience_authenticity(
    profile: RawProfile,
    posts: List[RawPost],
    comments: List[RawComment]
) -> HeuristicResult:
    """
    Computes Audience Authenticity Score (0-100).
    Derived from Bot Probability Floor.
    
    Bot Probability Drivers:
    1. Low Comment Entropy (Repetitive text)
    2. Low Commenter Uniqueness (Same users spamming)
    3. Low Timing Variance (Burst/Scripted behavior)
    """
    
    if not comments:
        # Fallback if no comments available
        # If we expected comments (posts exist with comment_count > 0) but have none,
        # it's a data completeness issue.
        
        has_posts_with_comments = any(p.comment_count > 0 for p in posts)
        
        if has_posts_with_comments:
            return HeuristicResult(
                score=50.0, # Neutral/Unknown
                confidence=0.1, # Very low confidence
                data_completeness=DataCompleteness.PARTIAL_NO_COMMENTS,
                signals={"reason": "no_scraped_comments"}
            )
        else:
            # Genuine no comments (e.g. new account)
            return HeuristicResult(
                score=100.0, # Innocent until proven guilty? Or 0? 
                # Usually new accounts with 0 comments are N/A. 
                # Let's say 50 neutral.
                confidence=0.5,
                data_completeness=DataCompleteness.FULL,
                signals={"reason": "no_comments_on_posts"}
            )

    # Feature Extraction
    comment_texts = [c.text for c in comments]
    author_ids = [c.author_id for c in comments]
    timestamps = [c.timestamp for c in comments]
    
    entropy = calculate_entropy(comment_texts)
    uniqueness = calculate_uniqueness_ratio(author_ids)
    variance = calculate_timing_variance(timestamps)
    
    # Bot Probability Calculation (0.0 - 1.0)
    # We define thresholds for "Suspicious" behavior
    
    bot_signals = 0.0
    weights = 0.0
    
    # 1. Entropy (Weight 0.4)
    # Threshold: < 3.0 bits implies limited vocabulary/spam
    if entropy is not None:
        w_entropy = 0.4
        # Normalize entropy: 0 bits -> 1.0 prob, 4.0+ bits -> 0.0 prob
        # Linear ramp 2.0 to 4.0
        if entropy < 2.0:
            prob = 1.0
        elif entropy > 4.0:
            prob = 0.0
        else:
            prob = 1.0 - ((entropy - 2.0) / 2.0)
            
        bot_signals += prob * w_entropy
        weights += w_entropy
        
    # 2. Uniqueness (Weight 0.4)
    # Threshold: < 0.5 implies many repeat commenters
    if uniqueness is not None:
        w_unique = 0.4
        # Normalize: 0.1 -> 1.0 prob, 0.8 -> 0.0 prob
        if uniqueness < 0.1:
            prob = 1.0
        elif uniqueness > 0.8:
            prob = 0.0
        else:
            prob = 1.0 - ((uniqueness - 0.1) / 0.7)
            
        bot_signals += prob * w_unique
        weights += w_unique
        
    # 3. Variance (Weight 0.2)
    # Low variance means bursty/artificial
    # This is highly dependent on total volume, but low variance in a set is suspicious.
    # We skip if variance is None
    if variance is not None:
        w_variance = 0.2
        # Arbitrary threshold: < 60 seconds variance for a batch is weird?
        # Actually variance of timestamps across *all* comments might be huge if posts are far apart.
        # Ideally this should be per-post variance averaged.
        # But we are passed a flat list of comments.
        # If these comments span months, variance will be huge.
        # If we calculate variance of the *flat list*, it captures "do they all happen at once?"
        # If they span months, variance is high -> Good.
        # If they all happened in 1 minute, variance is low -> Bad.
        # So global variance is a decent proxy for "did we just scrape a burst?" or "is the profile only active for 1 day?"
        
        # Threshold: 1 hour (3600s) variance?
        if variance < 3600: 
            prob = 1.0 # Very concentrated
        else:
            prob = 0.0
            
        bot_signals += prob * w_variance
        weights += w_variance
        
    # Normalize final probability
    if weights == 0:
        bot_prob = 0.0
    else:
        bot_prob = bot_signals / weights
        
    # Calculate Authenticity Score
    authenticity_score = (1.0 - bot_prob) * 100.0
    
    # Confidence
    confidence = 1.0
    if len(comments) < 20:
        confidence *= 0.8
    if len(comments) < 5:
        confidence *= 0.5
        
    return HeuristicResult(
        score=authenticity_score,
        raw_value=bot_prob, # "Bot Probability Floor" as raw value
        confidence=confidence,
        data_completeness=DataCompleteness.FULL,
        signals={
            "entropy": entropy,
            "uniqueness": uniqueness,
            "variance": variance,
            "bot_probability": bot_prob
        }
    )
