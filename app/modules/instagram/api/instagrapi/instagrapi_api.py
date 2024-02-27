from instagrapi import Client
from instagrapi.types import Media
from instagrapi.exceptions import LoginRequired
from app.modules.cookie.services.cookie_service import CookieService
from app.common.utilities.logging_utility import LoggingUtility
from app.modules.instagram.api.instagrapi.instagrapi_challenge import InstagrapiChallenge
from app.modules.instagram.api.instagrapi.instagrapi_profile import InstagrapiProfile
from app.modules.instagram.api.instagrapi.instagrapi_extract import InstagrapiExtract
from typing import Union,Dict, Optional,List
from app.modules.instagram.api.instagrapi.types import UserWithImage,User

logger = LoggingUtility.get_logger("InstagrapiApi")

class InstagrapiApi:
    cookie_service = CookieService()
    
    def __init__(self):
        self.instagrapi_extract = InstagrapiExtract(self)
        self.instagrapi_profile = InstagrapiProfile(self)

    @classmethod
    def login_custom(self,username:str,password:str,proxy:str='',verification_mode:str='',return_ig_error:bool=False)->Client:
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
                        name_challenge = InstagrapiChallenge.detect_name_challenge(e)
                        raise Exception(f"login by login_via_session.get_timeline_feed LoginRequired {name_challenge} {e}")
                except Exception as e:
                    raise Exception(f"login by login_via_session.get_timeline_feed")
                login_via_session = True
                #cl.dump_settings(f"{username}.json")
                self.cookie_service.save_state(username=username,state=cl.get_settings(),pk=cl.user_id)
                logger.warning(f'Cookies updated')
            except Exception as e:
                name_challenge = InstagrapiChallenge.detect_name_challenge(e)
                message_error = f"login by login_via_session username {username} {proxy} {name_challenge}->  Couldn't login user using session information: {e}"
                logger.error(message_error)

        if not login_via_session:
            try:
                logger.info(f"Attempting to login via username {username} and password")
                
                cl.set_uuids(old_session["uuids"]) if old_session.get("uuids") else cl.set_settings({})   
                
                #cl.set_settings({})

                if cl.login(username, password):
                    message_error = ""
                    logger.warning(f'Input Login accepted')
                    try:
                        cl.get_timeline_feed()
                    except Exception as e:
                        name_challenge = InstagrapiChallenge.detect_name_challenge(e)
                        raise Exception(f"login by login_via_session->get_timeline_feed() {name_challenge} {e}")
                    login_via_pw = True
                    #cl.dump_settings(f"{username}.json")
                    self.cookie_service.save_state(username=username,state=cl.get_settings(),pk=cl.user_id)
                    logger.warning(f'Cookies created')
            except Exception as e:
                name_challenge = InstagrapiChallenge.detect_name_challenge(e)
                message_error = f"login by login_via_pw ->  Couldn't login user using username {username} and pw, {proxy} {name_challenge}: {e}"
                logger.error(message_error)
        
        if message_error:
            logger.warning("ENTROU ERROR")
            raise Exception(f"ERROR login Couldn't login user with either password or session: {message_error}")
        
        logger.info(f"Logged in {cl.username} { 'via password' if login_via_pw else 'via session'}")
        return cl

    def get_user_info(self,cl: Client, username:str = '', pk='')->UserWithImage:
        user:UserWithImage = None
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
        

    async def get_user_recent_posts_custom(
        self,
        cl: Client,
        username: str = '',
        max: int = 60,
        pk: Union[str, None, int] = None,
        options: Optional[Dict[str, Union[str, bool]]] = None,
    ):
        list_posts: List[Media] = []
        next_max_id = ''
        return_with_next_max_id = False

        if options:
            next_max_id = options.get('next_max_id', '')
            return_with_next_max_id = options.get('return_with_next_max_id', False)

        try:
            if pk is None:
                pk = cl.user_id_from_username(username)
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

    def test_proxy(self,proxy:str):
        cl = Client()
        before_ip = cl._send_public_request("https://api.ipify.org/")
        cl.set_proxy(proxy)
        after_ip = cl._send_public_request("https://api.ipify.org/")
        print(f"Before: {before_ip}")
        print(f"After: {after_ip}")
        return before_ip!=after_ip

