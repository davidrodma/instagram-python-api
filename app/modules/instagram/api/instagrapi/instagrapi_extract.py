from instagrapi import Client
from typing import TYPE_CHECKING, List
from app.modules.instagram.api.instagrapi.instagrapi_profile import InstagrapiProfile
from app.modules.instagram.api.instagrapi.instagrapi_helper import InstagrapiHelper
from app.modules.instagram.api.instagrapi.types import UserWithImage,User,Media,MediaWithImage
from app.modules.profile.services.profile_service import ProfileService
from app.modules.instagram.utilities.instagram_utility import InstagramUtility
from app.common.utilities.exception_utility import ExceptionUtility
from app.common.utilities.image_utility import ImageUtility
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
                message_error = f"extract.login_extract->login: {e}"
                print(message_error)
                raise Exception(message_error)
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
                        info.image_base64 = ImageUtility.stream_image_to_base64(info.profile_pic_url, {'width': 150, 'height': 150})
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
            message_error = f'extract.user_info_extract: {e}'
            print(message_error)
            raise Exception(message_error)
        

    async def user_recent_posts_extract(self,
        username: str = '', 
        max: int = 60, 
        pk: str = '', 
        return_with_next_max_id:bool=False,
        next_max_id:str = ''
        ):
        try:
            print('user_recent_posts_type init username', username, 'pk', pk)
            attempts = 3
            posts:List[MediaWithImage] = []
            posts_media:List[Media] = [] 
            success = False
            info:UserWithImage = {}
            cl:Client = None
            while attempts >= 0:
                attempts -= 1
                success = True

                cl = await self.login_extract()
                try:
                    info_user = self.api.get_user_info(cl, username, pk)
                    info = UserWithImage(**info_user.model_dump())
                except Exception as e:
                    message_error = f"user_recent_posts_extract.get_user_info {e}"
                    success = False
                    if attempts <= 0 or 'not found' in message_error or 'user info response' in message_error:
                        await self.instagrapi_profile.error_handling(cl, message_error)
                        raise Exception(f'usuário não encontrado: {message_error}')

                if not info or not success:
                    continue

                if hasattr(info,'profile_pic_url'):
                    if not return_with_next_max_id:
                        image = ImageUtility.stream_image_to_base64(info.profile_pic_url, {'width': 150, 'height': 150})
                        #setattr(info, 'image_base64', image)
                        info.image_base64 = image
                    if not pk:
                        pk = str(info.pk)

                if info.is_private:
                    print(f'{username} {pk} privado:', info.is_private)
                    return {
                        'user': info,
                        'error': 'profile is private!',
                        'is_private': True,
                    
                    }

                if info.media_count == 0:
                    return {
                        'user': info,
                        'posts': [],
                        'total_recent_posts': 0,
                    }

                try:
                    posts_media = await self.api.get_user_recent_posts_custom(
                                        cl=cl, 
                                        username=username, 
                                        max=max, 
                                        pk=info.pk, 
                                        return_with_next_max_id=return_with_next_max_id,
                                        next_max_id=next_max_id
                    )
                    posts = [MediaWithImage(**post.model_dump()) for post in posts_media]
                except (Exception) as err:
                    success = False
                    message_error = f"{err}"
                    if attempts <= 0:
                        await self.instagrapi_profile.error_handling(cl, message_error)
                        raise Exception(f'posts não encontrado: {message_error}')

                if not success:
                    continue

                if success:
                    attempts = -1

            if not return_with_next_max_id and isinstance(posts, list):
                if not posts or not posts[0]:
                    return {
                        'user': info,
                        'error': 'posts não encontrado',
                        'total_recent_posts': 0,
                    }
                posts = await asyncio.gather(*[
                    InstagrapiHelper.merge_image_base64(post) for post in posts
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
            ExceptionUtility.print_line_error()
            message_error = f'extract.user_recent_posts_extract: {e}'
            print(message_error)
            raise Exception(message_error)
        
    async def media_info_extract(self,url:str="",pk:str="",no_image: bool = False):
        try:
            print('media_info_extract init', url or pk)
            success = False
            attempts = 3
            info:MediaWithImage = None
            cl:Client = None
            while not success:
                try:
                    attempts -= 1
                    cl = await self.login_extract()
                    success = True
                    if pk:
                        media:Media = await self.api.get_media_id_info(cl, pk)
                    elif url:
                        media:Media = await self.api.get_media_url_info(cl, url)
                    info = MediaWithImage(**media.model_dump())
                    if info and hasattr(info,'resources') and info.resources[0] and not no_image:
                        info = await InstagrapiHelper.merge_image_base64(info)
                    info.items = [info.model_dump()]
                    info.num_results = 1
                    self.profile_service.update_count(cl.username, 1)
                except Exception as err:
                    message_error = str(err)
                    await self.instagrapi_profile.error_handling(cl, message_error)
                    if attempts <= 0:
                        raise Exception(err)
                    success = False
            return info
        except Exception as e:
            ExceptionUtility.print_line_error()
            message_error = f'extract.media_info_extract: {e}'
            print(message_error)
            raise Exception(message_error)
        
    async def user_last_post_extract(self,username: str = '', pk: str = '') -> dict:
            try:
                obj_posts = await self.user_recent_posts_extract(username=username, max=1, pk=pk)
                if 'error' in obj_posts:
                    if 'is_private' in obj_posts and obj_posts['is_private']:
                        return {'error': 'profile is private', 'is_private': True}
                    raise Exception(obj_posts['error'])
                media:MediaWithImage = obj_posts['posts'][0] if 'posts' in obj_posts and isinstance(obj_posts['posts'], list) else None
                total_recent_posts = obj_posts['total_recent_posts'] if 'total_recent_posts' in obj_posts else 0
                post = None
                if media:
                    media.pk = str(media.pk)
                    post = media
                result = {
                    'total_recent_posts': total_recent_posts,
                    'post': post,
                    'last_post': post,
                    'user': obj_posts['user'] if obj_posts else None
                }
                return result
            except Exception as e:
                ExceptionUtility.print_line_error()
                message_error = f"extract.user_last_post_extract: {e}"
                print(message_error)
                raise Exception(message_error)
            
            
    
