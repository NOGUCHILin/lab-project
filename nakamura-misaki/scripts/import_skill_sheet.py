"""Script to import skill sheet from CSV file"""

import asyncio
import sys
from pathlib import Path

from src.infrastructure.database.connection import get_db_session

from src.contexts.workforce_management.application.use_cases.import_skill_sheet import (
    ImportSkillSheetRequest,
    ImportSkillSheetUseCase,
)
from src.contexts.workforce_management.infrastructure.repositories.postgresql_employee_repository import (
    PostgreSQLEmployeeRepository,
)
from src.contexts.workforce_management.infrastructure.repositories.postgresql_skill_repository import (
    PostgreSQLSkillRepository,
)


async def import_skill_sheet(csv_path: str) -> None:
    """Import skill sheet from CSV file

    Args:
        csv_path: Path to CSV file
    """
    # Read CSV file
    csv_file = Path(csv_path)
    if not csv_file.exists():
        print(f"Error: CSV file not found: {csv_path}")
        sys.exit(1)

    csv_content = csv_file.read_text(encoding="utf-8")

    # Execute import
    async with get_db_session() as session:
        employee_repo = PostgreSQLEmployeeRepository(session)
        skill_repo = PostgreSQLSkillRepository(session)

        use_case = ImportSkillSheetUseCase(
            employee_repository=employee_repo,
            skill_repository=skill_repo,
        )

        request = ImportSkillSheetRequest(csv_content=csv_content)

        print(f"Importing skill sheet from: {csv_path}")
        response = await use_case.execute(request)

        await session.commit()

        print("\n✅ Import completed successfully!")
        print(f"- Employees imported: {response.employees_imported}")
        print(f"- Skills imported: {response.skills_imported}")
        print(f"- Skill associations created: {response.associations_imported}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/import_skill_sheet.py <csv_file_path>")
        print("\nExample:")
        print("  uv run python scripts/import_skill_sheet.py ~/Downloads/スキルシート.csv")
        sys.exit(1)

    csv_path = sys.argv[1]
    asyncio.run(import_skill_sheet(csv_path))
