from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DocumentBase(BaseModel):
    description: Optional[str] = None

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(DocumentBase):
    pass

class DocumentInDB(DocumentBase):
    id: int
    filename: str
    original_filename: str
    content_type: str
    file_size: int
    file_path: str
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class Document(DocumentInDB):
    pass
