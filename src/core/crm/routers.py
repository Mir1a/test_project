from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.enums import TicketStatus
from src.security import get_current_user
from src.database import get_async_session
from src.core.crm import services
from src.security import require_admin, require_worker
from src.core.crm.schemas import (
    TicketListResponse,
    TicketResponse,
    UpdateTicketAssignmentRequest,
    UpdateTicketStatusRequest,
    UserCreateRequest,
    UserUpdateRequest,
    UserPatchRequest,
    UserResponse,
    UserListResponse
)


user_managment_router = APIRouter(prefix="/users", tags=["Users Management"])


@user_managment_router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateRequest,
    db: AsyncSession = Depends(get_async_session),
    _: None = Depends(require_admin)
):
    try:
        user = await services.create_user(user_data, db)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@user_managment_router.get("", response_model=UserListResponse)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
    _: None = Depends(require_admin)
):
    result = await services.get_users(skip, limit, db)
    return result


@user_managment_router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_async_session),
    _: None = Depends(require_admin)
):
    try:
        user = await services.get_user_by_id(user_id, db)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@user_managment_router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdateRequest,
    db: AsyncSession = Depends(get_async_session),
    _: None = Depends(require_admin)
):
    try:
        user = await services.update_user(user_id, user_data, db)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@user_managment_router.patch("/{user_id}", response_model=UserResponse)
async def patch_user(
    user_id: int,
    user_data: UserPatchRequest,
    db: AsyncSession = Depends(get_async_session),
    _: None = Depends(require_admin)
):
    try:
        user = await services.patch_user(user_id, user_data, db)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@user_managment_router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_session),
    _: None = Depends(require_admin)
):
    try:
        result = await services.delete_user(user_id, db)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    

ticket_router = APIRouter(prefix="/tickets", tags=["Tickets Management"])


@ticket_router.get("", response_model=TicketListResponse)
async def get_all_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = Query(None, description="Search by ticket title"),
    status: TicketStatus | None = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_async_session),
    admin_user = Depends(require_admin)
):
    result = await services.get_all_tickets(skip, limit, search, status, db)
    return result


@ticket_router.get("/my", response_model=TicketListResponse)
async def get_my_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = Query(None, description="Search by ticket title"),
    status: TicketStatus | None = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_async_session),
    current_worker = Depends(require_worker)
):
    result = await services.get_my_tickets(current_worker.id, skip, limit, search, status, db)
    return result


@ticket_router.patch("/{ticket_id}/assign", response_model=TicketResponse)
async def assign_worker_to_ticket(
    ticket_id: int,
    assignment_data: UpdateTicketAssignmentRequest,
    db: AsyncSession = Depends(get_async_session),
    admin_user = Depends(require_admin)
):
    try:
        ticket = await services.assign_worker_to_ticket(ticket_id, assignment_data, db)
        return ticket
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@ticket_router.delete("/{ticket_id}/assign", response_model=TicketResponse)
async def unassign_worker_from_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_async_session),
    admin_user = Depends(require_admin)
):
    try:
        ticket = await services.unassign_worker_from_ticket(ticket_id, db)
        return ticket
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    

@ticket_router.patch("/{ticket_id}/status", response_model=TicketResponse)
async def update_ticket_status(
    ticket_id: int,
    status_data: UpdateTicketStatusRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user = Depends(get_current_user)
):
    try:
        ticket = await services.update_ticket_status(ticket_id, status_data, current_user, db)
        return ticket
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )