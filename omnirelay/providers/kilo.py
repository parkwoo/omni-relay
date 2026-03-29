"""
Kilo Gateway Provider - At-cost proxy for multiple models
"""

import os
from typing import Optional
import requests

from ..config import KiloConfig
from ..models import ModelInfo


class KiloProvider:
    """Kilo Gateway Provider - At-cost proxy"""

    def __init__(self, config: KiloConfig):
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

        headers = {
            "X-API-Key": self.config.api_key
        }

        try:
            response = self.session.get(
                f"{self.config.endpoint}/v1/models/{model_id}",
                headers=headers,
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False

    def generate(self, model_id: str, prompt: str, **kwargs) -> str:
        """Generate content"""
        if not self.config.api_key:
            raise ValueError("Kilo Gateway API key not set")

        headers = {
            "X-API-Key": self.config.api_key,
            "Content-Type": "application/json"
        }

        response = self.session.post(
            f"{self.config.endpoint}/v1/chat/completions",
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
        return get_models_by_provider("kilo")
