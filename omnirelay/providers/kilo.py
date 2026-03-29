"""
Kilo Gateway Provider - Unified API for 500+ AI models
======================================================

OmniRelay provider for Kilo Gateway.
Unified API access to 500+ models including MiniMax, NVIDIA, and more.

GitHub: https://github.com/parkwoo/omni-relay
Author: parkwoo
License: MIT

Free Tier:
  - $5 initial credit
  - MiniMax M2.5 permanently free
  - No credit card required

Popular Models:
  - MiniMax M2.5 (204K context) - Free
  - NVIDIA Nemotron 3 Super (262K context)
  - Xiaomi Mimo V2 Pro (256K context)

API Docs:
  - https://kilo.ai/docs
  - Base URL: https://api.kilo.ai/api/gateway

Usage:
  from omnirelay.providers import KiloProvider
  provider = KiloProvider(config)
  models = provider.list_models()
"""

from typing import Optional
import requests

from ..config import KiloConfig
from ..models import ModelInfo
from ..utils import get_client_headers


class KiloProvider:
    """
    Kilo Gateway Provider - Unified API for 500+ models

    Kilo Gateway provides a unified API that routes requests to many models
    behind a single endpoint and API key.

    Base URL: https://api.kilo.ai/api/gateway
    Authentication: Bearer Token (API Key)

    See omnirelay/models.py for complete model list and metadata.
    """

    def __init__(self, config: KiloConfig):
        self.config = config
        self.base_url = config.endpoint
        self.session = requests.Session()

        if config.api_key:
            headers = get_client_headers()
            headers["X-API-Key"] = config.api_key
            self.session.headers.update(headers)

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
            response = self.session.post(
                f"{self.base_url}/v1/chat/completions",
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
            raise ValueError("Kilo Gateway API key not set")

        response = self.session.post(
            f"{self.base_url}/v1/chat/completions",
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
        return get_models_by_provider("kilo")
