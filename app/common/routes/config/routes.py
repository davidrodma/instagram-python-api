from flask import Flask,Blueprint
from app.common.routes.services.route_service import RouteService
from app.common.controllers.test_controller import TestController
from app.modules.proxy.controllers.proxy_controller import ProxyController
from app.modules.cookie.controllers.cookie_controller import CookieController
from app.modules.config.controllers.config_controller import ConfigController
from app.modules.nationality_name.controllers.nationality_name_controller import NationalityNameController
from app.modules.profile.controllers.profile_controller import ProfileController
from app.modules.worker.controllers.worker_controller import WorkerController
from app.modules.boost.controllers.boost_controller import BoostController
from app.modules.instagram.controllers.instagram_scrape_controller import InstagramScrapeController
from app.modules.instagram.controllers.instagram_profile_controller import InstagramProfileController
from app.modules.instagram.controllers.instagram_worker_controller import InstagramWorkerController
from app.modules.instagram.controllers.instagram_boost_controller import InstagramBoostController

class Routes:
    service = RouteService()
    
    def __init__(self,bp:Blueprint):
        #app.add_url_rule('/login-token-test', 'login_token_test', AuthMiddleware.login_token_test, methods=['POST'])

        bp.add_url_rule('/my-test', 'my_test', TestController.my_test, methods=['POST'])

        #Proxies
        bp.add_url_rule('/proxies/create-many', 'proxies_create_many', ProxyController.create_many, methods=['POST'])
        bp.add_url_rule('/proxies/test-proxy', 'proxies_test_proxy', ProxyController.test_proxy, methods=['GET'])
        self.service.create_default_routes(bp,'proxies',ProxyController)

        #Cookies
        self.service.create_default_routes(bp,'cookies',CookieController)

        #Config
        self.service.create_default_routes(bp,'config',ConfigController)

        #NationalityName
        bp.add_url_rule('/nationality-names/generate-name', 'nationality_names_generate_name', NationalityNameController.generate_name, methods=['GET'])
        bp.add_url_rule('/nationality-names/generate-simple-profile', 'nationality_names_generate_simple_profile', NationalityNameController.generate_simple_profile, methods=['GET'])
        self.service.create_default_routes(bp,'nationality-names',NationalityNameController)

        #Profiles
        bp.add_url_rule('/profiles/create-many', 'profiles_create_many', ProfileController.create_many, methods=['POST'])
        self.service.create_default_routes(bp,'profiles',ProfileController)

        #Workers
        bp.add_url_rule('/workers/create-many', 'workers_create_many', WorkerController.create_many, methods=['POST'])
        bp.add_url_rule('/workers/disable', 'workers_disable', WorkerController.disable, methods=['POST'])
        self.service.create_default_routes(bp,'workers',WorkerController)

        #Boost
        bp.add_url_rule('/boosts/disable', 'boosts_disable', BoostController.disable, methods=['POST'])
        self.service.create_default_routes(bp,'boosts',BoostController)

        #Instagram - Scrape
        bp.add_url_rule('/instagram/scrape/user-info', 'instagram_scrape_user_info', InstagramScrapeController.user_info, methods=['GET'])
        bp.add_url_rule('/instagram/scrape/user-info-by-id', 'instagram_scrape_user_info_by_id', InstagramScrapeController.user_info_by_id, methods=['GET'])
        bp.add_url_rule('/instagram/scrape/user-recent-posts', 'instagram_scrape_user_recent_posts', InstagramScrapeController.user_recent_posts, methods=['GET'])
        bp.add_url_rule('/instagram/scrape/user-last-post', 'instagram_scrape_user_last_post', InstagramScrapeController.user_last_post, methods=['GET'])
        bp.add_url_rule('/instagram/scrape/user-info-and-last-post', 'instagram_scrape_user_info_and_last_post', InstagramScrapeController.user_info_and_last_post, methods=['GET'])
        bp.add_url_rule('/instagram/scrape/media-url-info', 'instagram_scrape_media_url_info', InstagramScrapeController.media_url_info, methods=['GET'])
        bp.add_url_rule('/instagram/scrape/media-id-info', 'instagram_scrape_media_id_info', InstagramScrapeController.media_id_info, methods=['GET'])
        bp.add_url_rule('/instagram/scrape/media-id', 'instagram_scrape_media_id', InstagramScrapeController.media_id, methods=['GET'])
        bp.add_url_rule('/instagram/scrape/followers', 'instagram_scrape_followers', InstagramScrapeController.followers, methods=['GET'])
        bp.add_url_rule('/instagram/scrape/followers-in-profile', 'instagram_scrape_followers_in_profile', InstagramScrapeController.followers_in_profile, methods=['GET'])
        bp.add_url_rule('/instagram/scrape/recent-post-likers', 'instagram_scrape_recent_post_likers', InstagramScrapeController.recent_post_likers, methods=['GET'])
        bp.add_url_rule('/instagram/scrape/recent-post-likers-by-url', 'instagram_scrape_recent_post_likers_by_url', InstagramScrapeController.recent_post_likers_by_url, methods=['GET'])
        bp.add_url_rule('/instagram/scrape/likers-in-post-by-id', 'instagram_scrape_likers_in_post_by_id', InstagramScrapeController.likers_in_post_by_id, methods=['GET'])
        bp.add_url_rule('/instagram/scrape/likers-in-post', 'instagram_scrape_likers_in_post', InstagramScrapeController.likers_in_post, methods=['GET'])
        bp.add_url_rule('/instagram/scrape/post-comments', 'instagram_scrape_post_comments', InstagramScrapeController.post_comments, methods=['GET'])
        bp.add_url_rule('/instagram/scrape/post-comments-by-id', 'instagram_scrape_post_comments_by_id', InstagramScrapeController.post_comments_by_id, methods=['GET'])
        bp.add_url_rule('/instagram/scrape/comments-in-post', 'instagram_scrape_comments_in_post', InstagramScrapeController.comments_in_post, methods=['GET'])
        bp.add_url_rule('/instagram/scrape/comment-in-last-post', 'instagram_scrape_comment_in_last_post', InstagramScrapeController.comment_in_last_post, methods=['GET'])
        bp.add_url_rule('/instagram/scrape/user-commented-in-post', 'instagram_scrape_user_commented_in_post', InstagramScrapeController.user_commented_in_post, methods=['GET'])
        bp.add_url_rule('/instagram/scrape/user-recent-stories', 'instagram_scrape_user_recent_stories', InstagramScrapeController.user_recent_stories, methods=['GET'])
        bp.add_url_rule('/instagram/scrape/posts-by-tag', 'instagram_scrape_posts_by_tag', InstagramScrapeController.posts_by_tag, methods=['GET'])
        bp.add_url_rule('/instagram/scrape/extract-biographies', 'instagram_scrape_extract_biographies', InstagramScrapeController.extract_biographies, methods=['GET'])

        #Instagram - Profile Action
        bp.add_url_rule('/instagram/profile/seen-stories-action', 'instagram_profile_seen_stories_action', InstagramProfileController.seen_stories_action, methods=['POST'])

        #Instagram - Worker Action/Edit
        bp.add_url_rule('/instagram/worker/follower-action', 'instagram_worker_follower_action', InstagramWorkerController.follower_action, methods=['POST'])
        bp.add_url_rule('/instagram/worker/like-action', 'instagram_worker_like_action', InstagramWorkerController.like_action, methods=['POST'])
        bp.add_url_rule('/instagram/worker/comment-action', 'instagram_worker_comment_action', InstagramWorkerController.comment_action, methods=['POST'])
        bp.add_url_rule('/instagram/worker/story-action', 'instagram_worker_story_action', InstagramWorkerController.story_action, methods=['POST'])
        bp.add_url_rule('/instagram/worker/like-comment-action', 'instagram_worker_like_comment_action', InstagramWorkerController.like_comment_action, methods=['POST'])
        bp.add_url_rule('/instagram/worker/edit-instagram', 'instagram_worker_edit_instagram', InstagramWorkerController.edit_instagram, methods=['POST'])
        
        #Instagram - Boost Action/Save with Login
        bp.add_url_rule('/instagram/boost/save', 'instagram_boost_edit_instagram', InstagramBoostController.save, methods=['POST'])
        bp.add_url_rule('/instagram/boost/follower-action', 'instagram_boost_follower_action', InstagramBoostController.follower_action, methods=['POST'])
        bp.add_url_rule('/instagram/boost/like-action', 'instagram_boost_like_action', InstagramBoostController.like_action, methods=['POST'])
        bp.add_url_rule('/instagram/boost/comment-action', 'instagram_boost_comment_action', InstagramBoostController.comment_action, methods=['POST'])
        bp.add_url_rule('/instagram/boost/story-action', 'instagram_boost_story_action', InstagramBoostController.story_action, methods=['POST'])
        bp.add_url_rule('/instagram/boost/like-comment-action', 'instagram_boost_like_comment_action', InstagramBoostController.like_comment_action, methods=['POST'])