from datetime import datetime,timezone
from pydantic import BaseModel

class NationalityNameCreateDto(BaseModel):
    romanName: str
    nativeName: str = ''
    gender: str = ''
    nationality: str
    type: str
    createdAt: datetime = datetime.now(timezone.utc).replace(tzinfo=None)
    status: int = 1