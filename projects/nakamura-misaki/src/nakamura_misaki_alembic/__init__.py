"""Alembic database migrations for nakamura-misaki.

This package contains all database migration scripts managed by Alembic.

Directory structure:
- versions/: Migration scripts (numbered 001, 002, etc.)
- env.py: Alembic environment configuration
- script.py.mako: Template for new migrations
"""

from pathlib import Path

# Expose the directory path for scripts/init_db.py
ALEMBIC_DIR = Path(__file__).parent

__all__ = ["ALEMBIC_DIR"]
