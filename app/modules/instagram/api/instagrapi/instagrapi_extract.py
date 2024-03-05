from instagrapi import Client
from instagrapi.types import UserShort,Comment
from typing import TYPE_CHECKING, List,Dict,Union
from app.modules.instagram.api.instagrapi.instagrapi_profile import InstagrapiProfile
from app.modules.instagram.api.instagrapi.instagrapi_helper import InstagrapiHelper
from app.modules.instagram.api.instagrapi.types import UserWithImage,User,Media,MediaWithImage,Story,StoryWithImage
from app.modules.profile.services.profile_service import ProfileService
from app.common.utilities.exception_utility import ExceptionUtility
from app.common.utilities.image_utility import ImageUtility
from app import app
import asyncio
import math
import random
from app.common.utilities.logging_utility import LoggingUtility

logger = LoggingUtility.get_logger("InstagrapiExtract")

if TYPE_CHECKING:
    from app.modules.instagram.api.instagrapi.instagrapi_api import InstagrapiApi

class InstagrapiExtract:
    
    profile_service = ProfileService()

    def __init__(self,api:'InstagrapiApi'):
        self.api = api
        self.instagrapi_profile = InstagrapiProfile(api)

    def type_extract_by_port(self):
         port =  app.config.get('SERVER_PORT')
         switch = {
            5011: "extract",
            5012: "worker",
            5013: "boost",
         }
         return switch.get(port, "extract")
        

    async def login_extract(self):

        cl = Client()
        type = self.type_extract_by_port()
        if 'worker'==type:
            raise Exception("Not implement")
        elif 'boost'==type:
            raise Exception("Not implement")
        else:
            try:
                profile = self.profile_service.get_random_profile()
                cl = await self.instagrapi_profile.login(profile,True)
            except Exception as e:
                message_error = f"extract.login_extract->login: {e}"
                logger.error(message_error)
                ExceptionUtility.print_line_error()
                raise Exception(message_error)
        return cl
    
    async def user_info_extract(self,username:str = '', pk: str ='', noImage: bool = False) -> dict:
        try:
            print('user_info_extract init', username or pk)
            success = False
            attempts = 3
            info:UserWithImage = {}
            type = self.type_extract_by_port()
            cl:Client = None
            while not success:
                try:
                    cl = await self.login_extract()
                    attempts -= 1
                    success = True
                    infoUser:User = await self.api.get_user_info(cl, username, pk)
                    info = UserWithImage(**infoUser.model_dump())
                    if type=="worker":
                        pass
                    elif type=="boost":
                        pass
                    else:
                        self.profile_service.update_count(cl.username, 1)
                    if hasattr(info,'profile_pic_url') and not noImage:
                        info.image_base64 = ImageUtility.stream_image_to_base64(info.profile_pic_url.unicode_string(), {'width': 150, 'height': 150})
                except Exception as err:
                    success = False
                    message_error = f"user_info_extract->while: {err}"
                    logger.error(message_error)
                    await self.instagrapi_profile.error_handling(cl, message_error)
                    if attempts <= 0:
                        raise Exception(message_error)
            return info
        except Exception as e:
            message_error = f'extract.user_info_extract: {e}'
            logger.error(message_error)
            ExceptionUtility.print_line_error()
            raise Exception(message_error)
        

    async def user_recent_posts_extract(self,
        username: str = '', 
        max: int = 60, 
        pk: str = '', 
        return_with_next_max_id:bool=False,
        next_max_id:str = ''
        ):
        try:
            print('user_recent_posts_type init username', username, 'pk', pk)
            attempts = 3
            posts:List[MediaWithImage] = []
            posts_media:List[Media] = [] 
            success = False
            info:UserWithImage = {}
            cl:Client = None
            while attempts >= 0:
                attempts -= 1
                success = True

                cl = await self.login_extract()
                try:
                    info_user = await self.api.get_user_info(cl, username, pk)
                    info = UserWithImage(**info_user.model_dump())
                except Exception as e:
                    message_error = f"user_recent_posts_extract.get_user_info {e}"
                    success = False
                    if attempts <= 0 or 'not found' in message_error or 'user info response' in message_error:
                        await self.instagrapi_profile.error_handling(cl, message_error)
                        raise Exception(f'usuário não encontrado: {message_error}')

                if not info or not success:
                    continue

                if hasattr(info,'profile_pic_url'):
                    if not return_with_next_max_id:
                        image = ImageUtility.stream_image_to_base64(info.profile_pic_url, {'width': 150, 'height': 150})
                        #setattr(info, 'image_base64', image)
                        info.image_base64 = image
                    if not pk:
                        pk = str(info.pk)

                if info.is_private:
                    print(f'{username} {pk} privado:', info.is_private)
                    return {
                        'user': info,
                        'error': 'profile is private!',
                        'is_private': True,
                    }

                if info.media_count == 0:
                    return {
                        'user': info,
                        'posts': [],
                        'total_recent_posts': 0,
                    }

                try:
                    posts_media = await self.api.get_user_recent_posts_custom(
                                        cl=cl, 
                                        username=username, 
                                        max=max, 
                                        pk=info.pk, 
                                        return_with_next_max_id=return_with_next_max_id,
                                        next_max_id=next_max_id
                    )
                    posts = [MediaWithImage(**post.model_dump()) for post in posts_media]
                except (Exception) as err:
                    success = False
                    message_error = f"user_recent_posts_extract.get_user_recent_posts_custom: {err} "
                    if 'is private' in message_error:
                        return {
                            'user': info,
                            'error': f'profile is private! {message_error}',
                            'is_private': True,
                        }
                    if attempts <= 0:
                        await self.instagrapi_profile.error_handling(cl, message_error)
                        raise Exception(f'posts não encontrado: {message_error}')

                if not success:
                    continue

                if success:
                    attempts = -1

            if not return_with_next_max_id and isinstance(posts, list):
                if not posts or not posts[0]:
                    return {
                        'user': info,
                        'error': 'posts não encontrado',
                        'total_recent_posts': 0,
                    }
                posts = await asyncio.gather(*[
                    InstagrapiHelper.merge_image_base64(post) for post in posts
                ])
                self.profile_service.update_count(cl.username, len(posts))
                return {
                    'total_recent_posts': len(posts),
                    'posts': posts,
                    'user': info,
                }
            else:
                return {
                    **posts,
                    'username_action': cl.username if cl and cl.username else '',
                    'user': info,
                }
        except (Exception) as e:
            message_error = f'extract.user_recent_posts_extract: {e}'
            logger.error(message_error)
            ExceptionUtility.print_line_error()
            raise Exception(message_error)
        
    async def media_info_extract(self,url:str="",pk:str="",no_image: bool = False):
        try:
            print('media_info_extract init', url or pk)
            success = False
            attempts = 3
            info:MediaWithImage = None
            cl:Client = None
            while not success:
                try:
                    attempts -= 1
                    cl = await self.login_extract()
                    success = True
                    if pk:
                        media:Media = await self.api.get_media_id_info(cl, pk)
                    elif url:
                        media:Media = await self.api.get_media_url_info(cl, url)
                    info = MediaWithImage(**media.model_dump())
                    if info and hasattr(info,'resources') and info.resources[0] and not no_image:
                        info = await InstagrapiHelper.merge_image_base64(info)
                    info.items = [info.model_dump()]
                    info.num_results = 1
                    self.profile_service.update_count(cl.username, 1)
                except Exception as err:
                    message_error = str(err)
                    await self.instagrapi_profile.error_handling(cl, message_error)
                    if attempts <= 0:
                        raise Exception(err)
                    success = False
            return info
        except Exception as e:
            message_error = f'extract.media_info_extract: {e}'
            logger.error(message_error)
            ExceptionUtility.print_line_error()
            raise Exception(message_error)
        
    async def user_last_post_extract(self,username: str = '', pk: str = '') -> dict:
            try:
                obj_posts = await self.user_recent_posts_extract(username=username, max=1, pk=pk)
                if 'error' in obj_posts:
                    if 'is_private' in obj_posts and obj_posts['is_private']:
                        return {'error': 'profile is private', 'is_private': True}
                    raise Exception(obj_posts['error'])
                media:MediaWithImage = obj_posts['posts'][0] if 'posts' in obj_posts and isinstance(obj_posts['posts'], list) else None
                total_recent_posts = obj_posts['total_recent_posts'] if 'total_recent_posts' in obj_posts else 0
                post = None
                if media:
                    media.pk = str(media.pk)
                    post = media
                result = {
                    'total_recent_posts': total_recent_posts,
                    'post': post,
                    'last_post': post,
                    'user': obj_posts['user'] if obj_posts else None
                }
                return result
            except Exception as e:
                message_error = f"extract.user_last_post_extract: {e}"
                logger.error(message_error)
                ExceptionUtility.print_line_error()
                raise Exception(message_error)
            
    async def followers_extract(self,
        username: str = '',
        pk: str = '',
        query: str = None,
        max: int = 200,
        next_max_id:str = '',
        return_with_next_max_id:bool = False,
        only_username:bool = False
        ):

        username_action = ''
        try:
            cl = await self.login_extract()
            username_action = cl.username
            print('SCRAPER FOLLOWERS BEGIN')

            followers = await self.api.get_followers(
                cl = cl,
                username = username,
                pk = pk,
                query = query,
                max = max,
                next_max_id = next_max_id,
                return_with_next_max_id = return_with_next_max_id
            )

            print('SCRAPER EXTRACTED')
            if only_username:
                followers['list'] = [user['username'] for user in followers['list']]
            return followers

        except Exception as e:
            print('SCRAPER ERROR')             
            message_error = f"extract.followers: {e}"
            is_private = True if 'is private' in message_error else False
            logger.error(message_error)
            ExceptionUtility.print_line_error()
            return {'error': str(e), 'username_action': username_action, 'is_private':is_private}
        

    async def followers_in_profile_extract(self,
        username_target: str = '', 
        id_target: str = '', 
        max: int = 200,
        username_action: str = '',
        followers_number: int = None,
        return_image_base64: bool = False) -> dict:

        info_target: UserWithImage
        change_username = False
        try:
            cl = await self.login_extract()
            image_base64 = ''

            info_target = await self.api.get_user_info(cl, username_target, id_target)
            if username_target and username_target != info_target.username:
                change_username = True
            username_target = info_target.username
            id_target = str(info_target.pk)

            if followers_number:
                difference = info_target.follower_count - followers_number
                if difference >= 100:
                    times = math.ceil(difference / 100)
                    max = 100 * times + 100

            if return_image_base64 and info_target.profile_pic_url:
                image_base64 = ImageUtility.stream_image_to_base64(info_target.profile_pic_url, {'width': 150, 'height': 150})

            if info_target.is_private:
                return {
                    'error': f'profile private: {info_target.username}', 
                    'id_target': id_target,
                    'username_target': info_target.username, 
                    'is_private': True}

            followers = await self.api.get_followers(
                cl, 
                username=username_target, 
                pk=info_target.pk, 
                max=max,
                query=username_action)
            followersList:List[UserShort] = followers['list']
            self.profile_service.update_count(cl.username,  len(followersList))
            data = [user for user in followersList if user.username == username_action]
            is_follower = bool(data)
            id_action = data[0].pk if is_follower else ''
            results = {'username_action': username_action, 'id_action': id_action, 'is_follower': is_follower}
            if(is_follower):
                 logger.info(f"{username_action} followed {username_target}") 
            else:
                logger.error(f"{username_action} not followed {username_target}")   

            return {
                'username_target': username_target,
                'is_follower': is_follower,
                'id_target': id_target,
                'image_target': image_base64,
                'follower_count_target': info_target.follower_count,
                'change_username': change_username,
                'username_action': username_action,
                'id_action': id_action,
                'followers': results
            }
        except Exception as e:
            message_error = f"extract.followers_in_profile: {e}"
            logger.error(message_error)
            ExceptionUtility.print_line_error()
            raise Exception(message_error)
        

    async def likers_extract(self,pk:str='',url:str='') -> Dict[str, Union[str, int, List[UserShort]]]:
        error_link = False
        total = 0
        try:
            if not url and not pk:
                raise Exception('likers url or pk post required!')
            cl = await self.login_extract()
            likers:List[UserShort] = await self.api.get_recent_post_likers(cl, pk=pk,url=url)
            total = len(likers)
            self.profile_service.update_count(cl.username,  len(likers))            
            return {
                'media_id': pk,
                'total': total,
                'likers': likers,
            }
        except Exception as e:
            message_error = f"likers_extract: {e}"
            logger.error(message_error)
            ExceptionUtility.print_line_error()
            if '404' in message_error:
                error_link = True
            return {
                'error': message_error,
                'error_link': error_link
            }

    async def likers_in_post_by_id_extract(self,pk:str,ids_likers_action: Union[List[str], str]) -> Dict[str, Union[str, List[Dict[str, Union[str, bool]]], int]]:
        username_action = ''
        image_action = ''
        total = 0
        is_liker = False
        try:
            cl = await self.login_extract()
            likers:List[UserShort] = await self.api.get_recent_post_likers(cl, pk=pk)
            total = len(likers)
            ids_likers_action = [ids_likers_action] if isinstance(ids_likers_action, str) or isinstance(ids_likers_action, int) else ids_likers_action
            ids_likers_action = [str(id) for id in ids_likers_action]
            filtered = [user for user in likers if str(user.pk) in ids_likers_action]
            results = []
            for id in ids_likers_action:
                data = [user for user in filtered if str(user.pk) == id]
                is_liker = True if data else False
                
                username = data[0].username if is_liker else ''
                username_action = username if is_liker else ''
                image_action = data[0].profile_pic_url if is_liker else ''
                is_liker = True if total >= 1000 else is_liker
                if is_liker:
                    logger.info(f"{id} liked in {pk} in {total} likers")
                else:
                    logger.error(f"{id} not liked in {pk} in {total} likers")
                results.append({'username': username, 'id': str(id), 'is_liker': is_liker})

            self.profile_service.update_count(cl.username,  len(likers))            

            if image_action:
                image_action = ImageUtility.stream_image_to_base64(image_action, {'width': 150, 'height': 150})

            if results and not results[0]['is_liker']:
                try:
                    post_info = await self.api.get_media_id_info(cl, pk)
                except:
                    raise Exception(f"extract.likers_in_post_by_id_extract.get_media_id_info {e}")
                if post_info and post_info.pk:
                    if hasattr(post_info,'like_and_view_counts_disabled'):
                        results[0] = {'is_liker': True, 'note': 'is_liker because like_and_view_counts_disabled'}

            return {'media_id': pk, 'username_action': username_action, 'image_action': image_action, 'likers': results, 'total': total,'is_liker':is_liker}
        except Exception as e:
            message_error = f'extract.likers_in_post_by_id_extract {e}'
            logger.error(message_error)
            ExceptionUtility.print_line_error()
            raise Exception(message_error)
        
    async def likers_in_post_extract(self,url:str, usernames_action: Union[List[str], str]='') -> Dict[str, Union[str, List[Dict[str, Union[str, bool]]], int]]:

            username_action = ''
            image_action = ''
            total = 0
            is_liker = False
            try:
                cl = await self.login_extract()
                likers:List[UserShort] = await self.api.get_recent_post_likers(cl,url=url)
                total = len(likers)
                usernames_action = [usernames_action] if isinstance(usernames_action, str) else usernames_action
                filtered = [user for user in likers if user.username in usernames_action]
                results = []
                for username in usernames_action:
                    data = [user for user in filtered if user.username == username]
                    is_liker = True if data else False
                    
                    username = data[0].username if is_liker else ''
                    username_action = username if is_liker else ''
                    image_action = data[0].profile_pic_url if is_liker else ''
                    id = str(data[0].pk) if is_liker else ''
                    is_liker = True if total >= 1000 else is_liker
                    if is_liker:
                        logger.info(f"{username} liked in {url} in {total} likers")
                    else:
                        logger.error(f"{username} not liked in {url} in {total} likers")
                    results.append({'username': username, 'id': id, 'is_liker': is_liker})

                self.profile_service.update_count(cl.username,  len(likers))            

                if image_action:
                    image_action = ImageUtility.stream_image_to_base64(image_action, {'width': 150, 'height': 150})

                if results and not results[0]['is_liker']:
                    try:
                        post_info = await self.api.get_media_url_info(cl, url)
                    except:
                        raise Exception(f"extract.likers_in_post_extract.get_media_id_info {e}")
                    if post_info and post_info.pk:
                        if hasattr(post_info,'like_and_view_counts_disabled'):
                            results[0] = {'is_liker': True, 'note': 'is_liker because like_and_view_counts_disabled'}

                return {'url': url, 'username_action': username_action, 'image_action': image_action, 'likers': results, 'total': total, 'is_liker': is_liker}
            except Exception as e:
                message_error = f'extract.likers_in_post_extract {e}'
                logger.error(message_error)
                ExceptionUtility.print_line_error()
                raise Exception(message_error)
            

    async def post_comments(self,
            pk: str='',
            url:str='', 
            max: int = 20, 
            next_max_id: str = '', 
            only_text: bool = False) -> dict:
        try:
            cl = await self.login_extract()
            comments = await self.api.get_comments_on_post(
                                    cl=cl,
                                    pk=pk,
                                    url=url,
                                    max=max,
                                    next_max_id=next_max_id,
                                    return_with_next_max_id=True
                                )
            result: Union[Dict[str, Union[int, str, List[Comment]]], List[str]] = []
            list_comments:List[Comment] = comments['list']
            if only_text:
                result = [comment.text for comment in list_comments]
            else:
                result = {'count': comments['count'], 'next_max_id': comments['next_max_id'], 'list': list_comments, 'username_action': cl.username}
            return result
        except Exception as e:
            message_error = f'extract.post_comments: {e}'
            logger.error(message_error)
            ExceptionUtility.print_line_error()
            raise Exception(message_error)
        


    async def post_comments_by_id(self,
            pk: str,
            max: int = 20, 
            next_max_id: str = '', 
            only_text: bool = False) -> dict:
        try:
            result = await self.post_comments(pk=pk,max=max,next_max_id=next_max_id,only_text=only_text)
            return result
        except Exception as e:
            message_error = f'extract.post_comments_by_id: {e}'
            logger.error(message_error)
            ExceptionUtility.print_line_error()
            raise Exception(message_error)


    async def comments_in_post_extract(
            self,
            pk:str='',
            url: str='', 
            ids_action:str='', 
            usernames_action: str='', 
            max: int = 20
        ) -> Dict[str, Union[str, List[str], str]]:

        error_link = False
        try:
            if not url and not pk:
                raise Exception('url or pk post required!')
            if not ids_action and not pk:
                raise Exception('ids_action or usernames_action required!')
            cl = await self.login_extract()
            post = None
            attempts = 0
            max_attemps = 2
            message_error = ''
            while attempts < max_attemps:
                attempts += 1
                try:
                    post = await self.api.get_media_url_info(cl, url) if not pk else await self.api.get_media_id_info(cl, pk)
                    break
                except Exception as e:
                    cl = await self.login_extract()
                    message_error = f"comments_in_post_extract.get_media_url_info"
                
            
            if not post or message_error or not hasattr(post,'pk'):
                error_link = True
                raise Exception(f"post/media_id não encontrada {message_error}")
        
            
            if post.comments_disabled or post.commenting_disabled_for_viewer:
                error_link = True
                raise Exception("comentário desabilitado ou limitado para visitantes")
            
            if not post.user:
                error_link = True
                raise Exception("usuário do post limitado ou restrito por idade")
            
            try:
                image_action, comments, is_comment, username_comment = await self.api.find_user_in_comments(cl, pk=post.pk,max=max, username_comment=usernames_action, user_id_comment=ids_action)
                self.profile_service.update_count(cl.username,  len(comments))            
                return {'media_id': post.pk,'is_comment':is_comment,'username_comment':username_comment, 'comments': comments, 'image_action': image_action}
            except Exception as e:
                message_error = f"extract.comments_in_post_extract.find_user_in_comments: {e}"
                await self.instagrapi_profile.error_handling(cl, message_error)
                raise Exception(message_error)
        except Exception as e:
            ExceptionUtility.print_line_error()
            return {'error': str(e), 'error_link': error_link}
        

    async def comment_in_last_post_extract(
            self,
            username: str, 
            text: str, 
            media_id: str = '', 
            user_id:str = ''
        ):
        
        success = False
        attempts = 3
        success = False
        comments = []
        is_comment = False
        image = ''
        code = None
        last_post:Media = None
        cl:Client = None
        try:
            while not success:
                try:
                    success = True
                    attempts -= 1
                    cl = await self.login_extract()

                    if not media_id:
                        posts_media:List[Media] = await self.api.get_user_recent_posts_custom(
                                            cl=cl, 
                                            pk=user_id,
                                            username=username,
                                            max=1)
                        last_post = posts_media[0]
                        media_id = last_post.pk
                        code = last_post.code
                        if last_post.commenting_disabled_for_viewer or last_post.comments_disabled:
                            raise Exception("comentário desabilitado ou limitado para visitantes")

                    image, comments = await self.api.find_user_in_comments(cl, pk=media_id,max=100, username_comment=username, user_id_comment=user_id)
                    self.profile_service.update_count(cl.username, 1)
                    filtered = [comment for comment in comments if  comment['text'] and text.strip().upper() == comment['text'].strip().upper()]
                    is_comment = bool(filtered)
                except Exception as e:
                    message_error = f"extract.comment_in_last_post_extract(while): {e} "
                    if 'is private' in message_error:
                        return {
                            'error': f'profile is private! {message_error}',
                            'is_private': True,
                        }
                    logger.error(message_error)
                    if cl:
                        await self.instagrapi_profile.error_handling(cl, message_error)
                    obj_last_post = await self.user_last_post_extract(username)
                    if 'error' in obj_last_post:
                        return obj_last_post
                    last_post = obj_last_post['last_post']
                    if last_post.commenting_disabled_for_viewer or last_post.comments_disabled:
                        raise Exception("comentário desabilitado ou limitado para visitantes")
                    if attempts > 0:
                        success=False
                    else:
                        raise Exception(message_error)
        except Exception as e:
            message_error = f"extract.comment_in_last_post_extract: {e} "
            logger.error(message_error)
            ExceptionUtility.print_line_error()
            raise Exception(message_error)

    
        return {
            'post_id': media_id,
            'post_code': code,
            'post_image': image,
            'username': username,
            'text': text,
            'is_comment': is_comment,
            'total_comments': len(comments)
        }
    

    async def user_commented_in_post_extract(self,media_id:str,username_comment:str,max:int=200):
        try:
            return await self.comments_in_post_extract(pk=media_id,usernames_action=username_comment,max=max)
        except Exception as e:
            message_error = f"extract.user_commented_in_post_extract: {e} "
            logger.error(message_error)
            ExceptionUtility.print_line_error()
            raise Exception(message_error)
        
    async def user_recent_stories_extract(self,username: str, max: int = 20, pk: str = '', media_id: str = ''):
        try:
            logger.warning('user_recent_stories_extract', username, 'pk', pk)
            cl:Client = None
            attempts = 3
            stories:List[StoryWithImage] = None
            user:UserWithImage = None
            while attempts >= 0:
                attempts -= 1
                success = True

                cl = await self.login_extract()
                try:
                    info = await self.api.get_user_info(cl, username, pk)
                    user = UserWithImage(**info.model_dump())
                except Exception as e:
                    message_error = str(e)
                    success = False
                    if attempts <= 0 or 'not found' in message_error or 'user info response' in message_error:
                        await self.instagrapi_profile.error_handling(cl, message_error)
                        raise Exception('usuário do story parece que não foi encontrado (404 Not Found) : ' + message_error)

                if not user or not success:
                    continue

                if user and user.profile_pic_url:
                    user.image_base64 = ImageUtility.stream_image_to_base64(user.profile_pic_url, {"width":150, "height":150})
                    if not pk:
                        pk = str(user.pk)

                if user.is_private:
                    message_error = f'{username} {pk} privado: {user.is_private} '
                    logger.error(message_error)
                    return {
                        'error': 'profile is private!',
                        'is_private': True,
                        'user': user
                    }

                try:
                    stories_list = await self.api.get_recent_stories(cl=cl, username=username, max=max, pk=pk, media_id=media_id) 
                    stories = [StoryWithImage(**story.model_dump()) for story in stories_list]           
                except Exception as e:
                    success = False
                    message_error =  f'extract.user_recent_stories_extract.get_recent_stories: {e} '
                    logger.error(message_error)
                    await self.instagrapi_profile.error_handling(cl, message_error)
                    if attempts <= 0:
                        raise Exception(f'stories não encontrado: {message_error} ')

                if success:
                    attempts = -1

            if not stories or not stories[0]:
                return {
                    'user': user,
                    'error': 'stories não encontrado',
                    'total_recent_stories': 0
                }
            stories = await asyncio.gather(*[
                    InstagrapiHelper.merge_image_base64(story) for story in stories
            ])

            self.profile_service.update_count(cl.username, 1)
            return {
                'total_recent_stories': len(stories),
                'stories': stories,
                'user': user
            }
        except Exception as e:
            message_error = f'Error user_recent_stories_extract: {e}'
            is_private = True if 'is private' in message_error else False
            logger.error(message_error)
            ExceptionUtility.print_line_error()
            return {'error': message_error,'is_private':is_private}
        

    async def posts_by_tag_extract(self,tag: str, max: int = 27, next_max_id: str = '', tab: str = 'recent'):
        try:
            cl = await self.login_extract()
            try:
                posts = await self.api.get_posts_by_tag(cl, tag=tag, tab=tab, max=max, next_max_id=next_max_id)
                result = {'username_action': cl.username, **posts}
                return result
            except Exception as e:
                message_error = f"posts_by_tag_extract.get_posts_by_tag: {e}"
                raise Exception(message_error)
        except Exception as e:
            message_error = f"posts_by_tag_extract: {e}"
            logger.error(message_error)
            ExceptionUtility.print_line_error()
            if cl:
                await self.instagrapi_profile.error_handling(cl, message_error)
            raise Exception(message_error)
        

    async def biographies_extract(self,username: str, quantity: int, min_char: int = 0):
        try:
            cl = await self.login_extract()
            i = 0
            followers_info = []
            followers_obj = await self.api.get_followers(cl=cl, username=username, max=100)
            followers:List[UserShort] = followers_obj['list']
            random.shuffle(followers)
            for account in followers:
                if i < quantity:
                    profile = self.profile_service.get_by_username(cl.username)
                    if not profile or not profile.status:
                        break
                    followings_obj = await self.api.get_following(cl=cl, username=account.username, pk=account.pk, max=100)
                    followings:List[UserShort] = followings_obj['list']
                    random.shuffle(followings)
                    for acc in followings:
                        if i < quantity:
                            try:
                                followers_info = await self.add_biography_extract(acc, followers_info, min_char)
                                i = len(followers_info)
                                logger.warning(f'Extract Bio {i}/{quantity}')
                            except Exception as err:
                                message_error = str(err)
                                logger.error(f'Extract Bio Error {message_error}')
                                if 'challenge_required' in message_error:
                                    raise Exception(message_error)
            return {
                'username_target': username,
                'count': i,
                'followers': followers_info
            }
        except Exception as e:
            message_error = f"biographies_extract: {e}"
            logger.error(message_error)
            ExceptionUtility.print_line_error()
            raise Exception(message_error)


    async def add_biography_extract(self,account: UserShort, followers_info: list, min_char: int = 0):
        min_char = int(min_char)
        if not hasattr(account,'is_verified') and not hasattr(account,'external_url')  and account.full_name:
            try:
                cl = await self.login_extract()
                user = await self.api.get_user_info(cl,account.username,account.pk)
                bio = user.biography.strip()
                if len(bio) > min_char:
                    followers_info.append({
                        'pk': user.pk,
                        'username': user.username,
                        'full_name': user.full_name,
                        'biography': bio
                    })
                else:
                    logger.warning('Extract bio no minChar')
            except Exception as err:
                message_error = f'add_biography_extract: {user.username} {err}'
                logger.error(message_error)
                raise Exception(message_error)
        else:
            logger.warning('Extract bio is verified or contains external url, or not contains full name\n')
        return followers_info





            




            
            
    
