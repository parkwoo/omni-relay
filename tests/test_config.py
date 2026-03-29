"""
Tests for omnirelay.config
"""

import os
import pytest
from omnirelay.config import (
    OmniRelayConfig,
    GeminiConfig, OpenRouterConfig, KiloConfig,
    DeepSeekConfig, NovitaConfig, QwenConfig,
    XAIConfig, OpenAIConfig, ZhipuConfig,
)

ALL_ENV_KEYS = [
    "GEMINI_API_KEY", "OPENROUTER_API_KEY", "KILOCODE_API_KEY",
    "DEEPSEEK_API_KEY", "NOVITA_API_KEY", "DASHSCOPE_API_KEY",
    "XAI_API_KEY", "OPENAI_API_KEY", "ZHIPU_API_KEY",
]


def _clear_all_keys(monkeypatch):
    for key in ALL_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


class TestOmniRelayConfig:
    def test_empty_config_defaults(self):
        config = OmniRelayConfig()
        assert config.providers == {}
        assert config.fallbacks.primary == ""
        assert config.fallbacks.chain == []

    def test_load_from_env_empty(self, monkeypatch):
        _clear_all_keys(monkeypatch)
        config = OmniRelayConfig.load_from_env()
        assert len(config.providers) == 0

    def test_load_gemini(self, monkeypatch):
        _clear_all_keys(monkeypatch)
        monkeypatch.setenv("GEMINI_API_KEY", "gemini-key")
        config = OmniRelayConfig.load_from_env()
        assert "gemini" in config.providers
        assert config.providers["gemini"].api_key == "gemini-key"

    def test_load_deepseek(self, monkeypatch):
        _clear_all_keys(monkeypatch)
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-deepseek")
        config = OmniRelayConfig.load_from_env()
        assert "deepseek" in config.providers
        assert config.providers["deepseek"].api_key == "sk-deepseek"
        assert "deepseek-reasoner" in config.providers["deepseek"].models

    def test_load_novita(self, monkeypatch):
        _clear_all_keys(monkeypatch)
        monkeypatch.setenv("NOVITA_API_KEY", "sk-novita")
        config = OmniRelayConfig.load_from_env()
        assert "novita" in config.providers

    def test_load_qwen_via_dashscope(self, monkeypatch):
        _clear_all_keys(monkeypatch)
        monkeypatch.setenv("DASHSCOPE_API_KEY", "sk-dashscope")
        config = OmniRelayConfig.load_from_env()
        assert "qwen" in config.providers
        assert config.providers["qwen"].api_key == "sk-dashscope"

    def test_load_xai(self, monkeypatch):
        _clear_all_keys(monkeypatch)
        monkeypatch.setenv("XAI_API_KEY", "xai-key")
        config = OmniRelayConfig.load_from_env()
        assert "xai" in config.providers
        assert "grok-3" in config.providers["xai"].models

    def test_load_openai(self, monkeypatch):
        _clear_all_keys(monkeypatch)
        monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
        config = OmniRelayConfig.load_from_env()
        assert "openai" in config.providers
        assert "gpt-4o" in config.providers["openai"].models

    def test_load_zhipu(self, monkeypatch):
        _clear_all_keys(monkeypatch)
        monkeypatch.setenv("ZHIPU_API_KEY", "zhipu-key")
        config = OmniRelayConfig.load_from_env()
        assert "zhipu" in config.providers
        assert "glm-4-flash" in config.providers["zhipu"].models

    def test_load_all_nine_providers(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "k1")
        monkeypatch.setenv("OPENROUTER_API_KEY", "k2")
        monkeypatch.setenv("KILOCODE_API_KEY", "k3")
        monkeypatch.setenv("DEEPSEEK_API_KEY", "k4")
        monkeypatch.setenv("NOVITA_API_KEY", "k5")
        monkeypatch.setenv("DASHSCOPE_API_KEY", "k6")
        monkeypatch.setenv("XAI_API_KEY", "k7")
        monkeypatch.setenv("OPENAI_API_KEY", "k8")
        monkeypatch.setenv("ZHIPU_API_KEY", "k9")
        config = OmniRelayConfig.load_from_env()
        assert len(config.providers) == 9

    def test_get_available_providers_excludes_disabled(self):
        config = OmniRelayConfig()
        config.providers["gemini"] = GeminiConfig(enabled=True, api_key="key")
        config.providers["openrouter"] = OpenRouterConfig(enabled=False, api_key="key")
        config.providers["kilo"] = KiloConfig(enabled=True, api_key=None)
        assert config.get_available_providers() == ["gemini"]

    def test_get_provider_models(self):
        config = OmniRelayConfig()
        config.providers["xai"] = XAIConfig(api_key="k", models=["grok-3", "grok-3-mini"])
        assert config.get_provider_models("xai") == ["grok-3", "grok-3-mini"]

    def test_get_provider_models_unknown_returns_empty(self):
        config = OmniRelayConfig()
        assert config.get_provider_models("nonexistent") == []


class TestProviderConfigs:
    def test_deepseek_default_endpoint(self):
        assert "deepseek.com" in DeepSeekConfig().endpoint

    def test_novita_default_endpoint(self):
        assert "novita.ai" in NovitaConfig().endpoint

    def test_qwen_default_endpoint_is_compatible_mode(self):
        assert "compatible-mode" in QwenConfig().endpoint

    def test_xai_default_endpoint(self):
        assert "x.ai" in XAIConfig().endpoint

    def test_openai_default_endpoint(self):
        assert "openai.com" in OpenAIConfig().endpoint

    def test_zhipu_default_endpoint(self):
        assert "bigmodel.cn" in ZhipuConfig().endpoint
