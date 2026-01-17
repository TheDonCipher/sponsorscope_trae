import asyncio
import json
import pytest
from unittest.mock import Mock, AsyncMock
from typing import List, Dict, Any

from services.analyzer.llm.refiner import AuthenticityRefiner
from services.analyzer.llm.vertex_client import VertexAIGeminiClient
from services.analyzer.llm.config import VertexAIConfig
from services.analyzer.heuristics.types import HeuristicResult
from shared.schemas.domain import DataCompleteness


class TestVertexAIGeminiIntegration:
    """
    Test suite for Vertex AI Gemini integration with bounded refinement.
    """
    
    @pytest.fixture
    def mock_heuristic_result(self):
        """Create a mock heuristic result for testing."""
        return HeuristicResult(
            score=75.0,
            raw_value=0.75,
            confidence=0.8,
            data_completeness=DataCompleteness.FULL,
            signals={
                "bot_probability": 0.2,
                "entropy": 0.85,
                "uniqueness": 0.9,
                "variance": 0.7
            }
        )
    
    @pytest.fixture
    def sample_comments(self):
        """Sample comments for testing."""
        return [
            "Love this content! So inspiring 🌟",
            "Great post, really helpful information",
            "Amazing work, keep it up!",
            "This is exactly what I needed to hear today",
            "Your content always makes my day better"
        ]
    
    @pytest.fixture
    def mock_vertex_client(self):
        """Create a mock Vertex AI client."""
        client = Mock(spec=VertexAIGeminiClient)
        
        # Mock successful response
        async def mock_generate_content(system_prompt, user_prompt, **kwargs):
            return json.dumps({
                "adjustment": 5,
                "reason": "High-quality engagement detected with contextual relevance",
                "flags": ["high_quality_audience"]
            })
        
        client.generate_content = AsyncMock(side_effect=mock_generate_content)
        client.health_check = AsyncMock(return_value=True)
        return client
    
    @pytest.fixture
    def timeout_vertex_client(self):
        """Create a mock client that times out."""
        client = Mock(spec=VertexAIGeminiClient)
        
        async def mock_timeout(*args, **kwargs):
            raise asyncio.TimeoutError("Request timed out")
        
        client.generate_content = AsyncMock(side_effect=mock_timeout)
        return client
    
    @pytest.fixture
    def error_vertex_client(self):
        """Create a mock client that raises errors."""
        client = Mock(spec=VertexAIGeminiClient)
        
        async def mock_error(*args, **kwargs):
            raise Exception("API Error")
        
        client.generate_content = AsyncMock(side_effect=mock_error)
        return client
    
    @pytest.mark.asyncio
    async def test_successful_refinement(self, mock_heuristic_result, sample_comments, mock_vertex_client):
        """Test successful refinement with Vertex AI."""
        refiner = AuthenticityRefiner(model_client=mock_vertex_client)
        
        result = await refiner.refine(
            heuristic_result=mock_heuristic_result,
            comments=sample_comments,
            context="English"
        )
        
        assert result.refined_score == 80.0  # 75 + 5
        assert result.adjustment == 5
        assert "High-quality engagement" in result.explanation
        assert "high_quality_audience" in result.flags
        assert result.confidence < 0.8  # Confidence should be calibrated down
    
    @pytest.mark.asyncio
    async def test_monotonic_safety_partial_data(self, mock_heuristic_result, sample_comments, mock_vertex_client):
        """Test monotonic safety rule with partial data."""
        # Modify heuristic result to have partial data
        mock_heuristic_result.data_completeness = DataCompleteness.PARTIAL_NO_COMMENTS
        mock_heuristic_result.score = 60.0
        
        # Mock LLM response that wants to increase score
        async def mock_increase_response(system_prompt, user_prompt, **kwargs):
            return json.dumps({
                "adjustment": 10,
                "reason": "Should increase score",
                "flags": []
            })
        
        mock_vertex_client.generate_content = AsyncMock(side_effect=mock_increase_response)
        refiner = AuthenticityRefiner(model_client=mock_vertex_client)
        
        result = await refiner.refine(
            heuristic_result=mock_heuristic_result,
            comments=sample_comments,
            context="English"
        )
        
        # Score should not increase due to monotonic safety
        assert result.refined_score == 60.0  # No change
        assert result.adjustment == 0
        assert "monotonic_safety_applied" in result.flags
        assert "partial data" in result.explanation
    
    @pytest.mark.asyncio
    async def test_bot_floor_respect(self, mock_heuristic_result, sample_comments, mock_vertex_client):
        """Test bot floor respect rule."""
        # Set high bot probability
        mock_heuristic_result.signals["bot_probability"] = 0.85
        mock_heuristic_result.score = 70.0
        
        # Mock LLM response that wants to increase score
        async def mock_increase_response(system_prompt, user_prompt, **kwargs):
            return json.dumps({
                "adjustment": 8,
                "reason": "Should increase despite high bot probability",
                "flags": []
            })
        
        mock_vertex_client.generate_content = AsyncMock(side_effect=mock_increase_response)
        refiner = AuthenticityRefiner(model_client=mock_vertex_client)
        
        result = await refiner.refine(
            heuristic_result=mock_heuristic_result,
            comments=sample_comments,
            context="English"
        )
        
        # Score should not increase due to high bot probability
        assert result.refined_score == 70.0  # No change
        assert result.adjustment == 0
        assert "bot_floor_respected" in result.flags
        assert "high bot probability floor" in result.explanation
    
    @pytest.mark.asyncio
    async def test_timeout_handling(self, mock_heuristic_result, sample_comments, timeout_vertex_client):
        """Test timeout error handling."""
        refiner = AuthenticityRefiner(model_client=timeout_vertex_client)
        
        result = await refiner.refine(
            heuristic_result=mock_heuristic_result,
            comments=sample_comments,
            context="English"
        )
        
        # Should return fallback result
        assert result.refined_score == mock_heuristic_result.score  # No change
        assert result.adjustment == 0
        assert "Gemini timeout" in result.explanation
        assert "llm_timeout" in result.flags
        assert result.confidence < mock_heuristic_result.confidence  # Lowered confidence
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_heuristic_result, sample_comments, error_vertex_client):
        """Test general error handling."""
        refiner = AuthenticityRefiner(model_client=error_vertex_client)
        
        result = await refiner.refine(
            heuristic_result=mock_heuristic_result,
            comments=sample_comments,
            context="English"
        )
        
        # Should return fallback result
        assert result.refined_score == mock_heuristic_result.score  # No change
        assert result.adjustment == 0
        assert "Gemini error" in result.explanation
        assert "llm_error" in result.flags
        assert result.confidence < mock_heuristic_result.confidence  # Lowered confidence
    
    @pytest.mark.asyncio
    async def test_bounded_adjustment(self, mock_heuristic_result, sample_comments, mock_vertex_client):
        """Test that adjustments are bounded to +/- 15."""
        # Mock LLM response with extreme adjustment
        async def mock_extreme_response(system_prompt, user_prompt, **kwargs):
            return json.dumps({
                "adjustment": 25,  # Beyond bounds
                "reason": "Extreme adjustment",
                "flags": []
            })
        
        mock_vertex_client.generate_content = AsyncMock(side_effect=mock_extreme_response)
        refiner = AuthenticityRefiner(model_client=mock_vertex_client)
        
        result = await refiner.refine(
            heuristic_result=mock_heuristic_result,
            comments=sample_comments,
            context="English"
        )
        
        # Adjustment should be capped at +15
        assert result.adjustment == 15
        assert result.refined_score == 90.0  # 75 + 15
    
    @pytest.mark.asyncio
    async def test_json_parse_error(self, mock_heuristic_result, sample_comments, mock_vertex_client):
        """Test JSON parsing error handling."""
        # Mock invalid JSON response
        async def mock_invalid_json(system_prompt, user_prompt, **kwargs):
            return "invalid json response"
        
        mock_vertex_client.generate_content = AsyncMock(side_effect=mock_invalid_json)
        refiner = AuthenticityRefiner(model_client=mock_vertex_client)
        
        result = await refiner.refine(
            heuristic_result=mock_heuristic_result,
            comments=sample_comments,
            context="English"
        )
        
        # Should return fallback result
        assert result.refined_score == mock_heuristic_result.score
        assert result.adjustment == 0
        assert "LLM JSON Parse Error" in result.explanation
        assert "llm_error" in result.flags


class TestVertexAIConfig:
    """Test Vertex AI configuration."""
    
    def test_config_loading(self):
        """Test configuration loading from environment."""
        import os
        
        # Set test environment variables
        os.environ["VERTEX_AI_PROJECT_ID"] = "test-project"
        os.environ["VERTEX_AI_LOCATION"] = "us-east1"
        os.environ["VERTEX_AI_MODEL_NAME"] = "gemini-1.5-flash"
        os.environ["VERTEX_AI_TIMEOUT"] = "45"
        os.environ["VERTEX_AI_MAX_RETRIES"] = "3"
        
        config = VertexAIConfig.get_config()
        
        assert config["project_id"] == "test-project"
        assert config["location"] == "us-east1"
        assert config["model_name"] == "gemini-1.5-flash"
        assert config["timeout"] == 45
        assert config["max_retries"] == 3
        
        # Clean up
        del os.environ["VERTEX_AI_PROJECT_ID"]
        del os.environ["VERTEX_AI_LOCATION"]
        del os.environ["VERTEX_AI_MODEL_NAME"]
        del os.environ["VERTEX_AI_TIMEOUT"]
        del os.environ["VERTEX_AI_MAX_RETRIES"]
    
    def test_default_config(self):
        """Test default configuration values."""
        config = VertexAIConfig.get_config()
        
        assert config["project_id"] == ""
        assert config["location"] == "us-central1"
        assert config["model_name"] == "gemini-1.5-pro"
        assert config["timeout"] == 30
        assert config["max_retries"] == 2
    
    def test_is_configured(self):
        """Test configuration validation."""
        import os
        
        # Test unconfigured
        assert not VertexAIConfig.is_configured()
        
        # Test configured
        os.environ["VERTEX_AI_PROJECT_ID"] = "test-project"
        assert VertexAIConfig.is_configured()
        
        # Clean up
        del os.environ["VERTEX_AI_PROJECT_ID"]
    
    def test_validate_config(self):
        """Test configuration validation."""
        # Valid config
        valid_config = {
            "project_id": "test-project",
            "location": "us-central1",
            "model_name": "gemini-1.5-pro"
        }
        assert VertexAIConfig.validate_config(valid_config)
        
        # Invalid config - missing project_id
        invalid_config = {
            "location": "us-central1",
            "model_name": "gemini-1.5-pro"
        }
        assert not VertexAIConfig.validate_config(invalid_config)


if __name__ == "__main__":
    # Run basic tests
    asyncio.run(TestVertexAIGeminiIntegration().test_successful_refinement(
        HeuristicResult(score=75.0, raw_value=0.75, confidence=0.8, 
                       data_completeness=DataCompleteness.FULL, 
                       signals={"bot_probability": 0.2, "entropy": 0.85, 
                               "uniqueness": 0.9, "variance": 0.7}),
        ["Love this content!", "Great post!", "Amazing work!"],
        Mock(spec=VertexAIGeminiClient)
    ))
    print("✅ Vertex AI Gemini integration implementation complete!")