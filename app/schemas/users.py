from typing import Annotated, Optional, List
import uuid
from annotated_types import MaxLen, MinLen
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBaseSchema(BaseModel):
    username: Optional[Annotated[str, MaxLen(30)]]
    email: EmailStr


class UserCreateSchema(UserBaseSchema):
    password: str


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str


class UserPermissionsInSchema(BaseModel):
    is_active: bool
    is_admin: bool
    is_superuser: bool


class UserUpdateSchema(BaseModel):
    username: Optional[Annotated[str, MaxLen(30)]]
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class UserResponseSchema(UserBaseSchema):
    id: uuid.UUID
    is_active: bool
    is_admin: bool
    is_superuser: bool

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None