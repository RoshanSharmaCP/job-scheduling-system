from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class JobCreate(BaseModel):
    name: str

class JobUpdate(BaseModel):
    status: str
    result: str = None
    retry_count: int = 0

class JobResponse(BaseModel):
    id: int
    name: str
    status: str
    result: Optional[str] = None
    retry_count: int
    max_retries: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
