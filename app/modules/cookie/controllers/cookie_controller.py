# app/controllers/cookie_controller.py
from flask import jsonify, request
from app.common.controllers.controller import Controller
from app.common.utilities.paginate_utility import PaginateUtility
from app.common.utilities.json_enconder import JSONEncoder
from pydantic import ValidationError
from app.common.dto.status_dto import StatusDto
from app.common.dto.ids_dto import IdsDto
from app.common.utilities.exception_utility import ExceptionUtility
from app.modules.cookie.services.cookie_service import CookieService
from app.modules.cookie.dto.cookie_create_dto import CookieCreateDto
from app.modules.cookie.dto.cookie_update_dto import CookieUpdateDto

class CookieController(Controller):
    service = CookieService()

    @classmethod
    def paginate(self):
        try:
            paginated =self.service.paginate({}, PaginateUtility.get_request_options())
            return JSONEncoder().encode(paginated)
        except Exception as e:
            return ExceptionUtility.catch_response(e,'Error Paginate')
    
    @classmethod
    def find_by_id(self,id):
        try:
            obj =self.service.find_by_id(id)
            return JSONEncoder().encode(obj) if obj else (jsonify({'error': 'Record not found'}), 404)
        except BaseException as e:
            return ExceptionUtility.catch_response(e,'Error Get')

    @classmethod
    def create(self):
        try:
            dto = CookieCreateDto(**request.get_json())
            id =self.service.create(dto.model_dump())
            return jsonify({'id': id})
        except ValidationError as e:
            return ExceptionUtility.catch_response_validation(e)
        except Exception as e:
             return ExceptionUtility.catch_response(e,'Error Create')
    
    @classmethod
    def update_by_id(self,id):
        try:
            dto = CookieUpdateDto(_id=id,**request.get_json())
            modified_count =self.service.update_by_id(id, dto.model_dump(exclude_unset=True))
            return jsonify({'message': f'{modified_count} records successfully updated!','success': True})
        except ValidationError as e:
            return ExceptionUtility.catch_response_validation(e)
        except Exception as e:
            return ExceptionUtility.catch_response(e,'Error Update')
    
    @classmethod
    def delete_many_by_ids(self):
        try:
            dto = IdsDto(**request.get_json())
            deleted_count =self.service.delete_many_by_ids(dto.ids)
            return jsonify({'message': f'{deleted_count} records successfully deleted!','success': True})
        except Exception as e:
            return ExceptionUtility.catch_response(e,'Error Delete')
        
    @classmethod
    def status(self):
        try:
            dto = StatusDto(**request.get_json())
            modified_count =self.service.status(dto.ids, dto.status)
            return jsonify({'message': f'{modified_count} records updated successfully','success': True})
        except Exception as e:
             return ExceptionUtility.catch_response(e,'Error Status')
