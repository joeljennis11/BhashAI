"""
BhashAI Memory Utilities & Lifecycle Manager
Optimized for low-cost Android and CPU-constrained environments (~2 GB RAM).
Enforces sequential model loading and active memory reclamation.
"""

import os
import gc
import logging
from typing import Dict, Any, Optional, Callable
import psutil

logger = logging.getLogger("bhashai.memory")

# Thresholds for low-memory protection (in Megabytes)
LOW_MEMORY_THRESHOLD_MB = 450.0  # Alert/unload when free RAM drops below 450MB


def get_memory_info() -> Dict[str, Any]:
    """
    Returns current system and process memory metrics in Megabytes.
    """
    try:
        mem = psutil.virtual_memory()
        process = psutil.Process(os.getpid())
        proc_mem = process.memory_info()

        return {
            "total_ram_mb": round(mem.total / (1024 * 1024), 1),
            "available_ram_mb": round(mem.available / (1024 * 1024), 1),
            "used_ram_mb": round(mem.used / (1024 * 1024), 1),
            "ram_percent": mem.percent,
            "process_rss_mb": round(proc_mem.rss / (1024 * 1024), 1),
            "process_vms_mb": round(proc_mem.vms / (1024 * 1024), 1),
            "is_low_memory": (mem.available / (1024 * 1024)) < LOW_MEMORY_THRESHOLD_MB,
        }
    except Exception as e:
        logger.warning(f"Failed to read memory metrics: {e}")
        return {
            "total_ram_mb": 0.0,
            "available_ram_mb": 0.0,
            "used_ram_mb": 0.0,
            "ram_percent": 0.0,
            "process_rss_mb": 0.0,
            "process_vms_mb": 0.0,
            "is_low_memory": False,
        }


def collect_garbage():
    """Forces garbage collection and releases cached PyTorch memory if present."""
    gc.collect()
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    except ImportError:
        pass


class MemoryLifecycleManager:
    """
    Orchestrates sequential loading of AI models to fit within low RAM constraints.
    Allows registering unloading callbacks for each model service.
    """
    _instance: Optional['MemoryLifecycleManager'] = None

    def __init__(self):
        self._unload_callbacks: Dict[str, Callable[[], None]] = {}
        self._active_models: set = set()

    @classmethod
    def get_instance(cls) -> 'MemoryLifecycleManager':
        if cls._instance is None:
            cls._instance = MemoryLifecycleManager()
        return cls._instance

    def register_service(self, name: str, unload_cb: Callable[[], None]):
        """Registers a service name with a callback to release its model."""
        self._unload_callbacks[name] = unload_cb

    def mark_active(self, name: str):
        """Marks a model service as active in memory."""
        self._active_models.add(name)

    def mark_inactive(self, name: str):
        """Marks a model service as unloaded."""
        self._active_models.discard(name)

    def prepare_for_model(self, target_service: str, force_exclusive: bool = False):
        """
        Prepares memory before loading `target_service`.
        If available RAM is low (< LOW_MEMORY_THRESHOLD_MB) or if `force_exclusive` is True,
        unloads other active models sequentially.
        """
        mem = get_memory_info()
        logger.info(
            f"Preparing memory for '{target_service}': Process RSS={mem['process_rss_mb']}MB, "
            f"Available RAM={mem['available_ram_mb']}MB"
        )

        should_unload = force_exclusive or mem["is_low_memory"]

        if should_unload:
            for s_name, cb in list(self._unload_callbacks.items()):
                if s_name != target_service and s_name in self._active_models:
                    logger.info(f"Low memory detected. Unloading inactive service '{s_name}'...")
                    try:
                        cb()
                    except Exception as e:
                        logger.error(f"Error unloading '{s_name}': {e}")
                    self._active_models.discard(s_name)

            collect_garbage()
            new_mem = get_memory_info()
            logger.info(f"Post-cleanup: Process RSS={new_mem['process_rss_mb']}MB, Available RAM={new_mem['available_ram_mb']}MB")
