"""
Context Manager - Anthropic Context Engineering Best Practices

This module implements Anthropic's recommended "Compaction" strategy:
- Monitor token usage across conversation
- Compress context when approaching window limit (80% threshold)
- Maintain recent messages while summarizing older ones
- Reduce token consumption by up to 84% (Anthropic research)

Reference: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
"""

import os
from typing import Any

try:
    from anthropic import Anthropic

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    Anthropic = None


class ContextManager:
    """
    Anthropic推奨のコンテキスト管理

    Features:
    - Token estimation for conversation history
    - Automatic compression at 80% threshold
    - Preserves recent 10 messages
    - Summarizes older messages using Claude
    """

    # Claude 3.5 Sonnet context window
    CONTEXT_WINDOW = 200_000

    # Compress when reaching 80% of context window
    COMPRESSION_THRESHOLD = 0.8

    # Number of recent messages to preserve during compression
    RECENT_MESSAGES_TO_KEEP = 10

    def __init__(self):
        """Initialize Context Manager with Anthropic client"""
        if not ANTHROPIC_AVAILABLE or Anthropic is None:
            print("⚠️ Anthropic SDK not available - context compression disabled")
            self.client = None
            return

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("⚠️ ANTHROPIC_API_KEY not set - context compression disabled")
            self.client = None
            return

        self.client = Anthropic(api_key=api_key)

    def estimate_tokens(self, messages: list[dict[str, Any]]) -> int:
        """
        トークン数推定

        Anthropic推奨の簡易推定方法:
        - 日本語: 1文字 ≈ 0.4トークン
        - 英語: 1文字 ≈ 0.25トークン
        - 平均: 1文字 ≈ 0.35トークン

        Args:
            messages: メッセージ履歴 [{"role": "user/assistant", "content": "..."}]

        Returns:
            推定トークン数
        """
        total_chars = 0

        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                total_chars += len(content)
            elif isinstance(content, list):
                # Claude Code SDK format: [{"type": "text", "text": "..."}]
                for block in content:
                    if isinstance(block, dict):
                        total_chars += len(block.get("text", ""))

        # 日本語・英語混在を考慮した係数
        return int(total_chars * 0.35)

    async def compress_if_needed(
        self, user_id: str, messages: list[dict[str, Any]]
    ) -> tuple[list[dict[str, Any]], bool]:
        """
        Anthropic推奨: コンテキストウィンドウが80%超えたら圧縮

        Process:
        1. トークン数を推定
        2. 80%未満なら圧縮不要
        3. 80%以上なら:
           - 古いメッセージ（最新10件以外）を要約
           - 要約をsystem messageとして追加
           - 最新10件のメッセージを保持

        Args:
            user_id: ユーザーID（ログ用）
            messages: 現在のメッセージ履歴

        Returns:
            (圧縮後のメッセージ履歴, 圧縮実行フラグ)
        """
        if not self.client:
            return messages, False

        token_count = self.estimate_tokens(messages)
        threshold = int(self.CONTEXT_WINDOW * self.COMPRESSION_THRESHOLD)

        if token_count < threshold:
            print(
                f"📊 Context OK: {token_count:,} / {self.CONTEXT_WINDOW:,} tokens "
                f"({token_count/self.CONTEXT_WINDOW*100:.1f}%)"
            )
            return messages, False

        print(
            f"⚠️ Context approaching limit: {token_count:,} / {self.CONTEXT_WINDOW:,} tokens "
            f"({token_count/self.CONTEXT_WINDOW*100:.1f}%) - Compressing..."
        )

        # 古いメッセージと最新メッセージを分離
        if len(messages) <= self.RECENT_MESSAGES_TO_KEEP:
            # メッセージが少ない場合は圧縮不要
            return messages, False

        old_messages = messages[: -self.RECENT_MESSAGES_TO_KEEP]
        recent_messages = messages[-self.RECENT_MESSAGES_TO_KEEP :]

        # 古いメッセージを要約
        summary = await self._summarize_messages(old_messages)

        # 新しいコンテキスト構築
        compressed_context = [
            {
                "role": "user",
                "content": f"""<conversation_summary>
以前の会話の要約:

{summary}
</conversation_summary>

上記は過去の会話の要約です。この情報を踏まえて、以降のメッセージに応答してください。""",
            },
            {
                "role": "assistant",
                "content": "承知しました。過去の会話の要約を確認しました。引き続きサポートさせていただきます。",
            },
            *recent_messages,
        ]

        compressed_tokens = self.estimate_tokens(compressed_context)
        reduction = (1 - compressed_tokens / token_count) * 100

        print(
            f"✂️ Context compressed: {token_count:,} → {compressed_tokens:,} tokens "
            f"({reduction:.1f}% reduction)"
        )
        print(
            f"📝 Summarized {len(old_messages)} old messages, kept {len(recent_messages)} recent"
        )

        return compressed_context, True

    async def _summarize_messages(self, messages: list[dict[str, Any]]) -> str:
        """
        Claudeを使って古いメッセージを要約

        Args:
            messages: 要約対象のメッセージ履歴

        Returns:
            要約テキスト
        """
        if not self.client:
            return "要約機能が利用できません"

        # メッセージを読みやすく整形
        formatted_messages = self._format_messages(messages)

        summary_prompt = f"""<instruction>
以下の会話履歴を簡潔に要約してください。

**要約に含めるべき内容:**
- 重要な決定事項
- 修正・作成したファイル
- 未解決の問題
- 今後のタスク
- ユーザーの要求や意図

**要約形式:**
- 箇条書き
- 簡潔かつ明確に
- 重要な情報のみ抽出
- 200-300トークン程度

</instruction>

<conversation_history>
{formatted_messages}
</conversation_history>

上記の会話を要約してください。"""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[{"role": "user", "content": summary_prompt}],
            )

            summary_text = response.content[0].text
            return summary_text

        except Exception as e:
            print(f"❌ Summarization error: {e}")
            return f"要約エラー: {str(e)}"

    def _format_messages(self, messages: list[dict[str, Any]]) -> str:
        """
        メッセージをXML形式に整形

        Args:
            messages: メッセージ履歴

        Returns:
            XML形式の文字列
        """
        formatted = []

        for i, msg in enumerate(messages, 1):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")

            # Claude Code SDK format対応
            if isinstance(content, list):
                text_parts = []
                for block in content:
                    if isinstance(block, dict):
                        text_parts.append(block.get("text", ""))
                content = "\n".join(text_parts)

            formatted.append(
                f"""<message index="{i}" role="{role}">
{content}
</message>"""
            )

        return "\n".join(formatted)
