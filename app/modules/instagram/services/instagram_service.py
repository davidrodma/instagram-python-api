from app.modules.instagram.api.instagrapi.instagrapi_api import InstagrapiApi

class InstagramService:
    api = InstagrapiApi()    
    
    def login_custom(self,
        username:str,
        password:str,
        proxy:str='',
        verification_mode:str='',
        return_ig_error:bool=False):

        return self.api.login_custom(
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
    