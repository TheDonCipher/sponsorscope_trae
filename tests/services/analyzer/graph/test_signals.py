import unittest
from datetime import datetime, timedelta
from services.analyzer.graph.schema import EngagementGraph, GraphEdge, GraphNode
from services.analyzer.graph.signal_engine import SignalEngine

class TestSignalEngine(unittest.TestCase):
    
    def setUp(self):
        self.engine = SignalEngine()
        self.base_time = datetime.utcnow()
        
    def test_high_concentration_signal(self):
        """Simulate a burst of comments within seconds"""
        graph = EngagementGraph(window="24h", status="OK")
        
        # 50 comments all at same time
        for i in range(50):
            graph.edges.append(GraphEdge(
                from_node=f"u{i}",
                to_node="creator",
                comment_count=1,
                first_interaction=self.base_time,
                last_interaction=self.base_time,
                recency_weight=1.0
            ))
            
        signals = self.engine.compute_signals(graph)
        
        self.assertAlmostEqual(signals.timing_concentration, 1.0)
        self.assertIn("High temporal concentration", signals.notes[0])
        self.assertTrue(signals.confidence > 0.6)

    def test_high_reuse_signal(self):
        """Simulate loyal/pod users commenting multiple times"""
        graph = EngagementGraph(window="24h", status="OK")
        
        # 50 users, all have 5 interactions
        for i in range(50):
            graph.edges.append(GraphEdge(
                from_node=f"u{i}",
                to_node="creator",
                comment_count=5, # High reuse
                first_interaction=self.base_time,
                last_interaction=self.base_time,
                recency_weight=1.0
            ))
            
        signals = self.engine.compute_signals(graph)
        
        self.assertAlmostEqual(signals.edge_reuse_ratio, 1.0)
        # Note: Burst detection also triggers because timestamps are identical
        self.assertTrue(any("High interaction reuse" in n for n in signals.notes))

    def test_low_confidence_sparse_graph(self):
        """Simulate insufficient data"""
        graph = EngagementGraph(window="24h", status="OK")
        
        # Only 5 edges
        for i in range(5):
            graph.edges.append(GraphEdge(
                from_node=f"u{i}",
                to_node="creator",
                comment_count=1,
                first_interaction=self.base_time,
                last_interaction=self.base_time,
                recency_weight=1.0
            ))
            
        signals = self.engine.compute_signals(graph)
        
        self.assertTrue(signals.confidence < 0.6) # Should be penalized for sample size

if __name__ == '__main__':
    unittest.main()
