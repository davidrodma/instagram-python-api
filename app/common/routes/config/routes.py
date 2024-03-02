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
        app.add_url_rule('/instagram/user-recent-posts', 'instagram.user_recent_posts', InstagramScrapeController.user_recent_posts, methods=['GET'])
        app.add_url_rule('/instagram/user-last-post', 'instagram.user_last_post', InstagramScrapeController.user_last_post, methods=['GET'])
        app.add_url_rule('/instagram/user-info-and-last-post', 'instagram.user_info_and_last_post', InstagramScrapeController.user_info_and_last_post, methods=['GET'])
        app.add_url_rule('/instagram/media-url-info', 'instagram.media_url_info', InstagramScrapeController.media_url_info, methods=['GET'])
        app.add_url_rule('/instagram/media-id-info', 'instagram.media_id_info', InstagramScrapeController.media_id_info, methods=['GET'])
        app.add_url_rule('/instagram/media-id', 'instagram.media_id', InstagramScrapeController.media_id, methods=['GET'])
        app.add_url_rule('/instagram/followers', 'instagram.followers', InstagramScrapeController.followers, methods=['GET'])
        app.add_url_rule('/instagram/followers-in-profile', 'instagram.followers_in_profile', InstagramScrapeController.followers_in_profile, methods=['GET'])
        app.add_url_rule('/instagram/recent-post-likers', 'instagram.recent_post_likers', InstagramScrapeController.recent_post_likers, methods=['GET'])
        app.add_url_rule('/instagram/recent-post-likers-by-url', 'instagram.recent_post_likers_by_url', InstagramScrapeController.recent_post_likers_by_url, methods=['GET'])
        app.add_url_rule('/instagram/likers-in-post-by-id', 'instagram.likers_in_post_by_id', InstagramScrapeController.likers_in_post_by_id, methods=['GET'])
        app.add_url_rule('/instagram/likers-in-post', 'instagram.likers_in_post', InstagramScrapeController.likers_in_post, methods=['GET'])
        app.add_url_rule('/instagram/post-comments', 'instagram.post_comments', InstagramScrapeController.post_comments, methods=['GET'])
        app.add_url_rule('/instagram/post-comments-by-id', 'instagram.post_comments_by_id', InstagramScrapeController.post_comments_by_id, methods=['GET'])
        app.add_url_rule('/instagram/comments-in-post', 'instagram.comments_in_post', InstagramScrapeController.comments_in_post, methods=['GET'])