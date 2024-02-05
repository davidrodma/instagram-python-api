# app/controllers/item_controller.py
from flask import jsonify, request
from app.modules.item.services.item_service import ItemService
from app.common.controllers.controller import Controller
from app.common.utilities.paginate import Paginate
from app.common.utilities.json_enconder import JSONEncoder

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
        data = request.get_json()
        name = data.get('name')
        if name:
            id = ItemService.create(data)
            return jsonify({'id': id})
        return jsonify({'error': 'Invalid data'}), 400

    @staticmethod
    def update_by_id(id):
        data = request.get_json()
        updated = ItemService.update_by_id(id, data)
        if updated:
            return jsonify({'message': 'Item updated successfully'})
        return jsonify({'error': 'Not updated'}), 404

    @staticmethod
    def delete_by_id(id):
        deleted = ItemService.delete_by_id(id)
        if deleted:
            return jsonify({'message': 'Item deleted successfully'})
        return jsonify({'error': 'Item not found'}), 404
    
    @staticmethod
    def status(id):
        data = request.get_json()
        updated = ItemService.status(data.get('ids'), data.get('status'))
        if updated:
            return jsonify({'message': 'Item updated successfully'})
        return jsonify({'error': 'Not updated'}), 404
