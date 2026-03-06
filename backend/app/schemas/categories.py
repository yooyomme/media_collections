from pydantic import BaseModel, ConfigDict


class CategoryBaseSchema(BaseModel):
    slug: str


class CategoryInSchema(CategoryBaseSchema):
    title: str


class CategoryResponseSchema(CategoryInSchema):
    id: int

    model_config = ConfigDict(from_attributes=True)