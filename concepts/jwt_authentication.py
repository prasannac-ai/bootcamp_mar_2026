"""
Concept 4: JWT Authentication with fastapi-users 
===================================================================
Uses fastapi-users to avoid hand-written auth boilerplate while keeping
RBAC demonstration with a role field in the users table.

Run:
    pip install fastapi uvicorn sqlalchemy asyncpg fastapi-users[sqlalchemy]
    uvicorn concepts.04_jwt_authentication:app --reload --port 9004

Test:
    http://localhost:9004/docs
"""

from datetime import datetime
from typing import Literal, Optional
import uuid

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, schemas
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import DateTime, String
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column

import logging

# 1. CONFIGURATION


SECRET_KEY = "my-super-secret-key-change-in-production"
DATABASE_URL = (
    "postgresql+asyncpg://agriadmin:agriadmin123@localhost:5632/agri_db"
)
ACCESS_TOKEN_EXPIRE_SECONDS = 30 * 60
logger = logging.getLogger(__name__)



# 2. DATABASE SETUP + USER MODEL


Base = declarative_base()


class User(SQLAlchemyBaseUserTableUUID, Base):
    """
    Users table from fastapi-users + custom fields.
    Base fields include: id, email, hashed_password, is_active, is_superuser,
    is_verified.
    """

    __tablename__ = "users"

    username = Column(
        String(100), nullable=False, unique=True, index=True
    )
    full_name= Column(String(255), nullable=True)
    role= Column(String(50), nullable=False, default="farmer")
    created_at= Column(DateTime, default=datetime.utcnow)


engine = create_async_engine(DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session():
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)



# 3. SCHEMAS


class UserRead(schemas.BaseUser[uuid.UUID]):
    username: str
    full_name: Optional[str] = None
    role: str
    created_at: datetime


class UserCreate(schemas.BaseUserCreate):
    username: str
    full_name: Optional[str] = None
    role: Literal["farmer", "official", "admin"] = "farmer"


class UserUpdate(schemas.BaseUserUpdate):
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[Literal["farmer", "official", "admin"]] = None



# 4. USER MANAGER + AUTH BACKEND


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET_KEY
    verification_token_secret = SECRET_KEY


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=SECRET_KEY,
        lifetime_seconds=ACCESS_TOKEN_EXPIRE_SECONDS,
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)
current_active_user = fastapi_users.current_user(active=True)



# 5. RBAC DEPENDENCY


def require_roles(*allowed_roles: str):
    allowed_roles_set = set(allowed_roles)

    async def role_checker(
        current_user: User = Depends(current_active_user),
    ) -> User:
    
        if current_user.role not in allowed_roles_set:
        
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Insufficient role. Required: {sorted(allowed_roles_set)}, "
                    f"found: {current_user.role}"
                ),
            )
        logger.info(
            "RBAC allowed: user=%s role=%s",
            current_user.username,
            current_user.role,
        )
        return current_user

    return role_checker



# 6. FASTAPI APPLICATION


app = FastAPI(
    title="JWT + fastapi-users Demo",
    description=(
        "Authentication and Authorization  with fastapi-users and RBAC role "
        "checks."
    ),
    version="2.0.0",
)


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Built-in auth routes from fastapi-users (no custom login/register boilerplate)
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


@app.get("/profile", response_model=UserRead, tags=["rbac-demo"])
async def profile(current_user: User = Depends(current_active_user)):
    return current_user


@app.get("/official", tags=["rbac-demo"])
async def official_panel(
    current_user: User = Depends(require_roles("official", "admin")),
):
    return {
        "message": (
            f"Welcome {current_user.role} {current_user.username}. "
            "You can access official operations."
        )
    }


@app.get("/weather", tags=["rbac-demo"])
async def farmer_weather(
    current_user: User = Depends(require_roles("farmer")),
):
    """
    Farmer-only weather endpoint to demonstrate role-specific access.
    """
    return {
        "message": f"Hello {current_user.username}, weather access granted.",
        "role": current_user.role,
        "forecast": {
            "location": "farm-zone-1",
            "today": "Partly cloudy, 28C",
            "tomorrow": "Light rain expected, 26C",
            "advisory": "Plan irrigation based on rainfall forecast.",
        },
    }


@app.get("/admin", tags=["rbac-demo"])
async def admin_panel(
    current_user: User = Depends(require_roles("admin")),
):
    return {"message": f"Welcome admin {current_user.username}!"}