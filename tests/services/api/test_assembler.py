import unittest
from datetime import datetime
from shared.schemas.domain import DataCompleteness
from services.analyzer.heuristics.types import HeuristicResult
from services.analyzer.llm.types import LLMRefinementResult
from services.api.assembler import ReportAssembler

class TestReportAssembler(unittest.TestCase):
    
    def test_assemble_full_report(self):
        heuristic_res = HeuristicResult(
            score=80.0,
            confidence=1.0,
            data_completeness=DataCompleteness.FULL,
            signals={"entropy": 4.5}
        )
        
        llm_res = LLMRefinementResult(
            refined_score=75.0,
            adjustment=-5,
            explanation="Minor spam",
            confidence=0.95,
            flags=["spam_suspect"]
        )
        
        heuristics = {
            "engagement": heuristic_res,
            "authenticity": heuristic_res 
        }
        
        llm_results = {
            "authenticity": llm_res
        }
        
        report = ReportAssembler.assemble(
            "@test", "instagram", heuristics, llm_results, []
        )
        
        self.assertEqual(report.handle, "@test")
        self.assertEqual(report.audience_authenticity.score, 75.0)
        self.assertEqual(report.audience_authenticity.confidence, 0.95)
        self.assertEqual(len(report.evidence_vault), 2) # 1 for engagement, 1 for auth
        self.assertEqual(report.data_completeness, "full")

    def test_assemble_partial_report(self):
        heuristic_res = HeuristicResult(
            score=50.0,
            confidence=0.5,
            data_completeness=DataCompleteness.PARTIAL_NO_COMMENTS,
            signals={}
        )
        
        heuristics = {
            "engagement": heuristic_res,
            "authenticity": heuristic_res
        }
        
        report = ReportAssembler.assemble(
            "@test", "instagram", heuristics, {}, []
        )
        
        self.assertEqual(report.data_completeness, "partial_no_comments")
        self.assertTrue(len(report.warning_banners) > 0)
        self.assertIn("partial data", report.warning_banners[0])

if __name__ == '__main__':
    unittest.main()
