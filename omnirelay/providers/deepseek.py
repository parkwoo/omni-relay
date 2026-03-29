"""
DeepSeek API Provider - OpenAI-compatible API
=============================================

OmniRelay provider for DeepSeek models.
OpenAI-compatible API interface.

GitHub: https://github.com/parkwoo/omni-relay
Author: parkwoo
License: MIT

Free Tier:
  - $5 one-time credit (~5M tokens)
  - No credit card required

Models:
  - DeepSeek R1 (Reasoner) - Best for reasoning tasks
  - DeepSeek V3 (Chat) - Best for general chat

API Docs:
  - https://platform.deepseek.com/api-docs

Usage:
  from omnirelay.providers import DeepSeekProvider
  provider = DeepSeekProvider(config)
  models = provider.list_models()
"""

from typing import Optional
import requests

from ..config import DeepSeekConfig
from ..models import ModelInfo
from ..utils import get_client_headers


class DeepSeekProvider:
    """DeepSeek API Provider - Strongest reasoning"""

    def __init__(self, config: DeepSeekConfig):
        self.config = config
        self.session = requests.Session()

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

        headers = get_client_headers(f"Bearer {self.config.api_key}")

        try:
            response = self.session.post(
                f"{self.config.endpoint}/chat/completions",
                headers=headers,
                json={
                    "model": model_id,
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 10
                },
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False

    def generate(self, model_id: str, prompt: str, **kwargs) -> str:
        """Generate content"""
        if not self.config.api_key:
            raise ValueError("DeepSeek API key not set")

        headers = get_client_headers(f"Bearer {self.config.api_key}")

        response = self.session.post(
            f"{self.config.endpoint}/chat/completions",
            headers=headers,
            json={
                "model": model_id,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", kwargs.get("max_output_tokens", 1024)),
                "top_p": kwargs.get("top_p", 0.9),
            },
            timeout=60
        )

        response.raise_for_status()
        data = response.json()

        return data["choices"][0]["message"]["content"]

    def list_models(self) -> list[ModelInfo]:
        """List available models"""
        from ..models import get_models_by_provider
        return get_models_by_provider("deepseek")
