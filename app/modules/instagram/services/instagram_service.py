from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from app.modules.profile.services.profile_service import ProfileService
import logging

logger = logging.getLogger()


class InstagramService:

    def login_custom(self,username:str,password:str,proxy:str='',verification_mode:str='',return_ig_error:bool=False):
        """
        Attempts to login to Instagram using either the provided session information
        or the provided username and password.
        """

        cl = Client()
        try:
            session = cl.load_settings(f"{username}.json")
        except:
            session = None

        if proxy:
            cl.set_proxy(proxy)

        login_via_session = False
        login_via_pw = False

        if session:
            try:
                cl.set_settings(session)
                cl.login(username, password)

                # check if session is valid
                try:
                    cl.get_timeline_feed()
                except LoginRequired:
                    logger.info("Session is invalid, need to login via username and password")

                    old_session = cl.get_settings()

                    # use the same device uuids across logins
                    cl.set_settings({})
                    cl.set_uuids(old_session["uuids"])

                    cl.login(username, password)
                login_via_session = True
                cl.dump_settings(f"{username}.json")
            except Exception as e:
                logger.info("Couldn't login user using session information: %s" % e)

        if not login_via_session:
            try:
                logger.info("Attempting to login via username and password. username: %s" % password)
                if cl.login(username, password):
                    login_via_pw = True
                    cl.dump_settings(f"{username}.json")
            except Exception as e:
                logger.info("Couldn't login user using username and password: %s" % e)

        if not login_via_pw and not login_via_session:
            raise Exception("Couldn't login user with either password or session")
        return cl
    
    def get_user_info(self,cl: Client, username:str = '', pk=''):
        if pk=='':
            try:
                user = cl.user_info_by_username(username)
            except Exception as e:
                message_error = f"getUserInfo->ig.user.usernameInfo {e} user extract: {cl.username} proxy {cl.proxy}"
                logger.info(message_error)
                raise Exception(message_error)
            logger.info(f"Username information received: {username} {user.pk}")
            return user
        
        try:
            user = cl.user_info(pk)
        except Exception as e:
            message_error = f"getUserInfo->ig.user.info  {e} user extract: {cl.username} proxy {cl.proxy}"
            logger.info(message_error)
            raise Exception(message_error)
        
        logger.info("Username information received: %s %s" % user.username,user.pk)
        return user
    
    def user_info_by_username(self,username):
        profile = ProfileService.get_random_profile()
        cl = self.login_custom(profile.username,profile.password)
        return self.get_user_info(cl,username)
    
    def user_info_by_id(self,pk):
        profile = ProfileService.get_random_profile()
        cl = self.login_custom(profile.username,profile.password)
        return self.get_user_info(cl,pk=pk)

    def test_proxy(self,proxy:str):
        cl = Client()
        before_ip = cl._send_public_request("https://api.ipify.org/")
        cl.set_proxy(proxy)
        after_ip = cl._send_public_request("https://api.ipify.org/")
        print(f"Before: {before_ip}")
        print(f"After: {after_ip}")
        return before_ip!=after_ip
        

ig = InstagramService()
print(ig.user_info_by_username("anitta"))
