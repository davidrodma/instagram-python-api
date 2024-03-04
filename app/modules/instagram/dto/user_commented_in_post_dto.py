from pydantic import BaseModel

class UserCommentedInPostDto(BaseModel):
    media_id:str
    username_comment:str
    max:int = 500