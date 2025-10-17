"""Use case for suggesting task assignees based on required skills"""

from dataclasses import dataclass

from ...domain.entities.employee import Employee
from ...domain.repositories.skill_repository import SkillRepository


@dataclass(frozen=True)
class SuggestAssigneesRequest:
    """Request for suggesting assignees"""

    required_skills: list[str]
    limit: int = 5


@dataclass(frozen=True)
class SuggestAssigneesResponse:
    """Response with suggested assignees"""

    suggestions: list[tuple[Employee, int]]  # (Employee, match_count)


class SuggestAssigneesUseCase:
    """Use case for suggesting task assignees

    Given a list of required skills, returns employees who possess those skills,
    ordered by the number of matching skills.
    """

    def __init__(self, skill_repository: SkillRepository):
        self._skill_repository = skill_repository

    async def execute(self, request: SuggestAssigneesRequest) -> SuggestAssigneesResponse:
        """Execute the use case"""
        if not request.required_skills:
            return SuggestAssigneesResponse(suggestions=[])

        suggestions = await self._skill_repository.suggest_assignees(
            required_skills=request.required_skills,
            limit=request.limit,
        )

        return SuggestAssigneesResponse(suggestions=suggestions)
