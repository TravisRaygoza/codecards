from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
import jwt

from app.core.security import oauth2_scheme_user
from app.config import security_settings
from app.database.session import get_session
from app.database.models import User


async def get_current_user(
    token: str = Depends(oauth2_scheme_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        payload = jwt.decode(
            token,
            security_settings.JWT_SECRET_KEY,
            algorithms=[security_settings.JWT_ALGORITHM],
        )
        user_id = payload["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user 


    