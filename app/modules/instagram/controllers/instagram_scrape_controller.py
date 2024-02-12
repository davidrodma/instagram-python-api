from flask import jsonify, request
from app.common.controllers.controller import Controller
from app.common.utilities.exception_utility import ExceptionUtility
from app.modules.instagram.dto.username_dto import UsernameDto
from app.modules.instagram.services.instagram_service import InstagramService
from app.modules.instagram.dto.username_dto import UsernameDto
from app.common.utilities.json_enconder import JSONEncoder

service = InstagramService()

class InstagramScrapeController(Controller):
    
    @staticmethod
    def user_info():
        try:
            dto = UsernameDto(**request.get_json())
            info = service.get_user_info_by_username(dto.username)
            return JSONEncoder().encode(info)
        except BaseException as e:
            return ExceptionUtility.catch_response(e,f'Error Get')
