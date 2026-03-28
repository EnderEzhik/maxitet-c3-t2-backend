from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

import jwt
from jwt.exceptions import InvalidTokenError

from sqlmodel.ext.asyncio.session import AsyncSession

from pydantic import ValidationError

from src.access import AccessUser
from src.core.config import settings
from src.core.security import ALGORITHM
from src.database import AsyncSessionMaker
from src.models.user import User
from src.models.token import TokenPayload


SCOPES: dict[str, str] = {
    "items:read:own": "Чтение только своих items",
    "items:write:own": "Создание/изменение/удаление только своих items",
    "items:read:any": "Чтение items у любых пользователей",
    "items:write:any": "Создание/изменение/удаление items у любых пользователей и смена владельца",

    "users:read:own": "Чтение только своих данных",
    "users:write:own": "Создание/изменение/удаление только своих данных",
    "users:read:any": "Чтение данных любых пользователей",
    "users:write:any": "Создание/изменение/удаление данных любых пользователей"
}


async def get_session():
    async with AsyncSessionMaker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/login/access-token", scopes=SCOPES)
TokenDep = Annotated[str, Depends(reusable_oauth2)]


async def get_current_user(
    session: SessionDep,
    token: TokenDep,
    security_scopes: SecurityScopes
) -> AccessUser:
    if security_scopes:
        authenticate_value = f"Bearer scope=\"{security_scopes.scope_str}\""
    else:
        authenticate_value = "Bearer"

    credentials_error = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value}
    )

    try:
        payload = jwt.decode(
            algorithms=ALGORITHM,
            key=settings.SECRET_KEY,
            jwt=token
        )

        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise credentials_error

    if not token_data:
        raise credentials_error

    token_scopes = token_data.scope
    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=401,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value}
            )

    user = await session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return AccessUser(user=user, scopes=token_scopes)


CurrentUser = Annotated[User, Depends(get_current_user)]
