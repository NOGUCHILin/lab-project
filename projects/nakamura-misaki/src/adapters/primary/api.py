"""FastAPI Server for nakamura-misaki v4.0.0

Entry point for uvicorn. Imports application from new architecture.
"""

from src.adapters.primary.api.app import create_app

# Create app instance for uvicorn
app = create_app()

__all__ = ["app"]
