import unittest
from datetime import datetime, timedelta
from shared.schemas.raw import RawProfile, RawComment, Platform
from services.analyzer.graph.builder import GraphBuilder

class TestGraphBuilder(unittest.TestCase):
    
    def setUp(self):
        self.builder = GraphBuilder(min_commenters=5, min_interactions_per_edge=2)
        self.creator = RawProfile(
            handle="@creator", 
            platform=Platform.INSTAGRAM, 
            follower_count=1000, 
            following_count=10, 
            post_count=10
        )
        self.base_time = datetime.utcnow()

    def create_comments(self, count: int, author_prefix: str, interactions: int) -> list[RawComment]:
        comments = []
        for i in range(count):
            for j in range(interactions):
                comments.append(RawComment(
                    id=f"c_{i}_{j}",
                    text="test",
                    timestamp=self.base_time - timedelta(hours=1), # Recent
                    author_id=f"{author_prefix}_{i}"
                ))
        return comments

    def test_graph_construction_ok(self):
        # 6 commenters, 2 interactions each (Passes thresholds)
        comments = self.create_comments(6, "user", 2)
        graph = self.builder.build(self.creator, comments, "24h")
        
        self.assertEqual(graph.status, "OK")
        self.assertEqual(len(graph.edges), 6)
        self.assertEqual(graph.edges[0].comment_count, 2)
        self.assertAlmostEqual(graph.edges[0].recency_weight, 1.0, delta=0.1)

    def test_graph_inconclusive_commenters(self):
        # 4 commenters, 2 interactions each (Fails min_commenters=5)
        comments = self.create_comments(4, "user", 2)
        graph = self.builder.build(self.creator, comments, "24h")
        
        self.assertEqual(graph.status, "INCONCLUSIVE")
        # Edges still exist for debugging, but status is flagged
        self.assertEqual(len(graph.edges), 4)

    def test_graph_inconclusive_interactions(self):
        # 10 commenters, 1 interaction each (Fails min_interactions=2)
        comments = self.create_comments(10, "user", 1)
        graph = self.builder.build(self.creator, comments, "24h")
        
        # Edges are filtered out!
        self.assertEqual(len(graph.edges), 0)
        # Since valid edges = 0, valid commenters = 0 -> Inconclusive
        self.assertEqual(graph.status, "INCONCLUSIVE")

    def test_time_window_filtering(self):
        # 1 comment recent, 1 comment old (>24h)
        c1 = RawComment(id="1", text="new", timestamp=self.base_time, author_id="u1")
        c2 = RawComment(id="2", text="old", timestamp=self.base_time - timedelta(hours=25), author_id="u1")
        
        graph = self.builder.build(self.creator, [c1, c2], "24h")
        
        # Only c1 should be processed.
        # u1 has count=1. Fails min_interactions=2.
        self.assertEqual(len(graph.edges), 0)
        
        # If window is 7d, both included. count=2. Passes.
        # But fails min_commenters=5
        graph_7d = self.builder.build(self.creator, [c1, c2], "7d")
        self.assertEqual(len(graph_7d.edges), 1)
        self.assertEqual(graph_7d.edges[0].comment_count, 2)

if __name__ == '__main__':
    unittest.main()
