# app/main.py
from flask import Flask
from app.common.controllers.controller import Controller
from app.modules.item.controllers.item_controller import ItemController

class Routes:
    def __init__(self,app:Flask):
        self.create_default_routes(app,'items',ItemController)

    def create_default_routes(self,app:Flask,module,controller:Controller):
        app.add_url_rule('/'+module, 'paginate', controller.paginate, methods=['GET'])
        app.add_url_rule('/'+module+'/<string:id>', 'find_by_id', controller.find_by_id, methods=['GET'])
        app.add_url_rule('/'+module+'', 'create', controller.create, methods=['POST'])
        app.add_url_rule('/'+module+'/<string:id>', 'update_by_id', controller.update_by_id, methods=['PUT'])
        app.add_url_rule('/'+module+'/<string:id>', 'delete_by_id', controller.delete_by_id, methods=['DELETE'])
        app.add_url_rule('/'+module+'/status', 'status', controller.status, methods=['PUT'])