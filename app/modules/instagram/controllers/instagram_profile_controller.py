from flask import request
from app.common.controllers.controller import Controller
from app.common.utilities.exception_utility import ExceptionUtility
from app.modules.instagram.dto.user_recent_stories_dto import UserRecentStoriesDto
from app.modules.instagram.services.instagram_profile_service import InstagramProfileService
from app.common.utilities.json_enconder import JSONEncoder

class InstagramProfileController(Controller):
    service = InstagramProfileService()

    @classmethod
    async def seen_stories_action(self):
        try:
            dto = UserRecentStoriesDto(**request.get_json())
            info = await self.service.seen_stories_action(
                username=dto.username,
                pk=dto.pk,
                media_id=dto.media_id,
                max = dto.max)
            return JSONEncoder().encode(info)
        except Exception as e:
            return ExceptionUtility.catch_response(e,f'Error ctrl.seen_stories_action')
    
  
        
        
        


