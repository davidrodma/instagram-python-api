from app.modules.instagram.api.instagrapi.instagrapi_api import InstagrapiApi
from typing import List

class InstagramService:
    api = InstagrapiApi()    
    
    async def login_custom(self,
        username:str,
        password:str,
        proxy:str='',
        verification_mode:str='',
        return_ig_error:bool=False):

        return await self.api.login_custom(
            username=username,
            password=password,
            proxy=proxy,
            verification_mode=verification_mode,
            return_ig_error=return_ig_error)
    
    async def user_info_by_username(self,username:str):
        return await self.api.user_info(username)

    async def user_info_by_id(self,id:str):
        return await self.api.user_info_by_id(id)
    
    async def media_url_info(self,url:str):
        return await self.api.media_url_info(url)
    
    async def media_id_info(self,id:str):
        return await self.api.media_id_info(id)
    
    async def media_id(self,url:str):
        return await self.api.media_id(url)
    
    async def user_recent_posts(self,
        username: str = '', 
        max: int = 60, 
        pk: str = '', 
        return_with_next_max_id:bool=False,
        next_max_id:str = ''
    ):
        return await self.api.user_recent_posts(
            username=username,
            max=max,
            pk=pk,
            return_with_next_max_id=return_with_next_max_id,
            next_max_id=next_max_id
            )
    
    async def user_last_post(self,username: str = '', pk: str = ''):
        return await self.api.user_last_post(username=username,pk=pk)
    
    async def user_info_and_last_post(self,username: str = '', pk: str = ''):
        return await self.api.user_info_and_last_post(username=username,pk=pk)
    
    async def followers(self,
        username: str = '',
        pk: str = '',
        query: str = None,
        max: int = 100,
        next_max_id:str = '',
        return_with_next_max_id:bool = False,
        only_username:bool = False
        ):
        return await self.api.followers(
                username=username,
                pk=pk,
                query=query,
                max=max,
                next_max_id=next_max_id,
                return_with_next_max_id=return_with_next_max_id,
                only_username=only_username
        )
 
    async def followers_in_profile(self,
        username_target: str = '', 
        id_target: str = '', 
        max: int = 200,
        username_action: str = '',
        followers_number: int = None,
        return_image_base64: bool = False) -> dict:
            return await self.api.followers_in_profile(
                                username_target=username_target,
                                id_target=id_target,
                                max=max,
                                username_action=username_action,
                                followers_number=followers_number,
                                return_image_base64=return_image_base64)
    
    async def recent_post_likers(self,pk: str = '', url: str = ''):
        return await self.api.recent_post_likers(pk=pk,url=url)
    
    async def recent_post_likers_by_url(self,url: str):
         return await self.api.recent_post_likers_by_url(url)
    
    async def likers_in_post_by_id(self,pk: str,ids_likers_action: List[str] | str):
         return await self.api.likers_in_post_by_id(pk,ids_likers_action)
    
    async def likers_in_post(self,url: str,usernames_action: List[str] | str):
         return await self.api.likers_in_post(url,usernames_action)
    
    async def post_comments(
        self,
        pk:str='',
        url:str='',
        max:int=20,
        next_max_id:str='',
        only_text:bool=False):
            return await self.api.post_comments(
                 pk=pk,
                 url=url,
                 max=max,
                 next_max_id=next_max_id,
                 only_text=only_text)
    
    async def post_comments_by_id(
        self,
        pk:str,
        max:int=20,
        next_max_id:str='',
        only_text:bool=False):
            return await self.api.post_comments_by_id(
                 pk=pk,
                 max=max,
                 next_max_id=next_max_id,
                 only_text=only_text)
    
    async def comments_in_post(self,pk:str='',url: str='', usernames_action: str='',ids_action:str='', max: int = 20):
        return await self.api.comments_in_post( 
                pk=pk,
                url=url,
                usernames_action=usernames_action,
                ids_action=ids_action,
                max=max
        )
    
    async def comments_in_post_by_id(self,pk:str, ids_action:str, max: int = 20):
        return await self.api.comments_in_post_by_id( 
                pk=pk,
                ids_action=ids_action,
                max=max
        )


        
    