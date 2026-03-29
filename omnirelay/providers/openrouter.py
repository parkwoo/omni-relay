"""
OpenRouter API 提供商
"""

import os
from typing import Optional
import requests

from ..config import OpenRouterConfig
from ..models import ModelInfo


class OpenRouterProvider:
    """OpenRouter API 提供商"""

    def __init__(self, config: OpenRouterConfig):
        self.config = config
        self.session = requests.Session()

    def is_available(self) -> bool:
        """检查是否可用"""
        return self.config.enabled and self.config.api_key is not None

    def get_model(self, model_id: str) -> Optional[ModelInfo]:
        """获取模型信息"""
        from ..models import get_model_by_id
        return get_model_by_id(model_id)

    def test_model(self, model_id: str) -> bool:
        """测试模型是否可用"""
        if not self.config.api_key:
            return False

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "HTTP-Referer": "https://free-ride-enhanced.com"
        }

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
        """生成内容"""
        if not self.config.api_key:
            raise ValueError("OpenRouter API key not set")

        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "HTTP-Referer": "https://free-ride-enhanced.com",
            "Content-Type": "application/json"
        }

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

    def list_free_models(self) -> list[ModelInfo]:
        """列出免费模型"""
        from ..models import get_models_by_provider
        return get_models_by_provider("openrouter")
