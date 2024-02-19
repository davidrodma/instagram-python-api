from app.modules.proxy.repositories.proxy_repository import ProxyRepository
from app.modules.proxy.models.proxy import Proxy
from typing import List,Iterable
from app.common.types.paginate_options import PaginateOptions
from app.common.types.id import ID

class ProxyService:

    repository = ProxyRepository()
    
    @classmethod
    def find_many(self,filter = None)->List[Proxy]:
        return self.repository.find_many(filter)
    
    @classmethod
    def find_fist(self, filter:dict)->Proxy:
        return self.repository.find_first(filter)
    
    @classmethod
    def find_by_id(self, id:ID)->Proxy:
        return self.repository.find_by_id(id)
    
    @classmethod
    def create(self, data:Proxy):
        count = self.count()
        data['proxyId'] = str(count+1)
        return self.repository.create(data)
    
    @classmethod
    def create_many(self, data: Iterable[dict]):
        count = self.count()
        data = [{**obj, "proxyId": str(count+i+1)} for i,obj in enumerate(data)]
        return self.repository.create_many(data)
    
    @classmethod
    def update(self,filter:dict, data: dict):
        return self.repository.update(filter,data)

    @classmethod
    def update_by_id(self, id:ID, data: Proxy):
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
    def get_random_proxy(self)->Proxy:
        try:
            obj =  self.repository.get_one_random({"status":1})
            if not obj:
                raise BaseException("no proxy!")
            return obj
        except Exception as e:
             raise BaseException(f'get_random_proxy: {e}')