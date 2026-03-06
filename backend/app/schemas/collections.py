import uuid, enum
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AccessCollectionTypeSchema(str, enum.Enum):
    PRIVATE = "private"
    PASSWORD = "password"
    LINK = "link"
    LINK_AND_PASSWORD = "link_and_password"


class CollectionSchema(BaseModel):
    title: str = "Коллекция"
    is_public: Optional[bool] = False


class CollectionCreateSchema(CollectionSchema):
    description: Optional[str] = ""
    user_id: uuid.UUID


class CollectionResponseSchema(CollectionSchema):
    id: uuid.UUID
    user_id: uuid.UUID
    description: Optional[str] = ""
    cover_image: Optional[str] = None
    media_items: Optional[List["MediaItemInCollectionResponseSchema"]] = Field(..., alias="item_associations")
    access_type: Optional[str]
    has_password: Optional[bool] = False
    invite_token: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class CollectionSettingsUpdateSchema(BaseModel):
    access_type: Optional["AccessCollectionTypeSchema"] = "private"
    password: Optional[str] = Field(None, max_length=50)

    @field_validator("password")
    @classmethod
    def password_required_if_type_matches(cls, v, info):
        access_type = info.data.get("access_type")
        if access_type in [AccessCollectionTypeSchema.PASSWORD, AccessCollectionTypeSchema.LINK_AND_PASSWORD]:
            if not v:
                raise ValueError("Password is required for this access type")
        return v


class CollectionJoinSchema(BaseModel):
    invite_token: Optional[str] = None
    password: Optional[str] = None


class CollectionMemberResponseSchema(BaseModel):
    collection_id: uuid.UUID
    user_id: uuid.UUID
    joined_at: datetime
    user: "UserShortResponseSchema"