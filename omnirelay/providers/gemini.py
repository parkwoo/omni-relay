"""
Google Gemini API Provider - Native Google API access
=====================================================

OmniRelay provider for Google Gemini API.
Supports Gemini 2.5 Flash, 2.0 Flash, and other Gemini models.

GitHub: https://github.com/parkwoo/omni-relay
Author: parkwoo
License: MIT

Free Tier:
  - 1M tokens/min free (Gemini 2.5 Flash)
  - No credit card required

API Docs:
  - https://ai.google.dev/gemini-api/docs
  - https://github.com/googleapis/python-genai

Usage:
  from omnirelay.providers import GeminiProvider
  provider = GeminiProvider(config)
  models = provider.list_models()
"""

from typing import Optional

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

from ..config import GeminiConfig
from ..models import ModelInfo


class GeminiProvider:
    """
    Google Gemini API Provider - Native Google API
    
    Uses the new google.genai client (v1.0.0+)
    Replaces deprecated google.generativeai package
    """

    def __init__(self, config: GeminiConfig):
        self.config = config
        self.client = None
        
        if config.api_key and HAS_GENAI:
            self.client = genai.Client(api_key=config.api_key)

    def is_available(self) -> bool:
        """Check if provider is available"""
        return self.config.enabled and self.config.api_key is not None and HAS_GENAI

    def get_model(self, model_id: str) -> Optional[ModelInfo]:
        """Get model information"""
        from ..models import get_model_by_id
        return get_model_by_id(model_id)

    def test_model(self, model_id: str) -> bool:
        """Test if model is available"""
        if not self.client:
            return False

        try:
            response = self.client.models.generate_content(
                model=model_id,
                contents="test",
                config=types.GenerateContentConfig(max_output_tokens=10)
            )
            return response is not None and len(response.text) > 0
        except Exception:
            return False

    def generate(self, model_id: str, prompt: str, **kwargs) -> str:
        """Generate content using new google.genai API"""
        if not self.client:
            raise ValueError("Gemini API key not set or google-genai not installed")

        generation_config = types.GenerateContentConfig(
            temperature=kwargs.get("temperature", 0.7),
            top_p=kwargs.get("top_p", 0.9),
            top_k=kwargs.get("top_k", 40),
            max_output_tokens=kwargs.get("max_tokens", kwargs.get("max_output_tokens", 1024)),
        )

        response = self.client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=generation_config
        )

        if not response or not response.text:
            raise ValueError("Empty response from Gemini API")

        return response.text

    def list_models(self) -> list[ModelInfo]:
        """List available models"""
        from ..models import get_models_by_provider
        return get_models_by_provider("gemini")
