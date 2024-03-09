from app.modules.instagram.api.instagrapi.instagrapi_worker import InstagrapiWorker

class InstagramWorkerService:
    api = InstagrapiWorker()    

    async def follower_action(self,username_action:str,username_target:str='',id_target:str=''):
        return await self.api.follower_action(username_action,username_target,id_target)
