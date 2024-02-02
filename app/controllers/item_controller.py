# app/controllers/item_controller.py
from flask import jsonify, request
from app.services.item_service import ItemService
import json

from bson.objectid import ObjectId
# Codificador personalizado para converter ObjectId para string
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, object):
            # Convertendo o ObjectId para string
            obj_dict = obj.__dict__.copy()
            if isinstance(obj_dict.get('_id'), ObjectId):
                obj_dict['_id'] = str(obj_dict['_id'])
            return obj_dict
        return super().default(obj)

class ItemController:

    @staticmethod
    def get_all():
        list = ItemService.find_many()
        return JSONEncoder().encode(list)
    
    @staticmethod
    def get(id):
        obj = ItemService.find_by_id(id)
        if obj:
            return JSONEncoder().encode(obj)
        return jsonify({'error': 'Item not found'}), 404

    @staticmethod
    def add():
        data = request.get_json()
        name = data.get('name')
        if name:
            id = ItemService.create(data)
            return jsonify({'id': id})
        return jsonify({'error': 'Invalid data'}), 400

    @staticmethod
    def update(id):
        data = request.get_json()
        updated = ItemService.update_by_id(id, data)
        if updated:
            return jsonify({'message': 'Item updated successfully'})
        return jsonify({'error': 'Not updated'}), 404

    @staticmethod
    def delete(id):
        deleted = ItemService.delete_by_id(id)
        if deleted:
            return jsonify({'message': 'Item deleted successfully'})
        return jsonify({'error': 'Item not found'}), 404
