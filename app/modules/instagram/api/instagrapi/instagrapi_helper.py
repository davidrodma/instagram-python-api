from app.common.utilities.image_utility import ImageUtility
from app.modules.instagram.api.instagrapi.types import Media,MediaWithImage,StoryWithImage
from instagrapi import Client
from typing import Union
class InstagrapiHelper():
    @classmethod
    def test_proxy(self,proxy:str):
        cl = Client()
        before_ip = cl._send_public_request("https://api.ipify.org/")
        cl.set_proxy(proxy)
        after_ip = cl._send_public_request("https://api.ipify.org/")
        print(f"Before: {before_ip}")
        print(f"After: {after_ip}")
        return {'success':before_ip!=after_ip,'before_ip':before_ip,"after_ip":after_ip}
    
    @classmethod
    async def get_image_base64_from_post(self,post:Union[MediaWithImage,StoryWithImage], size: dict = {"width": 150, "height": 150}):
        url = ''
        if hasattr(post,'thumbnail_url'):
            url = post.thumbnail_url
        elif hasattr(post,'resources'):
            url = post.resources[0].thumbnail_url
        else:
            Exception("Invalid Post proprierty url image")
        return ImageUtility.stream_image_to_base64(url, size)
    
    @classmethod
    async def merge_image_base64(self,post:Union[MediaWithImage,StoryWithImage]):
        post.image_base64 = await InstagrapiHelper.get_image_base64_from_post(post)
        return post
