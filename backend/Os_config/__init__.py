"""
Os_config Package

Centralized configuration module for AI agent orchestration.
"""

from .setup_config import get_gemini_config, GeminiConfig

__all__ = ["get_gemini_config", "GeminiConfig"]
