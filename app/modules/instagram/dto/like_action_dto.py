from pydantic import BaseModel

class LikeActionDto(BaseModel):
    username_action:str
    url_target: str = ''
    id_target:str = ''