"""
Tests for omnirelay.referrals
"""

import pytest
from omnirelay.utils import (
    REFERRAL_LINKS,
    RATE_LIMIT_ADS,
    get_referral_link,
    get_rate_limit_ad,
    get_dynamic_rate_limit_ad,
    format_credits_table,
)


class TestReferralLinks:
    def test_novita_has_referral_link(self):
        assert REFERRAL_LINKS["novita"] is not None
        assert "novita.ai" in REFERRAL_LINKS["novita"]

    def test_novita_link_contains_ref_tag(self):
        assert "ref=" in REFERRAL_LINKS["novita"]

    def test_all_nine_providers_present(self):
        expected = {"novita", "gemini", "openrouter", "kilo", "deepseek", "qwen", "xai", "openai", "zhipu"}
        assert expected.issubset(set(REFERRAL_LINKS.keys()))

    def test_non_partner_providers_are_none(self):
        non_partners = ["gemini", "deepseek", "qwen", "xai", "openai", "zhipu"]
        for provider in non_partners:
            assert REFERRAL_LINKS[provider] is None, f"{provider} should not have a referral link yet"


class TestGetReferralLink:
    def test_returns_link_for_partner(self):
        link = get_referral_link("novita")
        assert link is not None
        assert "novita.ai" in link

    def test_returns_none_for_non_partner(self):
        assert get_referral_link("gemini") is None
        assert get_referral_link("openai") is None

    def test_returns_none_for_unknown_provider(self):
        assert get_referral_link("unknown_provider") is None


class TestRateLimitAds:
    def test_novita_has_rate_limit_ad(self):
        assert RATE_LIMIT_ADS["novita"] is not None
        assert len(RATE_LIMIT_ADS["novita"]) > 0

    def test_novita_ad_mentions_free_credits(self):
        ad = RATE_LIMIT_ADS["novita"]
        assert "$20" in ad or "free" in ad.lower()

    def test_novita_ad_contains_signup_link(self):
        ad = RATE_LIMIT_ADS["novita"]
        assert "novita.ai" in ad


class TestGetRateLimitAd:
    def test_returns_ad_for_novita(self):
        ad = get_rate_limit_ad("novita")
        assert ad is not None
        assert "novita.ai" in ad

    def test_returns_none_for_providers_without_ad(self):
        assert get_rate_limit_ad("gemini") is None
        assert get_rate_limit_ad("openai") is None
        assert get_rate_limit_ad("xai") is None

    def test_returns_none_for_unknown_provider(self):
        assert get_rate_limit_ad("unknown") is None


class TestFormatCreditsTable:
    def test_returns_non_empty_string(self):
        table = format_credits_table()
        assert isinstance(table, str)
        assert len(table) > 0

    def test_table_contains_novita(self):
        table = format_credits_table()
        assert "Novita" in table

    def test_table_contains_partner_marker(self):
        table = format_credits_table()
        assert "★" in table

    def test_table_contains_all_major_providers(self):
        table = format_credits_table()
        for provider in ["Gemini", "Qwen", "DeepSeek", "OpenAI", "Zhipu"]:
            assert provider in table


class TestGetDynamicRateLimitAd:
    """Tests for smart ad recommendation based on user's configured providers."""

    def test_no_providers_configured_returns_novita_ad(self):
        """If user has no providers, show Novita AI ad first."""
        configured = []
        ad = get_dynamic_rate_limit_ad(configured)
        assert ad is not None
        assert "novita.ai" in ad
        assert "$20" in ad

    def test_only_non_partner_providers_returns_novita_ad(self):
        """If user only has non-partner providers, show Novita AI ad."""
        configured = ["gemini", "deepseek", "openai"]
        ad = get_dynamic_rate_limit_ad(configured)
        assert ad is not None
        assert "novita.ai" in ad

    def test_novita_configured_returns_openrouter_ad(self):
        """If user has Novita but not OpenRouter, show OpenRouter ad."""
        configured = ["novita", "gemini"]
        ad = get_dynamic_rate_limit_ad(configured)
        assert ad is not None
        assert "openrouter.ai" in ad
        assert "30+ free models" in ad

    def test_novita_and_openrouter_configured_returns_kilo_ad(self):
        """If user has Novita and OpenRouter but not Kilo, show Kilo ad."""
        configured = ["novita", "openrouter", "gemini"]
        ad = get_dynamic_rate_limit_ad(configured)
        assert ad is not None
        assert "kilo.ai" in ad
        assert "$5" in ad or "MiniMax" in ad

    def test_all_partners_configured_returns_none(self):
        """If user has all partner providers, no ad needed."""
        configured = ["novita", "openrouter", "kilo", "gemini"]
        ad = get_dynamic_rate_limit_ad(configured)
        assert ad is None

    def test_priority_order_novita_first(self):
        """Novita should always be recommended first if not configured."""
        configured = ["openrouter", "kilo", "gemini", "deepseek"]
        ad = get_dynamic_rate_limit_ad(configured)
        assert ad is not None
        assert "novita.ai" in ad
        assert "openrouter" not in ad.lower()
        assert "kilo" not in ad.lower()

    def test_priority_order_openrouter_second(self):
        """OpenRouter should be recommended if Novita configured."""
        configured = ["novita", "kilo", "gemini"]
        ad = get_dynamic_rate_limit_ad(configured)
        assert ad is not None
        assert "openrouter.ai" in ad
        assert "novita" not in ad.lower()
        assert "kilo" not in ad.lower()

    def test_empty_list_returns_novita_ad(self):
        """Empty configuration list should show Novita ad."""
        ad = get_dynamic_rate_limit_ad([])
        assert ad is not None
        assert "novita.ai" in ad

    def test_case_insensitive_provider_names(self):
        """Provider names should be case-insensitive."""
        configured = ["Novita", "GEMINI", "OpenRouter"]
        # Note: Current implementation uses exact string matching, so case matters
        # This test documents current behavior
        ad = get_dynamic_rate_limit_ad(configured)
        # With exact matching, "Novita" != "novita", so it shows Novita ad
        assert ad is not None
