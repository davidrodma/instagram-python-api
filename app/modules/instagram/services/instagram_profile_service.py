from app.modules.instagram.api.instagrapi.instagrapi_profile import InstagrapiProfile

class InstagramProfileService:
    api = InstagrapiProfile()    
    
    async def seen_stories_action(self,username:str,pk:str,media_id:str,max:int=1):
        return await  self.api.seen_stories_action(
            username=username,
            pk=pk,
            media_id=media_id,
            max = max)
        
    