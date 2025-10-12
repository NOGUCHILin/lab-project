"""RQ Worker for Claude Agent processing

This worker processes Slack messages asynchronously using Redis Queue (RQ).
It prevents CancelledError by running Claude Agent SDK in a separate process
from the FastAPI HTTP lifecycle.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from redis import Redis
from rq import Worker, Queue

# Import the async processing function
from src.adapters.primary.api.routes import process_slack_message


def run_async_task(user_id: str, channel: str, text: str, is_dm: bool) -> None:
    """Wrapper to run async function in worker context

    RQ workers run in synchronous context, so we need to create an event loop
    to run our async Claude Agent processing.
    """
    try:
        # Create new event loop for this task
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            # Run the async processing with timeout
            loop.run_until_complete(
                asyncio.wait_for(
                    process_slack_message(user_id, channel, text, is_dm),
                    timeout=300  # 5 minutes
                )
            )
            print(f"✅ Successfully processed message from user {user_id}")
        except asyncio.TimeoutError:
            print(f"⏱️ Timeout processing message from user {user_id}")
            raise  # Re-raise so RQ knows the task failed
        finally:
            loop.close()
    except Exception as e:
        print(f"❌ Worker error processing message from user {user_id}: {e}")
        import traceback
        traceback.print_exc()
        raise  # Re-raise so RQ knows the task failed


if __name__ == '__main__':
    # Get Redis connection from environment
    redis_host = os.environ.get('REDIS_HOST', '127.0.0.1')
    redis_port = int(os.environ.get('REDIS_PORT', 6380))

    print(f"🔌 Connecting to Redis at {redis_host}:{redis_port}")

    # Create Redis connection
    redis_conn = Redis(
        host=redis_host,
        port=redis_port,
        db=0,
        decode_responses=False  # RQ requires bytes
    )

    # Test connection
    try:
        redis_conn.ping()
        print(f"✅ Redis connection successful")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        sys.exit(1)

    # Create queue
    queue = Queue('claude_tasks', connection=redis_conn)

    print(f"🤖 Starting RQ Worker for Claude Agent processing")
    print(f"📥 Listening on queue: claude_tasks")
    print(f"⏰ Job timeout: 300 seconds (5 minutes)")
    print()

    # Start worker
    worker = Worker([queue], connection=redis_conn)
    worker.work(with_scheduler=True, logging_level='INFO')
