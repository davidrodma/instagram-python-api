from flask import jsonify, request
from app.common.controllers.controller import Controller
from app.common.utilities.paginate_utility import PaginateUtility
from app.common.utilities.json_enconder import JSONEncoder
from pydantic import ValidationError
from app.common.dto.status_dto import StatusDto
from app.common.dto.ids_dto import IdsDto
from app.common.utilities.exception_utility import ExceptionUtility
from app.modules.worker.services.worker_service import WorkerService
from app.modules.worker.dto.worker_create_dto import WorkerCreateDto
from app.modules.worker.dto.worker_update_dto import WorkerUpdateDto
from app.modules.worker.dto.worker_disable_dto import WorkerDisableDto
from app.modules.config.services.config_service import ConfigService

class WorkerController(Controller):
    service = WorkerService()
    config_service = ConfigService()
    
    @classmethod
    def paginate(self):
        try:
            paginated = self.service.paginate({}, PaginateUtility.get_request_options())
            return JSONEncoder().encode(paginated)
        except Exception as e:
            return ExceptionUtility.catch_response(e,'Error Paginate')
    
    @classmethod
    def find_by_id(self,id):
        try:
            obj = self.service.find_by_id(id)
            return JSONEncoder().encode(obj) if obj else (jsonify({'error': 'Record not found'}), 404)
        except Exception as e:
            return ExceptionUtility.catch_response(e,'Error Get')

    @classmethod
    def create(self):
        try:
            dto = WorkerCreateDto(**request.get_json())
            id = self.service.create(dto.model_dump())
            return jsonify({'id': id})
        except ValidationError as e:
            return ExceptionUtility.catch_response_validation(e)
        except Exception as e:
             return ExceptionUtility.catch_response(e,'Error Create')
        
    @classmethod
    def create_many(self):
        try:
            objects:list = request.get_json()
            dtos = [WorkerCreateDto(**obj).model_dump()  for obj in objects]
            ids = self.service.create_many(dtos)
            return JSONEncoder().encode({"ids":ids})
        except ValidationError as e:
            return ExceptionUtility.catch_response_validation(e)
        except Exception as e:
             return ExceptionUtility.catch_response(e,'Error Create')
    
    @classmethod
    def update_by_id(self,id):
        try:
            dto = WorkerUpdateDto(_id=id,**request.get_json())
            modified_count = self.service.update_by_id(id, dto.model_dump(exclude_unset=True))
            return jsonify({'message': f'{modified_count} records successfully updated!','success': True})
        except ValidationError as e:
            return ExceptionUtility.catch_response_validation(e)
        except Exception as e:
            return ExceptionUtility.catch_response(e,'Error Update')
    
    @classmethod
    def delete_many_by_ids(self):
        try:
            dto = IdsDto(**request.get_json())
            deleted_count = self.service.delete_many_by_ids(dto.ids)
            return jsonify({'message': f'{deleted_count} records successfully deleted!','success': True})
        except Exception as e:
            return ExceptionUtility.catch_response(e,'Error Delete')
        
    @classmethod
    def status(self):
        try:
            dto = StatusDto(**request.get_json())
            modified_count = self.service.status(dto.ids, dto.status)
            return jsonify({'message': f'{modified_count} records updated successfully','success': True})
        except Exception as e:
             return ExceptionUtility.catch_response(e,'Error Status')
    
    @classmethod
    def disable(self):
        try:
            dto = WorkerDisableDto(**request.get_json())
            obj = self.service.disable(dto.username, dto.reason)
            return JSONEncoder().encode(obj) if obj else (jsonify({'error': 'Record not found'}), 404)
        except Exception as e:
             return ExceptionUtility.catch_response(e,'Error disable')
