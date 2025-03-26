from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ShareLinkBase(BaseModel):
    document_id: int
    expires_at: Optional[datetime] = None

class ShareLinkCreate(ShareLinkBase):
    pass

class ShareLinkInDB(ShareLinkBase):
    id: int
    token: str
    created_by: int
    created_at: datetime
    is_active: bool

    class Config:
        orm_mode = True

class ShareLink(ShareLinkInDB):
    pass

class SharedDocumentInfo(BaseModel):
    id: int
    original_filename: str
    content_type: str
    description: Optional[str] = None
    shared_by: str
    created_at: datetime

    class Config:
        orm_mode = True
