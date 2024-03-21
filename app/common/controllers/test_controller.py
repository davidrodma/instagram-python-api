

from flask import jsonify, request
from app.modules.cookie.services.cookie_service import CookieService
from app.modules.profile.models.profile import Profile
from app.common.utilities.logging_utility import LoggingUtility
from app.common.utilities.exception_utility import ExceptionUtility
from app.common.utilities.cryptography import Cryptography
from app.modules.nationality_name.services.profile_generator_service import ProfileGeneratorService
from datetime import datetime, timezone
logger = LoggingUtility.get_logger("Test")

def aware_utcnow():
    return datetime.now(timezone.utc)

def aware_utcfromtimestamp(timestamp):
    return datetime.fromtimestamp(timestamp, timezone.utc)

def naive_utcnow():
    return aware_utcnow().replace(tzinfo=None)

def naive_utcfromtimestamp(timestamp):
    return aware_utcfromtimestamp(timestamp).replace(tzinfo=None)



class TestController():
    
   @staticmethod
   def my_test():
      return TestController.test()

   def test():
      try:
         encrypt = Cryptography.encrypt("$3123!BR23&*")
         decrypt = Cryptography.decrypt(encrypt)
         return jsonify({'decrypt':decrypt,'encrypt':encrypt})
      except Exception as e:
            message_error = f'ERRO 2: {e}'
            print(message_error)
            ExceptionUtility.print_line_error()
            return ExceptionUtility.catch_response(message_error,'Error Test')
      
        