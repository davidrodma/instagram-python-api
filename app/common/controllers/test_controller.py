

from flask import jsonify, request
from app.modules.cookie.services.cookie_service import CookieService
from app.modules.profile.models.profile import Profile
from app.common.utilities.logging_utility import LoggingUtility
from app.common.utilities.exception_utility import ExceptionUtility
from app.database.repositories.mongo_repository import MongoRepository
from app.modules.instagram.utilities.instagram_utility import InstagramUtility
logger = LoggingUtility.get_logger("Test")

class TestController():
    
   @staticmethod
   def my_test():
      return TestController.test()

   def test():
      try:
         results = []
         results.append({'username': "test", 'id': "tideste", 'is_liker': True})
         return jsonify(results)
      except Exception as e:
            message_error = f'ERRO 2: {e}'
            print(message_error)
            return ExceptionUtility.catch_response(message_error,'Error Test')
        