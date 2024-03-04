from pydantic import BaseModel

class CommentInLastPostDto(BaseModel):
    username:str
    text:str
    media_id:str = ''
    user_id:str = ''