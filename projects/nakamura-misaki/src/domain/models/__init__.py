"""Domain Models - Legacy bridge package

DEPRECATION NOTICE:
This package provides legacy models for backward compatibility during
the migration to the new Bounded Context architecture.

New code should use models from:
    src.contexts.<context>/domain/entities/
    src.contexts.<context>/domain/value_objects/
"""

from .session import SessionInfo

__all__ = ["SessionInfo"]
