from instagrapi.types import User,Media,Resource
from typing import List

class UserWithImage(User):
    image_base64: str  = ''


class ResourceWithImage(Resource):
    image_base64: str  = ''

class MediaWithImage(Media):
    num_results:int = 0
    image_base64: str  = ''
    resources:List[ResourceWithImage]
    items:List = []
