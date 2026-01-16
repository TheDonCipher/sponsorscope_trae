from typing import List, Dict, Tuple
from collections import defaultdict
from services.analyzer.graph.schema import EngagementGraph, GraphCredibilitySignal

class EngagementReuseAnalyzer:
    """
    Detects if the same group of commenters appears across multiple posts/creators 
    in a way that defies organic probability.
    """
    
    def analyze(self, graph: EngagementGraph, target_handle: str) -> Optional[GraphCredibilitySignal]:
        # For a single creator scan, we look at "Commenter Reuse across Posts"
        # If the same 50 people comment on EVERY post, it's suspicious (or loyal fans).
        # We need to distinguish fans from pods.
        # Pods usually have EXACTLY the same set. Fans have overlap.
        
        # 1. Group commenters by post (using edge metadata or reconstructing)
        # For this MVP, let's assume we have edges with 'interaction_count'
        
        inbound = [e for e in graph.edges if e.target == target_handle]
        if not inbound:
            return None
            
        # Count how many commenters are "High Frequency"
        # e.g. Commented on > 80% of recent posts? 
        # Since edges are aggregated (comment_count), we can check:
        # If we scanned 10 posts, and Commenter A has 10 comments, they are 100% active.
        
        # We need 'scanned_post_count' passed in or inferred.
        # Let's infer from max interaction_count? No.
        # Let's assume we define "Hyper-Active" as > 5 interactions in window.
        
        hyper_active_users = [e for e in inbound if e.interaction_count >= 5]
        total_users = len(inbound)
        
        if total_users < 20:
            return None
            
        reuse_ratio = len(hyper_active_users) / total_users
        
        # If > 30% of commenters are hyper-active, it's either a cult or a pod.
        # Organic usually has a long tail of 1-off commenters.
        
        if reuse_ratio > 0.3:
            return GraphCredibilitySignal(
                signal_strength=reuse_ratio,
                detected_patterns=["high_engagement_reuse"],
                affected_metrics=["audience_authenticity"],
                explanation=f"{reuse_ratio:.1%} of commenters are hyper-active (5+ comments). This lacks the organic long-tail distribution.",
                confidence_penalty=0.2
            )
            
        return None
