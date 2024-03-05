from pydantic import BaseModel

class PostsByTagDto(BaseModel):
    tag: str = ''
    max:int = 27
    next_max_id:str = ''
    tab:str = 'recent'