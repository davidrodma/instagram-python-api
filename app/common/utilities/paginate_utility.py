# app/controllers/item_controller.py
from flask import request
from app.common.types.paginate_options import PaginateOptions

class PaginateUtility:
   
   @staticmethod
   def get_request_options():        
        content = True if request.get_data(as_text=True) else False
        options = PaginateOptions(**request.args) if request.args.get('page') else PaginateOptions(request.get_json() if content else {'page':1,'limit':100})
        return options