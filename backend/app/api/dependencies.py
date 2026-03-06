import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app import database
from app.crud import collections
from app.crud.users import get_user_by_email
from app.loggers import user_for_logs_var, debug_logger
from app.models import User
from app.security import verify_access_token

security = HTTPBearer(scheme_name="BearerAuth")


async def get_current_user(db: AsyncSession = Depends(database.get_db),
                           token: HTTPAuthorizationCredentials = Depends(security)) -> User:
    try:
        user_email = verify_access_token(token.credentials)
        if not user_email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        user = await get_user_by_email(db, user_email)
        if not user:
            user_for_logs_var.set("anonym user")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        user_for_logs_var.set(user.email)
        return user
    except HTTPException:
        raise
    except Exception as e:
        debug_logger.error(f"Error in get_current_user: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")


async def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.is_admin or current_user.is_superuser:
        return current_user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


async def get_current_superuser(current_user: User = Depends(get_current_user)):
    if current_user.is_superuser:
        return current_user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


async def get_current_collection_member(collection_id: uuid.UUID,
                                        db: AsyncSession = Depends(database.get_db),
                                        current_user: User = Depends(get_current_user)):
    is_member_or_owner = await collections.find_collection_member_or_owner(db, collection_id, current_user)
    if is_member_or_owner:
        return current_user
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)