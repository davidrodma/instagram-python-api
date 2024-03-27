# app/main.py
from flask import Blueprint
from app.common.controllers.controller import Controller

class RouteService:
    def create_default_routes(self,bp:Blueprint,module,controller:Controller):
        bp.add_url_rule(f'/{module}', f'{module}_paginate', controller.paginate, methods=['GET'])
        bp.add_url_rule(f'/{module}/<string:id>', f'{module}_find_by_id', controller.find_by_id, methods=['GET'])
        bp.add_url_rule(f'/{module}', f'{module}_create', controller.create, methods=['POST'])
        bp.add_url_rule(f'/{module}/<string:id>', f'{module}_update_by_id', controller.update_by_id, methods=['PUT'])
        bp.add_url_rule(f'/{module}', f'{module}_delete_many_by_ids', controller.delete_many_by_ids, methods=['DELETE'])
        bp.add_url_rule(f'/{module}/status', f'{module}_status', controller.status, methods=['PATCH'])