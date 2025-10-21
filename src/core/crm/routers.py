from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_async_session
from src.core.crm import services
from src.security import require_admin
from src.core.crm.schemas import (
    UserCreateRequest,
    UserUpdateRequest,
    UserPatchRequest,
    UserResponse,
    UserListResponse
)


router = APIRouter(prefix="/users", tags=["Users Management"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
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


@router.get("", response_model=UserListResponse)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session),
    _: None = Depends(require_admin)
):
    result = await services.get_users(skip, limit, db)
    return result


@router.get("/{user_id}", response_model=UserResponse)
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


@router.put("/{user_id}", response_model=UserResponse)
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


@router.patch("/{user_id}", response_model=UserResponse)
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


@router.delete("/{user_id}")
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