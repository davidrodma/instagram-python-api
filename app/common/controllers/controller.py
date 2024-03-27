from abc import ABC, abstractmethod
from typing import Dict,Any
from app.common.types.id import ID
class Controller(ABC):

   # @abstractmethod
   # def mandatory_method(self):
   #    pass

   @classmethod
   def paginate(self)->Dict[str, Any]:
      pass
   
   @classmethod
   def find_by_id(self,id:ID)->Dict[str, Any]:
      pass

   @classmethod
   def create(self)->Dict[str, Any]:
      pass

   @classmethod
   def update_by_id(self,id:ID)->Dict[str, Any]:
      pass

   @classmethod
   def delete_many_by_ids(self)->Dict[str, Any]:
      pass

   @classmethod
   def status(self)->Dict[str, Any]:
      pass