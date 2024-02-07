# app/models/item.py
from app.common.types.id import ID
# app/models/item.py
from datetime import datetime

class Item:
    def __init__(self, **data):
        self._id:ID = data.get('_id')
        self.name:str = str(data.get('name'))
        self.description:str = str(data.get('description'))
        create_at:datetime = datetime.strftime(data.get('create_at'),'Y-m-d') if data.get('create_at') else datetime.utcnow()
        self.status:int = int(data.get('status')) if data.get('status') else 1
