from typing import List, Dict, Any
from shared.schemas.raw import RawProfile, RawPost, RawComment
from services.analyzer.graph.schema import EngagementGraph, GraphNode, GraphEdge
from services.analyzer.graph.metrics.reciprocity import ReciprocityAnalyzer
from services.analyzer.graph.metrics.reuse import EngagementReuseAnalyzer
from services.analyzer.graph.schema import GraphCredibilitySignal

class GraphEngine:
    """
    Orchestrates graph construction and analysis.
    """
    
    def __init__(self):
        self.reciprocity = ReciprocityAnalyzer()
        self.reuse = EngagementReuseAnalyzer()
        
    def build_graph(self, profile: RawProfile, posts: List[RawPost], comments: List[RawComment]) -> EngagementGraph:
        """
        Constructs a local engagement graph from a single profile scan.
        """
        nodes = {}
        edges = []
        
        # Add Creator Node
        nodes[profile.handle] = GraphNode(account_id=profile.handle, type="creator")
        
        # Process Comments to build Edges
        # We aggregate comments by author
        comment_counts = {} # author -> count
        last_interactions = {} # author -> datetime
        
        for comment in comments:
            author = comment.author_id
            if author not in nodes:
                nodes[author] = GraphNode(account_id=author, type="commenter")
            
            comment_counts[author] = comment_counts.get(author, 0) + 1
            
            # Track recency
            ts = comment.timestamp
            if author not in last_interactions or ts > last_interactions[author]:
                last_interactions[author] = ts
                
        # Create Edges
        for author, count in comment_counts.items():
            edges.append(GraphEdge(
                source=author,
                target=profile.handle,
                weight=float(count), # Simple weight for now
                interaction_count=count,
                last_interaction=last_interactions[author]
            ))
            
        return EngagementGraph(nodes=nodes, edges=edges)
        
    def analyze(self, graph: EngagementGraph, target_handle: str) -> List[GraphCredibilitySignal]:
        signals = []
        
        # Run Reciprocity Check
        if sig := self.reciprocity.analyze(graph, target_handle):
            signals.append(sig)
            
        # Run Reuse Check
        if sig := self.reuse.analyze(graph, target_handle):
            signals.append(sig)
            
        return signals
