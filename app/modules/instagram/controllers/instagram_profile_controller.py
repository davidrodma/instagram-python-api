from flask import request
from app.common.controllers.controller import Controller
from app.common.utilities.exception_utility import ExceptionUtility
from app.modules.instagram.dto.user_recent_stories_dto import UserRecentStoriesDto
from app.modules.instagram.services.instagram_service import InstagramService
from app.modules.instagram.dto.username_dto import UsernameDto
from app.common.utilities.json_enconder import JSONEncoder

class InstagramProfileController(Controller):
    service = InstagramService()

    @classmethod
    async def profile_seen_stories_action(self):
        try:
            dto = UserRecentStoriesDto(**request.get_json())
            info = await self.service.profile_seen_stories_action(
                username=dto.username,
                pk=dto.pk,
                media_id=dto.media_id,
                max = dto.max)
            return JSONEncoder().encode(info)
        except Exception as e:
            return ExceptionUtility.catch_response(e,f'Error profile_seen_stories_action')
    
  
        
        
        


