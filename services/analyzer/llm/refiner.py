import json
from typing import List, Dict, Any, Optional
from shared.schemas.domain import DataCompleteness
from shared.contracts.scoring import LLMRefiner, PillarScore
from shared.schemas.raw import RawProfile
from services.analyzer.heuristics.types import HeuristicResult
from .types import LLMRefinementResult
from .prompts.authenticity import AUTHENTICITY_SYSTEM_PROMPT
from .calibration import calibrate_confidence

class AuthenticityRefiner:
    """
    Refines Audience Authenticity scores using Vertex AI Gemini.
    """
    
    def __init__(self, model_client=None):
        self.client = model_client # Injected for testing
        self.max_adjustment = 15.0
        
    async def refine(
        self, 
        heuristic_result: HeuristicResult, 
        comments: List[str], 
        context: str = "English"
    ) -> LLMRefinementResult:
        
        # 1. Prepare Prompt
        prompt_payload = {
            "heuristic_score": heuristic_result.score,
            "bot_probability_floor": heuristic_result.signals.get("bot_probability", 0.0),
            "signals": {
                "entropy": heuristic_result.signals.get("entropy"),
                "uniqueness": heuristic_result.signals.get("uniqueness"),
                "variance": heuristic_result.signals.get("variance")
            },
            "sample_comments": comments[:50], # Limit context window
            "language_context": context,
            "data_completeness": heuristic_result.data_completeness.value
        }
        
        # 2. Call LLM (Mocked/Abstracted)
        response = await self._call_llm(AUTHENTICITY_SYSTEM_PROMPT, json.dumps(prompt_payload))
        
        # 3. Parse & Validate
        try:
            parsed = json.loads(response)
            adjustment = int(parsed.get("adjustment", 0))
            reason = parsed.get("reason", "No reason provided")
            flags = parsed.get("flags", [])
        except json.JSONDecodeError:
            # Fail safe
            return LLMRefinementResult(
                refined_score=heuristic_result.score,
                adjustment=0,
                explanation="LLM JSON Parse Error",
                confidence=heuristic_result.confidence,
                flags=["llm_error"]
            )
            
        # 4. Apply Rules
        # Rule: Max adjustment +/- 15
        adjustment = max(min(adjustment, self.max_adjustment), -self.max_adjustment)
        
        # Rule: Monotonic Safety - Raise only if FULL data
        if adjustment > 0 and heuristic_result.data_completeness != DataCompleteness.FULL:
            adjustment = 0
            reason += " (Adjustment suppressed due to partial data)"
            
        # Rule: Bot Floor Respect
        bot_prob = heuristic_result.signals.get("bot_probability", 0.0)
        if adjustment > 0 and bot_prob > 0.8:
            adjustment = 0
            reason += " (Adjustment suppressed due to high bot probability floor)"
            
        final_score = max(0.0, min(100.0, heuristic_result.score + adjustment))
        
        # 5. Calibrate Confidence
        # Consistency: 1.0 if adj=0, 0.5 if adj=15
        consistency = 1.0 - (abs(adjustment) / 30.0) # Simple linear decay
        
        final_confidence = calibrate_confidence(
            heuristic_result.confidence,
            consistency,
            heuristic_result.data_completeness
        )
        
        return LLMRefinementResult(
            refined_score=final_score,
            adjustment=adjustment,
            explanation=reason,
            confidence=final_confidence,
            flags=flags
        )
        
    async def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        Abstracted LLM call. In production, this calls Vertex AI.
        For now, returns a mock if client is None.
        """
        if self.client:
            return await self.client.generate_content(system_prompt, user_prompt)
        
        # Default mock response for dev/test without client
        return json.dumps({
            "adjustment": 0,
            "reason": "Mock response: No significant signal found.",
            "flags": []
        })
