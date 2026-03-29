"""
Model definitions for all supported providers

For dynamic model loading from free-models.json, use:
    from omnirelay.data import get_free_models, get_model_by_id
"""

from typing import Optional, Literal, Dict
from pydantic import BaseModel, Field
from pathlib import Path
import json


class ModelInfo(BaseModel):
    """Model information"""

    name: str
    provider: Literal["gemini", "openrouter", "kilo", "deepseek", "novita", "qwen", "xai", "openai", "zhipu"]
    model_id: str
    context_length: int
    is_free: bool = True
    speed: Literal["fast", "medium", "slow"] = "medium"
    quality_score: float = Field(ge=0, le=10)
    popular: bool = False


# Model ID aliases for unified lookup
# Maps short model IDs to full IDs with provider prefix
MODEL_ALIASES: Dict[str, str] = {
    # Zhipu
    "glm-4.7-flash": "zhipu/glm-4.7-flash",
    "glm-4.6-flash": "zhipu/glm-4.6-flash",
    "glm-4.5-flash": "zhipu/glm-4.5-flash",
    "glm-4-flash": "zhipu/glm-4-flash",
    # Gemini
    "gemini-2.5-flash": "gemini/gemini-2.5-flash",
    "gemini-2.0-flash": "gemini/gemini-2.0-flash",
    "gemini-1.5-flash": "gemini/gemini-1.5-flash",
    # DeepSeek
    "deepseek-reasoner": "deepseek/deepseek-reasoner",
    "deepseek-chat": "deepseek/deepseek-chat",
    "deepseek-r1": "deepseek/deepseek-reasoner",
    "r1": "deepseek/deepseek-reasoner",
    # Qwen
    "qwen-max": "qwen/qwen-max",
    "qwen-plus": "qwen/qwen-plus",
    "qwen-turbo": "qwen/qwen-turbo",
    # xAI
    "grok-3": "xai/grok-3",
    "grok-3-mini": "xai/grok-3-mini",
    # OpenAI
    "gpt-4o": "openai/gpt-4o",
    "gpt-4o-mini": "openai/gpt-4o-mini",
    # Novita (models already have provider prefix)
    "deepseek/deepseek-r1": "novita/deepseek/deepseek-r1",
    "meta-llama/llama-3.1-70b-instruct": "novita/meta-llama/llama-3.1-70b-instruct",
}


def _infer_speed_tier(model_id: str) -> str:
    """Infer speed tier from model ID"""
    model_id_lower = model_id.lower()

    if any(x in model_id_lower for x in ["flash", "turbo", "mini", "fast", "lite"]):
        return "fast"
    return "medium"


def _calculate_quality_score(model_id: str, context_length: int, source: str = "static") -> float:
    """Calculate quality score based on model ID, context length, and data source"""
    base_score = 8.0

    # Data source confidence
    source_confidence = {
        "api": 0.5,      # API data most reliable
        "scraper": -0.3,  # Scraper data less reliable
        "static": 0.0     # Static data baseline
    }
    base_score += source_confidence.get(source, 0.0)

    # Model reputation bonuses
    if any(x in model_id for x in ["deepseek-reasoner", "deepseek-r1", "r1"]):
        base_score += 1.5
    elif any(x in model_id for x in ["grok-3"]):
        base_score += 1.3
    elif any(x in model_id for x in ["gpt-4o"]):
        base_score += 1.2
    elif any(x in model_id for x in ["gemini-2.5", "gemini-2.0"]):
        base_score += 1.0
    elif any(x in model_id for x in ["glm-4.7", "glm-4.6"]):
        base_score += 0.8
    elif any(x in model_id for x in ["qwen-max"]):
        base_score += 0.7

    # Context length bonus
    if context_length >= 1_000_000:
        base_score += 0.5
    elif context_length >= 200_000:
        base_score += 0.3
    elif context_length >= 128_000:
        base_score += 0.2

    return min(base_score, 10.0)


def _is_popular_model(model_id: str) -> bool:
    """Check if model is considered popular"""
    model_id_lower = model_id.lower()

    # Popular indicators
    popular_keywords = [
        "flash",      # Flash models are popular
        "r1",         # DeepSeek R1
        "reasoner",   # Reasoner models
        "grok-3",     # Grok 3
        "gpt-4o",     # GPT-4o
        "qwen-max",   # Qwen Max
        "llama-3",    # Llama 3 series
        "mini",       # Mini versions
    ]

    return any(keyword in model_id_lower for keyword in popular_keywords)


def _normalize_model_id(model_id: str, provider: str) -> str:
    """Normalize model ID to include provider prefix if needed

    Rules:
      - If already has "/" path separator, keep as-is
      - If in MODEL_ALIASES, use the alias (which may include provider prefix)
      - Otherwise, add provider prefix
    """
    # Already has provider prefix or path
    if "/" in model_id:
        return model_id

    # Check alias mapping first (may add provider prefix)
    if model_id in MODEL_ALIASES:
        return MODEL_ALIASES[model_id]

    # Add provider prefix
    return f"{provider}/{model_id}"


# Static fallback models (used if JSON not available)
STATIC_MODELS = [
    # Gemini models
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
        quality_score=9.1
    ),
    ModelInfo(
        name="Gemini 1.5 Flash",
        provider="gemini",
        model_id="gemini-1.5-flash",
        context_length=280_000,
        speed="fast",
        quality_score=8.5
    ),

    # DeepSeek models
    ModelInfo(
        name="DeepSeek R1 (Reasoner)",
        provider="deepseek",
        model_id="deepseek-reasoner",
        context_length=128_000,
        speed="medium",
        quality_score=9.5,
        popular=True
    ),
    ModelInfo(
        name="DeepSeek V3 (Chat)",
        provider="deepseek",
        model_id="deepseek-chat",
        context_length=128_000,
        speed="medium",
        quality_score=9.2
    ),

    # Novita AI models
    ModelInfo(
        name="DeepSeek R1 (via Novita)",
        provider="novita",
        model_id="deepseek/deepseek-r1",
        context_length=64_000,
        speed="medium",
        quality_score=9.4,
        popular=True
    ),
    ModelInfo(
        name="Llama 3.1 70B (via Novita)",
        provider="novita",
        model_id="meta-llama/llama-3.1-70b-instruct",
        context_length=131_000,
        speed="fast",
        quality_score=8.9
    ),

    # xAI models
    ModelInfo(
        name="Grok 3",
        provider="xai",
        model_id="grok-3",
        context_length=131_000,
        speed="medium",
        quality_score=9.2,
        popular=True
    ),
    ModelInfo(
        name="Grok 3 Mini",
        provider="xai",
        model_id="grok-3-mini",
        context_length=131_000,
        speed="fast",
        quality_score=8.7
    ),

    # OpenAI models
    ModelInfo(
        name="GPT-4o",
        provider="openai",
        model_id="gpt-4o",
        context_length=128_000,
        speed="medium",
        quality_score=9.3,
        popular=True
    ),
    ModelInfo(
        name="GPT-4o Mini",
        provider="openai",
        model_id="gpt-4o-mini",
        context_length=128_000,
        speed="fast",
        quality_score=8.6
    ),

    # Qwen models
    ModelInfo(
        name="Qwen Max",
        provider="qwen",
        model_id="qwen-max",
        context_length=32_000,
        speed="fast",
        quality_score=9.0,
        popular=True
    ),
    ModelInfo(
        name="Qwen Plus",
        provider="qwen",
        model_id="qwen-plus",
        context_length=131_000,
        speed="fast",
        quality_score=8.7
    ),
    ModelInfo(
        name="Qwen Turbo",
        provider="qwen",
        model_id="qwen-turbo",
        context_length=131_000,
        speed="fast",
        quality_score=8.3
    ),

    # Zhipu AI models
    ModelInfo(
        name="GLM-4 Flash",
        provider="zhipu",
        model_id="glm-4-flash",
        context_length=200_000,
        speed="fast",
        quality_score=8.2
    ),
    ModelInfo(
        name="GLM-4 Air",
        provider="zhipu",
        model_id="glm-4-air",
        context_length=128_000,
        speed="fast",
        quality_score=8.5
    ),
    ModelInfo(
        name="GLM-4",
        provider="zhipu",
        model_id="glm-4",
        context_length=128_000,
        speed="medium",
        quality_score=8.8
    ),

    # OpenRouter free models
    ModelInfo(
        name="OpenRouter Free Router",
        provider="openrouter",
        model_id="openrouter/free",
        context_length=200_000,
        speed="fast",
        quality_score=8.5
    ),
    ModelInfo(
        name="Qwen3 Coder (OpenRouter)",
        provider="openrouter",
        model_id="qwen/qwen3-coder:free",
        context_length=262_144,
        speed="fast",
        quality_score=8.7
    ),
    ModelInfo(
        name="NVIDIA Nemotron Super (OpenRouter)",
        provider="openrouter",
        model_id="nvidia/nemotron-3-super-120b-a12b:free",
        context_length=262_144,
        speed="medium",
        quality_score=8.6
    ),
    ModelInfo(
        name="MiniMax M2.5 (OpenRouter)",
        provider="openrouter",
        model_id="minimax/minimax-m2.5:free",
        context_length=196_608,
        speed="fast",
        quality_score=8.4
    ),
    ModelInfo(
        name="GPT-OSS 120B (OpenRouter)",
        provider="openrouter",
        model_id="openai/gpt-oss-120b:free",
        context_length=131_072,
        speed="medium",
        quality_score=8.3
    ),
    ModelInfo(
        name="GLM-4.5 Air (OpenRouter)",
        provider="openrouter",
        model_id="z-ai/glm-4.5-air:free",
        context_length=131_072,
        speed="fast",
        quality_score=8.2
    ),
    ModelInfo(
        name="Llama 3.3 70B (OpenRouter)",
        provider="openrouter",
        model_id="meta-llama/llama-3.3-70b-instruct:free",
        context_length=65_536,
        speed="fast",
        quality_score=8.5
    ),

    # Kilo Gateway models
    ModelInfo(
        name="MiniMax M2.5 (Free)",
        provider="kilo",
        model_id="minimax/minimax-m2.5",
        context_length=204_800,
        is_free=True,
        speed="fast",
        quality_score=8.8,
        popular=True
    ),
    ModelInfo(
        name="NVIDIA Nemotron 3 Super (Free)",
        provider="kilo",
        model_id="nvidia/nemotron-3-super-120b-a12b",
        context_length=262_144,
        is_free=True,
        speed="medium",
        quality_score=8.6
    ),
    ModelInfo(
        name="Arcee AI Trinity Large Preview (Free)",
        provider="kilo",
        model_id="arcee-ai/trinity-large-preview",
        context_length=131_072,
        is_free=True,
        speed="fast",
        quality_score=8.4
    ),
    ModelInfo(
        name="GLM-4.7 Flash",
        provider="kilo",
        model_id="z-ai/glm-4.7-flash",
        context_length=200_000,
        is_free=False,
        speed="fast",
        quality_score=8.2
    ),
    ModelInfo(
        name="MiniMax M2.7",
        provider="kilo",
        model_id="minimax/minimax-m2.7",
        context_length=204_800,
        is_free=False,
        speed="fast",
        quality_score=9.0,
        popular=True
    ),
]

# Try to load dynamic models from JSON
def _load_models_from_json() -> list[ModelInfo]:
    """Load models from free-models.json with intelligent attribute inference

    Loads both free_models and paid_models (paid models are marked with is_free=False)
    This allows OmniRelay to route both free and paid models based on user's API keys.
    """
    json_path = Path(__file__).parent / "data" / "free-models.json"
    if not json_path.exists():
        return STATIC_MODELS

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        models = []
        providers = data.get("providers", {})

        for provider_name, provider_data in providers.items():
            source = provider_data.get("source", "static")

            # Load free models
            for model in provider_data.get("free_models", []):
                model_id = model.get("model_id", "")
                context_length = model.get("context_length", 0)
                normalized_id = _normalize_model_id(model_id, provider_name)

                speed = _infer_speed_tier(normalized_id)
                quality_score = _calculate_quality_score(normalized_id, context_length, source)
                popular = _is_popular_model(normalized_id)

                models.append(ModelInfo(
                    name=model.get("name", normalized_id),
                    provider=provider_name,
                    model_id=normalized_id,
                    context_length=context_length,
                    is_free=True,
                    speed=speed,
                    quality_score=quality_score,
                    popular=popular
                ))

            # Load paid models (marked as is_free=False)
            for model in provider_data.get("paid_models", []):
                model_id = model.get("model_id", "")
                context_length = model.get("context_length", 0)
                normalized_id = _normalize_model_id(model_id, provider_name)

                speed = _infer_speed_tier(normalized_id)
                quality_score = _calculate_quality_score(normalized_id, context_length, source)
                popular = _is_popular_model(normalized_id)

                models.append(ModelInfo(
                    name=model.get("name", normalized_id),
                    provider=provider_name,
                    model_id=normalized_id,
                    context_length=context_length,
                    is_free=False,  # Mark as paid
                    speed=speed,
                    quality_score=quality_score,
                    popular=popular
                ))

        return models if models else STATIC_MODELS
    except Exception:
        return STATIC_MODELS

# Use dynamic models if available, fallback to static
AVAILABLE_MODELS = _load_models_from_json()


def get_models_by_provider(provider: str) -> list[ModelInfo]:
    """Get models filtered by provider"""
    return [m for m in AVAILABLE_MODELS if m.provider == provider]


def get_all_models() -> list[ModelInfo]:
    """Get all available models"""
    return AVAILABLE_MODELS


def get_model_by_id(model_id: str) -> Optional[ModelInfo]:
    """Get model by model_id, alias, or name (case-insensitive)"""
    # First, try exact match
    for model in AVAILABLE_MODELS:
        if model.model_id == model_id:
            return model

    # Try alias mapping
    normalized_id = MODEL_ALIASES.get(model_id, model_id)
    for model in AVAILABLE_MODELS:
        if model.model_id == normalized_id:
            return model

    # Try name match (case-insensitive)
    model_id_lower = model_id.lower()
    for model in AVAILABLE_MODELS:
        if model.name.lower() == model_id_lower:
            return model

    return None


def rank_models_by_quality() -> list[ModelInfo]:
    """Sort models by quality score descending, removing duplicates by base model name"""
    sorted_models = sorted(AVAILABLE_MODELS, key=lambda m: m.quality_score, reverse=True)
    
    # Remove duplicates: keep highest scored version of each base model
    seen: dict = {}
    for model in sorted_models:
        # Extract base model name (e.g., "glm-4.7-flash" from "zhipu/glm-4.7-flash")
        base_name = model.model_id.split("/")[-1].split(":")[0] if "/" in model.model_id else model.model_id
        if base_name not in seen:
            seen[base_name] = model
    
    return list(seen.values())
