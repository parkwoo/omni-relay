"""
OmniRelay Model Database Loader
===============================

Loads community-maintained free models database from JSON.
Updated daily via GitHub Actions.

GitHub: https://github.com/parkwoo/omni-relay
Author: parkwoo
License: MIT

Usage:
    from omnirelay.data import ModelDatabase
    
    db = ModelDatabase()
    free_models = db.get_free_models("zhipu")
    all_providers = db.get_all_providers()
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class ModelDatabase:
    """
    Community-maintained database of free and paid AI models
    
    Usage:
        db = ModelDatabase()
        free_models = db.get_free_models("zhipu")
        all_providers = db.get_all_providers()
    """
    
    def __init__(self, data_path: Optional[Path] = None):
        """
        Initialize model database
        
        Args:
            data_path: Path to free-models.json. Defaults to package data directory.
        """
        if data_path is None:
            # Use the directory where this file is located
            base_path = Path(__file__).parent
            data_path = base_path / "free-models.json"
        
        self.data_path = data_path
        self._data: Optional[Dict] = None
        self._load_time: Optional[datetime] = None
    
    def _load_data(self) -> Dict:
        """Load data from JSON file with caching"""
        # Return cached data if loaded within last 5 minutes
        if (
            self._data is not None and 
            self._load_time is not None and
            (datetime.now() - self._load_time).total_seconds() < 300
        ):
            return self._data
        
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self._data = json.load(f)
                self._load_time = datetime.now()
                return self._data
        except FileNotFoundError:
            raise RuntimeError(f"Model database not found: {self.data_path}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON in model database: {e}")
    
    def get_all_providers(self) -> List[str]:
        """Get list of all provider IDs"""
        data = self._load_data()
        return list(data.get("providers", {}).keys())
    
    def get_provider_info(self, provider_id: str) -> Optional[Dict]:
        """Get full provider information"""
        data = self._load_data()
        return data.get("providers", {}).get(provider_id)
    
    def get_free_models(self, provider_id: str) -> List[Dict]:
        """
        Get list of free models for a provider
        
        Args:
            provider_id: Provider ID (e.g., "zhipu", "openrouter")
        
        Returns:
            List of free model dictionaries
        """
        provider = self.get_provider_info(provider_id)
        if not provider:
            return []
        
        return provider.get("free_models", [])
    
    def get_paid_models(self, provider_id: str) -> List[Dict]:
        """
        Get list of paid models for a provider
        
        Args:
            provider_id: Provider ID
        
        Returns:
            List of paid model dictionaries with pricing info
        """
        provider = self.get_provider_info(provider_id)
        if not provider:
            return []
        
        return provider.get("paid_models", [])
    
    def get_all_free_models(self) -> Dict[str, List[Dict]]:
        """
        Get all free models across all providers
        
        Returns:
            Dictionary mapping provider_id to list of free models
        """
        data = self._load_data()
        result = {}
        
        for provider_id, provider_info in data.get("providers", {}).items():
            free_models = provider_info.get("free_models", [])
            if free_models:
                result[provider_id] = free_models
        
        return result
    
    def get_model_by_id(self, model_id: str) -> Optional[Dict]:
        """
        Get model information by model ID
        
        Args:
            model_id: Full model ID (e.g., "glm-4-flash", "deepseek-reasoner")
        
        Returns:
            Model dictionary with provider info, or None if not found
        """
        data = self._load_data()
        
        for provider_id, provider_info in data.get("providers", {}).items():
            # Search free models
            for model in provider_info.get("free_models", []):
                if model.get("model_id") == model_id:
                    return {
                        **model,
                        "provider": provider_id,
                        "provider_name": provider_info.get("provider_name"),
                        "is_free": True
                    }
            
            # Search paid models
            for model in provider_info.get("paid_models", []):
                if model.get("model_id") == model_id:
                    return {
                        **model,
                        "provider": provider_id,
                        "provider_name": provider_info.get("provider_name"),
                        "is_free": False
                    }
        
        return None
    
    def is_free_model(self, model_id: str) -> bool:
        """Check if a model is free"""
        model = self.get_model_by_id(model_id)
        return model is not None and model.get("is_free", False)
    
    def get_provider_note(self, provider_id: str) -> Optional[str]:
        """Get provider-specific note (e.g., free credits, special offers)"""
        provider = self.get_provider_info(provider_id)
        if not provider:
            return None
        return provider.get("note")
    
    def get_contribution_guide(self) -> Dict[str, Any]:
        """Get contribution guide for community submissions"""
        data = self._load_data()
        return data.get("contribution_guide", {})
    
    def get_database_metadata(self) -> Dict[str, Any]:
        """Get database metadata (version, last updated, etc.)"""
        data = self._load_data()
        return {
            "version": data.get("version", "unknown"),
            "last_updated": data.get("last_updated", "unknown"),
            "total_providers": len(data.get("providers", {})),
            "total_free_models": sum(
                len(p.get("free_models", []))
                for p in data.get("providers", {}).values()
            )
        }
    
    def refresh(self):
        """Force reload data from disk"""
        self._data = None
        self._load_time = None
        self._load_data()


# Global instance for convenience
_db: Optional[ModelDatabase] = None


def get_model_database() -> ModelDatabase:
    """Get global ModelDatabase instance"""
    global _db
    if _db is None:
        _db = ModelDatabase()
    return _db


# Convenience functions
def get_free_models(provider_id: str) -> List[Dict]:
    """Get free models for a provider"""
    return get_model_database().get_free_models(provider_id)


def get_all_free_models() -> Dict[str, List[Dict]]:
    """Get all free models across all providers"""
    return get_model_database().get_all_free_models()


def get_model_by_id(model_id: str) -> Optional[Dict]:
    """Get model information by ID"""
    return get_model_database().get_model_by_id(model_id)


def is_free_model(model_id: str) -> bool:
    """Check if a model is free"""
    return get_model_database().is_free_model(model_id)
