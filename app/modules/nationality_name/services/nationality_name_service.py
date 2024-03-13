from app.modules.nationality_name.repositories.nationality_name_repository import NationalityNameRepository
from app.modules.nationality_name.models.nationality_name import NationalityName
from typing import List,Iterable,Dict
from app.common.types.paginate_options import PaginateOptions
from app.common.types.id import ID
from app.modules.nationality_name.types.name_gender_nationality_generated_type import NameGenderNationalityGenerated
import random

class NationalityNameService:

    repository = NationalityNameRepository()
    
    @classmethod
    def find_many(self,filter = None)->List[NationalityName]:
        return self.repository.find_many(filter)
    
    @classmethod
    def find_one(self, filter:dict)->NationalityName:
        return self.repository.find_one(filter)
    
    @classmethod
    def find_by_id(self, id:ID)->NationalityName:
        return self.repository.find_by_id(id)
    
    @classmethod
    def create(self, data:NationalityName):
        return self.repository.create(data)
    
    @classmethod
    def create_many(self, data: Iterable[dict]):
        return self.repository.create_many(data)
    
    @classmethod
    def update(self,filter:dict, data: dict):
        return self.repository.update(filter,data)
    
    @classmethod
    def find_one_and_update(self,filter:dict, data: dict)->NationalityName:
        return self.repository.find_one_and_update(filter,data)
    

    @classmethod
    def update_by_id(self, id:ID, data: NationalityName):
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
    def get_one_random(self,filter:dict = {})->NationalityName:
        return self.repository.get_one_random(filter)
    
    @classmethod
    def generate(self,gender:str='female', nationality:str='') -> NameGenderNationalityGenerated:
        name = self.generate_full_name(gender, nationality)
        username = self.generate_username(name['roman'])
        full_name = self.emoji_full_name(name['native'], gender)
        return {'username': username, 'full_name': full_name}
        
    @classmethod
    def generate_full_name(self,gender: str, nationality: str) -> Dict[str, str]:
        first_name = self.get_one_random({'type': 'name', 'gender': gender, 'nationality': nationality, 'status': 1})
        last_name =  self.get_one_random({'type': 'lastname', 'nationality': nationality, 'status': 1})
        if not last_name and (nationality == 'BR' or nationality == 'KR'):
            last_name = self.get_one_random({'type': 'name', 'gender': gender, 'nationality': nationality, 'status': 1})
        full_name = f"{first_name.nativeName} {last_name.nativeName}" if first_name and last_name else f"{first_name.romanName} {last_name.romanName}" if first_name else f"{last_name.romanName}"
        roman = f"{first_name['romanName']} {last_name['romanName']}" if first_name and last_name else f"{first_name.romanName}"
        return {'native': full_name, 'roman': roman}
    
    @classmethod
    def generate_username(self,full_name: str) -> str:
        username = full_name.lower()
        random_separator = self.random_separator()
        if random_separator['direction'] == 'left':
            username = f"{random_separator['separator']}{username.replace(' ', '')}"
        elif random_separator['direction'] == 'center':
            username = f"{username.replace(' ', random_separator['separator'])}"
        elif random_separator['direction'] == 'right':
            username = f"{username.replace(' ', '')}{random_separator['separator']}"
        username = f"{username}{random_separator['characters']}"
        username = self.replace_special_characters(username)
        return username
    
    @classmethod
    def emoji_full_name(full_name: str, gender: str) -> str:
        if gender == 'female':
            possibilities = [False, False, True, False]
            enable_emoji = random.choice(possibilities)
            if enable_emoji:
                emojis = ['☪️', '⭐️', '✨', '❤️', '💕', '❣️', '💍', '💋', '🙈', '🥰', '😊', '🤓']
                emoji = random.choice(emojis)
                direction_possibilities = ['right', 'right', 'left', 'right', 'right', 'center', 'right', 'right', 'both', 'right', 'right']
                direction = random.choice(direction_possibilities)
                if direction == 'left':
                    full_name = f"{emoji} {full_name}"
                elif direction == 'center':
                    full_name = f"{full_name.replace(' ', f' {emoji} ')}"
                elif direction == 'right':
                    full_name = f"{full_name} {emoji}"
                elif direction == 'both':
                    full_name = f"{emoji} {full_name} {emoji}"
        return full_name
    
    @classmethod
    def random_separator(self) -> Dict[str, str]:
        directions = ['left', 'center', 'right']
        direction = random.choice(directions)
        separators = ['', '_', '__']
        if direction != 'left':
            separators.append('.')
        separator = random.choice(separators)
        characters = self.random_string(2)
        return {'separator': separator, 'direction': direction, 'characters': characters}

    @classmethod
    def random_string(self,length: int) -> str:
        random_chars = 'abcdefghijklmnopqrstuvwxyz'
        return ''.join(random.choice(random_chars) for _ in range(length))
    
    @classmethod
    def replace_special_characters(self,text: str) -> str:
        charList = {
            'Ą': 'A', 'ą': 'a', 'á': 'a', 'à': 'a', 'â': 'a', 'ã': 'a', 'Á': 'A', 'À': 'A', 'Â': 'A', 'Ã': 'A', 'ß': 'b',
            'Ć': 'C', 'ć': 'c', 'ç': 'c', 'Ç': 'C', 'Ę': 'E', 'ę': 'e', 'é': 'e', 'è': 'e', 'ê': 'e', 'É': 'E', 'È': 'E',
            'Ê': 'E', 'í': 'i', 'ì': 'i', 'î': 'i', 'Í': 'I', 'Ì': 'I', 'Î': 'I', 'Ł': 'L', 'ł': 'l', 'Ñ': 'N', 'ñ': 'n',
            'Ö': 'O', 'ö': 'o', 'ó': 'o', 'ò': 'o', 'ô': 'o', 'õ': 'o', 'Ó': 'O', 'Ò': 'O', 'Ô': 'O', 'Õ': 'O', 'Ś': 'S',
            'ś': 's', 'ü': 'u', 'Ü': 'U', 'ú': 'u', 'ù': 'u', 'û': 'u', 'Ú': 'U', 'Ù': 'U', 'Û': 'U', 'Ź': 'Z', 'ź': 'z',
            'Ż': 'Z', 'ż': 'z', "'": '', ' ': ''
        }
        return ''.join(charList[c] if c in charList else c for c in text)



