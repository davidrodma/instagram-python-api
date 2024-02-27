from flask import jsonify, request
from app.common.controllers.controller import Controller
from app.common.utilities.exception_utility import ExceptionUtility
from app.modules.instagram.dto.username_dto import UsernameDto
from app.modules.instagram.services.instagram_service import InstagramService
from app.modules.instagram.dto.username_dto import UsernameDto
from app.modules.instagram.dto.id_dto import IdDto
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
