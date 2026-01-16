from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from ..schemas.raw import RawProfile
from ..schemas.models import PillarScore, MethodologyMetadata

class ScoringContract(ABC):
    """
    Base contract for all scoring logic in SponsorScope.
    Ensures that inputs, outputs, and determinism are explicitly declared.
    """
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Version of this specific scoring algorithm."""
        pass
    
    @property
    @abstractmethod
    def required_inputs(self) -> List[str]:
        """List of required data fields (e.g., 'comments', 'likes')."""
        pass
        
    @property
    @abstractmethod
    def output_range(self) -> Tuple[float, float]:
        """Min and max possible values for this score."""
        pass
        
    @property
    @abstractmethod
    def is_deterministic(self) -> bool:
        """
        True if the same input always yields the exact same output.
        Heuristics MUST be True. LLM Refiners might be False (or quasi-deterministic).
        """
        pass

class HeuristicScorer(ScoringContract):
    """
    Contract for deterministic, rule-based scoring.
    """
    
    @abstractmethod
    def calculate(self, profile: RawProfile) -> PillarScore:
        """
        Pure function to calculate score based on raw data.
        MUST NOT make external API calls.
        """
        pass

class LLMRefiner(ScoringContract):
    """
    Contract for LLM-based score refinement.
    """
    
    @abstractmethod
    async def refine(self, current_score: PillarScore, profile: RawProfile, context: Dict[str, Any]) -> PillarScore:
        """
        Refines an existing heuristic score using LLM analysis.
        """
        pass
