import uuid
from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey, DateTime, Float, func, UniqueConstraint, CHAR, ForeignKeyConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.models.base import Base


class MediaItemCollection(Base):
    __tablename__ = "media_items_collections"
    collection_id: Mapped[uuid.UUID] = mapped_column(CHAR(36), ForeignKey("collections.id", ondelete="CASCADE"), primary_key=True, index=True)
    media_item_id: Mapped[int] = mapped_column(ForeignKey("media_items.id", ondelete="CASCADE"), primary_key=True, index=True)

    added_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    average_rating: Mapped[float] = mapped_column(Float, default=0.0)
    votes_count: Mapped[int] = mapped_column(default=0)

    collection: Mapped["Collection"] = relationship(back_populates="item_associations")
    media_item: Mapped["MediaItem"] = relationship(back_populates="collection_associations")
    votes: Mapped[List["Vote"]] = relationship(back_populates="collection_associations")


class CollectionMember(Base):
    __tablename__ = "collection_members"

    collection_id: Mapped[uuid.UUID] = mapped_column(CHAR(36), ForeignKey("collections.id", ondelete="CASCADE"), primary_key=True, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    user: Mapped["User"] = relationship("User", back_populates="memberships", lazy="selectin")
    collection: Mapped["Collection"] = relationship("Collection", back_populates="memberships", lazy="selectin")


class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    collection_id: Mapped[uuid.UUID] = mapped_column(CHAR(36), index=True)
    item_id: Mapped[int] = mapped_column()

    score: Mapped[int] = mapped_column(default=1)

    __table_args__ = (
        ForeignKeyConstraint(["collection_id", "item_id"],
                             ["media_items_collections.collection_id", "media_items_collections.media_item_id"],
                             ondelete="CASCADE"),

        UniqueConstraint("user_id",
                         "collection_id",
                         "item_id",
                         name="_user_collection_item_uc"),
    )

    collection_associations: Mapped["MediaItemCollection"] = relationship(back_populates="votes")