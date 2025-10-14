#!/usr/bin/env python3
"""Handoff Reminder Scheduler

引き継ぎ予定時刻の10分前にリマインダーDMを送信するスクリプト。
NixOS systemd timerで毎分実行される。
"""

import asyncio
import os
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from anthropic import Anthropic
from slack_sdk.web.async_client import AsyncWebClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.adapters.secondary.postgresql_handoff_repository import (
    PostgreSQLHandoffRepository,
)
from src.application.use_cases.send_handoff_reminder import SendHandoffReminderUseCase


class SlackClient:
    """Slack Client for sending DMs"""

    def __init__(self, token: str):
        self._client = AsyncWebClient(token=token)

    async def send_dm(self, user_id: str, message: str):
        """Send DM to user"""
        await self._client.chat_postMessage(
            channel=user_id,
            text=message,
            unfurl_links=False,
            unfurl_media=False,
        )


async def main():
    """メインエントリーポイント"""
    # 環境変数チェック
    database_url = os.getenv("DATABASE_URL")
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    if not database_url:
        print("Error: DATABASE_URL not set", file=sys.stderr)
        sys.exit(1)

    if not slack_token:
        print("Error: SLACK_BOT_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    if not anthropic_api_key:
        print("Error: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    # データベース接続
    engine = create_async_engine(database_url, echo=False)
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        # リポジトリとクライアント初期化
        handoff_repository = PostgreSQLHandoffRepository(session)
        slack_client = SlackClient(slack_token)

        # Use Case実行
        use_case = SendHandoffReminderUseCase(handoff_repository, slack_client)

        try:
            sent_count = await use_case.execute()
            await session.commit()

            print(f"✅ Sent {sent_count} reminders", file=sys.stderr)

        except Exception as e:
            print(f"❌ Error sending reminders: {e}", file=sys.stderr)
            await session.rollback()
            sys.exit(1)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
