import uuid
from datetime import datetime
from typing import List, Dict, Any

from shared.schemas.models import Report, PillarScore, ScoreEvidence
from shared.schemas.domain import DataCompleteness
from services.api.models.report import ReportResponse, PillarScoreResponse, Evidence
from services.analyzer.heuristics.types import HeuristicResult
from services.analyzer.llm.types import LLMRefinementResult

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
            final_score = llm.refined_score if llm else heuristic.score
            final_confidence = llm.confidence if llm else heuristic.confidence
            flags = llm.flags if llm else []
            
            # Link Evidence
            # For MVP, we just create a generic evidence item linked to the score
            evidence_id = str(uuid.uuid4())
            evidence_vault.append(Evidence(
                evidence_id=evidence_id,
                type="statistic",
                source_url=f"https://{platform}.com/{handle}", # Simplified
                excerpt=f"Heuristic signals: {heuristic.signals}",
                timestamp=datetime.utcnow().isoformat()
            ))
            
            return PillarScoreResponse(
                score=final_score,
                confidence=final_confidence,
                flags=flags,
                evidence_links=[evidence_id]
            )

        # Build Pillars
        engagement = build_pillar("true_engagement", heuristic_results["engagement"])
        authenticity = build_pillar("audience_authenticity", heuristic_results["authenticity"], llm_results.get("authenticity"))
        # Brand Safety placeholder (assuming it comes from LLM mostly)
        brand_safety = PillarScoreResponse(
            score=0.0, confidence=0.0, flags=[], evidence_links=[] # TODO: Implement Brand Safety pipeline
        )

        # Determine Global Completeness
        # Worst case wins
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
            true_engagement=engagement,
            audience_authenticity=authenticity,
            brand_safety=brand_safety,
            evidence_vault=evidence_vault,
            warning_banners=banners
        )
