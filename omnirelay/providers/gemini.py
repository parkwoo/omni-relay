"""
Google Gemini API Provider - Native Google API access
"""

import os
from typing import Optional
import google.generativeai as genai

from ..config import GeminiConfig
from ..models import ModelInfo


class GeminiProvider:
    """Google Gemini API Provider - Native Google API"""

    def __init__(self, config: GeminiConfig):
        self.config = config
        if config.api_key:
            genai.configure(api_key=config.api_key)

    def is_available(self) -> bool:
        """Check if provider is available"""
        return self.config.enabled and self.config.api_key is not None

    def get_model(self, model_id: str) -> Optional[ModelInfo]:
        """Get model information"""
        from ..models import get_model_by_id
        return get_model_by_id(model_id)

    def test_model(self, model_id: str) -> bool:
        """Test if model is available"""
        if not self.config.api_key:
            return False

        try:
            model = genai.GenerativeModel(model_id)
            response = model.generate_content("test", stream=False)
            return True
        except Exception:
            return False

    def generate(self, model_id: str, prompt: str, **kwargs) -> str:
        """Generate content"""
        if not self.config.api_key:
            raise ValueError("Gemini API key not set")

        model = genai.GenerativeModel(model_id)

        # Handle Gemini-specific parameters
        generation_config = {
            "temperature": kwargs.get("temperature", 0.7),
            "top_p": kwargs.get("top_p", 0.9),
            "top_k": kwargs.get("top_k", 40),
            "max_output_tokens": kwargs.get("max_tokens", kwargs.get("max_output_tokens", 1024)),
        }

        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(**generation_config),
            stream=False
        )

        return response.text

    def list_models(self) -> list[ModelInfo]:
        """List available models"""
        from ..models import get_models_by_provider
        return get_models_by_provider("gemini")
