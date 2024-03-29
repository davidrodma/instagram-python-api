from typing import Dict
from app.modules.profile.services.profile_service import ProfileService
from app.modules.instagram.api.instagrapi.instagrapi_worker import InstagrapiWorker
from app.modules.proxy.services.proxy_service import ProxyService
from app.modules.config.services.config_service import ConfigService
from app.modules.cookie.services.cookie_service import CookieService
from app.modules.instagram.utilities.instagram_utility import InstagramUtility
from app.modules.profile.models.profile import Profile
from app.common.utilities.exception_utility import ExceptionUtility
from app.common.utilities.logging_utility import LoggingUtility
from app.modules.instagram.api.instagrapi.instagrapi_api import InstagrapiApi
from instagrapi import Client
import asyncio

logger = LoggingUtility.get_logger("InstagrapiProfile")

#if TYPE_CHECKING:
#    from app.modules.instagram.api.instagrapi.instagrapi_api import InstagrapiApi

class InstagrapiProfile:
    api = InstagrapiApi()
    profile_service = ProfileService()
    instagrapi_worker = InstagrapiWorker()
    proxy_service = ProxyService()
    config_service = ConfigService()
    cookie_service = CookieService()
    profiles_cl: Dict[str, Client] = {}


    #def __init__(self,api:"InstagrapiApi"):
    #    self.api = api
 

    async def login(self,profile:Profile = None, random_after_error: bool = False, proxy_url:str = ""):
        logged = False
        random = True if profile is None else False
    
        max_attempts = 3
        cl = Client()
     
        while not logged:
            print('LOGIN PROFILE ----------------------------------')
            
            if random:
                try:
                    profile = self.profile_service.get_random_profile()
                except Exception as e:
                    message_error = f'PROFILE LOGIN ERROR random Extract {e}'
                    logger.error(message_error)
                    raise Exception(message_error)
            
            if random_after_error:
                random = True
            if not profile or not hasattr(profile, "username"):
                await asyncio.sleep(2) 
                max_attempts = max_attempts-1
                if max_attempts<0:
                    raise Exception('no profile')
                continue
            proxy = None
            if not proxy_url:
                try:
                    proxy = self.proxy_service.random_proxy(type='extract')
                    proxy_url = proxy.url if proxy else proxy_url
                except Exception as e:
                    pass
            if profile.username in self.profiles_cl:
                cl = self.profiles_cl[profile.username]
                if cl.proxy:
                    if self.proxy_service.is_active(cl.proxy):
                        proxy_url = cl.proxy
                    else:
                        cl.set_proxy("")
            
            if proxy_url:
                logger.warning(f'PROXY: {proxy_url}')
            else:
                logger.warning(f'SEM PROXY')
                allow_only_proxy = int(self.config_service.get_config_value('allow-only-proxy') or '0')
                if allow_only_proxy:
                    error_proxy = ' ! no proxies ! allow-only-proxy config enable!'
                    print(f'{error_proxy}')
                    raise Exception(error_proxy)
            
            logged = True
            if cl and cl.user_id:
                changed = False
                if not cl.proxy and proxy_url:
                    cl.set_proxy(proxy_url)
                    changed = True
                logger.warning(f'{profile.username} JÁ ESTAVA LOGADO ',
                    f'COM {changed if changed else ""} PROXY: {cl.proxy}' if cl.proxy else 'SEM PROXY')
                self.cookie_service.save_state(username=cl.username,state=cl.get_settings(),pk=cl.user_id)
            else:
                print(f'{profile.username} 1º LOGIN')
                try:
                    cl = await self.api.login_custom(
                        username = profile.username,
                        password = profile.password,
                        proxy = proxy_url
                    )
                except Exception as e:
                    logged = False
                    max_attempts -= 1
                    message_error = f"Error Login: {e}"
                    await self.error_login(message_error, profile, proxy_url)
                    if not random or max_attempts <= 0:
                        logged = True
                        print(f'não logar novamente após {max_attempts} ')
                        raise Exception(message_error)
                if logged:    
                    self.profiles_cl[profile.username] = cl
                    self.profile_service.check_count_few_minutes(profile.username)
                    if proxy_url:
                        self.proxy_service.update_count(proxy_url)
                if not logged:
                    logger.warning('sleep no logged')
                    await asyncio.sleep(1) 
        
        print('END LOGIN --------------------------------')
        return cl

    
    async def delete_memory_session(self,username: str):
        try:
            if self.profiles_cl.get(username):
                cl = self.profiles_cl[username]
                self.cookie_service.save_state(username=cl.username,state=cl.get_settings(),pk=cl.user_id)
                del self.profiles_cl[username]
        except Exception as e:
            ExceptionUtility.print_line_error()
            message_error = f'delete_memory_session: {e}'
            logger.error(message_error)
            raise Exception(message_error)
        

    async def error_login(self,message_error: str, profile: Profile, proxy_url: str = None):
        message_error = f"LOGIN ERROR: {message_error.lower()} username {profile.username} proxy {proxy_url}"
        logger.error(message_error)
        
        if InstagramUtility.is_error_prevent_login(message_error):
            if '429' in message_error or 'wait a few minutes' in message_error:
                profile = self.profile_service.check_count_few_minutes(profile.username, f"login error: {message_error}", True)
                if hasattr(profile,'username') and not profile.status:
                    self.delete_memory_session(profile.username)
            else:
                self.profile_service.disable(profile.username, f"login disable error: {message_error}")
                await self.delete_memory_session(profile.username)
        else:
            if self.proxy_service.is_proxy_error(message_error):
                message_error += f" Falha no Proxy {proxy_url} {message_error} "
                if proxy_url:
                    self.proxy_service.update_count(proxy_url, message_error, 'extract')
            self.profile_service.note_error(profile.username, f"login message error: {message_error}")

    async def error_action(self,cl: Client, message_error: str, type="extract"):
        if type == 'worker':
           return self.instagrapi_worker.error_action(cl,message_error)
        elif type == 'boost':
            raise Exception("Not implement")

        if hasattr(cl, "username"):
            input_login = cl.username
            message_error = f"Error Handling: {message_error} "
            proxy = cl.proxy  or 'proxy não detectado'
            message_error = f"{message_error} username {input_login} proxy {proxy}"
            logger.error(message_error)
        else:
            raise Exception(f"Error Handling: ig.loggedInUser.inputLogin without username {message_error}")

        if ('429' in message_error or
                'wait a few minutes' in message_error or
                self.proxy_service.is_proxy_error(message_error) and cl.proxy):
                self.proxy_service.update_count(cl.proxy, f"errorHandling: {message_error}", 'extract')
        else:
            if InstagramUtility.is_error_session(message_error):
                await self.clean_session(cl.username)
            if InstagramUtility.is_error_prevent_action(message_error):
                self.profile_service.disable(cl.username, f"errorHandling: {message_error}")
                await self.delete_memory_session(cl.username)
            else:
                self.profile_service.note_error(cl.username, f"errorHandling: {message_error}")
        return cl
    
    async def clean_session(self,username: str):
        try:  
            old_session = self.cookie_service.load_state(username); 
            if old_session:
                cl = Client()
                cl.set_settings({})
                if old_session["uuids"]:
                    cl.set_uuids(old_session["uuids"])
                self.cookie_service.save_state(username=cl.username,state=cl.get_settings(),pk=cl.user_id)       
            if self.profiles_cl.get(username):
                del self.profiles_cl[username]
        except Exception as e:
            ExceptionUtility.print_line_error()
            message_error = f'clean_session: {e}'
            logger.error(message_error)
            raise Exception(message_error)
        
    async def seen_stories_action(self,username:str,pk:str,media_id:str,max:int=1):
        try:
            cl = await self.login(random_after_error=True)
            try:
                result = await self.api.seen_stories(cl, username, max, pk, media_id)
                return result
            except Exception as e:
                message_error = f'errorHandling action_seen_stories.seen_stories: {e}'
                self.profile_service.note_error(cl.username, message_error)
        except Exception as e:
            ExceptionUtility.print_line_error()
            message_error = f'action_seen_stories: {e}'
            logger.error(message_error)
            raise Exception(message_error)


