from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from src.core.enums import TicketStatus, TicketPriority


class TicketCreateRequest(BaseModel):
    client_name: str = Field(..., min_length=1, max_length=100)
    client_email: EmailStr
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1)


class ClientResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True


class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    status: TicketStatus
    priority: TicketPriority
    client_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TicketCreateResponse(BaseModel):
    ticket: TicketResponse
    client: ClientResponse
    message: str = "Ticket created successfully"
