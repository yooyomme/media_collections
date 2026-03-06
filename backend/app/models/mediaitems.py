from typing import Optional, List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class MediaItem(Base):
    __tablename__ = "media_items"

    id: Mapped[int] = mapped_column(primary_key=True, unique=True, index=True)
    simkl_id: Mapped[int] = mapped_column(unique=True, index=True)
    category: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    title_en: Mapped[str] = mapped_column(String(250))
    year: Mapped[int] = mapped_column()
    poster: Mapped[Optional[str]] = mapped_column(String(150))

    item_category: Mapped["Category"] = relationship(back_populates="items")
    collection_associations: Mapped[List["MediaItemCollection"]] = relationship(back_populates="media_item", passive_deletes=True, lazy="selectin")
