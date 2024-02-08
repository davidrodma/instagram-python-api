# app/services/cookie_service.py

from app.modules.cookie.repositories.cookie_repository import CookieRepository
from app.modules.cookie.models.cookie import Cookie
from typing import List,Iterable
from app.common.types.paginate_options import PaginateOptions
from app.common.types.id import ID
class CookieService:

    repository = CookieRepository()
    
    @classmethod
    def find_many(self,filter = None)->List[Cookie]:
        return self.repository.find_many(filter)
    
    @classmethod
    def find_fist(self, filter:dict)->Cookie:
        return self.repository.find_first(filter)
    
    @classmethod
    def find_by_id(self, id:ID)->Cookie:
        return self.repository.find_by_id(id)
    
    @classmethod
    def create(self, data:Cookie):
        return self.repository.create(data)
    
    @classmethod
    def create_many(self, data: Iterable[dict]):
        return self.repository.create_many(data)
    
    @classmethod
    def update(self,filter:dict, data: dict):
        return self.repository.update(filter,data)

    @classmethod
    def update_by_id(self, id:ID, data: Cookie):
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