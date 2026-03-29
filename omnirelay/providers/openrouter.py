"""
OpenRouter API Provider - 30+ free models
=========================================

OmniRelay provider for OpenRouter.
Access to 30+ free models from various providers.

GitHub: https://github.com/parkwoo/omni-relay
Author: parkwoo
License: MIT

Free Tier:
  - 30+ free models forever
  - No credit card required
  - Rate limits apply on free tier

Popular Free Models:
  - NVIDIA Nemotron 3 Super (262K context)
  - Qwen3 Coder 480B (262K context)
  - MiniMax M2.5 (196K context)
  - OpenAI GPT-OSS 120B (131K context)

API Docs:
  - https://openrouter.ai/docs

Usage:
  from omnirelay.providers import OpenRouterProvider
  provider = OpenRouterProvider(config)
  models = provider.list_models()
"""

from typing import Optional
import requests

from ..config import OpenRouterConfig
from ..models import ModelInfo
from ..utils import get_client_headers


class OpenRouterProvider:
    """OpenRouter API Provider - 30+ free models"""

    def __init__(self, config: OpenRouterConfig):
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
            raise ValueError("OpenRouter API key not set")

        headers = get_client_headers(f"Bearer {self.config.api_key}")

        response = self.session.post(
            f"{self.config.endpoint}/chat/completions",
            headers=headers,
            json={
                "model": model_id,
                "messages": [{"role": "user", "content": prompt}],
                **kwargs
            },
            timeout=60
        )

        response.raise_for_status()
        data = response.json()

        return data["choices"][0]["message"]["content"]

    def list_models(self) -> list[ModelInfo]:
        """List available models"""
        from ..models import get_models_by_provider
        return get_models_by_provider("openrouter")
