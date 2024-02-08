# app/controllers/profile_controller.py
from flask import jsonify, request
from app.common.controllers.controller import Controller
from app.common.utilities.paginate_utility import PaginateUtility
from app.common.utilities.json_enconder import JSONEncoder
from pydantic import ValidationError
from app.common.dto.status_dto import StatusDto
from app.common.dto.ids_dto import IdsDto
from app.common.utilities.exception_utility import ExceptionUtility
from app.modules.profile.services.profile_service import ProfileService
from app.modules.profile.dto.profile_create_dto import ProfileCreateDto
from app.modules.profile.dto.profile_update_dto import ProfileUpdateDto

class ProfileController(Controller):
    service = ProfileService
    
    @staticmethod
    def paginate():
        try:
            paginated = ProfileService.paginate({}, PaginateUtility.get_request_options())
            return JSONEncoder().encode(paginated)
        except Exception as e:
            return ExceptionUtility.catch_response(e,'Error Paginate')
    
    @staticmethod
    def find_by_id(id):
        try:
            obj = ProfileService.find_by_id(id)
            return JSONEncoder().encode(obj) if obj else (jsonify({'error': 'Record not found'}), 404)
        except BaseException as e:
            return ExceptionUtility.catch_response(e,'Error Get')

    @staticmethod
    def create():
        try:
            dto = ProfileCreateDto(**request.get_json())
            id = ProfileService.create(dto.model_dump())
            return jsonify({'id': id})
        except ValidationError as e:
            return ExceptionUtility.catch_response_validation(e)
        except Exception as e:
             return ExceptionUtility.catch_response(e,'Error Create')
        
    @staticmethod
    def create_many():
        try:
            objects:list = request.get_json()
            dtos = [ProfileCreateDto(**obj).model_dump()  for obj in objects]
            ids = ProfileService.create_many(dtos)
            return JSONEncoder().encode({"ids":ids})
        except ValidationError as e:
            return ExceptionUtility.catch_response_validation(e)
        except Exception as e:
             return ExceptionUtility.catch_response(e,'Error Create')
    
    @staticmethod
    def update_by_id(id):
        try:
            dto = ProfileUpdateDto(_id=id,**request.get_json())
            modified_count = ProfileService.update_by_id(id, dto.model_dump(exclude_unset=True))
            return jsonify({'message': f'{modified_count} records successfully updated!','success': True})
        except ValidationError as e:
            return ExceptionUtility.catch_response_validation(e)
        except Exception as e:
            return ExceptionUtility.catch_response(e,'Error Update')
    
    @staticmethod
    def delete_many_by_ids():
        try:
            dto = IdsDto(**request.get_json())
            deleted_count = ProfileService.delete_many_by_ids(dto.ids)
            return jsonify({'message': f'{deleted_count} records successfully deleted!','success': True})
        except Exception as e:
            return ExceptionUtility.catch_response(e,'Error Delete')
        
    @staticmethod
    def status():
        try:
            dto = StatusDto(**request.get_json())
            modified_count = ProfileService.status(dto.ids, dto.status)
            return jsonify({'message': f'{modified_count} records updated successfully','success': True})
        except Exception as e:
             return ExceptionUtility.catch_response(e,'Error Status')
