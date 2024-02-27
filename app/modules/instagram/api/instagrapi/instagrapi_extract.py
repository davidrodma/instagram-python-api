from instagrapi import Client
from typing import TYPE_CHECKING
from app.modules.instagram.api.instagrapi.instagrapi_profile import InstagrapiProfile
from app.modules.instagram.api.instagrapi.types import UserWithImage,User
from app.modules.profile.services.profile_service import ProfileService
from app.modules.instagram.utilities.instagram_utility import InstagramUtility
from app.common.utilities.exception_utility import ExceptionUtility
from app import app
import asyncio

if TYPE_CHECKING:
    from app.modules.instagram.api.instagrapi.instagrapi_api import InstagrapiApi

class InstagrapiExtract:
    
    profile_service = ProfileService()

    def __init__(self,api:'InstagrapiApi'):
        self.api = api
        self.instagrapi_profile = InstagrapiProfile(api)

    def type_extract_by_port(self):
         port =  app.config.get('SERVER_PORT')
         switch = {
            5011: "extract",
            5012: "worker",
            5013: "boost",
         }
         return switch.get(port, "extract")
        

    async def login_extract(self):

        cl = Client()
        type = self.type_extract_by_port()
        if 'worker'==type:
            raise Exception("Not implement")
        elif 'boost'==type:
            raise Exception("Not implement")
        else:
            try:
                profile = self.profile_service.get_random_profile()
                cl = await self.instagrapi_profile.login(profile,True)
            except Exception as e:
                ExceptionUtility.print_line_error()
                raise Exception(f"login_extract->login: {e}")
        return cl
    
    async def user_info_extract(self,username:str = '', pk: str ='', noImage: bool = False) -> dict:
        try:
            print('user_info_extract init', username or pk)
            success = False
            attempts = 3
            info:UserWithImage = {}
            type = self.type_extract_by_port()
            cl:Client = None
            while not success:
                try:
                    cl = await self.login_extract()
                    attempts -= 1
                    success = True
                    infoUser:User = self.api.get_user_info(cl, username, pk)
                    info = UserWithImage(**infoUser.model_dump())
                    if type=="worker":
                        pass
                    elif type=="boost":
                        pass
                    else:
                        self.profile_service.update_count(cl.username, 1, 'userInfo')
                    if hasattr(info,'profile_pic_url') and not noImage:
                        image = InstagramUtility.stream_image_to_base64(info.profile_pic_url, {'width': 150, 'height': 150})
                        #setattr(info, 'image_base64', image)
                        info.image_base64 = image
                except Exception as err:
                    success = False
                    message_error = f"user_info_extract->while: {err}"
                    print(message_error)
                    await self.instagrapi_profile.error_handling(cl, message_error)
                    if attempts <= 0:
                        raise Exception(message_error)
            return info
        except Exception as e:
            ExceptionUtility.print_line_error()
            message_error = f'user_info_extract: {e}'
            print(message_error)
            raise Exception(message_error)
        

    async def user_recent_posts_extract(self,username: str, max: int = 60, pk: str = '', options: dict = None):
        try:
            print('user_recent_posts_type init username', username, 'pk', pk)
            ig = None
            attempts = 3
            posts = []
            success = False
            info:UserWithImage = {}
            cl:Client = None
            while attempts >= 0:
                attempts -= 1
                success = True

                cl = await self.login_extract()
                try:
                    infoUser = await self.api.get_user_info(cl, username, pk)
                    info = UserWithImage(**infoUser.model_dump())
                except Exception as e:
                    message_error = f"user_recent_posts_extract.get_user_info {e}"
                    success = False
                    if attempts <= 0 or 'not found' in message_error or 'user info response' in message_error:
                        await self.instagrapi_profile.error_handling(ig, message_error)
                        raise Exception(f'usuário não encontrado: {message_error}')

                if not info or not success:
                    continue

                if hasattr(info,'profile_pic_url'):
                    if not options.get('return_with_next_max_id', False):
                        image = InstagramUtility.stream_image_to_base64(info.profile_pic_url, {'width': 150, 'height': 150})
                        #setattr(info, 'image_base64', image)
                        info.image_base64 = image
                    if not pk:
                        pk = str(info.pk)

                if info.is_private:
                    print(f'{username} {pk} privado:', info.is_private)
                    return {
                        'error': 'profile is private!',
                        'is_private': True,
                        'user': info,
                    }

                if info.media_count == 0:
                    return {
                        'user': info,
                        'posts': [],
                        'total_recent_posts': 0,
                    }

                try:
                    posts = await self.api.get_user_recent_posts_custom(ig, username, max, info.pk, options)
                except (Exception) as err:
                    success = False
                    message_error = f"{err}"
                    if attempts <= 0:
                        await self.instagrapi_profile.error_handling(ig, message_error)
                        raise Exception(f'posts não encontrado: {message_error}')

                if not success:
                    continue

                if success:
                    attempts = -1

            if not options.get('return_with_next_max_id', False) and isinstance(posts, list):
                if not posts or not posts[0]:
                    return {
                        'user': info,
                        'error': 'posts não encontrado',
                        'total_recent_posts': 0,
                    }

                posts = await asyncio.gather(*[
                    InstagramUtility.get_image_base64_from_post(post) for post in posts
                ])
                self.profile_service.update_count(cl.username, len(posts))
                return {
                    'total_recent_posts': len(posts),
                    'posts': posts,
                    'user': info,
                }
            else:
                return {
                    **posts,
                    'username_action': cl.username if cl and cl.username else '',
                    'user': info,
                }
        except (Exception) as e:
            raise Exception(str(e))
