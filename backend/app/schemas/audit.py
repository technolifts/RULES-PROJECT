from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AuditLogBase(BaseModel):
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogInDB(AuditLogBase):
    id: int
    user_id: Optional[int] = None
    timestamp: datetime

    class Config:
        orm_mode = True


class AuditLog(AuditLogInDB):
    username: Optional[str] = None
