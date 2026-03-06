import uuid
from pydantic import BaseModel, ConfigDict, Field


class VoteBaseSchema(BaseModel):
    collection_id: uuid.UUID
    item_id: int

class VoteCreateSchema(VoteBaseSchema):
    score: int = Field(..., ge=1, le=5)

class VoteResponseSchema(VoteBaseSchema):
    id: int
    user_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)

class VoteExtendedResponseSchema(VoteBaseSchema):
    user_rate: int
    average_rating: float
    votes_count: int

    model_config = ConfigDict(from_attributes=True)