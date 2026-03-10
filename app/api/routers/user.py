from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.api.schemas.user import UserCreate, UserLogin, UserResponse
from app.core.security import create_access_token
from app.database.models import User
from app.database.session import get_session
from app.services.user import authenticate_user, create_user


router = APIRouter(prefix="/user", tags=["User"])


@router.post("/signup", response_model=UserResponse)
async def signup(user_data: UserCreate, session: AsyncSession = Depends(get_session)):
    user = await create_user(user_data, session)
    return user


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_session)):
    user_data = UserLogin(email=form_data.username, password=form_data.password)
    user = await authenticate_user(user_data, session)
    token = create_access_token({"sub": str(user.id)})
    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user