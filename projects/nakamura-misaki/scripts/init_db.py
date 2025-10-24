#!/usr/bin/env python3
"""Database initialization script

PostgreSQL + pgvector extension setup and Alembic migrations.
"""

import os
import subprocess
import sys
from pathlib import Path

# Import alembic directory from our package
# Note: src is the top-level package, so import as src.nakamura_misaki_alembic
try:
    from src.nakamura_misaki_alembic import ALEMBIC_DIR
except ImportError:
    # Fallback for local development without install
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    from src.nakamura_misaki_alembic import ALEMBIC_DIR


def run_alembic_upgrade():
    """Run Alembic migrations to upgrade database to latest version"""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("Error: DATABASE_URL not set", file=sys.stderr)
        sys.exit(1)

    print("🔧 Running Alembic migrations...")

    # Use alembic directory from nakamura_misaki_alembic package
    # This works in both development (src/nakamura_misaki_alembic/)
    # and production (installed as Python package)
    alembic_dir = ALEMBIC_DIR
    print(f"📁 Using alembic directory: {alembic_dir}")

    # Create temporary alembic.ini (since Nix store is read-only)
    import tempfile

    alembic_ini_content = f"""[alembic]
script_location = {alembic_dir}
version_path_separator = os

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""

    # Write to temporary file (Nix store is read-only)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as f:
        f.write(alembic_ini_content)
        alembic_ini = f.name

    # Find alembic executable (in same bin directory as this Python interpreter)
    python_exe = Path(sys.executable)
    alembic_exe = python_exe.parent / "alembic"

    if not alembic_exe.exists():
        print(f"Error: alembic executable not found at {alembic_exe}", file=sys.stderr)
        print(f"Python executable: {python_exe}", file=sys.stderr)
        sys.exit(1)

    print(f"🔧 Using alembic executable: {alembic_exe}")

    # Convert async DATABASE_URL to sync for Alembic (which uses sync SQLAlchemy)
    # Use psycopg (version 3) driver instead of psycopg2
    sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql+psycopg://")

    print(f"🔧 Using database URL: {sync_database_url.split('@')[0]}@...")

    result = subprocess.run(
        [alembic_exe, "-c", str(alembic_ini), "upgrade", "head"],
        cwd=project_root,
        env={**os.environ, "DATABASE_URL": sync_database_url},
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("Error running alembic upgrade:", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)

    print(result.stdout)
    print("✅ Database migrations applied")


def main():
    """Entry point for nakamura-init-db script"""
    run_alembic_upgrade()
    print("🎉 Database initialization complete")


if __name__ == "__main__":
    main()
