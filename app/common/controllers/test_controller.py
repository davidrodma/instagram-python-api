

from flask import jsonify
import json
from app.modules.cookie.services.cookie_service import CookieService
from app.modules.profile.models.profile import Profile
from app.common.utilities.json_enconder import JSONEncoder
from app.common.utilities.exception_utility import ExceptionUtility
from app.database.repositories.mongo_repository import MongoRepository

class TestController():
    
   @staticmethod
   def my_test():
      return TestController.test()

   def test():
        try:
            mongo = MongoRepository('profiles',Profile)
            result = mongo.has_custom_set({'countFewMinutes': 0, '$inc': {'countSuccess': 1}})
            print (result)
  
            return jsonify({"success":True,'result':result})
        except BaseException as e:
            return ExceptionUtility.catch_response(e,'Error Test')