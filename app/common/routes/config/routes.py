# app/main.py
from flask import Flask
from app.modules.item.controllers.item_controller import ItemController
from app.common.routes.services.route_service import RouteService

class Routes:
    service = RouteService()
    
    def __init__(self,app:Flask):
        #app.add_url_rule('/login-token-test', 'login_token_test', AuthMiddleware.login_token_test, methods=['POST'])
        self.service.create_default_routes(app,'items',ItemController)