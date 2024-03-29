from typing import Dict,Literal
from app.modules.worker.services.worker_service import WorkerService
from app.modules.proxy.services.proxy_service import ProxyService
from app.modules.proxy.models.proxy import Proxy
from app.modules.config.services.config_service import ConfigService
from app.modules.cookie.services.cookie_service import CookieService
from app.modules.instagram.utilities.instagram_utility import InstagramUtility
from app.modules.worker.models.worker import Worker
from app.common.utilities.exception_utility import ExceptionUtility
from app.common.utilities.logging_utility import LoggingUtility
from app.modules.instagram.api.instagrapi.instagrapi_api import InstagrapiApi
from app.modules.instagram.api.instagrapi.instagrapi_challenge import InstagrapiChallenge
from app.common.utilities.image_utility import ImageUtility
from instagrapi import Client

logger = LoggingUtility.get_logger("InstagrapiWorker")

#if TYPE_CHECKING:
#    from app.modules.instagram.api.instagrapi.instagrapi_api import InstagrapiApi

class InstagrapiWorker:
    api = InstagrapiApi()
    worker_service = WorkerService()
    proxy_service = ProxyService()
    config_service = ConfigService()
    cookie_service = CookieService()
    workers_cl: Dict[str, Client] = {}


    #def __init__(self,api:"InstagrapiApi"):
    #    self.api = api
    
    async def login(self,worker: Worker):
        print(f'LOGIN WORKER {worker.username} -----------------------------------')
        proxy_url = worker.proxy
        cl:Client = None

        if worker.username in self.workers_cl:
            cl = self.workers_cl[worker.username]
            if cl.proxy:
                if self.proxy_service.is_active(cl.proxy):
                    proxy_url = cl.proxy
                else:
                    if self.proxy_service.is_buy_proxy(cl.proxy):
                        message_error = f'login_by_worker.is_buy_proxy perfil desativado porque o proxy {cl.proxy} estava OFF'
                        self.worker_service.disable(worker.username, f"login disable error: {message_error}")
                        raise Exception(message_error)

                    if worker.proxy and worker.proxy != 'random':
                        worker.proxy = 'random'
                        proxy_url = ''
                        cl.set_proxy('')
        elif worker.proxy and worker.proxy != 'random':
            if self.proxy_service.is_active(worker.proxy):
                proxy_url = worker.proxy
            else:
                if self.proxy_service.is_buy_proxy(cl.proxy):
                    message_error = f'login_by_worker.is_buy_proxy perfil desativado porque o proxy {cl.proxy} estava OFF'
                    self.worker_service.disable(worker.username, f"login disable error: {message_error}")
                    raise Exception(message_error)

                worker.proxy = 'random'
                self.worker_service.update_by_id(worker._id,{"proxy":worker.proxy})
        proxy:Proxy = None
        if worker.proxy == 'random' or not proxy_url:
            try:
                proxy = self.proxy_service.random_proxy({
                    'type': 'worker',
                    'countryCode': worker.nationality,
                })
            except Exception as e:
                message_error = f"workerapi.follower.random_proxy {e}"
                logger.warning(message_error)

            proxy_url = proxy.url if proxy and proxy.url else ''

            if worker.proxy == 'random' and proxy_url:
                worker.proxy = proxy_url
                self.worker_service.update_by_id(worker._id,{"proxy":worker.proxy})

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
           

            logger.warning(f"{worker.username} JÁ ESTAVA LOGADO ")
            logger.warning(f"COM PROXY: {cl.proxy}" if cl.proxy else "SEM PROXY")
            self.cookie_service.save_state(username=cl.username,state=cl.get_settings(),pk=cl.user_id)

        else:
            print(f'{worker.username} 1º LOGIN')
            try:
                cl = await self.api.login_custom(
                    username = worker.username,
                    password = worker.password,
                    proxy = proxy_url
                )
            except Exception as e:
                message_error = f"Error workerapi.login.login_custom: {e}"
                await self.error_login(message_error, worker, proxy_url)
                #await RecoverChallengeController.check_auto_recover(worker, ig['error'])
                raise Exception(message_error)
        
        cl = await self.change_proxy(cl, 'worker-action', worker)
        self.workers_cl[worker.username] = cl
        self.worker_service.check_count_few_minutes(worker.username)

        print(f'END LOGIN WORKER {worker.username}  --------------------------------')
        return cl

    async def change_proxy(self,cl: Client, type: str, obj_account: Worker = None) -> Client:
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
                        self.worker_service.update_by_id(obj_account._id,{"proxy":obj_account.proxy})
            return cl
        except Exception as e:
            raise Exception(f'changeProxy: {e}')

    async def delete_memory_session(self,username: str):
        try:
            if self.workers_cl.get(username):
                cl = self.workers_cl[username]
                self.cookie_service.save_state(username=cl.username,state=cl.get_settings(),pk=cl.user_id)
                del self.workers_cl[username]
        except Exception as e:
            ExceptionUtility.print_line_error()
            message_error = f'delete_memory_session: {e}'
            logger.error(message_error)
            raise Exception(message_error)

    async def error_login(self,message_error: str, worker: Worker, proxy_url: str = '') -> None:
        message_error = f"LOGIN ERROR: {message_error.lower()} username {worker.username} proxy {proxy_url}"
        logger.error(message_error)
        if InstagramUtility.is_error_prevent_login(message_error) or self.proxy_service.is_proxy_error(message_error):
            if self.proxy_service.is_proxy_error(message_error):
                message_error += f' Falha no Proxy {proxy_url} {message_error} '
                self.proxy_service.update_count(proxy_url, message_error, 'worker')
                self.worker_service.note_error(worker.username, f"login message error: {message_error}")
            elif ' 429 ' in message_error or 'wait a few minutes' in message_error:
                worker = self.worker_service.check_count_few_minutes(worker.username, f"login error: {message_error}", True)
            elif ('challenge' in message_error or 'checkpoint' in message_error) and 'unimplemented' not in message_error.lower():
                 self.worker_service.check_count_challenge(worker.username, 'login error: ' + message_error, True)
            else:
                self.worker_service.disable(worker.username, f"login disable error: {message_error}")
        else:
            self.worker_service.note_error(worker.username, f"login message error: {message_error}")

    async def error_action(self,cl: Client, message_error: str):
        message_error = 'errorHandling: ' + message_error
        if cl.username:
            logger.error(f"Error Handling: {cl.username} {message_error}")
            proxy = cl.proxy or 'proxy não detectado'
            message_error = f"{message_error} username {cl.username} proxy {proxy}"
        else:
            raise Exception(f"Error Handling cl.username without username: {message_error}")
        worker = self.worker_service.get_by_username(cl.username)
        try:
            cl.get_timeline_feed()
        except Exception as e:
            message_error += f" detected {InstagrapiChallenge.detect_name_challenge(e)} "
        if ('429' in message_error or 'wait a few minutes' in message_error or self.proxy_service.is_proxy_error(message_error)) and cl.proxy:
            if worker and ('429' in message_error or 'wait a few minutes' in message_error):
                self.worker_service.check_count_few_minutes(worker.username, message_error, True)
            self.proxy_service.update_count(cl.proxy, 'errorHandling: ' + message_error, 'worker')
        else:
            if InstagramUtility.is_error_session(message_error):
                await self.clean_session(worker, True)
            if InstagramUtility.is_error_prevent_action(message_error):
                if ('challenge' in message_error or 'checkpoint' in message_error) and 'unimplemented' not in message_error.lower():
                    self.worker_service.check_count_challenge(cl.username, message_error, True)
                else:
                    self.worker_service.disable(cl.username, message_error)
            else:
                self.worker_service.note_error(cl.username, message_error)
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
            if self.workers_cl.get(username):
                print(f"DELETE cookies username {username}")
                del self.workers_cl[username]
        except Exception as e:
            ExceptionUtility.print_line_error()
            message_error = f'clean_session: {e}'
            logger.error(message_error)
            raise Exception(message_error)
        
    async def follower_action(self,username_action:str,username_target:str='',id_target:str=''):
        error_link = False
        is_follower = False
        already_exists = False
        worker:Worker = None
        max_limit = False
        is_action = False
        try:

            if not username_action:
                raise Exception('username action required!')

            if not username_target and not id_target:
                raise Exception('username_target or id_target required!')

            worker = self.worker_service.get_by_username(username_action)
            if not worker or not int(worker.status):
                raise Exception(f"Usuário {username_action} já foi desativado: {worker.noteError}")

            cl = await self.login(worker)

            if not id_target:
                try:
                    info_target = await self.api.get_user_info(cl, username_target, id_target)
                except Exception as e:
                    message_error = f"ERRO worker.follower_action.get_user_info: erro quando o usuário da ação de seguir for pegar dos dados do alvo {e}"
                    if 'not found' in message_error:
                        error_link = True
                    is_action = True
                    raise Exception(message_error)
                
                if not info_target or not info_target.pk:
                    error_link = True
                    raise Exception('username target não encontrado')

                if info_target.is_private:
                    message_error = f"worker private: {info_target.username}"
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
                message_error = f'ERRO worker.follower_action.follow_by_id: followerAction->followById username {worker.username} proxy {cl.proxy}: {e}'
                if 'following the max limit' in message_error:
                    max_limit = True
                if 'not found' in message_error:
                        error_link = True
                raise Exception(message_error)

           
            if not is_follower:
                message_error = f'not follow maybe already_followed'
                logger.error(message_error)
                self.worker_service.note_error(cl.username,message_error)
                already_exists = True

            self.worker_service.update_count(cl.username, 1, 'follower', is_follower)

            return {
                'username_action': username_action,
                'username_target': username_target,
                'is_follower': is_follower,
                'id_target': id_target,
                'already_exists': already_exists,
                'worker': {
                    '_id': worker._id,
                    'username': worker.username,
                    'status': worker.status,
                    'noteError': worker.noteError,
                },
            }
        except Exception as e:
            message_error = f"ERROR: {e}"
            logger.error(message_error)
            ExceptionUtility.print_line_error()
            self.error_action(cl,message_error) if is_action and cl and cl.username else self.worker_service.note_error(username_action,message_error)
            worker = self.worker_service.get_by_username(username_action) if username_action else None
            return {
                'error': message_error,
                'error_link': error_link,
                'max_limit':max_limit,
                'worker': {
                    '_id': worker._id if worker else '',
                    'username': worker.username if worker else username_action,
                    'status': worker.status if worker else 0,
                    'noteError': worker.noteError if worker else '',
                },
            }
        

    async def like_action(self,username_action:str,url_target:str='',id_target:str=''):
        error_link = False
        is_liker = False
        worker:Worker = None
        info_target = None
        already_exists = False
        is_action = False
        try:
            if not username_action:
                raise Exception('username action required!')
            if not url_target and not id_target:
                raise Exception('url_target or id_target required!')

            worker = self.worker_service.get_by_username(username_action)
            if not worker or not int(worker.status):
                raise Exception(f"Usuário {username_action} já foi desativado: {worker.noteError}")

            cl = await self.login(worker)

            if not id_target:
                try: 
                    info_target = await self.api.get_media_url_info(cl, url_target)
                except Exception as e:
                    message_error = f"ERRO worker.like_action.get_media_url_info: erro quando o usuário da ação de de curtir for pegar dos dados do alvo {e}"
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
                message_error = f'ERRO worker.like_action.like_media: likeAction->likeMediaId  username {worker.username} proxy {cl.proxy}: {e}'
                if 'not found' in message_error:
                    error_link = True
                raise Exception(message_error)
            
            if not is_liker:
                message_error = f'not liker maybe already_liked'
                logger.error(message_error)
                self.worker_service.note_error(cl.username,message_error)
                already_exists = True

            self.worker_service.update_count(cl.username, 1, 'like', is_liker)

            return {
                'username_action': username_action,
                'url_target': url_target,
                'is_liker': is_liker,
                'id_target': id_target,
                'already_exists': already_exists,
                'worker': {
                    '_id': worker._id,
                    'username': worker.username,
                    'status': worker.status,
                    'noteError': worker.noteError,
                },
            }
        except Exception as e:
            message_error = f"ERROR: {e}"
            logger.error(message_error)
            ExceptionUtility.print_line_error()
            self.error_action(cl,message_error) if is_action and cl and cl.username else self.worker_service.note_error(username_action,message_error)
            worker = self.worker_service.get_by_username(username_action) if username_action else None
            return {
                'error': message_error,
                'error_link': error_link,
                'worker': {
                    '_id': worker._id if worker else '',
                    'username': worker.username if worker else username_action,
                    'status': worker.status if worker else 0,
                    'noteError': worker.noteError if worker else '',
                },
            }
        
    async def comment_action(self,username_action:str,text:str,url_target:str='',id_target:str=''):
        error_link = False
        is_comment = False
        worker:Worker = None
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

            worker = self.worker_service.get_by_username(username_action)
            if not worker or not int(worker.status):
                raise Exception(f"Usuário {username_action} já foi desativado: {worker.noteError}")

            cl = await self.login(worker)

            if not id_target:
                try: 
                    info_target = await self.api.get_media_url_info(cl, url_target)
                except Exception as e:
                    message_error = f"ERRO worker.comment_action.get_media_url_info: erro quando o usuário da ação de comentar for pegar dos dados do alvo {e}"
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
                message_error = f'ERRO worker.comment_action.comment_media: commentAction->commentMedia  username {worker.username} proxy {cl.proxy}: {e}'
                if 'not found' in message_error:
                    error_link = True
                raise Exception(message_error)
            
            if not is_comment:
                message_error = f'not comment'
                logger.error(message_error)
                self.worker_service.note_error(cl.username,message_error)
                already_exists = True

            self.worker_service.update_count(cl.username, 1, 'comment', is_comment)

            return {
                'username_action': username_action,
                'url_target': url_target,
                'is_comment': is_comment,
                'id_target': id_target,
                'already_exists': already_exists,
                "text": text,
                'worker': {
                    '_id': worker._id,
                    'username': worker.username,
                    'status': worker.status,
                    'noteError': worker.noteError,
                },
            }
        except Exception as e:
            message_error = f"ERROR: {e}"
            logger.error(message_error)
            ExceptionUtility.print_line_error()
            self.error_action(cl,message_error) if is_action and cl and cl.username else self.worker_service.note_error(username_action,message_error)
            worker = self.worker_service.get_by_username(username_action) if username_action else None
            return {
                'error': message_error,
                'error_link': error_link,
                'worker': {
                    '_id': worker._id if worker else '',
                    'username': worker.username if worker else username_action,
                    'status': worker.status if worker else 0,
                    'noteError': worker.noteError if worker else '',
                },
            }

    async def story_action(self,username_action:str,username_target:str='',id_target:str='',media_id:str='',max=10):
        error_link = False
        is_story = False
        worker:Worker = None
        is_action = False
        result = {}
        try:

            if not username_action:
                raise Exception('username action required!')
            if not username_target and not id_target:
                raise Exception('username_target or id_target required!')

            worker = self.worker_service.get_by_username(username_action)
            if not worker or not int(worker.status):
                raise Exception(f"Usuário {username_action} já foi desativado: {worker.noteError}")

            cl = await self.login(worker)

            if not id_target:
                try:
                    info_target = await self.api.get_user_info(cl, username_target, id_target)
                except Exception as e:
                    message_error = f"ERRO worker.story_action.get_user_info: erro quando o usuário da ação de ver stories for pegar dos dados do alvo {e}"
                    is_action = True
                    raise Exception(message_error)
                
                if not info_target or not info_target.pk:
                    error_link = True
                    raise Exception('username target não encontrado')

                if info_target.is_private:
                    message_error = f"worker private: {info_target.username}"
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
                message_error = f'ERRO worker.story_action.seen_stories: storyAction->seenStories username {worker.username} proxy {cl.proxy}: {e}'
                raise Exception(message_error)

            if not is_story and result.get('count')<=0:
                error_link = True
                return {
                    'error': 'stories não existe ou não estão mais disponíveis',
                    'error_link': error_link,
                    'username': cl.username,
                }
            
            self.worker_service.update_count(cl.username, 1, 'story', is_story)
        
            return {
                'username_action': username_action,
                'username_target': username_target,
                'is_story': is_story,
                'id_target': id_target,
                'worker': {
                    '_id': worker._id,
                    'username': worker.username,
                    'status': worker.status,
                    'noteError': worker.noteError,
                },
            }
        except Exception as e:
            message_error = f"ERROR: {e}"
            logger.error(message_error)
            ExceptionUtility.print_line_error()
            self.error_action(cl,message_error) if is_action and cl and cl.username else self.worker_service.note_error(username_action,message_error)
            worker = self.worker_service.get_by_username(username_action) if username_action else None
            return {
                'error': message_error,
                'error_link': error_link,
                'worker': {
                    '_id': worker._id if worker else '',
                    'username': worker.username if worker else username_action,
                    'status': worker.status if worker else 0,
                    'noteError': worker.noteError if worker else '',
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
        worker:Worker = None
        info_target = None
        text = ''
        is_action = False
        try:

            if not username_action:
                raise Exception('worker.like_comment_action username_action required!')
            if not url_target and  not id_target and not comment_id:
                raise Exception('like_comment_action url_target or id_target or comment_id required!')

            worker = self.worker_service.get_by_username(username_action)
            if not worker or not int(worker.status):
                raise Exception(f"Usuário {username_action} já foi desativado: {worker.noteError}")

            cl = await self.login(worker)

            if not id_target and not comment_id:
                    try:
                        info_target = await self.api.get_media_url_info(cl, url_target)
                        id_target = info_target.pk
                    except Exception as e:
                        message_error = f"ERRO worker.like_comment_action.get_media_url_info: erro quando o usuário da ação de curtir comentário for pegar dos dados do alvo {e}"
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
                raise Exception('worker.like_comment_action.find_user_in_comments username do comentário não encontrado')
                
            logger.warning(f"{cl.username} will like comment: {id_target}")
            try:
                is_liker = await self.api.like_comment_by_id(cl,comment_id)
            except Exception as e:
                is_action = True
                message_error = f'ERRO worker.like_comment_action.like_comment_by_id username {worker.username} proxy {cl.proxy}: {e}'
                raise Exception(message_error)

            self.worker_service.update_count(cl.username, 1, 'like', is_liker)

            return {
                'username_action': username_action,
                'url_target': url_target,
                'is_liker': is_liker,
                'id_target': id_target,
                'comment_id': comment_id,
                'text': text,
                'worker': {
                    '_id': worker._id,
                    'username': worker.username,
                    'status': worker.status,
                    'noteError': worker.noteError,
                },
            }
        except Exception as e:
            message_error = f"ERROR: {e}"
            logger.error(message_error)
            ExceptionUtility.print_line_error()
            self.error_action(cl,message_error) if is_action and cl and cl.username else self.worker_service.note_error(username_action,message_error)
            worker = self.worker_service.get_by_username(username_action) if username_action else None
            return {
                'error': message_error,
                'error_link': error_link,
                'worker': {
                    '_id': worker._id if worker else '',
                    'username': worker.username if worker else username_action,
                    'status': worker.status if worker else 0,
                    'noteError': worker.noteError if worker else '',
                },
            }
        

    async def edit_instagram(
        self,
        username:str,
        password:str,
        new_username:str = '',
        new_password:str = '',
        nationality:str = '',
        gender:str = '',
        first_name:str = '',
        biography:str = '',
        visibility:Literal['public', 'private', ''] ='',
        album:str = '',
        filename:str = '',
        posts_album:str = '',
        posts_quantity:int = 0,
        email:str = '',
        external_url:str = '',
        phone_number:str = '',
        proxy:str = '',
        session_id:str = ''):
        
        try:
            proxy = '' if not proxy or proxy == 'random' else proxy
            proxyUrl = proxy if proxy else ''

            if not username:
                raise Exception('username required!')
            if not password:
                raise Exception('password required!')

            worker = self.worker_service.get_by_username(username)

            countryCode = worker.nationality if worker else nationality

            if proxyUrl in ['worker', 'boost', 'random', 'extract', 'test']:
                objProxy = self.proxy_service.random_proxy({'type': proxyUrl, 'countryCode': countryCode})
                if objProxy and objProxy.url:
                    proxyUrl = objProxy.url
                else:
                    raise Exception(f"Proxy não encontrado tipo {proxyUrl}!")

            if proxyUrl:
                logger.warning(f'1.1 Usando Proxy: {proxyUrl}\n')
                if worker:
                    worker.proxy = proxyUrl
                proxy = proxyUrl

            try:
                if worker:
                    if password:
                        worker.password = password
                    cl = await self.login(worker)
                else:
                    cl = await self.api.login_custom(
                            username=username,
                            password=password,
                            proxy=proxy,
                            session_id=session_id
                    )
            except Exception as e:
                message_error = f"Error edit_instagram.login/login_custom {username}:{password} {proxy} {e}"
                message_error += f" detected {InstagrapiChallenge.detect_name_challenge(e)} "
                raise Exception(message_error)
    
            try:
                cl = await self.api.edit_profile(
                    cl=cl,
                    new_username=new_username,
                    first_name=first_name,
                    biography=biography,
                    external_url=external_url,
                    phone_number=phone_number,
                    email=email,
                    visibility=visibility,
                    album=album,
                    filename=filename,
                    posts_album=posts_album,
                    posts_quantity=posts_quantity,
                    gender=gender,
                    nationality=nationality,
                    new_password=new_password
                ) 
            except Exception as e:
                ExceptionUtility.print_line_error()
                message_error = f"Error edit_instagram.edit_profile {username}:{password} {proxy} {e}"
                message_error += f" detected {InstagrapiChallenge.detect_name_challenge(e)} "
                if 'LoginRequired' in message_error:
                    logger.error('LoginRequired 2')
                    self.clean_session(cl.username)
                raise Exception(message_error)
            try:
                info = await self.api.get_user_info(cl=cl,username=cl.username,pk=cl.user_id)
                imageBase64 = ImageUtility.stream_image_to_base64(info.profile_pic_url.unicode_string(), {'width': 150, 'height': 150}) if info.profile_pic_url else ''
                new_username = info.username or cl.username or new_username
                new_password = cl.password or new_password
                first_name = info.full_name or first_name
                proxy = cl.proxy or proxy
            except Exception as e:
                message_error = f"Error edit_instagram.get_user_info {username}:{password} {proxy} {e}"
                raise Exception(message_error)

            self.cookie_service.save_state(username=cl.username,state=cl.get_settings(),pk=cl.user_id)
            if worker and (new_username or new_password):
                self.worker_service.update_by_id(worker._id,{
                    "username":new_username if new_username else worker.username,
                    "password":new_password if new_password else worker.password,
                })
            logger.info('1.3 Editado com sucesso:')
            return {
                'success': True,
                'imageBase64': imageBase64,
                'new_username': new_username,
                'new_password': new_password,
                'first_name': first_name,
                'proxy': proxy,
            }
        except Exception as e:
            ExceptionUtility.print_line_error()
            message_error = f"api.edit_instagram: {e}"
            logger.error(message_error)
            return {'error': message_error}
