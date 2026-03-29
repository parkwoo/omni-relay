"""
Tests for omnirelay.utils
"""

import os
import pytest
from omnirelay.utils import get_client_headers, ensure_api_key, get_env_var


class TestGetClientHeaders:
    def test_contains_required_identity_headers(self):
        headers = get_client_headers()
        assert "User-Agent" in headers
        assert "X-Title" in headers
        assert "HTTP-Referer" in headers
        assert "Content-Type" in headers

    def test_user_agent_identifies_omnirelay(self):
        headers = get_client_headers()
        assert "OmniRelay" in headers["User-Agent"]

    def test_content_type_is_json(self):
        headers = get_client_headers()
        assert headers["Content-Type"] == "application/json"

    def test_with_auth_header(self):
        headers = get_client_headers("Bearer sk-test-123")
        assert headers["Authorization"] == "Bearer sk-test-123"

    def test_without_auth_header_omits_authorization(self):
        headers = get_client_headers()
        assert "Authorization" not in headers

    def test_none_auth_omits_authorization(self):
        headers = get_client_headers(None)
        assert "Authorization" not in headers

    def test_returns_new_dict_each_call(self):
        h1 = get_client_headers()
        h2 = get_client_headers()
        h1["X-Custom"] = "mutated"
        assert "X-Custom" not in h2


class TestEnsureApiKey:
    def test_returns_key_when_set(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
        assert ensure_api_key("gemini") == "test-gemini-key"

    def test_raises_when_missing(self, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        with pytest.raises(ValueError, match="GEMINI_API_KEY"):
            ensure_api_key("gemini")

    def test_qwen_maps_to_dashscope(self, monkeypatch):
        monkeypatch.setenv("DASHSCOPE_API_KEY", "sk-dashscope")
        assert ensure_api_key("qwen") == "sk-dashscope"

    def test_kilo_maps_to_kilocode(self, monkeypatch):
        monkeypatch.setenv("KILOCODE_API_KEY", "kilo-key")
        assert ensure_api_key("kilo") == "kilo-key"

    def test_error_message_includes_export_hint(self, monkeypatch):
        monkeypatch.delenv("XAI_API_KEY", raising=False)
        with pytest.raises(ValueError, match="export XAI_API_KEY"):
            ensure_api_key("xai")


class TestGetEnvVar:
    def test_returns_value_when_set(self, monkeypatch):
        monkeypatch.setenv("MY_TEST_VAR", "hello")
        assert get_env_var("MY_TEST_VAR") == "hello"

    def test_returns_none_when_missing(self, monkeypatch):
        monkeypatch.delenv("MY_TEST_VAR", raising=False)
        assert get_env_var("MY_TEST_VAR") is None

    def test_returns_default_when_missing(self, monkeypatch):
        monkeypatch.delenv("MY_TEST_VAR", raising=False)
        assert get_env_var("MY_TEST_VAR", "fallback") == "fallback"
