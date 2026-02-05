import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app import database
from app.crud.users import get_user_by_email
from app.loggers import user_for_logs_var
from app.models import User
from app.security import verify_access_token

security = HTTPBearer(scheme_name="BearerAuth")


async def get_current_user(db: AsyncSession = Depends(database.get_db), token: HTTPAuthorizationCredentials = Depends(security)) -> User:
    try:
        user_email = verify_access_token(token.credentials)
        user = await get_user_by_email(db, user_email)
        if not user:
            user_for_logs_var.set("anonym user")
        user_for_logs_var.set(user.email)
        return user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


async def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.is_admin or current_user.is_superuser:
        return current_user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


async def get_current_superuser(current_user: User = Depends(get_current_user)):
    if current_user.is_superuser:
        return current_user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)