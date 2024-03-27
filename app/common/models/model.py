from datetime import datetime,timezone
from typing import  Optional
from pydantic import BaseModel

class Model(BaseModel):
    def __init__(self, **data):
        updatedAt = datetime.now(timezone.utc).replace(tzinfo=None)
        super().__init__(updatedAt=updatedAt, **data)

   