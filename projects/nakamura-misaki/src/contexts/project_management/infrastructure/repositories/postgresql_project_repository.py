"""PostgreSQL Project Repository Implementation"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database.schema import ProjectTable, ProjectTaskTable

from ...domain.entities.project import Project
from ...domain.repositories.project_repository import ProjectRepository
from ...domain.value_objects.project_status import ProjectStatus


class PostgreSQLProjectRepository(ProjectRepository):
    """PostgreSQL implementation of ProjectRepository"""

    def __init__(self, session: AsyncSession):
        """Initialize repository

        Args:
            session: SQLAlchemy async session
        """
        self._session = session

    async def save(self, project: Project) -> Project:
        """Save a project"""
        # Check if project exists
        stmt = select(ProjectTable).where(ProjectTable.project_id == project.project_id)
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            # Update existing project
            existing.name = project.name
            existing.description = project.description
            existing.owner_user_id = project.owner_user_id
            existing.deadline = project.deadline
            existing.status = project.status.value
            existing.updated_at = project.updated_at
        else:
            # Create new project
            project_row = ProjectTable(
                project_id=project.project_id,
                name=project.name,
                description=project.description,
                owner_user_id=project.owner_user_id,
                deadline=project.deadline,
                status=project.status.value,
                created_at=project.created_at,
                updated_at=project.updated_at,
            )
            self._session.add(project_row)

        await self._session.commit()
        return project

    async def find_by_id(self, project_id: UUID) -> Project | None:
        """Find a project by ID"""
        stmt = select(ProjectTable).where(ProjectTable.project_id == project_id)
        result = await self._session.execute(stmt)
        row = result.scalar_one_or_none()

        if not row:
            return None

        # Get associated task IDs
        task_ids = await self.get_task_ids(project_id)

        return Project(
            project_id=row.project_id,
            name=row.name,
            description=row.description,
            owner_user_id=row.owner_user_id,
            deadline=row.deadline,
            status=ProjectStatus(row.status),
            created_at=row.created_at,
            updated_at=row.updated_at,
            task_ids=task_ids,
        )

    async def find_by_owner(
        self,
        owner_user_id: str,
        status: ProjectStatus | None = None,
    ) -> list[Project]:
        """Find projects by owner"""
        stmt = select(ProjectTable).where(ProjectTable.owner_user_id == owner_user_id)

        if status:
            stmt = stmt.where(ProjectTable.status == status.value)

        result = await self._session.execute(stmt)
        rows = result.scalars().all()

        projects = []
        for row in rows:
            task_ids = await self.get_task_ids(row.project_id)
            projects.append(
                Project(
                    project_id=row.project_id,
                    name=row.name,
                    description=row.description,
                    owner_user_id=row.owner_user_id,
                    deadline=row.deadline,
                    status=ProjectStatus(row.status),
                    created_at=row.created_at,
                    updated_at=row.updated_at,
                    task_ids=task_ids,
                )
            )

        return projects

    async def delete(self, project_id: UUID) -> None:
        """Delete a project"""
        stmt = delete(ProjectTable).where(ProjectTable.project_id == project_id)
        await self._session.execute(stmt)
        await self._session.commit()

    async def get_task_ids(self, project_id: UUID) -> list[UUID]:
        """Get all task IDs associated with a project"""
        stmt = (
            select(ProjectTaskTable.task_id)
            .where(ProjectTaskTable.project_id == project_id)
            .order_by(ProjectTaskTable.position)
        )
        result = await self._session.execute(stmt)
        return [row[0] for row in result.all()]

    async def add_task_to_project(
        self,
        project_id: UUID,
        task_id: UUID,
        position: int,
    ) -> None:
        """Add a task to a project"""
        project_task = ProjectTaskTable(
            project_id=project_id,
            task_id=task_id,
            position=position,
            created_at=datetime.now(),
        )
        self._session.add(project_task)
        await self._session.commit()

    async def remove_task_from_project(
        self,
        project_id: UUID,
        task_id: UUID,
    ) -> None:
        """Remove a task from a project"""
        stmt = delete(ProjectTaskTable).where(
            and_(
                ProjectTaskTable.project_id == project_id,
                ProjectTaskTable.task_id == task_id,
            )
        )
        await self._session.execute(stmt)
        await self._session.commit()
