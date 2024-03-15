from typing import Dict
class NameGenderNationalityGenerated():
    username:str
    full_name:str

    def __init__(self, **data: Dict):
        [setattr(self, key, value) for key, value in data.items()]