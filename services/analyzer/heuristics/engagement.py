from typing import List
from shared.schemas.raw import RawPost, RawProfile, RawComment
from shared.schemas.domain import DataCompleteness
from .types import HeuristicResult
from .utils import calculate_engagement_rate

def normalize_engagement_score(raw_rate: float) -> float:
    """
    Normalizes raw engagement rate (0.0 to 1.0+) to a 0-100 score.
    Uses static bands as fallback for benchmarks.
    
    Bands:
    - < 1.0%: Poor (0-40)
    - 1.0% - 3.0%: Average (40-70)
    - 3.0% - 6.0%: Good (70-90)
    - > 6.0%: Excellent (90-100)
    """
    # Linear interpolation within bands
    if raw_rate < 0.01:
        # 0.0 -> 0, 0.01 -> 40
        return (raw_rate / 0.01) * 40
    elif raw_rate < 0.03:
        # 0.01 -> 40, 0.03 -> 70
        return 40 + ((raw_rate - 0.01) / 0.02) * 30
    elif raw_rate < 0.06:
        # 0.03 -> 70, 0.06 -> 90
        return 70 + ((raw_rate - 0.03) / 0.03) * 20
    else:
        # 0.06 -> 90, 0.10 -> 100 (cap at 100)
        score = 90 + ((raw_rate - 0.06) / 0.04) * 10
        return min(score, 100.0)

def compute_true_engagement(
    profile: RawProfile, 
    posts: List[RawPost], 
    comments: List[RawComment]
) -> HeuristicResult:
    """
    Computes True Engagement Score based on weighted interactions.
    Formula: (Likes + (Comments * 3)) / Followers
    """
    if not posts:
        return HeuristicResult(
            score=0.0,
            raw_value=0.0,
            confidence=0.0,
            data_completeness=DataCompleteness.FAILED, # Or ARCHIVAL? Assuming failed/empty
            signals={"reason": "no_posts"}
        )

    total_likes = sum(p.like_count for p in posts)
    total_comments = sum(p.comment_count for p in posts)
    
    # Calculate raw rate
    # Use average per post or total? Usually engagement rate is per post average.
    # "Engagement Rate: (likes + (comments * 3)) / followers"
    # Usually this means Average Engagement Rate per Post.
    # Let's compute average interactions per post, then divide by followers.
    
    avg_likes = total_likes / len(posts)
    avg_comments = total_comments / len(posts)
    
    raw_rate = calculate_engagement_rate(avg_likes, avg_comments, profile.follower_count)
    
    if raw_rate is None:
         return HeuristicResult(
            score=0.0,
            raw_value=0.0,
            confidence=0.0,
            data_completeness=DataCompleteness.FAILED,
            signals={"reason": "zero_followers"}
        )

    normalized_score = normalize_engagement_score(raw_rate)
    
    # Determine Completeness and Confidence
    completeness = DataCompleteness.FULL
    confidence = 1.0
    
    # Check if we have comment objects matching the counts
    # If we have 0 comment objects but total_comments > 0, we likely missed scraping comments
    # However, for Engagement Score, we rely on counts, so this is less critical than for Authenticity
    # But we should still flag it.
    
    scraped_comments_count = len(comments)
    if total_comments > 0 and scraped_comments_count == 0:
        completeness = DataCompleteness.PARTIAL_NO_COMMENTS
        # Confidence slightly lower because we can't verify if comments are spam
        confidence *= 0.9
        
    if len(posts) < 5:
        confidence *= 0.7
    elif len(posts) < 10:
        confidence *= 0.9

    return HeuristicResult(
        score=normalized_score,
        raw_value=raw_rate,
        confidence=confidence,
        data_completeness=completeness,
        signals={
            "avg_likes": avg_likes,
            "avg_comments": avg_comments,
            "post_count": len(posts),
            "follower_count": profile.follower_count
        }
    )
