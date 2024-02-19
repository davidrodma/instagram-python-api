from app.modules.instagram.services.instagrapi_api_service import InstagrapiApiService

class InstagramService:
    
    api = InstagrapiApiService()

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
  
    def get_user_info_by_username(self,username):
        return self.api.get_user_info_by_username(username)
    
    def get_user_info_by_id(self,pk):
        return self.api.get_user_info_by_id(pk)

    def test_proxy(self,proxy:str):
        return self.api.test_proxy(proxy)