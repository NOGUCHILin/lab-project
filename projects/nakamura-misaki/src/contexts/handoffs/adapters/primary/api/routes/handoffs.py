"""Handoffs API Routes"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.contexts.handoffs.application.use_cases.accept_handoff import (
    AcceptHandoffCommand,
    AcceptHandoffUseCase,
)
from src.contexts.handoffs.application.use_cases.complete_handoff import (
    CompleteHandoffCommand,
    CompleteHandoffUseCase,
)
from src.contexts.handoffs.application.use_cases.create_handoff import (
    CreateHandoffCommand,
    CreateHandoffUseCase,
)
from src.contexts.handoffs.application.use_cases.query_pending_handoffs import (
    QueryPendingHandoffsCommand,
    QueryPendingHandoffsUseCase,
)
from src.contexts.handoffs.application.use_cases.query_user_handoffs import (
    QueryUserHandoffsCommand,
    QueryUserHandoffsUseCase,
)
from src.infrastructure.di import get_di_container

router = APIRouter(prefix="/handoffs", tags=["handoffs"])


# Request/Response Models
class CreateHandoffRequest(BaseModel):
    """Create handoff request"""

    from_user_id: str
    to_user_id: str
    progress_note: str
    next_steps: str
    handoff_at: datetime
    task_id: str | None = None


class HandoffResponse(BaseModel):
    """Handoff response"""

    id: str
    task_id: str | None
    from_user_id: str
    to_user_id: str
    progress_note: str
    next_steps: str
    status: str
    handoff_at: datetime
    reminded_at: datetime | None
    completed_at: datetime | None
    created_at: datetime


class AcceptHandoffRequest(BaseModel):
    """Accept handoff request"""

    handoff_id: str


class CompleteHandoffRequest(BaseModel):
    """Complete handoff request"""

    handoff_id: str
    completed_at: datetime | None = None


# Dependency to get use cases
def get_create_handoff_use_case():
    """Get CreateHandoffUseCase"""
    container = get_di_container()
    return container.build_create_handoff_use_case()


def get_accept_handoff_use_case():
    """Get AcceptHandoffUseCase"""
    container = get_di_container()
    return container.build_accept_handoff_use_case()


def get_complete_handoff_use_case():
    """Get CompleteHandoffUseCase"""
    container = get_di_container()
    return container.build_complete_handoff_use_case()


def get_query_pending_handoffs_use_case():
    """Get QueryPendingHandoffsUseCase"""
    container = get_di_container()
    return container.build_query_pending_handoffs_use_case()


def get_query_user_handoffs_use_case():
    """Get QueryUserHandoffsUseCase"""
    container = get_di_container()
    return container.build_query_user_handoffs_use_case()


# API Endpoints
@router.post("/", response_model=HandoffResponse)
def create_handoff(
    request: CreateHandoffRequest,
    use_case: CreateHandoffUseCase = Depends(get_create_handoff_use_case),
):
    """Create a new handoff"""
    try:
        command = CreateHandoffCommand(
            from_user_id=request.from_user_id,
            to_user_id=request.to_user_id,
            progress_note=request.progress_note,
            next_steps=request.next_steps,
            handoff_at=request.handoff_at,
            task_id=request.task_id,
        )
        handoff = use_case.execute(command)
        return _to_response(handoff)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{handoff_id}/accept", response_model=HandoffResponse)
def accept_handoff(
    handoff_id: str,
    use_case: AcceptHandoffUseCase = Depends(get_accept_handoff_use_case),
):
    """Accept a handoff"""
    try:
        command = AcceptHandoffCommand(handoff_id=handoff_id)
        handoff = use_case.execute(command)
        return _to_response(handoff)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{handoff_id}/complete", response_model=HandoffResponse)
def complete_handoff(
    handoff_id: str,
    request: CompleteHandoffRequest | None = None,
    use_case: CompleteHandoffUseCase = Depends(get_complete_handoff_use_case),
):
    """Complete a handoff"""
    try:
        command = CompleteHandoffCommand(
            handoff_id=handoff_id,
            completed_at=request.completed_at if request else None,
        )
        handoff = use_case.execute(command)
        return _to_response(handoff)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/pending/{user_id}", response_model=list[HandoffResponse])
def get_pending_handoffs(
    user_id: str,
    use_case: QueryPendingHandoffsUseCase = Depends(
        get_query_pending_handoffs_use_case
    ),
):
    """Get pending handoffs for a user"""
    command = QueryPendingHandoffsCommand(user_id=user_id)
    handoffs = use_case.execute(command)
    return [_to_response(h) for h in handoffs]


@router.get("/user/{user_id}", response_model=list[HandoffResponse])
def get_user_handoffs(
    user_id: str,
    include_completed: bool = False,
    use_case: QueryUserHandoffsUseCase = Depends(get_query_user_handoffs_use_case),
):
    """Get all handoffs for a user"""
    command = QueryUserHandoffsCommand(
        user_id=user_id, include_completed=include_completed
    )
    handoffs = use_case.execute(command)
    return [_to_response(h) for h in handoffs]


def _to_response(handoff) -> HandoffResponse:
    """Convert handoff entity to response"""
    return HandoffResponse(
        id=str(handoff.id.value),
        task_id=str(handoff.task_id.value) if handoff.task_id else None,
        from_user_id=handoff.from_user_id.value,
        to_user_id=handoff.to_user_id.value,
        progress_note=handoff.content.progress_note,
        next_steps=handoff.content.next_steps,
        status=handoff.status.state.value,
        handoff_at=handoff.handoff_at,
        reminded_at=handoff.status.reminded_at,
        completed_at=handoff.status.completed_at,
        created_at=handoff.created_at,
    )
