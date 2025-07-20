from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SessionOut(BaseModel):
    session_id: str
    user_id: str
    refresh_token: str
    device_info: Optional[str]
    ip_address: Optional[str]
    expires_at: datetime
    created_at: datetime

    class Config:
        orm_mode = True