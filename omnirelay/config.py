"""
配置管理模块
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class ProviderConfig(BaseModel):
    """提供商配置"""

    enabled: bool = True
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    models: list[str] = []


class GeminiConfig(ProviderConfig):
    """Gemini 配置"""

    endpoint: str = "https://generativelanguage.googleapis.com"


class OpenRouterConfig(ProviderConfig):
    """OpenRouter 配置"""

    endpoint: str = "https://openrouter.ai/api/v1"


class KiloConfig(ProviderConfig):
    """Kilo Gateway 配置"""

    endpoint: str = "https://api.kilo.ai"


class FallbackConfig(BaseModel):
    """回退配置"""

    primary: str
    chain: list[str] = []
    max_retries: int = 3
    retry_delay: int = 5


class OmniRelayConfig(BaseModel):
    """OmniRelay 总配置"""

    providers: dict[str, ProviderConfig] = {}
    fallbacks: FallbackConfig = FallbackConfig(primary="", chain=[])

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @classmethod
    def load_from_env(cls) -> "OmniRelayConfig":
        """从环境变量加载配置"""
        config = cls()

        # Gemini
        if os.getenv("GEMINI_API_KEY"):
            config.providers["gemini"] = GeminiConfig(
                enabled=True,
                api_key=os.getenv("GEMINI_API_KEY"),
                models=["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
            )

        # OpenRouter
        if os.getenv("OPENROUTER_API_KEY"):
            config.providers["openrouter"] = OpenRouterConfig(
                enabled=True,
                api_key=os.getenv("OPENROUTER_API_KEY"),
                models=["qwen/qwen-plus:free", "nvidia/nemotron:free", "xiaomi/mimo-v2-pro:free"]
            )

        # Kilo
        if os.getenv("KILOCODE_API_KEY"):
            config.providers["kilo"] = KiloConfig(
                enabled=True,
                api_key=os.getenv("KILOCODE_API_KEY"),
                models=["kilocode/minimax-m2.5:free"]
            )

        return config

    def get_available_providers(self) -> list[str]:
        """获取可用的提供商列表"""
        return [name for name, config in self.providers.items() if config.enabled and config.api_key]

    def get_provider_models(self, provider: str) -> list[str]:
        """获取提供商的模型列表"""
        if provider not in self.providers:
            return []
        return self.providers[provider].models


# 默认配置
config = OmniRelayConfig.load_from_env()
