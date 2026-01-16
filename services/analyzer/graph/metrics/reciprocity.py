from typing import List, Dict, Set, Optional
from services.analyzer.graph.schema import EngagementGraph, GraphCredibilitySignal

class ReciprocityAnalyzer:
    """
    Detects if commenters are also creators who receive comments from the target.
    A high reciprocity ratio suggests "Comment Pods" (Engagement Groups).
    """
    
    def analyze(self, graph: EngagementGraph, target_handle: str) -> Optional[GraphCredibilitySignal]:
        # Filter edges where target is the creator
        inbound_edges = [e for e in graph.edges if e.target == target_handle]
        if not inbound_edges:
            return None
            
        commenter_ids = {e.source for e in inbound_edges}
        total_commenters = len(commenter_ids)
        
        if total_commenters < 10: # Minimum sample size
            return None
            
        # Check if target comments back on these commenters (Outbound edges)
        # Note: This requires the graph to contain outbound edges from the target, 
        # which implies we scraped the target's comments on OTHER profiles.
        # For MVP, we might only have "Commenter X commented on Target".
        # If we lack outbound data, we check "Closed Loop Density" within the cluster.
        
        # Simplified Reciprocity for MVP:
        # Check if Commenter A commented on Target, AND Target commented on Commenter A (if we have that data)
        # OR: Check if Commenter A and Commenter B commented on EACH OTHER (Pod behavior)
        
        # Let's implement "Cluster Density": 
        # Do the commenters of Target also comment on each other?
        
        pod_connections = 0
        possible_connections = total_commenters * (total_commenters - 1)
        
        if possible_connections == 0:
            return None
            
        # This is expensive O(N^2) without a proper graph DB, but fine for N<1000
        # We need edges between commenters.
        # Assuming 'graph' contains a subgraph of the niche.
        
        for c1 in commenter_ids:
            for c2 in commenter_ids:
                if c1 == c2: continue
                # Check if c1 -> c2 exists
                if any(e.source == c1 and e.target == c2 for e in graph.edges):
                    pod_connections += 1
                    
        density = pod_connections / possible_connections
        
        # Thresholds
        # Organic density is usually low (< 0.05) for large accounts.
        # Pod density is high (> 0.1).
        
        if density > 0.1:
            return GraphCredibilitySignal(
                signal_strength=density, # Higher density = Stronger signal of pods
                detected_patterns=["high_cluster_density"],
                affected_metrics=["true_engagement", "audience_authenticity"],
                explanation=f"Detected high density ({density:.2f}) engagement cluster. {len(commenter_ids)} commenters interact heavily with each other, suggesting a pod.",
                confidence_penalty=min(0.5, density * 2) # Penalize up to 0.5
            )
            
        return None
