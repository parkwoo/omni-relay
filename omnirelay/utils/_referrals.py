"""
Partner referral links and rate-limit promotional messages.

To add a new partner:
  1. Add provider key to PROVIDER_METADATA with referral_link
  2. Add a RATE_LIMIT_ADS entry for dynamic ad display
  
Dynamic Ad Logic:
  - If Novita not configured → show Novita ad ($20 credit)
  - If Novita configured but OpenRouter not → show OpenRouter ad (30+ free models)
  - If both above configured but Kilo not → show Kilo ad ($5 + free MiniMax)
  - If all partners configured → no ad (user has all free tiers)
"""

from typing import Optional
from pathlib import Path
import json

# Provider metadata including display names, signup URLs, and referral links
PROVIDER_METADATA: dict[str, dict[str, str]] = {
    "novita": {
        "display_name": "Novita AI",
        "display_url": "https://novita.ai",  # Show in table
        "signup_url": "https://novita.ai/?ref=mjdjzgr&utm_source=affiliate",  # Actual link
        "referral_link": "https://novita.ai/?ref=mjdjzgr&utm_source=affiliate",  # Partner link
    },
    "openrouter": {
        "display_name": "OpenRouter",
        "display_url": "https://openrouter.ai/signup",
        "signup_url": "https://openrouter.ai/signup?ref=omnirelay",
        "referral_link": "https://openrouter.ai/signup?ref=omnirelay",
    },
    "kilo": {
        "display_name": "Kilo Gateway",
        "display_url": "https://kilo.ai/signup",
        "signup_url": "https://kilo.ai/signup?ref=omnirelay",
        "referral_link": "https://kilo.ai/signup?ref=omnirelay",
    },
    "xai": {
        "display_name": "xAI (Grok)",
        "display_url": "https://console.x.ai",
        "signup_url": "https://console.x.ai",
        "referral_link": None,
    },
    "gemini": {
        "display_name": "Google Gemini",
        "display_url": "https://aistudio.google.com",
        "signup_url": "https://aistudio.google.com",
        "referral_link": None,
    },
    "qwen": {
        "display_name": "Alibaba Qwen",
        "display_url": "https://dashscope-intl.aliyuncs.com",
        "signup_url": "https://dashscope-intl.aliyuncs.com",
        "referral_link": None,
    },
    "deepseek": {
        "display_name": "DeepSeek",
        "display_url": "https://platform.deepseek.com",
        "signup_url": "https://platform.deepseek.com",
        "referral_link": None,
    },
    "openai": {
        "display_name": "OpenAI",
        "display_url": "https://platform.openai.com/signup",
        "signup_url": "https://platform.openai.com/signup",
        "referral_link": None,
    },
    "zhipu": {
        "display_name": "Zhipu AI",
        "display_url": "https://open.bigmodel.cn",  # 国内版
        "signup_url": "https://open.bigmodel.cn",  # 国内版
        "referral_link": None,
    },
}

# Legacy compatibility - extract referral links from metadata
REFERRAL_LINKS: dict[str, Optional[str]] = {
    provider: metadata.get("referral_link")
    for provider, metadata in PROVIDER_METADATA.items()
}

# Default credit descriptions (used if not in JSON)
DEFAULT_CREDITS: dict[str, str] = {
    "novita": "$20 one-time",
    "openrouter": "30+ free models",
    "kilo": "$5 + MiniMax M2.5 free",
    "xai": "$25 + $150/month*",
    "gemini": "1M tokens/min",
    "qwen": "1M+ tokens/month",
    "deepseek": "$5 one-time",
    "openai": "$5 trial",
    "zhipu": "GLM-4.x-Flash free†",
}

# Ads shown when a rate-limit error is encountered.
# Dynamic ads based on which providers user has already configured
RATE_LIMIT_ADS: dict[str, Optional[str]] = {
    "novita": (
        "💡 Need more capacity?  Sign up for Novita AI and get $20 free credits:\n"
        "   https://novita.ai/?ref=mjdjzgr&utm_source=affiliate\n"
        "   • DeepSeek R1 + Llama 3.1 70B  •  Low latency  •  No rate limits on paid tier"
    ),
    "openrouter": (
        "💡 Need more free models?  Sign up for OpenRouter and get 30+ free models:\n"
        "   https://openrouter.ai/signup?ref=omnirelay\n"
        "   • No credit card required  •  30+ free models  •  Instant access"
    ),
    "kilo": (
        "💡 Need more capacity?  Sign up for Kilo Gateway and get $5 credit + free MiniMax M2.5:\n"
        "   https://kilo.ai/signup?ref=omnirelay\n"
        "   • MiniMax M2.5 free  •  $5 credit  •  500+ models"
    ),
}

# Priority order for showing ads (most valuable first)
AD_PRIORITY_ORDER = ["novita", "openrouter", "kilo"]


def _load_credits_from_json() -> dict[str, str]:
    """Load credit descriptions from free-models.json if available."""
    json_path = Path(__file__).parent.parent / "data" / "free-models.json"
    if not json_path.exists():
        return DEFAULT_CREDITS

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        credits = {}
        for provider_name, provider_data in data.get("providers", {}).items():
            # Use default credits for consistency (more concise)
            if provider_name in DEFAULT_CREDITS:
                credits[provider_name] = DEFAULT_CREDITS[provider_name]
            else:
                free_count = len(provider_data.get("free_models", []))
                paid_count = len(provider_data.get("paid_models", []))
                note = provider_data.get("note", "")

                # Build description if no default
                if free_count > 0:
                    credits[provider_name] = f"{free_count}+ free models"
                elif paid_count > 0:
                    credits[provider_name] = "Paid models available"
                elif note:
                    credits[provider_name] = note[:40]  # Truncate long notes
                else:
                    credits[provider_name] = "See website"

        return credits if credits else DEFAULT_CREDITS
    except Exception:
        return DEFAULT_CREDITS


def get_referral_link(provider: str) -> Optional[str]:
    """Return the referral link for a provider, or None if not a partner."""
    return REFERRAL_LINKS.get(provider)


def get_rate_limit_ad(provider: str) -> Optional[str]:
    """Return the ad copy to show when *provider* hits a rate limit, or None."""
    return RATE_LIMIT_ADS.get(provider)


def get_dynamic_rate_limit_ad(configured_providers: list[str]) -> Optional[str]:
    """
    Return dynamic ad based on which providers user has already configured.
    
    Priority:
    1. If Novita not configured → show Novita ad
    2. If Novita configured but OpenRouter not → show OpenRouter ad
    3. If both above configured but Kilo not → show Kilo ad
    4. If all partners configured → return None (no ad)
    
    Args:
        configured_providers: List of provider keys user has API keys for
                             (e.g., ['novita', 'gemini', 'openrouter'])
    
    Returns:
        Ad string or None if all partner providers are configured
    """
    configured_set = set(configured_providers)
    
    # Check each partner in priority order
    for provider in AD_PRIORITY_ORDER:
        if provider not in configured_set:
            return RATE_LIMIT_ADS.get(provider)
    
    # All partners configured - no ad needed
    return None


def format_credits_table() -> str:
    """Return a formatted table of providers with signup links."""
    # Load credits dynamically
    credits_map = _load_credits_from_json()

    # Build table rows from metadata
    rows = []
    for provider_key, metadata in PROVIDER_METADATA.items():
        display_name = metadata["display_name"]
        # Use display_url for cleaner table output (without referral params)
        display_url = metadata.get("display_url", metadata["signup_url"])
        # Use signup_url (with referral params) as the actual link
        actual_url = metadata["signup_url"]
        credits = credits_map.get(provider_key, DEFAULT_CREDITS.get(provider_key, "See website"))

        rows.append((display_name, credits, display_url, actual_url, provider_key))

    # Sort by partner status first, then by name
    rows.sort(key=lambda x: (x[4] not in REFERRAL_LINKS or REFERRAL_LINKS[x[4]] is None, x[0]))

    # Format table
    lines = [
        "Provider              Free Credits              Sign Up",
        "-" * 88,
    ]

    for provider, credits, display_url, actual_url, provider_key in rows:
        partner_tag = " ★" if REFERRAL_LINKS.get(provider_key) else ""
        # Truncate long descriptions if needed
        if len(credits) > 24:
            credits = credits[:21] + "..."
        # Note: In terminal, users can't click links, so we show the display URL
        # The actual_url (with referral params) is what they would use if copying
        lines.append(f"{provider:<22}{credits:<26}{display_url}{partner_tag}")

    lines.append("\n★ = OmniRelay partner link (supports the project)")
    return "\n".join(lines)
