"""Slack Events API endpoint

Handles Slack Event Subscriptions with signature verification.
"""

import asyncio
import hashlib
import hmac
import logging
import time

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request
from slack_sdk.web.async_client import AsyncWebClient

from src.adapters.primary.slack_event_handler import SlackEventHandlerV5

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory set to track recently processed event IDs (prevent duplicate processing)
_processed_events: set[str] = set()
_processed_events_lock = asyncio.Lock()


@router.post("/slack")
async def slack_events(
    request: Request,
    background_tasks: BackgroundTasks,
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
            text = event.get("text", "").strip()
            channel = event.get("channel")

            logger.info(f"Message event: user={user_id}, channel={channel}, text_length={len(text)}")
            logger.debug(f"Message text: {text}")

            # Ignore messages from the bot itself (User Token posts as user, not bot)
            # Bot user ID: U09AHTB4X4H
            if user_id == "U09AHTB4X4H":
                logger.info("Ignoring message from bot itself")
                return {"status": "ignored"}

            # Ignore empty or whitespace-only messages
            if not text:
                logger.info("Ignoring empty or whitespace-only message")
                return {"status": "ignored"}

            # Check for duplicate events (Slack retry logic)
            event_id = event_data.get("event_id")
            if event_id:
                async with _processed_events_lock:
                    if event_id in _processed_events:
                        logger.info(f"Ignoring duplicate event: {event_id}")
                        return {"status": "ignored"}
                    _processed_events.add(event_id)
                    # Keep only last 1000 event IDs to prevent memory leak
                    if len(_processed_events) > 1000:
                        _processed_events.pop()

            # Process message in background to return 200 immediately
            # (Slack expects 200 within 3 seconds or will retry)
            handler = request.app.state.slack_event_handler
            slack_token = request.app.state.slack_token
            background_tasks.add_task(
                _process_message_async,
                handler,
                slack_token,
                user_id,
                text,
                channel,
            )

    logger.info("Webhook processed successfully")
    return {"status": "ok"}


async def _process_message_async(
    handler: SlackEventHandlerV5,
    slack_token: str,
    user_id: str,
    text: str,
    channel: str,
) -> None:
    """Process Slack message in background.

    Args:
        handler: SlackEventHandlerV5 instance
        slack_token: Slack bot token
        user_id: User ID
        text: Message text
        channel: Channel ID
    """
    try:
        response_text = await handler.handle_message(user_id, text, channel)
        logger.info(f"Message handled, response_generated={bool(response_text)}")

        # 応答がある場合はSlackに返信
        if response_text:
            slack_client = AsyncWebClient(token=slack_token)
            await slack_client.chat_postMessage(
                channel=channel,
                text=response_text,
                unfurl_links=False,
                unfurl_media=False,
            )
            logger.info(f"Response sent to Slack channel={channel}")
    except Exception as e:
        logger.error(f"Error handling message: {e}", exc_info=True)


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
    sig_basestring = f"v0:{timestamp}:{body}".encode()
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
