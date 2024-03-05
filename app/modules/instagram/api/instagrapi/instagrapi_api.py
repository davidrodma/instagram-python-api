from instagrapi import Client
from instagrapi.types import Media,UserShort,Comment,Story
from instagrapi.exceptions import LoginRequired
from app.modules.cookie.services.cookie_service import CookieService
from app.common.utilities.logging_utility import LoggingUtility
from app.modules.instagram.api.instagrapi.instagrapi_challenge import InstagrapiChallenge
from app.modules.instagram.api.instagrapi.instagrapi_profile import InstagrapiProfile
from app.modules.instagram.api.instagrapi.instagrapi_extract import InstagrapiExtract
from app.common.utilities.exception_utility import ExceptionUtility
from typing import List,Union,Dict
from app.modules.instagram.api.instagrapi.types import UserWithImage

logger = LoggingUtility.get_logger("InstagrapiApi")

class InstagrapiApi:
    cookie_service = CookieService()
    
    def __init__(self):
        self.instagrapi_extract = InstagrapiExtract(self)
        self.instagrapi_profile = InstagrapiProfile(self)

    @classmethod
    async def login_custom(self,username:str,password:str,proxy:str='',verification_mode:str='',return_ig_error:bool=False)->Client:
        print("login_custom")
        """
        Attempts to login to Instagram using either the provided session information
        or the provided username and password.
        """
        logger.warning(f'Trying to log with {username}')
        
        cl = Client()
        cl.delay_range = [1, 3]
        try:
            #session = cl.load_settings(f"{username}.json")
            session = self.cookie_service.load_state(username)
        except:
            session = None

        if proxy:
            logger.warning(f"Using proxy {proxy}")
            cl.set_proxy(proxy)
        else:
             logger.warning(f"Not using proxy")

        login_via_session = False
        login_via_pw = False
        message_error = ""
        old_session = {}
        if session:
            try:
                logger.warning(f'Cookie session state found and kept')
                cl.set_settings(session)
                old_session = cl.get_settings()
                cl.login(username, password)
                # check if session is valid
                try:
                    cl.get_timeline_feed()
                except LoginRequired:
                    logger.warning("Session is invalid, need to login via username and password")
                    old_session = cl.get_settings()
                    # use the same device uuids across logins
                    cl.set_settings({})
                    cl.set_uuids(old_session["uuids"])
                    try:
                        cl.login(username, password)
                    except Exception as e: 
                        name_challenge =''
                        #name_challenge = InstagrapiChallenge.detect_name_challenge(e)
                        raise Exception(f"login by login_via_session.get_timeline_feed LoginRequired {name_challenge} {e}")
                except Exception as e:
                    ExceptionUtility.print_line_error()
                    raise Exception(f"login by login_via_session.get_timeline_feed {e}")
                login_via_session = True
                #cl.dump_settings(f"{username}.json")
                self.cookie_service.save_state(username=username,state=cl.get_settings(),pk=cl.user_id)
                logger.warning(f'Cookies updated')
            except Exception as e:
                ExceptionUtility.print_line_error()
                name_challenge =''
                #name_challenge = InstagrapiChallenge.detect_name_challenge(e)
                message_error = f"login by login_via_session username {username} {proxy} {name_challenge}->  Couldn't login user using session information: {e}"
                logger.error(message_error)

        if not login_via_session:
            try:
                logger.info(f"Attempting to login via username {username} and password")
                if bool(old_session) and old_session.get("uuids"):
                    cl.set_uuids(old_session["uuids"])
                else:
                    cl.set_settings({})   
                
                #cl.set_settings({})

                if cl.login(username, password):
                    message_error = ""
                    logger.warning(f'Input Login accepted')
                    try:
                        cl.get_timeline_feed()
                    except Exception as e:
                        name_challenge =''
                        #name_challenge = InstagrapiChallenge.detect_name_challenge(e)
                        raise Exception(f"login by login_via_session->get_timeline_feed() {name_challenge} {e}")
                    login_via_pw = True
                    #cl.dump_settings(f"{username}.json")
                    self.cookie_service.save_state(username=username,state=cl.get_settings(),pk=cl.user_id)
                    logger.warning(f'Cookies created')
            except Exception as e:
                ExceptionUtility.print_line_error()
                name_challenge =''
                #name_challenge = InstagrapiChallenge.detect_name_challenge(e)
                message_error = f"login by login_via_pw ->  Couldn't login user using username {username} and pw, {proxy} {name_challenge}: {e}"
                logger.error(message_error)
        
        if message_error:
            message_error = f"ERROR login Couldn't login user with either password or session: {message_error}"
            logger.error(message_error)
            raise Exception(message_error)
        
        logger.info(f"Logged in {cl.username} { 'via password' if login_via_pw else 'via session'}")
        return cl

    async def get_user_info(self,cl: Client, username:str = '', pk='')->UserWithImage:
        user:UserWithImage = None
        if not username and not pk:
                raise Exception('username or pk required!')
        if not pk:
            try:
                print('username ',cl.username,'get user info by username', username)
                user = cl.user_info_by_username_v1(username=username)
            except Exception as e:
                message_error = f"get_user_info->user_info_by_username  {e} user extract: {cl.username} proxy {cl.proxy} target {username}"
                logger.error(message_error)
                raise Exception(message_error)
        else:
            try:
                print('username',cl.username,'get user info by pk', pk)
                user = cl.user_info_v1(user_id=pk)
            except Exception as e:
                message_error = f"get_user_info->user_info  {e} user extract: {cl.username} proxy {cl.proxy} target pk {pk}"
                logger.error(message_error)
                raise Exception(message_error)
        
        logger.info((f"Username information received: {user.username}, {user.pk}"))
        return user
    
    async def get_media_id_info(self,cl: Client, media_id: str)->Media:
        try:
            result = cl.media_info(media_id)
            logger.info(f'Post Info received {media_id}')
            return result
        except Exception as err:
            message_error = f'ERROR get_media_id_info {err}'
            logger.error(message_error)
            raise Exception(f"api.get_media_id_info target {media_id} (extract username {cl.username} proxy {cl.proxy}): {message_error}")
    
    async def get_story_id_info(self,cl: Client, media_id: str)->Story:
        try:
            result = cl.story_info(media_id)
            logger.info(f'Story Info received {media_id}')
            return result
        except Exception as err:
            message_error = f'ERROR get_story_id_info {err}'
            logger.error(message_error)
            raise Exception(f"api.get_story_id_info target {media_id} (extract username {cl.username} proxy {cl.proxy}): {message_error}")
    
    async def get_media_url_info(self,cl: Client, url: str)->Media:
        try:
            media_id = cl.media_pk_from_url(url)
            result = cl.media_info(media_id)
            logger.info(f'Post Info received {url}')
            return result
        except Exception as err:
            message_error = f'ERROR get_media_url_info {err}'
            logger.error(message_error)
            raise Exception(f"api.get_media_id_info target {url} (extract username {cl.username} proxy {cl.proxy}): {message_error}")  

    async def media_id(self,url: str)->Media:
        try:
            cl = Client()
            media_id = cl.media_pk_from_url(url)
            return media_id
        except Exception as err:
            message_error = f'ERROR media_id {err}'
            logger.error(message_error)
            raise Exception(f"api.get_media_id_info target {url}")      

    async def get_user_recent_posts_custom(
        self,
        cl: Client,
        username: str = '',
        max: int = 60,
        pk: str = '',
        next_max_id:str = '',
        return_with_next_max_id:bool = False
    ):
        if not username and not pk:
            raise Exception('username or pk required!')
        list_posts: List[Media] = []
        print('Username',username,'return_with_next_max_id',return_with_next_max_id,'max',max,'pk',pk,'next_max_id',next_max_id)
        try:
            if not pk:
                #pk = cl.user_id_from_username(username)
                info_user = cl.user_info_by_username_v1(username=username)
                if info_user.is_private:
                    raise Exception('profile is private!')
                pk = info_user.pk
            list_posts,next_max_id = cl.user_medias_paginated(user_id=pk, amount=max, end_cursor=next_max_id)
        except (Exception) as err:
            message_error = f"api.get_user_recent_posts_custom.user_medias_paginated {err}"
            logger.error(message_error)
            raise Exception(message_error)

        logger.info(
            f'User recent posts received {username} {str(pk)} {str(len(list_posts))} posts'
        )

        if return_with_next_max_id:
            return {'total_recent_posts': len(list_posts), 'next_max_id': next_max_id, 'posts': list_posts}

        return list_posts

    async def get_followers(
        self,
        cl: Client,
        username: str = '',
        pk: str = '',
        query: str = None,
        max: int = 100,
        next_max_id:str = '',
        return_with_next_max_id:bool = False
    ):
        followers:List[UserShort] = []
        try:
            if not username and not pk:
                raise Exception('username or pk required!')
            if not pk:
                #pk = cl.user_id_from_username(username)
                info_user = cl.user_info_by_username_v1(username=username)
                if info_user.is_private:
                    raise Exception('profile is private!')
                pk = info_user.pk
            logger.warning(f"get_followers username {username} pk {pk} query={query} max={max} (user extract {cl.username} )")
            if query:
                followers = cl.search_followers(user_id=pk,query=query)
            elif return_with_next_max_id:
                followers,next_max_id = cl.user_followers_v1_chunk(user_id=pk,max_amount=max,max_id=next_max_id)
            else:
                followers = cl.user_followers_v1(user_id=pk, amount=max)
                #followersDict = cl.user_followers(user_id=pk, amount=max)
                #followers = list(followersDict.values())
            
            count = len(followers)
            logger.info(f"User followers received query {query} {pk} {count} followers (user extract {cl.username} )")

            
            return {'count': count, 'next_max_id': next_max_id, 'username_action':cl.username, 'list': followers}

        except Exception as err:
            message_error = f"get_followers {err} user extract: {cl.username} proxy {cl.proxy}"
            logger.error(message_error)
            raise Exception(message_error)
        

    async def get_following(
        self,
        cl: Client,
        username: str = '',
        pk: str = '',
        query: str = None,
        max: int = 100,
        next_max_id:str = '',
        return_with_next_max_id:bool = False
    ):
        following:List[UserShort] = []
        try:
            if not username and not pk:
                raise Exception('username or pk required!')
            if not pk:
                #pk = cl.user_id_from_username(username)
                info_user = cl.user_info_by_username_v1(username=username)
                if info_user.is_private:
                    raise Exception('profile is private!')
                pk = info_user.pk
            logger.warning(f"get_following username {username} pk {pk} query={query} max={max} (user extract {cl.username} )")
            if query:
                following = cl.search_following(user_id=pk,query=query)
            elif return_with_next_max_id:
                following,next_max_id = cl.user_following_v1_chunk(user_id=pk,max_amount=max,max_id=next_max_id)
            else:
                following = cl.user_following_v1(user_id=pk, amount=max)
                #followersDict = cl.user_followers(user_id=pk, amount=max)
                #followers = list(followersDict.values())
            
            count = len(following)
            logger.info(f"User following received query {query} {pk} {count} following (user extract {cl.username} )")

            
            return {'count': count, 'next_max_id': next_max_id, 'username_action':cl.username, 'list': following}

        except Exception as err:
            message_error = f"api.get_following {err} user extract: {cl.username} proxy {cl.proxy}"
            logger.error(message_error)
            raise Exception(message_error)
        
    async def get_recent_post_likers(self, cl: Client, pk:str='',url:str='') -> list:
        try:
            if not url and not pk:
                raise Exception('url or pk required!')
            if not pk:
                pk = cl.media_pk_from_url(url)
            likers = cl.media_likers(pk)
            logger.info(f"Recent Post Likers {pk} {len(likers)} likers")
            return likers
        except Exception as e:
            message_error = f"api.get_recent_post_likers {e} user extract: {cl.username} proxy {cl.proxy}"
            logger.error(message_error)
            raise Exception(message_error)
        

    async def get_comments_on_post(self,
        cl:Client, 
        pk: str='', 
        url: str='', 
        max: int = 20, 
        next_max_id:str='',
        return_with_next_max_id:bool = False) -> List[Comment]|dict:
        
        list_comments: List[Comment] = []
        try:
            if not url and not pk:
                raise Exception('url or pk required!')
            
            if not pk:
                pk = cl.media_pk_from_url(url)
            if not return_with_next_max_id and not next_max_id:
               list_comments = cl.media_comments(media_id=pk, amount = max)
            else:
               list_comments, next_max_id = cl.media_comments_chunk(media_id=pk, max_amount=max, min_id = next_max_id)

            count_comments = len(list_comments)
            logger.info(f"Comments received: {count_comments} comments")
                
            if return_with_next_max_id:
                return {'count': count_comments, 'next_max_id': next_max_id, 'list': list_comments}
                
            return list_comments
        except Exception as e:
            message_error =  f"api.get_comments_on_post {e} username_action: {cl.username}, proxy {cl.proxy}, social_id_post {pk}"
            logger.error(message_error)
            raise Exception(message_error)
        
    async def get_recent_stories(
        self,
        cl: Client,
        username: str = '',
        max: int = 1,
        pk: Union[str, int] = '',
        media_id: Union[str, int] = ''
    ) -> List[Story]:
        list = []
        try:
            if not pk:
                info_user = cl.user_info_by_username_v1(username=username)
                if info_user.is_private:
                    raise Exception('profile is private!')
                pk = info_user.pk
            if media_id:
                story = await self.get_story_id_info(cl, media_id)
                list.append(story)
            else:
                list = cl.user_stories(user_id=pk,amount=max)
        except Exception as err:
            message_error = f'get_recent_stories: {err}'
            logger.error(message_error)
            raise Exception(message_error)
        logger.info(f"User recent stories received {username} {pk} {len(list)} stories")
        return list
    
    async def get_posts_by_tag(
        self,
        cl: Client,
        tag:str,
        next_max_id:str = '',
        max:int = 27,
        tab:str = 'recent'
    ):        
        list_posts:List[Media] = []
        count_posts = 0
        try:
            list_posts, next_max_id = cl.hashtag_medias_v1_chunk(name=tag, max_amount=max, tab_key=tab, max_id = next_max_id)
            count_posts = len(list_posts)
        except Exception as err:
            message_error = f'get_posts_by_tag: {err}'
            logger.error(message_error)
            raise Exception(message_error)

        logger.info(f"Hashag {tag} {count_posts} posts received")

        return {'count': count_posts, 'next_max_id': next_max_id, 'list': list_posts}
    
    async def seen_stories(
            self,
            cl: Client, 
            username: str = '', 
            max:int= 1,
            pk: str = '', 
            media_id: str = ''):
            seen_result = None
            stories:List[Story] = []
            try:
                if not pk:
                    info = await self.get_user_info(cl, username)
                    pk = info.pk
                stories = await self.get_recent_stories(cl=cl, username=username, max=max, pk=pk, media_id=media_id)
                stories_pk = [int(story.pk) for story in stories]
                seen_result = cl.story_seen(stories_pk)
            except Exception as err:
                message_error = f'seen_stories {err}'
                logger.error(message_error)
                raise Exception(message_error)
            
            logger.info(f'{cl.username} seen {username} {pk} {len(stories)} stories')

            return {'status': 'ok' if seen_result else 'error', 'list': stories, 'count': len(stories),'seen_result':seen_result}

    async def find_user_in_comments(
            self,
            cl: Client, 
            pk: str, 
            max: int, 
            username_comment: str = '', 
            user_id_comment: str = ''
        ) -> Dict[str, Union[str, List[Dict[str, Union[str, int]]]]]:
        
        try:
            comments_on_post:List[Comment] = await self.get_comments_on_post(cl, pk=pk, max=max)
            image_action = ''
            if not user_id_comment and not username_comment:
                raise Exception('user_id_comment or username_comment required')
            arr_find = [user_id_comment] if user_id_comment else [username_comment]
            filtered = [comment for comment in comments_on_post if comment.user.pk in arr_find or comment.user.username in arr_find]
            comments = []
            is_comment = False
            for pk_or_username in arr_find:
                data = [comment for comment in filtered if comment.user.pk == pk_or_username or comment.user.username == pk_or_username]
                is_comment = bool(data)
                comment_obj:Comment = data[0] if is_comment else None
                username = comment_obj.user.username if is_comment else username_comment
                id = comment_obj.user.pk if is_comment else user_id_comment
                image_action = comment_obj.user.profile_pic_url.unicode_string() if is_comment else ''
                text = comment_obj.text if is_comment else ''
                comment_id = comment_obj.pk if is_comment else 0
                comment_like_count = comment_obj.like_count if is_comment else 0
                if is_comment:
                    username_comment = username
                    logger.info(f"{id} {username} commented media {pk}")
                comments.append({'id': id, 'username': username, 'is_comment': is_comment, 'comment_id': comment_id, 'comment_like_count': comment_like_count, 'text': text})
            return image_action, comments, is_comment, username_comment
        except Exception as e:
            raise Exception(f"api.find_user_in_comments {e}")
        
    async def user_info(self,username:str="",pk:str=""):
        try:
            result = await self.instagrapi_extract.user_info_extract(username=username,pk=pk)
            return result
        except Exception as e:
            raise Exception(f"instagrapi_api.user_info.user_info_extract: {e}")
        
    async def user_info_by_username(self,username:str):
        try:
            result = await self.user_info(username=username)
            return result
        except Exception as e:
            raise Exception(f"instagrapi_api.user_info_by_username.user_info_extract: {e}")
        
    async def user_info_by_id(self,id:str):
        try:
            result = await self.user_info(pk=id)
            return result
        except Exception as e:
            raise Exception(f"instagrapi_api.user_info_by_id.user_info_extract: {e}")
        
    async def media_id_info(self,id:str):
        try:
            result = await self.instagrapi_extract.media_info_extract(pk=id)
            return result
        except Exception as e:
            raise Exception(f"instagrapi_api.media_id_info.media_info_extract: {e}")
        
    async def media_url_info(self,url:str):
        try:
            result = await self.instagrapi_extract.media_info_extract(url=url)
            return result
        except Exception as e:
            raise Exception(f"instagrapi_api.media_id_info.media_info_extract: {e}")
    
    async def user_recent_posts(
            self,
            username: str, 
            max: int = 60, 
            pk: str = '', 
            return_with_next_max_id: str='',
            next_max_id=''
        ):
        try:
            result = await self.instagrapi_extract.user_recent_posts_extract(
                username=username,
                max=max,
                pk=pk,
                return_with_next_max_id=return_with_next_max_id,
                next_max_id=next_max_id
            )
            return result
        except Exception as e:
            raise Exception(f"instagrapi_api.user_recent_posts: {e}")
        
    async def user_last_post(self,username: str = '', pk: str = '') -> dict:
        try:
            result = await self.instagrapi_extract.user_last_post_extract(username=username,pk=pk)
            return result
        except Exception as e:
            raise Exception(f"api.user_last_post: {e}")


    async def user_info_and_last_post(self,username: str = '', pk: str = '') -> dict:
        try:
            result = await self.instagrapi_extract.user_last_post_extract(username=username,pk=pk)
            return result
        except Exception as e:
            raise Exception(f"api.user_last_post: {e}")
        

    async def followers(self,
        username: str = '',
        pk: str = '',
        query: str = None,
        max: int = 200,
        next_max_id:str = '',
        return_with_next_max_id:bool = False,
        only_username:bool = False
        ):
        try:
            result = await self.instagrapi_extract.followers_extract(
                username=username,
                pk=pk,
                query=query,
                max=max,
                next_max_id=next_max_id,
                return_with_next_max_id=return_with_next_max_id,
                only_username=only_username
            )
            return result
        except Exception as e:
            raise Exception(f"api.followers: {e}")
        
    async def followers_in_profile(self,
        username_target: str = '', 
        id_target: str = '', 
        max: int = 200,
        username_action: str = '',
        followers_number: int = None,
        return_image_base64: bool = False) -> dict:
            try:
                result = await self.instagrapi_extract.followers_in_profile_extract(
                                username_target=username_target,
                                id_target=id_target,
                                max=max,
                                username_action=username_action,
                                followers_number=followers_number,
                                return_image_base64=return_image_base64)
                return result
            except Exception as e:
                raise Exception(f"api.followers: {e}")
    
    async def recent_post_likers(self,
        pk: str = '', 
        url: str = ''
        ):
        try:
            result = await self.instagrapi_extract.likers_extract(pk=pk,url=url)
            return result
        except Exception as e:
            raise Exception(f"api.likers_extract: {e}")

    async def recent_post_likers_by_url(self,url: str):
        try:
            result = await self.recent_post_likers(url=url)
            return result
        except Exception as e:
            raise Exception(f"api.recent_post_likers_by_url: {e}")
        

    async def likers_in_post_by_id(self,pk: str, ids_likers_action: List[str] | str):
        try:
            result = await self.instagrapi_extract.likers_in_post_by_id_extract(pk,ids_likers_action)
            return result
        except Exception as e:
            raise Exception(f"api.likers_in_post_by_id: {e}")
            
    async def likers_in_post(self,url: str, usernames_action: List[str] | str):
        try:
            result = await self.instagrapi_extract.likers_in_post_extract(url,usernames_action)
            return result
        except Exception as e:
            raise Exception(f"api.likers_in_post: {e}")
        
    async def post_comments(
            self,
            url:str='',
            pk:str='',
            max:int=20,
            next_max_id:str='',
            only_text:bool=False
        ):
        try:
            result = await self.instagrapi_extract.post_comments( 
                pk=pk,
                url=url,
                max=max,
                next_max_id = next_max_id,
                only_text= only_text 
            )
            return result
        except Exception as e:
            raise Exception(f"api.post_comments: {e}")
        
    async def post_comments_by_id(
            self,
            pk:str,
            max:int=20,
            next_max_id:str='',
            only_text:bool=False
        ):
        try:
            result = await self.instagrapi_extract.post_comments_by_id( 
                pk=pk,
                max=max,
                next_max_id = next_max_id,
                only_text= only_text 
            )
            return result
        except Exception as e:
            raise Exception(f"api.post_comments_by_id: {e}")
        
    async def comments_in_post(self,pk:str='',url:str='',ids_action:str='', usernames_action: str='', max: int = 20):
        try:
            result = await self.instagrapi_extract.comments_in_post_extract( 
                pk=pk,
                url=url,
                ids_action=ids_action,
                usernames_action=usernames_action,
                max=max
            )
            return result
        except Exception as e:
            raise Exception(f"api.comments_in_post: {e}")
        

    async def comments_in_post_by_id(self,pk:str='',ids_action:str='', max: int = 20):
        try:
            result = await self.instagrapi_extract.comments_in_post_extract( 
                pk=pk,
                ids_action=ids_action,
                max=max
            )
            return result
        except Exception as e:
            raise Exception(f"api.comments_in_post_by_id: {e}")
        
    async def comment_in_last_post(self,username:str,text:str,media_id:str='',user_id:str=''):
        try:
            result = await self.instagrapi_extract.comment_in_last_post_extract( 
                username=username,
                text=text,
                media_id=media_id,
                user_id=user_id
            )
            return result
        except Exception as e:
            raise Exception(f"api.comment_in_last_post_extract: {e}")
        
    async def user_commented_in_post(self,media_id:str,username_comment:str,max:int=200):
        try:
            result = await self.instagrapi_extract.user_commented_in_post_extract( 
                media_id=media_id,
                username_comment=username_comment,
                max=max
            )
            return result
        except Exception as e:
            raise Exception(f"api.user_commented_in_post: {e}")
    
    async def user_recent_stories(self,username: str, max: int = 20, pk: str = '', media_id: str = ''):
        try:
            result = await self.instagrapi_extract.user_recent_stories_extract( 
                username=username,
                pk=pk,
                max=max,
                media_id=media_id
            )
            return result
        except Exception as e:
            raise Exception(f"api.user_recent_stories: {e}")
        
    async def posts_by_tag(self,tag: str, max: int = 27, next_max_id: str = '', tab: str = 'recent'):
        try:
            result = await self.instagrapi_extract.posts_by_tag_extract( 
                tag=tag,
                max=max,
                next_max_id=next_max_id,
                tab=tab
            )
            return result
        except Exception as e:
            raise Exception(f"api.posts_by_tag: {e}")
        

    async def extract_biographies(self,username: str, quantity: int, min_char: int = 0):
        try:
            result = await self.instagrapi_extract.biographies_extract( 
                username=username,
                quantity=quantity,
                min_char=min_char,
            )
            return result
        except Exception as e:
            raise Exception(f"api.extract_biographie: {e}")
        

    async def profile_seen_stories_action(self,username:str,pk:str,media_id:str,max:int=1):
        try:
            result = await  self.instagrapi_profile.seen_stories_action(
                username=username,
                pk=pk,
                media_id=media_id,
                max = max)
            return result
        except Exception as e:
            raise Exception(f"api.profile_action_seen_stories: {e}")
        
        
        
        
            

            

