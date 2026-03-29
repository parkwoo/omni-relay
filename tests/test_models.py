"""
Tests for omnirelay.models
"""

import pytest
from omnirelay.models import (
    ModelInfo,
    AVAILABLE_MODELS,
    get_all_models,
    get_model_by_id,
    get_models_by_provider,
    rank_models_by_quality,
)

ALL_PROVIDERS = {"gemini", "openrouter", "kilo", "deepseek", "novita", "qwen", "xai", "openai", "zhipu"}


class TestAvailableModels:
    def test_total_model_count(self):
        assert len(AVAILABLE_MODELS) >= 9  # at least one per provider

    def test_all_nine_providers_represented(self):
        providers_in_list = {m.provider for m in AVAILABLE_MODELS}
        assert ALL_PROVIDERS == providers_in_list

    def test_quality_scores_in_range(self):
        for m in AVAILABLE_MODELS:
            assert 0 <= m.quality_score <= 10, f"{m.model_id} score out of range"

    def test_context_lengths_positive(self):
        for m in AVAILABLE_MODELS:
            assert m.context_length > 0, f"{m.model_id} has non-positive context length"

    def test_model_ids_unique(self):
        ids = [m.model_id for m in AVAILABLE_MODELS]
        assert len(ids) == len(set(ids)), "Duplicate model_id found"


class TestGetAllModels:
    def test_returns_list(self):
        assert isinstance(get_all_models(), list)

    def test_returns_model_info_instances(self):
        assert all(isinstance(m, ModelInfo) for m in get_all_models())


class TestGetModelsByProvider:
    def test_gemini_models(self):
        models = get_models_by_provider("gemini")
        assert len(models) > 0
        assert all(m.provider == "gemini" for m in models)

    def test_deepseek_models(self):
        models = get_models_by_provider("deepseek")
        assert len(models) > 0
        assert any(m.model_id == "deepseek/deepseek-reasoner" for m in models)

    def test_novita_models(self):
        models = get_models_by_provider("novita")
        assert len(models) > 0

    def test_qwen_models(self):
        models = get_models_by_provider("qwen")
        assert len(models) > 0
        assert any(m.model_id == "qwen/qwen-max" for m in models)

    def test_xai_models(self):
        models = get_models_by_provider("xai")
        assert len(models) > 0
        assert any(m.model_id == "xai/grok-3" for m in models)

    def test_openai_models(self):
        models = get_models_by_provider("openai")
        assert len(models) > 0
        assert any(m.model_id == "openai/gpt-4o" for m in models)

    def test_zhipu_models(self):
        models = get_models_by_provider("zhipu")
        assert len(models) > 0
        assert any(m.model_id == "zhipu/glm-4-flash" for m in models)

    def test_unknown_provider_returns_empty(self):
        assert get_models_by_provider("nonexistent") == []


class TestGetModelById:
    def test_lookup_by_model_id(self):
        model = get_model_by_id("deepseek-reasoner")
        assert model is not None
        assert model.model_id in ["deepseek-reasoner", "deepseek/deepseek-reasoner"]  # Support both formats
        assert model.provider == "deepseek"

    def test_lookup_grok(self):
        model = get_model_by_id("grok-3")
        assert model is not None
        assert model.model_id in ["grok-3", "xai/grok-3"]  # Support both formats
        assert model.provider == "xai"

    def test_lookup_gpt4o(self):
        model = get_model_by_id("gpt-4o")
        assert model is not None
        assert model.model_id in ["gpt-4o", "openai/gpt-4o"]  # Support both formats
        assert model.provider == "openai"

    def test_lookup_glm_flash(self):
        model = get_model_by_id("glm-4-flash")
        assert model is not None
        assert model.model_id in ["glm-4-flash", "zhipu/glm-4-flash"]  # Support both formats
        assert model.provider == "zhipu"

    def test_lookup_by_name(self):
        model = get_model_by_id("Gemini 2.5 Flash")
        assert model is not None
        assert "gemini-2.5-flash" in model.model_id  # Just check it contains the base ID

    def test_unknown_id_returns_none(self):
        assert get_model_by_id("does-not-exist") is None


class TestRankModelsByQuality:
    def test_sorted_descending(self):
        models = rank_models_by_quality()
        for i in range(len(models) - 1):
            assert models[i].quality_score >= models[i + 1].quality_score

    def test_all_models_included(self):
        assert len(rank_models_by_quality()) == len(AVAILABLE_MODELS)

    def test_highest_score_first(self):
        models = rank_models_by_quality()
        max_score = max(m.quality_score for m in AVAILABLE_MODELS)
        assert models[0].quality_score == max_score
