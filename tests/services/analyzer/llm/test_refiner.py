import unittest
import json
from unittest.mock import AsyncMock
from shared.schemas.domain import DataCompleteness
from services.analyzer.heuristics.types import HeuristicResult
from services.analyzer.llm.refiner import AuthenticityRefiner

class TestAuthenticityRefiner(unittest.IsolatedAsyncioTestCase):
    
    async def test_bounded_adjustment(self):
        """Test that adjustment is capped at +/- 15."""
        refiner = AuthenticityRefiner()
        # Mock LLM trying to add +50 points
        refiner._call_llm = AsyncMock(return_value=json.dumps({
            "adjustment": 50, 
            "reason": "It's super authentic!",
            "flags": []
        }))
        
        heuristic = HeuristicResult(
            score=50.0,
            confidence=1.0,
            data_completeness=DataCompleteness.FULL,
            signals={"bot_probability": 0.0}
        )
        
        result = await refiner.refine(heuristic, ["comment"], "English")
        
        self.assertEqual(result.adjustment, 15)
        self.assertEqual(result.refined_score, 65.0)
        
    async def test_partial_data_safety(self):
        """Test that scores cannot be raised if data is partial."""
        refiner = AuthenticityRefiner()
        # Mock LLM trying to add +10 points
        refiner._call_llm = AsyncMock(return_value=json.dumps({
            "adjustment": 10,
            "reason": "Looks good despite missing comments",
            "flags": []
        }))
        
        heuristic = HeuristicResult(
            score=50.0,
            confidence=0.8,
            data_completeness=DataCompleteness.PARTIAL_NO_COMMENTS,
            signals={"bot_probability": 0.0}
        )
        
        result = await refiner.refine(heuristic, [], "English")
        
        self.assertEqual(result.adjustment, 0)
        self.assertEqual(result.refined_score, 50.0)
        self.assertIn("suppressed due to partial data", result.explanation)

    async def test_bot_floor_respect(self):
        """Test that scores cannot be raised if bot probability is high."""
        refiner = AuthenticityRefiner()
        refiner._call_llm = AsyncMock(return_value=json.dumps({
            "adjustment": 10,
            "reason": "I think it's real",
            "flags": []
        }))
        
        heuristic = HeuristicResult(
            score=10.0, # Low score due to bot signals
            confidence=1.0,
            data_completeness=DataCompleteness.FULL,
            signals={"bot_probability": 0.9} # High bot prob
        )
        
        result = await refiner.refine(heuristic, ["spam"], "English")
        
        self.assertEqual(result.adjustment, 0)
        self.assertIn("suppressed due to high bot probability", result.explanation)

    async def test_lowering_score_always_allowed(self):
        """Test that Gemini can always lower the score."""
        refiner = AuthenticityRefiner()
        refiner._call_llm = AsyncMock(return_value=json.dumps({
            "adjustment": -10,
            "reason": "Found subtle spam",
            "flags": []
        }))
        
        heuristic = HeuristicResult(
            score=80.0,
            confidence=0.8,
            data_completeness=DataCompleteness.PARTIAL_NO_COMMENTS, # Even with partial data
            signals={"bot_probability": 0.0}
        )
        
        result = await refiner.refine(heuristic, [], "English")
        
        self.assertEqual(result.adjustment, -10)
        self.assertEqual(result.refined_score, 70.0)

if __name__ == '__main__':
    unittest.main()
