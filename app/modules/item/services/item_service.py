# app/services/item_service.py

from app.modules.item.repositories.item_repository import ItemRepository
from app.modules.item.models.item import Item
from typing import List
from app.common.types.paginate_options import PaginateOptions
class ItemService:

    repository = ItemRepository()

    @classmethod
    def find_many(cls,filter = None)->List[Item]:
        return cls.repository.find_many(filter)
    
    @classmethod
    def paginate(cls,filter={},options: PaginateOptions = {'page':1,'limit':100}):
        return cls.repository.paginate(filter,options)

    @classmethod
    def find_by_id(cls, id)->Item:
        return cls.repository.find_by_id(id)

    @classmethod
    def create(cls, data:Item):
        return cls.repository.create(data)

    @classmethod
    def update_by_id(cls, id:str, data: Item):
        return cls.repository.update_by_id(id, data)
    
    @classmethod
    def status(cls, ids:List, status:int):
        return cls.repository.status(ids, status)

    @classmethod
    def delete_by_id(cls, id:str):
        return cls.repository.delete_by_id(id)
