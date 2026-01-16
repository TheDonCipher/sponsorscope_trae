import unittest
from datetime import datetime
from services.analyzer.graph.schema import EngagementGraph, GraphNode, GraphEdge
from services.analyzer.graph.metrics.reciprocity import ReciprocityAnalyzer

class TestReciprocity(unittest.TestCase):
    
    def test_pod_detection(self):
        """
        Simulate a pod where 20 commenters all comment on each other.
        """
        analyzer = ReciprocityAnalyzer()
        graph = EngagementGraph()
        target = "@creator"
        
        # Create 20 commenters
        commenters = [f"user_{i}" for i in range(20)]
        
        # 1. All comment on Target
        for c in commenters:
            graph.edges.append(GraphEdge(
                source=c, target=target, weight=1, interaction_count=1, last_interaction=datetime.utcnow()
            ))
            
        # 2. All comment on EACH OTHER (The Pod)
        # 20 users * 19 peers = 380 edges
        for c1 in commenters:
            for c2 in commenters:
                if c1 == c2: continue
                graph.edges.append(GraphEdge(
                    source=c1, target=c2, weight=1, interaction_count=1, last_interaction=datetime.utcnow()
                ))
                
        signal = analyzer.analyze(graph, target)
        
        self.assertIsNotNone(signal)
        self.assertEqual(signal.detected_patterns, ["high_cluster_density"])
        self.assertTrue(signal.signal_strength > 0.8) # Should be very high density (1.0 actually)
        
    def test_organic_community(self):
        """
        Simulate organic fans who don't know each other.
        """
        analyzer = ReciprocityAnalyzer()
        graph = EngagementGraph()
        target = "@creator"
        
        commenters = [f"fan_{i}" for i in range(50)]
        
        # All comment on Target
        for c in commenters:
            graph.edges.append(GraphEdge(
                source=c, target=target, weight=1, interaction_count=1, last_interaction=datetime.utcnow()
            ))
            
        # Very few comment on each other (Organic)
        # Let's say fan_0 and fan_1 are friends
        graph.edges.append(GraphEdge(source="fan_0", target="fan_1", weight=1, interaction_count=1, last_interaction=datetime.utcnow()))
        
        signal = analyzer.analyze(graph, target)
        
        # Density should be tiny: 1 edge / (50*49) = 1/2450 ~= 0.0004
        self.assertIsNone(signal) # Should be below threshold

if __name__ == '__main__':
    unittest.main()
