import uuid
from datetime import datetime
from typing import List, Dict, Any

from shared.schemas.models import Report, PillarScore, ScoreEvidence
from shared.schemas.domain import DataCompleteness
from services.api.models.report import ReportResponse, PillarScoreResponse, Evidence
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
        
        # ... (Previous pillar logic) ...

        # Helper to create pillar response
        def build_pillar(name: str, heuristic: HeuristicResult, llm: LLMRefinementResult = None) -> PillarScoreResponse:
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
            
            return PillarScoreResponse(
                signal_strength=final_score,
                confidence=final_confidence,
                flags=flags,
                evidence_links=[evidence_id]
            )

        # Build Pillars
        engagement = build_pillar("true_engagement", heuristic_results["engagement"])
        authenticity = build_pillar("audience_authenticity", heuristic_results["authenticity"], llm_results.get("authenticity"))
        brand_safety = PillarScoreResponse(
            signal_strength=0.0, confidence=0.0, flags=[], evidence_links=[]
        )

        # Determine Global Completeness
        completeness_levels = [
            heuristic_results["engagement"].data_completeness,
            heuristic_results["authenticity"].data_completeness
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
            evidence_vault=evidence_vault,
            warning_banners=banners
        )
