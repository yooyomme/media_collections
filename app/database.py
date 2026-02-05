from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.config import settings
import os
from app.crud import users
from app.models import User
from app.security import get_password_hash
from app.loggers import debug_logger


engine = create_async_engine(settings.DATABASE_URL)

async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_db():
    async with async_session() as session:
        yield session


async def create_first_superuser():
    email = os.getenv("SUPERUSER_EMAIL")
    password = os.getenv("SUPERUSER_PASSWORD")

    if not email or not password:
        debug_logger.warning("No superuser email and/or password.")
        return None
    async with async_session() as db:
        user_exists = await users.find_user_by_email(db, str(email))
        if user_exists:
            debug_logger.warning(f"User with email {email=} already exists.")
            return None
        try:
            new_superuser = User(
                    email=email,
                    hashed_password=get_password_hash(password),
                    is_active=True,
                    is_admin=True,
                    is_superuser=True,
                )
            db.add(new_superuser)
            await db.commit()
            await db.refresh(new_superuser)
            debug_logger.info(f"Created superuser.")
        except Exception as e:
            debug_logger.error(e)
            pass