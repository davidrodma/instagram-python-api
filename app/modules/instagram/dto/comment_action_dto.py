from pydantic import BaseModel

class CommentActionDto(BaseModel):
    username_action:str
    text:str
    url_target: str = ''
    id_target:str = ''