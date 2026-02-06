from typing import Annotated, Optional, List
import uuid
from pydantic import BaseModel, EmailStr, ConfigDict
from sqlalchemy.orm import Mapped


class CategoryBaseSchema(BaseModel):
    slug: str


class CategoryInSchema(CategoryBaseSchema):
    title: str


class CategoryResponseSchema(CategoryInSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)