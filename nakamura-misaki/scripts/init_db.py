#!/usr/bin/env python3
"""Database initialization script

PostgreSQL + pgvector extension setup and table creation.
"""

import asyncio
import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from src.infrastructure.database.schema import Base


async def main():
    """データベース初期化"""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("Error: DATABASE_URL not set", file=sys.stderr)
        sys.exit(1)

    print(f"🔧 Connecting to database...")
    engine = create_async_engine(database_url, echo=True)

    async with engine.begin() as conn:
        print(f"✅ Connected to database")

        # pgvector extension 有効化
        print(f"🔧 Enabling pgvector extension...")
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        print(f"✅ pgvector extension enabled")

        # テーブル作成
        print(f"🔧 Creating tables...")
        await conn.run_sync(Base.metadata.create_all)
        print(f"✅ Tables created")

    await engine.dispose()
    print(f"🎉 Database initialization complete")


if __name__ == "__main__":
    asyncio.run(main())
