# app/models/item.py
from app.common.types.id import ID
# app/models/item.py
from datetime import datetime

class Item:
    def __init__(self, **data):
        self._id:ID = data.get('_id')
        self.name:str = data.get('name')
        self.description:str = data.get('description')
        self.create_at:datetime = data.get('create_at')
        self.status:int = data.get('status')