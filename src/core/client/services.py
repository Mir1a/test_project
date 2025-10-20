from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.core.models import Client, Ticket
from src.core.client.schemas import TicketCreateRequest, TicketCreateResponse, ClientResponse, TicketResponse


async def get_or_create_client(session: AsyncSession, name: str, email: str) -> Client:
    result = await session.execute(
        select(Client).where(Client.email == email)
    )
    client = result.scalar_one_or_none()

    if client:
        if client.name != name:
            client.name = name
            await session.commit()
            await session.refresh(client)
        return client

    new_client = Client(name=name, email=email)
    session.add(new_client)
    await session.commit()
    await session.refresh(new_client)
    return new_client


async def create_ticket_with_client(
    session: AsyncSession,
    ticket_data: TicketCreateRequest
) -> TicketCreateResponse:
    client = await get_or_create_client(
        session=session,
        name=ticket_data.client_name,
        email=ticket_data.client_email
    )

    ticket = Ticket(
        title=ticket_data.title,
        description=ticket_data.description,
        client_id=client.id
    )

    session.add(ticket)
    await session.commit()
    await session.refresh(ticket)

    return TicketCreateResponse(
        ticket=TicketResponse.model_validate(ticket),
        client=ClientResponse.model_validate(client),
        message="Ticket created successfully"
    )
