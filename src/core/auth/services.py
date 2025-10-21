import os
import jwt
import bcrypt
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.models import User


SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))


async def register_user(user_data, db_session: AsyncSession):
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
        is_active=True
    )
    
    db_session.add(db_user)
    await db_session.commit()
    await db_session.refresh(db_user)
    
    return db_user


async def authenticate_user(login_data, db_session: AsyncSession):
    stmt = select(User).where(
        (User.username == login_data.username) | (User.email == login_data.username)
    )
    result = await db_session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None or not bcrypt.checkpw(
        login_data.password.encode('utf-8'),
        user.password_hash.encode('utf-8')
    ):
        raise ValueError("Invalid credentials")
    
    if not user.is_active:
        raise ValueError("User account is inactive")
    
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "role": user.role.value
    }


async def refresh_access_token(refresh_token_str: str, db_session: AsyncSession):
    try:
        payload = jwt.decode(refresh_token_str, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ValueError("Refresh token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid refresh token")
    
    user_id = payload.get("sub")
    if user_id is None:
        raise ValueError("Invalid refresh token")
    
    stmt = select(User).where(User.id == int(user_id))
    result = await db_session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None or not user.is_active:
        raise ValueError("User not found or inactive")
    
    access_token = create_access_token(data={"sub": str(user_id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload


async def get_current_user(token: str, db_session: AsyncSession):
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise ValueError("Invalid token")
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
    
    stmt = select(User).where(User.id == int(user_id))
    result = await db_session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise ValueError("User not found")
    
    return user