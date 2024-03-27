from flask import request
from app.common.controllers.controller import Controller
from app.common.utilities.exception_utility import ExceptionUtility
from app.modules.instagram.dto.follower_action_dto import FollowerActionDto
from app.modules.instagram.dto.like_action_dto import LikeActionDto
from app.modules.instagram.dto.comment_action_dto import CommentActionDto
from app.modules.instagram.dto.story_action_dto import StoryActionDto
from app.modules.instagram.dto.like_comment_action_dto import LikeCommentActionDto
from app.modules.instagram.dto.edit_instagram_dto import EditInstagramDto
from app.modules.instagram.services.instagram_worker_service import InstagramWorkerService
from app.common.utilities.json_enconder import JSONEncoder

class InstagramWorkerController(Controller):
    service = InstagramWorkerService()

    @classmethod
    async def follower_action(self):
        try:
            dto = FollowerActionDto(**request.get_json())
            info = await self.service.follower_action(
                username_action=dto.username_action,
                username_target=dto.username_target,
                id_target=dto.id_target
            )
            return JSONEncoder().encode(info)
        except Exception as e:
            return ExceptionUtility.catch_response(e,f'Error ctrl.follower_action')
    
    @classmethod
    async def like_action(self):
        try:
            dto = LikeActionDto(**request.get_json())
            info = await self.service.like_action(
                username_action=dto.username_action,
                url_target=dto.url_target,
                id_target=dto.id_target
            )
            return JSONEncoder().encode(info)
        except Exception as e:
            return ExceptionUtility.catch_response(e,f'Error ctrl.like_action')
    
    @classmethod
    async def comment_action(self):
        try:
            dto = CommentActionDto(**request.get_json())
            info = await self.service.comment_action(
                username_action=dto.username_action,
                text=dto.text,
                url_target=dto.url_target,
                id_target=dto.id_target
            )
            return JSONEncoder().encode(info)
        except Exception as e:
            return ExceptionUtility.catch_response(e,f'Error ctrl.comment_action')
    
    @classmethod
    async def story_action(self):
        try:
            dto = StoryActionDto(**request.get_json())
            info = await self.service.story_action(
                username_action=dto.username_action,
                username_target=dto.username_target,
                id_target=dto.id_target,
                media_id=dto.media_id,
                max=dto.max
            )
            return JSONEncoder().encode(info)
        except Exception as e:
            return ExceptionUtility.catch_response(e,f'Error ctrl.story_action')
        

    @classmethod
    async def like_comment_action(self):
        try:
            dto = LikeCommentActionDto(**request.get_json())
            info = await self.service.like_comment_action(
                username_action=dto.username_action,
                comment_id=dto.comment_id,
                username_comment=dto.username_comment,
                url_target=dto.url_target,
                id_target=dto.id_target,
                user_id_comment=dto.user_id_comment,
                max=dto.max
            )
            return JSONEncoder().encode(info)
        except Exception as e:
            return ExceptionUtility.catch_response(e,f'Error ctrl.like_comment_action')
        

    @classmethod
    async def edit_instagram(self):
        try:
            dto = EditInstagramDto(**request.get_json())
            info = await self.service.edit_instagram(
                username=dto.username,
                password=dto.password,
                new_username=dto.new_username,
                new_password=dto.new_password,
                nationality=dto.nationality,
                gender=dto.gender,
                first_name=dto.first_name,
                biography=dto.biography,
                visibility=dto.visibility,
                album=dto.album,
                filename=dto.filename,
                posts_album=dto.posts_album,
                posts_quantity=dto.posts_quantity,
                email=dto.email,
                external_url=dto.external_url,
                phone_number=dto.phone_number,
                proxy=dto.proxy,
                session_id=dto.session_id
            )
            return JSONEncoder().encode(info)
        except Exception as e:
            return ExceptionUtility.catch_response(e,f'Error ctrl.edit_instagram')