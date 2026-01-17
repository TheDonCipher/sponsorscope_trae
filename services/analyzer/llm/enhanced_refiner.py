"""
Enhanced AuthenticityRefiner with Integrated Boundary Auditing

This module extends the existing AuthenticityRefiner to include comprehensive
boundary auditing capabilities, ensuring LLM refinements comply with safety
guidelines while maintaining epistemic integrity.
"""

import json
import logging
import asyncio
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime

from shared.schemas.domain import DataCompleteness
from services.analyzer.heuristics.types import HeuristicResult
from .types import LLMRefinementResult
from .prompts.authenticity import AUTHENTICITY_SYSTEM_PROMPT
from .calibration import calibrate_confidence
from .vertex_client import VertexAIGeminiClient
from .boundary_auditor import AIRefinementBoundaryAuditor, BoundaryAuditRecord

logger = logging.getLogger(__name__)


class EnhancedAuthenticityRefiner:
    """
    Enhanced Authenticity Refiner with integrated boundary auditing.
    
    This class extends the original AuthenticityRefiner to include:
    - Real-time boundary auditing during refinement
    - Comprehensive violation detection and reporting
    - Statistical analysis of refinement patterns
    - Integration with monitoring and alerting systems
    """
    
    def __init__(
        self, 
        model_client=None, 
        vertex_config: Optional[Dict[str, Any]] = None,
        boundary_auditor: Optional[AIRefinementBoundaryAuditor] = None,
        audit_callback: Optional[Callable[[BoundaryAuditRecord], None]] = None,
        enable_monitoring: bool = True
    ):
        """
        Initialize the enhanced refiner with boundary auditing capabilities.
        
        Args:
            model_client: Optional existing client for testing
            vertex_config: Configuration for Vertex AI (project_id, location, etc.)
            boundary_auditor: Optional custom boundary auditor instance
            audit_callback: Optional callback for audit results
            enable_monitoring: Whether to enable real-time monitoring
        """
        if model_client:
            self.client = model_client
        elif vertex_config:
            self.client = VertexAIGeminiClient(**vertex_config)
        else:
            # Fallback to mock client for testing
            self.client = None
            
        self.max_adjustment = 15.0
        self.boundary_auditor = boundary_auditor or AIRefinementBoundaryAuditor(adjustment_boundary=self.max_adjustment)
        self.audit_callback = audit_callback
        self.enable_monitoring = enable_monitoring
        
        # Statistical tracking
        self.refinement_stats = {
            "total_refinements": 0,
            "boundary_violations": 0,
            "average_adjustment": 0.0,
            "average_confidence_delta": 0.0,
            "last_violation": None,
            "violation_history": []
        }
        
        logger.info(f"EnhancedAuthenticityRefiner initialized with boundary auditing (±{self.max_adjustment})")
    
    async def refine(
        self, 
        heuristic_result: HeuristicResult, 
        comments: List[str], 
        context: str = "English",
        handle: str = "unknown",
        platform: str = "unknown"
    ) -> LLMRefinementResult:
        """
        Refine authenticity score with integrated boundary auditing.
        
        Args:
            heuristic_result: Base heuristic scoring result
            comments: Sample comments for analysis
            context: Language/cultural context
            handle: Social media handle being analyzed
            platform: Platform (Instagram, TikTok, etc.)
            
        Returns:
            LLMRefinementResult with boundary audit information
        """
        
        self.refinement_stats["total_refinements"] += 1
        
        try:
            # 1. Perform original refinement logic
            refinement_result = await self._perform_refinement(
                heuristic_result, comments, context
            )
            
            # 2. Perform boundary audit
            audit_record = self.boundary_auditor.audit_refinement(
                heuristic_result=heuristic_result,
                refinement_result=refinement_result,
                handle=handle,
                platform=platform,
                sample_content=comments
            )
            
            # 3. Update statistics
            self._update_refinement_stats(audit_record)
            
            # 4. Handle audit callback if provided
            if self.audit_callback and self.enable_monitoring:
                try:
                    await self.audit_callback(audit_record)
                except Exception as e:
                    logger.error(f"Audit callback failed: {str(e)}")
            
            # 5. Log audit results
            if audit_record.boundary_violations:
                logger.warning(
                    f"Boundary violations detected for {handle} on {platform}: "
                    f"{[v.value for v in audit_record.boundary_violations]}"
                )
            else:
                logger.info(
                    f"Refinement compliant for {handle} on {platform}: "
                    f"score {heuristic_result.score} -> {refinement_result.refined_score} "
                    f"(adj: {refinement_result.adjustment})"
                )
            
            # 6. Return enhanced result with audit information
            enhanced_result = LLMRefinementResult(
                refined_score=refinement_result.refined_score,
                adjustment=refinement_result.adjustment,
                explanation=refinement_result.explanation,
                confidence=refinement_result.confidence,
                flags=refinement_result.flags + [f"audit_score:{audit_record.audit_score}"]
            )
            
            # Store audit reference for later retrieval
            enhanced_result._audit_record = audit_record
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Enhanced refinement failed for {handle}: {str(e)}")
            # Fallback to original refinement logic
            return await self._perform_refinement(heuristic_result, comments, context)
    
    async def _perform_refinement(
        self, 
        heuristic_result: HeuristicResult, 
        comments: List[str], 
        context: str
    ) -> LLMRefinementResult:
        """
        Perform the original refinement logic (extracted from AuthenticityRefiner).
        
        Args:
            heuristic_result: Base heuristic scoring result
            comments: Sample comments for analysis
            context: Language/cultural context
            
        Returns:
            LLMRefinementResult with refinement details
        """
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
        
        # 2. Call LLM with timeout and error handling
        try:
            response = await self._call_llm_with_timeout(AUTHENTICITY_SYSTEM_PROMPT, json.dumps(prompt_payload))
        except TimeoutError as e:
            logger.error(f"Gemini timeout: {str(e)}")
            return self._create_fallback_result(heuristic_result, "Gemini timeout", ["llm_timeout"])
        except Exception as e:
            logger.error(f"Gemini error: {str(e)}")
            return self._create_fallback_result(heuristic_result, f"Gemini error: {str(e)}", ["llm_error"])
        
        # 3. Parse & Validate
        try:
            parsed = json.loads(response)
            adjustment = int(parsed.get("adjustment", 0))
            reason = parsed.get("reason", "No reason provided")
            flags = parsed.get("flags", [])
        except json.JSONDecodeError:
            logger.error("Failed to parse Gemini JSON response")
            return self._create_fallback_result(heuristic_result, "LLM JSON Parse Error", ["llm_error"])
            
        # 4. Apply Bounded Refinement Rules
        monotonic_safety_applied = False
        
        # Rule: Max adjustment +/- 15
        adjustment = max(min(adjustment, self.max_adjustment), -self.max_adjustment)
        
        # Rule: Monotonic Safety - Raise only if FULL data
        if adjustment > 0 and heuristic_result.data_completeness != DataCompleteness.FULL:
            adjustment = 0
            reason += " (Adjustment suppressed due to partial data)"
            flags.append("monotonic_safety_applied")
            monotonic_safety_applied = True
            
        # Rule: Bot Floor Respect
        bot_prob = heuristic_result.signals.get("bot_probability", 0.0)
        if adjustment > 0 and bot_prob > 0.8:
            adjustment = 0
            reason += " (Adjustment suppressed due to high bot probability floor)"
            flags.append("bot_floor_respected")
            
        final_score = max(0.0, min(100.0, heuristic_result.score + adjustment))
        
        # 5. Calibrate Confidence based on LLM agreement and safety rules
        # Consistency: 1.0 if adj=0, 0.5 if adj=15
        consistency = 1.0 - (abs(adjustment) / 30.0) # Simple linear decay
        
        final_confidence = calibrate_confidence(
            heuristic_result.confidence,
            consistency,
            heuristic_result.data_completeness,
            monotonic_safety_applied=monotonic_safety_applied,
            llm_error_occurred=False
        )
        
        logger.info(f"Gemini refinement: score {heuristic_result.score} -> {final_score} (adj: {adjustment}), confidence: {final_confidence}")
        
        return LLMRefinementResult(
            refined_score=final_score,
            adjustment=adjustment,
            explanation=reason,
            confidence=final_confidence,
            flags=flags
        )
    
    async def _call_llm_with_timeout(self, system_prompt: str, user_prompt: str) -> str:
        """Call LLM with timeout handling."""
        if self.client:
            return await self.client.generate_content(system_prompt, user_prompt)
        else:
            # Fallback to deterministic simulation for testing
            return await self._simulate_llm_response(user_prompt)
    
    async def _simulate_llm_response(self, user_prompt: str) -> str:
        """Deterministic simulation for testing."""
        import hashlib
        seed = int(hashlib.sha256(user_prompt.encode('utf-8')).hexdigest(), 16)
        
        # Simulate different AI findings
        scenarios = [
            {"adj": -10, "reason": "Detected high density of generic 'nice pic' comments indicating potential bot activity.", "flag": "bot_cluster_detected"},
            {"adj": -5, "reason": "Engagement patterns show signs of engagement pod participation (reciprocal grouping).", "flag": "pod_activity_suspected"},
            {"adj": 0, "reason": "Audience interactions appear organic and consistent with vertical benchmarks.", "flag": []},
            {"adj": 0, "reason": "Sentiment analysis confirms neutral-to-positive human engagement.", "flag": []},
            {"adj": 5, "reason": "High-value comments detected with specific contextual relevance to the content.", "flag": "high_quality_audience"},
            {"adj": 8, "reason": "Exceptional audience resonance indicated by detailed testimonial-style comments.", "flag": "superfan_activity"}
        ]
        
        scenario = scenarios[seed % len(scenarios)]
        
        return json.dumps({
            "adjustment": scenario["adj"],
            "reason": scenario["reason"],
            "flags": [scenario["flag"]] if scenario["flag"] else []
        })
    
    def _create_fallback_result(
        self, 
        heuristic_result: HeuristicResult, 
        explanation: str, 
        flags: List[str]
    ) -> LLMRefinementResult:
        """Create fallback result when LLM refinement fails."""
        lowered_confidence = calibrate_confidence(
            heuristic_result.confidence,
            llm_consistency_score=0.3,  # Low consistency due to error
            data_completeness=heuristic_result.data_completeness,
            monotonic_safety_applied=False,
            llm_error_occurred=True
        )
        
        return LLMRefinementResult(
            refined_score=heuristic_result.score,
            adjustment=0,
            explanation=explanation,
            confidence=lowered_confidence,
            flags=flags
        )
    
    def _update_refinement_stats(self, audit_record: BoundaryAuditRecord):
        """Update statistical tracking based on audit results."""
        
        # Update violation tracking
        if audit_record.boundary_violations:
            self.refinement_stats["boundary_violations"] += 1
            self.refinement_stats["violation_history"].append({
                "timestamp": audit_record.timestamp.isoformat(),
                "handle": audit_record.handle,
                "violations": [v.value for v in audit_record.boundary_violations],
                "audit_score": audit_record.audit_score
            })
            
            # Keep only recent violations (last 100)
            if len(self.refinement_stats["violation_history"]) > 100:
                self.refinement_stats["violation_history"] = self.refinement_stats["violation_history"][-100:]
        
        # Update running averages
        total_refinements = self.refinement_stats["total_refinements"]
        current_avg_adj = self.refinement_stats["average_adjustment"]
        current_avg_conf = self.refinement_stats["average_confidence_delta"]
        
        new_adj = audit_record.adjustment_delta
        new_conf_delta = audit_record.confidence_delta
        
        # Update running averages using incremental formula
        self.refinement_stats["average_adjustment"] = (
            (current_avg_adj * (total_refinements - 1) + new_adj) / total_refinements
        )
        self.refinement_stats["average_confidence_delta"] = (
            (current_avg_conf * (total_refinements - 1) + new_conf_delta) / total_refinements
        )
    
    def get_refinement_statistics(self) -> Dict[str, Any]:
        """Get current refinement statistics."""
        return {
            "total_refinements": self.refinement_stats["total_refinements"],
            "boundary_violations": self.refinement_stats["boundary_violations"],
            "violation_rate": (
                self.refinement_stats["boundary_violations"] / 
                max(1, self.refinement_stats["total_refinements"])
            ),
            "average_adjustment": self.refinement_stats["average_adjustment"],
            "average_confidence_delta": self.refinement_stats["average_confidence_delta"],
            "recent_violations": self.refinement_stats["violation_history"][-10:],  # Last 10
            "audit_summary": self.boundary_auditor.generate_audit_summary()
        }
    
    def get_boundary_auditor(self) -> AIRefinementBoundaryAuditor:
        """Get the underlying boundary auditor instance."""
        return self.boundary_auditor
    
    def reset_statistics(self):
        """Reset refinement statistics."""
        self.refinement_stats = {
            "total_refinements": 0,
            "boundary_violations": 0,
            "average_adjustment": 0.0,
            "average_confidence_delta": 0.0,
            "last_violation": None,
            "violation_history": []
        }
        logger.info("Refinement statistics reset")