"""
Qwen (Alibaba Tongyi Qianwen) API Provider - Stable cloud service
"""

import os
from typing import Optional
import requests
import json

from ..config import QwenConfig
from ..models import ModelInfo


class QwenProvider:
    """Qwen (Alibaba Tongyi Qianwen) API Provider - Stable cloud service"""

    def __init__(self, config: QwenConfig):
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
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }

        try:
            # DashScope uses OpenAI-compatible API
            response = self.session.post(
                f"{self.config.endpoint}/services/aigc/text-generation/generation",
                headers=headers,
                json={
                    "model": model_id,
                    "input": {
                        "messages": [{"role": "user", "content": "test"}]
                    },
                    "parameters": {
                        "max_tokens": 10
                    }
                },
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False

    def generate(self, model_id: str, prompt: str, **kwargs) -> str:
        """Generate content"""
        if not self.config.api_key:
            raise ValueError("Qwen DashScope API key not set")

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }

        # DashScope API format
        body = {
            "model": model_id,
            "input": {
                "messages": [{"role": "user", "content": prompt}]
            },
            "parameters": {
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", kwargs.get("max_output_tokens", 1024)),
                "top_p": kwargs.get("top_p", 0.9),
            }
        }

        response = self.session.post(
            f"{self.config.endpoint}/services/aigc/text-generation/generation",
            headers=headers,
            json=body,
            timeout=60
        )

        response.raise_for_status()
        data = response.json()

        return data["output"]["text"]

    def list_models(self) -> list[ModelInfo]:
        """List available models"""
        from ..models import get_models_by_provider
        return get_models_by_provider("qwen")
