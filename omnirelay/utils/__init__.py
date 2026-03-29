"""
工具函数
"""

import os
from typing import Optional

def get_env_var(key: str, default: Optional[str] = None) -> Optional[str]:
    """获取环境变量"""
    return os.getenv(key, default)


def ensure_api_key(provider: str) -> str:
    """确保 API Key 已设置"""
    key = os.getenv(f"{provider.upper()}_API_KEY")
    if not key:
        raise ValueError(
            f"{provider.upper()}_API_KEY not set. "
            f"Please get a free key from the provider's website."
        )
    return key
