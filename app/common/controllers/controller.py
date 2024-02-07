from abc import ABC, abstractmethod
from typing import Dict,Any
class Controller(ABC):

   # @abstractmethod
   # def mandatory_method(self):
   #    pass

   @staticmethod
   def paginate(self)->Dict[str, Any]:
      pass

   @staticmethod
   def create(self)->Dict[str, Any]:
      pass