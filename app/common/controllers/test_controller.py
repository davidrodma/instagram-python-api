

from flask import jsonify
import json
from app.modules.cookie.services.cookie_service import CookieService
from app.modules.profile.models.profile import Profile
from app.common.utilities.json_enconder import JSONEncoder
from app.common.utilities.exception_utility import ExceptionUtility
from app.database.repositories.mongo_repository import MongoRepository
from app.modules.instagram.utilities.instagram_utility import InstagramUtility

class TestController():
    
   @staticmethod
   def my_test():
      return TestController.test()

   def test():
      try:
   
         return jsonify({"username":bool({})})
         success = False
         attempts = 3
         while not success:
            try:
               attempts -= 1
               success = True
               print(f"Tentativa {attempts}")
               raise Exception("FORCE WHILE")
            except Exception as err:
               success = False
               message_error = f"ERROR 1: {err}"
               print(message_error)
               if attempts <= 0:
                     raise Exception(message_error)
         return jsonify({"success":True})
      except Exception as e:
            message_error = f'ERRO 2: {e}'
            print(message_error)
            return ExceptionUtility.catch_response(message_error,'Error Test')
        