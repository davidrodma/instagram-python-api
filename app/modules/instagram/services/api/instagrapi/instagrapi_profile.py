from typing import Optional, Union, Dict, Any
from app.modules.profile.services.profile_service import ProfileService
from app.modules.proxy.services.proxy_service import ProxyService
from app.modules.config.services.config_service import ConfigService
from app.modules.cookie.services.cookie_service import CookieService
from app.modules.instagram.utilities.instagram_utility import InstagramUtility
from app.modules.profile.models.profile import Profile
from instagrapi import Client
import asyncio
from datetime import datetime

class InstagrapiProfile:
    service = ProfileService()
    proxy_service = ProxyService()
    config_service = ConfigService()
    cookie_service = CookieService()
    profiles_cl: Dict[str, Client] = {}

    def __init__(self,api):
        self.api = api
 

    async def login(self,profile:Profile = None, random_after_error: bool = False, proxy_url:str = ""):
        logged = False
        random = True if profile is None else False
    
        max_attempts = 7
        cl = Client()
     
        while not logged:
            print('LOGIN PROFILE ----------------------------------\n')
            
            if random:
                try:
                    profile = await self.service.get_random_profile()
                except Exception as e:
                    message_error = f'PROFILE LOGIN ERROR random Extract {str(e)}\n'
                    print(message_error)
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
                    proxy = await self.proxy_service.random_proxy(type='extract')
                    proxy_url = proxy['url'] if proxy else proxy_url
                except Exception as e:
                    pass
            if profile.username in self.profiles_cl:
                cl = self.profiles_cl[profile.username]
                if cl.proxy:
                    if await self.proxy_service.is_active(cl.proxy):
                        proxy_url = cl.proxy
                    else:
                        cl.set_proxy("")
            
            if proxy_url:
                print(f'PROXY: {proxy_url}\n')
            else:
                print(f'SEM PROXY' + '\n')
                allow_only_proxy = int(self.config_service.get_config_value('allow-only-proxy') or '0')
                if allow_only_proxy:
                    error_proxy = ' ! no proxies ! allow-only-proxy confcl enable!'
                    print(f'{error_proxy}\n')
                    raise Exception(error_proxy)
            
            logged = True
            if cl and cl.user_id and not hasattr(cl, "error"):
                changed = False
                if not cl.proxy and proxy_url:
                    cl.set_proxy(proxy_url)
                    changed = True
                print(f'{profile.username} JÁ ESTAVA LOGADO ',
                    f'COM {changed if changed else ""} PROXY: {cl.proxy}' if cl.proxy else 'SEM PROXY')
                self.cookie_service.save_state(username=cl.username,state=cl.get_settings(),pk=cl.user_id)
            else:
                print(f'{profile.username} 1º LOGIN')
                try:
                    cl = self.api.login_custom(
                        username = profile.username,
                        password = profile.password,
                        proxy = proxy_url
                    )
                except Exception as e:
                    raise Exception(f"Error Login {e}")
                
                if hasattr(cl, "error"):
                    logged = False
                    max_attempts -= 1
                    await self.error_login(cl.error, profile, proxy_url)
                    if not random or max_attempts <= 0:
                        logged = True
                        print(f'não logar novamente após {max_attempts} ')
                        raise Exception(cl.error)
                else:
                    self.profiles_cl[profile.username] = cl
                    await self.service.check_count_few_minutes(profile.username)
                    if proxy_url:
                        self.proxy_service.update_count(proxy_url)
                if not logged:
                    print('sleep no logged\n')
                    await asyncio.sleep(2) 
        
        print('END LOGIN --------------------------------')
        return cl

    
    async def delete_memory_session(self,username: str):
        try:
            if self.profiles_cl.get(username):
                cl = self.profiles_cl[username]
                await self.cookie_service.save_state(username=cl.username,state=cl.get_settings(),pk=cl.user_id)
                del self.profiles_cl[username]
        except Exception as e:
            print('disable', e)
            raise Exception(f'disable: {e}')
        

    async def error_login(self,message_error: str, profile: dict, proxy_url: str = None):
        message_error = f"{message_error.lower()} username {profile.username} proxy {proxy_url}"
        print(f"LOGIN ERROR: username: {profile.username}, proxy: {proxy_url}, msg: {message_error}\n")
        
        if InstagramUtility.is_error_prevent_login(message_error):
            if '429' in message_error or 'wait a few minutes' in message_error:
                await self.service.check_count_few_minutes(profile.username, f"login error: {message_error}", True)
            else:
                await self.disable(profile.username, f"login disable error: {message_error}")
        else:
            if self.proxy_service.is_proxy_error(message_error):
                message_error += f" Falha no Proxy {proxy_url} {message_error} "
                if proxy_url:
                    self.proxy_service.update_count(proxy_url, message_error, 'extract')
            await self.service.note_error(profile.username, f"login message error: {message_error}")

    async def error_handling(self,cl: Client, message_error: str, type="extract"):
        if type == 'worker':
           raise Exception("Not implement")
        elif type == 'boost':
            raise Exception("Not implement")

        if hasattr(cl, "username"):
            input_login = cl.username
            print(f"Error Handling: {input_login} {message_error}\n")
            proxy = cl.proxy  or 'proxy não detectado'
            message_error = f"{message_error} username {input_login} proxy {proxy}"
        else:
            raise Exception(f"Error Handling: ig.loggedInUser.inputLogin without username {message_error}\n")

        if ('429' in message_error or
                'wait a few minutes' in message_error or
                self.proxy_service.is_proxy_error(message_error) and cl.proxy):
            self.proxy_service.update_count(cl.proxy, f"errorHandling: {message_error}", 'extract')
        else:
            if InstagramUtility.is_error_session(message_error):
                await self.clean_session(cl.username)
            if InstagramUtility.is_error_prevent_action(message_error):
                await self.disable(cl.username, f"errorHandling: {message_error}")
            else:
                await self.service.note_error(cl.username, f"errorHandling: {message_error}")
        return cl
    
    async def clean_session(self,username: str):
        try:  
            old_session = self.cookie_service.load_state(username); 
            if old_session:
                cl = Client()
                cl.set_settings({})
                if old_session["uuids"]:
                    cl.set_uuids(old_session["uuids"])
                await self.cookie_service.save_state(username=cl.username,state=cl.get_settings(),pk=cl.user_id)       
            if self.profiles_cl.get(username):
                del self.profiles_cl[username]
        except Exception as e:
            print('clean_session', e)
            raise f'clean_session: {e}'
        

    async def disable(self,username: str, reason: str = ''):
        try:
            print('disable', username)
            date = datetime.utcnow()
            update = {
                'status': 0,
                'disabledAt': date,
                'pausedAtFollower': date,
                'pausedAtLike': date,
                'pausedAtComment': date
            }
            if reason:
                expire_at = InstagramUtility.get_expire_at(reason)
                update.update({
                    'noteError': reason,
                    'expireAt': expire_at,
                    '$inc': {'countError': 1}
                })
            self.delete_memory_session(username)
            return await self.service.update_many({'username': username}, update)
        except Exception as e:
            print('disable', e)
            raise f'disable: {e}'
        





    

    
