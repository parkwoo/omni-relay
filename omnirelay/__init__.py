"""
OmniRelay - Multi-Cloud AI Failover for OpenClaw
================================================

High availability LLM API routing with intelligent failover across 9+ AI providers.
Automatic rate limit recovery in <100ms with zero downtime.

GitHub: https://github.com/parkwoo/omni-relay
Author: parkwoo
License: MIT

Providers:
  - Google Gemini (1M tokens/min free)
  - Alibaba Qwen (1M+ tokens/month free)
  - Zhipu AI (GLM-4-Flash free)
  - DeepSeek ($5 free credit)
  - Novita AI ($20 free credit)
  - xAI Grok ($25/month free)
  - OpenRouter (30+ free models)
  - OpenAI ($5 trial)
  - Kilo Gateway ($5 + MiniMax M2.5 free)

Usage:
  from omnirelay import __version__
  from omnirelay.cli import main
  from omnirelay.models import rank_models_by_quality
"""

__version__ = "1.4.1"
__author__ = "parkwoo"
__github__ = "https://github.com/parkwoo/omni-relay"
__license__ = "MIT"
