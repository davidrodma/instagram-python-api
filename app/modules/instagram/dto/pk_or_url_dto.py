from pydantic import BaseModel

class PkOrUrlDto(BaseModel):
    pk: str = ''
    id:str = ''
    url: str = ''