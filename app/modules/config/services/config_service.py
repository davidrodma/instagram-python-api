from app.modules.config.repositories.config_repository import ConfigRepository
from app.modules.config.models.config import Config
from typing import List
from app.common.types.paginate_options import PaginateOptions
from app.common.types.id import ID

class ConfigService:

    repository = ConfigRepository()
    
    @classmethod
    def find_many(self,filter = None)->List[Config]:
        return self.repository.find_many(filter)
    
    @classmethod
    def find_one(self, filter:dict)->Config:
        return self.repository.find_one(filter)
    
    @classmethod
    def find_by_id(self, id:ID)->Config:
        return self.repository.find_by_id(id)
    
    @classmethod
    def create(self, data:Config):
        return self.repository.create(data)
    
    @classmethod
    def update(self,filter:dict, data: dict):
        return self.repository.update(filter,data)
    
    @classmethod
    def find_one_and_update(self,filter:dict, data: dict)->Config:
        return self.repository.find_one_and_update(filter,data)

    @classmethod
    def update_by_id(self, id:ID, data: Config):
        return self.repository.update_by_id(id, data)
    
    @classmethod
    def update_many(self,filter:dict, data: dict):
        return self.update_many(filter,data)
    
    @classmethod
    def update_many_by_ids(self,ids:List[ID], data: dict):
        return self.update_many_by_ids(ids,data)

    @classmethod
    def delete(self, filter: dict):
        return self.repository.delete(filter)
    
    @classmethod
    def delete_by_id(self, id:ID):
        return self.repository.delete_by_id(id)

    @classmethod
    def delete_many_by_ids(self, ids:List[ID]):
        return self.repository.delete_many_by_ids(ids)
    
    @classmethod
    def count(self, filter: dict = {}):
        return self.repository.count(filter)
    
    @classmethod
    def status(self, ids:List[ID], status:int):
        return self.repository.status(ids, status)
    
    @classmethod
    def paginate(self,filter={},options: PaginateOptions = {'page':1,'limit':100}):
        return self.repository.paginate(filter,options)
    
    @classmethod
    def get_by_name(self,name:str)->Config:
        return self.repository.find_one({"name":name})
    
    @classmethod
    def get_config_actived(self,name:str)->Config:
        config:Config = self.repository.find_one({"name":name,"status":1})
        return config if config and config.value else None
    
    @classmethod
    def get_config_value(self,name:str)->Config:
        config:Config = self.get_config_actived(name)
        return config.value if config and config.value else None