from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

import jwt
from jwt.exceptions import InvalidTokenError

from sqlmodel.ext.asyncio.session import AsyncSession

from pydantic import ValidationError

from src.core.config import settings
from src.core.security import ALGORITHM
from src.database import AsyncSessionMaker
from src.models.user import User
from src.models.token import TokenPayload


async def get_session():
    async with AsyncSessionMaker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/login/access-token")
TokenDep = Annotated[str, Depends(reusable_oauth2)]


async def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            algorithms=ALGORITHM,
            key=settings.SECRET_KEY,
            jwt=token
        )

        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    user = await session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=403, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
