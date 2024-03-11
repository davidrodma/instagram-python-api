from flask import request
from app.common.controllers.controller import Controller
from app.common.utilities.exception_utility import ExceptionUtility
from app.modules.instagram.dto.follower_action_dto import FollowerActionDto
from app.modules.instagram.dto.like_action_dto import LikeActionDto
from app.modules.instagram.dto.comment_action_dto import CommentActionDto
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
    
  
        
        
        


