from app.modules.instagram.api.instagrapi.instagrapi_api import InstagrapiApi

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
    