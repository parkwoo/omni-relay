"""
Tests for Kilo Gateway provider
"""

import pytest
from unittest.mock import MagicMock, patch

from omnirelay.config import KiloConfig
from omnirelay.providers.kilo import KiloProvider
from omnirelay.utils import OMNIRELAY_USER_AGENT, OMNIRELAY_TITLE, OMNIRELAY_REFERER


def _mock_response(status_code=200, json_data=None):
    """Return a mock requests.Response"""
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data or {}
    mock.raise_for_status.return_value = None
    return mock


def _check_identity_headers(call_kwargs: dict):
    """Assert that OmniRelay identity headers were sent"""
    headers = call_kwargs.get("headers", {})
    assert headers.get("User-Agent") == OMNIRELAY_USER_AGENT
    assert headers.get("X-Title") == OMNIRELAY_TITLE
    assert headers.get("HTTP-Referer") == OMNIRELAY_REFERER
    assert headers.get("Content-Type") == "application/json"


class TestKiloProvider:
    def _provider(self):
        return KiloProvider(KiloConfig(api_key="kilo-secret"))

    def test_generate_returns_content(self):
        provider = self._provider()
        provider.session.post = MagicMock(return_value=_mock_response(
            json_data={"choices": [{"message": {"content": "Kilo reply"}}]}
        ))
        result = provider.generate("minimax/minimax-m2.5", "Hi")
        assert result == "Kilo reply"

    def test_generate_sends_identity_headers(self):
        # Kilo stores identity headers at session level (set in __init__),
        # not per-request; verify they are present on the session.
        provider = self._provider()
        assert provider.session.headers.get("User-Agent") == OMNIRELAY_USER_AGENT
        assert provider.session.headers.get("X-Title") == OMNIRELAY_TITLE
        assert provider.session.headers.get("HTTP-Referer") == OMNIRELAY_REFERER
        assert provider.session.headers.get("Content-Type") == "application/json"

    def test_generate_uses_correct_endpoint(self):
        provider = self._provider()
        provider.session.post = MagicMock(return_value=_mock_response(
            json_data={"choices": [{"message": {"content": "test"}}]}
        ))
        provider.generate("minimax/minimax-m2.5", "Hi")
        url = provider.session.post.call_args.args[0]
        assert "api.kilo.ai" in url
        assert url.endswith("/v1/chat/completions")

    def test_generate_raises_without_api_key(self):
        provider = KiloProvider(KiloConfig())
        with pytest.raises(ValueError, match="API key"):
            provider.generate("model", "Hi")

    def test_is_available_true_with_key(self):
        assert self._provider().is_available()

    def test_is_available_false_without_key(self):
        assert not KiloProvider(KiloConfig()).is_available()

    def test_list_models_delegates_to_models_registry(self):
        """list_models() should delegate to centralized model registry"""
        provider = self._provider()

        models = provider.list_models()
        assert len(models) > 0
        assert all(m.provider == "kilo" for m in models)
        assert any(m.is_free for m in models)
