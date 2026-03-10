from fastapi import HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.schemas.user import UserCreate, UserLogin
from app.core.security import hash_password, verify_password
from app.database.models import User


async def create_user(user_data: UserCreate, session: AsyncSession):
    # 1. Check if email already exists
    statement = select(User).where(User.email == user_data.email)
    result = await session.execute(statement)
    existing_user = result.scalar_one_or_none()

    # 2. If someone already signed up with this email, stop here
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 3. Hash the password
    hashed = hash_password(user_data.password)

    # 4. Creeate the User object
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed,
    )

    # 5. Save to database 
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    # 6. Return the user 
    return new_user

async def authenticate_user(user_data: UserLogin, session: AsyncSession):
    # 1. Find the user by email 
    statement = select(User).where(User.email == user_data.email)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()  
    
    # 2. Checking if they exist
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # 3. Verify the password 
    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    
    # 4. Return the user 
    return user