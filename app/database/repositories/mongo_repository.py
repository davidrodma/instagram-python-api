# app/repository/mongo_repository.py
from pymongo import MongoClient
from bson.objectid import ObjectId
from typing import List, cast,Iterable,Union,TypeVar
from dotenv import load_dotenv
import math
import os
from app.common.types.paginate_options import PaginateOptions

load_dotenv()

ID = TypeVar('ID', str, ObjectId)
class MongoRepository:
    
    def __init__(self, collection_name:str, model:object):
        self.client = MongoClient(os.getenv("DATABASE_URL"))
        self.db = self.client[os.getenv("DATABASE_NAME")]
        self.collection = self.db[collection_name]
        self.model = model
    
    def find_many(self,filter:dict=None):
        objects = self.collection.find(filter)
        listParsed =  [self.model(**obj)  for obj in objects]
        return cast(List[self.model],listParsed)
    
    def find_first(self, filter: dict):
        object = self.collection.find_one(filter)
        objParsed = self.model(**object) if object else None
        return cast(self.model,objParsed)
    
    def find_by_id(self,id:ID):
        return self.find_first({'_id': ObjectId(id)})

    def create(self, data: dict):
        result = self.collection.insert_one(data)
        return str(result.inserted_id)
    
    def create_many(self, data: Iterable[dict]):
        result = self.collection.insert_many(data)
        return result.inserted_ids

    def update(self, filter:dict, data: dict):
        update_data = {'$set': data}
        result = self.collection.update_one(filter,update_data)
        return result.modified_count
    
    def update_by_id(self, id:ID, data: dict):
        query = {'_id': ObjectId(id)}
        return self.update(query, data)
    
    def update_many(self,filter:dict, data: dict):
        update_data = {'$set': data}
        result = self.collection.update_many(filter,update_data)
        return result.modified_count
    
    def update_many_by_ids(self, ids:Union[List[ID], ID], data: dict):
        if not isinstance(ids, list):
            ids = [ids]
        ids = [ObjectId(id) for id in ids]
        return self.update_many({
            '_id': {'in': ids}
        },
        data)

    def delete(self, filter:dict):
        result = self.collection.delete_one(filter)
        return result.deleted_count
    
    def delete_by_id(self, id:ID):
        return self.delete({'_id': ObjectId(id)})
    
    def delete_many(self, filter:dict):
        result = self.collection.delete_many(filter)
        return result.deleted_count
    
    def delete_many_by_ids(self, ids:Union[List[ID], ID]):
        if not isinstance(ids, list):
            ids = [ids]
        ids = [ObjectId(id) for id in ids]
        return self.delete_many({
            '_id': {'in': ids}
        })
    
    def count(self, filter:dict = {}):
        count = self.collection.count_documents(filter)
        return count
    
    def status(self, ids:Union[List[ID], ID], status:int):
        return self.update_many_by_ids(ids,{'status':status})
    
    def paginate(self, filter:dict = {}, options:PaginateOptions = {'page':1,'limit':100}):
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
