"""
Groq API Provider - Ultra-fast inference (500+ tokens/s)
"""

import os
from typing import Optional
from groq import Groq as GroqClient

from ..config import GroqConfig
from ..models import ModelInfo


class GroqProvider:
    """Groq API Provider - Ultra-fast inference"""

    def __init__(self, config: GroqConfig):
        self.config = config
        if config.api_key:
            self.client = GroqClient(api_key=config.api_key)
        else:
            self.client = None

    def is_available(self) -> bool:
        """Check if provider is available"""
        return self.config.enabled and self.config.api_key is not None and self.client is not None

    def get_model(self, model_id: str) -> Optional[ModelInfo]:
        """Get model information"""
        from ..models import get_model_by_id
        return get_model_by_id(model_id)

    def test_model(self, model_id: str) -> bool:
        """Test if model is available"""
        if not self.client:
            return False

        try:
            response = self.client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=10
            )
            return True
        except Exception:
            return False

    def generate(self, model_id: str, prompt: str, **kwargs) -> str:
        """Generate content"""
        if not self.client:
            raise ValueError("Groq API key not set")

        response = self.client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", kwargs.get("max_output_tokens", 1024)),
            top_p=kwargs.get("top_p", 0.9),
        )

        return response.choices[0].message.content

    def list_models(self) -> list[ModelInfo]:
        """List available models"""
        from ..models import get_models_by_provider
        return get_models_by_provider("groq")
