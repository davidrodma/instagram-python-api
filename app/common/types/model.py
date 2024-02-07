from pydantic import BaseModel,Field
from typing import  Optional

class Model(BaseModel):
    id: Optional[str] = Field(alias='_id')

    def __init__(self, **data):
        _id = str(data.pop('_id')) if data.get('_id') else None
        super().__init__(_id=_id, **data)

   