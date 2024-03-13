# app/models/nationality_name.py
from app.common.types.id import ID
# app/models/nationality_name.py
from datetime import datetime

class NationalityName:
    def __init__(self, **data):
        self._id:ID = data.get('_id')
        self.romanName:str = data.get('romanName')
        self.nativeName:str = data.get('nativeName')
        self.nationality:str = data.get('nationality')
        self.type:str = data.get('type')
        self.createdAt:datetime = data.get('createdAt')
        self.status:int = data.get('status')
        


