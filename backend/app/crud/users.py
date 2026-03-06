import uuid
from typing import Union

from fastapi import HTTPException
from sqlalchemy import Select, Update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app import security
from app.loggers import debug_logger
from app.models import User
from app.schemas.users import UserCreateSchema, UserPermissionsInSchema, UserUpdateSchema


async def get_users(db: AsyncSession):
    try:
        users = await db.execute(Select(User))
        return users.scalars().all()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Users not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID):
    try:
        uid = str(user_id)
        users = await db.execute(Select(User).where(User.id == uid))
        return users.scalar_one()
    except NoResultFound:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_user_by_email(db: AsyncSession, email: str):
    try:
        user = await db.execute(Select(User).where(User.email == email))
        user = user.scalar_one()
        return user
    except NoResultFound:
        return None
    except Exception as e:
        debug_logger.warning(e)
        return None

async def find_user_by_email(db: AsyncSession, email: str):
    try:
        user = await db.execute(Select(User).where(User.email == email))
        if user.scalars().first():
            return True
        else:
            return False
    except NoResultFound:
        return False
    except Exception as e:
        debug_logger.warning(e)
        raise HTTPException(status_code=500, detail=str(e))

async def create_user(db: AsyncSession, user: UserCreateSchema):
    try:
        hashed_password = security.get_password_hash(user.password)
        user = User(email=user.email, hashed_password=hashed_password)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def update_user(db: AsyncSession, user_id: uuid.UUID, data: Union[UserPermissionsInSchema, UserUpdateSchema]):
    try:
        uid = str(user_id)
        existing_user = await db.execute(Select(User).where(User.id == uid))
        user_for_update = existing_user.scalar_one()
        data_for_update = data.model_dump(exclude_unset=True)
        for key, value in data_for_update.items():
            setattr(user_for_update, key, value)
        await db.commit()
        await db.refresh(user_for_update)
        return user_for_update
    except NoResultFound:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        # logs
        raise HTTPException(status_code=500, detail=str(e))


async def delete_user(db: AsyncSession, user_id: uuid.UUID):
    try:
        uid = str(user_id)
        existing_user = await db.execute(Select(User).where(User.id == uid))
        user = existing_user.scalar_one()
        await db.delete(user)
        await db.commit()
        return True
    except Exception as e:
        debug_logger.warning(e)
        raise HTTPException(status_code=500, detail=str(e))


async def change_password(db: AsyncSession):
    pass

async def set_userpic(db: AsyncSession, user_id: uuid.UUID, userpic_url: str):
    try:
        uid = str(user_id)
        existing_user = await db.execute(Select(User).where(User.id == uid))
        user_for_update = existing_user.scalar_one()
        user_for_update.avatar_url = userpic_url
        await db.commit()
        await db.refresh(user_for_update)
        result = await db.execute(Select(User).where(User.id == uid))
        return result.scalar_one()
    except Exception as e:
        debug_logger.warning(e)
        raise HTTPException(status_code=500, detail=str(e))

async def delete_userpic(db: AsyncSession, user_id: uuid.UUID):
    try:
        uid = str(user_id)
        existing_user = await db.execute(Select(User).where(User.id == uid))
        user = existing_user.scalar_one()
        user.avatar_url = None
        await db.commit()
        await db.refresh(user)
        result = await db.execute(Select(User).where(User.id == uid))
        return result.scalar_one()
    except Exception as e:
        debug_logger.warning(e)
        raise HTTPException(status_code=500, detail=str(e))