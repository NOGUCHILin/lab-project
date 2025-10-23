"""Slack API adapter"""

import json
from typing import Any

import requests


class SlackAdapter:
    """Slack Web API adapter"""

    API_URL = "https://slack.com/api/chat.postMessage"
    DND_END_URL = "https://slack.com/api/dnd.endDnd"
    USERS_LIST_URL = "https://slack.com/api/users.list"

    def __init__(self, token: str) -> None:
        self.token = token.strip()

    async def send_message(self, channel: str, text: str) -> dict[str, Any]:
        """Send message to channel or DM"""
        if not self.token:
            return {"ok": False, "error": "token_missing"}

        payload = {"channel": channel, "text": text}
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json; charset=utf-8",
        }

        try:
            response = requests.post(self.API_URL, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            return {"ok": False, "error": str(exc)}
        except json.JSONDecodeError:
            return {"ok": False, "error": "invalid_json"}

        return data

    async def end_dnd(self) -> dict[str, Any]:
        """End Do Not Disturb mode"""
        if not self.token:
            return {"ok": False, "error": "token_missing"}

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json; charset=utf-8",
        }

        try:
            response = requests.post(self.DND_END_URL, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            return {"ok": False, "error": str(exc)}
        except json.JSONDecodeError:
            return {"ok": False, "error": "invalid_json"}

        return data

    async def users_list(self) -> dict[str, Any]:
        """Get list of users in workspace"""
        if not self.token:
            return {"ok": False, "error": "token_missing"}

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json; charset=utf-8",
        }

        try:
            response = requests.get(self.USERS_LIST_URL, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            return {"ok": False, "error": str(exc)}
        except json.JSONDecodeError:
            return {"ok": False, "error": "invalid_json"}

        return data
