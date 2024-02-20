from typing import Optional, Union, Dict, Any
from app.modules.profile.services.profile_service import ProfileService
from app.modules.proxy.services.proxy_service import ProxyService
from app.modules.config.services.config_service import ConfigService
from app.modules.cookie.services.cookie_service import CookieService
from app.modules.instagram.services.instagrapi_api_service import InstagrapiApiService
from instagrapi import Client
import asyncio

class InstagrapiProfileService:
    service = ProfileService()
    proxy_service = ProxyService()
    config_service = ConfigService()
    cookie_service = CookieService()
    api = InstagrapiApiService()
    profiles_cl: Dict[str, Client]

    @classmethod
    async def login(self,profile: Optional[Dict[str, Union[str, Dict[str, Any]]]] = None, random_after_error: bool = False):
        logged = False
        random = True if profile is None else False
        cl = Client()
 

        proxy_url = profile.get('proxy').get('url') if profile and profile.get('proxy') else ''
        max_attempts = 7
        
        while not logged:
            print('LOGIN PROFILE ----------------------------------\n')
            
            if random:
                try:
                    profile = await self.service.get_random_profile()
                except Exception as e:
                    message_error = f'PROFILE LOGIN ERROR random Extract {str(e)}\n'
                    print(message_error)
                    raise RuntimeError(message_error)
            
            if random_after_error:
                random = True
            
            if not profile or not profile.get('username'):
                await asyncio.sleep(2) 
                continue
            
            proxy = None
            if not proxy_url:
                try:
                    proxy = await self.proxy_service.random_proxy(type='extract')
                    proxy_url = proxy['url'] if proxy else proxy_url
                except Exception as e:
                    pass
            
            if profile['username'] in self.profiles_cl:
                cl = self.profiles_cl[profile['username']]
                if cl.proxy:
                    if await self.proxy_service.is_active(cl.proxy):
                        proxy_url = cl.proxy
                    else:
                        cl.set_proxy("")
            
            if proxy_url:
                print(f'PROXY: {proxy_url}\n')
            else:
                print(f'SEM PROXY' + '\n')
                allow_only_proxy = int(await self.config_service.get_config_value('allow-only-proxy'))
                if allow_only_proxy:
                    error_proxy = ' ! no proxies ! allow-only-proxy confcl enable!'
                    print(f'{error_proxy}\n')
                    raise RuntimeError(error_proxy)
            
            logged = True
            if cl and not cl.get('error'):
                changed = False
                if not cl.proxy and proxy_url:
                    cl.set_proxy(proxy_url)
                    changed = True
                print(f'{profile["username"]} JÁ ESTAVA LOGADO ',
                    f'COM {changed if changed else ""} PROXY: {cl.proxy}' if cl["proxy"] else 'SEM PROXY')
                await self.cookie_service.save_state(username=cl.username,state=cl.get_settings(),pk=cl.user_id)
            else:
                print(f'{profile["username"]} 1º LOGIN')
                cl = await self.api.login_custom({
                    'username': profile['username'],
                    'password': profile['password'],
                    'proxy': proxy_url
                })
                if cl.get('error'):
                    logged = False
                    max_attempts -= 1
                    await self.msg_error_login(cl['error'], profile, proxy_url)
                    if not random or max_attempts <= 0:
                        logged = True
                        print(f'não logar novamente após {max_attempts} ')
                        raise RuntimeError(cl['error'])
                else:
                    self.profiles_cl[profile['username']] = cl
                    await ProfileController.check_count_few_minutes(profile['username'])
                    if proxy_url:
                        await self.proxy_service.update_count(proxy_url)
                if not logged:
                    print('sleep no logged\n')
                    await asyncio.sleep(2) 
        
        print('END LOGIN --------------------------------')
        return cl
