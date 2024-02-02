# app/services/item_service.py

from app.repositories.item_repository import ItemRepository
from app.models.item import Item
from typing import List

class ItemService:

    repository = ItemRepository()

    @classmethod
    def find_many(cls,filter = None)->List[Item]:
        return cls.repository.find_many(filter)

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
    def delete_by_id(cls, id:str):
        return cls.repository.delete_by_id(id)
