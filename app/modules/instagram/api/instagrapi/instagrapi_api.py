from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from app.modules.profile.services.profile_service import ProfileService
from app.modules.cookie.services.cookie_service import CookieService
from app.common.utilities.logging_utility import LoggingUtility
from app.modules.instagram.api.instagrapi.instagrapi_challenge import InstagrapiChallenge
from app.modules.instagram.api.instagrapi.instagrapi_profile import InstagrapiProfile
from app.modules.instagram.api.instagrapi.instagrapi_extract import InstagrapiExtract
import asyncio

from flask import Flask
app = Flask(__name__)

logger = LoggingUtility.get_logger("InstagrapiApiService")

class InstagrapiApi:
    cookie_service = CookieService()
    
    def __init__(self):
        self.instagrapi_extract = InstagrapiExtract(self)
        self.instagrapi_profile = InstagrapiProfile(self)

    def login_custom(self,username:str,password:str,proxy:str='',verification_mode:str='',return_ig_error:bool=False):
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
        if session:
            try:
                logger.warning(f'Cookie session state found and kept')
                cl.set_settings(session)
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
                        raise Exception(f"login by login_via_session required {name_challenge} {e}")
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
                cl.set_settings({})
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
            raise Exception(f"ERROR login Couldn't login user with either password or session: {message_error}")
        
        logger.info(f"Logged in {cl.username} { 'via password' if login_via_pw else 'via session'}")
        return cl

    def get_user_info(self,cl: Client, username:str = '', pk=''):
        if not pk:
            try:
                print('username ',cl.username)
                print ('get user info by username', username)
                user = cl.user_info_by_username(username)
            except Exception as e:
                message_error = f"get_user_info->user_info_by_username  {e} user extract: {cl.username} proxy {cl.proxy}"
                logger.error(message_error)
                raise BaseException(message_error)
            return user
        
        try:
            print ('get user info by pk', username)
            user = cl.user_info(pk)
        except Exception as e:
            message_error = f"get_user_info->user_info  {e} user extract: {cl.username} proxy {cl.proxy}"
            logger.error(message_error)
            raise Exception(message_error)
        
        logger.warning("Username information received: %s %s" % user.username,user.pk)
        return user
    
    def get_user_info_by_username(self,username):
        profile = ProfileService.get_random_profile()
        cl = self.login_custom(profile.username,profile.password)
        return self.get_user_info(cl,username)
    
    def get_user_info_by_id(self,pk):
        profile = ProfileService.get_random_profile()
        cl = self.login_custom(profile.username,profile.password)
        return self.get_user_info(cl,pk=pk)
    
    async def user_info(self,username:str):
        try:
            return await self.instagrapi_extract.user_info_extract(username=username)
        except Exception as e:
            raise BaseException(f"instagrapi_api.user_info.user_info_extract: {e}")

    def test_proxy(self,proxy:str):
        cl = Client()
        before_ip = cl._send_public_request("https://api.ipify.org/")
        cl.set_proxy(proxy)
        after_ip = cl._send_public_request("https://api.ipify.org/")
        print(f"Before: {before_ip}")
        print(f"After: {after_ip}")
        return before_ip!=after_ip
    
    def delete_memory_session(self,type:str,username:str):
        if   type == "worker":
            pass
        elif type == "boost":
            pass
        else:
           self.instagrapi_profile.delete_memory_session(username)

