
from app.common.types.id import ID
from datetime import datetime

class Config:
    def __init__(self, **data):
        self._id:ID = data.get('_id')
        self.name:str = data.get('name')
        self.title:str = data.get('title')
        self.description:str = data.get('description')
        self.type:str = data.get('type')
        self.value:str = data.get('value')
        self.jsonOptions:str = data.get('jsonOptions')
        self.classAdd:str = data.get('classAdd')
        self.createdAt:datetime = data.get('createdAt')
        self.status:int = data.get('status')
        


