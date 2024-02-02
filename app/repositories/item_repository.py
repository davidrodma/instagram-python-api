# app/services/item_service.py
from app.repositories.repository import Repository
from app.models.item import Item
from typing import Type,List, TypeVar, cast

class ItemRepository(Repository):
    
    repository:Repository

    def __init__(self):
       self.repository = super()
       self.repository.__init__('items',Item)