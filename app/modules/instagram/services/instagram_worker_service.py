from app.modules.instagram.api.instagrapi.instagrapi_worker import InstagrapiWorker
from typing import Literal

class InstagramWorkerService:
    api = InstagrapiWorker()    

    async def follower_action(self,username_action:str,username_target:str='',id_target:str=''):
        return await self.api.follower_action(username_action,username_target,id_target)
    
    async def like_action(self,username_action:str,url_target:str='',id_target:str=''):
        return await self.api.like_action(username_action,url_target,id_target)
    
    async def comment_action(self,username_action:str,text:str,url_target:str='',id_target:str=''):
        return await self.api.comment_action(username_action,text,url_target,id_target)
    
    async def story_action(self,username_action:str,username_target:str='',id_target:str='',media_id:str='',max=10):
        return await self.api.story_action(username_action,username_target,id_target,media_id,max)
    
    async def like_comment_action(
        self,
        username_action: str,
        comment_id: str = "",
        username_comment: str = "",
        url_target: str = "",
        id_target: str = "",
        user_id_comment: str = "",
        max: int = 100,
    ):
        return await self.api.like_comment_action(
            username_action=username_action,
            comment_id=comment_id,
            username_comment=username_comment,
            url_target=url_target,
            id_target=id_target,
            user_id_comment=user_id_comment,
            max=max
        )
    
    async def edit_instagram(
        self,
        username:str,
        password:str,
        new_username:str = '',
        new_password:str = '',
        nationality:str = '',
        gender:str = '',
        first_name:str = '',
        biography:str = '',
        visibility:Literal['public', 'private', ''] ='',
        album:str = '',
        filename:str = '',
        posts_album:str = '',
        posts_quantity:int = 0,
        email:str = '',
        external_url:str = '',
        phone_number:str = '',
        proxy:str = '',
        session_id:str = ''):

            return await self.api.edit_instagram(
                username=username,
                password=password,
                new_username=new_username,
                new_password=new_password,
                nationality=nationality,
                gender=gender,
                first_name=first_name,
                biography=biography,
                visibility=visibility,
                album=album,
                filename=filename,
                posts_album=posts_album,
                posts_quantity=posts_quantity,
                email=email,
                external_url=external_url,
                phone_number=phone_number,
                proxy=proxy,
                session_id=session_id
            )

