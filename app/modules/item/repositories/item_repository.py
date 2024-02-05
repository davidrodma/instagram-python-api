# app/services/item_service.py
from app.database.repositories.repository import Repository
from app.modules.item.models.item import Item

class ItemRepository(Repository):
    
    repository:Repository

    def __init__(self):
       self.repository = super()
       self.repository.__init__('items',Item)