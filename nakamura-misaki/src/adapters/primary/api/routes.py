"""FastAPI routes"""

import asyncio
import os
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from redis import Redis
from rq import Queue

from ....application.commands.chat_command import (
    ChatCommand,
    ChatCommandHandler,
)
from ....application.queries.health_query import HealthQuery, HealthQueryHandler
from ..dependencies import get_chat_handler, get_health_handler, get_slack_adapter

router = APIRouter()

# Initialize Redis connection and queue for RQ
redis_host = os.environ.get('REDIS_HOST', '127.0.0.1')
redis_port = int(os.environ.get('REDIS_PORT', 6380))
redis_conn = Redis(host=redis_host, port=redis_port, db=0, decode_responses=False)
claude_queue = Queue('claude_tasks', connection=redis_conn)


class SlackEvent(BaseModel):
    """Slack event model"""

    type: str
    challenge: str | None = None
    event: Dict[str, Any] | None = None


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    handler = get_health_handler()
    result = await handler.handle(HealthQuery())
    return {"status": result.status, "version": result.version}


async def process_slack_message(
    user_id: str, channel: str, text: str, is_dm: bool
) -> None:
    """Process Slack message - Core logic (reusable for both BackgroundTasks and Queue)"""
    # Get workspace path
    base_workspace = (
        Path(os.getcwd()) / "workspaces" / f"user_{user_id}" / "claude_workspace"
    )
    base_workspace.mkdir(parents=True, exist_ok=True)

    # Execute chat command
    chat_handler = get_chat_handler()
    command = ChatCommand(
        user_id=user_id,
        message=text,
        workspace_path=str(base_workspace),
        is_dm=is_dm,  # Anthropic Context Engineering: チャネルタイプをコンテキストに追加
    )
    result = await chat_handler.handle(command)

    # Send response via Slack
    slack = get_slack_adapter()
    send_result = await slack.send_message(channel=channel, text=result.response)

    status = "✅" if send_result.get("ok") else "⚠️"
    print(f"{status} Replied to {'DM' if is_dm else 'channel'} {channel}")

    if not send_result.get("ok"):
        print(f"❌ Slack send failed: {send_result}")


async def process_slack_message_detached(
    user_id: str, channel: str, text: str, is_dm: bool
) -> None:
    """Process Slack message in detached task (temporary fix for CancelledError)"""
    try:
        # Set timeout to prevent infinite loops (5 minutes)
        async with asyncio.timeout(300):
            await process_slack_message(user_id, channel, text, is_dm)
    except asyncio.TimeoutError:
        print(f"⏱️ Claude processing timeout for user {user_id}")
        # TODO: Send timeout message to Slack
    except Exception as e:
        print(f"❌ Detached task error: {e}")
        import traceback
        traceback.print_exc()


@router.post("/webhook/slack")
async def slack_webhook(request: Request):
    """Slack webhook endpoint - returns immediately to avoid retries"""
    try:
        data = await request.json()

        # URL verification challenge
        if data.get("type") == "url_verification":
            return {"challenge": data.get("challenge")}

        # Event callback
        if data.get("type") == "event_callback":
            event = data.get("event", {})
            event_type = event.get("type")

            # Handle message events
            if event_type == "message":
                # Ignore bot messages and message changes
                if event.get("subtype") in ["bot_message", "message_changed"]:
                    return {"ok": True}

                user_id = event.get("user")
                channel = event.get("channel")
                text = event.get("text", "")

                # Check if it's a DM
                is_dm = channel.startswith("D") if channel else False

                # Get nakamura user ID
                nakamura_id = os.environ.get("NAKAMURA_USER_ID", "")

                # Ignore nakamura's own messages (loop prevention)
                if user_id == nakamura_id:
                    return {"ok": True}

                # Process DM or mention
                if is_dm or (text and f"<@{nakamura_id}>" in text):
                    # Queue task to RQ worker - return 200 OK immediately
                    # Using Redis Queue to prevent CancelledError by processing in separate worker
                    from src.workers.claude_worker import run_async_task

                    job = claude_queue.enqueue(
                        run_async_task,
                        user_id, channel, text, is_dm,
                        job_timeout=300,  # 5 minute timeout
                        result_ttl=3600,  # Keep result for 1 hour
                        failure_ttl=86400  # Keep failures for 24 hours
                    )
                    print(f"📥 Queued message from user {user_id} to RQ (job: {job.id})")

        # Return immediately to prevent Slack retries
        return {"ok": True}

    except Exception as e:
        print(f"❌ Slack webhook error: {e}")
        # Still return 200 to prevent retries
        return {"ok": True, "error": str(e)}
