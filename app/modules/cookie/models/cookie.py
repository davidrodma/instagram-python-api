# app/models/cookie.py
from app.common.types.id import ID
# app/models/cookie.py
from datetime import datetime

class Cookie:
    def __init__(self, **data):
        self._id:ID = data.get('_id')
        self.username:str = data.get('username')
        self.pk:str = data.get('pk')
        self.state:str = data.get('state')
        self.createdAt:datetime = data.get('createdAt')
        self.updatedAt:datetime = data.get('updatedAt')
