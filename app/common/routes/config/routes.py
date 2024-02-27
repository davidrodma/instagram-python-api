from flask import Flask
from app.common.routes.services.route_service import RouteService
from app.common.controllers.test_controller import TestController
from app.modules.profile.controllers.profile_controller import ProfileController
from app.modules.proxy.controllers.proxy_controller import ProxyController
from app.modules.cookie.controllers.cookie_controller import CookieController
from app.modules.instagram.controllers.instagram_scrape_controller import InstagramScrapeController
from app.modules.config.controllers.config_controller import ConfigController

class Routes:
    service = RouteService()
    
    def __init__(self,app:Flask):
        #app.add_url_rule('/login-token-test', 'login_token_test', AuthMiddleware.login_token_test, methods=['POST'])

        app.add_url_rule('/my-test', 'my_test', TestController.my_test, methods=['POST'])

        #Proxies
        app.add_url_rule('/proxies/create-many', 'proxies.create_many', ProxyController.create_many, methods=['POST'])
        self.service.create_default_routes(app,'proxies',ProxyController)

        #Profiles
        app.add_url_rule('/profiles/create-many', 'profiles.create_many', ProfileController.create_many, methods=['POST'])
        self.service.create_default_routes(app,'profiles',ProfileController)

        #Cookies
        self.service.create_default_routes(app,'cookies',CookieController)

        #Config
        self.service.create_default_routes(app,'config',ConfigController)

        #Instagram
        app.add_url_rule('/instagram/user-info', 'instagram.user_info', InstagramScrapeController.user_info, methods=['GET'])
        app.add_url_rule('/instagram/user-info-by-id', 'instagram.user_info_by_id', InstagramScrapeController.user_info_by_id, methods=['GET'])
        