"""Primary API Adapters for nakamura-misaki v4.0.0

FastAPI-based REST API and Slack Events endpoints.
"""

from .app import create_app

__all__ = ["create_app"]
