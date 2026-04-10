from uuid import UUID

from pydantic import BaseModel


class SendOfferRequest(BaseModel):
    match_id: UUID


class SendTestRequest(BaseModel):
    phone: str
    message: str
