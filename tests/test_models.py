"""
测试模型模块
"""

import pytest
from omnirelay.models import (
    ModelInfo,
    get_all_models,
    get_model_by_id,
    get_models_by_provider,
    rank_models_by_quality,
)


class TestModels:
    """测试模型相关函数"""

    def test_get_all_models(self):
        """测试获取所有模型"""
        models = get_all_models()
        assert len(models) > 0
        assert all(isinstance(m, ModelInfo) for m in models)

    def test_get_models_by_provider(self):
        """测试按提供商获取模型"""
        gemini_models = get_models_by_provider("gemini")
        assert len(gemini_models) > 0
        assert all(m.provider == "gemini" for m in gemini_models)

    def test_get_model_by_id(self):
        """测试按ID获取模型"""
        model = get_model_by_id("gemini-2.5-flash")
        assert model is not None
        assert model.model_id == "gemini-2.5-flash"

    def test_get_model_by_name(self):
        """测试按名称获取模型"""
        model = get_model_by_id("Gemini 2.5 Flash")
        assert model is not None
        assert model.name == "Gemini 2.5 Flash"

    def test_rank_models_by_quality(self):
        """测试按质量排序"""
        models = rank_models_by_quality()
        assert len(models) > 0
        # 验证是降序排列
        for i in range(len(models) - 1):
            assert models[i].quality_score >= models[i + 1].quality_score


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
