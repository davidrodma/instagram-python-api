from flask import jsonify, request
from app.common.controllers.controller import Controller
from app.common.utilities.exception_utility import ExceptionUtility
from app.modules.instagram.dto.username_dto import UsernameDto
from app.modules.instagram.services.instagram_service import InstagramService
from app.modules.instagram.dto.username_dto import UsernameDto
from app.modules.instagram.dto.id_dto import IdDto
from app.modules.instagram.dto.url_dto import UrlDto
from app.modules.instagram.dto.post_list_dto import PostListDto
from app.modules.instagram.dto.pk_or_username_dto import PkOrUsernameDto
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
