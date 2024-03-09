from flask import request
from app.common.controllers.controller import Controller
from app.common.utilities.exception_utility import ExceptionUtility
from app.modules.instagram.dto.follower_action_dto import FollowerActionDto
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
    
  
        
        
        


