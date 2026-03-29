"""
Tests for model database loader
"""

import pytest
from pathlib import Path

from omnirelay.data.loader import (
    ModelDatabase,
    get_model_database,
    get_free_models,
    get_all_free_models,
    get_model_by_id,
    is_free_model,
)


class TestModelDatabase:
    @pytest.fixture
    def db(self):
        return ModelDatabase()
    
    def test_get_all_providers(self, db):
        providers = db.get_all_providers()
        assert len(providers) > 0
        assert "zhipu" in providers
        assert "openrouter" in providers
        assert "kilo" in providers
    
    def test_get_provider_info(self, db):
        provider = db.get_provider_info("zhipu")
        assert provider is not None
        assert provider.get("provider_name") == "Zhipu AI"
        assert "free_models" in provider
        assert "paid_models" in provider
    
    def test_get_free_models_zhipu(self, db):
        free_models = db.get_free_models("zhipu")
        assert len(free_models) > 0
        model_ids = [m["model_id"] for m in free_models]
        assert "glm-4-flash" in model_ids
    
    def test_get_free_models_openrouter(self, db):
        free_models = db.get_free_models("openrouter")
        assert len(free_models) > 5  # OpenRouter has many free models
    
    def test_get_free_models_kilo(self, db):
        free_models = db.get_free_models("kilo")
        assert len(free_models) >= 3  # At least 3 free models
        model_ids = [m["model_id"] for m in free_models]
        assert "minimax/minimax-m2.5" in model_ids
        assert "nvidia/nemotron-3-super-120b-a12b" in model_ids
        assert "arcee-ai/trinity-large-preview" in model_ids
    
    def test_get_paid_models(self, db):
        paid_models = db.get_paid_models("deepseek")
        assert len(paid_models) > 0
        assert any(m["model_id"] == "deepseek-reasoner" for m in paid_models)
    
    def test_get_all_free_models(self, db):
        all_free = db.get_all_free_models()
        assert isinstance(all_free, dict)
        assert "openrouter" in all_free
        assert "zhipu" in all_free
        assert "kilo" in all_free
    
    def test_get_model_by_id_found(self, db):
        model = db.get_model_by_id("glm-4-flash")
        assert model is not None
        assert model["model_id"] == "glm-4-flash"
        assert model["provider"] == "zhipu"
        assert model["is_free"] is True
    
    def test_get_model_by_id_not_found(self, db):
        model = db.get_model_by_id("nonexistent-model-12345")
        assert model is None
    
    def test_is_free_model_true(self, db):
        assert db.is_free_model("glm-4-flash") is True
        assert db.is_free_model("minimax/minimax-m2.5") is True
    
    def test_is_free_model_false(self, db):
        assert db.is_free_model("deepseek-reasoner") is False
        assert db.is_free_model("gpt-4o") is False
    
    def test_get_provider_note(self, db):
        note = db.get_provider_note("zhipu")
        assert note is not None
        assert "free" in note.lower()
    
    def test_database_metadata(self, db):
        metadata = db.get_database_metadata()
        assert "version" in metadata
        assert "last_updated" in metadata
        assert "total_providers" in metadata
        assert metadata["total_providers"] > 0
    
    def test_contribution_guide(self, db):
        guide = db.get_contribution_guide()
        assert "how_to_contribute" in guide
        assert "required_fields" in guide
    
    def test_refresh(self, db):
        # Load data
        db.get_all_providers()
        # Refresh
        db.refresh()
        # Should reload
        providers = db.get_all_providers()
        assert len(providers) > 0


class TestConvenienceFunctions:
    def test_get_free_models(self):
        models = get_free_models("zhipu")
        assert len(models) > 0
    
    def test_get_all_free_models(self):
        all_free = get_all_free_models()
        assert isinstance(all_free, dict)
    
    def test_get_model_by_id(self):
        model = get_model_by_id("glm-4-flash")
        assert model is not None
        assert model["is_free"] is True
    
    def test_is_free_model(self):
        assert is_free_model("glm-4-flash") is True
        assert is_free_model("deepseek-reasoner") is False


class TestModelDatabaseErrors:
    def test_invalid_provider(self):
        db = ModelDatabase()
        assert db.get_provider_info("nonexistent_provider") is None
        assert db.get_free_models("nonexistent_provider") == []
    
    def test_empty_model_list(self):
        db = ModelDatabase()
        # Some providers have no free models
        free_models = db.get_free_models("openai")
        assert isinstance(free_models, list)
