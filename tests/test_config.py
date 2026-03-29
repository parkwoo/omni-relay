"""
测试配置模块
"""

import os
import pytest
from omnirelay.config import (
    OmniRelayConfig,
    GeminiConfig,
    OpenRouterConfig,
    KiloConfig,
)


class TestConfig:
    """测试配置相关函数"""

    def test_create_empty_config(self):
        """测试创建空配置"""
        config = OmniRelayConfig()
        assert config.providers == {}
        assert config.fallbacks.primary == ""
        assert config.fallbacks.chain == []

    def test_load_from_env_empty(self):
        """测试从空环境变量加载"""
        # 清空环境变量
        for key in ["GEMINI_API_KEY", "OPENROUTER_API_KEY", "KILOCODE_API_KEY"]:
            if key in os.environ:
                del os.environ[key]

        config = OmniRelayConfig.load_from_env()
        assert len(config.providers) == 0

    def test_load_from_env_with_gemini(self):
        """测试从环境变量加载 Gemini 配置"""
        os.environ["GEMINI_API_KEY"] = "test-key"
        config = OmniRelayConfig.load_from_env()

        assert "gemini" in config.providers
        assert config.providers["gemini"].api_key == "test-key"
        assert config.providers["gemini"].enabled is True

        # 清理
        del os.environ["GEMINI_API_KEY"]

    def test_get_available_providers(self):
        """测试获取可用提供商"""
        config = OmniRelayConfig()
        config.providers = {
            "gemini": GeminiConfig(enabled=True, api_key="test"),
            "openrouter": OpenRouterConfig(enabled=True, api_key=None),
        }

        available = config.get_available_providers()
        assert available == ["gemini"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
