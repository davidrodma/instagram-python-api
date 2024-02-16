

from flask import jsonify
import json
from app.modules.cookie.services.cookie_service import CookieService
from app.common.utilities.json_enconder import JSONEncoder
from app.common.utilities.exception_utility import ExceptionUtility

class TestController():
    
   @staticmethod
   def my_test():
      return TestController.test()

   def test():
        try:
            service = CookieService()
            session = service.load_state('luiza.tanque')
            print('session',session)
            return jsonify({"success":True,'session':session})
        except BaseException as e:
            return ExceptionUtility.catch_response(e,'Error Test')