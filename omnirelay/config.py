"""
Configuration management

API Endpoint Notes:
- Default endpoints are for international/overseas users
- For users in mainland China, use the CN (China) endpoints where available
"""

import os
from typing import Optional
from pydantic import BaseModel


class ProviderConfig(BaseModel):
    """Base provider configuration"""

    enabled: bool = True
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    models: list[str] = []


class GeminiConfig(ProviderConfig):
    # International: https://generativelanguage.googleapis.com
    # China (CN): Not directly accessible, use proxy or mirror
    endpoint: str = "https://generativelanguage.googleapis.com"


class OpenRouterConfig(ProviderConfig):
    # International: https://openrouter.ai/api/v1
    # China (CN): Same endpoint, may require proxy
    endpoint: str = "https://openrouter.ai/api/v1"


class KiloConfig(ProviderConfig):
    # International: https://api.kilo.ai/api/gateway
    # China (CN): Same endpoint
    endpoint: str = "https://api.kilo.ai/api/gateway"


class DeepSeekConfig(ProviderConfig):
    # International: https://api.deepseek.com
    # China (CN): https://platform.deepseek.com (same endpoint)
    # Note: DeepSeek uses unified global endpoint
    endpoint: str = "https://api.deepseek.com"


class NovitaConfig(ProviderConfig):
    # International: https://api.novita.ai/v3/openai
    # China (CN): Same endpoint (Singapore-based, works in CN)
    endpoint: str = "https://api.novita.ai/v3/openai"


class QwenConfig(ProviderConfig):
    # International: https://dashscope-intl.aliyuncs.com/compatible-mode/v1
    # China (Beijing): https://dashscope.aliyuncs.com/compatible-mode/v1
    # China (Hong Kong): https://cn-hongkong.dashscope.aliyuncs.com/compatible-mode/v1
    # Default uses China (Beijing) endpoint; overseas users should set dashscope-intl
    endpoint: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"


class XAIConfig(ProviderConfig):
    # International: https://api.x.ai/v1
    # China (CN): Not directly accessible, use proxy
    endpoint: str = "https://api.x.ai/v1"


class OpenAIConfig(ProviderConfig):
    # International: https://api.openai.com/v1
    # China (CN): Not directly accessible, use proxy or mirror
    # Alternative CN proxy: https://api.openai-proxy.com/v1 (third-party)
    endpoint: str = "https://api.openai.com/v1"


class ZhipuConfig(ProviderConfig):
    # International: https://api.z.ai/api/paas/v4
    # China (CN): https://open.bigmodel.cn/api/paas/v4
    # Note: Zhipu operates two separate platforms
    # Default uses China endpoint (open.bigmodel.cn) for GLM-4-Flash free tier
    endpoint: str = "https://open.bigmodel.cn/api/paas/v4"


class FallbackConfig(BaseModel):
    """Fallback chain configuration"""

    primary: str = ""
    chain: list[str] = []
    max_retries: int = 3
    retry_delay: int = 5


class OmniRelayConfig(BaseModel):
    """OmniRelay top-level configuration"""

    providers: dict[str, ProviderConfig] = {}
    fallbacks: FallbackConfig = FallbackConfig()

    @classmethod
    def load_from_env(cls) -> "OmniRelayConfig":
        """Load configuration from environment variables"""
        config = cls()

        if os.getenv("GEMINI_API_KEY"):
            config.providers["gemini"] = GeminiConfig(
                enabled=True,
                api_key=os.getenv("GEMINI_API_KEY"),
                models=["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"],
            )

        if os.getenv("OPENROUTER_API_KEY"):
            config.providers["openrouter"] = OpenRouterConfig(
                enabled=True,
                api_key=os.getenv("OPENROUTER_API_KEY"),
                models=[
                    "openrouter/free",
                    "qwen/qwen3-coder:free",
                    "nvidia/nemotron-3-super-120b-a12b:free",
                    "minimax/minimax-m2.5:free",
                    "meta-llama/llama-3.3-70b-instruct:free",
                ],
            )

        if os.getenv("KILOCODE_API_KEY"):
            config.providers["kilo"] = KiloConfig(
                enabled=True,
                api_key=os.getenv("KILOCODE_API_KEY"),
                models=[
                    "minimax/minimax-m2.5",  # Free
                    "nvidia/nemotron-3-super-120b-a12b",  # Free
                    "arcee-ai/trinity-large-preview",  # Free
                    "z-ai/glm-4.7-flash",
                    "minimax/minimax-m2.7",
                ],
            )

        if os.getenv("DEEPSEEK_API_KEY"):
            config.providers["deepseek"] = DeepSeekConfig(
                enabled=True,
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                models=["deepseek-reasoner", "deepseek-chat"],
            )

        if os.getenv("NOVITA_API_KEY"):
            config.providers["novita"] = NovitaConfig(
                enabled=True,
                api_key=os.getenv("NOVITA_API_KEY"),
                models=["deepseek/deepseek-r1", "meta-llama/llama-3.1-70b-instruct"],
            )

        if os.getenv("DASHSCOPE_API_KEY"):
            config.providers["qwen"] = QwenConfig(
                enabled=True,
                api_key=os.getenv("DASHSCOPE_API_KEY"),
                models=["qwen-max", "qwen-plus", "qwen-turbo"],
            )

        if os.getenv("XAI_API_KEY"):
            config.providers["xai"] = XAIConfig(
                enabled=True,
                api_key=os.getenv("XAI_API_KEY"),
                models=["grok-3", "grok-3-mini"],
            )

        if os.getenv("OPENAI_API_KEY"):
            config.providers["openai"] = OpenAIConfig(
                enabled=True,
                api_key=os.getenv("OPENAI_API_KEY"),
                models=["gpt-4o", "gpt-4o-mini"],
            )

        if os.getenv("ZHIPU_API_KEY"):
            config.providers["zhipu"] = ZhipuConfig(
                enabled=True,
                api_key=os.getenv("ZHIPU_API_KEY"),
                models=["glm-4-flash", "glm-4-air", "glm-4"],
            )

        return config

    def get_available_providers(self) -> list[str]:
        """Return names of configured providers"""
        return [name for name, cfg in self.providers.items() if cfg.enabled and cfg.api_key]

    def get_provider_models(self, provider: str) -> list[str]:
        """Return model list for a given provider"""
        if provider not in self.providers:
            return []
        return self.providers[provider].models
