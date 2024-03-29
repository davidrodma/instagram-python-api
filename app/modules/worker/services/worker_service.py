from app.modules.worker.repositories.worker_repository import WorkerRepository
from app.modules.worker.models.worker import Worker
from typing import List,Iterable
from app.common.types.paginate_options import PaginateOptions
from app.common.types.id import ID
from datetime import datetime,timezone
from app.modules.config.services.config_service import ConfigService
from app.modules.instagram.utilities.instagram_utility import InstagramUtility
from app.modules.proxy.services.proxy_service import ProxyService

class WorkerService:

    repository = WorkerRepository()
    proxy_service = ProxyService()
    
    @classmethod
    def find_many(self,filter = None)->List[Worker]:
        return self.repository.find_many(filter)
    
    @classmethod
    def find_one(self, filter:dict)->Worker:
        return self.repository.find_one(filter)
    
    @classmethod
    def find_by_id(self, id:ID)->Worker:
        return self.repository.find_by_id(id)
    
    @classmethod
    def create(self, data:Worker):
        count = self.count()
        data['workerId'] = str(count+1)
        self.delete_many({"username":data['username']})
        return self.repository.create(data)
    
    @classmethod
    def create_many(self, data: Iterable[dict]):
        count = self.count()
        data = [{**obj, "workerId": str(count+i+1)} for i,obj in enumerate(data)]
        [self.delete_many({"username":obj['username']}) for i,obj in enumerate(data)]
        return self.repository.create_many(data)
    
    @classmethod
    def update(self,filter:dict, data: dict):
        return self.repository.update(filter,data)
    
    @classmethod
    def find_one_and_update(self,filter:dict, data: dict)->Worker:
        return self.repository.find_one_and_update(filter,data)
    

    @classmethod
    def update_by_id(self, id:ID, data: Worker):
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
    def delete_many(self, filter: dict):
        return self.repository.delete_many(filter)
    
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
    def get_one_random(self,filter:dict = {})->Worker:
        return self.repository.get_one_random(filter)
    
    @classmethod
    def get_by_username(self, username:str)->Worker:
        return self.find_one({"username":username})
    
    @classmethod
    def get_random_worker(self)->Worker:
        try:
            obj =  self.get_one_random({"status":1})
            if not obj:
                raise Exception("no worker!")
            return obj
        except Exception as e:
             raise Exception(f'get_random_worker: {e}')
    
    @classmethod
    def check_count_few_minutes(self,username: str, error: str = '', check_few_minutes: bool = False):
        try:
            update = {"$set":{}}
            disable_few_minutes = 0

            if error:
                update["$set"]['noteError'] = error

                if ('429' in error or 'wait a few minutes' in error) and check_few_minutes:
                    config = ConfigService.get_config_value('disable-few-minutes')
                    
                    if config:
                        arr = config.split(',')
                        disable_few_minutes = int(arr[1]) if len(arr) > 1 else int(arr[0])
                    
                    update['$inc'] = {'countError': 1, 'countFewMinutes': 1}
                    update["$set"]['fewMinutesAt'] = datetime.now(timezone.utc).replace(tzinfo=None)
                else:
                     update['$inc'] = {'countError': 1}

            else:
                update["$set"]['countFewMinutes'] = 0

            worker = self.find_one_and_update(
                {'username': username},
                update
            )

            if worker and disable_few_minutes > 0 and worker:
                worker.countFewMinutes >= disable_few_minutes
                self.disable(worker.username, f"disable error because config disable-few-minutes: {error}")


            if disable_few_minutes > 0 and worker:
                if worker.countFewMinutes >= disable_few_minutes:
                   self.disable(worker.username, f"disable error because config disable-few-minutes: {error}")
                elif worker.proxy:
                    if not self.proxy_service.is_proxy_fixed('worker') and \
                            worker.typeProxy != 'buy-proxy' and \
                            not self.proxy_service.is_buy_proxy(worker.proxy):
                        worker.proxy = 'random'
                        worker = self.find_one_and_update(worker._id,{"proxy":worker.proxy})
            return worker

        except Exception as e:
            print('checkCountFewMinutes', e)
            raise Exception(f'checkCountFewMinutes: {e}')

    @classmethod
    def note_error(self,username: str, message: str):
        return self.find_one_and_update(
            {'username': username},
            {'$set': {'noteError': message}, '$inc': {'countError': 1}}
        )  

    @classmethod
    def increment_count(self,username: str, quantity: int, type: str = '',is_success=False) -> Worker:
        try:
            update = {}
            increment = {
                'countUsed': quantity,
            }
            if type and type in ['follower', 'like', 'comment']:
                increment[f'countCurrent{type.capitalize()}'] = quantity
            if is_success:
                update.update({'$set': {"countChallenge":0}})
                increment['countSuccess'] = 1
            update.update({'$inc': increment})
            worker = self.find_one_and_update(
                {'username': username},
                update
            )

            return worker
        except Exception as e:
            print('incrementCount', e)
            raise Exception(f"incrementCount: {e}")

    @classmethod  
    def update_count(self,username: str, quantity: int, type: str = '',is_success=False) -> Worker:
        try:
            worker = self.increment_count(username, quantity, type, is_success)
            return worker
        except Exception as e:
            raise Exception(f"Worker->updateCount {username}: {e}")

    @classmethod
    def disable(self,username: str, reason: str = '')->Worker:
        try:
            print('disable', username)
            date = datetime.now(timezone.utc).replace(tzinfo=None)
            update = {
                '$set':{
                    'status': 0,
                    'disabledAt': date,
                    'pausedAtFollower': date,
                    'pausedAtLike': date,
                    'pausedAtComment': date
                }
            }
            if reason:
                expire_at = InstagramUtility.get_expire_at(reason)
                update['$set'].update({
                    'noteError': reason,
                    'expireAt': expire_at
                })
                update.update({'$inc': {'countError': 1}})
            return self.find_one_and_update({'username': username}, update)
        except Exception as e:
            message_error = f'worker_service->disable: {e}'
            print('disable', message_error)
            raise Exception(message_error)
        

    @classmethod
    def check_count_challenge(self,username: str, error: str = '', check_challenge: bool = False) -> None:
        try:
            update = {}
            disable_challenge = 0
            if error:
                update = {'noteError': error}
                if ('challenge' in error or 'checkpoint' in error) and check_challenge:
                    name_config = 'disable-challenge-login' if 'login' in error else 'disable-challenge-action'
                    disable_challenge = ConfigService.get_config_value(name_config)
                    disable_challenge = int(disable_challenge) if disable_challenge else 0
                    update['$inc'] = {'countError': 1, 'countChallenge': 1}
                else:
                    update['$inc'] = {'countError': 1}
            else:
                update['countChallenge'] = 0
            
            worker = self.find_one_and_update({'username': username}, update)

            if disable_challenge > 0 and worker and worker.countChallenge >= disable_challenge:
                self.disable(worker.username, f'disable error because config disable-challenge: {error}')
            elif worker and worker.proxy:
                if not self.proxy_service.is_proxy_fixed('worker') and worker.typeProxy != 'buy-proxy' and not self.proxy_service.is_buy_proxy(worker.proxy):
                    worker = self.find_one_and_update({'username': username}, {"proxy":"random"})
            return worker
        except Exception as e:
            print('checkCountChallenge', e)
            raise Exception(f'checkCountChallenge : {e}')

        

    


