# app/repository/mongo_repository.py
from pymongo import MongoClient
from bson.objectid import ObjectId
from typing import List, cast,Iterable,Union
from dotenv import load_dotenv
import math
import os
from app.common.types.paginate_options import PaginateOptions
from app.common.types.id import ID
import random

load_dotenv()
class MongoRepository:
    
    def __init__(self, collection_name:str, model:object):
        try:
            self.client = MongoClient(os.getenv("DATABASE_URL"))
            self.db = self.client[os.getenv("DATABASE_NAME")]
            self.collection = self.db[collection_name]
            self.model = model
        except Exception as e:
            raise BaseException(f'MongoRepository.__init__: {e}')
    
    def get_collection(self):
         return self.collection
    
    def find_many(self,filter:dict=None):
        try:
            objects = self.collection.find(filter)
            listParsed =  [self.model(**obj)  for obj in objects]
            return cast(List[self.model],listParsed)
        except Exception as e:
            raise BaseException(f'find_many: {e}')

    def find_first(self, filter: dict):
        try:
            object = self.collection.find_one(filter)
            objParsed = self.model(**object) if object else None
            return cast(self.model,objParsed)
        except Exception as e:
            raise BaseException(f'find_first: {e}')
    
    def find_by_id(self,id:ID):
        try:
            return self.find_first({'_id': ObjectId(id)})
        except Exception as e:
            raise BaseException(f"find: {e}")

    def create(self, data: dict):
        try:
            result = self.collection.insert_one(data)
            return str(result.inserted_id)
        except Exception as e:
            raise BaseException(f'create: {e}')
    
    def create_many(self, data: Iterable[dict]):
        try:
            result = self.collection.insert_many(data)
            return result.inserted_ids
        except Exception as e:
            raise BaseException(f'create_many: {e}')

    def update(self, filter:dict, data: dict):
        try:
            update_data = {'$set': data}
            result = self.collection.update_one(filter,update_data)
            return result.modified_count
        except Exception as e:
            raise BaseException(f'update: {e}')
    
    def update_by_id(self, id:ID, data: dict):
        try:
            query = {'_id': ObjectId(id)}
            return self.update(query, data)
        except Exception as e:
            raise BaseException(f'update_by_id: {e}')
    
    def update_many(self,filter:dict, data: dict):
        try:
            update_data = {'$set': data}
            result = self.collection.update_many(filter,update_data)
            return result.modified_count
        except Exception as e:
            raise BaseException(f'update_many: {e}')
    
    def update_many_by_ids(self, ids:Union[List[ID], ID], data: dict):
        try:
            if not isinstance(ids, list):
                ids = [ids]
            ids = [ObjectId(id) for id in ids]
            return self.update_many({
                '_id': {'$in': ids}
            },
            data)
        except Exception as e:
            raise BaseException(f'update_many_by_ids: {e}')

    def delete(self, filter:dict):
        try:
            result = self.collection.delete_one(filter)
            return result.deleted_count
        except Exception as e:
            raise BaseException(f'delete: {e}')
    
    def delete_by_id(self, id:ID):
        try:
            return self.delete({'_id': ObjectId(id)})
        except Exception as e:
            raise BaseException(f'delete_by_id: {e}')
    
    def delete_many(self, filter:dict):
        try:
            result = self.collection.delete_many(filter)
            return result.deleted_count
        except Exception as e:
            raise BaseException(f'delete_many: {e}')
    
    def delete_many_by_ids(self, ids:Union[List[ID], ID]):
        try:
            if not isinstance(ids, list):
                ids = [ids]
            ids = [ObjectId(id) for id in ids]
            return self.delete_many({
                '_id': {'$in': ids}
            })
        except Exception as e:
            raise BaseException(f'delete_many_by_ids: {e}')
    
    def count(self, filter:dict = {}):
        try:
            count = self.collection.count_documents(filter)
            return count
        except Exception as e:
            raise BaseException(f'count: {e}')
    
    def status(self, ids:Union[List[ID], ID], status:int):
        try:
            return self.update_many_by_ids(ids,{'status':status})
        except Exception as e:
            raise BaseException(f'status: {e}')
    
    def paginate(self, filter:dict = {}, options:PaginateOptions = {'page':1,'limit':100}):
        try:
            page, limit = int(options.get('page')), int(options.get('limit'))
            offset = (page - 1) * limit
            objects = self.collection.find(filter).skip(offset).limit(limit)
            listParsed =  [self.model(**obj)  for obj in objects]
            total = self.count(filter)
            pages =  math.ceil(total / limit)
            return {
                'total':total,
                'page':page,
                'pages':pages,
                'limit':limit,
                'list':listParsed,
            }
        except Exception as e:
            raise BaseException(f'paginate: {e}')
        
    def get_one_random(self,filter:dict = {}):
        try:
            count = self.count(filter)
            if not count:
                return None
            random_number = random.randint(0, count - 1)
            objects = self.collection.find(filter).skip(random_number).limit(1)
            return cast(self.model,self.model(**objects[0])) if objects[0] else None 
        except Exception as e:
            raise BaseException(f'get_one_random: {e}')
