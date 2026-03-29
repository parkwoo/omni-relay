"""
Utility helpers for omni-relay
"""

import os
from typing import Optional

from ._referrals import (  # noqa: F401
    REFERRAL_LINKS,
    RATE_LIMIT_ADS,
    get_referral_link,
    get_rate_limit_ad,
    get_dynamic_rate_limit_ad,
    format_credits_table,
)

# Import version dynamically from package
from .. import __version__

# Sent with every outbound API request so providers can identify our traffic
OMNIRELAY_USER_AGENT = f"OmniRelay/{__version__} (https://omnirelay.wawoo.jp)"
OMNIRELAY_TITLE = "OmniRelay"
OMNIRELAY_REFERER = "https://github.com/parkwoo/omni-relay"  # GitHub repository


def get_client_headers(auth_header: Optional[str] = None) -> dict:
    """
    Return a base set of headers to include in every provider API request.

    These headers identify OmniRelay to the upstream provider and are
    required by some APIs (e.g. OpenRouter mandates HTTP-Referer / X-Title).

    Args:
        auth_header: The value for the Authorization header, e.g.
                     "Bearer sk-abc123". If None the key is omitted.

    Returns:
        A dict ready to pass to requests.Session.request(headers=...).
    """
    headers = {
        "Content-Type": "application/json",
        "User-Agent": OMNIRELAY_USER_AGENT,
        "X-Title": OMNIRELAY_TITLE,
        "HTTP-Referer": OMNIRELAY_REFERER,
    }
    if auth_header:
        headers["Authorization"] = auth_header
    return headers


def get_env_var(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get an environment variable, returning default if not set."""
    return os.environ.get(key, default)


def ensure_api_key(provider: str) -> str:
    """
    Return the API key for the given provider, raising a clear error if unset.

    Special cases:
      - qwen  → DASHSCOPE_API_KEY
      - kilo  → KILOCODE_API_KEY
    """
    _env_var_map = {
        "qwen": "DASHSCOPE_API_KEY",
        "kilo": "KILOCODE_API_KEY",
    }
    env_var = _env_var_map.get(provider, f"{provider.upper()}_API_KEY")
    key = os.environ.get(env_var)
    if not key:
        raise ValueError(
            f"{env_var} is not set. "
            f"Export it with: export {env_var}='your-key-here'"
        )
    return key
