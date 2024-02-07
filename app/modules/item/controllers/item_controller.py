# app/controllers/item_controller.py
from flask import jsonify, request
from app.common.controllers.controller import Controller
from app.common.utilities.paginate_utility import PaginateUtility
from app.common.utilities.json_enconder import JSONEncoder
from pydantic import ValidationError
from app.common.dto.status_dto import StatusDto
from app.common.dto.ids_dto import IdsDto
from app.common.utilities.exception_utility import ExceptionUtility
from app.modules.item.services.item_service import ItemService
from app.modules.item.dto.item_create_dto import ItemCreateDto
from app.modules.item.dto.item_update_dto import ItemUpdateDto

class ItemController(Controller):
    service = ItemService
    @staticmethod
    def paginate():
        try:
            paginated = ItemService.paginate({}, PaginateUtility.get_request_options())
            return JSONEncoder().encode(paginated)
        except Exception as e:
            return ExceptionUtility.catch_response(e,'Error Paginate')
    
    @staticmethod
    def find_by_id(id):
        try:
            obj = ItemService.find_by_id(id)
            return JSONEncoder().encode(obj) if obj else (jsonify({'error': 'Item not found'}), 404)
        except BaseException as e:
            return ExceptionUtility.catch_response(e,'Error Get')

    @staticmethod
    def create():
        try:
            dto = ItemCreateDto(**request.get_json())
            id = ItemService.create(dto.model_dump())
            return jsonify({'id': id})
        except ValidationError as e:
            return ExceptionUtility.catch_response_validation(e)
        except Exception as e:
             return ExceptionUtility.catch_response(e,'Error Create')
    
    @staticmethod
    def update_by_id(id):
        try:
            dto = ItemUpdateDto(_id=id,**request.get_json())
            modified_count = ItemService.update_by_id(id, dto.model_dump(exclude_unset=True))
            return jsonify({'message': f'{modified_count} items successfully updated!','success': True})
        except ValidationError as e:
            return ExceptionUtility.catch_response_validation(e)
        except Exception as e:
            return ExceptionUtility.catch_response(e,'Error Update')
    
    @staticmethod
    def delete_many_by_ids():
        try:
            dto = IdsDto(**request.get_json())
            deleted_count = ItemService.delete_many_by_ids(dto.ids)
            return jsonify({'message': f'{deleted_count} items successfully deleted!','success': True})
        except Exception as e:
            return ExceptionUtility.catch_response(e,'Error Delete')
        
    @staticmethod
    def status():
        try:
            dto = StatusDto(**request.get_json())
            modified_count = ItemService.status(dto.ids, dto.status)
            return jsonify({'message': 'Item updated successfully','modified_count': modified_count})
        except Exception as e:
             return ExceptionUtility.catch_response(e,'Error Status')
