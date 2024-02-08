from datetime import datetime
from typing import  Optional
from pydantic import BaseModel

class Model(BaseModel):
    def __init__(self, **data):
        updatedAt = datetime.utcnow()
        super().__init__(updatedAt=updatedAt, **data)

   