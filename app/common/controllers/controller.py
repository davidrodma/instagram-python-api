from abc import ABC, abstractmethod
from typing import Dict,Any
from app.common.types.id import ID
class Controller(ABC):

   # @abstractmethod
   # def mandatory_method(self):
   #    pass

   @staticmethod
   def paginate(self)->Dict[str, Any]:
      pass
   
   @staticmethod
   def find_by_id(self,id:ID)->Dict[str, Any]:
      pass

   @staticmethod
   def create(self)->Dict[str, Any]:
      pass

   @staticmethod
   def update_by_id(self,id:ID)->Dict[str, Any]:
      pass

   @staticmethod
   def delete_many_by_ids(self)->Dict[str, Any]:
      pass

   @staticmethod
   def status(self)->Dict[str, Any]:
      pass