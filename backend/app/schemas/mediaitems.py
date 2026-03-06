import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator


class MediaItemBaseSchema(BaseModel):
    title_en: str
    category: int


class MediaItemInSchema(MediaItemBaseSchema):
    simkl_id: int
    year: int
    poster: Optional[str]


class MediaItemResponseSchema(MediaItemInSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)


class MediaItemInCollectionResponseSchema(MediaItemInSchema):
    id: int
    added_at: Optional[datetime] = None
    average_rating: Optional[float] = 0.0
    votes_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def merge_assoc_and_item(cls, data):
        if hasattr(data, "media_item"):
            item = data.media_item
            return {
                "id": item.id,
                "simkl_id": item.simkl_id,
                "title_en": item.title_en,
                "year": item.year,
                "poster": item.poster,
                "category": item.category,
                "added_at": data.added_at,
                "average_rating": data.average_rating,
                "votes_count": data.votes_count,
            }
        return data


class MediaItemAddSchema(BaseModel):
    media_type: str
    simkl_id: int


class MediaAddRequestSchema(BaseModel):
    simkl_id: int
    media_type: str
    collection_id: uuid.UUID