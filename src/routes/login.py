from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.core.config import settings
from src.core.security import create_access_token
from src.deps import CurrentUser, SessionDep
from src.models.token import Token
from src.models.user import UserOut
from src.repositories import users as users_repo


router = APIRouter(prefix="/login", tags=["login"])


@router.post("/access-token", response_model=Token)
async def login_access_token(session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = await users_repo.authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=create_access_token(user.id, access_token_expires)
    )


@router.post("/test-token", response_model=UserOut)
async def test_token(current_user: CurrentUser):
    return current_user
