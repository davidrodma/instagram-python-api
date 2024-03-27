from pydantic import BaseModel

class FollowerActionDto(BaseModel):
    username_action:str
    username_target: str = ''
    id_target:str = ''