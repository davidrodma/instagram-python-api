from pydantic import BaseModel

class PostCommentsDto(BaseModel):
  pk:str = ''
  id:str = ''
  url:str = ''
  max:int = 20
  next_max_id:str = ''
  only_text:bool = False