import os
from typing import Dict, Any, Optional

class VertexAIConfig:
    """
    Configuration for Vertex AI Gemini integration.
    Loads from environment variables with sensible defaults.
    """
    
    @staticmethod
    def get_config() -> Dict[str, Any]:
        """
        Get Vertex AI configuration from environment.
        
        Returns:
            Configuration dictionary for VertexAIGeminiClient
        """
        return {
            "project_id": os.getenv("VERTEX_AI_PROJECT_ID", ""),
            "location": os.getenv("VERTEX_AI_LOCATION", "us-central1"),
            "model_name": os.getenv("VERTEX_AI_MODEL_NAME", "gemini-1.5-pro"),
            "timeout": int(os.getenv("VERTEX_AI_TIMEOUT", "30")),
            "max_retries": int(os.getenv("VERTEX_AI_MAX_RETRIES", "2"))
        }
    
    @staticmethod
    def is_configured() -> bool:
        """
        Check if Vertex AI is properly configured.
        
        Returns:
            True if project_id is set, False otherwise
        """
        return bool(os.getenv("VERTEX_AI_PROJECT_ID", ""))
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> bool:
        """
        Validate Vertex AI configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["project_id", "location", "model_name"]
        return all(field in config and config[field] for field in required_fields)