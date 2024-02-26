from app.modules.instagram import api

class InstagramService:
    

    def login_custom(self,
        username:str,
        password:str,
        proxy:str='',
        verification_mode:str='',
        return_ig_error:bool=False):

        return api.login_custom(
            username=username,
            password=password,
            proxy=proxy,
            verification_mode=verification_mode,
            return_ig_error=return_ig_error)
    
    async def user_info(self,username:str):
        return await api.user_info(username)
    
    async def delete_memory_session(self,type:str,username: str):
        return api.delete_memory_session(type,username)

    def get_user_info_by_username(self,username):
        return api.get_user_info_by_username(username)
    
    def get_user_info_by_id(self,pk):
        return api.get_user_info_by_id(pk)

    def test_proxy(self,proxy:str):
        return api.test_proxy(proxy)
    