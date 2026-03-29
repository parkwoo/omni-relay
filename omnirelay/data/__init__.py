"""
OmniRelay Data Package
Community-maintained model databases and configuration
"""

from .loader import (
    ModelDatabase,
    get_model_database,
    get_free_models,
    get_all_free_models,
    get_model_by_id,
    is_free_model,
)

__all__ = [
    "ModelDatabase",
    "get_model_database",
    "get_free_models",
    "get_all_free_models",
    "get_model_by_id",
    "is_free_model",
]
