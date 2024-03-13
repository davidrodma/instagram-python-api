

from flask import jsonify, request
from app.modules.cookie.services.cookie_service import CookieService
from app.modules.profile.models.profile import Profile
from app.common.utilities.logging_utility import LoggingUtility
from app.common.utilities.exception_utility import ExceptionUtility
from app.database.repositories.mongo_repository import MongoRepository
from app.modules.nationality_name.services.profile_generator_service import ProfileGeneratorUtility
logger = LoggingUtility.get_logger("Test")

class TestController():
    
   @staticmethod
   def my_test():
      return TestController.test()

   def test():
      try:
         profile_generator = ProfileGeneratorUtility()
         results = {
            "username":profile_generator.username(),
            "password":profile_generator.password(),
            "name":profile_generator.full_name(),
            "birth":profile_generator.birth(),
         }        
         return jsonify(results)
      except Exception as e:
            message_error = f'ERRO 2: {e}'
            print(message_error)
            return ExceptionUtility.catch_response(message_error,'Error Test')
        