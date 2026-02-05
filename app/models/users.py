import uuid
from typing import Optional

from sqlalchemy import CHAR
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from app.models.base import Base

class User(Base):
	__tablename__ = "users"

	id: Mapped[uuid.UUID] = mapped_column(CHAR(36), default=uuid.uuid4, primary_key=True, index=True)
	username: Mapped[Optional[str]] = mapped_column(String(30))
	email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
	hashed_password: Mapped[str] = mapped_column(String(255))

	is_active: Mapped[bool] = mapped_column(default=True)
	is_admin: Mapped[bool] = mapped_column(default=False)
	is_superuser: Mapped[bool] = mapped_column(default=False)