"""FastAPI Server for Slack Event Subscriptions

Handles Slack Events API requests and processes Task/Handoff commands.
"""

import hashlib
import hmac
import os
import time
from typing import Any

from anthropic import Anthropic
from fastapi import FastAPI, Header, HTTPException, Request
from slack_sdk.web.async_client import AsyncWebClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.adapters.primary.slack_event_handler import SlackEventHandler

app = FastAPI(title="nakamura-misaki v4.0.0 API")

# グローバル変数（起動時に初期化）
slack_signing_secret: str | None = None
database_url: str | None = None
slack_token: str | None = None
anthropic_api_key: str | None = None
async_session_maker: sessionmaker | None = None


@app.on_event("startup")
async def startup():
    """サーバー起動時の初期化"""
    global slack_signing_secret, database_url, slack_token, anthropic_api_key, async_session_maker

    # 環境変数読み込み
    slack_signing_secret = os.getenv("SLACK_SIGNING_SECRET")
    database_url = os.getenv("DATABASE_URL")
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    if not slack_signing_secret:
        raise RuntimeError("SLACK_SIGNING_SECRET is not set")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")
    if not slack_token:
        raise RuntimeError("SLACK_BOT_TOKEN is not set")
    if not anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")

    # データベース接続
    engine = create_async_engine(database_url, echo=False)
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    print("✅ nakamura-misaki API server started")


@app.get("/health")
async def health():
    """ヘルスチェック"""
    return {"status": "ok", "service": "nakamura-misaki", "version": "4.0.0"}


@app.post("/slack/events")
async def slack_events(
    request: Request,
    x_slack_signature: str = Header(...),
    x_slack_request_timestamp: str = Header(...),
):
    """Slack Events API endpoint

    Args:
        request: FastAPI Request
        x_slack_signature: Slack署名
        x_slack_request_timestamp: リクエストタイムスタンプ

    Returns:
        イベント処理結果
    """
    # リクエストボディ取得
    body = await request.body()
    body_str = body.decode("utf-8")

    # 署名検証
    if not _verify_slack_signature(
        body_str, x_slack_signature, x_slack_request_timestamp
    ):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # JSONパース
    event_data = await request.json()

    # URL Verification Challenge（初回セットアップ）
    if event_data.get("type") == "url_verification":
        return {"challenge": event_data.get("challenge")}

    # Event Callback処理
    if event_data.get("type") == "event_callback":
        event = event_data.get("event", {})

        # botメッセージは無視
        if event.get("subtype") == "bot_message":
            return {"status": "ignored"}

        # メッセージイベント処理
        if event.get("type") == "message":
            user_id = event.get("user")
            text = event.get("text", "")
            channel = event.get("channel")

            # ハンドラーでメッセージ処理
            async with async_session_maker() as session:
                claude_client = Anthropic(api_key=anthropic_api_key)
                handler = SlackEventHandler(session, claude_client, slack_token)

                response_text = await handler.handle_message(user_id, text)

                # 応答がある場合（Task/Handoffコマンド）のみSlackに返信
                if response_text:
                    slack_client = AsyncWebClient(token=slack_token)
                    await slack_client.chat_postMessage(
                        channel=channel,
                        text=response_text,
                        unfurl_links=False,
                        unfurl_media=False,
                    )

                await session.commit()

    return {"status": "ok"}


def _verify_slack_signature(body: str, signature: str, timestamp: str) -> bool:
    """Slack署名を検証

    Args:
        body: リクエストボディ
        signature: X-Slack-Signature header
        timestamp: X-Slack-Request-Timestamp header

    Returns:
        署名が正しければTrue
    """
    # タイムスタンプが5分以上古い場合は拒否
    if abs(time.time() - int(timestamp)) > 60 * 5:
        return False

    # 署名生成
    sig_basestring = f"v0:{timestamp}:{body}".encode("utf-8")
    my_signature = (
        "v0="
        + hmac.new(
            slack_signing_secret.encode("utf-8"),
            sig_basestring,
            hashlib.sha256,
        ).hexdigest()
    )

    # 署名比較（タイミング攻撃対策）
    return hmac.compare_digest(my_signature, signature)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=10000)
