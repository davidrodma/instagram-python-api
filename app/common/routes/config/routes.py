# app/main.py
from flask import Flask
from app.common.routes.services.route_service import RouteService
from app.common.controllers.test_controller import TestController
from app.modules.item.controllers.item_controller import ItemController
from app.modules.profile.controllers.profile_controller import ProfileController
from app.modules.cookie.controllers.cookie_controller import CookieController
from app.modules.instagram.controllers.instagram_scrape_controller import InstagramScrapeController

class Routes:
    service = RouteService()
    
    def __init__(self,app:Flask):
        #app.add_url_rule('/login-token-test', 'login_token_test', AuthMiddleware.login_token_test, methods=['POST'])

        app.add_url_rule('/my-test', 'my_test', TestController.my_test, methods=['POST'])

        #Items
        self.service.create_default_routes(app,'items',ItemController)

        #Profiles
        app.add_url_rule('/profiles/create-many', 'profiles.create_many', ProfileController.create_many, methods=['POST'])
        self.service.create_default_routes(app,'profiles',ProfileController)

        #Cookies
        self.service.create_default_routes(app,'cookies',CookieController)

        #Instagram
        app.add_url_rule('/instagram/user-info', 'instagram.user_info', InstagramScrapeController.user_info, methods=['GET'])