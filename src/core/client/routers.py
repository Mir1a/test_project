from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_async_session
from src.core.client.schemas import TicketCreateRequest, TicketCreateResponse
from src.core.client.services import create_ticket_with_client


router = APIRouter(prefix="/client", tags=["Client"])


@router.post("/tickets", response_model=TicketCreateResponse, status_code=201)
async def submit_ticket(
    ticket_data: TicketCreateRequest,
    session: AsyncSession = Depends(get_async_session)
):
    return await create_ticket_with_client(session, ticket_data)
