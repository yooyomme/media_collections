import uuid
from typing import Optional, List

from sqlalchemy import CHAR, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String

from app.models.base import Base

class Collection(Base):
    __tablename__ = "collections"

    id: Mapped[uuid.UUID] = mapped_column(CHAR(36), default=uuid.uuid4, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String(250))
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))

    owner: Mapped["User"] = relationship(back_populates="user_collections")
    item_associations: Mapped[List["MediaItemCollection"]] = relationship(back_populates="collection")