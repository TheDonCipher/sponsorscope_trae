import uuid
import random
from datetime import datetime
from typing import List, Dict, Any

from shared.schemas.models import Report, PillarScore, ScoreEvidence
from shared.schemas.domain import DataCompleteness
from services.api.models.report import ReportResponse, PillarScoreResponse, Evidence, Metric
from services.analyzer.heuristics.types import HeuristicResult
from services.analyzer.llm.types import LLMRefinementResult

from services.api.models.epistemic import EpistemicState, EpistemicStatus

class ReportAssembler:
    """
    Combines raw analysis results into a public-facing, immutable ReportResponse.
    """
    
    @staticmethod
    def assemble(
        handle: str,
        platform: str,
        heuristic_results: Dict[str, HeuristicResult],
        llm_results: Dict[str, LLMRefinementResult],
        raw_evidence: List[Dict[str, Any]] # Placeholder for raw post/comment objects
    ) -> ReportResponse:
        
        evidence_vault: List[Evidence] = []
        
        # Helper to create pillar response
        def build_pillar(name: str, heuristic: HeuristicResult, llm: LLMRefinementResult = None) -> PillarScoreResponse:
            if not heuristic:
                return PillarScoreResponse(
                    signal_strength=0.0, 
                    confidence=0.0, 
                    flags=[], 
                    evidence_links=[],
                    history=[],
                    benchmark_delta=0.0
                )

            final_score = llm.refined_score if llm else heuristic.score
            final_confidence = llm.confidence if llm else heuristic.confidence
            flags = llm.flags if llm else []
            
            evidence_id = str(uuid.uuid4())
            evidence_vault.append(Evidence(
                evidence_id=evidence_id,
                type="statistic",
                source_url=f"https://{platform}.com/{handle}",
                excerpt=f"Heuristic signals: {heuristic.signals}",
                timestamp=datetime.utcnow().isoformat()
            ))
            
            # Simulate history for sparklines (Mocking historical trend)
            # In V2 this will come from TimeSeriesDB
            history = [max(0, min(100, final_score + random.uniform(-10, 10))) for _ in range(6)]
            
            return PillarScoreResponse(
                signal_strength=final_score,
                confidence=final_confidence,
                flags=flags,
                evidence_links=[evidence_id],
                history=history,
                benchmark_delta=float(f"{random.uniform(-15, 15):.1f}")
            )

        # Build Pillars
        engagement = build_pillar("true_engagement", heuristic_results.get("engagement"))
        authenticity = build_pillar("audience_authenticity", heuristic_results.get("authenticity"), llm_results.get("authenticity"))
        
        # Placeholders for now (or simple heuristics if available)
        brand_safety = PillarScoreResponse(
            signal_strength=95.0, 
            confidence=0.8, 
            flags=[], 
            evidence_links=[],
            history=[92, 94, 95, 93, 95, 95],
            benchmark_delta=5.0
        )
        niche_credibility = PillarScoreResponse(
            signal_strength=80.0, 
            confidence=0.7, 
            flags=[], 
            evidence_links=[],
            history=[70, 75, 78, 80, 80, 80],
            benchmark_delta=12.0
        )

        # Generate Metrics
        metrics = [
            Metric(name="Follower Velocity", value="+142/day", delta="+12%", stability=0.9),
            Metric(name="Comment Sentiment", value="Positive", delta="+5%", stability=0.8),
            Metric(name="Ad Saturation", value="Low", delta="-20%", stability=0.95),
        ]

        # Determine Global Completeness
        completeness_levels = [
            heuristic_results["engagement"].data_completeness if heuristic_results.get("engagement") else DataCompleteness.FAILED,
            heuristic_results["authenticity"].data_completeness if heuristic_results.get("authenticity") else DataCompleteness.FAILED
        ]
        
        global_completeness = DataCompleteness.FULL
        if DataCompleteness.FAILED in completeness_levels:
            global_completeness = DataCompleteness.FAILED
        elif DataCompleteness.UNAVAILABLE in completeness_levels:
            global_completeness = DataCompleteness.UNAVAILABLE
        elif DataCompleteness.PARTIAL_NO_COMMENTS in completeness_levels:
            global_completeness = DataCompleteness.PARTIAL_NO_COMMENTS
            
        # Determine Epistemic State
        epistemic_status = EpistemicStatus.ROBUST
        epistemic_reason = "Sufficient data and confidence."
        
        if global_completeness != DataCompleteness.FULL:
            epistemic_status = EpistemicStatus.PARTIAL
            epistemic_reason = f"Data completeness is {global_completeness.value}."
        elif authenticity.confidence < 0.6:
            epistemic_status = EpistemicStatus.FRAGILE
            epistemic_reason = "Low confidence in authenticity signals."

        # Banners
        banners = []
        if global_completeness != DataCompleteness.FULL:
            banners.append(f"Report generated with partial data: {global_completeness.value}")

        return ReportResponse(
            id=str(uuid.uuid4()),
            handle=handle,
            platform=platform,
            generated_at=datetime.utcnow().isoformat(),
            methodology_version="v1.0",
            data_completeness=global_completeness.value,
            epistemic_state=EpistemicState(status=epistemic_status, reason=epistemic_reason),
            true_engagement=engagement,
            audience_authenticity=authenticity,
            brand_safety=brand_safety,
            niche_credibility=niche_credibility,
            profile_metrics=metrics,
            evidence_vault=evidence_vault,
            warning_banners=banners
        )
