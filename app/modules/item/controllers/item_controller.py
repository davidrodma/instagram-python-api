# app/controllers/item_controller.py
from flask import jsonify, request
from app.modules.item.services.item_service import ItemService
from app.common.controllers.controller import Controller
from app.common.utilities.paginate import Paginate
from app.common.utilities.json_enconder import JSONEncoder
from pydantic import ValidationError
from app.modules.item.models.item import Item
from app.common.dto.status_dto import StatusDto

class ItemController(Controller):
    
    @staticmethod
    def paginate():
        paginated = ItemService.paginate({}, Paginate.get_request_options())
        return JSONEncoder().encode(paginated)
    
    @staticmethod
    def find_by_id(id):
        obj = ItemService.find_by_id(id)
        if obj:
            return JSONEncoder().encode(obj)
        return jsonify({'error': 'Item not found'}), 404

    @staticmethod
    def create():
        try:
            dto = Item(**request.get_json())
        except ValidationError as e:
            return jsonify({'error': f"Error validation {e}"}), 403
    
        try:
            id = ItemService.create(dto.model_dump())
            return jsonify({'id': id})
        except Exception as e:
            return jsonify({'error': f"Error Create {e}"}), 400
    
    @staticmethod
    def update_by_id(id):
        try:
            dto = Item(_id=id,**request.get_json())
        except ValidationError as e:
            return jsonify({'error': f"Error validation {e}"}), 403
    
        try:
            modified_count = ItemService.update_by_id(id, dto.model_dump(exclude_unset=True))
            return jsonify({'message': 'Item updated successfully','modified_count':modified_count})
        except Exception as e:
            return jsonify({'error': f"Error Edit {e}"}), 400
    

    @staticmethod
    def delete_by_id(id):
        deleted_count = ItemService.delete_by_id(id)
        if deleted_count:
            return jsonify({'message': 'Item deleted successfully'})
        return jsonify({'error': 'Item not found'}), 404
    
    @staticmethod
    def status():
        try:
            dto = StatusDto(**request.get_json())
        except ValidationError as e:
            return jsonify({'error': f"Error validation {e}"}), 403
        
        try:
            modified_count = ItemService.status(dto.ids, dto.status)
            return jsonify({'message': 'Item updated successfully','modified_count': modified_count})
        except Exception as e:
            return jsonify({'error': f"Error Edit {e}"}), 400
