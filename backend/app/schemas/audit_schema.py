from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class AuditLogBase(BaseModel):
    user_id: Optional[UUID] = None
    table_name: str
    record_id: UUID
    action: str
    old_values: Optional[str] = None
    new_values: Optional[str] = None
    ip_address: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    pass

class AuditLogResponse(AuditLogBase):
    audit_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True