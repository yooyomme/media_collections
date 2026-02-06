from typing import Annotated, Optional, List
import uuid
from pydantic import BaseModel, EmailStr, ConfigDict
from sqlalchemy.orm import Mapped

class CollectionSchema(BaseModel):
    title: str
    is_public: bool


class CollectionCreateSchema(CollectionSchema):
    description: Optional[str]
    media_items_id: Optional[List[int]]


class CollectionResponseSchema(CollectionSchema):
    description: Optional[str]
    media_items: List["MediaItemResponseSchema"]

    model_config = ConfigDict(from_attributes=True)