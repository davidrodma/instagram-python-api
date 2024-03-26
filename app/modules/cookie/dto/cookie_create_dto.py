from app.common.models.model import Model
from datetime import datetime,timezone
from typing import  Optional
from pydantic import BaseModel

class CookieCreateDto(Model):
    username: str
    pk: Optional[str] = ''
    state: str
    createdAt: Optional[datetime] = datetime.now(timezone.utc).replace(tzinfo=None)
    updatedAt: Optional[datetime] = None