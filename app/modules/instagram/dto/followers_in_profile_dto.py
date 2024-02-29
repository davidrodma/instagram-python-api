from pydantic import BaseModel

class FollowersInProfileDto(BaseModel):
    id_target:str = ''
    username_target: str = ''
    username_action:str = ''
    max:int = 200
    followers_number:int = None
    next_max_id:str =''
    return_image_base64:bool = False