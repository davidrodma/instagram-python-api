from pydantic import BaseModel

class PostListDto(BaseModel):
    id: str = ''
    username: str = ''
    max:int = 60
    next_max_id:str = ''
    returnWithNextMaxId:bool = False
    return_with_next_max_id:bool = returnWithNextMaxId if returnWithNextMaxId else False