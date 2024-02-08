from datetime import datetime
from .cookie_create_dto import CookieCreateDto
from typing import  Optional

class CookieUpdateDto(CookieCreateDto):
    username: Optional[str] = None
    updatedAt:datetime = datetime.utcnow()
  
