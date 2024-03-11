from app.modules.instagram.api.instagrapi.instagrapi_worker import InstagrapiWorker

class InstagramWorkerService:
    api = InstagrapiWorker()    

    async def follower_action(self,username_action:str,username_target:str='',id_target:str=''):
        return await self.api.follower_action(username_action,username_target,id_target)
    
    async def like_action(self,username_action:str,url_target:str='',id_target:str=''):
        return await self.api.like_action(username_action,url_target,id_target)
    
    async def comment_action(self,username_action:str,text:str,url_target:str='',id_target:str=''):
        return await self.api.comment_action(username_action,text,url_target,id_target)
