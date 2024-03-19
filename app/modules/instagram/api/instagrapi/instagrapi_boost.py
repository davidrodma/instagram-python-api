from typing import Dict,Literal
from app.modules.boost.services.boost_service import BoostService
from app.modules.proxy.services.proxy_service import ProxyService
from app.modules.proxy.models.proxy import Proxy
from app.modules.config.services.config_service import ConfigService
from app.modules.cookie.services.cookie_service import CookieService
from app.modules.instagram.utilities.instagram_utility import InstagramUtility
from app.modules.boost.models.boost import Boost
from app.common.utilities.cryptography import Cryptography
from app.common.utilities.exception_utility import ExceptionUtility
from app.common.utilities.logging_utility import LoggingUtility
from app.modules.instagram.api.instagrapi.instagrapi_api import InstagrapiApi
from app.modules.instagram.api.instagrapi.instagrapi_challenge import InstagrapiChallenge
from instagrapi import Client

logger = LoggingUtility.get_logger("InstagrapiBoost")

#if TYPE_CHECKING:
#    from app.modules.instagram.api.instagrapi.instagrapi_api import InstagrapiApi

class InstagrapiBoost:
    api = InstagrapiApi()
    boost_service = BoostService()
    proxy_service = ProxyService()
    config_service = ConfigService()
    cookie_service = CookieService()
    boosts_cl: Dict[str, Client] = {}


    #def __init__(self,api:"InstagrapiApi"):
    #    self.api = api
    
    async def login(self,boost: Boost):
        print(f'LOGIN BOOST {boost.username} -----------------------------------')
        proxy_url = boost.proxy
        cl:Client = None

        if boost.username in self.boosts_cl:
            cl = self.boosts_cl[boost.username]
            if cl.proxy:
                if self.proxy_service.is_active(cl.proxy):
                    proxy_url = cl.proxy
                else:
                    if self.proxy_service.is_buy_proxy(cl.proxy):
                        message_error = f'login_by_boost.is_buy_proxy perfil desativado porque o proxy {cl.proxy} estava OFF'
                        self.boost_service.disable(boost.username, f"login disable error: {message_error}")
                        raise Exception(message_error)

                    if boost.proxy and boost.proxy != 'random':
                        boost.proxy = 'random'
                        proxy_url = ''
                        cl.set_proxy('')
        elif boost.proxy and boost.proxy != 'random':
            if self.proxy_service.is_active(boost.proxy):
                proxy_url = boost.proxy
            else:
                if self.proxy_service.is_buy_proxy(cl.proxy):
                    message_error = f'login_by_boost.is_buy_proxy perfil desativado porque o proxy {cl.proxy} estava OFF'
                    self.boost_service.disable(boost.username, f"login disable error: {message_error}")
                    raise Exception(message_error)

                boost.proxy = 'random'
                self.boost_service.update_by_id(boost._id,{"proxy":boost.proxy})
        proxy:Proxy = None
        if boost.proxy == 'random' or not proxy_url:
            try:
                proxy = self.proxy_service.random_proxy({
                    'type': 'boost',
                    'countryCode': boost.nationality,
                })
            except Exception as e:
                message_error = f"boostapi.follower.random_proxy {e}"
                logger.warning(message_error)

            proxy_url = proxy.url if proxy and proxy.url else ''

            if boost.proxy == 'random' and proxy_url:
                boost.proxy = proxy_url
                self.boost_service.update_by_id(boost._id,{"proxy":boost.proxy})

        if proxy_url:
            logger.warning(f"PROXY: {proxy_url}")
        else:
            logger.warning(f"SEM PROXY")
            allow_only_proxy = int(self.config_service.get_config_value('allow-only-proxy') or '0')
            if allow_only_proxy:
                error_proxy = ' ! no proxies ! allow-only-proxy config enable!'
                logger.error(error_proxy)
                raise Exception(error_proxy)

        if cl:
            if not cl.proxy and proxy_url:
                cl.set_proxy(proxy_url)
           

            logger.warning(f"{boost.username} JÁ ESTAVA LOGADO ")
            logger.warning(f"COM PROXY: {cl.proxy}" if cl.proxy else "SEM PROXY")
            self.cookie_service.save_state(username=cl.username,state=cl.get_settings(),pk=cl.user_id)

        else:
            print(f'{boost.username} 1º LOGIN')
            try:
                cl = await self.api.login_custom(
                    username = boost.username,
                    password = boost.password,
                    proxy = proxy_url
                )
            except Exception as e:
                message_error = f"Error boostapi.login.login_custom: {e}"
                await self.error_login(message_error, boost, proxy_url)
                #await RecoverChallengeController.check_auto_recover(boost, ig['error'])
                raise Exception(message_error)
        
        cl = await self.change_proxy(cl, 'boost-action', boost)
        self.boosts_cl[boost.username] = cl
        self.boost_service.check_count_few_minutes(boost.username)

        print(f'END LOGIN BOOST {boost.username}  --------------------------------')
        return cl
    

    async def first_login_boost(self,username:str,password:str,proxy:str='',countryCode:str=''):
        cl:Client = None
        try:
            if not username or not password:
                raise Exception('Username and password are required')

            proxy_url = proxy if proxy and proxy != 'random' else None
            if proxy and proxy != 'random':
                if self.proxy_service.is_active(proxy):
                    proxy_url = proxy
                else:
                    proxy = 'random'

            loop = True
            attempts = 0
            while loop:
                loop = False
                logger.warning(f'LOGIN BOOST ATTEMPT: {attempts + 1} -----------------------------------')

                if proxy == 'random':
                    proxy_data = self.proxy_service.random_proxy(type='boost',countryCode=countryCode)
                    if proxy_data:
                        proxy_url = proxy_data.url

                if proxy_url:
                    logger.warning(f'PROXY: {proxy_url}')
                else:
                    logger.warning('NO PROXY')
                    allow_only_proxy = int(self.config_service.get_config_value('allow-only-proxy') or '0')
                    if allow_only_proxy:
                        raise Exception('No proxies available, allow-only-proxy config enabled')

                try:
                    logger.warning(f'{username} 1st LOGIN Boost')
                    cl = await self.api.login_custom(
                        username=username,
                        password=password,
                        proxy=proxy_url
                    )
                except Exception as e:
                    message_error = f"boost.first_login_boost.login_custom: {e}"
                    msg = await self.error_first_login_to_user(message_error)
                    attempts += 1
                    if msg.get('attempt') and attempts < 3:
                        loop = True
                    if loop:
                        proxy = 'random'
                    else:
                        return cl,msg
                            
            cl = await self.change_proxy(cl, 'boost-action')
            self.boosts_cl[username] = cl
            logger.warning('END LOGIN --------------------------------')
            return cl,''

        except Exception as e:
            return {'error': str(e)}
    
    async def save(self,
             username:str,
             password:str,
             accountId:str,
             socialId:str,
             proxy:str="random",
             status=1,
             countryCode=""
        ):
        cl:Client = None
        boost:Boost = None
        try:
            if password:
                try:
                    cl,error = await self.first_login_boost(
                        username = username,
                        password=password,
                        proxy=proxy,
                        countryCode=countryCode
                    )
                    if error:
                        return error
                except Exception as e:
                    message_error = "api.boost.save.first_login_boost"
                    raise Exception(message_error)
                if cl.proxy:
                    proxy = cl.proxy
                    
            boost = self.boost_service.find_one({"accountId":accountId})
            
            if not boost:
                params = {
                    "username":username,
                    "accountId":accountId,
                    "socialId":socialId,
                    "proxy":proxy,
                    "countryCode":countryCode,
                    "status":status,
                    "countCurrent":0,
                    "countSuccess":0,
                    "countFewMinutes":0,
                    "countError":0,
                    "countChallenge":0,
                    "countCurrentFollower":0,
                    "countCurrentLike":0,
                    "disabledAt":None,
                }
                if password:
                    params["password"] = Cryptography.encrypt(password)
                    params["noteError"] = 'ATIVADO manualmente pelo usuário'
        
                id = self.boost_service.create(params)
                boost = self.boost_service.find_by_id(id)
            else:
                params = {
                    "username":username,
                    "socialId":socialId,
                    "proxy":proxy,
                    "countryCode":countryCode,
                    "status": status
                }
                if password:
                    params['password'] = Cryptography.encrypt(password)
                    params['noteError'] = 'ATIVADO manualmente pelo usuário'
                    if boost.noteErrorBefore and InstagramUtility.is_blocked(boost.noteErrorBefore):
                        params['countUnblocked'] = boost.countUnblocked +1
                 
                self.boost_service.find_one_and_update({"_id":boost._id},params)

            return boost

        except Exception as e:
            ExceptionUtility.print_line_error()
            message_error = f"ERROR save boot: {e}"
            logger.error(message_error)
            return {'error': message_error}
                                                                  
    async def change_proxy(self,cl: Client, type: str, obj_account: Boost = None) -> Client:
        try:
            change_proxy_action = int(self.config_service.get_config_value('change-proxy-action') or '0')
            if change_proxy_action:
                proxy = self.proxy_service.random_proxy({
                    'type': type
                })
                proxy_url = proxy.url if proxy else None
                if not proxy_url:
                    allow_only_proxy = int(self.config_service.get_config_value('allow-only-proxy') or '0')
                    if allow_only_proxy:
                        error_proxy = ' ! no proxies ! allow-only-proxy config enable!'
                        print(f'{error_proxy}')
                        raise Exception(error_proxy)
                    if obj_account:
                        obj_account.proxy = proxy_url
                        self.boost_service.update_by_id(obj_account._id,{"proxy":obj_account.proxy})
            return cl
        except Exception as e:
            raise Exception(f'changeProxy: {e}')

    async def delete_memory_session(self,username: str):
        try:
            if self.boosts_cl.get(username):
                cl = self.boosts_cl[username]
                self.cookie_service.save_state(username=cl.username,state=cl.get_settings(),pk=cl.user_id)
                del self.boosts_cl[username]
        except Exception as e:
            ExceptionUtility.print_line_error()
            message_error = f'delete_memory_session: {e}'
            logger.error(message_error)
            raise Exception(message_error)

    async def error_login(self,message_error: str, boost: Boost, proxy_url: str = '') -> None:
        message_error = f"LOGIN ERROR: {message_error.lower()} username {boost.username} proxy {proxy_url}"
        logger.error(message_error)
        if InstagramUtility.is_error_prevent_login(message_error) or self.proxy_service.is_proxy_error(message_error):
            if self.proxy_service.is_proxy_error(message_error):
                message_error += f' Falha no Proxy {proxy_url} {message_error} '
                self.proxy_service.update_count(proxy_url, message_error, 'boost')
                self.boost_service.note_error(boost.username, f"login message error: {message_error}")
            elif ' 429 ' in message_error or 'wait a few minutes' in message_error:
                boost = self.boost_service.check_count_few_minutes(boost.username, f"login error: {message_error}", True)
            elif ('challenge' in message_error or 'checkpoint' in message_error) and 'unimplemented' not in message_error.lower():
                 self.boost_service.check_count_challenge(boost.username, 'login error: ' + message_error, True)
            else:
                self.boost_service.disable(boost.username, f"login disable error: {message_error}")
        else:
            self.boost_service.note_error(boost.username, f"login message error: {message_error}")


    async def error_first_login_to_user(self,message_error: str) -> Dict:
        message_error = message_error.lower()

        if ' 429 ' in message_error or 'wait a few minutes' in message_error or self.proxy_service.is_proxy_error(message_error):
            return {
                'error': message_error,
                'attempt': True,
                'message_user': 'Infelizmente não foi possível associar o perfil neste momento, tente novamente após algumas horas.'
            }
        elif 'challenge' in message_error or 'checkpoint' in message_error:
            return {
                'error': message_error,
                'message_user': 'Não foi possível associar este perfil no momento. Acesse ele no aplicativo no Instagram, confira se há algum bloqueio, se houver resolva e tente associar novamente.'
            }
        elif 'username you entered' in message_error:
            return {
                'error': message_error,
                'check_social_id': True,
                'attempt': True,
                'message_user': 'O username informado parece não existir no Instagram. Confira atentamente se não digitou algum caractere errado.'
            }
        elif 'been disabled' in message_error or 'account was disabled' in message_error \
                or 'you requested to delete' in message_error or 'not found' in message_error \
                or 'account details were deleted' in message_error:
            return {
                'error': message_error,
                'check_social_id': True,
                'message_user': 'O username informado parece não existir no Instagram. Abra o aplicativo e verifique se consegue logar, depois tente associá-lo novamente aqui.'
            }
        elif 'password' in message_error:
            return {
                'error': message_error,
                'attempt': True,
                'message_user': 'A senha informada parece não estar correta. Por favor, confira e insira novamente.'
            }
        else:
            return {
                'error': message_error,
                'message_user': 'Não foi possível associar o perfil neste momento. Verifique consegue entrar normalmente no aplicativo do Instagram, e tente associá-lo novamente mais tarde aqui.'
            }
        
    async def error_action(self,cl: Client, message_error: str):
        message_error = 'errorHandling: ' + message_error
        if cl.username:
            logger.error(f"Error Handling: {cl.username} {message_error}")
            proxy = cl.proxy or 'proxy não detectado'
            message_error = f"{message_error} username {cl.username} proxy {proxy}"
        else:
            raise Exception(f"Error Handling cl.username without username: {message_error}")
        boost = self.boost_service.get_by_username(cl.username)
        try:
            cl.get_timeline_feed()
        except Exception as e:
            message_error += f" detected {InstagrapiChallenge.detect_name_challenge(e)} "
        if ('429' in message_error or 'wait a few minutes' in message_error or self.proxy_service.is_proxy_error(message_error)) and cl.proxy:
            if boost and ('429' in message_error or 'wait a few minutes' in message_error):
                self.boost_service.check_count_few_minutes(boost.username, message_error, True)
            self.proxy_service.update_count(cl.proxy, 'errorHandling: ' + message_error, 'boost')
        else:
            if InstagramUtility.is_error_session(message_error):
                await self.clean_session(boost, True)
            if InstagramUtility.is_error_prevent_action(message_error):
                if ('challenge' in message_error or 'checkpoint' in message_error) and 'unimplemented' not in message_error.lower():
                    self.boost_service.check_count_challenge(cl.username, message_error, True)
                else:
                    self.boost_service.disable(cl.username, message_error)
            else:
                self.boost_service.note_error(cl.username, message_error)
        return message_error

    
    async def clean_session(self,username: str):
        try:  
            old_session = self.cookie_service.load_state(username); 
            if old_session:
                cl = Client()
                cl.set_settings({})
                if old_session["uuids"]:
                    cl.set_uuids(old_session["uuids"])
                self.cookie_service.save_state(username=cl.username,state=cl.get_settings(),pk=cl.user_id)       
            if self.boosts_cl.get(username):
                print(f"DELETE cookies username {username}")
                del self.boosts_cl[username]
        except Exception as e:
            ExceptionUtility.print_line_error()
            message_error = f'clean_session: {e}'
            logger.error(message_error)
            raise Exception(message_error)
        
    async def follower_action(self,username_action:str,username_target:str='',id_target:str=''):
        error_link = False
        is_follower = False
        already_exists = False
        boost:Boost = None
        max_limit = False
        is_action = False
        try:

            if not username_action:
                raise Exception('username action required!')

            if not username_target and not id_target:
                raise Exception('username_target or id_target required!')

            boost = self.boost_service.get_by_username(username_action)
            if not boost or not int(boost.status):
                raise Exception(f"Usuário {username_action} já foi desativado: {boost.noteError}")

            cl = await self.login(boost)

            if not id_target:
                try:
                    info_target = await self.api.get_user_info(cl, username_target, id_target)
                except Exception as e:
                    message_error = f"ERRO boost.follower_action.get_user_info: erro quando o usuário da ação de seguir for pegar dos dados do alvo {e}"
                    if 'not found' in message_error:
                        error_link = True
                    is_action = True
                    raise Exception(message_error)
                
                if not info_target or not info_target.pk:
                    error_link = True
                    raise Exception('username target não encontrado')

                if info_target.is_private:
                    message_error = f"boost private: {info_target.username}"
                    logger.error(message_error)
                    return {
                        'error': message_error,
                        'id_target': info_target.pk,
                        'username_target': info_target.username,
                        'is_private': True,
                    }

                id_target = info_target.pk

            logger.warning(f"{cl.username} will follow: {id_target}")

            try:
                is_follower = await self.api.follow_by_id(cl, id_target)
            except Exception as e:
                is_action = True
                message_error = f'ERRO boost.follower_action.follow_by_id: followerAction->followById username {boost.username} proxy {cl.proxy}: {e}'
                if 'following the max limit' in message_error:
                    max_limit = True
                if 'not found' in message_error:
                        error_link = True
                raise Exception(message_error)

           
            if not is_follower:
                message_error = f'not follow maybe already_followed'
                logger.error(message_error)
                self.boost_service.note_error(cl.username,message_error)
                already_exists = True

            self.boost_service.update_count(cl.username, 1, 'follower', is_follower)

            return {
                'username_action': username_action,
                'username_target': username_target,
                'is_follower': is_follower,
                'id_target': id_target,
                'already_exists': already_exists,
                'boost': {
                    '_id': boost._id,
                    'username': boost.username,
                    'status': boost.status,
                    'noteError': boost.noteError,
                },
            }
        except Exception as e:
            message_error = f"ERROR: {e}"
            logger.error(message_error)
            ExceptionUtility.print_line_error()
            self.error_action(cl,message_error) if is_action and cl and cl.username else self.boost_service.note_error(username_action,message_error)
            boost = self.boost_service.get_by_username(username_action) if username_action else None
            return {
                'error': message_error,
                'error_link': error_link,
                'max_limit':max_limit,
                'boost': {
                    '_id': boost._id if boost else '',
                    'username': boost.username if boost else username_action,
                    'status': boost.status if boost else 0,
                    'noteError': boost.noteError if boost else '',
                },
            }
        

    async def like_action(self,username_action:str,url_target:str='',id_target:str=''):
        error_link = False
        is_liker = False
        boost:Boost = None
        info_target = None
        already_exists = False
        is_action = False
        try:
            if not username_action:
                raise Exception('username action required!')
            if not url_target and not id_target:
                raise Exception('url_target or id_target required!')

            boost = self.boost_service.get_by_username(username_action)
            if not boost or not int(boost.status):
                raise Exception(f"Usuário {username_action} já foi desativado: {boost.noteError}")

            cl = await self.login(boost)

            if not id_target:
                try: 
                    info_target = await self.api.get_media_url_info(cl, url_target)
                except Exception as e:
                    message_error = f"ERRO boost.like_action.get_media_url_info: erro quando o usuário da ação de de curtir for pegar dos dados do alvo {e}"
                    if 'not found' in message_error:
                        error_link = True
                    is_action = True
                    raise Exception(message_error)
                
                if not info_target or not info_target.pk:
                    error_link = True
                    raise Exception('post/media target não encontrado')

                id_target = info_target.pk

            logger.warning(f"{cl.username} will like: {id_target}")

            try:
                is_liker = await self.api.like_media(cl,id_target)
            except Exception as e:
                is_action = True
                message_error = f'ERRO boost.like_action.like_media: likeAction->likeMediaId  username {boost.username} proxy {cl.proxy}: {e}'
                if 'not found' in message_error:
                    error_link = True
                raise Exception(message_error)
            
            if not is_liker:
                message_error = f'not liker maybe already_liked'
                logger.error(message_error)
                self.boost_service.note_error(cl.username,message_error)
                already_exists = True

            self.boost_service.update_count(cl.username, 1, 'like', is_liker)

            return {
                'username_action': username_action,
                'url_target': url_target,
                'is_liker': is_liker,
                'id_target': id_target,
                'already_exists': already_exists,
                'boost': {
                    '_id': boost._id,
                    'username': boost.username,
                    'status': boost.status,
                    'noteError': boost.noteError,
                },
            }
        except Exception as e:
            message_error = f"ERROR: {e}"
            logger.error(message_error)
            ExceptionUtility.print_line_error()
            self.error_action(cl,message_error) if is_action and cl and cl.username else self.boost_service.note_error(username_action,message_error)
            boost = self.boost_service.get_by_username(username_action) if username_action else None
            return {
                'error': message_error,
                'error_link': error_link,
                'boost': {
                    '_id': boost._id if boost else '',
                    'username': boost.username if boost else username_action,
                    'status': boost.status if boost else 0,
                    'noteError': boost.noteError if boost else '',
                },
            }
        
    async def comment_action(self,username_action:str,text:str,url_target:str='',id_target:str=''):
        error_link = False
        is_comment = False
        boost:Boost = None
        info_target = None
        already_exists = False
        is_action = False
        try:
            if not username_action:
                raise Exception('username action required!')
            if not url_target and not id_target:
                raise Exception('url_target or id_target required!')
            if not text:
                raise Exception('text required!')

            boost = self.boost_service.get_by_username(username_action)
            if not boost or not int(boost.status):
                raise Exception(f"Usuário {username_action} já foi desativado: {boost.noteError}")

            cl = await self.login(boost)

            if not id_target:
                try: 
                    info_target = await self.api.get_media_url_info(cl, url_target)
                except Exception as e:
                    message_error = f"ERRO boost.comment_action.get_media_url_info: erro quando o usuário da ação de comentar for pegar dos dados do alvo {e}"
                    if 'not found' in message_error:
                        error_link = True
                    is_action = True
                    raise Exception(message_error)
                
                if not info_target or not info_target.pk:
                    error_link = True
                    raise Exception('post/media target não encontrado')

                id_target = info_target.pk

            logger.warning(f"{cl.username} will comment: {id_target}")

            
            try:
               is_comment, comment = await self.api.comment_media(cl=cl,text=text, media_id=id_target,url=url_target)
               text = comment.text if comment and hasattr(comment,'text') else text
            except Exception as e:
                is_action = True
                message_error = f'ERRO boost.comment_action.comment_media: commentAction->commentMedia  username {boost.username} proxy {cl.proxy}: {e}'
                if 'not found' in message_error:
                    error_link = True
                raise Exception(message_error)
            
            if not is_comment:
                message_error = f'not comment'
                logger.error(message_error)
                self.boost_service.note_error(cl.username,message_error)
                already_exists = True

            self.boost_service.update_count(cl.username, 1, 'comment', is_comment)

            return {
                'username_action': username_action,
                'url_target': url_target,
                'is_comment': is_comment,
                'id_target': id_target,
                'already_exists': already_exists,
                "text": text,
                'boost': {
                    '_id': boost._id,
                    'username': boost.username,
                    'status': boost.status,
                    'noteError': boost.noteError,
                },
            }
        except Exception as e:
            message_error = f"ERROR: {e}"
            logger.error(message_error)
            ExceptionUtility.print_line_error()
            self.error_action(cl,message_error) if is_action and cl and cl.username else self.boost_service.note_error(username_action,message_error)
            boost = self.boost_service.get_by_username(username_action) if username_action else None
            return {
                'error': message_error,
                'error_link': error_link,
                'boost': {
                    '_id': boost._id if boost else '',
                    'username': boost.username if boost else username_action,
                    'status': boost.status if boost else 0,
                    'noteError': boost.noteError if boost else '',
                },
            }

    async def story_action(self,username_action:str,username_target:str='',id_target:str='',media_id:str='',max=10):
        error_link = False
        is_story = False
        boost:Boost = None
        is_action = False
        result = {}
        try:

            if not username_action:
                raise Exception('username action required!')
            if not username_target and not id_target:
                raise Exception('username_target or id_target required!')

            boost = self.boost_service.get_by_username(username_action)
            if not boost or not int(boost.status):
                raise Exception(f"Usuário {username_action} já foi desativado: {boost.noteError}")

            cl = await self.login(boost)

            if not id_target:
                try:
                    info_target = await self.api.get_user_info(cl, username_target, id_target)
                except Exception as e:
                    message_error = f"ERRO boost.story_action.get_user_info: erro quando o usuário da ação de ver stories for pegar dos dados do alvo {e}"
                    is_action = True
                    raise Exception(message_error)
                
                if not info_target or not info_target.pk:
                    error_link = True
                    raise Exception('username target não encontrado')

                if info_target.is_private:
                    message_error = f"boost private: {info_target.username}"
                    logger.error(message_error)
                    return {
                        'error': message_error,
                        'id_target': info_target.pk,
                        'username_target': info_target.username,
                        'is_private': True
                    }

                id_target = info_target.pk

            logger.warning(f"{cl.username} will seen stories: {id_target}")

            try:
                result = await self.api.seen_stories(cl=cl, username=username_target,pk=id_target,media_id=media_id,max=max)
                is_story = result.get('success')
            except Exception as e:
                is_action = True
                message_error = f'ERRO boost.story_action.seen_stories: storyAction->seenStories username {boost.username} proxy {cl.proxy}: {e}'
                raise Exception(message_error)

            if not is_story and result.get('count')<=0:
                error_link = True
                return {
                    'error': 'stories não existe ou não estão mais disponíveis',
                    'error_link': error_link,
                    'username': cl.username,
                }
            
            self.boost_service.update_count(cl.username, 1, 'story', is_story)
        
            return {
                'username_action': username_action,
                'username_target': username_target,
                'is_story': is_story,
                'id_target': id_target,
                'boost': {
                    '_id': boost._id,
                    'username': boost.username,
                    'status': boost.status,
                    'noteError': boost.noteError,
                },
            }
        except Exception as e:
            message_error = f"ERROR: {e}"
            logger.error(message_error)
            ExceptionUtility.print_line_error()
            self.error_action(cl,message_error) if is_action and cl and cl.username else self.boost_service.note_error(username_action,message_error)
            boost = self.boost_service.get_by_username(username_action) if username_action else None
            return {
                'error': message_error,
                'error_link': error_link,
                'boost': {
                    '_id': boost._id if boost else '',
                    'username': boost.username if boost else username_action,
                    'status': boost.status if boost else 0,
                    'noteError': boost.noteError if boost else '',
                },
            }
        
    async def like_comment_action( self,
        username_action:str,
        comment_id:str='',
        username_comment:str='',
        url_target:str='',
        id_target:str='',
        user_id_comment:str='',
        max:int=100):

        cl:Client = None
        error_link = False
        is_liker = False
        boost:Boost = None
        info_target = None
        text = ''
        is_action = False
        try:

            if not username_action:
                raise Exception('boost.like_comment_action username_action required!')
            if not url_target and  not id_target and not comment_id:
                raise Exception('like_comment_action url_target or id_target or comment_id required!')

            boost = self.boost_service.get_by_username(username_action)
            if not boost or not int(boost.status):
                raise Exception(f"Usuário {username_action} já foi desativado: {boost.noteError}")

            cl = await self.login(boost)

            if not id_target and not comment_id:
                    try:
                        info_target = await self.api.get_media_url_info(cl, url_target)
                        id_target = info_target.pk
                    except Exception as e:
                        message_error = f"ERRO boost.like_comment_action.get_media_url_info: erro quando o usuário da ação de curtir comentário for pegar dos dados do alvo {e}"
                        if 'not found' in message_error:
                            error_link = True
                        is_action = True
                        raise Exception(message_error)

            if not comment_id:
                image_action, comments, is_comment, username_comment = await self.api.find_user_in_comments(cl=cl, pk=id_target, max=max,username_comment=username_comment,user_id_comment=user_id_comment)
                if is_comment:
                    comment_id = comments[0]['comment_id']
                    text = comments[0]['text']
            if not comment_id:
                raise Exception('boost.like_comment_action.find_user_in_comments username do comentário não encontrado')
                
            logger.warning(f"{cl.username} will like comment: {id_target}")
            try:
                is_liker = await self.api.like_comment_by_id(cl,comment_id)
            except Exception as e:
                is_action = True
                message_error = f'ERRO boost.like_comment_action.like_comment_by_id username {boost.username} proxy {cl.proxy}: {e}'
                raise Exception(message_error)

            self.boost_service.update_count(cl.username, 1, 'like', is_liker)

            return {
                'username_action': username_action,
                'url_target': url_target,
                'is_liker': is_liker,
                'id_target': id_target,
                'comment_id': comment_id,
                'text': text,
                'boost': {
                    '_id': boost._id,
                    'username': boost.username,
                    'status': boost.status,
                    'noteError': boost.noteError,
                },
            }
        except Exception as e:
            message_error = f"ERROR: {e}"
            logger.error(message_error)
            ExceptionUtility.print_line_error()
            self.error_action(cl,message_error) if is_action and cl and cl.username else self.boost_service.note_error(username_action,message_error)
            boost = self.boost_service.get_by_username(username_action) if username_action else None
            return {
                'error': message_error,
                'error_link': error_link,
                'boost': {
                    '_id': boost._id if boost else '',
                    'username': boost.username if boost else username_action,
                    'status': boost.status if boost else 0,
                    'noteError': boost.noteError if boost else '',
                },
            }
        
