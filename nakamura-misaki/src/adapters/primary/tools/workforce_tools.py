"""Workforce management tools for Claude Tool Use."""

from typing import Any

from src.contexts.workforce_management.application.use_cases.suggest_assignees import (
    SuggestAssigneesRequest,
    SuggestAssigneesUseCase,
)
from src.contexts.workforce_management.domain.repositories.skill_repository import SkillRepository

from .base_tool import BaseTool


class FindEmployeesWithSkillTool(BaseTool):
    """特定のスキルを持つ社員を検索するTool.

    ユーザーが「〜できる人は誰？」「〜を担当できるのは？」などの質問をした際に使用。
    """

    def __init__(self, skill_repository: SkillRepository):
        """Initialize FindEmployeesWithSkillTool.

        Args:
            skill_repository: SkillRepository instance
        """
        self._skill_repository = skill_repository

    @property
    def name(self) -> str:
        return "find_employees_with_skill"

    @property
    def description(self) -> str:
        return "特定のスキル（例: 返信、査定、出品など）を持つ社員を検索する"

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "skill_name": {
                    "type": "string",
                    "description": "検索するスキル名（例: 返信、査定、出品）",
                }
            },
            "required": ["skill_name"],
        }

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        """Execute the tool.

        Args:
            skill_name: Skill name to search for

        Returns:
            Dict with execution result
        """
        skill_name = kwargs.get("skill_name", "")

        employees = await self._skill_repository.find_employees_with_skill(skill_name)

        if not employees:
            return {
                "success": True,
                "skill_name": skill_name,
                "employees": [],
                "message": f"「{skill_name}」スキルを持つ社員は見つかりませんでした。",
            }

        employee_names = [emp.name for emp in employees]
        return {
            "success": True,
            "skill_name": skill_name,
            "employees": employee_names,
            "message": f"「{skill_name}」スキルを持つ社員: {', '.join(employee_names)}（{len(employee_names)}名）",
        }


class GetEmployeeSkillsTool(BaseTool):
    """特定の社員が持つスキル一覧を取得するTool.

    ユーザーが「〜さんは何ができるの？」「〜さんのスキルは？」などの質問をした際に使用。
    """

    def __init__(self, skill_repository: SkillRepository):
        """Initialize GetEmployeeSkillsTool.

        Args:
            skill_repository: SkillRepository instance
        """
        self._skill_repository = skill_repository

    @property
    def name(self) -> str:
        return "get_employee_skills"

    @property
    def description(self) -> str:
        return "特定の社員が持つスキル一覧を取得する"

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "employee_name": {
                    "type": "string",
                    "description": "社員名（例: 江口 那都、野口 器）",
                }
            },
            "required": ["employee_name"],
        }

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        """Execute the tool.

        Args:
            employee_name: Employee name to search for

        Returns:
            Dict with execution result
        """
        from src.contexts.workforce_management.infrastructure.repositories.postgresql_employee_repository import (
            PostgreSQLEmployeeRepository,
        )
        from src.infrastructure.database.connection import get_db_session

        employee_name = kwargs.get("employee_name", "")

        # Get employee by name
        async with get_db_session() as session:
            employee_repo = PostgreSQLEmployeeRepository(session)
            employee = await employee_repo.find_by_name(employee_name)

            if not employee:
                return {
                    "success": False,
                    "employee_name": employee_name,
                    "error": f"社員「{employee_name}」は見つかりませんでした。",
                }

            skills = await self._skill_repository.find_employee_skills(employee.employee_id)

        if not skills:
            return {
                "success": True,
                "employee_name": employee_name,
                "skills": [],
                "message": f"{employee_name}さんのスキル情報は登録されていません。",
            }

        skill_names = [skill.skill_name for skill in skills]
        return {
            "success": True,
            "employee_name": employee_name,
            "skills": skill_names,
            "message": f"{employee_name}さんのスキル: {', '.join(skill_names)}（{len(skill_names)}種類）",
        }


class SuggestAssigneesTool(BaseTool):
    """タスクに必要なスキルから適任者を提案するTool.

    ユーザーが「〜と〜ができる人は？」「このタスクは誰に任せれば？」などの質問をした際に使用。
    """

    def __init__(self, suggest_assignees_use_case: SuggestAssigneesUseCase):
        """Initialize SuggestAssigneesTool.

        Args:
            suggest_assignees_use_case: SuggestAssigneesUseCase instance
        """
        self._suggest_assignees_use_case = suggest_assignees_use_case

    @property
    def name(self) -> str:
        return "suggest_assignees"

    @property
    def description(self) -> str:
        return "タスクに必要な複数のスキルから、最適な担当者を提案する"

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "required_skills": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "必要なスキルのリスト（例: ['返信', '査定']）",
                },
                "limit": {
                    "type": "integer",
                    "description": "提案する候補者の最大数（デフォルト: 5）",
                    "default": 5,
                },
            },
            "required": ["required_skills"],
        }

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        """Execute the tool.

        Args:
            required_skills: List of required skill names
            limit: Maximum number of candidates to suggest

        Returns:
            Dict with execution result
        """
        required_skills = kwargs.get("required_skills", [])
        limit = kwargs.get("limit", 5)

        request = SuggestAssigneesRequest(required_skills=required_skills, limit=limit)
        response = await self._suggest_assignees_use_case.execute(request)

        if not response.suggestions:
            return {
                "success": True,
                "required_skills": required_skills,
                "suggestions": [],
                "message": f"必要なスキル（{', '.join(required_skills)}）を持つ社員は見つかりませんでした。",
            }

        suggestions_data = []
        for employee, match_count in response.suggestions:
            total_required = len(required_skills)
            match_percentage = (match_count / total_required) * 100
            suggestions_data.append({
                "name": employee.name,
                "match_count": match_count,
                "total_required": total_required,
                "match_percentage": match_percentage,
            })

        result_lines = [f"必要なスキル: {', '.join(required_skills)}\n推奨担当者:"]
        for suggestion in suggestions_data:
            result_lines.append(
                f"- {suggestion['name']}: {suggestion['match_count']}/{suggestion['total_required']}スキル適合（{suggestion['match_percentage']:.0f}%）"
            )

        return {
            "success": True,
            "required_skills": required_skills,
            "suggestions": suggestions_data,
            "message": "\n".join(result_lines),
        }
