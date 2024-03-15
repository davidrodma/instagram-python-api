from flask import Flask
from app.common.routes.services.route_service import RouteService
from app.common.controllers.test_controller import TestController
from app.modules.proxy.controllers.proxy_controller import ProxyController
from app.modules.cookie.controllers.cookie_controller import CookieController
from app.modules.config.controllers.config_controller import ConfigController
from app.modules.nationality_name.controllers.nationality_name_controller import NationalityNameController
from app.modules.profile.controllers.profile_controller import ProfileController
from app.modules.worker.controllers.worker_controller import WorkerController
from app.modules.instagram.controllers.instagram_scrape_controller import InstagramScrapeController
from app.modules.instagram.controllers.instagram_profile_controller import InstagramProfileController
from app.modules.instagram.controllers.instagram_worker_controller import InstagramWorkerController

class Routes:
    service = RouteService()
    
    def __init__(self,app:Flask):
        #app.add_url_rule('/login-token-test', 'login_token_test', AuthMiddleware.login_token_test, methods=['POST'])

        app.add_url_rule('/my-test', 'my_test', TestController.my_test, methods=['POST'])

        #Proxies
        app.add_url_rule('/proxies/create-many', 'proxies.create_many', ProxyController.create_many, methods=['POST'])
        self.service.create_default_routes(app,'proxies',ProxyController)

        #Cookies
        self.service.create_default_routes(app,'cookies',CookieController)

        #Config
        self.service.create_default_routes(app,'config',ConfigController)

        #NationalityName
        app.add_url_rule('/nationality-names/generate-name', 'nationality_name.generate_name', NationalityNameController.generate_name, methods=['GET'])
        app.add_url_rule('/nationality-names/generate-simple-profile', 'nationality_names.generate_simple_profile', NationalityNameController.generate_simple_profile, methods=['GET'])
        self.service.create_default_routes(app,'nationality-names',NationalityNameController)

        #Profiles
        app.add_url_rule('/profiles/create-many', 'profiles.create_many', ProfileController.create_many, methods=['POST'])
        self.service.create_default_routes(app,'profiles',ProfileController)

        #Workers
        app.add_url_rule('/workers/create-many', 'workers.create_many', WorkerController.create_many, methods=['POST'])
        self.service.create_default_routes(app,'workers',WorkerController)

        #Instagram - Scrape
        app.add_url_rule('/instagram/scrape/user-info', 'instagram_scrape.user_info', InstagramScrapeController.user_info, methods=['GET'])
        app.add_url_rule('/instagram/scrape/user-info-by-id', 'instagram_scrape.user_info_by_id', InstagramScrapeController.user_info_by_id, methods=['GET'])
        app.add_url_rule('/instagram/scrape/user-recent-posts', 'instagram_scrape.user_recent_posts', InstagramScrapeController.user_recent_posts, methods=['GET'])
        app.add_url_rule('/instagram/scrape/user-last-post', 'instagram_scrape.user_last_post', InstagramScrapeController.user_last_post, methods=['GET'])
        app.add_url_rule('/instagram/scrape/user-info-and-last-post', 'instagram_scrape.user_info_and_last_post', InstagramScrapeController.user_info_and_last_post, methods=['GET'])
        app.add_url_rule('/instagram/scrape/media-url-info', 'instagram_scrape.media_url_info', InstagramScrapeController.media_url_info, methods=['GET'])
        app.add_url_rule('/instagram/scrape/media-id-info', 'instagram_scrape.media_id_info', InstagramScrapeController.media_id_info, methods=['GET'])
        app.add_url_rule('/instagram/scrape/media-id', 'instagram_scrape.media_id', InstagramScrapeController.media_id, methods=['GET'])
        app.add_url_rule('/instagram/scrape/followers', 'instagram_scrape.followers', InstagramScrapeController.followers, methods=['GET'])
        app.add_url_rule('/instagram/scrape/followers-in-profile', 'instagram_scrape.followers_in_profile', InstagramScrapeController.followers_in_profile, methods=['GET'])
        app.add_url_rule('/instagram/scrape/recent-post-likers', 'instagram_scrape.recent_post_likers', InstagramScrapeController.recent_post_likers, methods=['GET'])
        app.add_url_rule('/instagram/scrape/recent-post-likers-by-url', 'instagram_scrape.recent_post_likers_by_url', InstagramScrapeController.recent_post_likers_by_url, methods=['GET'])
        app.add_url_rule('/instagram/scrape/likers-in-post-by-id', 'instagram_scrape.likers_in_post_by_id', InstagramScrapeController.likers_in_post_by_id, methods=['GET'])
        app.add_url_rule('/instagram/scrape/likers-in-post', 'instagram_scrape.likers_in_post', InstagramScrapeController.likers_in_post, methods=['GET'])
        app.add_url_rule('/instagram/scrape/post-comments', 'instagram_scrape.post_comments', InstagramScrapeController.post_comments, methods=['GET'])
        app.add_url_rule('/instagram/scrape/post-comments-by-id', 'instagram_scrape.post_comments_by_id', InstagramScrapeController.post_comments_by_id, methods=['GET'])
        app.add_url_rule('/instagram/scrape/comments-in-post', 'instagram_scrape.comments_in_post', InstagramScrapeController.comments_in_post, methods=['GET'])
        app.add_url_rule('/instagram/scrape/comment-in-last-post', 'instagram_scrape.comment_in_last_post', InstagramScrapeController.comment_in_last_post, methods=['GET'])
        app.add_url_rule('/instagram/scrape/user-commented-in-post', 'instagram_scrape.user_commented_in_post', InstagramScrapeController.user_commented_in_post, methods=['GET'])
        app.add_url_rule('/instagram/scrape/user-recent-stories', 'instagram_scrape.user_recent_stories', InstagramScrapeController.user_recent_stories, methods=['GET'])
        app.add_url_rule('/instagram/scrape/posts-by-tag', 'instagram_scrape.posts_by_tag', InstagramScrapeController.posts_by_tag, methods=['GET'])
        app.add_url_rule('/instagram/scrape/extract-biographies', 'instagram_scrape.extract_biographies', InstagramScrapeController.extract_biographies, methods=['GET'])

        #Instagram - Profile Action
        app.add_url_rule('/instagram/profile/seen-stories-action', 'instagram_profile.seen_stories_action', InstagramProfileController.seen_stories_action, methods=['POST'])

        #Instagram - Worker Action/Edit
        app.add_url_rule('/instagram/worker/follower-action', 'instagram_worker.follower_action', InstagramWorkerController.follower_action, methods=['POST'])
        app.add_url_rule('/instagram/worker/like-action', 'instagram_worker.like_action', InstagramWorkerController.like_action, methods=['POST'])
        app.add_url_rule('/instagram/worker/comment-action', 'instagram_worker.comment_action', InstagramWorkerController.comment_action, methods=['POST'])
        app.add_url_rule('/instagram/worker/story-action', 'instagram_worker.story_action', InstagramWorkerController.story_action, methods=['POST'])
        app.add_url_rule('/instagram/worker/like-comment-action', 'instagram_worker.like_comment_action', InstagramWorkerController.like_comment_action, methods=['POST'])
        app.add_url_rule('/instagram/worker/edit-instagram', 'instagram_worker.edit_instagram', InstagramWorkerController.edit_instagram, methods=['POST'])