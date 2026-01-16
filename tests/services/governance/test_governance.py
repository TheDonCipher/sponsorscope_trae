import unittest
from datetime import datetime, timedelta
from shared.schemas.models import Report, PillarScore, MethodologyMetadata, InfluencerProfile
from shared.schemas.domain import DataCompleteness, Platform
from services.governance.models.request import IssueType, RequestStatus
from services.governance.core.engine import GovernanceEngine

class TestGovernanceEngine(unittest.TestCase):
    
    def setUp(self):
        self.engine = GovernanceEngine()
        
        # Create a mock report
        self.mock_report = Report(
            id="rep_1",
            handle="@test_user",
            platform=Platform.INSTAGRAM,
            methodology_version="v2.3",
            methodology_metadata=MethodologyMetadata(version="v2.3", heuristics_version="v1", llm_model="test"),
            data_completeness=DataCompleteness.PARTIAL_NO_COMMENTS,
            overall_score=70.0,
            overall_confidence_interval=(65.0, 75.0),
            true_engagement=PillarScore(score=70.0, confidence=0.8, flags=[]),
            audience_authenticity=PillarScore(score=70.0, confidence=0.8, flags=[]),
            brand_safety=PillarScore(score=70.0, confidence=0.8, flags=[]),
            niche_credibility=PillarScore(score=70.0, confidence=0.8, flags=[]),
            expires_at=datetime.utcnow() + timedelta(days=30),
            request_id="req_origin"
        )

    def test_submit_valid_rescan(self):
        """Should approve rescan for partial data."""
        req = self.engine.submit_request(
            "@test_user", 
            self.mock_report, 
            IssueType.DATA_INCOMPLETE, 
            "127.0.0.1"
        )
        
        self.assertEqual(req.status, RequestStatus.RESCAN_SCHEDULED)
        self.assertEqual(req.handle, "@test_user")

    def test_deny_full_data_rescan(self):
        """Should deny rescan if data is already full (and no error claimed)."""
        full_report = self.mock_report.model_copy(update={"data_completeness": DataCompleteness.FULL})
        
        req = self.engine.submit_request(
            "@test_user", 
            full_report, 
            IssueType.DATA_INCOMPLETE, 
            "127.0.0.1"
        )
        
        self.assertEqual(req.status, RequestStatus.DENIED)
        self.assertIn("Data is already FULL", req.denial_reason)

    def test_rate_limit_30_days(self):
        """Should deny second rescan within 30 days."""
        # First request
        self.engine.submit_request(
            "@test_user", 
            self.mock_report, 
            IssueType.DATA_INCOMPLETE, 
            "127.0.0.1"
        )
        
        # Second request
        req2 = self.engine.submit_request(
            "@test_user", 
            self.mock_report, 
            IssueType.DATA_INCOMPLETE, 
            "127.0.0.1"
        )
        
        self.assertEqual(req2.status, RequestStatus.DENIED)
        self.assertIn("Limit 1 per 30 days", req2.denial_reason)

if __name__ == '__main__':
    unittest.main()
