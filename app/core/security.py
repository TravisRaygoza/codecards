from datetime import datetime, timedelta, timezone

from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

import jwt 
from app.config import security_settings

pwd_context = CryptContext(schemes=["bcrypt"])

oauth2_scheme_user = OAuth2PasswordBearer(tokenUrl="/user/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, security_settings.JWT_SECRET_KEY, algorithm=security_settings.JWT_ALGORITHM)

