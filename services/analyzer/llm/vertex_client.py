import asyncio
import json
import logging
from typing import Optional, Dict, Any
import time

try:
    from google.cloud import aiplatform
    from vertexai.preview.generative_models import GenerativeModel, GenerationConfig
    VERTEX_AI_AVAILABLE = True
except ImportError:
    VERTEX_AI_AVAILABLE = False
    aiplatform = None
    GenerativeModel = None
    GenerationConfig = None

logger = logging.getLogger(__name__)

class VertexAIGeminiClient:
    """
    Vertex AI Gemini client for bounded refinement operations.
    Handles timeouts, retries, and error management.
    """
    
    def __init__(
        self, 
        project_id: str,
        location: str = "us-central1",
        model_name: str = "gemini-1.5-pro",
        timeout: int = 30,
        max_retries: int = 2
    ):
        if not VERTEX_AI_AVAILABLE:
            raise ImportError(
                "Vertex AI dependencies not available. "
                "Install with: pip install google-cloud-aiplatform vertexai"
            )
            
        self.project_id = project_id
        self.location = location
        self.model_name = model_name
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Initialize Vertex AI
        aiplatform.init(project=project_id, location=location)
        self.model = GenerativeModel(model_name)
        
    async def generate_content(
        self, 
        system_prompt: str, 
        user_prompt: str,
        temperature: float = 0.1,
        max_output_tokens: int = 500
    ) -> str:
        """
        Generate content with Vertex AI Gemini with timeout and retry logic.
        
        Args:
            system_prompt: The system instruction prompt
            user_prompt: The user input prompt
            temperature: Controls randomness (0.0-1.0)
            max_output_tokens: Maximum tokens in response
            
        Returns:
            Generated text response
            
        Raises:
            TimeoutError: If request exceeds timeout
            Exception: For other API errors after retries
        """
        
        generation_config = GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            top_p=0.8,
            top_k=40
        )
        
        full_prompt = f"{system_prompt}\n\nUser Input:\n{user_prompt}"
        
        for attempt in range(self.max_retries + 1):
            try:
                # Use asyncio timeout to handle hanging requests
                response = await asyncio.wait_for(
                    self._generate_with_model(full_prompt, generation_config),
                    timeout=self.timeout
                )
                
                # Validate response format
                if self._is_valid_json_response(response.text):
                    return response.text
                else:
                    logger.warning(f"Invalid JSON response on attempt {attempt + 1}")
                    if attempt == self.max_retries:
                        raise ValueError("Invalid response format from Gemini")
                    
            except asyncio.TimeoutError:
                logger.error(f"Timeout on attempt {attempt + 1}")
                if attempt == self.max_retries:
                    raise TimeoutError(f"Gemini request timed out after {self.timeout}s")
                    
            except Exception as e:
                logger.error(f"Error on attempt {attempt + 1}: {str(e)}")
                if attempt == self.max_retries:
                    raise
                
                # Exponential backoff
                await asyncio.sleep(2 ** attempt)
        
        raise RuntimeError("Max retries exceeded")
    
    async def _generate_with_model(self, prompt: str, config: GenerationConfig):
        """Internal method to handle the actual model call."""
        # Run the synchronous Vertex AI call in a thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            lambda: self.model.generate_content(
                prompt,
                generation_config=config
            )
        )
    
    def _is_valid_json_response(self, response_text: str) -> bool:
        """Validate that the response is valid JSON with required fields."""
        try:
            parsed = json.loads(response_text)
            required_fields = ["adjustment", "reason", "flags"]
            return all(field in parsed for field in required_fields)
        except json.JSONDecodeError:
            return False
    
    async def health_check(self) -> bool:
        """Check if the Vertex AI service is accessible."""
        try:
            response = await asyncio.wait_for(
                self._generate_with_model("Health check", GenerationConfig(temperature=0.0, max_output_tokens=10)),
                timeout=10
            )
            return bool(response.text)
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False