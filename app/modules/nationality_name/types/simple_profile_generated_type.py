from typing import Dict
class SimpleProfileGenerated():
    username:str
    password:str
    full_name:str
    birth:dict

    def __init__(self, **data: Dict):
        [setattr(self, key, value) for key, value in data.items()]
    



