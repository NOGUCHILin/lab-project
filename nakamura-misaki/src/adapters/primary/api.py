"""FastAPI Server for nakamura-misaki v4.0.0

DEPRECATED: This file is kept for backward compatibility.
Use src.adapters.primary.api.app.create_app() instead.

This module re-exports the new application factory for compatibility.
"""

from .api.app import create_app

# Create app instance for uvicorn
app = create_app()

__all__ = ["app"]
