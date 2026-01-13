"""
Gemini API Configuration Module (OpenAI Agents SDK Compatible)

This module provides the google_gemini_config for all AI agent interactions.
All requests MUST route through this configuration using OpenAI Agents SDK.

Architectural Guardrails:
- Uses OpenAI Agents SDK (openai-agents package) for agent orchestration
- AsyncOpenAI client pointed at Google's Gemini OpenAI-compatible endpoint
- Stateless configuration (no in-memory state)
- Environment-based API key management
- Multi-tenant safe (no shared state)

CRITICAL: Do NOT use native google-generativeai library. Use AsyncOpenAI client only.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GeminiConfig:
    """
    Gemini API Configuration for OpenAI Agents SDK

    This class encapsulates all Gemini API settings and provides
    a centralized configuration point for AsyncOpenAI client initialization.
    """

    def __init__(self):
        """Initialize Gemini configuration from environment variables."""
        self.api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
        # CRITICAL: Use OpenAI-compatible endpoint with /openai/ suffix
        self.base_url: str = os.getenv(
            "GEMINI_BASE_URL",
            "https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.timeout: int = int(os.getenv("GEMINI_TIMEOUT", "5"))  # 5 seconds max
        self.max_retries: int = int(os.getenv("GEMINI_MAX_RETRIES", "3"))

        # Validate required configuration
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is required. "
                "Please set it in your .env file."
            )

    def get_async_openai_config(self) -> dict:
        """
        Get AsyncOpenAI client configuration dictionary.

        Returns:
            dict: Configuration for AsyncOpenAI client initialization
                  Compatible with: AsyncOpenAI(**config)
        """
        return {
            "api_key": self.api_key,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
        }

    def get_model_config(self) -> dict:
        """
        Get model configuration for OpenAIChatCompletionsModel wrapper.

        Returns:
            dict: Configuration for model initialization
        """
        return {
            "model": self.model,
            "temperature": 0.7,
            "max_tokens": 2048,
        }

    def __repr__(self) -> str:
        """String representation (hides API key for security)."""
        return (
            f"GeminiConfig(model={self.model}, "
            f"base_url={self.base_url}, "
            f"timeout={self.timeout}s)"
        )


# Global configuration instance
# This is the ONLY configuration that should be used throughout the application
google_gemini_config = GeminiConfig()


def get_gemini_config() -> GeminiConfig:
    """
    Get the global Gemini configuration instance.

    Returns:
        GeminiConfig: The global configuration instance

    Usage:
        from Os_config.setup_config import get_gemini_config

        config = get_gemini_config()
        client_config = config.get_client_config()
    """
    return google_gemini_config


# Validation on module import
if __name__ == "__main__":
    print("Gemini Configuration:")
    print(google_gemini_config)
    print("\nClient Config:")
    print(google_gemini_config.get_client_config())
