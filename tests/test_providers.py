"""
Tests for all 9 provider implementations.

Focuses on:
  - Unified OmniRelay identity headers sent with every request
  - Correct API endpoint construction
  - Response parsing
  - Missing API key raises ValueError
"""

import pytest
import requests
from unittest.mock import MagicMock, patch

from omnirelay.config import (
    DeepSeekConfig, NovitaConfig, QwenConfig,
    XAIConfig, OpenAIConfig, ZhipuConfig,
    OpenRouterConfig, KiloConfig,
)
from omnirelay.providers.deepseek import DeepSeekProvider
from omnirelay.providers.novita import NovitaProvider
from omnirelay.providers.qwen import QwenProvider
from omnirelay.providers.xai import XAIProvider
from omnirelay.providers.openai import OpenAIProvider
from omnirelay.providers.zhipu import ZhipuProvider
from omnirelay.providers.openrouter import OpenRouterProvider
from omnirelay.providers.kilo import KiloProvider
from omnirelay.utils import OMNIRELAY_USER_AGENT, OMNIRELAY_TITLE, OMNIRELAY_REFERER


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_response(content: str = "Hello") -> MagicMock:
    """Return a mock requests.Response with a standard chat completion payload."""
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = {
        "choices": [{"message": {"content": content}}]
    }
    mock.raise_for_status.return_value = None
    return mock


def _check_identity_headers(call_kwargs: dict):
    """Assert that OmniRelay identity headers were sent."""
    headers = call_kwargs.get("headers", {})
    assert headers.get("User-Agent") == OMNIRELAY_USER_AGENT, "Missing User-Agent"
    assert headers.get("X-Title") == OMNIRELAY_TITLE, "Missing X-Title"
    assert headers.get("HTTP-Referer") == OMNIRELAY_REFERER, "Missing HTTP-Referer"
    assert headers.get("Content-Type") == "application/json", "Missing Content-Type"


# ---------------------------------------------------------------------------
# DeepSeek
# ---------------------------------------------------------------------------

class TestDeepSeekProvider:
    def _provider(self):
        return DeepSeekProvider(DeepSeekConfig(api_key="sk-deepseek"))

    def test_generate_returns_content(self):
        provider = self._provider()
        provider.session.post = MagicMock(return_value=_mock_response("DS reply"))
        result = provider.generate("deepseek-chat", "Hello")
        assert result == "DS reply"

    def test_generate_sends_identity_headers(self):
        provider = self._provider()
        provider.session.post = MagicMock(return_value=_mock_response())
        provider.generate("deepseek-chat", "Hello")
        _check_identity_headers(provider.session.post.call_args.kwargs)

    def test_generate_sends_bearer_auth(self):
        provider = self._provider()
        provider.session.post = MagicMock(return_value=_mock_response())
        provider.generate("deepseek-chat", "Hello")
        headers = provider.session.post.call_args.kwargs["headers"]
        assert headers["Authorization"] == "Bearer sk-deepseek"

    def test_generate_uses_correct_endpoint(self):
        provider = self._provider()
        provider.session.post = MagicMock(return_value=_mock_response())
        provider.generate("deepseek-chat", "Hello")
        url = provider.session.post.call_args.args[0]
        assert url.endswith("/chat/completions")

    def test_generate_raises_without_api_key(self):
        provider = DeepSeekProvider(DeepSeekConfig())
        with pytest.raises(ValueError, match="API key"):
            provider.generate("deepseek-chat", "Hello")

    def test_is_available_true_with_key(self):
        assert self._provider().is_available()

    def test_is_available_false_without_key(self):
        assert not DeepSeekProvider(DeepSeekConfig()).is_available()


# ---------------------------------------------------------------------------
# Novita
# ---------------------------------------------------------------------------

class TestNovitaProvider:
    def _provider(self):
        return NovitaProvider(NovitaConfig(api_key="sk-novita"))

    def test_generate_returns_content(self):
        provider = self._provider()
        provider.session.post = MagicMock(return_value=_mock_response("Novita reply"))
        assert provider.generate("deepseek/deepseek-r1", "Hi") == "Novita reply"

    def test_generate_sends_identity_headers(self):
        provider = self._provider()
        provider.session.post = MagicMock(return_value=_mock_response())
        provider.generate("deepseek/deepseek-r1", "Hi")
        _check_identity_headers(provider.session.post.call_args.kwargs)

    def test_generate_sends_bearer_auth(self):
        provider = self._provider()
        provider.session.post = MagicMock(return_value=_mock_response())
        provider.generate("deepseek/deepseek-r1", "Hi")
        headers = provider.session.post.call_args.kwargs["headers"]
        assert headers["Authorization"] == "Bearer sk-novita"

    def test_generate_raises_without_api_key(self):
        with pytest.raises(ValueError, match="API key"):
            NovitaProvider(NovitaConfig()).generate("model", "Hi")


# ---------------------------------------------------------------------------
# Qwen — uses OpenAI-compatible endpoint now
# ---------------------------------------------------------------------------

class TestQwenProvider:
    def _provider(self):
        return QwenProvider(QwenConfig(api_key="sk-qwen"))

    def test_generate_returns_content(self):
        provider = self._provider()
        provider.session.post = MagicMock(return_value=_mock_response("Qwen reply"))
        assert provider.generate("qwen-max", "Hi") == "Qwen reply"

    def test_generate_sends_identity_headers(self):
        provider = self._provider()
        provider.session.post = MagicMock(return_value=_mock_response())
        provider.generate("qwen-max", "Hi")
        _check_identity_headers(provider.session.post.call_args.kwargs)

    def test_generate_uses_openai_compatible_endpoint(self):
        """Qwen must use /chat/completions, not the legacy DashScope native path."""
        provider = self._provider()
        provider.session.post = MagicMock(return_value=_mock_response())
        provider.generate("qwen-max", "Hi")
        url = provider.session.post.call_args.args[0]
        assert url.endswith("/chat/completions")
        assert "services/aigc" not in url

    def test_generate_raises_without_api_key(self):
        with pytest.raises(ValueError, match="API key"):
            QwenProvider(QwenConfig()).generate("qwen-max", "Hi")


# ---------------------------------------------------------------------------
# xAI
# ---------------------------------------------------------------------------

class TestXAIProvider:
    def _provider(self):
        return XAIProvider(XAIConfig(api_key="xai-key"))

    def test_generate_returns_content(self):
        provider = self._provider()
        provider.session.post = MagicMock(return_value=_mock_response("Grok reply"))
        assert provider.generate("grok-3", "Hi") == "Grok reply"

    def test_generate_sends_identity_headers(self):
        provider = self._provider()
        provider.session.post = MagicMock(return_value=_mock_response())
        provider.generate("grok-3", "Hi")
        _check_identity_headers(provider.session.post.call_args.kwargs)

    def test_generate_uses_correct_endpoint(self):
        provider = self._provider()
        provider.session.post = MagicMock(return_value=_mock_response())
        provider.generate("grok-3", "Hi")
        url = provider.session.post.call_args.args[0]
        assert "x.ai" in url
        assert url.endswith("/chat/completions")

    def test_generate_raises_without_api_key(self):
        with pytest.raises(ValueError, match="API key"):
            XAIProvider(XAIConfig()).generate("grok-3", "Hi")


# ---------------------------------------------------------------------------
# OpenAI
# ---------------------------------------------------------------------------

class TestOpenAIProvider:
    def _provider(self):
        return OpenAIProvider(OpenAIConfig(api_key="sk-openai"))

    def test_generate_returns_content(self):
        provider = self._provider()
        provider.session.post = MagicMock(return_value=_mock_response("GPT reply"))
        assert provider.generate("gpt-4o", "Hi") == "GPT reply"

    def test_generate_sends_identity_headers(self):
        provider = self._provider()
        provider.session.post = MagicMock(return_value=_mock_response())
        provider.generate("gpt-4o", "Hi")
        _check_identity_headers(provider.session.post.call_args.kwargs)

    def test_generate_uses_correct_endpoint(self):
        provider = self._provider()
        provider.session.post = MagicMock(return_value=_mock_response())
        provider.generate("gpt-4o", "Hi")
        url = provider.session.post.call_args.args[0]
        assert "openai.com" in url
        assert url.endswith("/chat/completions")

    def test_generate_raises_without_api_key(self):
        with pytest.raises(ValueError, match="API key"):
            OpenAIProvider(OpenAIConfig()).generate("gpt-4o", "Hi")


# ---------------------------------------------------------------------------
# Zhipu
# ---------------------------------------------------------------------------

class TestZhipuProvider:
    def _provider(self):
        return ZhipuProvider(ZhipuConfig(api_key="zhipu-key"))

    def test_generate_returns_content(self):
        provider = self._provider()
        provider.session.post = MagicMock(return_value=_mock_response("GLM reply"))
        assert provider.generate("glm-4-flash", "Hi") == "GLM reply"

    def test_generate_sends_identity_headers(self):
        provider = self._provider()
        provider.session.post = MagicMock(return_value=_mock_response())
        provider.generate("glm-4-flash", "Hi")
        _check_identity_headers(provider.session.post.call_args.kwargs)

    def test_generate_uses_correct_endpoint(self):
        provider = self._provider()
        provider.session.post = MagicMock(return_value=_mock_response())
        provider.generate("glm-4-flash", "Hi")
        url = provider.session.post.call_args.args[0]
        assert "bigmodel.cn" in url
        assert url.endswith("/chat/completions")

    def test_generate_raises_without_api_key(self):
        with pytest.raises(ValueError, match="API key"):
            ZhipuProvider(ZhipuConfig()).generate("glm-4-flash", "Hi")


# ---------------------------------------------------------------------------
# OpenRouter
# ---------------------------------------------------------------------------

class TestOpenRouterProvider:
    def _provider(self):
        return OpenRouterProvider(OpenRouterConfig(api_key="sk-or-v1-key"))

    def test_generate_returns_content(self):
        provider = self._provider()
        provider.session.post = MagicMock(return_value=_mock_response("OR reply"))
        assert provider.generate("qwen/qwen-plus:free", "Hi") == "OR reply"

    def test_generate_sends_identity_headers(self):
        provider = self._provider()
        provider.session.post = MagicMock(return_value=_mock_response())
        provider.generate("qwen/qwen-plus:free", "Hi")
        _check_identity_headers(provider.session.post.call_args.kwargs)

    def test_generate_raises_without_api_key(self):
        with pytest.raises(ValueError, match="API key"):
            OpenRouterProvider(OpenRouterConfig()).generate("model", "Hi")


# ---------------------------------------------------------------------------
# Kilo — uses X-API-Key, not Bearer
# ---------------------------------------------------------------------------

class TestKiloProvider:
    def _provider(self):
        return KiloProvider(KiloConfig(api_key="kilo-secret"))

    def test_generate_returns_content(self):
        provider = self._provider()
        provider.session.post = MagicMock(return_value=_mock_response("Kilo reply"))
        assert provider.generate("kilocode/minimax-m2.5:free", "Hi") == "Kilo reply"

    def test_generate_sends_identity_headers(self):
        # Kilo stores identity headers at session level (set in __init__),
        # not per-request; verify they are present on the session.
        provider = self._provider()
        assert provider.session.headers.get("User-Agent") == OMNIRELAY_USER_AGENT
        assert provider.session.headers.get("X-Title") == OMNIRELAY_TITLE
        assert provider.session.headers.get("HTTP-Referer") == OMNIRELAY_REFERER
        assert provider.session.headers.get("Content-Type") == "application/json"

    def test_generate_sends_x_api_key_not_bearer(self):
        """Kilo uses X-API-Key auth stored in session headers, not Authorization Bearer."""
        provider = self._provider()
        assert provider.session.headers.get("X-API-Key") == "kilo-secret"
        assert "Authorization" not in provider.session.headers

    def test_generate_raises_without_api_key(self):
        with pytest.raises(ValueError, match="API key"):
            KiloProvider(KiloConfig()).generate("model", "Hi")
