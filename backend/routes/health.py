"""
BhashAI Health & Diagnostics Route
Provides system health, model residency, offline readiness, and memory metrics.
"""

from fastapi import APIRouter
from backend.models.response_models import HealthResponse, ModelStatusItem
from backend.models.language_config import SUPPORTED_LANGUAGES, list_supported_pairs
from backend.services.model_manager import ModelManager
from backend.utils.memory_utils import get_memory_info

router = APIRouter(prefix="/api", tags=["Health & Models"])


@router.get("/health", response_model=HealthResponse)
async def check_health():
    """
    Returns live system status, model availability, offline state, and memory metrics.
    """
    mgr = ModelManager.get_instance()
    statuses = mgr.get_model_statuses()
    memory_info = get_memory_info()
    offline_ready = mgr.is_fully_offline_ready()

    models_dict = {
        k: ModelStatusItem(**v) for k, v in statuses.items()
    }

    return HealthResponse(
        status="operational",
        version="1.0.0-prototype",
        offline_mode=offline_ready,
        models=models_dict,
        memory=memory_info
    )


@router.post("/models/prepare-offline")
async def prepare_offline():
    """
    Triggers pre-caching and synchronization of all models for full offline classroom operation.
    """
    mgr = ModelManager.get_instance()
    result = mgr.prepare_offline_mode()
    return result


@router.get("/languages")
async def get_supported_languages():
    """
    Returns list of supported language configurations and extensible language stubs.
    """
    return {
        "supported_pairs": list_supported_pairs(),
        "languages": [cfg.model_dump() for cfg in SUPPORTED_LANGUAGES.values()]
    }
