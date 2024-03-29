from app.modules.profile.repositories.profile_repository import ProfileRepository
from app.modules.profile.models.profile import Profile
from typing import List,Iterable
from app.common.types.paginate_options import PaginateOptions
from app.common.types.id import ID
from datetime import datetime,timezone
from app.modules.config.services.config_service import ConfigService
from app.modules.instagram.utilities.instagram_utility import InstagramUtility

class ProfileService:

    repository = ProfileRepository()
    
    @classmethod
    def find_many(self,filter = None)->List[Profile]:
        return self.repository.find_many(filter)
    
    @classmethod
    def find_one(self, filter:dict)->Profile:
        return self.repository.find_one(filter)
    
    @classmethod
    def find_by_id(self, id:ID)->Profile:
        return self.repository.find_by_id(id)
    
    @classmethod
    def create(self, data:Profile):
        count = self.count()
        data['profileId'] = str(count+1)
        self.delete_many({"username":data['username']})
        return self.repository.create(data)
    
    @classmethod
    def create_many(self, data: Iterable[dict]):
        count = self.count()
        data = [{**obj, "profileId": str(count+i+1)} for i,obj in enumerate(data)]
        self.delete_many({"username":data['username']})
        return self.repository.create_many(data)
    
    @classmethod
    def update(self,filter:dict, data: dict):
        return self.repository.update(filter,data)
    
    @classmethod
    def find_one_and_update(self,filter:dict, data: dict)->Profile:
        return self.repository.find_one_and_update(filter,data)
    

    @classmethod
    def update_by_id(self, id:ID, data: Profile):
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
    def get_one_random(self,filter:dict = {})->Profile:
        return self.repository.get_one_random(filter)
    
    @classmethod
    def get_by_username(self, username:str)->Profile:
        return self.find_one({"username":username})
    
    @classmethod
    def get_random_profile(self)->Profile:
        try:
            obj =  self.get_one_random({"status":1})
            if not obj:
                raise Exception("no profile!")
            return obj
        except Exception as e:
             raise Exception(f'get_random_profile: {e}')
        
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
                        disable_few_minutes = int(arr[0]) if arr else 0
                    
                    update['$inc'] = {'countError': 1, 'countFewMinutes': 1}
                    update["$set"]['fewMinutesAt'] = datetime.now(timezone.utc).replace(tzinfo=None)

            else:
                update["$set"]['countFewMinutes'] = 0
                update['$inc'] = {'countSuccess': 1}


            profile = self.find_one_and_update(
                {'username': username},
                update
            )

            if profile and disable_few_minutes > 0 and profile.countFewMinutes >= disable_few_minutes:
                self.disable(profile.username, f"disable error because config disable-few-minutes: {error}")

            return profile

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
    def increment_count(self,username: str, quantity: int, type: str = '') -> Profile:
        try:
            update = {
                'countUsed': quantity,
            }
            if type and type in ['follower', 'like', 'comment']:
                update[f'countCurrent{type.capitalize()}'] = quantity

            profile = self.find_one_and_update(
                {'username': username},
                {'$inc': update}
            )

            return profile
        except Exception as e:
            print('incrementCount', e)
            raise Exception(f"incrementCount: {e}")

    @classmethod  
    def update_count(self,username: str, quantity: int, type: str = '') -> Profile:
        try:
            profile = self.increment_count(username, quantity, type)
            return profile
        except Exception as e:
            raise Exception(f"Profile->updateCount {username}: {e}")
        

    @classmethod
    def disable(self,username: str, reason: str = '')->Profile:
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
            message_error = f'profile_service->disable: {e}'
            print('disable', message_error)
            raise Exception(message_error)
        

    


