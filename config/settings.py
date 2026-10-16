"""Compatibility settings for the AI Hub backend.

The existing src.core.config module remains the canonical source
for application settings. This module provides a stable import path.
"""

from src.core.config import PROJECT_ROOT, Settings, settings

__all__ = ["PROJECT_ROOT", "Settings", "settings"]
