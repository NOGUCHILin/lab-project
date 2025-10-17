"""Use case for importing skill sheet from CSV"""

import csv
from dataclasses import dataclass
from datetime import datetime
from io import StringIO
from uuid import UUID, uuid4

from ...domain.entities.business_skill import BusinessSkill
from ...domain.entities.employee import Employee
from ...domain.entities.employee_skill import EmployeeSkill
from ...domain.repositories.employee_repository import EmployeeRepository
from ...domain.repositories.skill_repository import SkillRepository
from ...domain.value_objects.skill_category import SkillCategory

# Skill name to category mapping
SKILL_CATEGORY_MAP = {
    # 顧客対応
    "返信": SkillCategory.CUSTOMER_SUPPORT,
    "振込ﾒｯｾ": SkillCategory.CUSTOMER_SUPPORT,
    "催促": SkillCategory.CUSTOMER_SUPPORT,
    "査定結果": SkillCategory.CUSTOMER_SUPPORT,
    "返送交渉": SkillCategory.CUSTOMER_SUPPORT,
    "電話対応": SkillCategory.CUSTOMER_SUPPORT,
    "発送完了連絡": SkillCategory.CUSTOMER_SUPPORT,
    # 物流
    "梱包キット作成": SkillCategory.LOGISTICS,
    "開封": SkillCategory.LOGISTICS,
    "成約仕分": SkillCategory.LOGISTICS,
    "検品": SkillCategory.LOGISTICS,
    "発送準備": SkillCategory.LOGISTICS,
    "送り状作成": SkillCategory.LOGISTICS,
    # 査定・修理
    "ｱｸﾃｨﾍﾞｰﾄ": SkillCategory.APPRAISAL,
    "査定": SkillCategory.APPRAISAL,
    "修理": SkillCategory.APPRAISAL,
    "パーツ注文": SkillCategory.APPRAISAL,
    "店舗査定": SkillCategory.APPRAISAL,
    "店舗修理受付": SkillCategory.APPRAISAL,
    "店舗修理お渡し": SkillCategory.APPRAISAL,
    # 販売
    "出品": SkillCategory.SALES,
    "ﾑｽﾋﾞｰ撮影": SkillCategory.SALES,
    "ﾑｽﾋﾞｰ出品": SkillCategory.SALES,
    "新品価格変更": SkillCategory.SALES,
    "法人販売": SkillCategory.SALES,
    # 管理
    "KPI入力": SkillCategory.MANAGEMENT,
    "実残高入力": SkillCategory.MANAGEMENT,
    "座席決定": SkillCategory.MANAGEMENT,
    "タスク設定": SkillCategory.MANAGEMENT,
    "BM在庫確認": SkillCategory.MANAGEMENT,
    "進捗変更": SkillCategory.MANAGEMENT,
    "品質管理": SkillCategory.MANAGEMENT,
    # 店舗
    "店舗準備": SkillCategory.STORE_OPERATION,
}


@dataclass(frozen=True)
class ImportSkillSheetRequest:
    """Request for importing skill sheet"""

    csv_content: str  # CSV file content as string


@dataclass(frozen=True)
class ImportSkillSheetResponse:
    """Response with import statistics"""

    employees_imported: int
    skills_imported: int
    associations_imported: int


class ImportSkillSheetUseCase:
    """Use case for importing skill sheet from CSV

    Expected CSV format:
    - First row: skill names (columns)
    - Subsequent rows: employee_name, skill1, skill2, ...
    - "○" indicates the employee has the skill
    """

    def __init__(
        self,
        employee_repository: EmployeeRepository,
        skill_repository: SkillRepository,
    ):
        self._employee_repository = employee_repository
        self._skill_repository = skill_repository

    async def execute(self, request: ImportSkillSheetRequest) -> ImportSkillSheetResponse:
        """Execute the use case"""
        # Parse CSV
        reader = csv.reader(StringIO(request.csv_content))
        rows = list(reader)

        if len(rows) < 2:
            raise ValueError("CSV must have at least 2 rows (header + data)")

        # First row is skill names (skip first column which is empty)
        skill_names = [name.strip() for name in rows[0][1:] if name.strip()]

        # Import skills
        skill_map: dict[str, UUID] = {}
        for idx, skill_name in enumerate(skill_names):
            existing_skill = await self._skill_repository.find_skill_by_name(skill_name)

            if existing_skill:
                skill_map[skill_name] = existing_skill.skill_id
            else:
                # Create new skill
                skill_id = uuid4()
                category = SKILL_CATEGORY_MAP.get(skill_name, SkillCategory.MANAGEMENT)
                skill = BusinessSkill(
                    skill_id=skill_id,
                    skill_name=skill_name,
                    category=category,
                    display_order=idx,
                    is_active=True,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )
                await self._skill_repository.save_skill(skill)
                skill_map[skill_name] = skill_id

        # Import employees and their skills
        employee_count = 0
        association_count = 0

        for row in rows[1:]:
            if not row or not row[0].strip():
                continue

            employee_name = row[0].strip()
            skill_values = row[1 : len(skill_names) + 1]

            # Create or update employee
            existing_employee = await self._employee_repository.find_by_name(employee_name)

            if existing_employee:
                employee_id = existing_employee.employee_id
            else:
                employee_id = uuid4()
                employee = Employee(
                    employee_id=employee_id,
                    name=employee_name,
                    is_active=True,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )
                await self._employee_repository.save(employee)
                employee_count += 1

            # Add employee skills (where value is "○")
            for idx, value in enumerate(skill_values):
                if value.strip() == "○" and idx < len(skill_names):
                    skill_name = skill_names[idx]
                    skill_id = skill_map[skill_name]

                    # Check if association already exists
                    try:
                        employee_skill = EmployeeSkill(
                            id=uuid4(),
                            employee_id=employee_id,
                            skill_id=skill_id,
                            acquired_at=datetime.now(),
                            created_at=datetime.now(),
                            updated_at=datetime.now(),
                        )
                        await self._skill_repository.add_employee_skill(employee_skill)
                        association_count += 1
                    except Exception:
                        # Association might already exist (UNIQUE constraint)
                        pass

        return ImportSkillSheetResponse(
            employees_imported=employee_count,
            skills_imported=len(skill_map),
            associations_imported=association_count,
        )
