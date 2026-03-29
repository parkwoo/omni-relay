"""
模型定义模块
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


class ModelInfo(BaseModel):
    """模型信息"""

    name: str
    provider: Literal["gemini", "openrouter", "kilo"]
    model_id: str
    context_length: int
    is_free: bool = True
    speed: Literal["fast", "medium", "slow"] = "medium"
    quality_score: float = Field(ge=0, le=10)
    popular: bool = False


# 可用模型列表
AVAILABLE_MODELS = [
    # Gemini 模型
    ModelInfo(
        name="Gemini 2.5 Flash",
        provider="gemini",
        model_id="gemini-2.5-flash",
        context_length=1_000_000,
        speed="fast",
        quality_score=9.5,
        popular=True
    ),
    ModelInfo(
        name="Gemini 2.0 Flash",
        provider="gemini",
        model_id="gemini-2.0-flash",
        context_length=1_000_000,
        speed="fast",
        quality_score=9.0
    ),
    ModelInfo(
        name="Gemini 1.5 Flash",
        provider="gemini",
        model_id="gemini-1.5-flash",
        context_length=280_000,
        speed="fast",
        quality_score=8.5
    ),

    # OpenRouter 免费模型
    ModelInfo(
        name="Qwen Plus",
        provider="openrouter",
        model_id="qwen/qwen-plus:free",
        context_length=32768,
        speed="fast",
        quality_score=9.0
    ),
    ModelInfo(
        name="NVIDIA Nemotron",
        provider="openrouter",
        model_id="nvidia/nemotron:free",
        context_length=128000,
        speed="slow",
        quality_score=8.5
    ),
    ModelInfo(
        name="Xiaomi Mimo v2 Pro",
        provider="openrouter",
        model_id="xiaomi/mimo-v2-pro:free",
        context_length=32000,
        speed="fast",
        quality_score=8.0
    ),

    # Kilo Gateway 模型
    ModelInfo(
        name="MiniMax M2.5",
        provider="kilo",
        model_id="kilocode/minimax-m2.5:free",
        context_length=32768,
        speed="fast",
        quality_score=8.8
    ),
]


def get_models_by_provider(provider: str) -> list[ModelInfo]:
    """按提供商获取模型"""
    return [m for m in AVAILABLE_MODELS if m.provider == provider]


def get_all_models() -> list[ModelInfo]:
    """获取所有可用模型"""
    return AVAILABLE_MODELS


def get_model_by_id(model_id: str) -> Optional[ModelInfo]:
    """按 model_id 获取模型"""
    for model in AVAILABLE_MODELS:
        if model.model_id == model_id or model.name.lower() == model_id.lower():
            return model
    return None


def rank_models_by_quality() -> list[ModelInfo]:
    """按质量评分排序模型"""
    return sorted(AVAILABLE_MODELS, key=lambda m: m.quality_score, reverse=True)
