"""Dependency injection for FastAPI"""

import os
from pathlib import Path

from ...application.commands.chat_command import ChatCommandHandler
from ...application.queries.health_query import HealthQueryHandler
from ..secondary.claude_adapter import ClaudeAgentAdapter
from ..secondary.prompt_repository_adapter import JsonPromptRepository
from ..secondary.session_store_adapter import JsonSessionRepository
from ..secondary.slack_adapter import SlackAdapter

# Global instances (singleton pattern for simplicity)
_session_repository = None
_prompt_repository = None
_claude_service = None
_slack_adapter = None
_chat_handler = None
_health_handler = None


def get_session_repository():
    """Get session repository instance"""
    global _session_repository
    if _session_repository is None:
        sessions_path = Path(os.getcwd()) / "workspaces" / "sessions"
        _session_repository = JsonSessionRepository(sessions_path)
    return _session_repository


def get_prompt_repository():
    """Get prompt repository instance"""
    global _prompt_repository
    if _prompt_repository is None:
        prompts_dir = Path(os.getcwd()) / "config" / "prompts"
        _prompt_repository = JsonPromptRepository(prompts_dir)
    return _prompt_repository


def get_claude_service():
    """Get Claude service instance"""
    global _claude_service
    if _claude_service is None:
        _claude_service = ClaudeAgentAdapter(
            prompt_repository=get_prompt_repository()
        )
    return _claude_service


def get_slack_adapter():
    """Get Slack adapter instance"""
    global _slack_adapter
    if _slack_adapter is None:
        token = os.environ.get("SLACK_BOT_TOKEN", "")
        _slack_adapter = SlackAdapter(token)
    return _slack_adapter


def get_chat_handler():
    """Get chat command handler"""
    global _chat_handler
    if _chat_handler is None:
        _chat_handler = ChatCommandHandler(
            claude_service=get_claude_service(),
            session_repository=get_session_repository(),
        )
    return _chat_handler


def get_health_handler():
    """Get health query handler"""
    global _health_handler
    if _health_handler is None:
        _health_handler = HealthQueryHandler()
    return _health_handler
