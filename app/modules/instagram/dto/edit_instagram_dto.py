from pydantic import BaseModel
from typing import Literal

class EditInstagramDto(BaseModel):
    username:str
    password:str
    new_username:str = ''
    new_password:str = ''
    nationality:str = ''
    gender:str = ''
    first_name:str = ''
    biography:str = ''
    visibility:Literal['public', 'private', ''] ='',
    album:str = ''
    filename:str = ''
    posts_album:str = ''
    posts_quantity:int = 0
    email:str = ''
    external_url:str = ''
    phone_number:str = ''
    proxy:str = ''
    session_id:str = ''