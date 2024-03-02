from flask import request
from app.common.controllers.controller import Controller
from app.common.utilities.exception_utility import ExceptionUtility
from app.modules.instagram.dto.username_dto import UsernameDto
from app.modules.instagram.services.instagram_service import InstagramService
from app.modules.instagram.dto.username_dto import UsernameDto
from app.modules.instagram.dto.id_dto import IdDto
from app.modules.instagram.dto.url_dto import UrlDto
from app.modules.instagram.dto.post_list_dto import PostListDto
from app.modules.instagram.dto.pk_or_username_dto import PkOrUsernameDto
from app.modules.instagram.dto.followers_list_dto import FollowersListDto
from app.modules.instagram.dto.followers_in_profile_dto import FollowersInProfileDto
from app.modules.instagram.dto.pk_or_url_dto import PkOrUrlDto
from app.modules.instagram.dto.likers_in_post_by_id_dto import LikersInPostByIdDto
from app.modules.instagram.dto.likers_in_post_dto import LikersInPostDto
from app.modules.instagram.dto.post_comments_dto import PostCommentsDto
from app.modules.instagram.dto.comments_in_post_dto import CommentsInPostDto
from app.common.utilities.json_enconder import JSONEncoder

class InstagramScrapeController(Controller):
    service = InstagramService()

    @classmethod
    async def user_info(self):
        try:
            dto = UsernameDto(**request.get_json())
            info = await self.service.user_info_by_username(dto.username)
            return JSONEncoder().encode(info)
        except Exception as e:
            return ExceptionUtility.catch_response(e,f'Error user_info')
    
    @classmethod
    async def user_info_by_id(self):
        try:
            dto = IdDto(**request.get_json())
            info = await self.service.user_info_by_id(dto.id)
            return JSONEncoder().encode(info)
        except Exception as e:
            return ExceptionUtility.catch_response(e,f'Error Get user_info_by_id')
        
    @classmethod
    async def media_id_info(self):
        try:
            dto = IdDto(**request.get_json())
            info = await self.service.media_id_info(dto.id)
            return JSONEncoder().encode(info)
        except Exception as e:
            return ExceptionUtility.catch_response(e,f'ctrl.media_id_info')
    
    @classmethod
    async def media_url_info(self):
        try:
            dto = UrlDto(**request.get_json())
            info = await self.service.media_url_info(dto.url)
            return JSONEncoder().encode(info)
        except Exception as e:
            return ExceptionUtility.catch_response(e,f'ctrl.media_url_info')
   
    @classmethod
    async def media_id(self):
        try:
            dto = UrlDto(**request.get_json())
            pk = await self.service.media_id(dto.url)
            return JSONEncoder().encode({"pk":pk})
        except Exception as e:
            return ExceptionUtility.catch_response(e,f'ctrl.media_id')
    
    @classmethod
    async def user_recent_posts(self):
        try:
            dto = PostListDto(**request.get_json())
            obj_posts = await self.service.user_recent_posts(
                username=dto.username,
                max=dto.max,
                pk=dto.id,
                return_with_next_max_id = dto.returnWithNextMaxId or dto.return_with_next_max_id,
                next_max_id=dto.next_max_id
            )
            return JSONEncoder().encode(obj_posts)
        except Exception as e:
            return ExceptionUtility.catch_response(e,f'ctrl.user_recent_posts')
        
    @classmethod
    async def user_last_post(self):
        try:
            dto = PkOrUsernameDto(**request.get_json())
            obj_posts = await self.service.user_last_post(
                username=dto.username,
                pk=dto.pk or dto.id,
            )
            return JSONEncoder().encode(obj_posts)
        except Exception as e:
            return ExceptionUtility.catch_response(e,f'ctrl.user_recent_posts')
    
    @classmethod
    async def user_info_and_last_post(self):
        try:
            dto = PkOrUsernameDto(**request.get_json())
            obj_posts = await self.service.user_info_and_last_post(
                username=dto.username,
                pk=dto.pk or dto.id,
            )
            return JSONEncoder().encode(obj_posts)
        except Exception as e:
            return ExceptionUtility.catch_response(e,f'ctrl.user_info_and_last_post')
        
    @classmethod
    async def followers(self):
        try:
            dto = FollowersListDto(**request.get_json())
            result = await self.service.followers(
                username=dto.username,
                pk=dto.pk or dto.id,
                query=dto.query,
                max=dto.max,
                next_max_id=dto.next_max_id,
                return_with_next_max_id = dto.returnWithNextMaxId or dto.return_with_next_max_id,
                only_username = dto.only_username
            )
            return JSONEncoder().encode(result)
        except Exception as e:
            return ExceptionUtility.catch_response(e,f'ctrl.followers')
        
    @classmethod
    async def followers_in_profile(self):
        try:
            dto = FollowersInProfileDto(**request.get_json())
            result = await self.service.followers_in_profile(
                username_target=dto.username_target,
                id_target=dto.id_target,
                max=dto.max,
                username_action=dto.username_action,
                followers_number=dto.followers_number,
                return_image_base64 = dto.return_image_base64,
            )
            return JSONEncoder().encode(result)
        except Exception as e:
            return ExceptionUtility.catch_response(e,f'ctrl.followers_in_profile')
        
    @classmethod
    async def recent_post_likers(self):
        try:
            dto = PkOrUrlDto(**request.get_json())
            result = await self.service.recent_post_likers(
                pk=dto.id or dto.pk,
                url=dto.url
            )
            return JSONEncoder().encode(result)
        except Exception as e:
            return ExceptionUtility.catch_response(e,f'ctrl.recent_post_likers')
    
    @classmethod
    async def recent_post_likers_by_url(self):
        try:
            dto = UrlDto(**request.get_json())
            result = await self.service.recent_post_likers_by_url(dto.url)
            return JSONEncoder().encode(result)
        except Exception as e:
            return ExceptionUtility.catch_response(e,f'ctrl.recent_post_likers_by_url')
    
    @classmethod
    async def likers_in_post_by_id(self):
        try:
            dto = LikersInPostByIdDto(**request.get_json())
            result = await self.service.likers_in_post_by_id(pk=dto.pk or dto.media_id,ids_likers_action=dto.ids_likers_action)
            return JSONEncoder().encode(result)
        except Exception as e:
            return ExceptionUtility.catch_response(e,f'ctrl.likers_in_post_by_id')
    
    @classmethod
    async def likers_in_post(self):
        try:
            dto = LikersInPostDto(**request.get_json())
            result = await self.service.likers_in_post(url=dto.url,usernames_action=dto.usernames_action)
            return JSONEncoder().encode(result)
        except Exception as e:
            return ExceptionUtility.catch_response(e,f'ctrl.likers_in_post')
        

    @classmethod
    async def post_comments(self):
        try:
            dto = PostCommentsDto(**request.get_json())
            result = await self.service.post_comments(
                pk=dto.pk or dto.id,
                url=dto.url,
                max=dto.max,
                next_max_id=dto.next_max_id,
                only_text=dto.only_text
            )
            return JSONEncoder().encode(result)
        except Exception as e:
            return ExceptionUtility.catch_response(e,f'ctrl.post_comments')
        
    @classmethod
    async def post_comments_by_id(self):
        try:
            dto = PostCommentsDto(**request.get_json())
            result = await self.service.post_comments_by_id(
                pk=dto.pk or dto.id,
                max=dto.max,
                next_max_id=dto.next_max_id,
                only_text=dto.only_text
            )
            return JSONEncoder().encode(result)
        except Exception as e:
            return ExceptionUtility.catch_response(e,f'ctrl.post_comments_by_id')
    
    @classmethod
    async def comments_in_post(self):
        try:
            dto = CommentsInPostDto(**request.get_json())
            result = await self.service.comments_in_post(
                pk=dto.pk or dto.media_id,
                url=dto.url,
                usernames_action=dto.usernames_action,
                ids_action=dto.ids_action,
                max=dto.max
            )
            return JSONEncoder().encode(result)
        except Exception as e:
            return ExceptionUtility.catch_response(e,f'ctrl.comments_in_post')

    @classmethod
    async def comments_in_post_by_id(self):
        try:
            dto = CommentsInPostDto(**request.get_json())
            result = await self.service.comments_in_post_by_id(
                pk=dto.pk or dto.media_id,
                url=dto.url,
                usernames_action=dto.usernames_action,
                ids_action=dto.ids_action,
                max=dto.max
            )
            return JSONEncoder().encode(result)
        except Exception as e:
            return ExceptionUtility.catch_response(e,f'ctrl.comments_in_post_by_id')

        
        
        


