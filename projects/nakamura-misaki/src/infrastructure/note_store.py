"""
Note Store - Anthropic Structured Note-Taking

This module implements Anthropic's recommended "Structured Note-Taking" strategy:
- Agents write persistent notes outside the context window
- Notes are retrieved when needed for context
- Enables session-to-session memory
- Reduces token consumption by storing important info externally

Reference: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
"""

import json
from datetime import datetime
from pathlib import Path


class NoteStore:
    """
    Anthropic推奨: コンテキスト外永続化ノート

    Features:
    - Persistent storage in user workspace
    - Category-based organization
    - JSON serialization
    - Automatic timestamping
    - Cross-session memory
    """

    # Note categories
    CATEGORY_CODE_CHANGES = "code_changes"
    CATEGORY_DECISIONS = "decisions"
    CATEGORY_TODOS = "todos"
    CATEGORY_ERRORS = "errors"
    CATEGORY_LEARNINGS = "learnings"

    def __init__(self, workspace_path: str):
        """
        Initialize Note Store

        Args:
            workspace_path: User's workspace directory
        """
        self.workspace_path = Path(workspace_path)
        self.notes_dir = self.workspace_path / ".nakamura_notes"
        self.notes_dir.mkdir(parents=True, exist_ok=True)

    async def save_note(
        self, user_id: str, category: str, content: str, metadata: dict | None = None
    ) -> None:
        """
        構造化されたノートを保存

        Args:
            user_id: ユーザーID
            category: ノートカテゴリ（code_changes, decisions, todos, errors, learnings）
            content: ノート内容
            metadata: 追加メタデータ（オプション）
        """
        note_file = self.notes_dir / f"{category}.json"

        note = {
            "user_id": user_id,
            "category": category,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }

        # 既存ノート読み込み
        notes = []
        if note_file.exists():
            try:
                with open(note_file, encoding="utf-8") as f:
                    notes = json.load(f)
            except json.JSONDecodeError:
                print(f"⚠️ Corrupted note file: {note_file}, creating new")
                notes = []

        notes.append(note)

        # 保存（最新100件のみ保持）
        notes = notes[-100:]

        with open(note_file, "w", encoding="utf-8") as f:
            json.dump(notes, f, indent=2, ensure_ascii=False)

        print(f"📝 Note saved: {category} ({len(content)} chars)")

    async def retrieve_notes(
        self, user_id: str, category: str | None = None, limit: int = 10
    ) -> str:
        """
        ノートをXML形式で取得

        Args:
            user_id: ユーザーID
            category: カテゴリでフィルタ（Noneの場合は全カテゴリ）
            limit: 最大取得件数

        Returns:
            XML形式のノート文字列
        """
        notes = []

        if category:
            # 特定カテゴリのみ取得
            note_file = self.notes_dir / f"{category}.json"
            if note_file.exists():
                try:
                    with open(note_file, encoding="utf-8") as f:
                        category_notes = json.load(f)
                        notes.extend(category_notes[-limit:])
                except json.JSONDecodeError:
                    print(f"⚠️ Cannot read note file: {note_file}")
        else:
            # 全カテゴリ取得
            for note_file in self.notes_dir.glob("*.json"):
                try:
                    with open(note_file, encoding="utf-8") as f:
                        category_notes = json.load(f)
                        notes.extend(category_notes)
                except json.JSONDecodeError:
                    continue

            # 新しい順にソート
            notes.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            notes = notes[:limit]

        if not notes:
            return "<notes>\n<!-- No notes found -->\n</notes>"

        # XML形式に整形
        xml_notes = ["<notes>"]
        for note in notes:
            category_val = note.get("category", "unknown")
            timestamp_val = note.get("timestamp", "")
            content_val = note.get("content", "")
            metadata_val = note.get("metadata", {})

            metadata_str = ""
            if metadata_val:
                metadata_items = [
                    f'{k}="{v}"' for k, v in metadata_val.items() if v
                ]
                if metadata_items:
                    metadata_str = " " + " ".join(metadata_items)

            xml_notes.append(
                f"""
<note category="{category_val}" timestamp="{timestamp_val}"{metadata_str}>
{content_val}
</note>"""
            )
        xml_notes.append("</notes>")

        return "\n".join(xml_notes)

    async def get_summary(self, user_id: str) -> str:
        """
        全ノートの簡潔なサマリーを取得

        Args:
            user_id: ユーザーID

        Returns:
            サマリーテキスト
        """
        summary_parts = []

        categories = [
            self.CATEGORY_CODE_CHANGES,
            self.CATEGORY_DECISIONS,
            self.CATEGORY_TODOS,
            self.CATEGORY_ERRORS,
            self.CATEGORY_LEARNINGS,
        ]

        category_names = {
            self.CATEGORY_CODE_CHANGES: "コード変更",
            self.CATEGORY_DECISIONS: "決定事項",
            self.CATEGORY_TODOS: "TODO",
            self.CATEGORY_ERRORS: "エラー",
            self.CATEGORY_LEARNINGS: "学習事項",
        }

        for category in categories:
            note_file = self.notes_dir / f"{category}.json"
            if note_file.exists():
                try:
                    with open(note_file, encoding="utf-8") as f:
                        notes = json.load(f)
                        count = len(notes)
                        if count > 0:
                            name = category_names.get(category, category)
                            summary_parts.append(f"- {name}: {count}件")
                except json.JSONDecodeError:
                    continue

        if not summary_parts:
            return "ノートはまだありません"

        return "保存されているノート:\n" + "\n".join(summary_parts)

    async def clear_category(self, category: str) -> bool:
        """
        特定カテゴリのノートを削除

        Args:
            category: カテゴリ名

        Returns:
            削除成功フラグ
        """
        note_file = self.notes_dir / f"{category}.json"
        if note_file.exists():
            note_file.unlink()
            print(f"🗑️ Cleared notes: {category}")
            return True
        return False

    async def auto_save_code_changes(
        self, user_id: str, file_path: str, change_type: str, description: str
    ) -> None:
        """
        コード変更を自動的にノート保存

        Args:
            user_id: ユーザーID
            file_path: 変更ファイルパス
            change_type: 変更タイプ（created, modified, deleted）
            description: 変更内容説明
        """
        content = f"""ファイル: {file_path}
変更タイプ: {change_type}
内容: {description}"""

        await self.save_note(
            user_id=user_id,
            category=self.CATEGORY_CODE_CHANGES,
            content=content,
            metadata={"file": file_path, "type": change_type},
        )

    async def auto_save_decision(self, user_id: str, decision: str, reason: str) -> None:
        """
        重要な決定事項を自動保存

        Args:
            user_id: ユーザーID
            decision: 決定内容
            reason: 理由
        """
        content = f"""決定: {decision}
理由: {reason}"""

        await self.save_note(
            user_id=user_id, category=self.CATEGORY_DECISIONS, content=content
        )

    async def auto_save_error(
        self, user_id: str, error_message: str, solution: str | None = None
    ) -> None:
        """
        エラーと解決策を自動保存

        Args:
            user_id: ユーザーID
            error_message: エラーメッセージ
            solution: 解決策（オプション）
        """
        content = f"""エラー: {error_message}"""
        if solution:
            content += f"\n解決策: {solution}"

        await self.save_note(user_id=user_id, category=self.CATEGORY_ERRORS, content=content)
