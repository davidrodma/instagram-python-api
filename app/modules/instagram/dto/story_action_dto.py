from pydantic import BaseModel

class StoryActionDto(BaseModel):
    username_action:str
    username_target:str = ''
    id_target:str = ''
    media_id:str = ''
    max:int = 10