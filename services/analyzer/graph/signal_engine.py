from typing import List, Dict, Set
from services.analyzer.graph.schema import EngagementGraph
from services.analyzer.graph.signals import CoordinationSignals
from services.analyzer.graph.metrics.utils import calculate_timing_concentration, calculate_jaccard_similarity

class SignalEngine:
    """
    Computes statistical coordination signals from EngagementGraph artifacts.
    """
    
    def compute_signals(self, graph: EngagementGraph) -> CoordinationSignals:
        # 1. Timing Concentration (Requires edge metadata)
        # We need raw timestamps from edges. 
        # Schema `GraphEdge` has `first_interaction` and `last_interaction`.
        # This is a proxy. For precise timing, we'd need raw comments.
        # We will use `first_interaction` as the "arrival time".
        
        timestamps = [e.first_interaction for e in graph.edges]
        timing_conc = calculate_timing_concentration(timestamps)
        
        # 2. Edge Reuse Ratio
        # Ratio of edges that have > 1 interaction
        total_edges = len(graph.edges)
        if total_edges == 0:
            return self._empty_signal()
            
        reused_edges = sum(1 for e in graph.edges if e.comment_count > 1)
        edge_reuse = reused_edges / total_edges
        
        # 3. Commenter Overlap
        # Requires multi-post data. 
        # Since EngagementGraph is an aggregate of a window, we can't compute "overlap across posts" strictly from the graph structure alone without post-level segmentation.
        # However, `comment_count` > 1 implies overlap if the window covers multiple posts.
        # We'll use `edge_reuse` as a proxy for overlap in this aggregate view.
        overlap_score = edge_reuse # Simplified for aggregate graph
        
        # 4. Reciprocity (Not tracked in current GraphEdge schema for MVP)
        # We'll default to 0.0 unless we have outbound edges (Creator -> Commenter).
        reciprocity = 0.0 
        
        # 5. Confidence Calculation
        # Sample size gating
        confidence = 1.0
        if total_edges < 50:
            confidence *= 0.5
        if graph.status == "INCONCLUSIVE":
            confidence = 0.0
            
        # Notes generation
        notes = []
        if timing_conc > 0.8:
            notes.append("High temporal concentration detected (>80% within 5 mins).")
        if edge_reuse > 0.5:
            notes.append("High interaction reuse (>50% repeat commenters).")
            
        return CoordinationSignals(
            timing_concentration=timing_conc,
            commenter_overlap=overlap_score,
            edge_reuse_ratio=edge_reuse,
            reciprocity_score=reciprocity,
            sample_size=total_edges,
            confidence=confidence,
            notes=notes
        )
        
    def _empty_signal(self) -> CoordinationSignals:
        return CoordinationSignals(
            timing_concentration=0.0,
            commenter_overlap=0.0,
            edge_reuse_ratio=0.0,
            reciprocity_score=0.0,
            sample_size=0,
            confidence=0.0,
            notes=["Insufficient data"]
        )
