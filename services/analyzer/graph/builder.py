from typing import List, Dict, Optional, Literal
from datetime import datetime, timedelta
from services.analyzer.graph.schema import EngagementGraph, GraphNode, GraphEdge
from shared.schemas.raw import RawPost, RawComment, RawProfile

class GraphBuilder:
    """
    Constructs immutable engagement graphs from raw interaction data.
    Enforces sample size gating and deterministic windowing.
    """
    
    def __init__(self, min_commenters: int = 15, min_interactions_per_edge: int = 2):
        self.min_commenters = min_commenters
        self.min_interactions_per_edge = min_interactions_per_edge

    def build(
        self, 
        creator: RawProfile, 
        comments: List[RawComment], 
        window: Literal["24h", "7d", "30d"]
    ) -> EngagementGraph:
        """
        Builds a graph for a specific time window.
        Returns 'INCONCLUSIVE' if data is insufficient.
        """
        
        # 1. Determine Cutoff Time
        now = datetime.utcnow()
        if window == "24h":
            cutoff = now - timedelta(hours=24)
        elif window == "7d":
            cutoff = now - timedelta(days=7)
        else: # 30d
            cutoff = now - timedelta(days=30)
            
        # 2. Filter Data (Deterministic Ordering)
        # Sort comments by timestamp to ensure deterministic processing order
        sorted_comments = sorted(
            [c for c in comments if c.timestamp >= cutoff],
            key=lambda x: x.timestamp
        )
        
        # 3. Aggregate Interactions
        node_map: Dict[str, GraphNode] = {}
        edge_map: Dict[str, Dict] = {} # commenter -> {count, first, last}
        
        # Add Creator Node
        node_map[creator.handle] = GraphNode(
            account_id=creator.handle, 
            role="creator", 
            first_seen=now # Placeholder, ideally profile.created_at if available
        )
        
        for comment in sorted_comments:
            author = comment.author_id
            
            # Skip invalid/private/deleted authors if flagged (assuming sanitized input)
            if not author or author == "unknown":
                continue

            # Update Commenter Node
            if author not in node_map:
                node_map[author] = GraphNode(
                    account_id=author,
                    role="commenter",
                    first_seen=comment.timestamp
                )
            
            # Update Edge Stats
            if author not in edge_map:
                edge_map[author] = {
                    "count": 0,
                    "first": comment.timestamp,
                    "last": comment.timestamp
                }
            
            edge_map[author]["count"] += 1
            if comment.timestamp < edge_map[author]["first"]:
                edge_map[author]["first"] = comment.timestamp
            if comment.timestamp > edge_map[author]["last"]:
                edge_map[author]["last"] = comment.timestamp

        # 4. Construct Edges & Apply Gating
        final_edges: List[GraphEdge] = []
        valid_commenter_count = 0
        
        for author, stats in edge_map.items():
            # Apply Edge Gating (Min interactions)
            # NOTE: Requirement says "Minimum interactions per edge: 2"
            # If we enforce this strictly, one-off comments are dropped.
            # This cleans the graph of noise.
            
            if stats["count"] < self.min_interactions_per_edge:
                continue
                
            valid_commenter_count += 1
            
            # Calculate Recency Weight (Linear decay)
            # 1.0 = now, 0.0 = cutoff
            # weight = 1 - (now - last) / (now - cutoff)
            total_window_seconds = (now - cutoff).total_seconds()
            age_seconds = (now - stats["last"]).total_seconds()
            weight = max(0.0, 1.0 - (age_seconds / total_window_seconds))
            
            final_edges.append(GraphEdge(
                from_node=author,
                to_node=creator.handle,
                comment_count=stats["count"],
                like_count=0, # Not available in comment object usually
                first_interaction=stats["first"],
                last_interaction=stats["last"],
                recency_weight=weight
            ))
            
        # 5. Graph Level Gating
        status = "OK"
        if valid_commenter_count < self.min_commenters:
            status = "INCONCLUSIVE"
            # Requirement: "Graph emits no downstream artifacts"
            # We return the graph object but marked inconclusive.
            # The analyzer layer must respect this flag.
            
        return EngagementGraph(
            window=window,
            nodes=node_map,
            edges=final_edges,
            status=status,
            built_at=now
        )
