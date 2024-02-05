
from app.database.repositories.mongo_repository import MongoRepository

class Repository(MongoRepository):
    
    repository:MongoRepository

    def __init__(self,collection_name:str, model:object):
       self.repository = super()
       self.repository.__init__(collection_name,model)