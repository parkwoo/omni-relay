"""
OmniRelay Provider Implementations
==================================

Multi-cloud AI provider implementations for OmniRelay.
Each provider supports OpenAI-compatible or native API interfaces.

GitHub: https://github.com/parkwoo/omni-relay
Author: parkwoo
License: MIT

Supported Providers:
  - Google Gemini (1M tokens/min free)
  - Alibaba Qwen (1M+ tokens/month free)
  - Zhipu AI (GLM-4-Flash free)
  - DeepSeek ($5 free credit)
  - Novita AI ($20 free credit, partner)
  - xAI Grok ($25/month free)
  - OpenRouter (30+ free models)
  - OpenAI ($5 trial)
  - Kilo Gateway ($5 + MiniMax M2.5 free)

Usage:
  from omnirelay.providers import GeminiProvider, QwenProvider, ZhipuProvider
"""

from .gemini import GeminiProvider
from .openrouter import OpenRouterProvider
from .kilo import KiloProvider
from .deepseek import DeepSeekProvider
from .novita import NovitaProvider
from .qwen import QwenProvider
from .xai import XAIProvider
from .openai import OpenAIProvider
from .zhipu import ZhipuProvider

__all__ = [
    "GeminiProvider",
    "OpenRouterProvider",
    "KiloProvider",
    "DeepSeekProvider",
    "NovitaProvider",
    "QwenProvider",
    "XAIProvider",
    "OpenAIProvider",
    "ZhipuProvider",
]
