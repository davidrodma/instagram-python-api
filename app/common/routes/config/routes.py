# app/main.py
from flask import Flask
from app.modules.item.controllers.item_controller import ItemController
from app.modules.profile.controllers.profile_controller import ProfileController
from app.modules.cookie.controllers.cookie_controller import CookieController
from app.common.routes.services.route_service import RouteService

class Routes:
    service = RouteService()
    
    def __init__(self,app:Flask):
        #app.add_url_rule('/login-token-test', 'login_token_test', AuthMiddleware.login_token_test, methods=['POST'])

        #Items
        self.service.create_default_routes(app,'items',ItemController)

        #Profiles
        app.add_url_rule('/profiles/create-many', 'profiles.create_many', ProfileController.create_many, methods=['POST'])
        self.service.create_default_routes(app,'profiles',ProfileController)

        #Cookies
        self.service.create_default_routes(app,'cookies',CookieController)