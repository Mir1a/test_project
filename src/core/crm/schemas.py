from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from src.core.enums import TicketStatus, UserRole


class UserCreateRequest(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str | None = None
    role: UserRole = UserRole.WORKER
    is_active: bool = True


class UserUpdateRequest(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=20)
    email: EmailStr | None = None
    password: str | None = Field(None, min_length=6)
    full_name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class UserPatchRequest(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=20)
    email: EmailStr | None = None
    password: str | None = Field(None, min_length=6)
    full_name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    full_name: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    total: int
    users: list[UserResponse]


class ClientInfo(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


class AssignedUserInfo(BaseModel):
    id: int
    username: str
    full_name: str | None

    class Config:
        from_attributes = True


class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    priority: str
    client_id: int
    assigned_to_id: int | None
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None
    client: ClientInfo
    assigned_to_user: AssignedUserInfo | None

    class Config:
        from_attributes = True


class TicketListResponse(BaseModel):
    total: int
    tickets: list[TicketResponse]


class AssignWorkerRequest(BaseModel):
    worker_id: int | None


class UpdateTicketAssignmentRequest(BaseModel):
    assigned_to_id: int | None
    status: TicketStatus | None = None

class UpdateTicketStatusRequest(BaseModel):
    status: TicketStatus