"""
LLM-assisted Brand Safety Scoring Module

This module provides contextual risk detection for brand safety analysis using LLM.
It detects hate speech, sexual content, violence, and other contextual risks while
considering cultural slang and sarcasm. Always uses graded risk language and provides
evidence-based scoring.
"""

import json
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime

from shared.schemas.domain import DataCompleteness
from shared.schemas.raw import RawComment, RawPost
from services.analyzer.llm.types import BrandSafetyResult
from services.analyzer.llm.prompts.brand_safety import BRAND_SAFETY_SYSTEM_PROMPT


class BrandSafetyAnalyzer:
    """
    LLM-assisted brand safety analyzer that detects contextual risks in social media content.
    
    Key Features:
    - Detects hate speech, harassment, sexual content, violence, illegal activities
    - Considers cultural slang and sarcasm in risk assessment
    - Uses graded risk language (never labels as "unsafe")
    - Provides evidence-based scoring with traceable evidence_ids
    - Handles multiple content types: captions, comments, OCR text
    """
    
    def __init__(self, model_client=None):
        """
        Initialize the brand safety analyzer.
        
        Args:
            model_client: Optional LLM client for production use. If None, uses deterministic simulation.
        """
        self.client = model_client
        self.risk_categories = {
            "hate_speech": "Content promoting hatred against protected groups",
            "harassment": "Targeted abuse or bullying behavior",
            "sexual_content": "Explicit or suggestive sexual content",
            "violence": "Graphic violence or dangerous acts",
            "illegal_drugs": "Promotion of illegal substances",
            "political_extremism": "Extremist political content",
            "scam_fraud": "Deceptive or fraudulent content",
            "cultural_insensitivity": "Content offensive to cultural groups"
        }
        
    async def analyze_content(
        self,
        post: RawPost,
        comments: List[RawComment],
        ocr_text: Optional[str] = None,
        fallback_mode: Optional[str] = None
    ) -> BrandSafetyResult:
        """
        Analyze post content for brand safety risks using LLM assistance.
        
        Args:
            post: The main post content to analyze
            comments: List of comments associated with the post
            ocr_text: Optional OCR text extracted from images
            fallback_mode: "text_only" if images are missing
            
        Returns:
            BrandSafetyResult with graded risk assessment and evidence
        """
        # Prepare content for analysis
        content_data = self._prepare_content_data(post, comments, ocr_text, fallback_mode)
        
        # Call LLM for analysis
        llm_response = await self._call_llm(BRAND_SAFETY_SYSTEM_PROMPT, json.dumps(content_data))
        
        # Parse and validate LLM response
        try:
            parsed_response = json.loads(llm_response)
            return self._create_brand_safety_result(parsed_response, content_data)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Fallback to safe defaults on parsing errors
            return self._create_fallback_result(f"LLM parsing error: {str(e)}", content_data)
    
    def _prepare_content_data(
        self,
        post: RawPost,
        comments: List[RawComment],
        ocr_text: Optional[str] = None,
        fallback_mode: Optional[str] = None
    ) -> Dict[str, Any]:
        """Prepare content data for LLM analysis."""
        return {
            "caption": post.caption or "",
            "comments": [
                {
                    "text": comment.text,
                    "like_count": comment.like_count,
                    "timestamp": comment.timestamp.isoformat()
                }
                for comment in comments[:20]  # Limit context window
            ],
            "ocr_text": ocr_text or "",
            "fallback_mode": fallback_mode or "full_content",
            "platform": post.platform.value,
            "engagement_metrics": {
                "like_count": post.like_count,
                "comment_count": post.comment_count,
                "share_count": post.share_count or 0
            }
        }
    
    async def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        Abstracted LLM call. In production, this calls Vertex AI or similar.
        For now, returns deterministic simulation based on content analysis.
        """
        if self.client:
            return await self.client.generate_content(system_prompt, user_prompt)
        
        # Deterministic simulation based on content analysis
        return self._simulate_llm_analysis(user_prompt)
    
    def _simulate_llm_analysis(self, content_json: str) -> str:
        """
        Simulate LLM analysis with deterministic risk detection based on content.
        This provides realistic testing without actual LLM calls.
        """
        # Create hash-based seed for deterministic results
        seed = int(hashlib.sha256(content_json.encode('utf-8')).hexdigest(), 16)
        
        # Define risk patterns for simulation
        high_risk_patterns = [
            ("hate", ["hate", "kill", "destroy", "die", "worthless"]),
            ("sexual", ["sex", "nude", "naked", "porn", "explicit"]),
            ("violence", ["violence", "fight", "attack", "weapon", "blood"]),
            ("drugs", ["drug", "cocaine", "heroin", "weed", "high"]),
            ("scam", ["scam", "fraud", "fake", "money", "quick rich"])
        ]
        
        medium_risk_patterns = [
            ("harassment", ["stupid", "idiot", "loser", "ugly", "dumb"]),
            ("cultural", ["racist", "discrimination", "offensive", "insensitive"]),
            ("political", ["extremist", "radical", "terrorist", "revolution"])
        ]
        
        # Analyze content for risk patterns
        content_lower = content_json.lower()
        detected_risks = []
        risk_score = 0
        
        # Check for high-risk patterns
        for risk_type, patterns in high_risk_patterns:
            for pattern in patterns:
                if pattern in content_lower:
                    detected_risks.append(risk_type)
                    risk_score += 25
                    break
        
        # Check for medium-risk patterns
        for risk_type, patterns in medium_risk_patterns:
            for pattern in patterns:
                if pattern in content_lower:
                    detected_risks.append(risk_type)
                    risk_score += 15
                    break
        
        # Cap risk score at 100
        risk_score = min(risk_score, 100)
        
        # Determine grade based on risk score
        if risk_score >= 80:
            grade = "F"
        elif risk_score >= 60:
            grade = "D"
        elif risk_score >= 40:
            grade = "C"
        elif risk_score >= 20:
            grade = "B"
        else:
            grade = "A"
        
        # Generate evidence-based explanation
        if detected_risks:
            explanation = f"Detected elevated risk indicators: {', '.join(detected_risks)}. "
            if risk_score >= 60:
                explanation += "Content shows significant brand safety concerns with multiple risk factors."
            elif risk_score >= 30:
                explanation += "Content contains moderate risk elements that may require brand consideration."
            else:
                explanation += "Content shows minor risk indicators within acceptable thresholds."
        else:
            explanation = "Content analysis reveals no significant brand safety risks. Safe for brand association."
        
        return json.dumps({
            "grade": grade,
            "risk_score": float(risk_score),
            "flags": detected_risks,
            "explanation": explanation
        })
    
    def _create_brand_safety_result(
        self,
        llm_response: Dict[str, Any],
        content_data: Dict[str, Any]
    ) -> BrandSafetyResult:
        """Create BrandSafetyResult from LLM response with evidence tracking."""
        # Validate grade format
        grade = llm_response.get("grade", "A")
        if not self._is_valid_grade(grade):
            grade = "A"  # Default to safe grade on validation error
        
        # Validate risk score range
        risk_score = float(llm_response.get("risk_score", 0.0))
        risk_score = max(0.0, min(100.0, risk_score))
        
        # Get flags and ensure they're valid
        flags = llm_response.get("flags", [])
        if not isinstance(flags, list):
            flags = []
        
        # Generate evidence IDs for traceability
        evidence_ids = self._generate_evidence_ids(content_data, flags)
        
        # Create explanation with evidence references
        explanation = llm_response.get("explanation", "No explanation provided")
        if evidence_ids:
            explanation += f" Evidence available in vault: {', '.join(evidence_ids)}"
        
        return BrandSafetyResult(
            grade=grade,
            risk_score=risk_score,
            flags=flags,
            confidence=self._calculate_confidence(risk_score, len(flags)),
            explanation=explanation,
            fallback_mode=content_data.get("fallback_mode")
        )
    
    def _create_fallback_result(self, error_message: str, content_data: Dict[str, Any]) -> BrandSafetyResult:
        """Create safe fallback result when LLM analysis fails."""
        return BrandSafetyResult(
            grade="A",  # Default to safest grade
            risk_score=0.0,
            flags=["analysis_error"],
            confidence=0.3,  # Low confidence due to error
            explanation=f"Brand safety analysis failed: {error_message}. Defaulting to safe grade.",
            fallback_mode=content_data.get("fallback_mode")
        )
    
    def _is_valid_grade(self, grade: str) -> bool:
        """Validate grade format (A-F with optional +/-)."""
        import re
        return bool(re.match(r"^[A-F][+-]?$", grade))
    
    def _generate_evidence_ids(self, content_data: Dict[str, Any], flags: List[str]) -> List[str]:
        """Generate evidence IDs for traceability to evidence vault."""
        evidence_ids = []
        
        # Create hash-based evidence IDs for content
        content_hash = hashlib.sha256(json.dumps(content_data, sort_keys=True).encode()).hexdigest()[:8]
        
        for flag in flags:
            evidence_id = f"bs_{flag}_{content_hash}_{int(datetime.now().timestamp())}"
            evidence_ids.append(evidence_id)
        
        return evidence_ids
    
    def _calculate_confidence(self, risk_score: float, flag_count: int) -> float:
        """Calculate confidence score based on analysis completeness."""
        # Base confidence starts high
        confidence = 0.85
        
        # Reduce confidence if no flags detected but moderate risk score
        if flag_count == 0 and risk_score > 30:
            confidence *= 0.8
        
        # Reduce confidence for very high or very low risk scores
        if risk_score > 80 or risk_score < 10:
            confidence *= 0.9
        
        return round(confidence, 2)