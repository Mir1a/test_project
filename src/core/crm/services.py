
import bcrypt
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.enums import UserRole
from src.core.models import Ticket, User


async def create_user(user_data, db_session: AsyncSession):
    stmt = select(User).where(User.username == user_data.username)
    result = await db_session.execute(stmt)
    if result.scalar_one_or_none():
        raise ValueError("Username already exists")
    
    stmt = select(User).where(User.email == user_data.email)
    result = await db_session.execute(stmt)
    if result.scalar_one_or_none():
        raise ValueError("Email already registered")
    
    password_hash = bcrypt.hashpw(
        user_data.password.encode('utf-8'), 
        bcrypt.gensalt()
    ).decode('utf-8')
    
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=password_hash,
        role=user_data.role,
        full_name=user_data.full_name,
        is_active=user_data.is_active
    )
    
    db_session.add(db_user)
    await db_session.commit()
    await db_session.refresh(db_user)
    
    return db_user


async def get_users(skip: int, limit: int, db_session: AsyncSession):
    count_stmt = select(func.count()).select_from(User)
    total_result = await db_session.execute(count_stmt)
    total = total_result.scalar()
    
    stmt = select(User).offset(skip).limit(limit)
    result = await db_session.execute(stmt)
    users = result.scalars().all()
    
    return {
        "total": total,
        "users": users
    }


async def get_user_by_id(user_id: int, db_session: AsyncSession):
    stmt = select(User).where(User.id == user_id)
    result = await db_session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise ValueError("User not found")
    
    return user


async def update_user(user_id: int, user_data, db_session: AsyncSession):
    stmt = select(User).where(User.id == user_id)
    result = await db_session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise ValueError("User not found")
    
    if user_data.username and user_data.username != user.username:
        stmt = select(User).where(User.username == user_data.username)
        result = await db_session.execute(stmt)
        if result.scalar_one_or_none():
            raise ValueError("Username already exists")
        user.username = user_data.username
    
    if user_data.email and user_data.email != user.email:
        stmt = select(User).where(User.email == user_data.email)
        result = await db_session.execute(stmt)
        if result.scalar_one_or_none():
            raise ValueError("Email already registered")
        user.email = user_data.email
    
    if user_data.password:
        password_hash = bcrypt.hashpw(
            user_data.password.encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
        user.password_hash = password_hash
    
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    
    if user_data.role is not None:
        user.role = user_data.role
    
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    
    await db_session.commit()
    await db_session.refresh(user)
    
    return user


async def patch_user(user_id: int, user_data, db_session: AsyncSession):
    stmt = select(User).where(User.id == user_id)
    result = await db_session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise ValueError("User not found")
    
    update_data = user_data.model_dump(exclude_unset=True)
    
    if "username" in update_data and update_data["username"] != user.username:
        stmt = select(User).where(User.username == update_data["username"])
        result = await db_session.execute(stmt)
        if result.scalar_one_or_none():
            raise ValueError("Username already exists")
        user.username = update_data["username"]
    
    if "email" in update_data and update_data["email"] != user.email:
        stmt = select(User).where(User.email == update_data["email"])
        result = await db_session.execute(stmt)
        if result.scalar_one_or_none():
            raise ValueError("Email already registered")
        user.email = update_data["email"]
    
    if "password" in update_data:
        password_hash = bcrypt.hashpw(
            update_data["password"].encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
        user.password_hash = password_hash
    
    if "full_name" in update_data:
        user.full_name = update_data["full_name"]
    
    if "role" in update_data:
        user.role = update_data["role"]
    
    if "is_active" in update_data:
        user.is_active = update_data["is_active"]
    
    await db_session.commit()
    await db_session.refresh(user)
    
    return user


async def delete_user(user_id: int, db_session: AsyncSession):
    stmt = select(User).where(User.id == user_id)
    result = await db_session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise ValueError("User not found")
    
    await db_session.delete(user)
    await db_session.commit()
    
    return {"message": "User deleted successfully"}


async def get_all_tickets(skip: int, limit: int, search: str | None, status: str | None, db_session: AsyncSession):
    count_stmt = select(func.count()).select_from(Ticket)
    stmt = select(Ticket).options(
        selectinload(Ticket.client),
        selectinload(Ticket.assigned_to_user)
    )
    
    if search:
        count_stmt = count_stmt.where(Ticket.title.ilike(f"%{search}%"))
        stmt = stmt.where(Ticket.title.ilike(f"%{search}%"))
    
    if status:
        count_stmt = count_stmt.where(Ticket.status == status)
        stmt = stmt.where(Ticket.status == status)
    
    total_result = await db_session.execute(count_stmt)
    total = total_result.scalar()
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db_session.execute(stmt)
    tickets = result.scalars().all()
    
    return {
        "total": total,
        "tickets": tickets
    }


async def get_my_tickets(worker_id: int, skip: int, limit: int, search: str | None, status: str | None, db_session: AsyncSession):
    count_stmt = select(func.count()).select_from(Ticket).where(Ticket.assigned_to_id == worker_id)
    stmt = select(Ticket).options(
        selectinload(Ticket.client),
        selectinload(Ticket.assigned_to_user)
    ).where(Ticket.assigned_to_id == worker_id)
    
    if search:
        count_stmt = count_stmt.where(Ticket.title.ilike(f"%{search}%"))
        stmt = stmt.where(Ticket.title.ilike(f"%{search}%"))
    
    if status:
        count_stmt = count_stmt.where(Ticket.status == status)
        stmt = stmt.where(Ticket.status == status)
    
    total_result = await db_session.execute(count_stmt)
    total = total_result.scalar()
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db_session.execute(stmt)
    tickets = result.scalars().all()
    
    return {
        "total": total,
        "tickets": tickets
    }


async def assign_worker_to_ticket(ticket_id: int, assignment_data, db_session: AsyncSession):
    stmt = select(Ticket).where(Ticket.id == ticket_id)
    result = await db_session.execute(stmt)
    ticket = result.scalar_one_or_none()
    
    if ticket is None:
        raise ValueError("Ticket not found")
    
    if assignment_data.assigned_to_id is not None:
        stmt = select(User).where(User.id == assignment_data.assigned_to_id)
        result = await db_session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user is None:
            raise ValueError("User not found")
        
        if user.role != UserRole.WORKER:
            raise ValueError("Can only assign workers to tickets")
        
        ticket.assigned_to_id = assignment_data.assigned_to_id
    else:
        ticket.assigned_to_id = None
    
    if assignment_data.status is not None:
        ticket.status = assignment_data.status
    
    await db_session.commit()
    await db_session.refresh(ticket)
    
    stmt = (
        select(Ticket)
        .options(
            selectinload(Ticket.client),
            selectinload(Ticket.assigned_to_user)
        )
        .where(Ticket.id == ticket_id)
    )
    result = await db_session.execute(stmt)
    ticket = result.scalar_one()
    
    return ticket


async def unassign_worker_from_ticket(ticket_id: int, db_session: AsyncSession):
    stmt = select(Ticket).where(Ticket.id == ticket_id)
    result = await db_session.execute(stmt)
    ticket = result.scalar_one_or_none()
    
    if ticket is None:
        raise ValueError("Ticket not found")
    
    ticket.assigned_to_id = None
    
    await db_session.commit()
    await db_session.refresh(ticket)
    
    stmt = (
        select(Ticket)
        .options(
            selectinload(Ticket.client),
            selectinload(Ticket.assigned_to_user)
        )
        .where(Ticket.id == ticket_id)
    )
    result = await db_session.execute(stmt)
    ticket = result.scalar_one()
    
    return ticket


async def update_ticket_status(ticket_id: int, status_data, current_user, db_session: AsyncSession):
    stmt = (
        select(Ticket)
        .options(
            selectinload(Ticket.client),
            selectinload(Ticket.assigned_to_user)
        )
        .where(Ticket.id == ticket_id)
    )
    result = await db_session.execute(stmt)
    ticket = result.scalar_one_or_none()
    
    if ticket is None:
        raise ValueError("Ticket not found")
    
    if current_user.role == UserRole.WORKER:
        if ticket.assigned_to_id != current_user.id:
            raise ValueError("You can only update status of your assigned tickets")
    
    ticket.status = status_data.status
    
    await db_session.commit()
    await db_session.refresh(ticket)
    
    stmt = (
        select(Ticket)
        .options(
            selectinload(Ticket.client),
            selectinload(Ticket.assigned_to_user)
        )
        .where(Ticket.id == ticket_id)
    )
    result = await db_session.execute(stmt)
    ticket = result.scalar_one()
    
    return ticket