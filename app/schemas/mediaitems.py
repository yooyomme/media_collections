from typing import Annotated, Optional, List
import uuid
from pydantic import BaseModel, EmailStr, ConfigDict
from sqlalchemy.orm import Mapped


class MediaItemBaseSchema(BaseModel):
    title_en: str
    category: int


class MediaItemInSchema(MediaItemBaseSchema):
    simkl_id: int
    title_original: Optional[str]
    year: int
    poster: Optional[str]
    ep_count: Optional[int]


class MediaItemResponseSchema(MediaItemInSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)