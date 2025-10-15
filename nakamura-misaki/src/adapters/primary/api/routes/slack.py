"""Slack Events API endpoint

Handles Slack Event Subscriptions with signature verification.
"""

import hashlib
import hmac
import logging
import time

from anthropic import Anthropic
from fastapi import APIRouter, Header, HTTPException, Request
from slack_sdk.web.async_client import AsyncWebClient

from src.adapters.primary.slack_event_handler import SlackEventHandler

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/slack")
async def slack_events(
    request: Request,
    x_slack_signature: str = Header(...),
    x_slack_request_timestamp: str = Header(...),
):
    """Slack Events API endpoint

    Slack Events APIからのWebhookを受信し、イベントを処理します。

    Args:
        request: FastAPI Request
        x_slack_signature: Slack署名
        x_slack_request_timestamp: リクエストタイムスタンプ

    Returns:
        イベント処理結果

    Raises:
        HTTPException: 署名検証失敗時
    """
    # リクエストボディ取得
    body = await request.body()
    body_str = body.decode("utf-8")

    logger.info(f"Received Slack webhook, timestamp={x_slack_request_timestamp}")

    # 署名検証
    signing_secret = request.app.state.slack_signing_secret
    if not _verify_slack_signature(
        body_str, x_slack_signature, x_slack_request_timestamp, signing_secret
    ):
        logger.warning("Slack signature verification failed")
        raise HTTPException(status_code=401, detail="Invalid signature")

    # JSONパース
    event_data = await request.json()
    event_type = event_data.get("type")
    logger.debug(f"Slack event type: {event_type}, payload: {event_data}")

    # URL Verification Challenge（初回セットアップ）
    if event_type == "url_verification":
        challenge = event_data.get("challenge")
        logger.info(f"Responding to URL verification challenge: {challenge}")
        return {"challenge": challenge}

    # Event Callback処理
    if event_type == "event_callback":
        event = event_data.get("event", {})
        event_subtype = event.get("type")

        logger.info(f"Processing event_callback: subtype={event_subtype}, user={event.get('user')}")

        # botメッセージは無視
        if event.get("subtype") == "bot_message":
            logger.info("Ignoring bot_message event")
            return {"status": "ignored"}

        # メッセージイベント処理
        if event_subtype == "message":
            user_id = event.get("user")
            text = event.get("text", "")
            channel = event.get("channel")

            logger.info(f"Message event: user={user_id}, channel={channel}, text_length={len(text)}")
            logger.debug(f"Message text: {text}")

            # ハンドラーでメッセージ処理
            async_session_maker = request.app.state.async_session_maker
            async with async_session_maker() as session:
                claude_client = Anthropic(api_key=request.app.state.anthropic_api_key)
                slack_token = request.app.state.slack_token
                handler = SlackEventHandler(session, claude_client, slack_token)

                try:
                    response_text = await handler.handle_message(user_id, text)
                    logger.info(f"Message handled, response_generated={bool(response_text)}")

                    # 応答がある場合（Task/Handoffコマンド）のみSlackに返信
                    if response_text:
                        slack_client = AsyncWebClient(token=slack_token)
                        await slack_client.chat_postMessage(
                            channel=channel,
                            text=response_text,
                            unfurl_links=False,
                            unfurl_media=False,
                        )
                        logger.info(f"Response sent to Slack channel={channel}")

                    await session.commit()
                    logger.debug("Database session committed")
                except Exception as e:
                    logger.error(f"Error handling message: {e}", exc_info=True)
                    raise

    logger.info("Webhook processed successfully")
    return {"status": "ok"}


def _verify_slack_signature(
    body: str, signature: str, timestamp: str, signing_secret: str
) -> bool:
    """Slack署名を検証

    Args:
        body: リクエストボディ
        signature: X-Slack-Signature header
        timestamp: X-Slack-Request-Timestamp header
        signing_secret: Slack Signing Secret

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
            signing_secret.encode("utf-8"),
            sig_basestring,
            hashlib.sha256,
        ).hexdigest()
    )

    # 署名比較（タイミング攻撃対策）
    return hmac.compare_digest(my_signature, signature)
