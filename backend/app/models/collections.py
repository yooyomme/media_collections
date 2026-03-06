import uuid, enum
from typing import Optional, List

from sqlalchemy import CHAR, ForeignKey, Boolean, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class AccessCollectionType(str, enum.Enum):
    PRIVATE = "private"
    PASSWORD = "password"
    LINK = "link"
    LINK_AND_PASSWORD = "link_and_password"

class Collection(Base):
    __tablename__ = "collections"

    id: Mapped[uuid.UUID] = mapped_column(CHAR(36), default=uuid.uuid4, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), default="Коллекция")
    description: Mapped[Optional[str]] = mapped_column(String(250))
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    cover_image: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    owner: Mapped["User"] = relationship(back_populates="user_collections", passive_deletes=True)

    access_type: Mapped["AccessCollectionType"] = mapped_column(Enum(AccessCollectionType), default=AccessCollectionType.PRIVATE)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255))
    invite_token: Mapped[Optional[str]] = mapped_column(String(64), index=True, default=uuid.uuid4)

    memberships: Mapped[list["CollectionMember"]] = relationship("CollectionMember", back_populates="collection",cascade="all, delete-orphan")
    item_associations: Mapped[List["MediaItemCollection"]] = relationship(back_populates="collection", passive_deletes=True)
    media_items: Mapped[List["MediaItem"]] = relationship(
        secondary="media_items_collections",
        viewonly=True,
    )

    @property
    def has_password(self) -> bool:
        return bool(self.password_hash)