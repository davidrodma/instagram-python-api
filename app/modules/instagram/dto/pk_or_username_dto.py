from pydantic import BaseModel

class PkOrUsernameDto(BaseModel):
    pk: str = ''
    id:str = ''
    username: str = ''