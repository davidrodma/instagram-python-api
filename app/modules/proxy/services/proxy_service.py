from app.modules.proxy.repositories.proxy_repository import ProxyRepository
from app.modules.proxy.models.proxy import Proxy
from app.modules.config.services.config_service import ConfigService
from typing import List,Iterable
from app.common.types.paginate_options import PaginateOptions
from app.common.types.id import ID
from datetime import datetime

class ProxyService:

    repository = ProxyRepository()
    
    @classmethod
    def find_many(self,filter = None)->List[Proxy]:
        return self.repository.find_many(filter)
    
    @classmethod
    def find_one(self, filter:dict)->Proxy:
        return self.repository.find_one(filter)
    
    @classmethod
    def find_by_id(self, id:ID)->Proxy:
        return self.repository.find_by_id(id)
    
    @classmethod
    def create(self, data:Proxy):
        return self.repository.create(data)
    
    @classmethod
    def create_many(self, data: Iterable[dict]):
        return self.repository.create_many(data)
    
    @classmethod
    def update(self,filter:dict, data: dict):
        return self.repository.update(filter,data)
    
    @classmethod
    def find_one_and_update(self,filter:dict, data: dict)->Proxy:
        return self.repository.find_one_and_update(filter,data)

    @classmethod
    def update_by_id(self, id:ID, data: Proxy):
        return self.repository.update_by_id(id, data)
    
    @classmethod
    def update_many(self,filter:dict, data: dict):
        return self.update_many(filter,data)
    
    @classmethod
    def update_many_by_ids(self,ids:List[ID], data: dict):
        return self.update_many_by_ids(ids,data)

    @classmethod
    def delete(self, filter: dict):
        return self.repository.delete(filter)
    
    @classmethod
    def delete_by_id(self, id:ID):
        return self.repository.delete_by_id(id)

    @classmethod
    def delete_many_by_ids(self, ids:List[ID]):
        return self.repository.delete_many_by_ids(ids)
    
    @classmethod
    def count(self, filter: dict = {}):
        return self.repository.count(filter)
    
    @classmethod
    def status(self, ids:List[ID], status:int):
        return self.repository.status(ids, status)
    
    @classmethod
    def paginate(self,filter={},options: PaginateOptions = {'page':1,'limit':100}):
        return self.repository.paginate(filter,options)
    
    @classmethod
    def get_by_url(self,url:str)->Proxy:
        return self.repository.find_one({"url":url})
    
    @classmethod
    async def random_proxy(self,type='',countryCode='') -> any:
        where = {'status': 1}

        try:
            if type in ['extract', 'worker', 'worker-action', 'boost', 'boost-action', 'website-view', 'test']:
                where['type'] = type
            else:
                where['type'] = ''

            if countryCode:
                where['countryCode'] = countryCode
            else:
                if type == 'worker' or type == 'worker-action':
                    where['$and'] = [{'$or': [{'countryCode': ''}, {'countryCode': None}]}]

            proxy:Proxy = self.repository.get_one_random(where)

            if not proxy or not proxy.get('url'):
                print(countryCode, '|', type)
                if countryCode and 'boost' in type:
                    return self.random_proxy(type=type)
                raise Exception('No proxy available!')

            if type != 'website-view':
                self.update_count(proxy['url'])
                pass

            return proxy

        except Exception as e:
            message_error = f"ProxyController.random_proxy: {e}"
            print(message_error)
            raise RuntimeError(message_error)
        
    @classmethod
    async def update_count(self,url_proxy: str, error: str = '', check_few_minutes: str = '') -> dict:
        try:
            update = {}
            limit_proxy_few_minutes = 0
            error = error.lower()
            
            proxy = self.find_one({'url': url_proxy})
            
            if error:
                update['noteError'] = error
                if 'ip_block' in error:
                    update = {
                        'noteError': f"Desabilitar proxy porque o ip está bloqueado no momento! {error}",
                        'status': 0,
                        'fewMinutesAt': datetime.utcnow(),
                    }
                elif ('few minutes' in error or ' 429 ' in error or self.is_proxy_error(error)) and check_few_minutes:
                    config = await ConfigService.get_config_value('limit-proxy-few-minutes')
                    is_bot = check_few_minutes == 'worker' or check_few_minutes == 'boost'
                    change_proxy_action_error = bool(int(await ConfigService.get_config_value('change-proxy-action-error')))
                    is_action = 'errorhandling' in error or 'action' in error
                    
                    if proxy and proxy.countFewMinutes > 1:
                        if is_bot and (not is_action or (is_action and change_proxy_action_error)):
                            update['change'] = True
                    
                    if config:
                        arr = config.split(',')
                        limit_proxy_few_minutes = int(arr[1] if is_bot and arr[1] else arr[0])
                    
                    update.update({
                        'fewMinutesAt': datetime.utcnow(),
                        '$inc': {'countErrors': 1, 'countFewMinutes': 1},
                    })
                else:
                    update.update({
                        '$inc': {'countErrors': 1},
                    })
            else:
                update = {
                    'countFewMinutes': 0,
                    '$inc': {'countSuccess': 1},
                }
            
            proxy = self.find_one_and_update(
                {'url': url_proxy},
                update
            )
            
            if proxy and limit_proxy_few_minutes > 0 and proxy.countFewMinutes >= limit_proxy_few_minutes:
                proxy = self.find_one_and_update(
                    {'url': url_proxy},
                    {
                        'status': 0,
                        'noteError': f"Desabilitado porque a quantidade {proxy['countFewMinutes']} erros proxy/few minutes é maior que o limite {limit_proxy_few_minutes} do config limit-proxy-few-minutes: {error}"
                    }
                )
            
            return proxy
        
        except Exception as e:
            print('proxyCount', e)
            raise RuntimeError('proxyCount: ' + str(e))
        
    @classmethod
    async def is_active(self,url: str):
        try:
            current_proxy = self.get_by_url(url)
        except Exception as error:
            return False
        
        if current_proxy and current_proxy.get('status'):
            if current_proxy.get('change'):
                self.update_by_id(current_proxy._id,{
                    "change":False,
                    "countChange": current_proxy.countChange +1
                })
                return False
            return True
        return False
        
    @classmethod
    def is_proxy_error(message_error: str) -> bool:
        message_error = message_error.lower()
        return any([
            ' socket ' in message_error,
            'proxy error' in message_error,
            'getaddrinfo' in message_error,
            'timeout awaiting' in message_error,
            'timed out' in message_error,
            'econnrefused' in message_error,
            'proxy protocol' in message_error,
            'server aborted' in message_error,
            'promise was canceled' in message_error,
            'no proxies' in message_error,
            ' masq ' in message_error,
            ' tunnel ' in message_error,
            'ip_block' in message_error,
            ' socks ' in message_error
        ])