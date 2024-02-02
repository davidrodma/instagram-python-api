# app/repository/mongo_repository.py
from pymongo import MongoClient
from bson.objectid import ObjectId
from typing import List, cast
from dotenv import load_dotenv
import os

load_dotenv()

class MongoRepository:
    
    def __init__(self, collection_name:str, model:object):
        self.client = MongoClient(os.getenv("DATABASE_URL"))
        self.db = self.client[os.getenv("DATABASE_NAME")]
        self.collection = self.db[collection_name]
        self.model = model
    
    def find_many(self,filter=None):
        objects = self.collection.find(filter)
        listParsed =  [self.model(**obj)  for obj in objects]
        return cast(List[self.model],listParsed)

    def find_by_id(self,id):
        object = self.collection.find_one({'_id': ObjectId(id)})
        objParsed = self.model(**object) if object else None
        return cast(self.model,objParsed)

    def create(self, data: dict):
        result = self.collection.insert_one(data)
        return str(result.inserted_id)

    def update_by_id(self, id, data: dict):
        query = {'_id': ObjectId(id)}
        update_data = {'$set': data}
        result = self.collection.update_one(query, update_data)
        return result.modified_count > 0

    def delete_by_id(self, id):
        result = self.collection.delete_one({'_id': ObjectId(id)})
        return result.deleted_count > 0
