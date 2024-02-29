from pydantic import BaseModel

class FollowersListDto(BaseModel):
    pk: str = ''
    id:str = ''
    username: str = ''
    query:str = ''
    max:int = 200
    next_max_id:str =''
    returnWithNextMaxId:bool = False
    return_with_next_max_id:bool = returnWithNextMaxId if returnWithNextMaxId else False
    only_username:bool = False